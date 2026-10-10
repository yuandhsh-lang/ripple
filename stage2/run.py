"""Stage 2 isolated RC2 operations, reusing Stage 1's verified control API."""
import json, sys, urllib.parse
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WORK / 'stage1'))
import verify as v
v.E = WORK / 'stage2/evidence'
v.R = WORK / 'stage2/runtime'
v.E.mkdir(exist_ok=True)
# Never fall back to Stage 1's shared peer registry. An unconfigured isolated
# core must report Provider unavailable instead of touching old workspaces.
v.CORE = v.R / 'kernel-core'

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
    if mode == 'prepare': v.prepare(revision)
    elif mode == 'start': v.start(sys.argv[2], '--reuse' in sys.argv, '--no-provider' in sys.argv,revision=revision)
    elif mode == 'snap': v.snap(sys.argv[2])
    elif mode == 'click': v.click(sys.argv[2])
    elif mode == 'enter': enter(sys.argv[2], sys.argv[3])
    elif mode == 'state': v.state(sys.argv[2], revision=revision)
    elif mode == 'capture': v.capture(sys.argv[2])
    elif mode == 'request': print(v.request(sys.argv[2]).decode())
