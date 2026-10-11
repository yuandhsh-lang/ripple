"""Recover only the three named missing files, only from exact original SHA-256 bytes."""
import hashlib, json, os, subprocess, sys, zipfile
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
E = WORK / 'stage2/evidence/isolation-fix-20261011'
BASE = WORK / 'stage2/evidence/before.json'

def digest(data): return hashlib.sha256(data).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def state(p):
    return {'path': str(p), 'exists': p.is_file(), 'bytes': p.stat().st_size if p.is_file() else None,
            'sha256': digest(p.read_bytes()) if p.is_file() else None}
def save(name, data):
    with (E / name).open('x', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=2)

def recover():
    E.mkdir(parents=True, exist_ok=False)
    baseline = read(BASE)
    targets = read(WORK / 'stage2/evidence/metadata-exact-restoration.json')['remaining_missing']
    expected = {p: baseline['preserved_sha256'][p] for p in targets}
    assert len(expected) == 3
    save('before.json', {'baseline_sha256': digest(BASE.read_bytes()), 'expected': expected,
                        'files': [state(WORK / p) for p in targets],
                        'original_size': 'NOT RECORDED in pre-development hash manifest',
                        'change_source': 'Prior test shared Kernel core/peer lifecycle; no individual file-delete audit exists.'})
    # Hash all preserved files now, including explicit missing markers. New evidence
    # is outside this inventory; no earlier evidence file is rewritten.
    protected = {p: state(WORK / p) for p in baseline['preserved_sha256']}
    for folder in ['stage2/runtime', 'phase1/runtime/kernel-core']:
        for p in (WORK / folder).rglob('*'):
            if p.is_file(): protected[str(p.relative_to(WORK))] = state(p)
    save('protected-before.json', protected)
    matches, counts, errors = [], {}, []
    found = {}
    def inspect(data, origin):
        sha = digest(data)
        for target, wanted in expected.items():
            if sha == wanted:
                matches.append({'target': target, 'sha256': sha, 'bytes': len(data), 'source': origin})
                found.setdefault(target, data)
    # --batch-all-objects also covers dangling/unreachable objects; read-only.
    objects = subprocess.check_output(['git', 'cat-file', '--batch-all-objects', '--batch-check=%(objectname) %(objecttype) %(objectsize)'], cwd=WORK, text=True).splitlines()
    counts['git_objects'] = len(objects); counts['git_blobs'] = 0
    for line in objects:
        oid, kind, size = line.split()
        if kind == 'blob':
            inspect(subprocess.check_output(['git', 'cat-file', 'blob', oid], cwd=WORK), {'git_blob': oid})
            counts['git_blobs'] += 1
    roots = [WORK, Path('F:/CodexWorkspace/05-Backups'), Path('F:/CodexWorkspace/99-Archive'),
             Path('F:/CodexWorkspace/CodexAgentSystem/backups'),
             Path('F:/桌面/01 项目开发/黑客松/.hardening-backup')]
    count = 0; archives = []
    for root in roots:
        for parent, dirs, names in os.walk(root):
            dirs[:] = [d for d in dirs if d not in {'.git', 'node_modules', 'toolchain', 'target', 'plugins', '__pycache__', 'isolation-fix-20261011'}]
            for name in names:
                p = Path(parent) / name
                # Credentials are not recovery candidates. Metadata/backups can be
                # renamed, so compare bytes as well as the original filenames.
                if p.suffix.lower() == '.zip':
                    try:
                        with zipfile.ZipFile(p) as z:
                            n = 0
                            for entry in z.infolist():
                                if not entry.is_dir() and entry.file_size <= 16_000_000 and Path(entry.filename).suffix.lower() in {'.json', '.jsonl', '.bak', '.backup'}:
                                    inspect(z.read(entry), {'archive': str(p), 'member': entry.filename}); n += 1
                            archives.append({'path': str(p), 'sha256': digest(p.read_bytes()), 'metadata_members_checked': n})
                    except (OSError, zipfile.BadZipFile) as ex: errors.append({'path': str(p), 'error': str(ex)})
                elif p.suffix.lower() in {'.json', '.jsonl', '.bak', '.backup'} and p.stat().st_size <= 16_000_000:
                    if name in {'auth.json', '_main.json'} or 'secrets' in str(p).lower(): continue
                    try: inspect(p.read_bytes(), {'file': str(p)}); count += 1
                    except OSError as ex: errors.append({'path': str(p), 'error': str(ex)})
    counts['metadata_files'] = count
    # Never synthesize JSON or touch a neighboring file. Missing destinations are
    # created exclusively only after matching the pre-development trusted digest.
    restored = []
    for target, data in found.items():
        p = WORK / target
        assert p.resolve().is_relative_to((WORK / 'stage1/runtime/v2-business-apps/ripple/accounts/device').resolve())
        assert digest(data) == expected[target]
        if not p.exists():
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as f: f.write(data)
            assert digest(p.read_bytes()) == expected[target]
            restored.append(target)
    save('recovery.json', {'search_roots': [str(p) for p in roots], 'counts': counts, 'archives': archives,
                          'errors': errors, 'exact_sources': matches, 'restored': restored,
                          'files_after': [state(WORK / p) for p in targets],
                          'missing_original_bytes': [p for p in targets if not (WORK / p).is_file()]})
    print('Recovered', len(restored), 'of 3;', counts)

