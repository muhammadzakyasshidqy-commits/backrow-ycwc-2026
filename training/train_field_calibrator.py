#!/usr/bin/env python3
"""Train BACKROW's optional human-grounded field calibration head.

The trainer deliberately refuses to run on tiny or synthetic-only collections.
Expected input: JSON exports produced by BACKROW field-study mode.
"""
from __future__ import annotations
import argparse, glob, json, os, re, sys
from difflib import SequenceMatcher
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.preprocessing import StandardScaler

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.insert(0,ROOT)
from field_calibrator import FEATURE_NAMES, make_features


def norm(s):
    s=(s or '').lower().replace('—','-').replace('–','-')
    s=re.sub(r'[^a-z0-9%.,:/+\- ]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def response_correct(src,ans):
    a,b=norm(src),norm(ans)
    if not a or not b:return False
    src_nums=re.findall(r'\d+(?:[.,]\d+)?%?',a); ans_nums=re.findall(r'\d+(?:[.,]\d+)?%?',b)
    if src_nums and src_nums!=ans_nums:return False
    return SequenceMatcher(None,a,b).ratio()>=0.84

def valid_exposure_log(d):
    target=float(d.get('exposure_seconds') or 0)
    if not (3.0<=target<=12.0):return False
    events=d.get('presentation_events') or [];starts={};valid=set()
    for e in events:
        iid=str(e.get('item_id') or '');act=e.get('action');t=e.get('server_time')
        if not iid or not isinstance(t,(int,float)):continue
        if act=='start':starts[iid]=float(t)
        elif act=='end' and iid in starts:
            dt=float(t)-starts[iid];starts.pop(iid,None)
            if max(1.0,target-1.5)<=dt<=target+1.5:valid.add(iid)
    return {str(x.get('id')) for x in d.get('items',[])} <= valid

def iter_examples(paths):
    for path in paths:
        with open(path,'r',encoding='utf-8') as f:d=json.load(f)
        if not valid_exposure_log(d): raise SystemExit(f'REFUSED: field-study file {path} is missing valid fixed-exposure logs for one or more targets.')
        items={str(x['id']):x for x in d.get('items',[])}
        sid=d.get('study_id') or os.path.basename(path)
        for resp in d.get('responses',[]):
            participant=str(resp.get('participant_code','anon'))
            for a in resp.get('answers',[]):
                item=items.get(str(a.get('item_id')))
                if not item: continue
                recog={'confidence':item.get('camera_confidence',0),'similarity':item.get('text_similarity',0)}
                x,_=make_features(recog,item.get('metrics',{}),item.get('audiencenet',{}),item.get('physical_baseline',{}),item.get('source_text',''))
                y=1 if response_correct(item.get('source_text',''),a.get('text','')) else 0
                # Group on study + slide to prevent the same slide from leaking across train/test.
                group=f"{sid}:slide:{item.get('slide',0)}"
                yield x,y,group,participant

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('inputs',nargs='*',help='field-study JSON files; defaults to data/field_studies/*.json')
    ap.add_argument('--out',default=os.path.join(ROOT,'models','field_calibrator.json'))
    args=ap.parse_args()
    paths=args.inputs or sorted(glob.glob(os.path.join(ROOT,'data','field_studies','*.json')))
    rows=list(iter_examples(paths))
    training_study_ids=[]
    for path in paths:
        try:
            training_study_ids.append(str(json.load(open(path,encoding='utf-8')).get('study_id') or os.path.basename(path)))
        except Exception: training_study_ids.append(os.path.basename(path))
    if not rows:
        raise SystemExit('REFUSED: no real field-study responses were found.')
    X=np.stack([r[0] for r in rows]); y=np.asarray([r[1] for r in rows],dtype=int); groups=np.asarray([r[2] for r in rows])
    unique_slides=len(set(groups.tolist()))
    if len(rows)<100 or unique_slides<8:
        raise SystemExit(f'REFUSED: need >=100 participant-region judgements across >=8 independent slides; found {len(rows)} judgements across {unique_slides} slides.')
    if len(set(y.tolist()))<2:
        raise SystemExit('REFUSED: labels contain only one class; a calibrator would be meaningless.')
    splitter=GroupShuffleSplit(n_splits=24,test_size=0.25,random_state=20260905)
    tr=te=None
    for a,b in splitter.split(X,y,groups):
        if len(set(y[a].tolist()))==2 and len(set(y[b].tolist()))==2:
            tr,te=a,b;break
    if tr is None: raise SystemExit('REFUSED: no group-disjoint split contains both recovered and failed examples in train and test.')
    scaler=StandardScaler().fit(X[tr]); Xt=scaler.transform(X[tr]); Xe=scaler.transform(X[te])
    clf=LogisticRegression(C=1.0,max_iter=2000,class_weight='balanced',random_state=20260905).fit(Xt,y[tr])
    pred=clf.predict(Xe); proba=clf.predict_proba(Xe)[:,1]
    pr,rc,f1,_=precision_recall_fscore_support(y[te],pred,average='binary',zero_division=0)
    report={'n_total':len(rows),'n_train':len(tr),'n_test':len(te),'independent_slide_groups':unique_slides,'accuracy':float(accuracy_score(y[te],pred)),'precision_recovered':float(pr),'recall_recovered':float(rc),'f1_recovered':float(f1),'roc_auc':float(roc_auc_score(y[te],proba)) if len(set(y[te].tolist()))>1 else None,'split':'group-disjoint by study+slide'}
    out={'version':'field-calibrator-v1','feature_names':FEATURE_NAMES,'scaler':{'mean':scaler.mean_.tolist(),'scale':scaler.scale_.tolist()},'coef':clf.coef_[0].tolist(),'intercept':float(clf.intercept_[0]),'metadata':{'training_type':'locked real-projector naïve-reader field labels only','created_from_files':[os.path.basename(p) for p in paths],'training_study_ids':training_study_ids,'report':report,'claim_boundary':'Predicts empirical naïve-reader recovery only within the measured field-study domain; not visual acuity diagnosis.'}}
    os.makedirs(os.path.dirname(args.out),exist_ok=True)
    with open(args.out,'w',encoding='utf-8') as f:json.dump(out,f,indent=2)
    print(json.dumps(report,indent=2));print('WROTE',args.out)
if __name__=='__main__':main()
