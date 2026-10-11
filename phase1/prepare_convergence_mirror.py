"""Unchanged official admission/signing; ephemeral local rehearsal trust only."""
import json, shutil, subprocess, tempfile, sys
from pathlib import Path
import converge as c
hub=c.WORK/'phase1/toolchain/OctoSense-App-Hub/target/release/hub.exe'
prefix='authority-v15' if '--timely' in sys.argv else 'authority'
source=c.WORK/('phase1/probe-authority-timely/bundle' if '--timely' in sys.argv else 'phase1/probe-authority/bundle')
mirror=c.R/(prefix+'-mirror');mirror.mkdir()
bundles=[]
for name,bundle_source in [('bootstrap',c.WORK/'phase1/baseline-bundle'),(prefix,source)]:
    dest=c.R/(name+'-signed-bundle-v15' if '--timely' in sys.argv else name+'-signed-bundle');shutil.copytree(bundle_source,dest)
    if name=='bootstrap':
        p=dest/'manifest.json';m=json.loads(p.read_text());m.update(id='phase1.bootstrap',name='Ripple Baseline Runner Bootstrap',integrity={'bundle_blake3':''});p.write_text(json.dumps(m,indent=2))
    bundles.append(dest)
commands=[]
def run(*args):
    cmd=[str(hub),*map(str,args)];p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
    commands.append({'at_utc':c.now(),'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    if p.returncode: c.save(prefix+'-mirror-commands.json',commands);raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()
with tempfile.TemporaryDirectory(prefix='RippleConvergenceLocalTrust-') as tmp:
    keys=Path(tmp);anchor=run('keygen',keys/'anchor.key');run('keygen',keys/'working.key');signer=run('keygen',keys/'fixture.key');cert=run('certify','--anchor',keys/'anchor.key','--working',keys/'working.key')
    for bundle in bundles:
        run('stamp',bundle);run('sign-manifest',bundle,'--key',keys/'fixture.key','--key-id','phase1-synthetic-test')
        run('publish',bundle,'--catalog',mirror/'catalog.json','--key',keys/'working.key','--anchor-cert',cert,'--publisher','phase1-synthetic-test','--publisher-key','phase1-synthetic-test='+signer,'--out',mirror,'--anchor',anchor)
    run('verify',mirror/'catalog.json','--anchor',anchor)
c.save(prefix+'-mirror-commands.json',commands)
c.save(prefix+'-mirror-receipt.json',{'classification':'LOCAL_REHEARSAL_ONLY','mirror':str(mirror),'anchor_public_hex':anchor,'private_keys_deleted_after_use':True,'probe_version':'0.1.5-phase1' if '--timely' in sys.argv else '0.1.4-phase1','source':str(bundles[1]),'source_hashes':{p.name:c.sha(p) for p in bundles[1].rglob('*') if p.is_file()}})
print('Official admission passed, isolated mirror only.')
