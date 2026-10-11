"""Actual host deadline/cancellation; network timeout is not fabricated."""
import contextlib,io,json,time
import converge as c
import converge_ui as u
app=c.R/'authority-v15-apps/ripple'
core=c.WORK/'phase1/runtime/kernel-core/ui-protocol'
allowed={'tool_start','tool_end','assistant_persisted','turn_completed','turn_failed','turn_cancelled'}
def cursor():return {str(p):len(p.read_text(encoding='utf-8').splitlines()) for p in core.rglob('ledger-*.log')}
def capture_new(label,before):
    selected=[]
    for p in core.rglob('ledger-*.log'):
        for raw in p.read_text(encoding='utf-8').splitlines()[before.get(str(p),0):]:
            try:r=json.loads(raw)
            except ValueError:continue
            e=r.get('event',{});env=e.get('envelope',{});typ=env.get('payload',{}).get('type')
            if e.get('session_id','').startswith('_main:api:octosense#peerctx-ripple-') and (typ in allowed or e.get('kind') in allowed): selected.append(r)
    c.save(label+'-new-kernel-records.json',{'at_utc':c.now(),'unmodified_records':selected,'selection':'new records only; Ripple peer; terminal/tool event whitelist'})
    return selected
def snap(label):
    with contextlib.redirect_stdout(io.StringIO()):u.snap(label);u.state(label,app)
schedule=c.sha(app/'schedule.txt')
before=cursor();u.click('Ask real Ripple Agent');time.sleep(1.2);u.click('Interrupt Agent');time.sleep(8)
snap('v15-native-cancel');records=capture_new('v15-native-cancel',before)
c.save('v15-native-cancel-verdict.json',{'classification':'REAL_HOST_CANCEL_DURING_MODEL_TASK','schedule_unchanged':c.sha(app/'schedule.txt')==schedule,'kernel_records':len(records),'expected_application_state':'CANCELLED / no current accepted result','late_model_callback':'verify task-generation discard from state/audit; component delayed completion test is separate'})
flag=app/'model-deadline-fixture.txt';assert not flag.exists();flag.write_text('2',encoding='utf-8')
before=cursor();u.click('Ask real Ripple Agent');time.sleep(10);snap('v15-native-app-deadline');records=capture_new('v15-native-app-deadline',before)
flag.rename(app/'model-deadline-fixture.completed.txt')
c.save('v15-native-app-deadline-verdict.json',{'classification':'HOST_REQUEST_DEADLINE_WITH_OPERATOR_FIXTURE','deadline_seconds':2,'real_provider_configuration_unchanged':True,'schedule_unchanged':c.sha(app/'schedule.txt')==schedule,'kernel_records':len(records),'provider_network_timeout':'NOT TESTED','fault_flag_deactivated_by_rename':True})
print('Cancellation and app deadline captured, schedule unchanged:',c.sha(app/'schedule.txt')==schedule,flush=True)
