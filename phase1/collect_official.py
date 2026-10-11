"""Read-only collection of public official sources and original Ripple baseline."""
import hashlib, json, pathlib, subprocess, urllib.request, datetime

ROOT = pathlib.Path(__file__).resolve().parent
from local_paths import ORIGINAL

def save(name, obj):
    p = ROOT / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def command(args, cwd=ORIGINAL):
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True, encoding='utf-8', errors='replace')
    return {'command': args, 'cwd': str(cwd), 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}

def baseline():
    tracked = command(['git', 'ls-files', '-z'])['stdout'].split('\0')
    untracked = command(['git', 'ls-files', '--others', '--exclude-standard', '-z'])['stdout'].split('\0')
    files = {}
    for f in tracked + untracked:
        if f and (ORIGINAL / f).is_file():
            files[f] = hashlib.sha256((ORIGINAL / f).read_bytes()).hexdigest()
    # App state and historical build inventory are evidence, never used as experiment state.
    state = {}
    for f in (ORIGINAL / 'octoscript' / '.local-state').rglob('*'):
        if f.is_file():
            state[str(f.relative_to(ORIGINAL))] = hashlib.sha256(f.read_bytes()).hexdigest()
    return {'time_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'git': [command(a) for a in [ ['git','rev-parse','HEAD'], ['git','status','--porcelain=v2','--branch'],
                    ['git','show-ref','--tags'], ['git','rev-parse','v0.1.0^{}'], ['git','diff','--binary'],
                    ['git','diff','--cached','--binary']]],
            'file_sha256': files, 'original_app_state_sha256': state,
            'historical_build_files': sorted(str(f.relative_to(ORIGINAL)) for f in (ORIGINAL / 'build').rglob('*') if f.is_file())}

def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Ripple-Phase1-ReadOnly-Validation'})
    return urllib.request.urlopen(req, timeout=60).read()

if __name__ == '__main__':
    save('evidence/original-before.json', baseline())
    repos = ['OctoSense-org/OctoSense', 'OctoSense-org/OctoSense-App-Flow',
             'OctoSense-org/OctoSense-App-Hub', 'gosimfoundation/hackathon-agenticapp26']
    sources = []
    for repo in repos:
        meta = json.loads(fetch(f'https://api.github.com/repos/{repo}/commits/HEAD'))
        sha = meta['sha']
        tree = json.loads(fetch(f'https://api.github.com/repos/{repo}/git/trees/{sha}?recursive=1'))
        folder = ROOT / 'sources' / repo.split('/')[-1]
        folder.mkdir(parents=True, exist_ok=True)
        save(str(folder.relative_to(ROOT) / 'tree.json'), tree)
        paths = [t['path'] for t in tree['tree'] if t['type'] == 'blob' and (
            pathlib.PurePosixPath(t['path']).name.lower() in
            {'agents.md','quickstart.md','ai-services.md','host-api-v1.md','capabilities.md','submitting.md','publishing.md','readme.md','rules.md'}
            or (repo.endswith('hackathon-agenticapp26') and t['path'].endswith(('.md','.json')) and not t['path'].startswith('package-lock')))]
        # Only top-level instructions + relevant documentation; skip vendored/sample READMEs.
        paths = [p for p in paths if '/' not in p or p.startswith('docs/') or p.startswith('desktop/') or (repo.endswith('hackathon-agenticapp26') and p.startswith('src/'))]
        for path in paths:
            url=f'https://raw.githubusercontent.com/{repo}/{sha}/{path}'
            data=fetch(url)
            out=folder / path
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(data)
            sources.append({'repository':repo,'commit':sha,'path':path,'url':url,'sha256':hashlib.sha256(data).hexdigest()})
        print(repo, sha, 'docs', len(paths), flush=True)
    release=json.loads(fetch('https://api.github.com/repos/OctoSense-org/OctoSense/releases/tags/desktop-v0.1.0-rc.2'))
    save('sources/rc2-release.json',release)
    for a in release['assets']:
        if a['name'] in {'RELEASE-NOTES.md','RELEASE-NOTES.zh-CN.md','RELEASE-PROVENANCE.json','SHA256SUMS',
                         'OctoSense_0.1.0-rc.2.windows-acceptance.json','OctoSense_0.1.0-rc.2.windows-backend-acceptance.json',
                         'OctoSense_0.1.0-rc.2.sdk-discovery.json','OctoSense_0.1.0-rc.2_windows-x64.receipt.json'}:
            data=fetch(a['browser_download_url'])
            digest='sha256:'+hashlib.sha256(data).hexdigest()
            if digest!=a['digest']: raise RuntimeError('Official asset digest mismatch: '+a['name'])
            (ROOT/'sources'/a['name']).write_bytes(data)
    save('sources/app-hub-issue-94.json',json.loads(fetch('https://api.github.com/repos/OctoSense-org/OctoSense-App-Hub/issues/94')))
    save('sources/app-hub-issue-94-comments.json',json.loads(fetch('https://api.github.com/repos/OctoSense-org/OctoSense-App-Hub/issues/94/comments')))
    save('sources/INDEX.json',sources)
    print('Official source records saved', flush=True)
