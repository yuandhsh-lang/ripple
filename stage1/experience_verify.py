"""Stage 1 official RC6 UI driver. Synthetic test data; no Provider credentials.

Run with python -X utf8 -B (the reused Windows driver reads UTF-8 paths).
Set RIPPLE_STAGE1_AUDIT to a fresh sibling _audits/Ripple/Stage1-* directory.
Use a new p4-stage1-* run initialized by stage4/new_run.ps1 (empty core).
The application bundle is copied only for local test signing. No host changes.
"""
import datetime as dt,json,os,sys,time,urllib.parse
from pathlib import Path
import verify as v

P=Path(__file__).resolve().parent.parent
A=Path(os.environ['RIPPLE_STAGE1_AUDIT']).resolve()
assert A.parent == (P.parent/'_audits/Ripple').resolve() and A.name.startswith('Stage1-')
run=os.environ['RIPPLE_TEST_RUN'];assert run.startswith('p4-stage1-') and all(c.islower() or c.isdigit() or c=='-' for c in run)
evidence_name=os.environ.get('RIPPLE_STAGE1_HOST_EVIDENCE','rc6')
assert evidence_name.startswith('rc6') and all(c.islower() or c.isdigit() or c=='-' for c in evidence_name)
v.R=P/'stage2/runtime/runs'/run;v.E=A/evidence_name;v.E.mkdir(exist_ok=True)
v.CORE=v.R/'kernel-core';v.RC2=P/'stage4/runtime/rc6';v.HUB=P/'stage4/runtime/hub.exe';v.PORT=8186
v.check_test_isolation()
APP=v.R/'s1-business-apps/ripple'

def snapshot():return json.loads(v.request('/snap'))['s']
def scroll(dy):v.request(f'/m?k=scroll&x=850&y=620&dy={dy}&wait=1')
def labels():return [x.get('t','') for x in snapshot() if x.get('ty')=='Label']
def wait_text(text,seconds=25):
 end=time.monotonic()+seconds
 while time.monotonic()<end:
  if any(text in t for t in labels()):return
  time.sleep(.3)
 raise RuntimeError('UI text not observed: '+text)
def click_contains(text):
 matches=[x for x in snapshot() if x.get('ty')=='Button' and text in x.get('t','')]
 if len(matches)!=1:raise RuntimeError((text,len(matches)))
 x,y,w,h=matches[0]['r'];v.request(f'/click?x={x+w/2}&y={y+h/2}&wait=1')
def record(name):
 v.snap(name);v.state(name,revision='s1-')
def read(name):return json.loads((APP/name).read_text(encoding='utf-8'))
def create():
 assert not (APP/'schedule.txt').exists(),'Fresh synthetic activity only'
 scroll(-5000);v.enter('title_input','Synthetic Stage 1 park walk');v.enter('city_input','深圳');v.click('搜索城市')
 wait_text('请逐项核对',25);v.snap('live-city-results')
 click_contains('广东 / 深圳 / Asia/Shanghai');wait_text('已选择：')
 day=(dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))+dt.timedelta(days=1)).strftime('%Y-%m-%d')
 v.enter('start_input',day+' 15:00');v.enter('duration','60');v.enter('available_start','09:00');v.enter('available_end','14:00')
 v.click('Save activity');scroll(1500);wait_text('READY');saved()
def saved():
 before=read('schedule.txt')
 assert before['schema']==3 and before['location']['id']==1795565 and before['timezone']=='Asia/Shanghai'
 assert before['availability']['max_end']-before['availability']['min_start']==5*3600
 record('live-saved');v.save('live-created.json',{'classification':'OFFICIAL_RC6_SYNTHETIC_USER_INPUT_LIVE_GEOCODING','schedule':before,'source_sha256':v.sha(P/'stage1/bundle/main.splash')})
def weather():
 before=read('schedule.txt');scroll(4000);v.click('查询天气与可用时段');wait_text('LIVE Open-Meteo',25)
 end=time.monotonic()+15
 while time.monotonic()<end:
  state=next((s for s in labels() if s in ['NO_CHANGE','CANDIDATES','NO_CANDIDATE','FAILED']),None)
  if state:break
  time.sleep(.2)
 else:raise RuntimeError('No terminal weather state')
 w=read('weather.json');assert w['source']=='LIVE';assert read('schedule.txt')==before
 record('live-weather');v.save('live-weather-result.json',{'classification':'OFFICIAL_RC6_LIVE_WEATHER_NO_MODEL','state':state,'weather_source':w['source'],'record_unchanged':True,'source_sha256':v.sha(P/'stage1/bundle/main.splash')})
