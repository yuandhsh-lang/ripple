import json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
from local_paths import HOST_WORKSPACE
OLD=HOST_WORKSPACE
WS=ROOT/'toolchain'
records=[]
for name,repo,sha in [
 ('makepad','OctoSense-org/makepad','32d6415fb7476345ad36ee4f98d6f844d1f07fd2'),
 ('octoscript','OctoSense-org/Octoscript','2e37d9e657a246f16718d9a475e167ccd2d5b5fa'),
 ('octoscript-makepad','OctoSense-org/Octoscript-Makepad','33dea2f1f3ad3f1346a219aa8cf6e91b31361e23')]:
    dest=WS/name
    commands=[]
    if not dest.exists():commands += [['git','clone','--shared','--no-checkout',str(OLD/name),str(dest)],['git','-C',str(dest),'remote','set-url','origin','https://github.com/'+repo+'.git']]
    commands += [['git','-C',str(dest),'fetch','--depth','1','origin',sha],['git','-C',str(dest),'checkout','--detach',sha]]
    for args in commands:
        p=subprocess.run(args,text=True,capture_output=True,encoding='utf-8',errors='replace')
        records.append({'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
        (ROOT/'evidence'/'runtime-sources-commands.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
        if p.returncode:raise RuntimeError(p.stderr)
    print(name,sha,flush=True)
