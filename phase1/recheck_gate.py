"""Preserve Phase 1, then recheck the gate without reading credentials.

Uses the unchanged official RC2 and its documented Makepad remote API.
Fresh negative-test directories do not replace the interactive Provider profile.
"""
import datetime
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent
WORK = ROOT.parent
RUN = ROOT / 'evidence' / 'phase2-gate-20261010-1027'
RUNTIME = ROOT / 'runtime' / RUN.name
PORT = 8157


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(name, data):
    p = RUN / name
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        raise RuntimeError('Evidence already exists: ' + str(p))
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def log(action, detail):
    with (RUN / 'actions.jsonl').open('a', encoding='utf-8') as f:
        f.write(json.dumps({'at_utc': now(), 'action': action, 'detail': detail}, ensure_ascii=False) + '\n')


def request(port, path):
    response = urllib.request.urlopen(f'http://127.0.0.1:{port}{path}', timeout=8).read()
    log('official_makepad_http', {'port': port, 'path': path, 'response_bytes': len(response)})
    return response


def snapshot(label, port=PORT):
    s = json.loads(request(port, '/snap'))
    # Provider capture intentionally excludes all text inputs, not just password inputs.
    public = [{k: w[k] for k in ['i', 'ty', 'r', 'text', 't'] if k in w}
              for w in s['s'] if w.get('ty') in ['Label', 'Button']]
    for w in public:
        for key in ['text', 't']:
            if w.get(key, '').startswith('Key '):
                w[key] = '[credential configured; value omitted]'
    save(label + '.json', {'at_utc': now(), 'port': port, 'labels_and_buttons': public})
    provider_page = any(w.get('t') == 'AI providers' for w in public)
    if not provider_page:
        p = RUN / (label + '.png')
        if p.exists():
            raise RuntimeError('Screenshot already exists')
        p.write_bytes(request(port, '/g?raw=1'))
    print(json.dumps(public, ensure_ascii=True, indent=2))


