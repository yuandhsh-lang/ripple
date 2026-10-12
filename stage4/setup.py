"""Fresh source dependencies and official distribution assets; no user state."""
import concurrent.futures,hashlib,json,shutil,subprocess
from pathlib import Path
W=Path(__file__).resolve().parent.parent
S=Path('F:/CodexWorkspace/Projects/RipplePhase1-20261010')
E=W/'stage4/evidence';E.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,obj):
    with (E/n).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2)
def git(p,*a):return subprocess.check_output(['git','--no-optional-locks','-C',str(p),*a]).decode().strip()
pins={'makepad':'32d6415fb7476345ad36ee4f98d6f844d1f07fd2','octoscript':'2e37d9e657a246f16718d9a475e167ccd2d5b5fa','octoscript-makepad':'33dea2f1f3ad3f1346a219aa8cf6e91b31361e23','OctoSense-App-Hub':'95e4831afca7227b640f075b252c04355bb63865'}
def clone(item):
    name,pin=item;src=S/'phase1/toolchain'/name;dst=W/'phase1/toolchain'/name
    assert git(src,'rev-parse','HEAD')==pin and not git(src,'status','--short')
    command=['git','clone','--no-hardlinks','--no-checkout',str(src),str(dst)]
    p=subprocess.run(command,capture_output=True,text=True)
    save('clone-'+name+'.json',{'command':command,'exit_code':p.returncode,'stderr':p.stderr});p.check_returncode()
    subprocess.run(['git','-C',str(dst),'checkout','--detach',pin],check=True,capture_output=True)
    assert not (dst/'.git/objects/info/alternates').exists() and not git(dst,'status','--short')
    print('Pinned independent dependency:',name,pin,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(clone,pins.items()))
# Only pristine executable distribution/assets, never adjacent home/core/app data.
assets={}
for src,dst in [(S/'phase1/runtime/rc2',W/'stage4/runtime/rc2'),(S/'stage3/runtime/rc6-extracted',W/'stage4/runtime/rc6')]:
    assert not dst.exists()
    files=list(p for p in src.rglob('*') if p.is_file())
    assert not any(p.suffix in {'.db','.sqlite','.sqlite3'} or p.name in {'_main.json','schedule.txt','agent-session.json'} for p in files)
    shutil.copytree(src,dst)
    assets.update({str(p.relative_to(W)):sha(p) for p in dst.rglob('*') if p.is_file()})
for src,rel in [(S/'phase1/toolchain/OctoSense-App-Hub/target/release/hub.exe','stage4/runtime/hub.exe')]:
    dst=W/rel;shutil.copyfile(src,dst);assert sha(src)==sha(dst);assets[rel]=sha(dst)
src=S/'phase1/baseline-bundle';dst=W/'phase1/baseline-bundle'
assert not dst.exists();shutil.copytree(src,dst)
for rel in ['phase1/business-harness/src/lib.rs','stage1/bundle/main.splash','stage1/bundle/manifest.json']:
    assert sha(S/rel)==sha(W/rel)
save('dependency-and-host-pins.json',{'dependencies':pins,'official_asset_sha256':assets,'copied_provider':False,'copied_core':False,'copied_activity_or_session':False,'source_sha256':sha(W/'stage1/bundle/main.splash')})
print('Fresh sources and distribution assets prepared; no credentials or old state copied')
