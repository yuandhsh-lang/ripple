"""Start untouched RC2 with the official locally signed rehearsal catalog."""
import datetime, json, os, pathlib, subprocess, sys, time, urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
E=ROOT/'evidence'; RC2=ROOT/'runtime/rc2'
receipt=json.loads((E/('bootstrap-mirror-receipt.json' if '--bootstrap' in sys.argv else 'local-mirror-receipt.json')).read_text())
env=os.environ.copy()
for k in list(env):
    if k.startswith(('OCTOS','MAKEPAD','RINX_')): del env[k]
suffix='lab-no-provider' if '--no-provider' in sys.argv else 'lab'
if '--bootstrap' in sys.argv: suffix+='-bootstrap'
port='8157'
overrides={'OCTOSENSE_HOME':str(ROOT/'runtime'/f'{suffix}-home'),
           'OCTOSENSE_APP_DATA':str(ROOT/'runtime'/f'{suffix}-apps'),
           'OCTOS_APP_CORE_DIR':str(ROOT/'runtime'/('no-provider-core' if '--no-provider' in sys.argv else 'kernel-core')),
           'OCTOSENSE_HUB_CATALOG':'legacy', 'OCTOSENSE_HUB':receipt['mirror'],
           'OCTOSENSE_HUB_ANCHOR':receipt['anchor_public_hex'], 'MAKEPAD_REMOTE':port}
if '--visible' not in sys.argv: overrides['MAKEPAD_HIDE_WINDOWS']='1'
env.update(overrides)
args=[str(RC2/'octosense.exe'),'--test-action','launch-apphub']
log=(E/f'{suffix}-shell.log').open('a',encoding='utf-8')
p=subprocess.Popen(args,cwd=RC2,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
(E/f'{suffix}-process.json').write_text(json.dumps({'command':args,'environment':overrides,'pid':p.pid,'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
for _ in range(40):
    if p.poll() is not None:raise RuntimeError(f'Exited {p.returncode}')
    try:
        urllib.request.urlopen('http://127.0.0.1:'+port+'/snap',timeout=2).read();break
    except Exception:time.sleep(.5)
time.sleep(3)
print('Official signed catalog rehearsal Shell running, PID',p.pid,'port',port)
