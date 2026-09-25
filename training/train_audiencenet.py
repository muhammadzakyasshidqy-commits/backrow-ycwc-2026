from __future__ import annotations
import os, sys, json, random, math
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, accuracy_score, f1_score, classification_report
from sklearn.model_selection import GroupShuffleSplit

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,ROOT)
from vision_engine import crop_metrics
from audiencenet import FEATURE_NAMES, make_feature_vector, room_geometry_features

SEED=20260910
rng=np.random.default_rng(SEED); random.seed(SEED)
OUT_MODEL=os.path.join(ROOT,'models','audiencenet_v2.json')
OUT_REPORT=os.path.join(ROOT,'docs','AUDIENCENET_TRAINING_REPORT.json')
SOURCE_SHAPE=(720,1280,3)

FONTS=[p for p in [
 '/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf','/usr/share/fonts/truetype/lato/Lato-Medium.ttf',
 '/usr/share/fonts/truetype/lato/Lato-Semibold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
 '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf','/usr/share/fonts/truetype/freefont/FreeSans.ttf',
 '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf','/usr/share/fonts/truetype/liberation2/LiberationSerif-Regular.ttf'
] if os.path.exists(p)]

TEMPLATES=[
 'Launch only if error rate stays below {n}%.','Revenue grew {n}% compared with last quarter.',
 'Submit the final report before {time}.','Room {n}B opens at {time}.','The sample contains {n} observations.',
 'Battery health should remain above {n}%.','Critical threshold: {n}.{d} milliseconds.',
 'Do not exceed {n} requests per minute.','Version {n}.{d} ships on Friday.','Average latency fell to {n} ms.',
 'The control group scored {n}.{d} points.','Budget remaining: ${n},500.','Audience capacity is {n} people.',
 'Keep the temperature below {n} C.','Confidence interval: plus or minus {n}%.',
 'This paragraph contains a decision-critical detail.','A good headline can hide a bad detail.',
 'Small text becomes fragile before the title does.','Check the exact number, not only the overall message.',
 'Projection quality changes with light and viewing position.','The audience should receive the same information you intended.',
 'Readable design is a property of the room, not only the file.','Never trust a slide preview without testing the real display.',
 'Perspective and glare can erase local information.','Use evidence from the farthest seat before presenting.',
 'The source file is not the final viewing condition.','A camera can reveal information loss after projection.',
 'Measure the exact region that matters to the decision.','If the evidence is uncertain, BACKROW should abstain.',
 'The safest result is sometimes not enough evidence.','Numbers and units deserve stricter checking.',
 'A single missing decimal point can reverse a decision.','Text contrast can collapse under ambient light.',
 'Thin strokes disappear earlier than large shapes.','The back row is a real-world stress test for a slide.',
 'Do not confuse visual polish with recoverable information.',
 'Quarterly target: {n}.{d} million units.','The deadline moved from {time} to {time2}.',
 'Minimum acceptable score is {n} points.','Temperature range: {n} to {n2} degrees.',
 'Model latency must remain under {n} ms.','Projector brightness was reduced during the test.',
 'Use the same audience position for the rescan.','A chart label can fail even when the headline survives.',
 'Exact values matter more than a vague summary.','The presenter should not need to inspect every slide manually.',
 'This is a clean control with high local contrast.','This region is intentionally close to the visibility boundary.'
]


def fill(t,i):
 n=2+(i*7)%89; n2=5+(i*11)%93; d=(i*3)%10; hour=8+(i%10); minute=[0,15,30,45][i%4]; hour2=9+((i+3)%9)
 return t.format(n=n,n2=n2,d=d,time=f'{hour}:{minute:02d}',time2=f'{hour2}:{minute:02d}')


def render_line(text,seed,target=None):
 rr=np.random.default_rng(seed); W=int(rr.integers(720,1180)); H=int(rr.integers(92,170)); theme=int(rr.integers(0,4))
 if theme==0: bg=int(rr.integers(242,256)); fg=int(rr.integers(0,38)); bgc=(bg,bg,bg); fgc=(fg,fg,fg)
 elif theme==1: bg=int(rr.integers(4,26)); fg=int(rr.integers(222,256)); bgc=(bg,bg,bg); fgc=(fg,fg,fg)
 elif theme==2: bg=int(rr.integers(224,252)); v=int(rr.integers(58,125)); bgc=(bg,bg,bg); fgc=(v,v,v)
 else:
  bg=int(rr.integers(238,255)); bgc=(bg,bg,bg); fgc=(int(rr.integers(20,75)),int(rr.integers(45,110)),int(rr.integers(20,90)))
 im=Image.new('RGB',(W,H),bgc); d=ImageDraw.Draw(im); fp=FONTS[int(rr.integers(0,len(FONTS)))];
 if target=='supported': fs=int(rr.integers(34,59))
 elif target=='watch': fs=int(rr.integers(23,39))
 elif target=='at_risk': fs=int(rr.integers(14,29))
 else: fs=int(rr.integers(16,58))
 font=ImageFont.truetype(fp,fs)
 while d.textbbox((0,0),text,font=font)[2]>W-36 and fs>13: fs-=1; font=ImageFont.truetype(fp,fs)
 bb=d.textbbox((0,0),text,font=font); th=bb[3]-bb[1]; y=max(5,(H-th)//2-bb[1]); d.text((18,y),text,font=font,fill=fgc)
 return cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR),fs,theme


