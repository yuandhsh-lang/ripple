"""Official Makepad remote controls; state and evidence stay isolated."""
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
import converge as c
import recheck_gate as g
import continue_gate as previous

g.RUN = c.E
g.RUNTIME = c.R
PORT = 8162

def request(path): return g.request(PORT, path)
def snap(label): g.snapshot(label, PORT)
def click(label):
    s = json.loads(request('/snap'))
    matches = [w for w in s['s'] if w.get('ty') == 'Button' and w.get('t') == label]
    assert len(matches) == 1, (label, len(matches))
    x,y,w,h = matches[0]['r']
    return request('/click?x=%s&y=%s' % (x+w/2,y+h/2))

def start(label, which='a', exe=None, reuse=False, receipt_override=None):
    if which == 'existing':
        home = c.WORK/'phase1/runtime/phase2-gate-20261010-1027/quota-home'
        apps = c.WORK/'phase1/runtime/phase2-gate-20261010-1027/quota-apps'
    else:
        home,apps = c.R/(which+'-home'),c.R/(which+'-apps')
        if reuse:
            assert home.is_dir() and apps.is_dir()
        else:
            home.mkdir(exist_ok=False)
            apps.mkdir(exist_ok=False)
    exe = Path(exe) if exe else c.WORK/'phase1/runtime/rc2/octosense.exe'
    receipt_path=c.E/'authority-mirror-receipt.json' if which=='authority' else c.WORK/'phase1/evidence/phase2-gate-20261010-1027/quota-mirror-receipt.json'
    if receipt_override: receipt_path=Path(receipt_override)
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    overrides = {'OCTOSENSE_HOME':str(home),'OCTOSENSE_APP_DATA':str(apps),
      'OCTOS_APP_CORE_DIR':str(c.WORK/'phase1/runtime/kernel-core'),
      'OCTOSENSE_HUB_CATALOG':'legacy','OCTOSENSE_HUB':receipt['mirror'],
      'OCTOSENSE_HUB_ANCHOR':receipt['anchor_public_hex'],'MAKEPAD_REMOTE':str(PORT),
      'MAKEPAD_HIDE_WINDOWS':'1'}
    env={k:v for k,v in os.environ.items() if not k.startswith(('OCTOS','MAKEPAD','RINX_'))}
    env.update(overrides)
    log=(c.E/(label+'-shell.log')).open('x',encoding='utf-8')
    p=subprocess.Popen([str(exe)],cwd=exe.parent,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
    c.save(label+'-process.json',{'at_utc':c.now(),'pid':p.pid,'command':[str(exe)],'environment':overrides,'shell_sha256':c.sha(exe),'preopened_card':False})
    for _ in range(50):
        if p.poll() is not None: raise RuntimeError('Shell exited '+str(p.returncode))
        try: request('/s'); break
        except Exception: time.sleep(.2)
    print('Shell',p.pid,'port',PORT,flush=True)

def state(label, path=None):
    app=Path(path) if path else c.WORK/'phase1/runtime/phase2-gate-20261010-1027/quota-apps/ripple'
    files={}
    for name in ['schedule.txt','phase1-tool-audit.log','phase1-turn.json','phase1-session.json','phase1-history-meta.json','phase1-runtime-describe.json','phase1-runtime-list.json','authority-turn.json','authority-state.json','task-audit.log']:
        p=app/name
        if p.exists():
            files[name]={'sha256':c.sha(p),'bytes':p.stat().st_size,'content':p.read_text(encoding='utf-8')}
    c.save(label+'-state.json',{'at_utc':c.now(),'app_directory':str(app),'files':files,'total_storage_bytes':sum(p.stat().st_size for p in app.rglob('*') if p.is_file())})
    print(json.dumps({'files':list(files),'storage_bytes':sum(p.stat().st_size for p in app.rglob('*') if p.is_file())},ensure_ascii=True))

if __name__=='__main__':
    mode,label=sys.argv[1:3]
    if mode=='start': start(label,sys.argv[3] if len(sys.argv)>3 else 'a')
    elif mode=='snap': snap(label)
    elif mode=='click': print(click(label).decode())
    elif mode=='request': print(request(label).decode())
    elif mode=='state': state(label,sys.argv[3] if len(sys.argv)>3 else None)
    elif mode=='capture': previous.capture(label,sys.argv[3] if len(sys.argv)>3 else None)
