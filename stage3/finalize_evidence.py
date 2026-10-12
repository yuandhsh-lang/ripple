"""Read-only aggregation of this round's receipts; no inferred test PASS."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
W=Path(__file__).resolve().parent.parent;E=W/'stage3/evidence'
suffix=sys.argv[1] if len(sys.argv)>1 else ''
assert not suffix or suffix=='-rc6-supplement', 'Use a known new evidence name; never overwrite receipts.'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def git(*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=W).decode('utf-8').strip()
def save(name,value):
    with (E/name).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
bundles={}
for run,expected in [('p3-rc2-before-01','7d08ba447ac9bd16bb2a08a049d9232c1d63329fc31764cf50d362cbe415223e'),('p3-rc2-after-01',sha(W/'stage1/bundle/main.splash')),('p3-rc6-before-02','7d08ba447ac9bd16bb2a08a049d9232c1d63329fc31764cf50d362cbe415223e'),('p3-rc6-after-01',sha(W/'stage1/bundle/main.splash'))]:
    root=W/'stage2/runtime/runs'/run
    copies={str(p.relative_to(W)):sha(p) for p in [root/'soak-signed-bundle/main.splash',root/'soak-mirror/artifacts/ripple-0.2.3-stage2.bundle/main.splash',root/'soak-business-apps/.bundles/ripple/bundle/main.splash']}
    assert all(x==expected for x in copies.values()),copies
    bundles[run]=copies
sdk=E/'sdk-all-retry';assert read(sdk/'editor-regressions.json')['title_only_save']
rc2=W/'stage2/evidence/runs/p3-rc2-after-01';rc6=W/'stage2/evidence/runs/p3-rc6-before-02'
required=['fixed-editor-result','fixed-editor-immediate-save','fixed-decline-result','fixed-stale-result','fixed-cancel-analyzing-result','fixed-draft-result','fixed-readback-injection','fixed-readback-result','fixed-dry-result','fixed-reopen-result','ai-vs-rule','acl-access-check']
receipts={str((rc2/(n+'.json')).relative_to(W)):sha(rc2/(n+'.json')) for n in required}
for n in ['rc6-baseline-result','rc6-decline-result','rc6-stale-result','rc6-cancel-analyzing-result','rc6-dry-result','rc6-reopen-result','rc6-missing-provider-result','ai-vs-rule','acl-access-check']:
    p=rc6/(n+'.json');receipts[str(p.relative_to(W))]=sha(p)
assert read(rc2/'fixed-readback-injection.json')['status']=='PARTIAL'
assert read(rc6/'rc6-missing-provider-result.json')['activity_unchanged']
rc6fixed=W/'stage2/evidence/runs/p3-rc6-after-01'
for p in sorted(rc6fixed.glob('*.json')):
    receipts[str(p.relative_to(W))]=sha(p)
commands=[read(p) for p in sorted(rc6fixed.glob('*-command.json'))]
assert len(commands)==9 and all(p['exit_code']==0 for p in commands)
assert read(rc6fixed/'rc6-fixed-editor-result.json')['time_preserved']
assert read(rc6fixed/'rc6-fixed-readback-injection.json')['status']=='PARTIAL'
assert read(rc6fixed/'rc6-fixed-no-candidate-result.json')['state']=='NO_CANDIDATE'
assert read(rc6fixed/'rc6-fixed-missing-provider-result.json')['activity_unchanged']
assert read(E/'protection-final-rc6.json')['changed']==[]
assert read(E/'protection-final-rc6.json')['refs_unchanged']
assert read(E/'hosts-stopped-final.json')['all_stage3_hosts_stopped']
assert all(x['unchanged'] for x in read(E/'provider-acl-final.json'))
syntax=[]
for p in sorted((W/'stage3').glob('*.py')):ast.parse(p.read_text(encoding='utf-8'),filename=str(p));syntax.append(p.name)
patch=subprocess.check_output(['git','diff','--binary'],cwd=W)
patch_name='development'+suffix+'.patch'
with (E/patch_name).open('xb') as f:f.write(patch)
manifest={'git_head':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'working_tree_changes_uncommitted':True,'business_entry':'stage1/bundle/main.splash','source_sha256':sha(W/'stage1/bundle/main.splash'),'bundle_blake3':read(W/'stage1/bundle/manifest.json')['integrity']['bundle_blake3'],'bundle_file_sha256':{str(p.relative_to(W)):sha(p) for p in sorted((W/'stage1/bundle').rglob('*')) if p.is_file()},'tested_installed_source_copies':bundles,'receipt_sha256':receipts,'stage3_python_ast_checked':syntax,'development_patch_sha256':sha(E/'development.patch'),'overall_status':'BLOCKED','external_user_trials':'BLOCKED_USER_CONFIRMED_NONE','independent_reproduction':'BLOCKED','historical_provider_acl':'BLOCKED_USER_DECLINED_CHANGE','competition_version':'COMPETITION_VERSION_UNVERIFIED','rc6_full_current_source_compatibility':'NOT VERIFIED_BASELINE_ONLY_PARTIAL_MATRIX','sdk_native_abort':'0xc0000409 first combined run; retry 5/5 passed; root cause NOT VERIFIED'}
manifest.update(development_patch_sha256=sha(E/patch_name),
                rc6_full_current_source_compatibility='PASS_WITHIN_RECORDED_WINDOWS_ISOLATED_EXTRACTED_HOST_MATRIX; system installer, all failure types and long-term operation NOT VERIFIED',
                rc6_current_commands=commands,
                stage3_source_file_sha256={str(p.relative_to(W)):sha(p) for p in sorted((W/'stage3').iterdir()) if p.is_file()},
                protection_receipt='protection-final-rc6.json',
                previous_manifest_preserved='final-manifest.json',
                evidence_scope='Development quality only; no competition acceptance inferred')
save('final-manifest'+suffix+'.json',manifest)
print(json.dumps({k:manifest[k] for k in ['git_head','branch','source_sha256','bundle_blake3','overall_status']},ensure_ascii=False))
