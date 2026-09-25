#!/usr/bin/env python3
from __future__ import annotations
import os, json, base64, traceback, time, io, re, secrets, socket
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, unquote
import cv2, numpy as np
from audiencenet import get_model
from field_calibrator import get_field_calibrator
from vision_engine import analyze, image_from_bytes, encode_png_b64, align_view_to_source, rough_orb_signature, rough_orb_match_score

ROOT=os.path.abspath(os.path.dirname(__file__))
MAX_BODY=48*1024*1024
DECKS={}
DECK_ORDER=[]
MAX_DECKS=8
OBSERVER_SESSIONS={}
OBSERVER_ORDER=[]
MAX_OBSERVER_SESSIONS=12
OBSERVER_TTL_S=2*60*60
JOIN_ATTEMPTS={}
STUDY_DIR=os.path.join(ROOT,'data','field_studies')
os.makedirs(STUDY_DIR,exist_ok=True)
ID_RE=re.compile(r'^[A-Za-z0-9_-]{8,48}$')


def parse_data_url(s:str)->bytes:
    if not isinstance(s,str): raise ValueError('Missing image data.')
    if s.startswith('data:'):
        try: s=s.split(',',1)[1]
        except Exception: raise ValueError('Invalid data URL.')
    return base64.b64decode(s,validate=True)


def _study_path(study_id:str):
    if not isinstance(study_id,str) or not ID_RE.fullmatch(study_id):
        raise ValueError('Invalid study id.')
    return os.path.join(STUDY_DIR,study_id+'.json')


def _load_study(study_id:str):
    path=_study_path(study_id)
    if not os.path.isfile(path): raise FileNotFoundError('Field study was not found.')
    with open(path,'r',encoding='utf-8') as f:return json.load(f)


def _save_study(d):
    path=_study_path(d['study_id']); tmp=path+'.tmp'
    with open(tmp,'w',encoding='utf-8') as f:
        json.dump(d,f,indent=2,ensure_ascii=False)
        f.flush(); os.fsync(f.fileno())
    os.replace(tmp,path)


def _num(v,lo,hi):
    try:x=float(v)
    except (TypeError,ValueError):return None
    return x if lo<=x<=hi else None


def _room(req):
    cfg=req.get('room') or {}
    d=_num(cfg.get('farthest_seat_m'),0.3,100.0)
    h=_num(cfg.get('image_height_m'),0.1,20.0)
    if d is None or h is None:return None
    return {'farthest_seat_m':round(d,3),'image_height_m':round(h,3)}


def _lan_ip():
    # No external network request; use local routing information only.
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255',1)); return s.getsockname()[0]
    except Exception:
        try:return socket.gethostbyname(socket.gethostname())
        except Exception:return '127.0.0.1'
    finally:s.close()


def _clean_text(v,n=500):
    return str(v or '').replace('\x00','').strip()[:n]


def _safe_data_image(v):
    if not isinstance(v,str) or not v.startswith('data:image/') or len(v)>900_000:return None
    # Validate base64 and that the image actually decodes before storing it.
    try:image_from_bytes(parse_data_url(v))
    except Exception:return None
    return v


