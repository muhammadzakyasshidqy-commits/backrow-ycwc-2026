#!/usr/bin/env python3
from __future__ import annotations
import base64,json,os,re,time,sys
import cv2
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));sys.path.insert(0,ROOT);OUT=os.path.join(ROOT,'preview');os.makedirs(OUT,exist_ok=True)
from vision_engine import analyze,encode_png_b64

def inline_page(name, scripts):
    h=open(os.path.join(ROOT,name),encoding='utf-8').read();css=open(os.path.join(ROOT,'styles.css'),encoding='utf-8').read();h=re.sub(r'<link rel="stylesheet" href="styles.css"\s*/?>',f'<style>{css}</style>',h)
    for script_name,content in scripts:
        h=h.replace(f'<script src="{script_name}"></script>',f'<script>{content}</script>')
    return h
locale=open(os.path.join(ROOT,'locale.js'),encoding='utf-8').read()
app=open(os.path.join(ROOT,'app.js'),encoding='utf-8').read()
html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read();css=open(os.path.join(ROOT,'styles.css'),encoding='utf-8').read();html=re.sub(r'<link rel="stylesheet" href="styles.css"\s*/?>',f'<style>{css}</style>',html)
for rel in ['assets/hero_source_detail.png','assets/hero_audience_detail.png']:
    raw=base64.b64encode(open(os.path.join(ROOT,rel),'rb').read()).decode('ascii');html=html.replace(rel,'data:image/png;base64,'+raw)
health={'ok':True,'engine':'tesseract 5.5.0','audiencenet':{'available':True,'version':'AudienceNet-2.0.0'}}
stub=f"window.fetch=async(url,opt)=>({{ok:true,json:async()=>String(url).includes('/api/health')?{json.dumps(health)}:({{ok:true}})}});"
html=html.replace('<script src="app.js"></script>',f'<script>{stub}</script><script>{app}</script>')
room={'farthest_seat_m':8.4,'image_height_m':1.8}
def prepare(src,view):
    t=time.perf_counter();r=analyze(cv2.imread(os.path.join(ROOT,'assets',src)),cv2.imread(os.path.join(ROOT,'assets',view)),max_lines=18,room_config=room);r['latency_ms']=round((time.perf_counter()-t)*1000);r['overlay']='data:image/png;base64,'+encode_png_b64(r['overlay']);r['rectified']='data:image/png;base64,'+encode_png_b64(r['rectified']);r['engine']='AudienceNet custom MLP + Tesseract 5 LSTM + ORB/RANSAC';r['audiencenet_model']={'available':True,'version':'AudienceNet-2.0.0'};r['field_calibrator_model']={'available':False,'version':'not-trained'};return r
