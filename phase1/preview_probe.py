"""UI-only preview to bootstrap a genuine capture. Never Agent/runtime evidence.
Final probe keeps script-tools-v1; this copy does not test or dispatch app tools.
"""
import json,pathlib,shutil,subprocess,os,time,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'preview-bundle'; E=ROOT/'evidence'
if OUT.exists(): raise RuntimeError('Inspect existing preview before retry')
shutil.copytree(ROOT/'probe'/'bundle',OUT)
mf=json.loads((OUT/'manifest.json').read_text())
mf.pop('requires',None)
mf['capabilities']=[c for c in mf['capabilities'] if c!='runtime']
(OUT/'manifest.json').write_text(json.dumps(mf,indent=2))
d=json.loads((OUT/'listing.json').read_text())
for f in ['name','summary']: d.pop(f,None)
d['subtitle']='Isolated Agent and read-only tool experiment'
d['release_notes']='Unpublished synthetic-state experiment. No personal calendar or schedule-writing Agent tool.'
(OUT/'listing.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
env=os.environ.copy();env['MAKEPAD_HIDE_WINDOWS']='1';env['MAKEPAD_REMOTE']='8156'
from local_paths import HOST_WORKSPACE
host=str(HOST_WORKSPACE/'OctoSense-App-Hub/target/release/card-host.exe')
args=[host,'--bundle',str(OUT),'--app-data',str(ROOT/'runtime'/'preview-apps'),'--allow-unsigned','--stamp','--size','1100x850']
log=(E/'probe-ui-preview.log').open('w',encoding='utf-8')
p=subprocess.Popen(args,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
time.sleep(4)
if p.poll() is not None:raise RuntimeError('UI preview exited')
snap=urllib.request.urlopen('http://127.0.0.1:8156/snap',timeout=10).read()
(E/'probe-ui-preview-snap.json').write_bytes(snap)
capture=urllib.request.urlopen('http://127.0.0.1:8156/g?raw=1',timeout=10).read()
(E/'probe-ui-preview.png').write_bytes(capture)
(E/'probe-ui-preview-record.json').write_text(json.dumps({'pid':p.pid,'command':args,'classification':'UI rendering only, no Agent or tool-dispatch validation','manifest_differences':['requires removed in this preview copy only','runtime disclosure removed for old card-host compatibility'],'final_probe_requires_unchanged':True},indent=2))
print('UI-only preview captured at 8156; inspect before using',flush=True)
