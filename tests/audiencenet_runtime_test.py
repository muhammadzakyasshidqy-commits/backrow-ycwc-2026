from __future__ import annotations
import os,sys,json,cv2
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));sys.path.insert(0,ROOT)
from audiencenet import get_model, make_feature_vector
from vision_engine import analyze
m=get_model(); assert m.available, m.error
report=json.load(open(os.path.join(ROOT,'docs','AUDIENCENET_TRAINING_REPORT.json')))
assert report['test_macro_f1'] > max(report['signal_baseline_macro_f1'], report['geometry_baseline_macro_f1']), report
# Runtime JSON model must produce normalized probabilities with no sklearn dependency.
fv,_=make_feature_vector('Launch only if error rate stays below 2.5%.',{'structure_corr':.7,'contrast_ratio':.8,'sharpness_ratio':.7,'glare_fraction':.01,'dark_fraction':.01,'edge_ratio':.8},[0,0,600,45],(1080,1920,3),95)
p=m.predict(fv); assert p and abs(sum(p['probabilities'].values())-1)<1e-6
# End-to-end fixture must expose AudienceNet metadata and preserve the numeric mismatch guard.
A=os.path.join(ROOT,'assets')
r=analyze(cv2.imread(os.path.join(A,'slide_2_source.png')),cv2.imread(os.path.join(A,'slide_2_view_risk.png')),max_lines=18)
assert all(x.get('audiencenet',{}).get('model')=='AudienceNet-2.0.0' for x in r['lines'])
assert any(x['status']=='at_risk' and '2.5%' in x['source_text'] and '25%' in x['camera_text'] for x in r['lines'])
out={'ok':True,'model':m.version,'procedural_macro_f1':report['test_macro_f1'],'baseline_macro_f1':max(report['signal_baseline_macro_f1'], report['geometry_baseline_macro_f1']),'judge_counts':r['counts']};print(json.dumps(out,indent=2));json.dump(out,open(os.path.join(ROOT,'docs','audiencenet_runtime_verification.json'),'w'),indent=2)
