"""Native save/readback/fail-closed smoke; deliberately no model credentials."""
import datetime as dt,json,sys,time
import host
from host import v
import live as t
from run import enter
v.check_test_isolation()
def wait_card():
    until=time.monotonic()+12
    while time.monotonic()<until:
        if any(x.get('i')=='start_input' for x in json.loads(v.request('/snap'))['s']):return
        time.sleep(.2)
    raise RuntimeError('Native Card did not mount')
def begin(name):
    wait_card();assert not (t.APP/'schedule.txt').exists(),'Must start empty'
    stamp=dt.datetime.fromtimestamp(time.time()+86400,dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    saved=t.create('Synthetic Stage 4 smoke '+host.host,start=stamp,lat='60.39',lon='5.32')
    t.scroll(-4000);enter('title_input','Synthetic Stage 4 title edit '+host.host);v.click('Save activity');t.scroll(4000)
    assert t.wait({'READY'},15)=='READY'
    after=t.read('schedule.txt');assert after['start']==saved['start'] and after['end']==saved['end']
    v.save(name+'-before.json',{'classification':'NATIVE_SYNTHETIC_ACTIVITY_SAVE_NOT_USER_TRIAL','saved':saved,'after':after,'source_sha256':v.sha(v.R/'soak-signed-bundle/main.splash')})
    t.record(name+'-saved');v.click('Analyze with Agent');t.scroll(4000)
    assert t.wait({'FAILED'},30)=='FAILED'
    assert t.read('schedule.txt')==after
    t.record(name+'-initial-failure')
def failure(name):
    before=json.loads((v.E/(name+'-before.json')).read_text(encoding='utf-8'))['after']
    t.scroll(4000);assert t.wait({'FAILED'},30)=='FAILED'
    labels=t.labels();assert any('profile_unresolved' in x for x in labels),labels
    assert not any(x.get('t')=='Approve change' for x in json.loads(v.request('/snap'))['s'])
    assert t.read('schedule.txt')==before
    assert not list(v.CORE.rglob('tool_audit.jsonl'))
    t.record(name+'-missing-provider')
    v.save(name+'-result.json',{'classification':'NEW_STAGE4_NATIVE_LIVE_WEATHER_MISSING_PROVIDER_NO_MODEL_CALLED','source_sha256':v.sha(v.R/'soak-signed-bundle/main.splash'),'state':'FAILED','weather_source':t.read('weather.json')['source'],'activity_unchanged':True,'actual_record':before,'no_approval_button':True,'tool_audit_files':0,'provider_configuration':'ABSENT_NOT_COPIED'})
def reopen(name):
    before=t.read('schedule.txt');v.request('/click?x=101&y=118&wait=1');time.sleep(.3);v.click('Open');wait_card()
    verify(name,'actual_card_close_reopen')
def verify(name,kind='actual_host_restart'):
    wait_card();t.scroll(4000);assert t.wait({'READY'},15)=='READY';t.scroll(-4000)
    actual=t.read('schedule.txt');before=json.loads((v.E/(name+'-before.json')).read_text(encoding='utf-8'))['after'];assert actual==before
    fields={x['i']:x.get('t') for x in json.loads(v.request('/snap'))['s'] if x.get('ty')=='TextInput'}
    stamp=dt.datetime.fromtimestamp(actual['start'],dt.timezone(dt.timedelta(hours=8))).strftime('%Y-%m-%d %H:%M')
    assert fields['start_input']==stamp and fields['title_input']==actual['title']
    t.record(name+'-'+kind);v.save(name+'-'+kind+'-result.json',{'classification':'NEW_STAGE4_NATIVE_SYNTHETIC_ACTIVITY_PERSISTENCE','unchanged':True,'fields':fields,'source_sha256':v.sha(v.R/'soak-signed-bundle/main.splash')})
if __name__=='__main__':globals()[sys.argv[1]](sys.argv[2])
