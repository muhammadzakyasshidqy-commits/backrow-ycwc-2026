#!/usr/bin/env python3
from __future__ import annotations
import base64,json,os,re
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
css=open(os.path.join(ROOT,'styles.css'),encoding='utf-8').read().lower()
html=open(os.path.join(ROOT,'index.html'),encoding='utf-8').read()
js=open(os.path.join(ROOT,'app.js'),encoding='utf-8').read()
# Explicit anti-template checks. These do not claim aesthetic quality; they prevent the specific
# decorative patterns intentionally removed in V3.
assert 'linear-gradient' not in css
assert 'radial-gradient' not in css
assert 'backdrop-filter' not in css
assert 'glassmorphism' not in html.lower()
assert 'trust score' not in html.lower()
assert 'assets/slide_2_view_risk.png' in html
assert 'assets/hero_source_detail.png' in html
assert 'assets/hero_audience_detail.png' in html
page_html=re.sub(r'<link rel="stylesheet" href="styles.css"\s*/?>',f'<style>{open(os.path.join(ROOT,"styles.css"),encoding="utf-8").read()}</style>',html)
for name in ['slide_2_view_risk.png','hero_source_detail.png','hero_audience_detail.png']:
    raw=open(os.path.join(ROOT,'assets',name),'rb').read();page_html=page_html.replace(f'assets/{name}','data:image/png;base64,'+base64.b64encode(raw).decode())
page_html=page_html.replace('<script src="app.js"></script>',f'<script>window.fetch=async()=>({{ok:true,json:async()=>({{ok:true}})}});</script><script>{js}</script>')
errors=[]
with sync_playwright() as pw:
    b=pw.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height in [(1440,1050),(390,844)]:
        p=b.new_page(viewport={'width':width,'height':height});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(page_html,wait_until='load')
        overflow=p.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
        assert overflow<=1,(width,overflow)
        assert p.locator('#startBtn').is_visible() and p.locator('#demoBtn').is_visible()
        assert p.locator('.proofContext img').get_attribute('alt')
        if width==390:
            p.click('#langBtn');assert 'Baris paling belakang' in p.locator('h1').inner_text()
        p.close()
    b.close()
assert not errors,errors
out={'ok':True,'desktop_horizontal_overflow':False,'mobile_horizontal_overflow':False,'decorative_gradients':False,'backdrop_filter':False,'real_evidence_hero':True,'bilingual_mobile':True,'pageerrors':errors}
print(json.dumps(out,indent=2))
json.dump(out,open(os.path.join(ROOT,'docs','ui_design_verification.json'),'w'),indent=2)
