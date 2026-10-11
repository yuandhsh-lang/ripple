"""Isolated convergence evidence. Never inspect Provider credentials."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

WORK = Path(__file__).resolve().parent.parent
E = WORK / 'phase1/evidence/convergence-20261010-1343'
R = WORK / 'phase1/runtime/convergence-20261010-1343'
SRC = WORK / 'phase1/toolchain/OctoSense-upstream-dedd14a'
COMMITS = ['8ee0dad0b46a142d31dfe489fef37ecfe101d94d', '3311d1a6156712ee7f8cb8f17bc892fb5155a470', 'dedd14a3e4eaaf384f137ee3ab0b8832378e2581']

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value):
    with (E / name).open('x', encoding='utf-8') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def command(label, cmd, cwd=WORK, env=None, require=True):
    log = E / (label + '.log')
    with log.open('x', encoding='utf-8') as out:
        p = subprocess.run(cmd, cwd=cwd, env=env, stdout=out, stderr=subprocess.STDOUT)
    save(label + '.json', {'at_utc': now(), 'command': list(map(str, cmd)), 'cwd': str(cwd), 'exit_code': p.returncode, 'log': str(log), 'log_sha256': sha(log)})
    print(label, 'exit', p.returncode, flush=True)
    if require and p.returncode: raise RuntimeError(str(log))
    return p.returncode

def init():
    E.mkdir(parents=True, exist_ok=False)
    R.mkdir(parents=True, exist_ok=False)
    paths = [WORK / '.gitignore'] + list(WORK.glob('PHASE1_*'))
    paths += [p for p in (WORK / 'docs').rglob('*') if p.is_file()]
    paths += [p for name in ['probe', 'probe-repaired', 'probe-quota'] for p in (WORK / 'phase1' / name).rglob('*') if p.is_file()]
    paths += list((WORK / 'phase1').glob('*.py'))
    with zipfile.ZipFile(E / 'before-convergence.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for p in paths: z.write(p, p.relative_to(WORK).as_posix())
    save('preservation.json', {'at_utc': now(), 'sha256': {p.relative_to(WORK).as_posix(): sha(p) for p in paths}, 'archive_sha256': sha(E / 'before-convergence.zip'), 'credentials_in_archive': False})
    from collect_official import baseline
    current = baseline()
    previous = json.loads((WORK / 'phase1/evidence/original-before.json').read_text(encoding='utf-8'))
    same = {k: previous[k] == current[k] for k in ['file_sha256', 'original_app_state_sha256', 'historical_build_files']}
    same['git_outputs_identical'] = [x['stdout'] for x in previous['git']] == [x['stdout'] for x in current['git']]
    save('original-before.json', current)
    save('original-before-comparison.json', same)
    assert all(same.values())
    command('experiment-git-before', ['git', 'status', '--porcelain=v2', '--branch'])
    save('provider-scope.json', {'at_utc': now(), 'provider_switched': False, 'scope': 'experiment source collection only'})

def source():
    from local_paths import ORIGINAL
    original = Path(os.environ.get('RIPPLE_OCTOSENSE_SOURCE', str(ORIGINAL.parent / 'OctoSense')))
    command('upstream-original-git', ['git', 'status', '--porcelain=v2', '--branch'], original)
    command('source-borrow', ['git', 'clone', '--shared', '--no-checkout', str(original), str(SRC)])
    command('source-origin', ['git', 'remote', 'set-url', 'origin', 'https://github.com/OctoSense-org/OctoSense.git'], SRC)
    command('source-main-fetch', ['git', 'fetch', '--no-tags', 'origin', 'main:refs/remotes/origin/main'], SRC)
    for c in COMMITS:
        command(c[:7] + '-main-ancestor', ['git', 'merge-base', '--is-ancestor', c, 'origin/main'], SRC)
        command(c[:7] + '-patch', ['git', 'show', '--format=fuller', '--stat', '--patch', c], SRC)
    command('source-main-head', ['git', 'rev-parse', 'origin/main'], SRC)
    command('source-checkout', ['git', 'checkout', '--detach', COMMITS[-1]], SRC)

if __name__ == '__main__':
    {'init': init, 'source': source}[sys.argv[1]]()
