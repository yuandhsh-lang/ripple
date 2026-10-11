"""Read-only privacy, ownership and version receipts for the final audit.

Configured credential values are compared only in memory and never emitted.
This is an acceptance helper, not a formal application dependency.
"""
import hashlib, json, re
from pathlib import Path
from run import WORK, v

RUNS = ['audit-20261011-final-01', 'audit-20261011-final-02']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def walk(data):
    if isinstance(data, dict):
        for k, value in data.items():
            yield k, value
            yield from walk(value)
    elif isinstance(data, list):
        for value in data: yield from walk(value)

def main():
    v.check_test_isolation()
    profile = json.loads((WORK/'stage2/runtime/kernel-core/profiles/_main.json').read_text(encoding='utf-8'))
    secrets = {value for key, value in walk(profile) if re.search(r'key|token|secret|password', key, re.I)
               and isinstance(value, str) and len(value) >= 12}
    # env_vars can also use [{name, value}] rather than a map.
    for _, obj in walk(profile):
        if isinstance(obj, dict) and re.search(r'key|token|secret|password', str(obj.get('name', '')), re.I):
            value = obj.get('value')
            if isinstance(value, str) and len(value) >= 12: secrets.add(value)
    roots = [WORK/'stage1/bundle']
    roots += [WORK/'stage2/evidence/runs'/run for run in RUNS]
    roots += [WORK/'stage2/runtime/runs'/run for run in RUNS]
    files = set()
    for root in roots:
        for p in root.rglob('*'):
            if p.is_file() and p.suffix.lower() in {'.json', '.jsonl', '.log', '.txt', '.md', '.splash', '.py'}:
                if p.parent.name == 'profiles' and p.name == '_main.json': continue
                files.add(p)
    files.update(WORK/p for p in ['stage1/verify.py','stage2/live.py','stage2/final_native.py','stage2/final_audit.py','stage2/final_receipts.py','stage2/test_isolation.py'])
    exact, patterns = [], []
    credential_pattern = re.compile(r'\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{24,}|gh[pousr]_[A-Za-z0-9]{24,}|Bearer\s+[A-Za-z0-9._-]{24,})')
    for p in sorted(files):
        data = p.read_text(encoding='utf-8', errors='replace')
        if any(secret in data for secret in secrets): exact.append(str(p.relative_to(WORK)))
        if credential_pattern.search(data): patterns.append(str(p.relative_to(WORK)))
    v.save('privacy-scan-complete.json', {'classification':'SCOPED_TEXT_SCAN_NOT_PROOF_OF_ALL_POSSIBLE_LEAKS',
        'checked_text_files':len(files), 'credential_values_compared':len(secrets),
        'exact_credential_matches':exact, 'credential_pattern_matches':patterns,
        'excluded':'Provider profile storage; pixels/OCR and transport packets NOT TESTED',
        'provider_profile_modified':False})
    assert secrets, 'No credential values found: exact comparison is unverified.'
    assert not exact and not patterns, 'Review private paths before publishing any evidence.'
    ownership=[]
    for run in RUNS:
        runtime=WORK/'stage2/runtime/runs'/run
        cwd=set()
        for p in (runtime/'kernel-core/ui-protocol').rglob('*.log'):
            for line in p.read_text(encoding='utf-8').splitlines():
                try: record=json.loads(line)
                except ValueError: continue
                for key, value in walk(record):
                    if key in {'cwd','workspace_dir','working_directory'} and isinstance(value,str): cwd.add(value)
        for p in (runtime/'kernel-core/profiles/_main/data/peers').rglob('*.json'):
            for key, value in walk(json.loads(p.read_text(encoding='utf-8'))):
                if key in {'cwd','workspace_dir','working_directory'} and isinstance(value,str): cwd.add(value)
        owned=all(Path(path).resolve().is_relative_to(runtime.resolve()) for path in cwd)
        ownership.append({'run':run, 'cwd_paths':sorted(cwd), 'all_within_owned_runtime':owned,
                          'cwd_observed':bool(cwd)})
        assert owned and cwd, 'Runtime directory evidence missing or escaped.'
    v.save('runtime-ownership-final.json', {'runs':ownership})
    old=json.loads((WORK/'stage2/evidence/isolation-fix-20261011/code-version.json').read_text(encoding='utf-8'))
    metadata=[]
    for item in old['metadata']:
        p=Path(item['path']); exists=p.is_file()
        metadata.append({'path':str(p),'exists':exists,'sha256':sha(p) if exists else None,
                         'matches_previous_receipt':exists==item['exists'] and (not exists or sha(p)==item['sha256'])})
    v.save('historical-integrity-final.json', {'status':'BLOCKED','restored':sum(x['exists'] for x in metadata),
        'total':len(metadata),'metadata':metadata,'historical_search_repeated':False,'generated_replacement':False})
    assert all(x['matches_previous_receipt'] for x in metadata)
    v.save('source-correspondence-final.json', {'formal_source_sha256':sha(WORK/'stage1/bundle/main.splash'),
        'manifest_sha256':sha(WORK/'stage1/bundle/manifest.json'),
        'signed_runtime_source_sha256':{run:sha(WORK/'stage2/runtime/runs'/run/'soak-signed-bundle/main.splash') for run in RUNS},
        'final_sdk':json.loads((v.E/'sdk-final-version.json').read_text(encoding='utf-8')),
        'transitional_run':'audit-20261011-final-01','final_source_run':'audit-20261011-final-02'})
    print('Privacy, runtime ownership, historical integrity and source receipts recorded.')

if __name__=='__main__': main()
