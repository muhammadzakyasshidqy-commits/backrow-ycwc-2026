import requests, json
BASE='http://127.0.0.1:8098'
r=requests.get(BASE+'/',timeout=10)
assert r.status_code==200 and '<title>BACKROW' in r.text
assert r.headers.get('X-Content-Type-Options')=='nosniff'
assert 'camera=(self)' in r.headers.get('Permissions-Policy','')
csp=r.headers.get('Content-Security-Policy','');assert "object-src 'none'" in csp;assert "frame-ancestors 'self'" in csp
assert 'media-src' in csp and 'storage.googleapis.com' not in csp
assert r.headers.get('X-Frame-Options')=='SAMEORIGIN';assert r.headers.get('Cross-Origin-Opener-Policy')=='same-origin'
h=requests.get(BASE+'/api/health',timeout=10).json();assert h['ok'] and 'tesseract' in h['engine'].lower()
assert h.get('audiencenet',{}).get('available') is True
# API refuses missing/invalid payload rather than pretending success.
bad=requests.post(BASE+'/api/analyze',json={'source':'bad','view':'bad'},timeout=10)
assert bad.status_code==400 and not bad.json()['ok']
# Encoded traversal must never escape the project static root.
trav=requests.get(BASE+'/%2e%2e/server.py',timeout=10)
assert trav.status_code==404
out={'ok':True,'index':r.status_code,'engine':h['engine'],'audiencenet':h['audiencenet']['version'],'field_calibrator_available':h.get('field_calibrator',{}).get('available',False),'invalid_input_rejected':True,'path_traversal_rejected':True,'csp':True};print(json.dumps(out));json.dump(out,open('docs/http_smoke_verification.json','w'),indent=2)
