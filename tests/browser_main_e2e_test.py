#!/usr/bin/env python3
from __future__ import annotations
import base64,json,os,re,sys,time
import cv2
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));sys.path.insert(0,ROOT);OUT=os.path.join(ROOT,'preview');os.makedirs(OUT,exist_ok=True)
from vision_engine import analyze,encode_png_b64
room={'farthest_seat_m':8.4,'image_height_m':1.8}
def prepare(src,view):
    t=time.perf_counter();r=analyze(cv2.imread(os.path.join(ROOT,'assets',src)),cv2.imread(os.path.join(ROOT,'assets',view)),max_lines=18,room_config=room);r['latency_ms']=round((time.perf_counter()-t)*1000);r['overlay']='data:image/png;base64,'+encode_png_b64(r['overlay']);r['rectified']='data:image/png;base64,'+encode_png_b64(r['rectified']);r['engine']='AudienceNet custom MLP + Tesseract 5 LSTM + ORB/RANSAC + transparent BDM source baseline';r['claim_boundary']='Camera recoverability + source geometry evidence; human probability requires field calibration.';r['audiencenet_model']={'available':True,'version':'AudienceNet-2.0.0'};r['field_calibrator_model']={'available':False,'version':'not-trained'};return r
before=prepare('slide_2_source.png','slide_2_view_risk.png');after=prepare('slide_2_source_fixed.png','slide_2_view_fixed.png')
html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read();css=open(os.path.join(ROOT,'styles.css'),encoding='utf-8').read();js=open(os.path.join(ROOT,'app.js'),encoding='utf-8').read();html=re.sub(r'<link rel="stylesheet" href="styles.css"\s*/?>',f'<style>{css}</style>',html)
for rel in ['assets/hero_source_detail.png','assets/hero_audience_detail.png']:
    raw=base64.b64encode(open(os.path.join(ROOT,rel),'rb').read()).decode('ascii')
    html=html.replace(rel,'data:image/png;base64,'+raw)
health={'ok':True,'engine':'tesseract 5.5.0','audiencenet':{'available':True,'version':'AudienceNet-2.0.0'}}
stub=f"window.fetch=async(url,opt)=>({{ok:true,json:async()=>String(url).includes('/api/health')?{json.dumps(health)}:({{ok:true}})}});"
html=html.replace('<script src="app.js"></script>',f'<script>{stub}</script><script>{js}</script>')
errors=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    p=b.new_page(viewport={'width':1440,'height':1050});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(html,wait_until='load',timeout=20000);p.wait_for_timeout(100)
    assert p.locator('#engineState').inner_text().strip()=='ENGINE READY';assert 'Can the last row still read it?' in p.locator('h1').inner_text();assert not p.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth');p.screenshot(path=os.path.join(OUT,'BACKROW_V11_LANDING.png'),full_page=True)
    p.evaluate("""({before,after})=>{showWorkspace();document.querySelector('#distanceInput').value='8.4';document.querySelector('#imageHeightInput').value='1.8';document.querySelector('#roomNote').classList.remove('hidden');setSource('assets/slide_2_source.png','Judge demo · source',false);viewData='assets/slide_2_view_risk.png';document.querySelector('#viewReady').classList.remove('hidden');document.querySelector('#viewName').textContent='Judge demo · audience seat';window.__queue=[after];window.analyzeFrame=async()=>window.__queue.shift();renderResults(before,{scroll:false});}""",{'before':before,'after':after})
    counts=p.locator('#counts').inner_text();ledger=p.locator('#ledgerList').inner_text();assert '2' in counts and 'at risk' in counts.lower();assert '2.5%' in ledger and '25%' in ledger;p.screenshot(path=os.path.join(OUT,'BACKROW_V11_RESULTS.png'),full_page=True)
    p.click('#fixDemoBtn');p.wait_for_function("document.querySelector('.countPill.risk strong')?.textContent.trim()==='0'",timeout=10000);p.wait_for_timeout(100);delta=p.locator('#beforeAfter').inner_text();assert 'AFTER 0 risk' in delta; p.evaluate("document.documentElement.style.scrollBehavior='auto';window.scrollTo(0,0)");p.screenshot(path=os.path.join(OUT,'BACKROW_V11_FIXED_RESCAN.png'),full_page=True)
    m=b.new_page(viewport={'width':390,'height':844});m.set_content(html,wait_until='load');m.wait_for_timeout(100);assert m.locator('#engineState').inner_text().strip()=='ENGINE READY';assert not m.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth');m.screenshot(path=os.path.join(OUT,'BACKROW_V11_MOBILE.png'),full_page=True);m.click('#langBtn');assert 'Baris paling belakang' in m.locator('h1').inner_text();m.close();b.close()
out={'ok':not errors,'engine_ready':True,'desktop_horizontal_overflow':False,'mobile_horizontal_overflow':False,'judge_counts':counts,'fix_rescan_delta':delta,'pageerrors':errors,'screenshots':['BACKROW_V11_LANDING.png','BACKROW_V11_RESULTS.png','BACKROW_V11_FIXED_RESCAN.png','BACKROW_V11_MOBILE.png']};print(json.dumps(out,indent=2));json.dump(out,open(os.path.join(ROOT,'docs','browser_main_e2e_verification.json'),'w'),indent=2)
if errors:raise SystemExit(errors)
