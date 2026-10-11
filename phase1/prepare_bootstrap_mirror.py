"""Initialize Card normally, without altering runtime feature/admission gates.
Baseline source/screenshot remain genuine; app id is explicitly a bootstrap.
"""
import datetime,json,pathlib,shutil,subprocess,tempfile
ROOT=pathlib.Path(__file__).resolve().parent; E=ROOT/'evidence'
HUB=ROOT/'toolchain/OctoSense-App-Hub/target/release/hub.exe'
M=ROOT/'runtime/lab-mirror-bootstrap-v2'; M.mkdir()
B=ROOT/'runtime/bootstrap-bundle-v2'
shutil.copytree(ROOT/'baseline-bundle',B)
mf=json.loads((B/'manifest.json').read_text());mf['id']='phase1.bootstrap';mf['name']='Ripple Baseline Runner Bootstrap';mf['integrity']={'bundle_blake3':''}
(B/'manifest.json').write_text(json.dumps(mf,indent=2))
li=json.loads((B/'listing.json').read_text());li['description']='Unpublished runtime bootstrap: original Ripple fixed-version code in a separate app sandbox, no Agent.'
(B/'listing.json').write_text(json.dumps(li,indent=2))
P=ROOT/'runtime/lab-probe-bootstrap-v2';shutil.copytree(ROOT/'probe/bundle',P)
commands=[]
def run(*args):
    cmd=[str(HUB),*map(str,args)];p=subprocess.run(cmd,text=True,encoding='utf-8',capture_output=True)
    commands.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr,'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
    (E/'bootstrap-mirror-v2-commands.json').write_text(json.dumps(commands,indent=2),encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    return p.stdout.strip()
with tempfile.TemporaryDirectory(prefix='RipplePhase1EphemeralTrust-') as tmp:
    keys=pathlib.Path(tmp);anchor=run('keygen',keys/'anchor.key');run('keygen',keys/'working.key');signer=run('keygen',keys/'fixture.key')
    cert=run('certify','--anchor',keys/'anchor.key','--working',keys/'working.key')
    for bundle in (B,P):
        run('stamp',bundle);run('sign-manifest',bundle,'--key',keys/'fixture.key','--key-id','phase1-synthetic-test')
        run('publish',bundle,'--catalog',M/'catalog.json','--key',keys/'working.key','--anchor-cert',cert,'--publisher','phase1-synthetic-test','--publisher-key','phase1-synthetic-test='+signer,'--out',M,'--anchor',anchor)
    run('verify',M/'catalog.json','--anchor',anchor)
(E/'bootstrap-mirror-receipt.json').write_text(json.dumps({'classification':'local rehearsal only; bootstrap is not Ripple Agent proof','mirror':str(M),'anchor_public_hex':anchor,'private_keys_deleted_after_use':True,'bootstrap_source_is_original_main_splash':True},indent=2))
print('Two-app local rehearsal signed and verified; no gate changes.')