def verify_reopen(label):
 scroll(-5000)
 end=time.monotonic()+15
 while time.monotonic()<end:
  if any(x.get('i')=='available_start' for x in snapshot()):break
  time.sleep(.2)
 result=v.E/'live-execution-result.json'
 original=json.loads(result.read_text(encoding='utf-8'))['actual_readback'] if result.exists() else json.loads((v.E/'live-created.json').read_text(encoding='utf-8'))['schedule']
 actual=read('schedule.txt');assert original==actual
 fields={x['i']:x.get('t') for x in snapshot() if x.get('ty')=='TextInput'}
 zone=dt.timezone(dt.timedelta(hours=8))
 assert fields['available_start']==dt.datetime.fromtimestamp(actual['availability']['min_start'],zone).strftime('%H:%M')
 assert fields['available_end']==dt.datetime.fromtimestamp(actual['availability']['max_end'],zone).strftime('%H:%M')
 assert fields['start_input']==dt.datetime.fromtimestamp(actual['start'],zone).strftime('%Y-%m-%d %H:%M')
 record(label);v.save(label+'-result.json',{'same_schedule':True,'window_fields_restored':True,'city':actual['location'],'source_sha256':v.sha(P/'stage1/bundle/main.splash')})
def rainy():
 zone=dt.timezone(dt.timedelta(hours=8));w=read('weather.json')
 def local(t):return dt.datetime.fromtimestamp(t,zone)
 def wet(h):return h['rain']>=1 or h['chance']>=50 or 51<=h['code']<=67 or 80<=h['code']<=82 or h['code']>=95
 pair=None
 for h in w['hours']:
  if h['start']<=time.time() or not wet(h) or not 8<=local(h['start']).hour<=20:continue
  safe=next((x for x in w['hours'] if x['start']>time.time() and not wet(x) and local(x['start']).date()==local(h['start']).date() and 8<=local(x['start']).hour<=20),None)
  if safe:pair=(h,safe);break
 assert pair,'No real future rain/dry pair available; do not fabricate one'
 rain,safe=pair;v.save('live-selected-forecast.json',{'classification':'SYNTHETIC_ACTIVITY_CHOSEN_FROM_ACTUAL_LIVE_FORECAST_NOT_WEATHER_FIXTURE','rain':rain,'dry':safe,'forecast_sha256':v.sha(APP/'weather.json')})
 scroll(-5000);v.enter('start_input',local(rain['start']).strftime('%Y-%m-%d %H:%M'));v.enter('available_start',local(safe['start']).strftime('%H:%M'));v.enter('available_end',local(safe['end']).strftime('%H:%M'))
 scroll(450);v.click('Save activity');scroll(4000);wait_text('READY');before=read('schedule.txt')
 v.click('查询天气与可用时段');wait_text('CANDIDATES',25);scroll(4000);record('live-candidates')
 buttons=[x for x in snapshot() if x.get('ty')=='Button' and x.get('t','').startswith('选择 ')]
 assert len(buttons)==1;v.click(buttons[0]['t']);scroll(4000);wait_text('AWAITING_APPROVAL');record('live-unapproved')
 assert read('schedule.txt')==before
 # Edit the actual native input while approval is pending. The old approval disappears.
 scroll(-5000);v.enter('available_end',local(safe['end']+1800).strftime('%H:%M'));scroll(4000);wait_text('STALE')
 assert not any(x.get('t')=='Approve change' for x in snapshot());assert read('schedule.txt')==before;record('live-window-draft-stale')
 scroll(-5000);scroll(450);v.click('Save activity');scroll(4000);wait_text('READY');before=read('schedule.txt')
 v.click('查询天气与可用时段');wait_text('CANDIDATES',25);scroll(4000)
 buttons=[x for x in snapshot() if x.get('ty')=='Button' and x.get('t','').startswith('选择 ')];assert buttons
 v.click(buttons[0]['t']);scroll(4000);wait_text('AWAITING_APPROVAL');record('live-final-proposal')
 assert read('schedule.txt')==before;v.click('Approve change');scroll(4000);wait_text('COMPLETED',15);record('live-completed')
 after=read('schedule.txt');receipt=read('execution.json');expected=json.loads(receipt['expected'])
 assert after==expected and json.loads(receipt['before'])==before and receipt['status']=='COMPLETED'
 assert after['revision']==before['revision']+1 and after['start']>=before['availability']['min_start'] and after['end']<=before['availability']['max_end']
 for key in ['event_id','title','lat','lon','location','timezone','availability']:assert after[key]==before[key]
 v.save('live-execution-result.json',{'classification':'OFFICIAL_UNMODIFIED_RC6_LIVE_WEATHER_USER_SELECTED_CANDIDATE_NO_MODEL','before':before,'actual_readback':after,'receipt':receipt,'no_write_before_approval':True,'native_window_draft_invalidated_old_approval':True,'source_sha256':v.sha(P/'stage1/bundle/main.splash')})
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='prepare':v.prepare('s1-')
 elif mode=='start':v.start(sys.argv[2],reuse='--reuse' in sys.argv,revision='s1-')
 elif mode=='snapshot':v.snap(sys.argv[2])
 elif mode=='request':print(v.request(sys.argv[2]).decode())
 elif mode=='click':v.click(sys.argv[2])
 elif mode=='enter':v.enter(sys.argv[2],sys.argv[3])
 elif mode=='create':create()
 elif mode=='saved':saved()
 elif mode=='weather':weather()
 elif mode=='reopen':verify_reopen(sys.argv[2])
 elif mode=='rainy':rainy()