def preserve():
    RUN.mkdir(parents=True, exist_ok=False)
    paths = [WORK / '.gitignore'] + list(WORK.glob('PHASE1_*'))
    paths += [p for p in (ROOT / 'probe').rglob('*') if p.is_file()]
    paths += list(ROOT.glob('*.py'))
    hashes = {}
    with zipfile.ZipFile(RUN / 'phase1-source-before.zip', 'w', zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            rel = p.relative_to(WORK).as_posix()
            hashes[rel] = hashlib.sha256(p.read_bytes()).hexdigest()
            z.write(p, rel)
    git = subprocess.run(['git', 'status', '--porcelain=v2', '--branch'], cwd=WORK,
                         capture_output=True, text=True, encoding='utf-8')
    diff = subprocess.run(['git', 'diff', '--binary'], cwd=WORK, capture_output=True)
    (RUN / 'worktree-before.diff').write_bytes(diff.stdout)
    save('preservation.json', {'at_utc': now(), 'worktree': str(WORK), 'files': hashes,
                              'git_status': git.stdout, 'runtime_credentials_in_archive': False})
    log('preserve_source', {'file_count': len(hashes), 'archive': 'phase1-source-before.zip'})


def start(positive=False, repaired=False, fresh=False):
    if not positive:
        RUNTIME.mkdir(parents=True, exist_ok=False)
    receipt_path = RUN / 'repaired-mirror-receipt.json' if repaired else ROOT / 'evidence/bootstrap-mirror-receipt.json'
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    env = os.environ.copy()
    for k in list(env):
        if k.startswith(('OCTOS', 'MAKEPAD', 'RINX_')):
            del env[k]
    prefix = 'positive-repair-fresh' if fresh else ('positive-repair' if repaired else ('positive' if positive else 'cold'))
    port = 8155 if positive else PORT
    overrides = {
        'OCTOSENSE_HOME': str(RUNTIME / 'repaired-home' if fresh else (ROOT / 'runtime/shell-home' if positive else RUNTIME / 'home')),
        'OCTOSENSE_APP_DATA': str(RUNTIME / 'repaired-apps' if fresh else (ROOT / 'runtime/shell-apps' if positive else RUNTIME / 'apps')),
        'OCTOS_APP_CORE_DIR': str(ROOT / 'runtime/kernel-core' if positive else RUNTIME / 'empty-core'),
        'OCTOSENSE_HUB_CATALOG': 'legacy',
        'OCTOSENSE_HUB': receipt['mirror'],
        'OCTOSENSE_HUB_ANCHOR': receipt['anchor_public_hex'],
        'MAKEPAD_REMOTE': str(port),
    }
    if not positive:
        overrides['MAKEPAD_HIDE_WINDOWS'] = '1'
    env.update(overrides)
    exe = ROOT / 'runtime/rc2/octosense.exe'
    args = [str(exe), '--test-action', 'launch-apphub']
    out = (RUN / (prefix + '-shell.log')).open('x', encoding='utf-8')
    p = subprocess.Popen(args, cwd=exe.parent, env=env, stdout=out, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NO_WINDOW)
    save(prefix + '-process.json', {'at_utc': now(), 'pid': p.pid, 'command': args,
                             'environment': overrides, 'shell_sha256': hashlib.sha256(exe.read_bytes()).hexdigest()})
    log('start_owned_' + prefix + '_shell', {'pid': p.pid, 'command': args, 'environment': overrides})
    for _ in range(30):
        if p.poll() is not None:
            raise RuntimeError('Cold Shell exited: ' + str(p.returncode))
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{port}/s', timeout=1).read()
            break
        except Exception:
            time.sleep(.3)
    print(prefix, 'Shell PID', p.pid, 'port', port)


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'preserve':
        preserve()
    elif mode == 'start':
        start()
    elif mode == 'start-positive':
        start(positive=True)
    elif mode == 'start-positive-repair':
        start(positive=True, repaired=True)
    elif mode == 'start-repair-fresh':
        start(positive=True, repaired=True, fresh=True)
    elif mode == 'snapshot':
        snapshot(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else PORT)
    elif mode == 'request':
        print(request(int(sys.argv[3]) if len(sys.argv) > 3 else PORT, sys.argv[2]).decode('utf-8', errors='replace'))
    elif mode == 'click-button':
        label = sys.argv[2]
        if label == 'Allow':
            raise RuntimeError('Native permission must be explicitly approved; not handled by this helper')
        port = int(sys.argv[3]) if len(sys.argv) > 3 else 8155
        s = json.loads(request(port, '/snap'))
        buttons = [w for w in s['s'] if w.get('ty') == 'Button' and w.get('t') == label]
        if len(buttons) != 1:
            raise RuntimeError('Expected one visible button: ' + label + '; got ' + str(len(buttons)))
        x, y, w, h = buttons[0]['r']
        print(request(port, f'/click?x={x+w/2}&y={y+h/2}').decode())
    elif mode == 'baseline':
        from collect_official import baseline
        current = baseline()
        previous = json.loads((ROOT / 'evidence/original-before.json').read_text(encoding='utf-8'))
        label = sys.argv[2] if len(sys.argv) > 2 else 'original-recheck'
        save(label + '.json', current)
        keys = ['file_sha256', 'original_app_state_sha256', 'historical_build_files']
        comparison = {k: previous[k] == current[k] for k in keys}
        comparison['git_outputs_identical'] = [x['stdout'] for x in previous['git']] == [x['stdout'] for x in current['git']]
        save(label + '-comparison.json', comparison)
        print(json.dumps(comparison))
    elif mode == 'app-state':
        label = sys.argv[2]
        which = sys.argv[3] if len(sys.argv) > 3 else 'negative'
        app = RUNTIME / 'repaired-apps/ripple' if which == 'repaired' else (ROOT / 'runtime/shell-apps/ripple' if which == 'positive' else RUNTIME / 'apps/ripple')
        result = {'at_utc': now(), 'app_directory': str(app), 'files': {}}
        for name in ['schedule.txt', 'phase1-tool-audit.log', 'phase1-runtime-list.json', 'phase1-runtime-describe.json',
                     'phase1-session.json', 'phase1-turn.json', 'phase1-session-history.json', 'phase1-history-meta.json']:
            p = app / name
            if p.exists():
                b = p.read_bytes()
                result['files'][name] = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b),
                                         'content': b.decode('utf-8')}
        save(label + '.json', result)
        print(json.dumps({'label': label, 'files': list(result['files'])}))
    elif mode == 'provider-status':
        core = ROOT / 'runtime/kernel-core'
        files = [p for p in core.rglob('*') if p.is_file()]
        save(sys.argv[2] + '.json', {'at_utc': now(), 'core_directory': str(core),
                                    'file_count': len(files), 'main_profile_exists': (core / 'profiles/_main.json').exists(),
                                    'credential_contents_read': False})
        print('Provider file count:', len(files), 'main profile exists:', (core / 'profiles/_main.json').exists())
    elif mode == 'quit':
        print(request(int(sys.argv[2]) if len(sys.argv) > 2 else PORT, '/quit').decode('utf-8', errors='replace'))
    else:
        raise ValueError(mode)
