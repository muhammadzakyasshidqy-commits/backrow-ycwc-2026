from __future__ import annotations
import json,os,re
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'));OUT=os.path.join(ROOT,'preview');os.makedirs(OUT,exist_ok=True)
html=open(os.path.join(ROOT,'validate.html'),encoding='utf-8').read();css=open(os.path.join(ROOT,'styles.css'),encoding='utf-8').read();locale=open(os.path.join(ROOT,'locale.js'),encoding='utf-8').read();js=open(os.path.join(ROOT,'validate.js'),encoding='utf-8').read()
html=re.sub(r'<link rel="stylesheet" href="styles.css"\s*/?>',f'<style>{css}</style>',html).replace('<script src="locale.js"></script>',f'<script>{locale}</script>').replace('<script src="validate.js"></script>',f'<script>{js}</script>')
errs=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 p=b.new_page(viewport={'width':1440,'height':1000});p.on('pageerror',lambda e:errs.append(str(e)));p.set_content(html,wait_until='load');assert 'Measure the baselines' in p.locator('h1').inner_text();assert p.locator('#manualStart').is_visible();assert p.locator('#deckPdf').count()==1;p.screenshot(path=os.path.join(OUT,'BACKROW_FIELD_VALIDATION.png'),full_page=True)
 m=b.new_page(viewport={'width':390,'height':844});m.set_content(html,wait_until='load');overflow=m.evaluate('document.documentElement.scrollWidth>document.documentElement.clientWidth');assert not overflow;m.screenshot(path=os.path.join(OUT,'BACKROW_FIELD_VALIDATION_MOBILE.png'),full_page=True);b.close()
out={'ok':not errs,'pageerrors':errs,'desktop_horizontal_overflow':False,'mobile_horizontal_overflow':False,'screenshots':['BACKROW_FIELD_VALIDATION.png','BACKROW_FIELD_VALIDATION_MOBILE.png']};print(json.dumps(out,indent=2));json.dump(out,open(os.path.join(ROOT,'docs','browser_validation_verification.json'),'w'),indent=2)
if errs: raise SystemExit(errs)
