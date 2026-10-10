"""Read-only audit of captured native evidence; does not run or simulate a model."""
import datetime, hashlib, json, subprocess, sys
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
E = WORK / 'stage2/evidence'

def read(name): return json.loads((E / name).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=WORK, text=True, encoding='utf-8').strip()
def unchanged(name, state):
    d = read(name + '-comparison.json')
    assert d['unchanged'] and d.get('status', d.get('ui_status')) == state, name
    if 'source_sha256' in d: assert d['source_sha256'] == source
    return {'record': name + '-comparison.json', 'status': state, 'activity_unchanged': True}

source = sha(WORK / 'stage1/bundle/main.splash')
manifest = json.loads((WORK / 'stage1/bundle/manifest.json').read_text(encoding='utf-8'))
rounds, turns = [], set()
for n in range(1, 6):
    name = f'soak-{n}'
    d, kernel = read(name + '-readback.json'), read(name + '-approval-kernel.json')
    assert d['source_sha256'] == source and d['app_version'] == manifest['version']
    assert d['ui_status'] == 'COMPLETED' and d['after'] == json.loads(d['choice']['expected'])
    before, after = d['before'], d['after']
    assert before == json.loads(d['choice']['before'])
    assert after['revision'] == before['revision'] + 1 == n * 2
    assert before['start'] != after['start'] and before['end'] - before['start'] == after['end'] - after['start']
    for key in ['event_id', 'schema', 'title', 'lat', 'lon', 'data_source']: assert before[key] == after[key]
    assert d['execution_receipt']['status'] == 'COMPLETED'
    assert d['execution_receipt']['operation_id'] == d['choice']['task_id']
    assert kernel['turn_id'] == d['session']['turn_id'] and kernel['turn_id'] not in turns
    turns.add(kernel['turn_id'])
    assert d['session']['model']['provider'] == 'deepseek'
    successful = [a for a in kernel['tool_audits'] if a['outcome'] == 'ok' and a['decision'] == 'allowed']
    names = [a['tool'] for a in successful]
    assert names.index('ripple.context.read') < names.index('ripple.slots.search')
    assert all(a['turn_id'] == kernel['turn_id'] and a['risk'] == 'read' for a in successful)
    payloads = [r['event'].get('envelope', {}).get('payload', {}) for r in kernel['selected_unmodified_records']]
    replies = [json.loads(p['data']['text']) for p in payloads if p.get('type') == 'assistant_persisted']
    selected = next(r for r in replies if r.get('decision') == 'PROPOSE')
    for key in ['task_id', 'read_token', 'search_id', 'candidate_id']: assert selected[key] == d['choice'][key]
    assert any(d['choice']['candidate_id'] in p.get('data', {}).get('output_preview', '') for p in payloads)
    weather = json.loads(read(name + '-approval-state.json')['files']['weather.json']['content'])
    assert weather['source'] == 'LIVE' and weather['provider'] == 'Open-Meteo'
    assert weather['revision'] == d['choice']['weather_revision']
    assert read(name + '-result-state.json')['files']['schedule.txt']['content'] == d['choice']['expected']
    assert any(x.get('t') == 'COMPLETED' for x in read(name + '-result.json')['s'])
    assert (E / (name + '-approval.png')).is_file() and (E / (name + '-result.png')).is_file()
    rounds.append({'round': n, 'turn_id': kernel['turn_id'], 'before_revision': before['revision'],
                   'after_revision': after['revision'], 'storage_bytes': d['storage_bytes'],
                   'tool_call_ids': [a['tool_call_id'] for a in successful],
                   'safely_rejected_tool_calls': [a for a in kernel['tool_audits'] if a['outcome'] != 'ok'],
                   'receipt': name + '-readback.json'})
assert read('soak-2-readback.json')['duplicate_approval_click']

failures = [unchanged(name, state) for name, state in [
    ('native-declined-current', 'DECLINED'), ('native-stale-rejected', 'STALE'),
    ('native-replan-declined', 'DECLINED'), ('native-cancel-late', 'CANCELLED'),
    ('native-readonly-denied', 'FAILED'), ('native-quota-denied', 'FAILED'),
    ('native-weather-cache-denied', 'FAILED'), ('native-no-provider', 'FAILED'),
    ('native-close-reopen-no-approval', 'READY')]]
