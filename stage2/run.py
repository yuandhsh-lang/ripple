"""Stage 2 isolated RC2 operations, reusing Stage 1's verified control API."""
import json, os, re, shutil, sys, urllib.parse
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORK / 'stage1'))
import verify as v
run_name = os.environ.get('RIPPLE_TEST_RUN', '')
if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,63}', run_name):
    raise RuntimeError('Set RIPPLE_TEST_RUN to a new lowercase run name; historical test roots are never reused.')
v.R = WORK / 'stage2/runtime/runs' / run_name
v.E = WORK / 'stage2/evidence/runs' / run_name
v.CORE = v.R / 'kernel-core'
for path in (v.R, v.E):
    if path.resolve() != path.absolute(): raise RuntimeError('Test roots must not use symlinks/junctions.')

def initialize():
    # Copy only the already configured test Provider profile, never a peer
    # registry, workspace, conversation, home or app-state directory.
    profile = WORK / 'stage2/runtime/kernel-core/profiles/_main.json'
    data = json.loads(profile.read_text(encoding='utf-8'))
    if set(data['config']) - {'env_vars', 'llm', 'tool_policy'}:
        raise RuntimeError('Unexpected test Provider profile fields; refuse to clone runtime state.')
    if v.R.exists() or v.E.exists(): raise RuntimeError('Run already exists; choose a new run name.')
    v.R.mkdir(parents=True); v.E.mkdir(parents=True)
    target = v.CORE / 'profiles/_main.json'; target.parent.mkdir(parents=True)
    shutil.copyfile(profile, target)
    with (v.R / 'isolation.json').open('x', encoding='utf-8') as f:
        json.dump({'runtime_root':str(v.R.resolve()), 'core_dir':str(v.CORE.resolve()),
                   'provider_profile_only':True}, f)
    print('Fresh test run initialized; no peer/workspace/history copied.')

def enter(widget,text):
    snapshot=json.loads(v.request('/snap'))['s']
    matches=[x for x in snapshot if x.get('ty')=='TextInput' and x.get('i')==widget]
    if len(matches)>1 and widget in ['latitude','longitude']:
        # The bootstrap Card shares these names. Scope to the actual Save row.
        save=next(x for x in snapshot if x.get('ty')=='Button' and x.get('t')=='Save activity')
        matches=[x for x in matches if abs(x['r'][1]-save['r'][1])<3]
    if len(matches)!=1: raise RuntimeError((widget,len(matches)))
    x,y,w,h=matches[0]['r'];v.request(f'/click?x={x+w/2}&y={y+h/2}&wait=1')
    v.request('/k?k=down&c=KeyA&ctrl=1');v.request('/k?k=up&c=KeyA&ctrl=1')
    v.request('/t?t='+urllib.parse.quote(text)+'&wait=1')

if __name__ == '__main__':
    mode = sys.argv[1]
    revision = sys.argv[sys.argv.index('--revision')+1] if '--revision' in sys.argv else 'soak-'
    if mode == 'init': initialize()
    elif mode == 'prepare':
        v.check_test_isolation()
        v.prepare(revision)
    elif mode == 'start': v.start(sys.argv[2], '--reuse' in sys.argv, '--no-provider' in sys.argv,revision=revision)
    elif mode == 'snap': v.snap(sys.argv[2])
    elif mode == 'click': v.click(sys.argv[2])
    elif mode == 'enter': enter(sys.argv[2], sys.argv[3])
    elif mode == 'state': v.state(sys.argv[2], revision=revision)
    elif mode == 'capture': v.capture(sys.argv[2])
    elif mode == 'request': print(v.request(sys.argv[2]).decode())
