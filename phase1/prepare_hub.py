"""Reuse Git objects; create untouched official RC2-pinned CLI sources in isolation."""
import json,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parent
from local_paths import HOST_WORKSPACE
OLD=HOST_WORKSPACE
WS=ROOT/'toolchain';WS.mkdir(exist_ok=True)
records=[]
def run(a,cwd=None):
    p=subprocess.run(a,cwd=cwd,text=True,capture_output=True,encoding='utf-8',errors='replace')
    records.append({'command':a,'cwd':str(cwd),'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    (ROOT/'evidence'/'toolchain-commands.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
    if p.returncode: raise RuntimeError(p.stderr or p.stdout)
    return p.stdout
repo=WS/'OctoSense-App-Hub'
if not repo.exists():
    run(['git','clone','--shared','--no-checkout',str(OLD/'OctoSense-App-Hub'),str(repo)])
    run(['git','-C',str(repo),'remote','set-url','origin','https://github.com/OctoSense-org/OctoSense-App-Hub.git'])
sha='95e4831afca7227b640f075b252c04355bb63865'
run(['git','-C',str(repo),'fetch','--depth','1','origin',sha])
run(['git','-C',str(repo),'checkout','--detach',sha])
print('Official RC2-pinned App Hub source:',sha,flush=True)
print((repo/'native-runtime.lock.json').read_text() if (repo/'native-runtime.lock.json').exists() else 'Lock file not in Hub root',flush=True)
