#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys
import cv2
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));sys.path.insert(0,ROOT)
from physical_baseline import bdm_required_percent, evaluate_region
from vision_engine import analyze

expected={0.8:0.50,1.0:0.75,1.5:1.00,2.0:1.50,3.0:2.00,4.0:2.50,5.0:3.00,6.0:3.50,7.0:4.00,8.0:4.50,9.0:5.00}
for r,p in expected.items():
    got=bdm_required_percent(r)
    assert got==p,(r,got,p)
assert bdm_required_percent(0.79) is None
assert bdm_required_percent(10.01) is None
assert evaluate_region([0,0,20,20],(900,1600,3),None)['available'] is False
room={'farthest_seat_m':8.4,'image_height_m':1.8}
A=os.path.join(ROOT,'assets')
r2=analyze(cv2.imread(os.path.join(A,'slide_2_source.png')),cv2.imread(os.path.join(A,'slide_2_view_risk.png')),max_lines=18,room_config=room)
critical=[x for x in r2['lines'] if '2.5%' in x['source_text'] and 'Launch only' in x['source_text']]
assert critical and critical[0]['status']=='at_risk'
assert critical[0]['physical_baseline']['available'] is True
assert critical[0]['physical_baseline']['minimum_element_height_pct']==2.5
# Demonstrate the structural point: source geometry alone can meet BDM while the real room/camera loses content.
r3=analyze(cv2.imread(os.path.join(A,'slide_3_source.png')),cv2.imread(os.path.join(A,'slide_3_view_glare.png')),max_lines=18,room_config=room)
room_loss=[x for x in r3['lines'] if x['status']=='at_risk' and x['physical_baseline'].get('status')=='meets']
assert len(room_loss)>=3,len(room_loss)
out={'ok':True,'bdm_table_boundaries':len(expected),'judge_critical_status':critical[0]['status'],'judge_critical_bdm':critical[0]['physical_baseline'],'room_degradation_despite_source_geometry_meeting_bdm':len(room_loss),'examples':[{'source_text':x['source_text'],'camera_text':x['camera_text'],'bdm':x['physical_baseline']['status']} for x in room_loss[:3]],'claim_boundary':'This validates our implementation of the public source-geometry baseline and its separation from camera evidence; it is not a human-readability benchmark.'}
print(json.dumps(out,indent=2))
with open(os.path.join(ROOT,'docs','avixa_baseline_verification.json'),'w',encoding='utf-8') as f:json.dump(out,f,indent=2)
