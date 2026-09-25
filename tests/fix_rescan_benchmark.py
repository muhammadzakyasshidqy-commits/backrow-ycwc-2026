#!/usr/bin/env python3
import cv2,json,os,sys
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));sys.path.insert(0,ROOT)
from vision_engine import analyze
A=os.path.join(ROOT,'assets');room={'farthest_seat_m':8.4,'image_height_m':1.8}
before=analyze(cv2.imread(os.path.join(A,'slide_2_source.png')),cv2.imread(os.path.join(A,'slide_2_view_risk.png')),max_lines=18,room_config=room)
after=analyze(cv2.imread(os.path.join(A,'slide_2_source_fixed.png')),cv2.imread(os.path.join(A,'slide_2_view_fixed.png')),max_lines=18,room_config=room)
assert before['counts']['at_risk']>=2,before['counts']
assert after['counts']['at_risk']==0 and after['counts']['watch']==0,after['counts']
# Ensure the exact repaired threshold is recovered.
crit=[x for x in after['lines'] if '2.5%' in x['source_text']]
assert crit and all(x['status']=='supported' for x in crit),crit
report={'benchmark_type':'procedural same-condition fix→rescan proof','before':before['counts'],'after':after['counts'],'critical_threshold_recovered':True,'claim_boundary':'Engineering proof that BACKROW can verify a slide change under the same simulated capture transform; not a real-projector human result.'}
print(json.dumps(report,indent=2))
with open(os.path.join(ROOT,'docs','fix_rescan_verification.json'),'w') as f:json.dump(report,f,indent=2)
