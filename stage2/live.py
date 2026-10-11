"""Real RC2 UI acceptance on isolated generated test data, never a model fixture."""
import contextlib, io, json, time, sys
from run import v, enter, WORK

REV = 'soak-'
APP = v.R / (REV+'business-apps/ripple')
STATES = {'READY','EMPTY','LOADING','ANALYZING','SAVING','EXECUTING','VERIFYING','AWAITING_APPROVAL','COMPLETED','FAILED','STALE','CANCELLED','DECLINED','PARTIAL','NO_CHANGE','NO_CANDIDATE'}
def read(name): return json.loads((APP/name).read_text(encoding='utf-8'))
def labels(): return [x.get('t','') for x in json.loads(v.request('/snap'))['s'] if x.get('ty')=='Label']
def status(): return next((t for t in reversed(labels()) if t in STATES),None)
def record(label):
    with contextlib.redirect_stdout(io.StringIO()): v.snap(label); v.state(label,revision=REV)
def scroll(dy):
    v.request('/m?k=scroll&x=450&y=500&dy='+str(dy)+'&wait=1');time.sleep(.25)
def wait(states,seconds=95):
    until=time.monotonic()+seconds
    while time.monotonic()<until:
        s=status()
        if s in states:return s
        time.sleep(.5)
    raise RuntimeError(('UI deadline',labels()[-12:]))
def create(title,start='2026-10-14 21:00',duration='60',lat='47.61',lon='-122.33'):
    scroll(-4000)
    for key,text in [('title_input',title),('start_input',start),('duration',duration),('latitude',lat),('longitude',lon)]:enter(key,text);time.sleep(.12)
    v.click('Save activity');time.sleep(.25)
    current=read('schedule.txt');assert current['title']==title,current
    scroll(4000);s=wait({'READY','STALE','FAILED','PARTIAL'},15);assert s in {'READY','STALE'},(s,labels()[-6:])
    return current
def decision(label):
    scroll(4000); s=wait({'AWAITING_APPROVAL','FAILED','NO_CHANGE','NO_CANDIDATE','STALE'})
    scroll(4000)
    if not (v.E/(label+'.json')).exists():record(label)
    assert s in {'AWAITING_APPROVAL','NO_CHANGE','NO_CANDIDATE'},(s,labels()[-10:])
    session=read('agent-session.json')
    if not (v.E/(label+'-kernel.json')).exists():
        with contextlib.redirect_stdout(io.StringIO()):v.capture(label)
    kernel=json.loads((v.E/(label+'-kernel.json')).read_text())
    names=[a['tool'] for a in kernel['tool_audits'] if a['outcome']=='ok' and a['decision']=='allowed']
    assert 'ripple.context.read' in names,names
    if s != 'NO_CHANGE':assert 'ripple.slots.search' in names,names
    return s,dict(session,session_id=kernel['session_id'],turn_id=kernel['turn_id'],tool_denials=[a for a in kernel['tool_audits'] if a['outcome']!='ok']),kernel

def approval(label):
    s,session,kernel=decision(label)
    assert s=='AWAITING_APPROVAL',(s,labels()[-10:])
    choice=read('agent-choice.json')
    assert choice['task_id'] in json.dumps(kernel) and choice['candidate_id'] in json.dumps(kernel)
    return choice,session
def finish(round_number, before, duplicate=False):
    name='soak-'+str(round_number)
    s,session,kernel=decision(name+'-approval')
    if s in {'NO_CHANGE','NO_CANDIDATE'}:
        after=read('schedule.txt');assert after==before
        record(name+'-result')
        v.save(name+'-readback.json',{'classification':'REAL_UI_REAL_DEEPSEEK_REAL_OPEN_METEO_INDEPENDENT_OS_READ','at_utc':v.now(),'app_version':read_manifest()['version'],'source_sha256':v.sha(WORK/'stage1/bundle/main.splash'),'session':session,'before':before,'after':after,'ui_status':s,'activity_unchanged':True,'storage_bytes':sum(p.stat().st_size for p in APP.rglob('*') if p.is_file()),'approval_clicked':False})
        print(name,s,'activity unchanged',session['turn_id'],flush=True)
        return
    choice=read('agent-choice.json')
    assert choice['task_id'] in json.dumps(kernel) and choice['candidate_id'] in json.dumps(kernel)
    assert json.loads(choice['before'])==before
    if duplicate:
        button=next(x for x in json.loads(v.request('/snap'))['s'] if x.get('ty')=='Button' and x.get('t')=='Approve change')
        x,y,w,h=button['r'];path=f'/click?x={x+w/2}&y={y+h/2}&wait=1'
        v.request(path);v.request(path)
    else:v.click('Approve change')
    s=wait({'COMPLETED','FAILED','PARTIAL','STALE'},15);record(name+'-result')
    after=read('schedule.txt');expected=json.loads(choice['expected']);receipt=read('execution.json')
    assert s=='COMPLETED',(s,labels()[-8:]);assert after==expected
    assert after['event_id']==before['event_id'] and after['revision']==before['revision']+1
    assert after['title']==before['title'] and after['end']-after['start']==before['end']-before['start']
    assert receipt['status']=='COMPLETED' and json.loads(receipt['before'])==before
    v.save(name+'-readback.json',{'classification':'REAL_UI_REAL_DEEPSEEK_REAL_OPEN_METEO_INDEPENDENT_OS_READ','at_utc':v.now(),'app_version':read_manifest()['version'],'source_sha256':v.sha(WORK/'stage1/bundle/main.splash'),'session':session,'choice':choice,'before':before,'after':after,'execution_receipt':receipt,'ui_status':s,'storage_bytes':sum(p.stat().st_size for p in APP.rglob('*') if p.is_file()),'duplicate_approval_click':duplicate})
    print(name,'COMPLETED',session,'revision',after['revision'],flush=True)
def read_manifest():return json.loads((WORK/'stage1/bundle/manifest.json').read_text())
if __name__=='__main__':
    mode=sys.argv[1]
    if mode=='finish':finish(int(sys.argv[2]),read('schedule.txt'),duplicate='--duplicate' in sys.argv)
    elif mode=='round':
        n=int(sys.argv[2]);before=create('Current final soak round '+str(n));record('soak-'+str(n)+'-created');v.click('Analyze with Agent')
        if '--duplicate-analysis' in sys.argv:
            scroll(4000);assert wait({'ANALYZING'},30)=='ANALYZING';v.click('Analyze with Agent')
        finish(n,before,duplicate='--duplicate' in sys.argv)
