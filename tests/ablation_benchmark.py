#!/usr/bin/env python3
"""Ablation / safety benchmark on bundled procedural fixtures.

Purpose: prove that the custom learned channel is actually consulted and that
independent OCR/numeric guards prevent the model from overriding direct evidence.
This is engineering evidence only, not human-readability accuracy.
"""
from __future__ import annotations
import cv2,json,os,sys
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));sys.path.insert(0,ROOT)
from vision_engine import analyze
A=os.path.join(ROOT,'assets');room={'farthest_seat_m':8.4,'image_height_m':1.8}
fixtures=[(1,'slide_1_view_good.png'),(2,'slide_2_view_risk.png'),(3,'slide_3_view_glare.png')]
rows=[];learned_escalations=[];safety_overrides=[];numeric_guards=[]
for sid,vname in fixtures:
    r=analyze(cv2.imread(os.path.join(A,f'slide_{sid}_source.png')),cv2.imread(os.path.join(A,vname)),max_lines=18,room_config=room)
    row={'slide':sid,'final_counts':r['counts'],'rule_at_risk':0,'audiencenet_at_risk':0,'learned_escalations':0,'safety_overrides':0}
    for x in r['lines']:
        raw=x.get('audiencenet') or {};pred=raw.get('prediction')
        if x.get('rule_baseline_status')=='at_risk':row['rule_at_risk']+=1
        if pred=='at_risk':row['audiencenet_at_risk']+=1
        # Learned channel matters when deterministic policy was only WATCH/SUPPORTED
        # but final evidence becomes AT_RISK without a direct numeric hard guard.
        if x['status']=='at_risk' and x.get('rule_baseline_status')!='at_risk':
            learned_escalations.append({'slide':sid,'source_text':x['source_text'],'camera_text':x['camera_text'],'rule':x.get('rule_baseline_status'),'audiencenet':pred,'audiencenet_confidence':raw.get('confidence')});row['learned_escalations']+=1
        # Direct exact content evidence is allowed to overrule a pessimistic learned channel.
        if x['status']=='supported' and pred=='at_risk' and x.get('text_similarity',0)>=.98 and x.get('camera_confidence',0)>=70:
            safety_overrides.append({'slide':sid,'source_text':x['source_text'],'audiencenet_confidence':raw.get('confidence'),'final':'supported'});row['safety_overrides']+=1
        src=x.get('source_text','');cam=x.get('camera_text','')
        if '2.5%' in src and '25%' in cam:
            numeric_guards.append({'slide':sid,'source_text':src,'camera_text':cam,'final':x['status'],'rule':x.get('rule_baseline_status'),'audiencenet':pred})
    rows.append(row)
assert len(learned_escalations)>=1,learned_escalations
assert len(safety_overrides)>=2,safety_overrides
assert numeric_guards and all(x['final']=='at_risk' for x in numeric_guards),numeric_guards
out={'ok':True,'benchmark_type':'procedural ablation / safety engineering only','slides':rows,'learned_channel_non_cosmetic':{'pass':True,'count':len(learned_escalations),'examples':learned_escalations[:4]},'direct_evidence_safety_override':{'pass':True,'count':len(safety_overrides),'examples':safety_overrides[:4]},'numeric_hard_guard':{'pass':True,'examples':numeric_guards},'claim_boundary':'Shows implemented channel interaction on generated fixtures; does not establish human readability or real-projector superiority.'}
print(json.dumps(out,indent=2));json.dump(out,open(os.path.join(ROOT,'docs','ablation_benchmark.json'),'w'),indent=2)
