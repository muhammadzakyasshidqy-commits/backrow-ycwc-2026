from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs'/'locked_evaluator_logic_verification.json'

def dump(path,obj):
    path.write_text(json.dumps(obj,indent=2),encoding='utf-8')

with tempfile.TemporaryDirectory(prefix='backrow_locked_eval_') as td:
    td=Path(td)
    items=[]
    for slide in range(1,11):
        items += [
            {'id':f'{slide}-risk','slide':slide,'source_text':f'Decision threshold {slide}.5%','status':'at_risk'},
            {'id':f'{slide}-ok','slide':slide,'source_text':f'Project status stable {slide}','status':'supported'},
        ]
    responses=[]
    for participant in range(1,6):
        answers=[]
        for slide in range(1,11):
            answers += [
                {'item_id':f'{slide}-risk','text':f'Decision threshold {slide}5%'},
                {'item_id':f'{slide}-ok','text':f'Project status stable {slide}'},
            ]
        responses.append({'participant_code':f'P{participant:02d}','answers':answers})
    events=[]
    t0=1_700_000_000.0
    for i,item in enumerate(items):
        events += [{'item_id':item['id'],'action':'start','server_time':t0+i*8.0},{'item_id':item['id'],'action':'end','server_time':t0+i*8.0+6.0}]
    study={'schema':'backrow-field-study-v2','study_id':'LOCKED-LOGIC-TEST','exposure_seconds':6.0,'presentation_order':[x['id'] for x in items],'presentation_events':events,'items':items,'responses':responses}
    study_path=td/'locked.json';dump(study_path,study)
    workflow=td/'workflow.json';dump(workflow,{'slides':15,'manual_seconds':180,'backrow_seconds':60,'manual_critical_recall':0.9,'backrow_critical_recall':1.0})
    deck=td/'deck.json';dump(deck,{'frames':[{'stable':True,'expected_slide':i%10,'matched_slide':i%10} for i in range(50)]})
    report_path=td/'report.json'
    cmd=[sys.executable,str(ROOT/'training'/'evaluate_locked_field_studies.py'),str(study_path),'--workflow-json',str(workflow),'--deck-json',str(deck),'--calibrator',str(td/'none.json'),'--out',str(report_path)]
    p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert p.returncode==0,(p.stdout,p.stderr)
    report=json.loads(report_path.read_text())
    assert report['all_predeclared_gates_pass'] is True
    assert report['counts']['participant_region_observations']==100
    assert report['counts']['independent_slides']==10
    assert report['metrics']['at_risk_precision']==1.0
    assert report['metrics']['critical_number_failure_recall']==1.0
    assert report['metrics']['false_alert_rate']==0.0
    assert report['exposure_protocol']['pass'] is True
    assert report['workflow_gate']['pass'] is True
    assert report['real_deck_retrieval_gate']['pass'] is True

    calibrator=td/'calibrator.json';dump(calibrator,{'metadata':{'training_study_ids':['LOCKED-LOGIC-TEST']}})
    blocked=subprocess.run([sys.executable,str(ROOT/'training'/'evaluate_locked_field_studies.py'),str(study_path),'--calibrator',str(calibrator),'--out',str(td/'bad.json')],cwd=ROOT,capture_output=True,text=True,timeout=30)
    assert blocked.returncode!=0
    assert 'used to train the field calibrator' in (blocked.stdout+blocked.stderr)

out={
    'ok':True,
    'scope':'synthetic evaluator-logic unit test only; not a field-performance result',
    'observations':100,
    'independent_slides':10,
    'perfect_gate_fixture_passed':True,
    'calibration_leakage_refused':True,
    'timed_exposure_enforced':True,
    'claim_boundary':'This proves evaluator gate/refusal logic executes as designed. It does not claim BACKROW accuracy on humans or projectors.'
}
dump(OUT,out)
print(json.dumps(out,indent=2))
