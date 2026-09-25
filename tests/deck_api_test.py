from pathlib import Path
import base64, json, requests, time
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8098'

def dataurl(path,mime):
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()

pdf=dataurl(ROOT/'assets/demo_deck.pdf','application/pdf')
r=requests.post(BASE+'/api/render_pdf',json={'pdf':pdf},timeout=60).json(); assert r['ok'],r
assert r['count']==3
deck=r['deckId']
rows=[]
for idx,name in enumerate(['slide_1_view_good.png','slide_2_view_risk.png','slide_3_view_glare.png']):
    view=dataurl(ROOT/'assets'/name,'image/png')
    dm=requests.post(BASE+'/api/deck_match',json={'view':view,'deckId':deck},timeout=30).json();assert dm['ok'],dm;assert dm['matched_slide_index']==idx,(idx,dm)
    t=time.perf_counter()
    j=requests.post(BASE+'/api/analyze',json={'view':view,'deckId':deck,'autoMatch':True,'maxLines':18},timeout=90).json()
    assert j['ok'],j
    res=j['result']; rows.append({'expected':idx,'matched':res['matched_slide_index'],'counts':res['counts'],'deck_match_ms':res.get('deck_match_ms'),'analysis_ms':res['latency_ms'],'wall_ms':round((time.perf_counter()-t)*1000),'match_only_ms':dm.get('deck_match_ms')})
    assert res['matched_slide_index']==idx,(idx,res['matched_slide_index'])
assert rows[1]['counts']['at_risk']>=1,rows[1]
out={'ok':True,'deckId_created':True,'auto_match':rows};print(json.dumps(out,indent=2));json.dump(out,open(ROOT/'docs'/'deck_api_verification.json','w'),indent=2)
