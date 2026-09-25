from __future__ import annotations
import cv2, numpy as np, pytesseract, re, math
from dataclasses import dataclass
from difflib import SequenceMatcher
from PIL import Image
from audiencenet import get_model, make_feature_vector
from physical_baseline import evaluate_region
from field_calibrator import get_field_calibrator, make_features as make_field_features

OCR_TIMEOUT_S=3.0


def norm_text(s:str)->str:
    s=s.lower().replace('—','-').replace('–','-')
    s=re.sub(r'[^a-z0-9%.,:/+\- ]+',' ',s)
    return re.sub(r'\s+',' ',s).strip()

def sim(a,b):
    a,b=norm_text(a),norm_text(b)
    if not a or not b: return 0.0
    return SequenceMatcher(None,a,b).ratio()

def image_from_bytes(data:bytes):
    if not data or len(data) > 48*1024*1024:
        raise ValueError('Image payload is empty or too large.')
    arr=np.frombuffer(data,np.uint8)
    im=cv2.imdecode(arr,cv2.IMREAD_COLOR)
    if im is None: raise ValueError('Invalid image')
    h,w=im.shape[:2]
    if h < 24 or w < 24: raise ValueError('Image is too small to analyze.')
    if h*w > 30_000_000 or max(h,w) > 10_000:
        raise ValueError('Image dimensions are too large for a safe local analysis session.')
    return im

def encode_png_b64(im):
    import base64
    ok,buf=cv2.imencode('.png',im)
    if not ok: raise RuntimeError('encode failed')
    return base64.b64encode(buf).decode()

def _gray(im): return cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)

def rough_orb_signature(im, max_dim=900):
    """Fast descriptor-only signature for deck page retrieval before full homography."""
    h,w=im.shape[:2]
    scale=min(1.0, max_dim/max(h,w))
    work=cv2.resize(im,None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA) if scale<1 else im
    gray=_gray(work)
    orb=cv2.ORB_create(nfeatures=1600,scaleFactor=1.18,nlevels=8,edgeThreshold=12,fastThreshold=9)
    kp,des=orb.detectAndCompute(gray,None)
    return des

def rough_orb_match_score(src_des, view_des):
    if src_des is None or view_des is None or len(src_des)<8 or len(view_des)<8: return 0.0
    bf=cv2.BFMatcher(cv2.NORM_HAMMING)
    try: pairs=bf.knnMatch(src_des,view_des,k=2)
    except cv2.error: return 0.0
    good=[m for pair in pairs if len(pair)==2 for m,n in [pair] if m.distance < 0.76*n.distance]
    if not good: return 0.0
    # Reward both count and descriptor quality; used only to shortlist candidates.
    mean_dist=float(np.mean([m.distance for m in good]))
    return float(len(good)) * (1.0 + max(0.0, 64.0-mean_dist)/64.0)

