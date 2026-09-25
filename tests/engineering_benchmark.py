from __future__ import annotations
import cv2,numpy as np,sys,os,time,json,statistics,random
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,ROOT)
from vision_engine import analyze
A=os.path.join(ROOT,'assets'); random.seed(20260905)

def make_view(src,seed,severity):
    rng=np.random.default_rng(seed); h,w=src.shape[:2]; H,W=1080,1760
    bg=np.full((H,W,3),rng.integers(25,50),np.uint8)
    margin=120+int(severity*80)
    jitter=40+int(severity*70)
    dst=np.float32([[margin+rng.integers(-jitter,jitter),100+rng.integers(-jitter,jitter)],
                    [W-margin+rng.integers(-jitter,jitter),110+rng.integers(-jitter,jitter)],
                    [W-margin+rng.integers(-jitter,jitter),H-90+rng.integers(-jitter,jitter)],
                    [margin+rng.integers(-jitter,jitter),H-90+rng.integers(-jitter,jitter)]])
    sp=np.float32([[0,0],[w-1,0],[w-1,h-1],[0,h-1]])
    M=cv2.getPerspectiveTransform(sp,dst);warp=cv2.warpPerspective(src,M,(W,H));mask=cv2.warpPerspective(np.full((h,w),255,np.uint8),M,(W,H));bg[mask>0]=warp[mask>0]
    brightness=0.96-severity*0.26; bg=np.clip(bg.astype(float)*brightness+severity*14,0,255).astype(np.uint8)
    sig=0.35+severity*1.25; bg=cv2.GaussianBlur(bg,(0,0),sig)
    if severity>0.62:
        overlay=bg.copy();cx=int(W*.76+rng.integers(-90,90));cy=int(H*.62+rng.integers(-60,60));cv2.ellipse(overlay,(cx,cy),(280,190),-15,0,360,(250,250,244),-1);bg=cv2.addWeighted(overlay,.42,bg,.58,0)
    return bg

def run():
    rows=[]
    for sid in [1,2,3]:
        src=cv2.imread(os.path.join(A,f'slide_{sid}_source.png'))
        for sev in [0.18,0.58]:
            view=make_view(src,1000+sid*10+int(sev*100),sev); t=time.perf_counter()
            try:
                r=analyze(src,view,max_lines=8); ok=True; counts=r['counts']; inliers=r['alignment']['inliers']
            except Exception as e:
                ok=False;counts={};inliers=0
            rows.append({'slide':sid,'severity':sev,'aligned':ok,'inliers':inliers,'counts':counts,'latency_s':round(time.perf_counter()-t,3)})
    # Mismatched source/view must fail closed.
    mismatches=[]
    pairs=[(1,'slide_2_view_risk.png'),(2,'slide_3_view_glare.png')]
    for sid,vname in pairs:
        try: analyze(cv2.imread(os.path.join(A,f'slide_{sid}_source.png')),cv2.imread(os.path.join(A,vname)),max_lines=8); rejected=False
        except Exception: rejected=True
        mismatches.append({'source':sid,'view':vname,'rejected':rejected})
    # Fixed judge demo numeric detail must be caught.
    r=analyze(cv2.imread(os.path.join(A,'slide_2_source.png')),cv2.imread(os.path.join(A,'slide_2_view_risk.png')),max_lines=18)
    numeric=any(x['status']=='at_risk' and '2.5%' in x['source_text'] and '25%' in x['camera_text'] for x in r['lines'])
    out={'generated_at':'2026-09-05','synthetic_engineering_only':True,'projection_cases':rows,'wrong_pair_rejections':mismatches,'judge_demo_numeric_mismatch_detected':numeric}
    json.dump(out,open(os.path.join(ROOT,'docs','engineering_benchmark.json'),'w'),indent=2)
    assert all(x['aligned'] for x in rows), [x for x in rows if not x['aligned']]
    assert all(x['rejected'] for x in mismatches),mismatches
    assert numeric
    summary={'cases':len(rows),'alignment_pass':sum(x['aligned'] for x in rows),'wrong_pair_reject':sum(x['rejected'] for x in mismatches),'numeric_demo':numeric,'median_latency_s':round(statistics.median(x['latency_s'] for x in rows),3)};json.dump(summary,open(os.path.join(ROOT,'docs','engineering_runtime_verification.json'),'w'),indent=2);print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