assert 'DISCARDED late MODEL callback' in read('native-cancel-late-state.json')['files']['agent-audit.log']['content']
assert 'profile_unresolved' in json.dumps(read('native-no-provider-comparison.json'))
quota = read('native-quota-measurement.json')
assert quota['at_fault_bytes'] == manifest['storage']['max_bytes'] == 1048576
mismatch = read('native-readback-mismatch-comparison.json')
assert mismatch['source_sha256'] == source and mismatch['status'] == 'PARTIAL' and not mismatch['automatic_repeat_write']
assert read('native-final-restart-comparison.json')['unchanged']
assert read('native-no-change-comparison.json')['status'] == 'NO_CHANGE'
assert read('native-no-change-comparison.json')['before_sha256'] == read('native-no-change-comparison.json')['after_sha256']
vectors = read('vm-current-final/current-time-vectors.json')
assert vectors['count'] == 90 and vectors['passed']
assert '3 passed; 0 failed' in (E / 'vm-current-final.log').read_text(encoding='utf-8')
weather_cases = read('vm-current-final/weather-failures.json')['cases']
assert len(weather_cases) == 9 and all(c['activity_unchanged'] and c['prior_forecast_unchanged'] for c in weather_cases)
gate = read('soak-check.json')
assert gate['exit_code'] == 0 and json.loads(gate['stdout'])['passed']

baseline = read('before.json')
history = {p: digest for p, digest in baseline['preserved_sha256'].items() if not p.replace('\\', '/').startswith('stage1/bundle/')}
changes = [{'path': p, 'before_sha256': digest, 'after_sha256': sha(WORK / p) if (WORK / p).is_file() else None}
           for p, digest in history.items() if not (WORK / p).is_file() or sha(WORK / p) != digest]
sys.path.insert(0, str(WORK / 'phase1'))
from collect_official import baseline as original_baseline
original = original_baseline()
original_checks = {k: original[k] == baseline['original'][k] for k in ['file_sha256', 'original_app_state_sha256', 'historical_build_files']}
original_checks['git_head_status_tags_diff_unchanged'] = [r['stdout'] for r in original['git']] == [r['stdout'] for r in baseline['original']['git']]
assert all(original_checks.values())
installed = WORK / 'stage2/runtime/soak-signed-bundle'
for name in ['main.splash', 'tools.json', 'AGENT.md']:
    assert sha(installed / name) == sha(WORK / 'stage1/bundle' / name)

status = 'BLOCKED' if changes else 'PASS'
receipt = {'final_status': status, 'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'workspace': str(WORK), 'branch': git('branch', '--show-current'), 'head': git('rev-parse', 'HEAD'),
    'baseline_commit': baseline['head'], 'source_sha256': source, 'app_version': manifest['version'],
    'official_host': read('stage2-soak-process.json'), 'kernel_version': '2.0.3-rc.13 (b0759a5 2026-10-09)',
    'installation': 'ORIGINAL_RC2_WITH_CARD_PREHEAT; NOT_CLEAN_COLD_START_PASS',
    'native_complete_rounds': rounds, 'native_failures': failures,
    'native_readback_mismatch': mismatch, 'sdk_fixture_tests': '3/3 current SDK; not real model evidence',
    'time_vectors': 90, 'weather_injected_cases': 9, 'original_project_checks': original_checks,
    'historical_files_checked': len(history), 'historical_files_not_preserved': changes,
    'blockers': ['Three historical Stage 1 test Agent ledger/session files have no byte-exact recovery copy.'] if changes else [],
    'not_tested': ['Real Provider transport timeout', 'Fixed-source host build/cold start (missing pinned SDK)',
                   'Long-term host Agent-history retention', 'Real model no-candidate branch (current SDK/FIXTURE only)'],
    'system_interruption': 'Windows BlueScreen 154/boot 2026-10-11 02:49; later native recovery/failure checks completed',
    'published': False, 'frozen_submission_modified': False}
out = E / (sys.argv[1] if len(sys.argv) > 1 else 'acceptance-final.json')
with out.open('x', encoding='utf-8') as f: json.dump(receipt, f, ensure_ascii=False, indent=2)
print(status, 'native full rounds=5, SDK=3, UTC vectors=90, preserved exceptions=' + str(len(changes)))