before=prepare('slide_2_source.png','slide_2_view_risk.png')
# Validation inline
vjs=open(os.path.join(ROOT,'validate.js'),encoding='utf-8').read();vhtml=inline_page('validate.html',[('locale.js',locale),('validate.js',vjs)])
# Study pages
img='data:image/png;base64,'+base64.b64encode(open(os.path.join(ROOT,'assets','slide_2_source.png'),'rb').read()).decode();study={'schema':'backrow-field-study-v2','study_id':'TESTID','title':'BACKROW locked projector study','deck_name':'demo deck','room':{},'slides':{'1':img},'items':[{'id':'item001','slide':1,'source_size':{'width':1600,'height':900},'source_text':'Launch only if error rate stays below 2.5%.','box':[112,679,410,22],'camera_text':'Launch only if error rate stays below 25%','camera_confidence':92.2,'status':'at_risk','physical_baseline':{'status':'below'}}],'responses':[],'exposure_seconds':6.0,'presentation_order':['item001'],'presentation_events':[]};public={'schema':study['schema'],'study_id':'TESTID','title':study['title'],'deck_name':'demo deck','item_count':1,'exposure_seconds':6.0,'items':[{'id':'item001','sequence':1,'slide':1}]}
admin_stub=f"window.fetch=async(url,opt)=>({{ok:true,json:async()=>url.includes('/api/study/present')?({{ok:true}}):({{ok:true,study:{json.dumps(study)}}})}});"
reader_stub=f"window.fetch=async(url,opt)=>({{ok:true,json:async()=>url.includes('/public')?({{ok:true,study:{json.dumps(public)}}}):({{ok:true,saved:1}})}});"
adminjs=open(os.path.join(ROOT,'study_admin.js'),encoding='utf-8').read();readerjs=open(os.path.join(ROOT,'study.js'),encoding='utf-8').read()
adminhtml=inline_page('study_admin.html',[('locale.js',locale),('study_admin.js',admin_stub+adminjs)]).replace("const params=new URLSearchParams(location.search),studyId=params.get('study'),adminToken=params.get('token');","const params={get:(k)=>k==='study'?'TESTID':(k==='token'?'TOKEN123456789':null)},studyId=params.get('study'),adminToken=params.get('token');")
readerhtml=inline_page('study.html',[('locale.js',locale),('study.js',reader_stub+readerjs)]).replace("const q=new URLSearchParams(location.search);const studyId=q.get('study');","const q={get:(k)=>k==='study'?'TESTID':null};const studyId=q.get('study');")
errors=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    p=b.new_page(viewport={'width':1440,'height':1050});p.on('pageerror',lambda e:errors.append('main:'+str(e)));p.set_content(html,wait_until='load');p.click('#langBtn');assert 'Baris paling belakang' in p.locator('h1').inner_text();p.evaluate("""(before)=>{showWorkspace();setSource('assets/slide_2_source.png','Demo juri · sumber',false);viewData='assets/slide_2_view_risk.png';document.querySelector('#viewReady').classList.remove('hidden');document.querySelector('#viewName').textContent='Demo juri · kursi penonton';renderResults(before,{scroll:false});}""",before);assert 'BUKTI DARI PENONTON' in p.locator('#results').inner_text();p.screenshot(path=os.path.join(OUT,'BACKROW_V11_ID_RESULTS.png'),full_page=True)
    p2=b.new_page(viewport={'width':1440,'height':1000});p2.on('pageerror',lambda e:errors.append('validate:'+str(e)));p2.set_content(vhtml,wait_until='load');p2.click('#langBtn');assert 'Ukur baseline' in p2.locator('h1').inner_text();assert 'Waktu workflow' in p2.locator('#workflowBand').inner_text();p2.screenshot(path=os.path.join(OUT,'BACKROW_V11_ID_VALIDATION.png'),full_page=True)
    p3=b.new_page(viewport={'width':390,'height':844});p3.on('pageerror',lambda e:errors.append('reader:'+str(e)));p3.set_content(readerhtml,wait_until='load');p3.click('#langBtn');p3.wait_for_selector('#readerForm:not(.hidden)');body=p3.locator('body').inner_text();assert 'Baca proyektor' in body and 'Launch only' not in body and '25%' not in body;p3.screenshot(path=os.path.join(OUT,'BACKROW_V11_ID_READER.png'),full_page=True)
    p4=b.new_page(viewport={'width':1440,'height':1000});p4.on('pageerror',lambda e:errors.append('admin:'+str(e)));p4.set_content(adminhtml,wait_until='load');p4.click('#langBtn');p4.wait_for_selector('#projectionStage:not(.hidden)');assert 'PRESENTER STUDI LAPANGAN' in p4.locator('body').inner_text();p4.locator('.studyTruth details').evaluate('(e)=>e.open=true');p4.screenshot(path=os.path.join(OUT,'BACKROW_V11_ID_ADMIN.png'),full_page=True)
    b.close()
out={'ok':not errors,'pageerrors':errors,'indonesian_main':True,'indonesian_validation':True,'indonesian_reader_truth_hidden':True,'indonesian_admin':True,'screenshots':['BACKROW_V11_ID_RESULTS.png','BACKROW_V11_ID_VALIDATION.png','BACKROW_V11_ID_READER.png','BACKROW_V11_ID_ADMIN.png']};print(json.dumps(out,indent=2));json.dump(out,open(os.path.join(ROOT,'docs','browser_id_e2e_verification.json'),'w'),indent=2)
if errors:raise SystemExit(errors)
