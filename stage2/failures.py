"""Native failure checks. Mutations target only this run's generated test jail."""
import hashlib,json,sys,time
import live as t
from run import v,enter
def check_jail():
    assert t.APP.resolve().is_relative_to((v.R/'soak-business-apps').resolve())
def digest():return v.sha(t.APP/'schedule.txt')
def result(name,before,expected):
    t.scroll(4000);s=t.wait(set(expected),20);t.record(name)
    after=digest();v.save(name+'-comparison.json',{'classification':'OFFICIAL_RC2_NATIVE_CURRENT_CODE','at_utc':v.now(),'source_sha256':v.sha(t.WORK/'stage1/bundle/main.splash'),'before_sha256':before,'after_sha256':after,'unchanged':before==after,'status':s});assert before==after
def plan(label):
    t.create(label);before=digest();v.click('Analyze with Agent');t.approval(label+'-approval');return before
if __name__=='__main__':
    check_jail();mode=sys.argv[1]
    if mode=='decline':
        before=plan('native-decline-current');v.click('Decline');result('native-declined-current',before,{'DECLINED'})
    elif mode=='stale':
        before=plan('native-stale-current');old=t.read('schedule.txt')
        edited=t.create('native-stale-edited');assert edited['event_id']==old['event_id'] and edited['revision']==old['revision']+1
        before=digest();result('native-stale-rejected',before,{'STALE'})
        assert not any(x.get('t')=='Approve change' for x in json.loads(v.request('/snap'))['s'])
        v.click('Replan once');t.approval('native-replan-new-approval');v.click('Decline');result('native-replan-declined',before,{'DECLINED'})
    elif mode=='cancel':
        t.create('native-cancel');before=digest()
        old_call=next(x.get('t') for x in json.loads(v.request('/snap'))['s'] if x.get('i')=='call')
        v.click('Analyze with Agent');t.scroll(4000);t.wait({'ANALYZING'},30)
        until=time.monotonic()+30
        while time.monotonic()<until:
            call=next(x.get('t') for x in json.loads(v.request('/snap'))['s'] if x.get('i')=='call')
            if call!=old_call and call.startswith('ripple.context.read'):break
            time.sleep(.1)
        else:raise RuntimeError('No actual context tool before cancellation')
        v.click('Cancel Agent');time.sleep(12);result('native-cancel-late',before,{'CANCELLED'})
        with __import__('contextlib').redirect_stdout(__import__('io').StringIO()):v.capture('native-cancel-late')
    elif mode=='readonly':
        import os,stat
        before=digest();schedule=t.APP/'schedule.txt';os.chmod(schedule,stat.S_IREAD)
        try:
            t.scroll(-4000);enter('title_input','Native readonly save denial');v.click('Save activity');result('native-readonly-denied',before,{'FAILED'})
        finally:os.chmod(schedule,stat.S_IWRITE|stat.S_IREAD)
    elif mode=='quota':
        before=digest();usage=sum(p.stat().st_size for p in t.APP.rglob('*') if p.is_file());cap=1048576
        pad=t.APP/'stage2-capacity-test.txt';assert not pad.exists() and usage<cap
        pad.write_bytes(b'x'*(cap-usage))
        try:
            assert sum(p.stat().st_size for p in t.APP.rglob('*') if p.is_file())==cap
            t.scroll(-4000);enter('title_input','Native full quota save denial, original activity must remain completely intact');v.click('Save activity');result('native-quota-denied',before,{'FAILED'})
            v.save('native-quota-measurement.json',{'manifest_storage_bytes':cap,'native_test_jail_bytes_before':usage,'at_fault_bytes':cap,'created_padding_sha256':v.sha(pad),'existing_files_removed':False})
        finally:
            destination=v.E/'preserved-capacity-padding.txt';assert not destination.exists();pad.rename(destination)
    elif mode=='no-weather':
        # Real OS cache-write denial during a live HTTP query, not an injected HTTP response.
        import os,stat
        before=digest();weather=t.APP/'weather.json';os.chmod(weather,stat.S_IREAD)
        try:v.click('Analyze with Agent');result('native-weather-cache-denied',before,{'FAILED'})
        finally:os.chmod(weather,stat.S_IREAD|stat.S_IWRITE)
    elif mode=='readback':
        before=plan('native-readback-mismatch');choice=t.read('agent-choice.json');original=(t.APP/'schedule.txt').read_bytes()
        v.click('Approve change');until=time.monotonic()+3;written=None
        while time.monotonic()<until:
            actual=(t.APP/'schedule.txt').read_bytes()
            if actual!=original:written=actual;break
            time.sleep(.005)
        assert written is not None and written.decode()==choice['expected']
        # Controlled operator injection into ONLY the generated test activity,
        # after observing the real write and before the scheduled independent read.
        damaged=written.decode().replace('native-readback-mismatch','Operator injected mismatch')
        (t.APP/'schedule.txt').write_text(damaged,encoding='utf-8');t.wait({'PARTIAL','COMPLETED'},5);t.record('native-readback-unconfirmed')
        assert t.status()=='PARTIAL';actual_digest=digest();t.scroll(4000);v.click('Inspect actual result');time.sleep(.3);assert digest()==actual_digest
        v.save('native-readback-mismatch-comparison.json',{'classification':'REAL_AGENT_APPROVED_WRITE_WITH_OPERATOR_INJECTED_READBACK_MISMATCH','source_sha256':v.sha(t.WORK/'stage1/bundle/main.splash'),'real_written_record':written.decode(),'injected_record':damaged,'status':t.status(),'automatic_repeat_write':False,'actual_sha256_after_inspection':actual_digest})
        (t.APP/'schedule.txt').write_bytes(written);v.click('Inspect actual result');t.wait({'COMPLETED'},5);t.record('native-readback-operator-restored')
    elif mode=='close':
        before=plan('native-close-pending')
        # Actual observed RC2 Card title-bar close, not a simulated app callback.
        v.request('/click?x=101&y=117&wait=1');time.sleep(8)
        assert digest()==before
        v.request('/click?x=1225&y=848&wait=1');time.sleep(.5)
        t.scroll(4000);t.wait({'READY'},8)
        assert not any(x.get('t')=='Approve change' for x in json.loads(v.request('/snap'))['s'])
        result('native-close-reopen-no-approval',before,{'READY'})
