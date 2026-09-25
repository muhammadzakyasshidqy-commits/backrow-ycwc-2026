from pathlib import Path
import base64, json, requests
ROOT=Path(__file__).resolve().parents[1]
BASE='http://127.0.0.1:8098'

def dataurl(path,mime):
    return f'data:{mime};base64,'+base64.b64encode(path.read_bytes()).decode()

pdf=dataurl(ROOT/'assets/demo_deck.pdf','application/pdf')
r=requests.post(BASE+'/api/render_pdf',json={'pdf':pdf},timeout=60).json(); assert r['ok'],r
deck=r['deckId']
c=requests.post(BASE+'/api/observer/create',json={'deckId':deck,'deck_name':'demo deck','room':{'farthest_seat_m':8.4,'image_height_m':1.8}},timeout=20).json();assert c['ok'],c
sid=c['session_id'];admin=c['admin_token'];observer_url=c['observer_path'];join_code=c['join_code']
assert 'token=' in observer_url and len(join_code)==6
join=requests.post(BASE+'/api/observer/join',json={'join_code':join_code},timeout=10).json();assert join['ok'] and join['session_id']==sid
reuse=requests.post(BASE+'/api/observer/join',json={'join_code':join_code},timeout=10);assert reuse.status_code==404 and not reuse.json().get('ok')
public=requests.get(BASE+f'/api/observer/{sid}/public',timeout=10).json();assert public['ok'];assert 'admin_token' not in json.dumps(public)
unauth=requests.get(BASE+f'/api/observer/{sid}/status',timeout=10);assert unauth.status_code==403
view=dataurl(ROOT/'assets/slide_2_view_risk.png','image/png')
from urllib.parse import urlparse,parse_qs
ot=join['observer_token'];assert ot==parse_qs(urlparse(observer_url).query)['token'][0]
f=requests.post(BASE+'/api/observer/frame',json={'session_id':sid,'observer_token':ot,'view':view},timeout=90).json();assert f['ok'],f
res=f['result'];assert res['matched_slide_index']==1,res;assert res['counts']['at_risk']>=1,res['counts']
status=requests.get(BASE+f'/api/observer/{sid}/status?token={admin}',timeout=10).json();assert status['ok'];ss=status['session'];assert ss['sequence']==1 and ss['latest']['matched_slide_index']==1
assert ss['observed_slides']==[2]
out={'ok':True,'session_pairing':True,'six_digit_join':True,'pairing_code_single_use':True,'public_secret_leak':False,'admin_status_protected':True,'remote_slide_match':2,'remote_counts':res['counts']}
print(json.dumps(out,indent=2));json.dump(out,open(ROOT/'docs'/'observer_api_verification.json','w'),indent=2)
