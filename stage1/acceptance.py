"""Validate recorded current RC2 evidence; never substitutes for a live run.

Run after verify.py and the actual-SDK business harness. Output is a local
receipt; runtime/evidence remain outside Git and the installed App bundle.
"""
import datetime, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
E = ROOT / 'evidence'
def read(name): return json.loads((E / name).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def state(name): return read(name + '-state.json')['files']
def event(name): return json.loads(state(name)['schedule.txt']['content'])
def payloads(d):
    return [r['event'].get('envelope', {}).get('payload', {}) for r in d['selected_unmodified_records']]

receipt = {'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'scope': 'STAGE1_BUSINESS_ACCEPTANCE_RC2_PREHEATED_NOT_CLEAN_COLD_START',
           'live_turns': [], 'fixtures_separate': True}
for name, decision in [('v2-no-change-final','NO_CHANGE'),
                       ('v2-real-pending-decline','PROPOSE'),
                       ('v2-before-stale-edit','PROPOSE'), ('v2-replan-pending','PROPOSE')]:
    d = read(name + '-kernel.json')
    assert d['classification'] == 'REAL_DEEPSEEK_MODEL_OFFICIAL_RC2_WITH_LIVE_WEATHER'
    tools = d['tool_audits']
    assert [a['tool'] for a in tools] == (['ripple.context.read'] if decision == 'NO_CHANGE' else ['ripple.context.read','ripple.slots.search'])
    assert all(a['outcome']=='ok' and a['decision']=='allowed' and a['turn_id']==d['turn_id'] for a in tools)
    p = payloads(d)
    choice = json.loads(next(x['data']['text'] for x in p if x.get('type')=='assistant_persisted'))
    assert choice['decision'] == decision
    assert [x['data']['tool_call_id'] for x in p if x.get('type')=='tool_start'] == [a['tool_call_id'] for a in tools]
    receipt['live_turns'].append({'evidence':name+'-kernel.json','turn_id':d['turn_id'], 'tools':tools,'model_choice':choice})

pending = json.loads(state('v2-replan-pending')['agent-choice.json']['content'])
choice = receipt['live_turns'][-1]['model_choice']
assert all(choice[k]==pending[k] for k in ['task_id','read_token','search_id','candidate_id'])
before = json.loads(pending['before']); expected = json.loads(pending['expected'])
actual = event('v2-completed-final')
assert actual == expected == read('v2-independent-external-readback.json')['actual']
assert actual['event_id']==before['event_id'] and actual['revision']==before['revision']+1
assert actual['start']==pending['start'] and actual['end']==pending['end']
assert state('v2-real-pending-decline')['schedule.txt']['sha256']==state('v2-declined')['schedule.txt']['sha256']
assert event('v2-stale-user-edit')['revision']==event('v2-before-stale-edit')['revision']+1
for name in ['v2-reopened','v2-restart-readback','v2-no-provider-result']:
    assert event(name)==actual
assert read('restart-and-decline-comparison.json')['clean_cold_start_pass'] is False
assert read('no-provider-comparison.json')['schedule_unchanged'] is True
assert any(x.get('t')=='FAILED' for x in read('v2-no-provider-scrolled.json')['s'])
assert any(x.get('t')=='COMPLETED' for x in read('v2-completed-final.json')['s'])
assert json.loads(state('v2-no-change')['agent-session.json']['content'])['model']['provider']=='deepseek'
assert json.loads(state('v2-no-change')['agent-session.json']['content'])['model']['model']=='deepseek-v4-flash'

vm = read('vm-delivery/business-abi-results.json')
assert vm['real_model_used'] is False and len(vm['guards_verified'])==18
time = read('vm-delivery/current-time-vectors.json')
assert time['passed'] is True and time['count']==90
for v in time['vectors']:
    if v['epoch'] % 1 or not 0 <= v['epoch'] <= 4102444799:
        assert v['utc'] is None and v['utc8'] is None
    else:
        dt=datetime.datetime.fromtimestamp(v['epoch'],datetime.timezone.utc)
        assert dt.isoformat().replace('+00:00','Z')==v['utc']
        assert dt.astimezone(datetime.timezone(datetime.timedelta(hours=8))).isoformat()==v['utc8']
assert read('delivery-check.json')['passed'] is True
preserved = read('preservation-after.json')
assert all(preserved[k] for k in ['original_files_equal_existing_predevelopment_baseline','original_local_data_equal_existing_baseline','original_frozen_and_prior_probe_bundles_equal_session_before'])
for f in ['main.splash','tools.json','AGENT.md']:
    assert sha(ROOT/'bundle'/f)==sha(ROOT/'runtime/v2-signed-bundle'/f)

receipt.update(status='PASS', actual_event=actual, previous_event=before,
               source_sha256={f:sha(ROOT/'bundle'/f) for f in ['main.splash','tools.json','AGENT.md']},
               packaging_only_changes_after_live_run=['listing.json','screenshots','PRIVACY.md','manifest integrity'],
               delivery_digest=read('delivery-check.json')['digest'],
               fixture_guards=vm['guards_verified'], time_vectors=90,
               not_tested=['Provider transport network timeout','fixed upstream host build/cold-start','real OS disk-write fault injection'],
               current_storage_bytes=read('v2-no-provider-result-state.json')['storage_bytes'])
output = E / (sys.argv[1] if len(sys.argv)>1 else 'acceptance-current.json')
with output.open('x',encoding='utf-8') as f: json.dump(receipt,f,ensure_ascii=False,indent=2)
print(json.dumps({'status':receipt['status'],'evidence':str(output),'real_turns':len(receipt['live_turns'])},ensure_ascii=False))