def _create_study(req):
    items=req.get('items') or []
    if not isinstance(items,list) or not (1<=len(items)<=240):
        raise ValueError('A field study needs 1–240 region items.')
    study_id=secrets.token_urlsafe(12).replace('-','A').replace('_','B')[:16]
    slides={}
    for k,v in (req.get('slides') or {}).items():
        try:key=str(int(k))
        except Exception:continue
        img=_safe_data_image(v)
        if img:slides[key]=img
    clean=[]
    for ordinal,x in enumerate(items,1):
        if not isinstance(x,dict):continue
        box=x.get('box') or []
        if not (isinstance(box,list) and len(box)==4):continue
        try:box=[int(max(0,float(a))) for a in box]
        except Exception:continue
        if box[2]<=0 or box[3]<=0:continue
        ai=x.get('audiencenet') if isinstance(x.get('audiencenet'),dict) else {}
        physical=x.get('physical_baseline') if isinstance(x.get('physical_baseline'),dict) else {}
        metrics=x.get('metrics') if isinstance(x.get('metrics'),dict) else {}
        clean.append({
            'id':secrets.token_urlsafe(7),
            'ordinal':ordinal,
            'slide':int(x.get('slide') or 1),
            'source_text':_clean_text(x.get('source_text')),
            'source_size':{'width':int((x.get('source_size') or {}).get('width') or 0),'height':int((x.get('source_size') or {}).get('height') or 0)},
            'box':box,
            'camera_text':_clean_text(x.get('camera_text')),
            'camera_confidence':float(x.get('camera_confidence') or 0),
            'text_similarity':float(x.get('text_similarity') or 0),
            'status':_clean_text(x.get('status'),20),
            'metrics':{str(k):float(v) for k,v in metrics.items() if isinstance(v,(int,float))},
            'audiencenet':{
                'prediction':_clean_text(ai.get('prediction'),20),
                'confidence':float(ai.get('confidence') or 0),
                'probabilities':{str(k):float(v) for k,v in (ai.get('probabilities') or {}).items() if isinstance(v,(int,float))},
            },
            'physical_baseline':{str(k):v for k,v in physical.items() if isinstance(v,(str,int,float,bool)) or v is None},
        })
    if not clean:raise ValueError('No valid region items were supplied.')
    # Freeze one randomized target order at creation time. All readers see the same order,
    # which prevents the presenter from selecting an easier sequence after seeing responses.
    presentation_order=[x['id'] for x in clean]
    secrets.SystemRandom().shuffle(presentation_order)
    exposure=_num(req.get('exposure_seconds'),3.0,12.0) or 6.0
    d={
        'schema':'backrow-field-study-v2','study_id':study_id,'admin_token':secrets.token_urlsafe(24),'created_at':time.time(),
        'title':_clean_text(req.get('title') or 'BACKROW locked field study',120),
        'deck_name':_clean_text(req.get('deck_name') or 'presentation',160),
        'room':req.get('room') if isinstance(req.get('room'),dict) else {},
        'protocol':'Naïve readers look only at the real projector/display. Targets follow one frozen randomized order and use a fixed timed exposure. Source truth remains hidden on participant devices.',
        'exposure_seconds':round(exposure,2),
        'presentation_order':presentation_order,
        'slides':slides,'items':clean,'responses':[],'presentation_events':[]
    }
    _save_study(d)
    return d


def _ordered_items(d):
    by_id={x.get('id'):x for x in d.get('items',[]) if isinstance(x,dict)}
    order=d.get('presentation_order') or list(by_id)
    out=[by_id[i] for i in order if i in by_id]
    # Backward-compatible recovery for any old study missing order entries.
    seen={x.get('id') for x in out}
    out.extend(x for x in d.get('items',[]) if x.get('id') not in seen)
    return out


def _valid_exposure_items(d):
    """Return target ids with at least one server-logged exposure close to the frozen duration.

    This is deliberately computed server-side so a participant cannot unlock answers by
    changing browser state. It mirrors the locked evaluator tolerance.
    """
    target=float(d.get('exposure_seconds') or 0)
    if not (3.0 <= target <= 12.0): return set()
    starts={}
    valid=set()
    lo=max(1.0,target-1.5); hi=target+1.5
    for e in d.get('presentation_events') or []:
        iid=str(e.get('item_id') or ''); act=e.get('action'); t=e.get('server_time')
        if not iid or not isinstance(t,(int,float)): continue
        if act=='start': starts[iid]=float(t)
        elif act=='end' and iid in starts:
            dt=float(t)-starts.pop(iid)
            if lo <= dt <= hi: valid.add(iid)
    return valid


def _public_study(d):
    # Deliberately omit source_text, camera decode, source images, model evidence,
    # target boxes, and the admin token. Sequence numbers are not source ordinals.
    ordered=_ordered_items(d)
    return {
        'schema':d.get('schema'),'study_id':d['study_id'],'title':d.get('title'),'deck_name':d.get('deck_name'),
        'item_count':len(ordered),'exposure_seconds':d.get('exposure_seconds',6.0),
        'items':[{'id':x['id'],'sequence':i+1,'slide':x['slide']} for i,x in enumerate(ordered)],
        'completed_item_ids':sorted(_valid_exposure_items(d)),
        'instructions':'Look only at the real projector/display. Each target is shown for a fixed timed exposure. After it disappears, type exactly what you could read. Do not use the presenter laptop, source file, camera decode, or another transcript.'
    }




