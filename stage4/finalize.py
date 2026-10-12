"""Close-out assertions over observed receipts and exact source identities."""
import ast,hashlib,json,subprocess,sys
from pathlib import Path
W=Path(__file__).resolve().parent.parent;E=W/'stage4/evidence'
S=Path('F:/CodexWorkspace/Projects/RipplePhase1-20261010')
A=Path('F:/CodexWorkspace/05-Backups/RippleStage4-20261012-1617')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,obj):
    with (E/n).open('x',encoding='utf-8') as f:json.dump(obj,f,indent=2,ensure_ascii=False)
checks=[]
for cmd in [['git','diff','--check'],[str(W/'stage4/runtime/hub.exe'),'check',str(W/'stage1/bundle'),'--allow-unsigned','--json']]:
    p=subprocess.run(cmd,cwd=W,capture_output=True,text=True,encoding='utf-8',errors='replace')
    checks.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
    assert p.returncode==0
parsed=[]
for p in sorted((W/'stage4').glob('*.py')):ast.parse(p.read_text(encoding='utf-8'),filename=str(p));parsed.append(p.name)
save('final-checks.json',{'commands':checks,'python_ast':parsed})
expected='ce61aaa2108932e290cd4096122897f2ae097eb99da23de4dcb7dee5264fb94b'
assert sha(W/'stage1/bundle/main.splash')==expected
assert subprocess.check_output(['git','diff','--binary','--no-ext-diff','HEAD'],cwd=W)==(A/'stage3.patch').read_bytes()
old=read(A/'baseline.json')
assert all(sha(W/rel)==h for rel,h in old['archived_untracked'].items())
sdk=read(E/'sdk-bounded-summary.json');assert len(sdk)==3 and all(r['exit_code']==0 for r in sdk)
for i in range(1,4):
    assert 'test result: ok. 5 passed; 0 failed' in (E/f'sdk-bounded-{i}.log').read_text(encoding='utf-8')
    assert read(E/f'sdk-bounded-{i}/editor-regressions.json')['title_only_save']
pins=read(E/'dependency-and-host-pins.json');assert all(sha(W/p)==h for p,h in pins['official_asset_sha256'].items())
sdk_state=[]
for name,pin in pins['dependencies'].items():
    for base,kind in [(S,'protected_stage3'),(W,'stage4')]:
        p=base/'phase1/toolchain'/name
        head=subprocess.check_output(['git','--no-optional-locks','-C',str(p),'rev-parse','HEAD']).decode().strip()
        status=subprocess.check_output(['git','--no-optional-locks','-C',str(p),'status','--short']).decode().strip()
        assert head==pin and not status
        sdk_state.append({'repository':str(p),'kind':kind,'head':head,'clean':True})
native=[]
for host in ['rc2','rc6']:
    run='p4-'+host+'-clean-01';r=W/'stage2/runtime/runs'/run;e=W/'stage2/evidence/runs'/run
    for rel in ['soak-signed-bundle/main.splash','soak-mirror/artifacts/ripple-0.2.3-stage2.bundle/main.splash','soak-business-apps/.bundles/ripple/bundle/main.splash']:assert sha(r/rel)==expected
    assert not (r/'kernel-core/profiles/_main.json').exists()
    failure=read(e/(host+'-smoke-result.json'));assert failure['activity_unchanged'] and failure['tool_audit_files']==0 and failure['weather_source']=='LIVE'
    assert read(e/(host+'-smoke-actual_card_close_reopen-result.json'))['unchanged']
    assert read(e/(host+'-smoke-actual_host_restart-result.json'))['unchanged']
    native.append({'run':run,'installed_sha256':expected,'scope':'native synthetic save/persistence and missing-Provider fail-closed; no model called','receipt_sha256':{str(p.relative_to(W)):sha(p) for p in sorted(e.glob('*.json'))}})
assert read(E/'hosts-stopped.json')['all_stopped']
assert all(r['unchanged'] for r in read(E/'historical-acl-unchanged.json'))
protected=read(A/'protection-final.json');assert not protected['changed'] and protected['source_refs_unchanged'] and protected['original_refs_unchanged']
manifest={'overall_status':'BLOCKED','source_sha256':expected,'bundle_blake3':read(W/'stage1/bundle/manifest.json')['integrity']['bundle_blake3'],'base_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=W).decode().strip(),'stage4_business_changes':0,'stage3_patch_sha256':sha(A/'stage3.patch'),'protection_receipt':str(A/'protection-final.json'),'protected_files':protected['checked_files'],'sdk':sdk,'sdk_source_state':sdk_state,'native':native,'new_real_model_calls':0,'ai_comparison':'read-only reanalysis of 10 Stage 3 pairs; all equal earliest; no new user trials','user_trial':'USER_TRIAL_BLOCKED','independent_reproduction':'BLOCKED','new_provider_authorization':'NOT VERIFIED; profiles intentionally absent','competition':'COMPETITION_VERSION_UNVERIFIED','source_files_sha256':{str(p.relative_to(W)):sha(p) for root in [W/'stage1/bundle',W/'stage4'] for p in (root.rglob('*') if root.name=='bundle' else root.iterdir()) if p.is_file()},'evidence_files_sha256':{str(p.relative_to(W)):sha(p) for p in E.rglob('*') if p.is_file()},'git_status':subprocess.check_output(['git','status','--short'],cwd=W).decode()}
save('final-manifest.json',manifest)
print(json.dumps({k:manifest[k] for k in ['overall_status','source_sha256','stage4_business_changes','protected_files','new_real_model_calls','user_trial','independent_reproduction','competition']}))
