#!/usr/bin/env python3
from __future__ import annotations
import base64, os, re, json
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
OUT=os.path.join(ROOT,'preview_v11');os.makedirs(OUT,exist_ok=True)
html=open(os.path.join(ROOT,'present.html'),encoding='utf-8').read()
css=open(os.path.join(ROOT,'present.css'),encoding='utf-8').read()
js=open(os.path.join(ROOT,'present.js'),encoding='utf-8').read()
html=re.sub(r'<link rel="stylesheet" href="present.css"\s*/?>',f'<style>{css}</style>',html)
for rel in ['assets/hero_source_detail.png','assets/hero_audience_detail.png','assets/slide_2_view_risk.png','assets/slide_2_view_fixed.png']:
    raw=base64.b64encode(open(os.path.join(ROOT,rel),'rb').read()).decode('ascii')
    html=html.replace(rel,'data:image/png;base64,'+raw)
html=html.replace('<iframe id="productFrame" src="/?lang=en" title="BACKROW live product"></iframe>','<iframe id="productFrame" title="BACKROW live product"></iframe>')
html=html.replace('<script src="present.js"></script>',f'<script>{js}</script>')
errors=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    p=b.new_page(viewport={'width':1440,'height':900});p.on('pageerror',lambda e:errors.append(str(e)))
    p.set_content(html,wait_until='load',timeout=20000);p.wait_for_timeout(100)
    assert 'audience sees the room' in p.locator('#introTitle').inner_text().lower()
    assert not p.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth')
    p.click('#idBtn');assert 'Penonton melihat ruangan' in p.locator('#introTitle').inner_text()
    p.click('#enBtn');p.click('#nextBtn');assert 'information changed' in p.locator('#evTitle').inner_text().lower()
    p.evaluate('showStep(3)');assert 'AudienceNet 2.0' in p.locator('.stack').inner_text()
    p.evaluate('showStep(5)');assert p.locator('#validationScene').evaluate('(e)=>e.classList.contains(\"active\")');assert 'human eyesight' in p.locator('#valTitle').inner_text().lower();p.evaluate('showStep(6)');assert 'CHOOSE A SLIDE' in p.locator('.choose').inner_text().upper()
    m=b.new_page(viewport={'width':390,'height':844});m.set_content(html,wait_until='load');m.wait_for_timeout(100)
    assert not m.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth')
    m.close();b.close()
assert js.count('mcp-preview') == 0
assert 'speakLocal' in js and 'SpeechSynthesisUtterance' in js
assert 'storage.googleapis.com' not in js and 'new Audio(' not in js
out={'ok':not errors,'desktop_overflow':False,'mobile_overflow':False,'pageerrors':errors,'scenes':7,'bilingual':True,'external_voice_segments':0,'local_voice_rehearsal':True,'paid_plugin_dependency':False,'live_product_hook':'same-origin iframe + loadJudgeDemo/runFixRescanDemo'}
json.dump(out,open(os.path.join(ROOT,'docs','presenter_mode_verification.json'),'w'),indent=2)
print(json.dumps(out,indent=2))
if errors:raise SystemExit(errors)
