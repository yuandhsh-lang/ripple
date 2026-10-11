"""Bounded real-model soak; actual saved result and Kernel audit required."""
import contextlib, io, json, time, sys
import converge as c
import converge_ui as u
prefix='v15-soak' if '--timely' in sys.argv else 'authority-soak'
app=c.R/('authority-v15-apps/ripple' if '--timely' in sys.argv else 'authority-apps/ripple')
def usage(): return sum(p.stat().st_size for p in app.rglob('*') if p.is_file())
schedule_hash=c.sha(app/'schedule.txt')
records=[]
for i in range(5):
    label=prefix+'-'+str(i+1)
    before=json.loads((app/'authority-turn.json').read_text())
    n=usage();u.click('Ask real Ripple Agent');started=time.monotonic()
    result=None
    while time.monotonic()-started<50:
        time.sleep(.5)
        try:
            candidate=json.loads((app/'authority-turn.json').read_text())
            if candidate['task_id']!=before['task_id']:result=candidate;break
        except (ValueError,FileNotFoundError): pass
    record={'at_utc':c.now(),'classification':'REAL_MODEL','before_bytes':n,'after_bytes':usage(),'deadline_seconds':50,'schedule_unchanged':c.sha(app/'schedule.txt')==schedule_hash,'actual_saved_result':result,'status':'PASS' if result else 'BLOCKED'}
    with contextlib.redirect_stdout(io.StringIO()):u.snap(label);u.state(label,app)
    if result:
        u.previous.capture(label)
        assert result['status']=='READ_ONLY_COMPLETE' and record['schedule_unchanged']
    records.append(record);c.save(label+'-storage.json',record)
    print(label,record['status'],n,'->',record['after_bytes'],flush=True)
    if not result: break
c.save(prefix+'-bounded-real-model-soak.json',{'classification':'REAL_MODEL','requested_turns':5,'executed_turns':len(records),'successful_saved_results':sum(r['status']=='PASS' for r in records),'declared_quota_bytes':1048576,'records':records,'long_term_quota_exhaustion':'NOT TESTED','automatic_retention':'NOT IMPLEMENTED'})
