"""Recheck official source gates and experiment helpers; no model substitute."""
import datetime, hashlib, json, pathlib, py_compile, subprocess
ROOT=pathlib.Path(__file__).resolve().parent; E=ROOT/'evidence'
HUB=ROOT/'toolchain/OctoSense-App-Hub/target/release/hub.exe'
records=[]
for args in [('stamp',ROOT/'baseline-bundle'),('check',ROOT/'baseline-bundle','--allow-unsigned','--json'),
             ('check',ROOT/'probe/bundle','--allow-unsigned','--json')]:
    cmd=[str(HUB),*map(str,args)]
    p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    records.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,
                    'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
for path in sorted(ROOT.glob('*.py')):
    py_compile.compile(str(path),doraise=True)
records.append({'operation':'py_compile','files':[str(p.relative_to(ROOT)) for p in ROOT.glob('*.py')],'passed':True})
for folder in ('OctoSense-App-Hub','makepad','octoscript','octoscript-makepad'):
    source=ROOT/'toolchain'/folder
    for args in (['git','rev-parse','HEAD'],['git','status','--porcelain']):
        p=subprocess.run(args,cwd=source,capture_output=True,text=True,encoding='utf-8')
        records.append({'command':args,'cwd':str(source),'exit_code':p.returncode,'stdout':p.stdout})
(E/'final-local-checks.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
print('Official gates:',[(r['command'][1],r['exit_code']) for r in records if 'command' in r and r['command'][0]==str(HUB)])
print('Official toolchain source status:',[r['stdout'] for r in records if r.get('command')==['git','status','--porcelain']])