def align_view_to_source(source, view):
    # Scale for feature work
    maxw=1200
    def sc(im):
        h,w=im.shape[:2]
        if w<=maxw: return im,1.0
        s=maxw/w
        return cv2.resize(im,None,fx=s,fy=s,interpolation=cv2.INTER_AREA),s
    ssrc,ss=sc(source); svw,vs=sc(view)
    g1,g2=_gray(ssrc),_gray(svw)
    orb=cv2.ORB_create(nfeatures=5000,scaleFactor=1.15,nlevels=10,edgeThreshold=12,fastThreshold=7)
    k1,d1=orb.detectAndCompute(g1,None); k2,d2=orb.detectAndCompute(g2,None)
    if d1 is None or d2 is None or len(k1)<10 or len(k2)<10:
        raise ValueError('Not enough visual features to align the projected content.')
    bf=cv2.BFMatcher(cv2.NORM_HAMMING)
    pairs=bf.knnMatch(d1,d2,k=2)
    good=[m for m,n in pairs if m.distance < 0.74*n.distance]
    if len(good)<8:
        # fallback looser but cross-check distance quartile
        allm=bf.match(d1,d2)
        allm=sorted(allm,key=lambda m:m.distance)
        good=allm[:max(12,min(100,len(allm)//8))]
    if len(good)<8: raise ValueError('Could not establish enough source-to-camera correspondences.')
    p1=np.float32([k1[m.queryIdx].pt for m in good]).reshape(-1,1,2)
    p2=np.float32([k2[m.trainIdx].pt for m in good]).reshape(-1,1,2)
    Hs,mask=cv2.findHomography(p1,p2,cv2.RANSAC,4.0)
    if Hs is None: raise ValueError('Homography estimation failed.')
    # Hs maps scaled source -> scaled view. Convert to full-size mapping.
    # x_view_full = (1/vs) Hs (ss*x_src_full)
    A=np.array([[ss,0,0],[0,ss,0],[0,0,1]],float)
    B=np.array([[1/vs,0,0],[0,1/vs,0],[0,0,1]],float)
    Hfull=B@Hs@A
    inliers=int(mask.ravel().sum()) if mask is not None else 0
    inlier_ratio=inliers/max(1,len(good))
    # Validate projected corners
    h,w=source.shape[:2]
    corners=np.float32([[[0,0]],[[w-1,0]],[[w-1,h-1]],[[0,h-1]]])
    proj=cv2.perspectiveTransform(corners,Hfull).reshape(-1,2)
    area=abs(cv2.contourArea(proj.astype(np.float32)))
    view_area=view.shape[0]*view.shape[1]
    coverage=area/max(1,view_area)
    if inliers<7 or inlier_ratio<0.22 or coverage<0.08:
        raise ValueError('Alignment was too uncertain to use as evidence.')
    Hinv=np.linalg.inv(Hfull)
    rect=cv2.warpPerspective(view,Hinv,(w,h),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,borderValue=(20,20,20))
    return rect, {
        'method':'ORB + RANSAC homography',
        'matches':len(good),'inliers':inliers,'inlier_ratio':round(inlier_ratio,3),
        'screen_coverage':round(float(coverage),3),
        'projected_corners':proj.round(1).tolist(),
    }

def ocr_lines(im, psm=6):
    # Tesseract LSTM OCR, return grouped line boxes on the image coordinate system.
    rgb=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
    try:
        data=pytesseract.image_to_data(rgb,config=f'--oem 1 --psm {psm}',output_type=pytesseract.Output.DICT,timeout=OCR_TIMEOUT_S)
    except RuntimeError as e:
        raise ValueError('OCR timed out before reliable evidence was available.') from e
    groups={}
    n=len(data['text'])
    for i in range(n):
        txt=(data['text'][i] or '').strip()
        try: conf=float(data['conf'][i])
        except: conf=-1
        if not txt or conf<0: continue
        key=(data['block_num'][i],data['par_num'][i],data['line_num'][i])
        x,y,w,h=[int(data[k][i]) for k in ('left','top','width','height')]
        g=groups.setdefault(key,{'words':[],'confs':[],'x1':x,'y1':y,'x2':x+w,'y2':y+h})
        g['words'].append(txt); g['confs'].append(conf)
        g['x1']=min(g['x1'],x);g['y1']=min(g['y1'],y);g['x2']=max(g['x2'],x+w);g['y2']=max(g['y2'],y+h)
    out=[]
    for g in groups.values():
        text=' '.join(g['words']).strip()
        if len(norm_text(text))<2 or float(np.mean(g['confs'])) < 42: continue
        # reject OCR garbage lines that are mostly punctuation/singletons
        alnum=sum(ch.isalnum() for ch in text)
        if alnum < max(2, int(len(text)*0.28)): continue
        toks=re.findall(r'[A-Za-z0-9%]+', text)
        if len(toks)>=3 and sum(len(t)<=1 for t in toks)/len(toks) > 0.60: continue
        alpha_words=re.findall(r'[A-Za-z]{3,}', text)
        pure_numeric=bool(re.fullmatch(r'\s*\d+(?:[.,]\d+)?%?\s*', text))
        if not alpha_words and not pure_numeric: continue
        out.append({'text':text,'confidence':float(np.mean(g['confs'])),'box':[g['x1'],g['y1'],g['x2']-g['x1'],g['y2']-g['y1']]})
    out.sort(key=lambda x:(x['box'][1],x['box'][0]))
    return out

def crop_pad(im,box,pad=8):
    x,y,w,h=box; H,W=im.shape[:2]
    x1=max(0,x-pad);y1=max(0,y-pad);x2=min(W,x+w+pad);y2=min(H,y+h+pad)
    return im[y1:y2,x1:x2]

def crop_metrics(src_crop, view_crop):
    if src_crop.size==0 or view_crop.size==0: return {}
    gs=_gray(src_crop); gv=_gray(view_crop)
    if gv.shape!=gs.shape: gv=cv2.resize(gv,(gs.shape[1],gs.shape[0]),interpolation=cv2.INTER_CUBIC)
    # Normalize exposure for shape preservation measurement
    def robust_contrast(g):
        p5,p95=np.percentile(g,[5,95]); return float((p95-p5)/255.0)
    sharp=float(cv2.Laplacian(gv,cv2.CV_64F).var())
    ssharp=float(cv2.Laplacian(gs,cv2.CV_64F).var())
    contrast=robust_contrast(gv); scontrast=robust_contrast(gs)
    glare=float(np.mean(gv>244)); dark=float(np.mean(gv<22))
    # normalized cross-correlation after CLAHE (robust to brightness)
    clahe=cv2.createCLAHE(clipLimit=2.0,tileGridSize=(4,4))
    a=clahe.apply(gs); b=clahe.apply(gv)
    if a.std()<1e-6 or b.std()<1e-6: corr=0.0
    else: corr=float(np.corrcoef(a.ravel(),b.ravel())[0,1])
    # edge preservation
    es=cv2.Canny(gs,60,160)>0; ev=cv2.Canny(gv,60,160)>0
    edge_src=float(es.mean()); edge_view=float(ev.mean())
    edge_ratio=min(2.0,edge_view/(edge_src+1e-6))
    return {
        'sharpness':round(sharp,2),'sharpness_ratio':round(min(2,sharp/(ssharp+1e-6)),3),
        'contrast':round(contrast,3),'contrast_ratio':round(min(2,contrast/(scontrast+1e-6)),3),
        'glare_fraction':round(glare,4),'dark_fraction':round(dark,4),
        'structure_corr':round(max(-1,min(1,corr)),3),'edge_ratio':round(edge_ratio,3)
    }

def recognize_expected_region(view_crop, expected):
    # Upscale small camera regions before OCR.
    h,w=view_crop.shape[:2]
    scale=max(1.0,min(4.0,80/max(1,h)))
    work=cv2.resize(view_crop,None,fx=scale,fy=scale,interpolation=cv2.INTER_CUBIC) if scale>1 else view_crop
    gray=_gray(work)
    # Two recognition passes: original and contrast-normalized. Select closest to source string.
    variants=[work]
    eq=cv2.createCLAHE(clipLimit=2.2,tileGridSize=(6,6)).apply(gray)
    variants.append(cv2.cvtColor(eq,cv2.COLOR_GRAY2BGR))
    best={'text':'','confidence':0.0,'similarity':0.0}
    for v in variants:
        rgb=cv2.cvtColor(v,cv2.COLOR_BGR2RGB)
        try:
            d=pytesseract.image_to_data(rgb,config='--oem 1 --psm 7',output_type=pytesseract.Output.DICT,timeout=OCR_TIMEOUT_S)
        except RuntimeError:
            continue
        words=[];confs=[]
        for t,c in zip(d['text'],d['conf']):
            t=(t or '').strip()
            try: c=float(c)
            except: c=-1
            if t and c>=0: words.append(t);confs.append(c)
        text=' '.join(words)
        s=sim(expected,text)
        conf=float(np.mean(confs)) if confs else 0.0
        score=s*0.8+(conf/100)*0.2
        old=best['similarity']*0.8+(best['confidence']/100)*0.2
        if score>old: best={'text':text,'confidence':round(conf,1),'similarity':round(s,3)}
    return best

def rule_classify_line(expected, recog, metrics, box, source_shape):
    """Deterministic baseline retained as a safety guard and benchmark comparator."""
    hsrc,wsrc=source_shape[:2]; x,y,w,h=box
    s=recog['similarity']; c=recog['confidence']/100
    corr=max(0,metrics.get('structure_corr',0)); contrast=metrics.get('contrast_ratio',0); sharp=metrics.get('sharpness_ratio',0)
    glare=metrics.get('glare_fraction',0)
    evidence=0.48*s+0.20*c+0.12*min(1,corr)+0.10*min(1,contrast)+0.10*min(1,sharp)
    evidence-=min(0.18,glare*1.8)
    src_nums=re.findall(r'(?<![a-z])\d+(?:[.,]\d+)?%?(?![a-z])', norm_text(expected))
    cam_nums=re.findall(r'(?<![a-z])\d+(?:[.,]\d+)?%?(?![a-z])', norm_text(recog.get('text','')))
    numeric_mismatch=bool(src_nums) and src_nums != cam_nums
    if numeric_mismatch: status='at_risk'
    elif s<0.42 or c<0.20 or (contrast<0.32 and corr<0.45): status='at_risk'
    elif evidence<0.60 or s<0.72 or c<0.43: status='watch'
    elif evidence>=0.76 and s>=0.83 and c>=0.58: status='supported'
    else: status='watch'
    return status,float(max(0,min(1,evidence))),numeric_mismatch


def recommend_fixes(expected, recog, metrics, physical, numeric_mismatch=False):
    """Evidence-driven, conservative repair suggestions.

    These are deterministic actions linked to observed failure modes; they are not
    presented as generative-AI design advice.
    """
    actions=[]
    if numeric_mismatch:
        actions.append({'kind':'critical_content','priority':1,'action':'Enlarge the decision-critical number/text and add a redundant label; then rescan from the same seat.','why':'The audience decode changed an exact numeric value.'})
    if physical and physical.get('available') and physical.get('status') in ('below','borderline'):
        scale=float(physical.get('recommended_scale_factor') or 1.0)
        actions.append({'kind':'source_geometry','priority':2,'action':f'Increase this text region to about {scale:.2f}× its current height or reduce the farthest viewing ratio; then rescan.','why':'The source-only BDM geometry baseline is below/borderline for the supplied room.'})
    if float(metrics.get('contrast_ratio',1)) < 0.45:
        actions.append({'kind':'contrast','priority':3,'action':'Increase foreground/background contrast or reduce ambient washout; then rescan.','why':'Local contrast collapsed in the audience capture.'})
    if float(metrics.get('sharpness_ratio',1)) < 0.30:
        actions.append({'kind':'sharpness','priority':3,'action':'Increase text size/stroke weight and verify projector focus; then rescan from the same seat.','why':'Fine edges were lost after projection/capture.'})
    if float(metrics.get('glare_fraction',0)) > 0.08:
        actions.append({'kind':'glare','priority':3,'action':'Move the critical region away from glare or adjust room light/projector/screen angle; then rescan.','why':'Glare covers part of the tested region.'})
    if not actions and float((recog or {}).get('similarity',0)) < 0.78:
        actions.append({'kind':'recovery','priority':4,'action':'Make the region larger and simpler, then repeat the audience-seat capture.','why':'The camera could not reliably recover the source phrase.'})
    # Stable ordering and deduplication.
    seen=set();out=[]
    for a in sorted(actions,key=lambda x:x['priority']):
        key=(a['kind'],a['action'])
        if key not in seen: seen.add(key);out.append(a)
    return out[:4]


def classify_line(expected, recog, metrics, box, source_shape, source_confidence=100.0, room_config=None):
    """Fuse AudienceNet, exact OCR, transparent physical baseline, and optional human calibration.

    AudienceNet is procedural pretraining for visual signal survivability. The optional
    FieldCalibrator is loaded only after a locked real-projector / naïve-reader study
    has met the training gate. Exact number changes and catastrophic OCR loss remain
    independent hard guards.
    """
    rule_status, rule_evidence, numeric_mismatch = rule_classify_line(expected,recog,metrics,box,source_shape)
    s=recog['similarity']; c=recog['confidence']/100
    corr=max(0,metrics.get('structure_corr',0)); contrast=metrics.get('contrast_ratio',0); sharp=metrics.get('sharpness_ratio',0)
    glare=metrics.get('glare_fraction',0)
    model=get_model()
    fv,feature_map=make_feature_vector(expected,metrics,box,source_shape,source_confidence,room_config)
    ai=model.predict(fv) if model.available else None
    physical=evaluate_region(box,source_shape,room_config)

    # Human-grounded calibration is intentionally optional/fail-closed.
    calibrator=get_field_calibrator()
    field_x, field_feature_map = make_field_features(recog,metrics,ai,physical,expected)
    field=calibrator.predict_recovery(field_x) if calibrator.available else None

    # Independent hard guards: no learned output may overrule an exact number change or catastrophic loss.
    if numeric_mismatch:
        status='at_risk'
    elif s<0.38 or c<0.15:
        status='at_risk'
    elif ai is None:
        status=rule_status
    else:
        pred=ai['class']; conf=ai['confidence']
        if rule_status=='supported' and s>=0.82 and c>=0.52:
            status='supported'
        elif rule_status=='at_risk':
            status='at_risk'
        elif pred=='at_risk' and conf>=0.90 and (s<0.82 or c<0.52):
            status='at_risk'
        else:
            status='watch'

    # Once a real field calibrator exists it may only make the output more conservative,
    # except that strong recovery evidence can resolve WATCH -> SUPPORTED. It never clears hard guards.
    if field and not numeric_mismatch and not (s<0.38 or c<0.15):
        hp=float(field['human_recovery_probability'])
        if hp < 0.25:
            status='at_risk'
        elif status=='supported' and hp < 0.55:
            status='watch'
        elif status=='watch' and hp >= 0.82 and s>=0.80 and c>=0.50:
            status='supported'

    ai_supported=(ai or {}).get('probabilities',{}).get('supported',0.0) if ai else 0.0
    evidence=max(0.0,min(1.0,0.58*rule_evidence+0.42*ai_supported)) if ai else rule_evidence
    reasons=[]
    if numeric_mismatch: reasons.append('a number or percentage changed in the audience decode')
    if s<0.72: reasons.append('camera OCR did not recover the source text reliably')
    if c<0.43: reasons.append('recognition confidence is low')
    if contrast<0.45: reasons.append('local contrast collapsed in the audience capture')
    if sharp<0.30: reasons.append('fine edges were lost')
    if glare>0.08: reasons.append('glare covers part of this region')
    if corr<0.35: reasons.append('source structure changed strongly after projection/capture')
    if physical.get('available') and physical.get('status')=='below': reasons.append('source text geometry is below the supplied-room BDM baseline')
    elif physical.get('available') and physical.get('status')=='borderline': reasons.append('source text geometry is only borderline against the supplied-room BDM baseline')
    if ai and ai['class']=='at_risk' and ai['confidence']>=0.78:
        reasons.append('AudienceNet detected a projector/camera degradation pattern associated with signal loss')
    elif ai and ai['class']=='watch' and status=='watch':
        reasons.append('AudienceNet found borderline visual survivability')
    if field:
        hp=float(field['human_recovery_probability'])
        if hp<0.55: reasons.append('the human-grounded field calibrator predicts low recovery within its measured domain')
    if status=='watch' and not reasons: reasons.append('learned and OCR evidence do not agree strongly enough for a recovered result')
    if status=='supported':
        if ai and ai['class']=='supported':
            reasons=['source text was recovered and AudienceNet also found stable visual survivability']
        elif ai and ai['class']=='at_risk':
            reasons=['source text was recovered exactly; AudienceNet raised a visual-degradation warning, so the raw model disagreement is kept in technical evidence']
        else:
            reasons=['source text was recovered exactly; the learned visual channel was not decisive enough to override direct recovery evidence']
        if physical.get('available') and physical.get('status')=='below':
            reasons.append('note: source-only room geometry baseline is below minimum even though this particular camera capture recovered the phrase')
    ai_out = {
        'available': bool(ai),
        'model': model.version,
        'prediction': ai['class'] if ai else None,
        'confidence': round(float(ai['confidence']),3) if ai else None,
        'probabilities': {k:round(float(v),3) for k,v in (ai['probabilities'].items() if ai else [])},
        'scope':'procedural projector/camera survivability pretraining; not human eyesight',
        'features': {k:round(float(v),4) for k,v in feature_map.items()}
    }
    field_out={
        'available':bool(field),
        'model':calibrator.version,
        'human_recovery_probability':round(float(field['human_recovery_probability']),3) if field else None,
        'scope':field.get('scope') if field else 'not trained; no human-readability probability is emitted',
        'features':{k:round(float(v),4) for k,v in field_feature_map.items()}
    }
    actions=recommend_fixes(expected,recog,metrics,physical,numeric_mismatch)
    return status,round(float(evidence),3),reasons,ai_out,rule_status,physical,field_out,actions

def analyze(source,view,max_lines=18,room_config=None):
    rect,align=align_view_to_source(source,view)
    lines=ocr_lines(source,psm=6)
    if not lines: raise ValueError('No source text could be detected. Use a slide with visible text.')
    # prioritize meaningful lines; cap latency
    lines=sorted(lines,key=lambda r:(-len(norm_text(r['text'])),r['box'][1]))[:max_lines]
    lines=sorted(lines,key=lambda r:(r['box'][1],r['box'][0]))
    results=[]
    for r in lines:
        sc=crop_pad(source,r['box'],6); vc=crop_pad(rect,r['box'],6)
        rec=recognize_expected_region(vc,r['text'])
        met=crop_metrics(sc,vc)
        status,score,reasons,ai_out,rule_status,physical,field_out,actions=classify_line(r['text'],rec,met,r['box'],source.shape,r['confidence'],room_config)
        results.append({
            'source_text':r['text'],'source_confidence':round(r['confidence'],1),'box':r['box'],
            'camera_text':rec['text'],'camera_confidence':rec['confidence'],'text_similarity':rec['similarity'],
            'status':status,'evidence_score':score,'reasons':reasons,'metrics':met,'audiencenet':ai_out,'rule_baseline_status':rule_status,
            'physical_baseline':physical,'field_calibrator':field_out,'recommended_actions':actions
        })
    counts={k:sum(1 for r in results if r['status']==k) for k in ['supported','watch','at_risk']}
    # generate overlay on source
    overlay=source.copy()
    colors={'supported':(79,123,91),'watch':(36,129,190),'at_risk':(68,65,190)} # BGR
    for r in results:
        x,y,w,h=r['box']; col=colors[r['status']]
        cv2.rectangle(overlay,(x-4,y-4),(x+w+4,y+h+4),col,3,lineType=cv2.LINE_AA)
    bdm_counts={k:sum(1 for r in results if (r.get('physical_baseline') or {}).get('status')==k) for k in ['meets','borderline','below']}
    fc=get_field_calibrator()
    return {'alignment':align,'counts':counts,'lines':results,'rectified':rect,'overlay':overlay,'source_size':{'width':int(source.shape[1]),'height':int(source.shape[0])},'room_config':room_config or {},'source_geometry_baseline_counts':bdm_counts,'field_calibrator':{'available':fc.available,'version':fc.version,'reason':fc.metadata.get('reason') if not fc.available else None}}
