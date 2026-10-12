"""Hash existing source/evidence/runtime files without exporting their contents."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
ORIGINAL = Path('F:/桌面/01 项目开发/黑客松/Ripple')
E = WORK / 'stage3/evidence'

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def git(root, *args):
    return subprocess.check_output(['git', '--no-optional-locks', *args], cwd=root).decode('utf-8').strip()

def refs():
    return {'main': git(WORK, 'rev-parse', 'main'),
            'original_head': git(ORIGINAL, 'rev-parse', 'HEAD'),
            'tags': git(WORK, 'show-ref', '--tags'),
            'original_status': git(ORIGINAL, 'status', '--porcelain=v1')}

def save(name, data):
    E.mkdir(parents=True, exist_ok=True)
    with (E / name).open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def baseline():
    assert sha(WORK/'stage1/bundle/main.splash') == '7d08ba447ac9bd16bb2a08a049d9232c1d63329fc31764cf50d362cbe415223e'
    paths = {ORIGINAL / s for s in git(ORIGINAL, 'ls-files').splitlines()}
    paths.add(ORIGINAL/'submission/video/Ripple-OctoScript-Demo-v0.1.0-final.mp4')
    roots = [WORK / s for s in ('phase1/runtime', 'phase1/evidence', 'stage1/runtime', 'stage1/evidence', 'stage2/runtime', 'stage2/evidence')]
    roots += [ORIGINAL/'octoscript/.local-state', ORIGINAL/'build']
    for root in roots:
        if root.exists():
            paths.update(p for p in root.rglob('*') if p.is_file())
    records = {str(p): {'size':p.stat().st_size, 'sha256':sha(p)} for p in sorted(paths) if p.is_file()}
    save('baseline.json', {'refs':refs(), 'files':records, 'source_sha256':sha(WORK/'stage1/bundle/main.splash')})
    print('Protected existing files:', len(records), flush=True)

def verify(name):
    before = json.loads((E/'baseline.json').read_text(encoding='utf-8'))
    changed = [path for path, item in before['files'].items() if not Path(path).is_file() or sha(Path(path)) != item['sha256']]
    after = refs()
    result = {'checked_files':len(before['files']), 'changed':changed, 'refs_unchanged':before['refs']==after,
              'refs':after, 'current_source_sha256':sha(WORK/'stage1/bundle/main.splash')}
    save(name, result)
    print(json.dumps(result, ensure_ascii=True))
    assert not changed and result['refs_unchanged'], 'Protected baseline changed; stop host work.'

if __name__ == '__main__':
    baseline() if sys.argv[1]=='baseline' else verify(sys.argv[2])