def degrade(src,seed,severity):
 rr=np.random.default_rng(seed); im=src.astype(np.float32); h,w=im.shape[:2]
 ds=float(np.clip(1.0-severity*rr.uniform(.42,.90),.11,1.0))
 if ds<.985:
  sm=cv2.resize(im,(max(16,int(w*ds)),max(8,int(h*ds))),interpolation=cv2.INTER_AREA); im=cv2.resize(sm,(w,h),interpolation=cv2.INTER_CUBIC)
 sigma=float(severity*rr.uniform(.06,3.4))
 if sigma>.08: im=cv2.GaussianBlur(im,(0,0),sigma)
 wash=float(severity*rr.uniform(0,108)); contrast_scale=float(1.0-severity*rr.uniform(0,.48)); im=im*contrast_scale+wash
 gamma=float(rr.uniform(.70,1.45)); im=255*np.power(np.clip(im,0,255)/255.0,gamma)
 noise_sd=float(severity*rr.uniform(.1,8.5)); im+=rr.normal(0,noise_sd,im.shape)
 im=np.clip(im,0,255).astype(np.uint8); glare_alpha=0.0; glare_overlap=0.0
 if rr.random()<severity*.68:
  overlay=im.copy(); cx=int(rr.integers(int(w*.15),int(w*.95))); cy=int(rr.integers(0,h)); ax=int(rr.integers(max(18,w//16),max(24,w//3))); ay=int(rr.integers(max(9,h//7),max(14,h//2)))
  mask=np.zeros((h,w),np.uint8); ang=float(rr.integers(-30,30)); cv2.ellipse(mask,(cx,cy),(ax,ay),ang,0,360,255,-1); cv2.ellipse(overlay,(cx,cy),(ax,ay),ang,0,360,(252,252,247),-1)
  glare_alpha=float(rr.uniform(.08,.58)); glare_overlap=float(np.mean(mask>0)); im=cv2.addWeighted(overlay,glare_alpha,im,1-glare_alpha,0)
 q=int(np.clip(98-severity*rr.uniform(2,70),24,98)); ok,b=cv2.imencode('.jpg',im,[cv2.IMWRITE_JPEG_QUALITY,q]); im=cv2.imdecode(b,cv2.IMREAD_COLOR) if ok else im
 return im,{'ds':ds,'blur':sigma,'wash':wash,'contrast_scale':contrast_scale,'noise_sd':noise_sd,'glare_alpha':glare_alpha,'glare_overlap':glare_overlap,'jpeg_q':q}


def sample_room(rr):
 # Include missing room metadata so runtime without physical measurements is in-domain.
 if rr.random()<0.24:return None
 image_height=float(rr.uniform(.8,4.2)); ratio=float(rr.uniform(1.0,9.8)); distance=image_height*ratio
 return {'farthest_seat_m':distance,'image_height_m':image_height}


def proxy_label(meta,metrics,box,room):
 # Curriculum target only: a conservative combination of simulated camera signal loss
 # and physical source geometry. Thresholds are not human eyesight thresholds.
 corr=max(0,float(metrics.get('structure_corr',0))); cr=float(metrics.get('contrast_ratio',0)); sr=float(metrics.get('sharpness_ratio',0)); glare=float(metrics.get('glare_fraction',0))
 quality = 0.34*corr + 0.28*min(1.0,cr) + 0.24*min(1.0,sr) + 0.14*(1.0-min(1.0,glare*4.0))
 quality -= min(.34, meta['blur']*.075 + (1-meta['ds'])*.22 + max(0,55-meta['jpeg_q'])/180)
 geom=room_geometry_features(box,SOURCE_SHAPE,room)
 geom_penalty=0.0; geom_bonus=0.0
 if geom['room_available']:
  ratio_min=geom['bdm_ratio_to_minimum']*2.5; arc=(geom['visual_angle_arcmin'] or 0.0)
  if ratio_min<.72: geom_penalty += .25
  elif ratio_min<1.0: geom_penalty += .11
  elif ratio_min>=1.25: geom_bonus += .06
  if arc<5.0: geom_penalty += .24
  elif arc<8.0: geom_penalty += .10
  elif arc>=13.0: geom_bonus += .04
 score=quality-geom_penalty+geom_bonus
 severe=(cr<.30 or corr<.25 or sr<.18 or (glare>.16 and meta['glare_alpha']>.28) or meta['ds']<.18)
 if severe or score<.28:return 'at_risk'
 if score>=.68 and not (geom['room_available'] and geom['bdm_ratio_to_minimum']*2.5<.92):return 'supported'
 return 'watch'


def collect(n_per_target_per_template=10):
 X=[];y=[];groups=[];room_avail=[];targets=['supported','watch','at_risk']
 ranges={'supported':(.005,.22),'watch':(.30,.58),'at_risk':(.72,.999)}
 for tid,t in enumerate(TEMPLATES):
  for target in targets:
   lo,hi=ranges[target]
   for k in range(n_per_target_per_template):
    j=(targets.index(target)*100000)+(k*131)+tid
    text=fill(t,tid*100000+j); src,fs,_=render_line(text,SEED+tid*733+j*13,target); sev=float(rng.uniform(lo,hi)); deg,meta=degrade(src,SEED+900000+tid*911+j*29,sev); met=crop_metrics(src,deg)
    region_h=max(10,int(round(fs*1.22))); box=[0,0,src.shape[1],region_h]
    # Bias geometry toward the requested curriculum stratum without using it as truth.
    if target=='supported':
     image_h=float(rng.uniform(1.8,4.2)); ratio=float(rng.uniform(1.0,3.2)); room={'farthest_seat_m':image_h*ratio,'image_height_m':image_h} if rng.random()>.20 else None
    elif target=='at_risk':
     image_h=float(rng.uniform(.8,2.0)); ratio=float(rng.uniform(6.2,9.8)); room={'farthest_seat_m':image_h*ratio,'image_height_m':image_h} if rng.random()>.12 else None
    else:
     image_h=float(rng.uniform(1.1,3.0)); ratio=float(rng.uniform(3.2,6.4)); room={'farthest_seat_m':image_h*ratio,'image_height_m':image_h} if rng.random()>.20 else None
    label=target
    feat,_=make_feature_vector(text,met,box,SOURCE_SHAPE,float(rng.uniform(88,100)),room)
    X.append(feat);y.append(label);groups.append(tid);room_avail.append(room is not None)
 X=np.asarray(X); y=np.asarray(y); groups=np.asarray(groups); room_avail=np.asarray(room_avail)
 keep=np.arange(len(y)); rng.shuffle(keep)
 return X[keep],y[keep],groups[keep],room_avail[keep]

def softmax(z,T=1): z=z/max(T,1e-6);z-=z.max(axis=1,keepdims=True);e=np.exp(z);return e/e.sum(axis=1,keepdims=True)
def nll(p,yi): return float(-np.mean(np.log(np.clip(p[np.arange(len(yi)),yi],1e-9,1))))


def baseline_signal(X):
 out=[];ci=FEATURE_NAMES.index('structure_corr');cc=FEATURE_NAMES.index('contrast_ratio');si=FEATURE_NAMES.index('sharpness_ratio');gi=FEATURE_NAMES.index('glare_fraction')
 for r in X:
  if r[ci]<.28 or r[cc]<.30 or r[si]<.18 or r[gi]>.20:out.append('at_risk')
  elif r[ci]>.58 and r[cc]>.62 and r[si]>.42 and r[gi]<.07:out.append('supported')
  else:out.append('watch')
 return np.asarray(out)


def baseline_geometry(X):
 out=[];avail=FEATURE_NAMES.index('room_available');bi=FEATURE_NAMES.index('bdm_ratio_to_minimum');ai=FEATURE_NAMES.index('visual_angle_arcmin_norm')
 for r in X:
  if r[avail]<.5:out.append('watch');continue
  ratio_min=r[bi]*2.5; arc=r[ai]*30.0
  if ratio_min<.85 or arc<6.0:out.append('at_risk')
  elif ratio_min>=1.15 and arc>=10.0:out.append('supported')
  else:out.append('watch')
 return np.asarray(out)


def main():
 X,y,g,room_avail=collect(); class_names=np.array(['at_risk','supported','watch']); name_to_int={n:i for i,n in enumerate(class_names)}; yi_all=np.array([name_to_int[v] for v in y],dtype=np.int64)
 gss=GroupShuffleSplit(n_splits=1,test_size=.22,random_state=SEED); tv,te=next(gss.split(X,yi_all,g)); g2=GroupShuffleSplit(n_splits=1,test_size=.20,random_state=SEED+1); trl,va=next(g2.split(X[tv],yi_all[tv],g[tv])); tr=tv[trl]; va=tv[va]
 sc=StandardScaler().fit(X[tr]); counts=np.bincount(yi_all[tr],minlength=3); sw=np.array([len(tr)/(3*max(1,counts[v])) for v in yi_all[tr]],dtype=float)
 clf=MLPClassifier(hidden_layer_sizes=(48,24),activation='relu',solver='adam',alpha=.0018,batch_size=128,learning_rate_init=.0025,max_iter=650,early_stopping=True,validation_fraction=.15,n_iter_no_change=35,random_state=SEED).fit(sc.transform(X[tr]),yi_all[tr],sample_weight=sw)
 pv=np.clip(clf.predict_proba(sc.transform(X[va])),1e-8,1); logits=np.log(pv); yva=yi_all[va]; temps=np.linspace(.65,1.9,126); T=float(temps[int(np.argmin([nll(softmax(logits,t),yva) for t in temps]))])
 pt=np.clip(clf.predict_proba(sc.transform(X[te])),1e-8,1); pp=softmax(np.log(pt),T); pred=class_names[pp.argmax(1)]; test_y=y[te]; b_signal=baseline_signal(X[te]); b_geom=baseline_geometry(X[te])
 rep={
  'version':'AudienceNet-2.0.0','seed':SEED,'samples':len(X),'train':len(tr),'validation':len(va),'test':len(te),
  'split':'group-disjoint by text-template family','training_scope':'physics-aware procedural projection/camera survivability pretraining','human_readability_claim':False,
  'class_counts':{c:int(np.sum(y==c)) for c in sorted(set(y))},'room_metadata_available_fraction':float(np.mean(room_avail)),
  'temperature':T,'iterations':int(clf.n_iter_),'test_accuracy':float(accuracy_score(test_y,pred)),'test_macro_f1':float(f1_score(test_y,pred,average='macro')),
  'signal_baseline_accuracy':float(accuracy_score(test_y,b_signal)),'signal_baseline_macro_f1':float(f1_score(test_y,b_signal,average='macro')),
  'geometry_baseline_accuracy':float(accuracy_score(test_y,b_geom)),'geometry_baseline_macro_f1':float(f1_score(test_y,b_geom,average='macro')),
  'classes':class_names.tolist(),'confusion_matrix':confusion_matrix(test_y,pred,labels=class_names.tolist()).tolist(),'classification_report':classification_report(test_y,pred,output_dict=True,zero_division=0),
  'claim_boundary':'Procedural curriculum only. These metrics do not establish human readability or real-room generalization.'
 }
 layers=[]
 for i,(W,b) in enumerate(zip(clf.coefs_,clf.intercepts_)):layers.append({'weights':np.asarray(W).round(10).tolist(),'bias':np.asarray(b).round(10).tolist(),'activation':'relu' if i<len(clf.coefs_)-1 else 'linear'})
 model={'version':'AudienceNet-2.0.0','feature_names':FEATURE_NAMES,'classes':class_names.tolist(),'scaler':{'mean':sc.mean_.round(10).tolist(),'scale':sc.scale_.round(10).tolist()},'temperature':round(T,6),'layers':layers,'metadata':{'training_type':rep['training_scope'],'human_readability_claim':False,'samples':len(X),'test_macro_f1':rep['test_macro_f1'],'signal_baseline_macro_f1':rep['signal_baseline_macro_f1'],'geometry_baseline_macro_f1':rep['geometry_baseline_macro_f1'],'seed':SEED,'label_source':'physics-aware procedural curriculum strata; not human labels','physical_features':'optional room geometry + BDM-relative source size + angular region geometry'}}
 os.makedirs(os.path.dirname(OUT_MODEL),exist_ok=True);json.dump(model,open(OUT_MODEL,'w'),separators=(',',':'));json.dump(rep,open(OUT_REPORT,'w'),indent=2)
 print(json.dumps({k:rep[k] for k in ['samples','class_counts','test_accuracy','test_macro_f1','signal_baseline_macro_f1','geometry_baseline_macro_f1','temperature','iterations']},indent=2))

if __name__=='__main__':main()
