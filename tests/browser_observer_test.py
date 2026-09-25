from pathlib import Path
import json,re
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'preview';OUT.mkdir(exist_ok=True)
html=(ROOT/'observer.html').read_text();css=(ROOT/'styles.css').read_text();js=(ROOT/'observer.js').read_text()
html=re.sub(r'<link rel="stylesheet" href="styles.css"\s*/?>',f'<style>{css}</style>',html)
stub="""window.fetch=async(url,opt)=>{if(String(url).includes('/api/observer/join'))return {ok:true,json:async()=>({ok:true,session_id:'SESSION123456',observer_token:'TOKEN123456789',deck_name:'YCWC final deck'})};if(String(url).includes('/public'))return {ok:true,json:async()=>({ok:true,session:{deck_name:'YCWC final deck'}})};if(String(url).includes('/api/observer/frame'))return {ok:true,json:async()=>({ok:true,result:{matched_slide_index:1,counts:{at_risk:2,watch:0,supported:6}}})};return {ok:false,json:async()=>({ok:false,error:'stub'})}};"""
html=html.replace('<script src="observer.js"></script>',f'<script>{stub}</script><script>{js}</script>')
errs=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 p=b.new_page(viewport={'width':390,'height':844});p.on('pageerror',lambda e:errs.append(str(e)));p.set_content(html,wait_until='load');p.wait_for_timeout(100);assert p.locator('#joinPanel').is_visible();assert not p.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth');p.screenshot(path=str(OUT/'BACKROW_V11_OBSERVER_PAIR.png'),full_page=True)
 p.fill('#joinCode','482193');p.click('#joinBtn');p.wait_for_selector('#capturePanel:not(.hidden)');assert 'YCWC FINAL DECK' in p.locator('#deckName').inner_text();p.screenshot(path=str(OUT/'BACKROW_V11_OBSERVER_CAPTURE.png'),full_page=True)
 p.click('#langBtn');assert 'Berdiri di posisi penonton' in p.locator('#title').inner_text();b.close()
out={'ok':not errs,'pairing_ui':True,'capture_ui':True,'mobile_overflow':False,'bilingual':True,'pageerrors':errs,'framing_guide':'frameGuide' in html,'stable_scan_logic':all(x in js for x in ['probeFrame','probeDelta','stableHits','lastSentProbe','const sent=await send(true)','if(sent)']),'screenshots':['BACKROW_V11_OBSERVER_PAIR.png','BACKROW_V11_OBSERVER_CAPTURE.png']};print(json.dumps(out,indent=2));json.dump(out,open(ROOT/'docs'/'browser_observer_verification.json','w'),indent=2)
if errs:raise SystemExit(errs)
