"""Native checks; live weather by default, explicitly labeled fault/weather fixtures."""
import datetime as dt
import json
import sys
import time
import urllib.request
import host
from host import v, WORK
import live as t
from run import enter

def choose():
    rows=[]
    for city,lat,lon in [('Bergen',60.39,5.32),('Seattle',47.61,-122.33)]:
        url=f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=weather_code,precipitation,precipitation_probability&forecast_days=7&timeformat=unixtime&timezone=GMT'
        raw=urllib.request.urlopen(url,timeout=25).read()
        (v.E/(city+'-live-weather.json')).write_bytes(raw)
        w=json.loads(raw)['hourly']; wet=[]; dry=[]
        for epoch,code,rain,chance in zip(w['time'],w['weather_code'],w['precipitation'],w['precipitation_probability']):
            if epoch <= time.time()+3600: continue
            row={'epoch':epoch,'stamp':dt.datetime.fromtimestamp(epoch,dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M'),'code':code,'rain':rain,'chance':chance}
            (wet if rain>=1 or chance>=50 or 51<=code<=67 or 80<=code<=82 or code>=95 else dry).append(row)
        rows.append({'city':city,'lat':lat,'lon':lon,'wet':wet,'dry':dry})
    v.save('live-weather-selection.json',rows)
    print([(r['city'],len(r['wet']),len(r['dry'])) for r in rows])

def setup(name,kind='wet'):
    rows=json.loads((v.E/'live-weather-selection.json').read_text())
    city=next(r for r in rows if r[kind] and r['dry'])
    row=city[kind][min(8,len(city[kind])-1)]
    before=t.create(name,start=row['stamp'],lat=str(city['lat']),lon=str(city['lon']))
    v.save(name+'-input.json',{'before':before,'selected_live_hour':row,'installed_source_sha256':v.sha(v.R/'soak-signed-bundle/main.splash')})
    t.record(name+'-created');v.click('Analyze with Agent')
    return before

def begin(name): setup(name)

def finish(name,expected_bug=False):
    before=json.loads((v.E/(name+'-input.json')).read_text())['before']
    choice,session=t.approval(name+'-approval')
    assert t.read('schedule.txt')==before
    button=next(x for x in json.loads(v.request('/snap'))['s'] if x.get('t')=='Approve change')
    x,y,w,h=button['r']; path=f'/click?x={x+w/2}&y={y+h/2}&wait=1'
    v.request(path);v.request(path)
    s=t.wait({'COMPLETED','PARTIAL','FAILED','STALE'},20)
    approved=t.read('schedule.txt');execution=t.read('execution.json')
    assert s=='COMPLETED' and approved==json.loads(choice['expected'])
    assert approved['revision']==before['revision']+1
    t.record(name+'-approved')
    t.scroll(-4000);enter('title_input',name+' title only');v.click('Save activity')
    t.scroll(4000);assert t.wait({'READY','FAILED','PARTIAL'},15)=='READY'
    saved=t.read('schedule.txt'); t.record(name+'-title-saved')
    result={'classification':'REAL_NATIVE_UI_REAL_MODEL_LIVE_WEATHER','host':host.host,'source_sha256':v.sha(v.R/'soak-signed-bundle/main.splash'),'before':before,'approved':approved,'after_title_only_save':saved,'execution':execution,'session':session,'duplicate_approval_revision_increment':approved['revision']-before['revision'],'time_preserved':saved['start']==approved['start'],'expected_baseline_bug':expected_bug}
    v.save(name+'-result.json',result)
    assert result['time_preserved'] != expected_bug
    if not expected_bug:
        t.scroll(-4000);v.click('Save activity');t.scroll(4000)
        assert t.wait({'READY','FAILED','PARTIAL'},15)=='READY'
        immediate=t.read('schedule.txt');assert immediate['start']==approved['start'] and immediate['end']==approved['end']
        v.save(name+'-immediate-save.json',{'before':saved,'after':immediate,'same_time':True})
    print(name,'baseline defect reproduced' if expected_bug else 'title-only/immediate/duplicate approval passed')

def decline(name):
    before=setup(name); t.approval(name+'-approval');v.click('Decline')
    assert t.wait({'DECLINED'},15)=='DECLINED';assert t.read('schedule.txt')==before
    t.record(name+'-declined');v.save(name+'-result.json',{'unchanged':True,'before':before,'after':t.read('schedule.txt')})

def stale(name):
    before=setup(name);t.approval(name+'-approval');t.scroll(-4000)
    enter('title_input',name+' explicit edit');v.click('Save activity');t.scroll(4000)
    assert t.wait({'STALE','FAILED','PARTIAL'},15)=='STALE'
    after=t.read('schedule.txt');assert after['start']==before['start']
    assert not any(x.get('t')=='Approve change' for x in json.loads(v.request('/snap'))['s'])
    t.record(name+'-stale');v.save(name+'-result.json',{'old_approval_unavailable':True,'before':before,'after':after})

def cancel(name):
    before=setup(name);t.scroll(4000);t.wait({'ANALYZING'},30);v.click('Cancel Agent');t.scroll(4000)
    assert t.wait({'CANCELLED'},20)=='CANCELLED';assert t.read('schedule.txt')==before
    t.record(name+'-cancelled');v.save(name+'-result.json',{'unchanged':True,'before':before,'after':t.read('schedule.txt')})

def draft(name):
    before=setup(name);choice,session=t.approval(name+'-approval')
    stamp=dt.datetime.fromtimestamp(before['start']+3600,dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    t.scroll(-4000);enter('title_input',name+' unsaved title');enter('start_input',stamp)
    t.scroll(4000);v.click('Approve change');assert t.wait({'COMPLETED'},20)=='COMPLETED'
    approved=t.read('schedule.txt');assert approved==json.loads(choice['expected'])
    t.scroll(-4000);fields={x['i']:x.get('t') for x in json.loads(v.request('/snap'))['s'] if x.get('ty')=='TextInput'}
    assert fields['title_input']==name+' unsaved title' and fields['start_input']==stamp,fields
    v.click('Save activity');t.scroll(4000);assert t.wait({'READY'},15)=='READY'
    after=t.read('schedule.txt');assert after['start']==before['start']+3600
    t.record(name+'-saved');v.save(name+'-result.json',{'unsaved_fields':fields,'approved':approved,'explicitly_saved':after,'draft_preserved':True})

def dry(name):
    before=setup(name,'dry');s,session,kernel=t.decision(name+'-decision')
    assert s=='NO_CHANGE' and t.read('schedule.txt')==before
    v.save(name+'-result.json',{'unchanged':True,'state':s,'before':before,'session':session})

def readback(name):
    before=setup(name);choice,session=t.approval(name+'-approval');original=(t.APP/'schedule.txt').read_bytes()
    v.click('Approve change');until=time.monotonic()+3;written=None
    while time.monotonic()<until:
        actual=(t.APP/'schedule.txt').read_bytes()
        if actual!=original:written=actual;break
        time.sleep(.005)
    assert written is not None and written.decode()==choice['expected']
    damaged=written.decode().replace(name,'Operator injected mismatch')
    (t.APP/'schedule.txt').write_text(damaged,encoding='utf-8')
    s=t.wait({'PARTIAL','COMPLETED'},5);t.record(name+'-mismatch')
    v.save(name+'-injection.json',{'classification':'REAL_MODEL_REAL_WRITE_OPERATOR_INJECTED_READBACK_MISMATCH','status':s,'written':written.decode(),'injected':damaged})
    assert s=='PARTIAL'
    t.scroll(4000);v.click('Inspect actual result');assert (t.APP/'schedule.txt').read_text()==damaged
    (t.APP/'schedule.txt').write_bytes(written);v.click('Inspect actual result');assert t.wait({'COMPLETED'},5)=='COMPLETED'
    t.record(name+'-restored');v.save(name+'-result.json',{'restored_exact_test_record':True,'after':t.read('schedule.txt'),'no_false_completed_on_mismatch':True})

def reopen(name):
    before=t.read('schedule.txt');t.record(name+'-before')
    v.request('/click?x=101&y=118&wait=1');time.sleep(.3);v.click('Open')
    until=time.monotonic()+10
    while time.monotonic()<until:
        if any(x.get('i')=='start_input' for x in json.loads(v.request('/snap'))['s']):break
        time.sleep(.2)
    verify_reopen(name)

def verify_reopen(name):
    before=json.loads(json.loads((v.E/(name+'-before-state.json')).read_text())['files']['schedule.txt']['content'])
    t.scroll(4000);s=t.wait({'READY','COMPLETED','PARTIAL','FAILED'},10)
    after=t.read('schedule.txt');assert before==after and s in {'READY','COMPLETED'}
    t.scroll(-4000);fields={x['i']:x.get('t') for x in json.loads(v.request('/snap'))['s'] if x.get('ty')=='TextInput'}
    expected=dt.datetime.fromtimestamp(after['start'],dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    assert fields['title_input']==after['title'] and fields['start_input']==expected
    t.record(name+'-reopened');v.save(name+'-result.json',{'before':before,'after':after,'fields':fields,'status':s,'actual_native_card_closed_and_reopened':True})

def provider_failure(name):
    before=json.loads((v.E/(sys.argv[3] if len(sys.argv)>3 else 'rc6-reopen-result.json')).read_text())['after']
    t.scroll(4000);assert t.wait({'FAILED'},20)=='FAILED'
    assert any('profile_unresolved' in x for x in t.labels())
    after=t.read('schedule.txt');assert after==before
    assert not list((v.R/'no-provider-core').rglob('tool_audit.jsonl'))
    t.record(name+'-checked')
    v.save(name+'-result.json',{'classification':'NATIVE_MISSING_PROVIDER_FAILURE_NO_MODEL_CALLED','before':before,'after':after,'status':'FAILED','new_core':str(v.R/'no-provider-core'),'tool_audit_files':0,'activity_unchanged':True,'shell_restart_record_preserved':True})

def no_candidate_fixture(name):
    previous=t.read('weather.json')['revision'] if (t.APP/'weather.json').exists() else None
    before=setup(name);until=time.monotonic()+20
    while time.monotonic()<until:
        weather=t.read('weather.json')
        if weather['revision']!=previous:break
        time.sleep(.01)
    else:raise RuntimeError('No new weather snapshot to replace in isolated test jail')
    weather['source']='FIXTURE';weather['revision']='stage3-all-wet-fixture-'+str(int(time.time()))
    for hour in weather['hours']:hour.update(code=61,rain=2,chance=100)
    assert t.APP.resolve().is_relative_to(v.R.resolve())
    (t.APP/'weather.json').write_text(json.dumps(weather),encoding='utf-8')
    v.save(name+'-fixture.json',{'classification':'OPERATOR_INJECTED_ALL_WET_WEATHER_FIXTURE','weather':weather})
    s,session,kernel=t.decision(name+'-decision')
    assert s=='NO_CANDIDATE' and t.read('schedule.txt')==before
    v.save(name+'-result.json',{'classification':'NATIVE_REAL_MODEL_WITH_EXPLICIT_FIXTURE_WEATHER','state':s,'unchanged':True,'before':before,'session':session})

if __name__=='__main__':
    v.check_test_isolation()
    mode=sys.argv[1]
    if mode=='choose':choose()
    elif mode=='finish':finish(sys.argv[2], '--baseline-bug' in sys.argv)
    else:globals()[mode](sys.argv[2])