def _observer_session_id():
    return secrets.token_urlsafe(9).replace('-','A').replace('_','B')[:12]

def _create_observer_session(req):
    deck_id=_clean_text(req.get('deckId'),64)
    if not deck_id or deck_id not in DECKS:
        raise ValueError('Load a deck before creating an audience observer session.')
    sid=_observer_session_id()
    admin_token=secrets.token_urlsafe(24)
    observer_token=secrets.token_urlsafe(18)
    d={
        'session_id':sid,'deck_id':deck_id,'created_at':time.time(),
        'admin_token':admin_token,'observer_token':observer_token,'join_code':f'{secrets.randbelow(1000000):06d}',
        'deck_name':_clean_text(req.get('deck_name') or 'presentation',160),
        'room':req.get('room') if isinstance(req.get('room'),dict) else {},
        'sequence':0,'last_seen':None,'latest':None,'observed_slides':{}
    }
    OBSERVER_SESSIONS[sid]=d;OBSERVER_ORDER.append(sid)
    while len(OBSERVER_ORDER)>MAX_OBSERVER_SESSIONS:
        old=OBSERVER_ORDER.pop(0);OBSERVER_SESSIONS.pop(old,None)
    return d

def _get_observer_session(sid):
    sid=_clean_text(sid,48)
    d=OBSERVER_SESSIONS.get(sid)
    if not d: raise FileNotFoundError('Audience observer session was not found or expired.')
    if time.time()-float(d.get('created_at') or 0)>OBSERVER_TTL_S:
        OBSERVER_SESSIONS.pop(sid,None)
        raise FileNotFoundError('Audience observer session was not found or expired.')
    return d

def _public_observer_session(d):
    return {
        'session_id':d['session_id'],'deck_name':d.get('deck_name'),'created_at':d.get('created_at'),
        'sequence':d.get('sequence',0),'last_seen':d.get('last_seen'),
        'instructions':'Stand at the audience position, frame the full projected screen, then send a capture. Secure HTTPS enables live camera; photo capture remains available as a fallback.'
    }

def _observer_admin_view(d):
    latest=d.get('latest')
    return {
        'session_id':d['session_id'],'deck_name':d.get('deck_name'),'sequence':d.get('sequence',0),
        'last_seen':d.get('last_seen'),'latest':latest,
        'observed_slides':sorted(int(k) for k in d.get('observed_slides',{}).keys())
    }

def _match_deck_view(deck_id, view):
    if not deck_id or deck_id not in DECKS:
        raise ValueError('Deck session is missing or expired.')
    tm=time.perf_counter();view_sig=rough_orb_signature(view);shortlist=[]
    for idx,item in enumerate(DECKS[deck_id]):
        rs=rough_orb_match_score(item.get('sig'),view_sig)
        if rs>0:shortlist.append((rs,idx,item))
    if not shortlist:raise ValueError('The camera view did not match any slide in this deck.')
    shortlist.sort(reverse=True,key=lambda x:x[0]);verified=[]
    for rough_score,idx,item in shortlist[:min(4,len(shortlist))]:
        cand=image_from_bytes(item['png'])
        try:
            _,a=align_view_to_source(cand,view);score=a['inliers']*a['inlier_ratio']+rough_score*0.12;verified.append((score,idx,cand,a,rough_score))
        except Exception:pass
    if not verified:raise ValueError('The camera view did not geometrically match any slide in this deck.')
    verified.sort(reverse=True,key=lambda x:x[0]);best=verified[0]
    if best[0]<15:raise ValueError('Deck matching was too uncertain to use.')
    if len(verified)>1 and verified[1][0]>best[0]*0.92:raise ValueError('Two slides look too similar from this camera view. Wait for a more distinctive frame or select the slide manually.')
    return {'matched_index':best[1],'source':best[2],'alignment':best[3],'rough_score':best[4],'match_score':best[0],'deck_match_ms':round((time.perf_counter()-tm)*1000)}


