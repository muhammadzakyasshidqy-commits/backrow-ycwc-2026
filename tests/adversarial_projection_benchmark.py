#!/usr/bin/env python3
"""Procedural adversarial engineering benchmark.

This deliberately does NOT claim human readability. It asks whether BACKROW
reacts to distinct physical/camera failure modes and whether a source-only
geometry baseline misses room-induced losses by construction.
"""
from __future__ import annotations
import cv2, numpy as np, os, sys, json, time
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));sys.path.insert(0,ROOT)
from vision_engine import analyze
A=os.path.join(ROOT,'assets')
room={'farthest_seat_m':8.4,'image_height_m':1.8}


def local_degrade(view,mode):
    im=view.copy();h,w=im.shape[:2]
    if mode=='extra_blur':
        im=cv2.GaussianBlur(im,(0,0),2.2)
    elif mode=='washout':
        im=np.clip(im.astype(np.float32)*0.36+255*0.64,0,255).astype(np.uint8)
    elif mode=='central_glare':
        ov=im.copy();cv2.ellipse(ov,(int(w*.57),int(h*.56)),(int(w*.26),int(h*.20)),-12,0,360,(255,255,250),-1);im=cv2.addWeighted(ov,.74,im,.26,0)
    elif mode=='low_res':
        small=cv2.resize(im,(max(240,w//7),max(140,h//7)),interpolation=cv2.INTER_AREA);im=cv2.resize(small,(w,h),interpolation=cv2.INTER_LINEAR)
    return im

cases=[
 ('clean',1,'slide_1_view_good.png',None),
 ('critical_numeric_loss',2,'slide_2_view_risk.png',None),
 ('glare_washout',3,'slide_3_view_glare.png',None),
 ('extra_blur',1,'slide_1_view_good.png','extra_blur'),
 ('low_res',1,'slide_1_view_good.png','low_res'),
]
rows=[]
for name,sid,vname,mode in cases:
    src=cv2.imread(os.path.join(A,f'slide_{sid}_source.png'));view=cv2.imread(os.path.join(A,vname))
    if mode:view=local_degrade(view,mode)
    t=time.perf_counter()
    try:
        r=analyze(src,view,max_lines=18,room_config=room);ok=True;err=None
        latency=time.perf_counter()-t
        bdm=r['source_geometry_baseline_counts'];room_only=sum(1 for x in r['lines'] if x['status']=='at_risk' and x['physical_baseline'].get('status')=='meets')
        ocr_risk=sum(1 for x in r['lines'] if x['text_similarity']<.42 or x['camera_confidence']<20)
        rules_risk=sum(1 for x in r['lines'] if x['rule_baseline_status']=='at_risk')
        rows.append({'case':name,'ok':ok,'counts':r['counts'],'bdm_source_only':bdm,'at_risk_despite_bdm_meets':room_only,'catastrophic_ocr_risk_regions':ocr_risk,'deterministic_rule_at_risk':rules_risk,'latency_s':round(latency,3)})
    except Exception as e:
        rows.append({'case':name,'ok':False,'error':str(e),'latency_s':round(time.perf_counter()-t,3)})
# Assertions are intentionally mechanism-level rather than fake accuracy claims.
by={x['case']:x for x in rows}
assert by['clean']['ok'] and by['clean']['counts']['at_risk']==0
assert by['critical_numeric_loss']['ok'] and by['critical_numeric_loss']['counts']['at_risk']>=1
assert by['glare_washout']['ok'] and by['glare_washout']['at_risk_despite_bdm_meets']>=3
# Severe degradation may fail alignment; fail-closed is acceptable. It must never silently return all-green.
for name in ['extra_blur','low_res']:
    x=by[name]
    assert (not x['ok']) or (x['counts']['at_risk']+x['counts']['watch']>0),x
report={'benchmark_type':'procedural adversarial engineering only','room_assumption':room,'cases':rows,'verified_properties':{'clean_control_no_false_risk':True,'critical_number_loss_detected':True,'camera_adds_room_evidence_beyond_source_geometry':True,'severe_degradation_not_silently_green':True},'not_claimed':['human readability accuracy','real-projector prevalence','generic frontier-AI superiority']}
print(json.dumps(report,indent=2))
with open(os.path.join(ROOT,'docs','adversarial_projection_benchmark.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
