#!/usr/bin/env python3
"""Evaluate frozen BACKROW decisions against locked real-projector naïve-reader responses.

This evaluator never trains or changes thresholds. It is intentionally separate from
train_field_calibrator.py so the final test can remain genuinely locked.
"""
from __future__ import annotations
import argparse,json,os,re,sys,math,glob
from difflib import SequenceMatcher
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def norm(s):
    s=(s or '').lower().replace('—','-').replace('–','-')
    s=re.sub(r'[^a-z0-9%.,:/+\- ]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def response_correct(src,ans):
    a,b=norm(src),norm(ans)
    if not a or not b:return False
    src_nums=re.findall(r'\d+(?:[.,]\d+)?%?',a);ans_nums=re.findall(r'\d+(?:[.,]\d+)?%?',b)
    if src_nums and src_nums!=ans_nums:return False
    return SequenceMatcher(None,a,b).ratio()>=0.84

def wilson(k,n,z=1.959963984540054):
    if n<=0:return None
    p=k/n;den=1+z*z/n;ctr=(p+z*z/(2*n))/den;half=z*math.sqrt((p*(1-p)+z*z/(4*n))/n)/den
    return [max(0,ctr-half),min(1,ctr+half)]

def safe_div(a,b):return a/b if b else None

def exposure_audit(d):
    """Verify that every evaluated target has at least one logged fixed exposure."""
    target=float(d.get('exposure_seconds') or 0)
    if not (3.0<=target<=12.0):return {'pass':False,'reason':'missing/invalid exposure_seconds','target_seconds':target,'valid_items':0,'total_items':len(d.get('items',[]))}
    events=d.get('presentation_events') or []
    starts={};durations={}
    for e in events:
        iid=str(e.get('item_id') or '');act=e.get('action');t=e.get('server_time')
        if not iid or not isinstance(t,(int,float)):continue
        if act=='start':starts[iid]=float(t)
        elif act=='end' and iid in starts:
            dt=float(t)-starts[iid]
            if dt>0:durations.setdefault(iid,[]).append(dt)
            starts.pop(iid,None)
    valid={iid:min(ds,key=lambda x:abs(x-target)) for iid,ds in durations.items() if any(max(1.0,target-1.5)<=x<=target+1.5 for x in ds)}
    total=len(d.get('items',[]));return {'pass':total>0 and len(valid)==total,'target_seconds':target,'valid_items':len(valid),'total_items':total,'closest_duration_seconds':{k:round(v,3) for k,v in valid.items()}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('studies',nargs='+',help='locked field-study export JSON files')
    ap.add_argument('--workflow-json',help='optional real manual-vs-BACKROW workflow timing JSON')
    ap.add_argument('--deck-json',help='optional real stable-frame deck-match JSON')
    ap.add_argument('--calibrator',default=str(ROOT/'models'/'field_calibrator.json'))
    ap.add_argument('--out',default=str(ROOT/'docs'/'FIELD_LOCKED_TEST_REPORT.json'))
    args=ap.parse_args()

    calibration_ids=set()
    if os.path.exists(args.calibrator):
        try:
            d=json.load(open(args.calibrator,encoding='utf-8'));calibration_ids=set(d.get('metadata',{}).get('training_study_ids') or [])
        except Exception:pass

    observations=[];study_ids=set();slide_groups=set();participants=set();regions=set();exposure_audits=[]
    paths=[]
    for spec in args.studies:
        hits=glob.glob(spec);paths.extend(hits or ([spec] if os.path.exists(spec) else []))
    if not paths: raise SystemExit('REFUSED: no locked field-study JSON files were found.')
    for path in paths:
        d=json.load(open(path,encoding='utf-8'));sid=str(d.get('study_id') or os.path.basename(path));study_ids.add(sid);ea=exposure_audit(d);exposure_audits.append({'study_id':sid,**ea});
        if not ea['pass']:raise SystemExit(f"REFUSED: study {sid} does not contain a complete valid timed exposure log for every target.")
        if sid in calibration_ids:raise SystemExit(f'REFUSED: locked study {sid} was used to train the field calibrator.')
        items={str(x['id']):x for x in d.get('items',[])}
        for resp in d.get('responses',[]):
            pc=f"{sid}:{resp.get('participant_code','anon')}";participants.add(pc)
            for a in resp.get('answers',[]):
                iid=str(a.get('item_id'));item=items.get(iid)
                if not item:continue
                src=item.get('source_text','');correct=response_correct(src,a.get('text',''))
                sys_status=str(item.get('status','')).lower();risk=sys_status=='at_risk'
                numeric=bool(re.search(r'\d',src or ''))
                key=f"{sid}:{iid}";regions.add(key);slide_groups.add(f"{sid}:slide:{item.get('slide',0)}")
                observations.append({'study':sid,'participant':pc,'region':key,'slide':item.get('slide'),'source_text':src,'answer':a.get('text',''),'human_recovered':correct,'system_at_risk':risk,'system_status':sys_status,'numeric':numeric})
    if len(observations)<100 or len(slide_groups)<8:
        raise SystemExit(f'REFUSED: locked report requires >=100 participant-region observations across >=8 independent slides; found {len(observations)} across {len(slide_groups)} slides.')

    tp=sum(o['system_at_risk'] and not o['human_recovered'] for o in observations)
    fp=sum(o['system_at_risk'] and o['human_recovered'] for o in observations)
    fn=sum((not o['system_at_risk']) and not o['human_recovered'] for o in observations)
    tn=sum((not o['system_at_risk']) and o['human_recovered'] for o in observations)
    precision=safe_div(tp,tp+fp);recall=safe_div(tp,tp+fn);false_alert=safe_div(fp,fp+tn)
    crit=[o for o in observations if o['numeric'] and not o['human_recovered']]
    crit_hit=sum(o['system_at_risk'] for o in crit);crit_recall=safe_div(crit_hit,len(crit))

    human_gates={
        'at_risk_precision_ge_0_90':precision is not None and precision>=.90,
        'critical_number_failure_recall_ge_0_90':crit_recall is not None and crit_recall>=.90,
        'false_alert_rate_le_0_10':false_alert is not None and false_alert<=.10,
    }

    workflow={'provided':False,'pass':False}
    if args.workflow_json:
        w=json.load(open(args.workflow_json,encoding='utf-8'));manual=float(w['manual_seconds']);backrow=float(w['backrow_seconds']);mrec=float(w['manual_critical_recall']);brec=float(w['backrow_critical_recall']);slides=int(w['slides'])
        workflow={'provided':True,'slides':slides,'manual_seconds':manual,'backrow_seconds':backrow,'manual_critical_recall':mrec,'backrow_critical_recall':brec,'faster':backrow<manual,'not_worse_critical_recall':brec>=mrec,'pass':slides>=15 and backrow<manual and brec>=mrec}

    deck={'provided':False,'pass':False}
    if args.deck_json:
        dd=json.load(open(args.deck_json,encoding='utf-8'));rows=dd.get('frames') or []
        stable=[x for x in rows if x.get('stable',True)];correct=sum(int(x.get('expected_slide'))==int(x.get('matched_slide')) for x in stable if x.get('matched_slide') is not None);total=len(stable);acc=safe_div(correct,total)
        deck={'provided':True,'stable_frames':total,'correct':correct,'accuracy':acc,'pass':total>=50 and acc is not None and acc>=.98}

    report={
        'schema':'backrow-locked-field-report-v1','locked':True,'study_ids':sorted(study_ids),'counts':{'participant_region_observations':len(observations),'unique_regions':len(regions),'independent_slides':len(slide_groups),'participants':len(participants),'critical_numeric_fail_observations':len(crit)},
        'confusion':{'tp':tp,'fp':fp,'fn':fn,'tn':tn},
        'metrics':{
            'at_risk_precision':precision,'at_risk_precision_95ci':wilson(tp,tp+fp),
            'failure_recall':recall,'failure_recall_95ci':wilson(tp,tp+fn),
            'false_alert_rate':false_alert,'false_alert_95ci':wilson(fp,fp+tn),
            'critical_number_failure_recall':crit_recall,'critical_number_failure_recall_95ci':wilson(crit_hit,len(crit)) if crit else None,
        },
        'human_gates':human_gates,'exposure_protocol':{'pass':all(x['pass'] for x in exposure_audits),'studies':exposure_audits},'workflow_gate':workflow,'real_deck_retrieval_gate':deck,
        'all_predeclared_gates_pass':all(human_gates.values()) and all(x['pass'] for x in exposure_audits) and workflow['pass'] and deck['pass'],
        'claim_boundary':'Only locked real-projector naïve-reader exports may be used. A false all-gates-pass value must not be relabeled as success.'
    }
    os.makedirs(os.path.dirname(args.out),exist_ok=True);json.dump(report,open(args.out,'w',encoding='utf-8'),indent=2)
    print(json.dumps(report,indent=2))
    raise SystemExit(0 if report['all_predeclared_gates_pass'] else 2)

if __name__=='__main__':main()