class Handler(SimpleHTTPRequestHandler):
    server_version='BackrowServer/2.0'
    def translate_path(self,path):
        path=unquote(urlparse(path).path)
        if path=='/': path='/index.html'
        rel=os.path.normpath(path.replace('\\','/').lstrip('/'))
        full=os.path.abspath(os.path.join(ROOT,rel))
        try:
            if os.path.commonpath([ROOT,full]) != ROOT:return os.path.join(ROOT,'__forbidden__')
        except ValueError:return os.path.join(ROOT,'__forbidden__')
        return full
    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Permissions-Policy','camera=(self)')
        self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data: blob:; media-src 'self' blob:; connect-src 'self'; script-src 'self'; style-src 'self'; worker-src 'self' blob:; object-src 'none'; base-uri 'none'; frame-ancestors 'self'")
        self.send_header('X-Frame-Options','SAMEORIGIN')
        self.send_header('Cross-Origin-Opener-Policy','same-origin')
        self.send_header('Cache-Control','no-store' if urlparse(self.path).path.startswith('/api/') else 'no-cache')
        super().end_headers()
    def log_message(self,format,*args):print('[BACKROW]',format%args)
    def send_json(self,obj,status=200,headers=None):
        raw=json.dumps(obj,separators=(',',':'),ensure_ascii=False).encode('utf-8')
        self.send_response(status); self.send_header('Content-Type','application/json; charset=utf-8'); self.send_header('Content-Length',str(len(raw)))
        for k,v in (headers or {}).items():self.send_header(k,v)
        self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        parsed=urlparse(self.path);path=parsed.path
        # Field-study files contain blinded source truth and must never be reachable as static files.
        if path.startswith('/data/field_studies') or path.startswith('/data/'):
            return self.send_json({'ok':False,'error':'Not found'},404)
        if path=='/api/health':
            import subprocess
            try:v=subprocess.check_output(['tesseract','--version'],stderr=subprocess.STDOUT,text=True,timeout=5).splitlines()[0]
            except Exception:v='unavailable'
            m=get_model();fc=get_field_calibrator()
            return self.send_json({'ok':True,'engine':v,'audiencenet':{'available':m.available,'version':m.version,'scope':m.metadata.get('training_type')},'field_calibrator':{'available':fc.available,'version':fc.version,'reason':fc.metadata.get('reason') if not fc.available else None},'time':time.time()})
        if path=='/api/network':
            return self.send_json({'ok':True,'lan_ip':_lan_ip(),'port':int(getattr(self.server,'server_port',8080)),'host':getattr(self.server,'server_address',('127.0.0.1',))[0]})
        om=re.fullmatch(r'/api/observer/([A-Za-z0-9_-]{8,48})/(public|status)',path)
        if om:
            try:d=_get_observer_session(om.group(1))
            except FileNotFoundError:return self.send_json({'ok':False,'error':'Observer session not found'},404)
            if om.group(2)=='public':return self.send_json({'ok':True,'session':_public_observer_session(d)})
            from urllib.parse import parse_qs
            token=(parse_qs(parsed.query).get('token') or [''])[0]
            expected=str(d.get('admin_token') or '')
            if not expected or not secrets.compare_digest(str(token),expected):
                return self.send_json({'ok':False,'error':'Presenter authorization required'},403)
            return self.send_json({'ok':True,'session':_observer_admin_view(d)})
        m=re.fullmatch(r'/api/study/([A-Za-z0-9_-]{8,48})/(public|admin|export)',path)
        if m:
            try:d=_load_study(m.group(1))
            except FileNotFoundError:return self.send_json({'ok':False,'error':'Study not found'},404)
            except Exception as e:return self.send_json({'ok':False,'error':str(e)},400)
            if m.group(2)=='public':return self.send_json({'ok':True,'study':_public_study(d)})
            from urllib.parse import parse_qs
            token=(parse_qs(parsed.query).get('token') or [''])[0]
            expected=str(d.get('admin_token') or '')
            if not expected or not secrets.compare_digest(str(token),expected):
                return self.send_json({'ok':False,'error':'Admin authorization required'},403)
            # Never return the admin token inside the exported/admin study body.
            safe=dict(d);safe.pop('admin_token',None)
            return self.send_json({'ok':True,'study':safe})
        return super().do_GET()
    def _read_json(self):
        n=int(self.headers.get('Content-Length','0'))
        if n<=0 or n>MAX_BODY:raise ValueError('Request size is invalid or too large.')
        body=self.rfile.read(n)
        try:return json.loads(body)
        except Exception:raise ValueError('Request body must be valid JSON.')
    def do_POST(self):
        path=urlparse(self.path).path
        allowed={'/api/analyze','/api/deck_match','/api/render_pdf','/api/study/create','/api/study/respond','/api/study/present','/api/observer/create','/api/observer/join','/api/observer/frame'}
        if path not in allowed:return self.send_json({'ok':False,'error':'Not found'},404)
        try:
            req=self._read_json()
            if path=='/api/observer/create':
                d=_create_observer_session(req);lan=_lan_ip();port=int(getattr(self.server,'server_port',8080))
                sid=d['session_id'];ot=d['observer_token'];at=d['admin_token']
                return self.send_json({
                    'ok':True,'session_id':sid,'admin_token':at,'join_code':d['join_code'],
                    'observer_path':f'/observer.html?session={sid}&token={ot}',
                    'lan_observer_url':f'http://{lan}:{port}/observer.html?session={sid}&token={ot}',
                    'observer_home_url':f'http://{lan}:{port}/observer.html'
                })
            if path=='/api/observer/join':
                now=time.time();ip=str(self.client_address[0] if self.client_address else 'unknown')
                hist=[t for t in JOIN_ATTEMPTS.get(ip,[]) if now-t<60];JOIN_ATTEMPTS[ip]=hist
                if len(hist)>=20:return self.send_json({'ok':False,'error':'Too many pairing attempts. Wait one minute.'},429)
                hist.append(now)
                code=re.sub(r'\D','',_clean_text(req.get('join_code'),12))
                if len(code)!=6:raise ValueError('Observer code must contain 6 digits.')
                matches=[]
                for x in list(OBSERVER_SESSIONS.values()):
                    if now-float(x.get('created_at') or 0)>OBSERVER_TTL_S:continue
                    if x.get('join_code')==code:matches.append(x)
                if not matches:raise FileNotFoundError('Observer code was not found or expired.')
                d=max(matches,key=lambda x:x.get('created_at',0))
                # Pairing codes are single-use. The observer token in the paired URL survives reloads,
                # while the short human-entered code stops being a reusable credential after pairing.
                d['paired_at']=now;d['join_code']=None
                return self.send_json({'ok':True,'session_id':d['session_id'],'observer_token':d['observer_token'],'deck_name':d.get('deck_name')})
            if path=='/api/observer/frame':
                sid=_clean_text(req.get('session_id'),48);d=_get_observer_session(sid)
                token=str(req.get('observer_token') or '');expected=str(d.get('observer_token') or '')
                if not expected or not secrets.compare_digest(token,expected):
                    return self.send_json({'ok':False,'error':'Audience observer authorization required'},403)
                view=image_from_bytes(parse_data_url(req.get('view')));m=_match_deck_view(d.get('deck_id'),view);src=m['source']
                room=_room({'room':d.get('room') or {}})
                t=time.perf_counter();r=analyze(src,view,max_lines=18,room_config=room);elapsed=time.perf_counter()-t
                overlay='data:image/png;base64,'+encode_png_b64(r.pop('overlay'))
                rectified='data:image/png;base64,'+encode_png_b64(r.pop('rectified'))
                idx=int(m['matched_index']);summary={
                    'matched_slide_index':idx,'counts':r.get('counts'),'lines':r.get('lines'),'alignment':r.get('alignment'),
                    'source_size':r.get('source_size'),'room_config':r.get('room_config'),'source_geometry_baseline_counts':r.get('source_geometry_baseline_counts'),
                    'latency_ms':round(elapsed*1000),'deck_match_ms':m['deck_match_ms'],'overlay':overlay,'rectified':rectified,
                    'captured_at':time.time(),'engine':'AudienceNet + OCR + ORB/RANSAC'
                }
                d['sequence']=int(d.get('sequence',0))+1;d['last_seen']=time.time();d['latest']=summary;d.setdefault('observed_slides',{})[str(idx+1)]={'sequence':d['sequence'],'counts':r.get('counts'),'captured_at':d['last_seen']}
                return self.send_json({'ok':True,'sequence':d['sequence'],'result':summary})
            if path=='/api/study/create':
                d=_create_study(req);sid=d['study_id'];token=d['admin_token'];lan=_lan_ip();port=int(getattr(self.server,'server_port',8080))
                return self.send_json({'ok':True,'study_id':sid,'participant_path':f'/study.html?study={sid}','admin_path':f'/study_admin.html?study={sid}&token={token}','lan_participant_url':f'http://{lan}:{port}/study.html?study={sid}'})
            if path=='/api/study/present':
                sid=_clean_text(req.get('study_id'),48);d=_load_study(sid)
                token=str(req.get('admin_token') or '')
                expected=str(d.get('admin_token') or '')
                if not expected or not secrets.compare_digest(token,expected):
                    return self.send_json({'ok':False,'error':'Admin authorization required'},403)
                item_id=_clean_text(req.get('item_id'),64);action=_clean_text(req.get('action'),12)
                if item_id not in {x.get('id') for x in d.get('items',[])}:raise ValueError('Unknown study item.')
                if action not in {'start','end'}:raise ValueError('Presentation action must be start or end.')
                events=d.setdefault('presentation_events',[])
                # Prevent unbounded event growth if a presenter repeatedly replays targets.
                if len(events)>=2000:raise ValueError('Presentation event limit reached.')
                events.append({'item_id':item_id,'action':action,'server_time':time.time()})
                _save_study(d)
                return self.send_json({'ok':True,'recorded':action})
            if path=='/api/study/respond':
                sid=_clean_text(req.get('study_id'),48);d=_load_study(sid)
                valid={x['id'] for x in d.get('items',[])}
                answers=[]
                for a in req.get('answers') or []:
                    if not isinstance(a,dict) or str(a.get('item_id')) not in valid:continue
                    answers.append({'item_id':str(a.get('item_id')),'text':_clean_text(a.get('text'),500)})
                if not answers:raise ValueError('No valid study answers were supplied.')
                completed=_valid_exposure_items(d)
                answered_ids={a['item_id'] for a in answers}
                if not answered_ids.issubset(completed):
                    raise ValueError('Responses are locked until each answered target has completed its timed projector exposure.')
                code=re.sub(r'[^A-Za-z0-9_-]','',_clean_text(req.get('participant_code') or 'reader',32))[:32] or 'reader'
                # One immutable submission per participant code: prevents a participant from overwriting
                # an earlier blinded response after later seeing source truth.
                if any(x.get('participant_code')==code for x in d.get('responses',[])):
                    raise ValueError('This participant code has already submitted a response.')
                d['responses'].append({'participant_code':code,'submitted_at':time.time(),'answers':answers})
                _save_study(d)
                return self.send_json({'ok':True,'saved':len(answers)})
            if path=='/api/deck_match':
                view=image_from_bytes(parse_data_url(req.get('view')));m=_match_deck_view(req.get('deckId'),view)
                return self.send_json({'ok':True,'matched_slide_index':m['matched_index'],'deck_match_ms':m['deck_match_ms'],'alignment':{'inliers':m['alignment'].get('inliers'),'inlier_ratio':m['alignment'].get('inlier_ratio'),'screen_coverage':m['alignment'].get('screen_coverage')},'match_score':round(float(m['match_score']),3)})
            if path=='/api/render_pdf':
                import pypdfium2 as pdfium
                raw=parse_data_url(req.get('pdf'))
                doc=pdfium.PdfDocument(raw);page_count=len(doc)
                if page_count<1:raise ValueError('PDF has no pages.')
                if page_count>30:raise ValueError('For exhibition reliability, decks are capped at 30 slides per scan session.')
                pages=[];stored=[];total_pixels=0
                try:
                    for i in range(page_count):
                        page=doc[i]
                        try:
                            bitmap=page.render(scale=1.35);pil=bitmap.to_pil().convert('RGB');arr_full=cv2.cvtColor(np.asarray(pil),cv2.COLOR_RGB2BGR)
                        finally:page.close()
                        hfull,wfull=arr_full.shape[:2];total_pixels+=int(wfull)*int(hfull)
                        if wfull*hfull>12_000_000 or total_pixels>150_000_000:raise ValueError('PDF pages are too large for a safe local scan session.')
                        ok,png_arr=cv2.imencode('.png',arr_full)
                        if not ok:raise ValueError('Could not encode rendered PDF page.')
                        stored.append({'png':png_arr.tobytes(),'sig':rough_orb_signature(arr_full)})
                        h,w=arr_full.shape[:2];tw=360;th=max(1,int(h*tw/w));thumb=cv2.resize(arr_full,(tw,th),interpolation=cv2.INTER_AREA)
                        ok,jpg=cv2.imencode('.jpg',thumb,[cv2.IMWRITE_JPEG_QUALITY,82])
                        if not ok:raise ValueError('Could not encode PDF thumbnail.')
                        pages.append('data:image/jpeg;base64,'+base64.b64encode(jpg).decode())
                finally:doc.close()
                deck_id=secrets.token_urlsafe(10);DECKS[deck_id]=stored;DECK_ORDER.append(deck_id)
                while len(DECK_ORDER)>MAX_DECKS:
                    oldid=DECK_ORDER.pop(0);DECKS.pop(oldid,None)
                return self.send_json({'ok':True,'pages':pages,'count':len(pages),'deckId':deck_id})

            # /api/analyze
            view=image_from_bytes(parse_data_url(req.get('view')));deck_id=req.get('deckId');matched_index=None;deck_match_ms=None
            if deck_id and deck_id in DECKS and req.get('autoMatch',True):
                m=_match_deck_view(deck_id,view);matched_index=m['matched_index'];src=m['source'];deck_match_ms=m['deck_match_ms']
            else:src=image_from_bytes(parse_data_url(req.get('source')))
            max_lines=max(5,min(24,int(req.get('maxLines',18))));room=_room(req)
            t=time.perf_counter();r=analyze(src,view,max_lines=max_lines,room_config=room);elapsed=time.perf_counter()-t
            overlay=encode_png_b64(r.pop('overlay'));rect=encode_png_b64(r.pop('rectified'));r['overlay']='data:image/png;base64,'+overlay;r['rectified']='data:image/png;base64,'+rect
            r['latency_ms']=round(elapsed*1000);m=get_model();fc=get_field_calibrator()
            r['engine']='AudienceNet custom MLP + Tesseract 5 LSTM + ORB/RANSAC + transparent BDM source baseline'
            r['audiencenet_model']={'available':m.available,'version':m.version,'training_scope':m.metadata.get('training_type'),'human_readability_claim':False}
            r['field_calibrator_model']={'available':fc.available,'version':fc.version,'human_grounded':fc.available,'reason':fc.metadata.get('reason') if not fc.available else None}
            if matched_index is not None:r['matched_slide_index']=matched_index;r['deck_match_ms']=deck_match_ms
            r['claim_boundary']='Camera recoverability + source geometry evidence. Human-readability probability is emitted only after a locked real-projector naïve-reader calibrator has actually been trained.'
            return self.send_json({'ok':True,'result':r})
        except FileNotFoundError as e:
            return self.send_json({'ok':False,'error':str(e)},404)
        except Exception as e:
            traceback.print_exc();return self.send_json({'ok':False,'error':str(e)},400)


def main():
    host=os.environ.get('BACKROW_HOST','127.0.0.1');port=int(os.environ.get('PORT','8080'))
    httpd=ThreadingHTTPServer((host,port),Handler)
    shown='127.0.0.1' if host=='0.0.0.0' else host
    print(f'BACKROW running at http://{shown}:{port}')
    if host=='0.0.0.0':print(f'Field-study LAN participant access: http://{_lan_ip()}:{port}/study.html')
    try:httpd.serve_forever()
    except KeyboardInterrupt:pass

if __name__=='__main__':main()