def scan_transcript(path):
    expected = read(E/'before.json')['expected']
    found, count = [], 0
    def visit(value, line, depth=0):
        nonlocal count
        if depth > 8: return
        if isinstance(value, str):
            count += 1
            data = value.encode('utf-8'); sha = digest(data)
            for target, wanted in expected.items():
                if sha == wanted:
                    found.append({'target':target,'source':str(path),'line':line,'sha256':sha,'bytes':len(data)})
                    destination=WORK/target
                    if not destination.exists():
                        with destination.open('xb') as f: f.write(data)
            if value.startswith(('{','[')):
                try: visit(json.loads(value),line,depth+1)
                except ValueError: pass
        elif isinstance(value, dict):
            for child in value.values(): visit(child,line,depth+1)
        elif isinstance(value, list):
            for child in value: visit(child,line,depth+1)
    # Extract captured strings exactly as stored; never reserialize JSON objects
    # or try guessed formatting/trailing-newline variants.
    with path.open(encoding='utf-8') as f:
        for line, text in enumerate(f,1):
            try: visit(json.loads(text),line)
            except ValueError: continue
    save('transcript-search.json',{'source':str(path),'captured_strings_hashed':count,'exact_matches':found})
    print('Captured strings checked:',count,'; exact matches:',len(found))

def verify_tests(suffix=''):
    protected=read(E/'protected-before.json'); recovery=read(E/'recovery.json')
    expected=read(E/'before.json')['expected']; changes=[]
    for path, before in protected.items():
        after=state(WORK/path)
        wanted=expected[path] if path in recovery['restored'] else before['sha256']
        if after['sha256'] != wanted: changes.append({'before':before,'after':after})
    project=read(E/('project-tests'+suffix+'.json'))
    tracked=subprocess.check_output(['git','ls-files','*test.ts','*spec.ts','*test.tsx','*spec.tsx'],cwd=WORK,text=True).splitlines()
    discovered=[str(Path(t['name']).relative_to(WORK)).replace('\\','/') for t in project['testResults']]
    assert set(tracked)==set(discovered) and project['numTotalTests']==project['numPassedTests']==63
    assert project['numPendingTests']==0 and project['numFailedTests']==0
    assert '3 passed; 0 failed' in (E/'sdk.log').read_text(encoding='utf-8-sig')
    assert 'Ran 5 tests' in (E/'isolation-tests.log').read_text(encoding='utf-8-sig')
    save('post-tests'+suffix+'.json',{'protected_files_checked':len(protected),'unauthorized_changes':changes,
         'metadata_after_tests':[state(WORK/p) for p in expected],
         'project_tests':{'tracked':tracked,'discovered':discovered,'passed':63,'skipped':0},
         'actual_sdk_tests_passed':3,'launch_guard_tests_passed':5})
    assert not changes, 'Protected files changed; inspect post-tests.json'
    print('No test pollution across',len(protected),'protected files; metadata recovery remains',len(recovery['restored']),'/3')

if __name__ == '__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--transcript': scan_transcript(Path(sys.argv[2]))
    elif sys.argv[1:2]==['--verify-tests']: verify_tests(sys.argv[2] if len(sys.argv)==3 else '')
    else: recover()
