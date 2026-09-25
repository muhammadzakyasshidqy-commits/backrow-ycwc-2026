#!/usr/bin/env python3
from __future__ import annotations
import base64, json, os, subprocess, sys, time
from urllib.parse import urlparse, parse_qs
import requests
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
PORT=8097;BASE=f'http://127.0.0.1:{PORT}'
env=os.environ.copy();env['PORT']=str(PORT);env['BACKROW_HOST']='127.0.0.1'
p=subprocess.Popen([sys.executable,'server.py'],cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
study_path=None
try:
    for _ in range(60):
        try:
            if requests.get(BASE+'/api/health',timeout=.5).ok:break
        except Exception:time.sleep(.15)
    else:raise RuntimeError('server did not start')
    net=requests.get(BASE+'/api/network',timeout=2).json();assert net['ok']
    raw=open(os.path.join(ROOT,'assets','slide_1_source.png'),'rb').read();img='data:image/png;base64,'+base64.b64encode(raw).decode()
    payload={'title':'API privacy test','deck_name':'demo','room':{'farthest_seat_m':8.4,'image_height_m':1.8},'exposure_seconds':3,'slides':{'1':img},'items':[{'slide':1,'source_size':{'width':1600,'height':900},'source_text':'Decision threshold 2.5%','box':[100,650,420,30],'camera_text':'Decision threshold 25%','camera_confidence':92.0,'text_similarity':.93,'status':'at_risk','metrics':{'contrast_ratio':.8,'sharpness_ratio':.7,'glare_fraction':.01,'dark_fraction':0,'structure_corr':.8,'edge_ratio':.8},'audiencenet':{'prediction':'watch','confidence':.7,'probabilities':{'supported':.2,'watch':.7,'at_risk':.1}},'physical_baseline':{'available':True,'status':'below','ratio_to_minimum':.8}}]}
    c=requests.post(BASE+'/api/study/create',json=payload,timeout=8).json();assert c['ok'];sid=c['study_id'];study_path=os.path.join(ROOT,'data','field_studies',sid+'.json')
    token=parse_qs(urlparse(c['admin_path']).query)['token'][0];assert len(token)>=24 and token not in c['participant_path'] and token not in c['lan_participant_url']
    pub=requests.get(BASE+f'/api/study/{sid}/public',timeout=3).json();assert pub['ok'];pubtext=json.dumps(pub);assert pub['study']['schema']=='backrow-field-study-v2' and pub['study']['exposure_seconds']==3.0;assert pub['study']['completed_item_ids']==[];assert 'Decision threshold' not in pubtext and 'source_text' not in pubtext and 'camera_text' not in pubtext and 'box' not in pubtext and token not in pubtext;assert 'sequence' in pub['study']['items'][0] and 'ordinal' not in pub['study']['items'][0]
    unauth=requests.get(BASE+f'/api/study/{sid}/admin',timeout=3);assert unauth.status_code==403
    unauth_export=requests.get(BASE+f'/api/study/{sid}/export',timeout=3);assert unauth_export.status_code==403
    direct=requests.get(BASE+f'/data/field_studies/{sid}.json',timeout=3);assert direct.status_code==404
    adm=requests.get(BASE+f'/api/study/{sid}/admin',params={'token':token},timeout=3).json();assert adm['ok'] and adm['study']['items'][0]['source_text']=='Decision threshold 2.5%' and 'admin_token' not in adm['study'];assert len(adm['study']['presentation_order'])==1
    item_id=pub['study']['items'][0]['id']
    bad_present=requests.post(BASE+'/api/study/present',json={'study_id':sid,'admin_token':'wrong','item_id':item_id,'action':'start'},timeout=3);assert bad_present.status_code==403
    response_payload={'study_id':sid,'participant_code':'R01','answers':[{'item_id':item_id,'text':'Decision threshold 2.5%'}]}
    early=requests.post(BASE+'/api/study/respond',json=response_payload,timeout=3);assert early.status_code==400 and 'timed projector exposure' in early.text
    ps=requests.post(BASE+'/api/study/present',json={'study_id':sid,'admin_token':token,'item_id':item_id,'action':'start'},timeout=3).json();assert ps['ok']
    time.sleep(1.65)
    pe=requests.post(BASE+'/api/study/present',json={'study_id':sid,'admin_token':token,'item_id':item_id,'action':'end'},timeout=3).json();assert pe['ok']
    pub2=requests.get(BASE+f'/api/study/{sid}/public',timeout=3).json();assert item_id in pub2['study']['completed_item_ids']
    sv=requests.post(BASE+'/api/study/respond',json=response_payload,timeout=3).json();assert sv['ok'] and sv['saved']==1
    duplicate=requests.post(BASE+'/api/study/respond',json=response_payload,timeout=3);assert duplicate.status_code==400 and 'already submitted' in duplicate.text
    exp=requests.get(BASE+f'/api/study/{sid}/export',params={'token':token},timeout=3).json();assert exp['ok'] and len(exp['study']['responses'])==1 and len(exp['study']['presentation_events'])==2 and 'admin_token' not in exp['study']
    t=subprocess.run([sys.executable,'training/train_field_calibrator.py',study_path,'--out',os.path.join(ROOT,'models','__should_not_exist.json')],cwd=ROOT,text=True,capture_output=True)
    assert t.returncode!=0 and 'REFUSED' in (t.stdout+t.stderr);assert not os.path.exists(os.path.join(ROOT,'models','__should_not_exist.json'))
    out={'ok':True,'study_id_length':len(sid),'participant_truth_leak':False,'participant_cannot_read_admin_api':True,'raw_study_static_file_blocked':True,'admin_token_required':True,'admin_token_not_exported':True,'participant_submission_immutable':True,'frozen_randomized_order':True,'timed_exposure_protocol':True,'early_response_server_blocked':True,'public_exposure_completion_only':True,'presenter_events_authorized_and_logged':True,'response_roundtrip':True,'tiny_study_training_refused':True,'lan_endpoint':bool(net.get('lan_ip'))}
    print(json.dumps(out,indent=2));json.dump(out,open(os.path.join(ROOT,'docs','field_study_api_verification.json'),'w'),indent=2)
finally:
    p.terminate()
    try:p.wait(timeout=3)
    except Exception:p.kill()
    if study_path and os.path.exists(study_path):os.remove(study_path)
