"""Bounded final audit receipts; historical data is hashed, never reused."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
from run import v, WORK

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=WORK, encoding='utf-8').strip()

def baseline():
    v.check_test_isolation()
    paths = set()
    # Existing runtime/evidence only; the fresh run is explicitly excluded.
    for name in ['stage1/runtime', 'stage1/evidence', 'stage2/runtime', 'stage2/evidence', 'phase1/evidence']:
        for p in (WORK/name).rglob('*'):
            if p.is_file() and not p.is_relative_to(v.R) and not p.is_relative_to(v.E): paths.add(p)
    for name in ['stage2/evidence/before.json', 'stage2/evidence/isolation-fix-20261011/before.json']:
        p = WORK/name
        if p.exists():
            data = json.loads(p.read_text(encoding='utf-8-sig'))
            for field in ['preserved_sha256', 'protected_sha256']:
                for raw in data.get(field, {}):
                    q = Path(raw)
                    if not q.is_absolute(): q = WORK/q
                    if q.is_file(): paths.add(q)
    sys.path.insert(0, str(WORK/'phase1'))
    from collect_official import baseline as original_baseline
    original = original_baseline()
    original_root = Path(r'F:\桌面\01 项目开发\黑客松\Ripple')
    for raw in [*original['file_sha256'], *original['original_app_state_sha256'], *original['historical_build_files']]:
        p = original_root/raw
        if p.is_file(): paths.add(p)
    # Preserve all pre-existing local modifications by content as well as status.
    for raw in git('ls-files', '--others', '--exclude-standard').splitlines():
        p = WORK/raw
        if p.is_file() and not p.is_relative_to(v.E) and not p.is_relative_to(WORK/'phase1/sources'): paths.add(p)
    paths.add(WORK/'.gitignore')
    v.save('baseline.json', {'head':git('rev-parse','HEAD'), 'branch':git('branch','--show-current'),
        'ecc0cbc':git('rev-parse','ecc0cbc'), 'business_baseline':git('rev-parse','9f4557a'),
        'tags':git('show-ref','--tags'), 'refs':git('show-ref'),
        'status':git('status','--porcelain=v2','--branch'),
        'ignored':git('status','--short','--ignored=matching'),
        'original':original, 'protected_sha256':{str(p):digest(p) for p in sorted(paths)},
        'formal_source_sha256':digest(WORK/'stage1/bundle/main.splash'),
        'provider_handoff':'script disabled; not enabled or run', 'runtime':str(v.R),
        'source_files':{str(p.relative_to(WORK)):digest(p) for p in (WORK/'stage1/bundle').rglob('*') if p.is_file()}})
    print('Protected baseline files:',len(paths))

def protection(label='protection-final'):
    before = json.loads((v.E/'baseline.json').read_text(encoding='utf-8'))
    changes, authorized = [], []
    allowed = {str(WORK/p) for p in ['.gitattributes', 'stage1/bundle/main.splash', 'stage1/bundle/manifest.json', 'stage1/verify.py', 'stage2/final_audit.py']}
    for raw, expected in before['protected_sha256'].items():
        p = Path(raw)
        actual = digest(p) if p.is_file() else None
        if actual != expected:
            (authorized if raw in allowed else changes).append({'path':raw,'before':expected,'after':actual})
    sys.path.insert(0,str(WORK/'phase1'))
    from collect_official import baseline as original_baseline
    current=original_baseline()
    frozen_same=all(current[k]==before['original'][k] for k in ['git','file_sha256','original_app_state_sha256','historical_build_files'])
    # command receipts have no volatile timestamps; their bytes are compared.
    v.save(label+'.json',{'checked':len(before['protected_sha256']), 'changes':changes,'authorized_local_source_changes':authorized,
        'original_frozen_same':frozen_same,'tags_same':git('show-ref','--tags')==before['tags'],
        'refs_same':git('show-ref')==before['refs'], 'head':git('rev-parse','HEAD'),
        'branch':git('branch','--show-current'),'git_status':git('status','--porcelain=v2','--branch')})
    assert not changes and frozen_same
    print('Protected files unchanged:',len(before['protected_sha256']))

if __name__=='__main__': globals()[sys.argv[1]](*sys.argv[2:])
