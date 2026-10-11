"""Run SHA-verified official RC2 after explicit user approval; no installer."""
import datetime,hashlib,json,os,pathlib,subprocess,time,urllib.request,sys
ROOT=pathlib.Path(__file__).resolve().parent
RC2=ROOT/'runtime'/'rc2'; E=ROOT/'evidence'
receipt=json.loads((RC2/'octos-kernel.json').read_text())
kernel_hash=hashlib.sha256((RC2/'octos-kernel.exe').read_bytes()).hexdigest()
if kernel_hash!=receipt['sha256']: raise RuntimeError('Kernel receipt hash mismatch')
approved={'approval':'User explicitly approved isolated RC2 execution in chat on 2026-10-10',
          'installer_executed':False,'system_configuration_changed':False,'elevation_used':False,
          'kernel_sha256_verified':kernel_hash,'kernel_receipt':receipt,
          'host_sha256':hashlib.sha256((RC2/'octosense.exe').read_bytes()).hexdigest()}
env=os.environ.copy()
for key in list(env):
    if key.startswith(('OCTOS','MAKEPAD','RINX_')): del env[key]
overrides={'OCTOSENSE_HOME':str(ROOT/'runtime'/'shell-home'),
           'OCTOSENSE_APP_DATA':str(ROOT/'runtime'/'shell-apps'),
           'OCTOS_APP_CORE_DIR':str(ROOT/'runtime'/'kernel-core'),
           'MAKEPAD_REMOTE':'8155'}
if '--visible' not in sys.argv: overrides['MAKEPAD_HIDE_WINDOWS']='1'
env.update(overrides)
args=[str(RC2/'octosense.exe'),'--test-action','launch-ai-providers']
log=(E/'rc2-shell.log').open('a',encoding='utf-8')
p=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW,cwd=RC2)
approved.update({'command':args,'environment':overrides,'pid':p.pid,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
(E/'rc2-process.json').write_text(json.dumps(approved,ensure_ascii=False,indent=2),encoding='utf-8')
for _ in range(40):
    if p.poll() is not None: raise RuntimeError('RC2 exited '+str(p.returncode))
    try:
        data=urllib.request.urlopen('http://127.0.0.1:8155/',timeout=2).read()
        (E/'rc2-remote-help.txt').write_bytes(data); break
    except Exception: time.sleep(0.5)
else: raise RuntimeError('RC2 remote bridge unavailable')
time.sleep(3)
if '--visible' not in sys.argv:
    for route,name in [('snap','rc2-startup-snap.json'),('g?raw=1','rc2-startup.png')]:
        (E/name).write_bytes(urllib.request.urlopen('http://127.0.0.1:8155/'+route,timeout=15).read())
print('Official RC2 Shell alive; kernel bytes verified; PID',p.pid,'port 8155',flush=True)
