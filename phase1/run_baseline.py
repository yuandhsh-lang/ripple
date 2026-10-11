"""Run fixed-version Ripple in existing official card-host; this is NOT Agent evidence."""
import json, os, pathlib, shutil, subprocess, time, urllib.request, hashlib, datetime
ROOT=pathlib.Path(__file__).resolve().parent
from local_paths import ORIGINAL, HOST_WORKSPACE
BIN=HOST_WORKSPACE/'OctoSense-App-Hub/target/release'
SRC=ROOT.parent/'bundle'
OUT=ROOT/'baseline-bundle'
E=ROOT/'evidence'
if OUT.exists(): raise RuntimeError('Baseline copy already exists; inspect before retry')
shutil.copytree(SRC,OUT)
commands=[]
def run(args):
    p=subprocess.run(args,text=True,capture_output=True,encoding='utf-8',errors='replace',cwd=ROOT.parent)
    commands.append({'command':list(map(str,args)),'cwd':str(ROOT.parent),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    (E/'baseline-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2),encoding='utf-8')
    return p
run([str(BIN/'hub.exe'),'stamp',str(OUT)])
run([str(BIN/'hub.exe'),'check',str(OUT),'--allow-unsigned'])
linux_hub=os.environ.get('RIPPLE_LINUX_HUB',str(ORIGINAL/'.host/cross-linux/hub-wsl.exe'))
run([linux_hub,'check',str(OUT),'--allow-unsigned'])
env=os.environ.copy();env['MAKEPAD_HIDE_WINDOWS']='1';env['MAKEPAD_REMOTE']='8154'
args=[str(BIN/'card-host.exe'),'--bundle',str(OUT),'--app-data',str(ROOT/'runtime'/'baseline-apps'),'--allow-unsigned','--stamp','--size','1100x850']
log=(E/'baseline-host.log').open('w',encoding='utf-8')
p=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,cwd=BIN)
commands.append({'command':args,'environment':{k:env[k] for k in ['MAKEPAD_HIDE_WINDOWS','MAKEPAD_REMOTE']},'pid':p.pid,'classification':'application runtime only; no Agent/AI service'})
for _ in range(30):
    if p.poll() is not None: raise RuntimeError('card-host exited '+str(p.returncode))
    try:
        data=urllib.request.urlopen('http://127.0.0.1:8154/',timeout=2).read()
        (E/'baseline-remote-help.txt').write_bytes(data)
        break
    except Exception: time.sleep(0.5)
else: raise RuntimeError('Baseline remote bridge did not become ready')
time.sleep(2)
for route,name in [('snap','baseline-startup-snap.json'),('g?raw=1','baseline-startup.png')]:
    (E/name).write_bytes(urllib.request.urlopen('http://127.0.0.1:8154/'+route,timeout=10).read())
(E/'baseline-process.json').write_text(json.dumps({'pid':p.pid,'port':8154,'command':args,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
(E/'baseline-commands.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2),encoding='utf-8')
print('Official card-host baseline running; PID',p.pid,'port 8154; no Agent claim',flush=True)
