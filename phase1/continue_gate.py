"""Phase 1 continuation: preserve real evidence and launch isolated official Shell.

No credential files are read. No consent grants, capability checks or official
sources are patched. Permission is accepted only through the normal host UI.
"""
import hashlib
import json
import os
import pathlib
import subprocess
import sys
import time

import recheck_gate as g


def usage(label, quota=False):
    app = g.RUNTIME / ('quota-apps/ripple' if quota else 'repaired-apps/ripple')
    files = [{'path': p.relative_to(app).as_posix(), 'bytes': p.stat().st_size}
             for p in app.rglob('*') if p.is_file()]
    g.save(label + '.json', {'at_utc': g.now(), 'files': files,
                           'total_bytes': sum(x['bytes'] for x in files),
                           'declared_quota': 1048576 if quota else 65536, 'contents_read': False})


def state(label):
    app = g.RUNTIME / 'quota-apps/ripple'
    files = {}
    for name in ['schedule.txt', 'phase1-tool-audit.log', 'phase1-runtime-list.json', 'phase1-runtime-describe.json',
                 'phase1-session.json', 'phase1-turn.json', 'phase1-history-meta.json']:
        p = app / name
        if p.exists():
            b = p.read_bytes()
            files[name] = {'sha256': hashlib.sha256(b).hexdigest(), 'bytes': len(b), 'content': b.decode('utf-8')}
    g.save(label + '.json', {'at_utc': g.now(), 'app_directory': str(app), 'files': files})
    print(json.dumps({'files': list(files), 'turn': files.get('phase1-turn.json', {}).get('content', '')}, ensure_ascii=True))


def capture(label, turn_id=None):
    core = g.ROOT / 'runtime/kernel-core'
    audit_path = core / 'profiles/_main/data/peers/ripple-22a12f906cd27b73/tool_audit.jsonl'
    audits = [json.loads(s) for s in audit_path.read_text(encoding='utf-8').splitlines() if s.strip()]
    audit = [a for a in audits if a['turn_id'] == turn_id][-1] if turn_id else audits[-1]
    session, turn = audit['session_id'], audit['turn_id']
    selected, sources = [], []
    allowed = {'tool_start', 'tool_end', 'assistant_persisted', 'turn_completed', 'turn_failed', 'turn_cancelled'}
    for p in (core / 'ui-protocol').rglob('ledger-*.log'):
        chosen = []
        for line in p.read_text(encoding='utf-8').splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            event = record.get('event', {})
            env = event.get('envelope', {})
            if event.get('session_id') != session:
                continue
            if env.get('turn_id', event.get('turn_id')) != turn:
                continue
            typ = env.get('payload', {}).get('type')
            if typ in allowed or event.get('kind') in allowed or event.get('metadata', {}).get('kind') == 'tool_completed':
                chosen.append(record)
        if chosen:
            selected.extend(chosen)
            sources.append({'path': str(p), 'sha256_at_capture': hashlib.sha256(p.read_bytes()).hexdigest()})
    g.save(label + '-kernel.json', {'at_utc': g.now(), 'session_id': session, 'turn_id': turn,
                                   'sources': sources, 'selected_unmodified_records': selected})
    g.save(label + '-peer-tool-audit.json', {'source': str(audit_path), 'selected_unmodified_record': audit})
    print(json.dumps({'turn_id': turn, 'model_call_id': audit['tool_call_id'], 'outcome': audit['outcome'],
                      'records': len(selected)}))


def start(label, empty=False, quota=False, normal_cold=False):
    old = json.loads((g.RUN / 'positive-repair-fresh-process.json').read_text(encoding='utf-8'))
    overrides = old['environment'].copy()
    if quota:
        receipt = json.loads((g.RUN / 'quota-mirror-receipt.json').read_text(encoding='utf-8'))
        overrides.update({'OCTOSENSE_HOME': str(g.RUNTIME / 'quota-home'),
                          'OCTOSENSE_APP_DATA': str(g.RUNTIME / 'quota-apps'),
                          'OCTOSENSE_HUB': receipt['mirror'],
                          'OCTOSENSE_HUB_ANCHOR': receipt['anchor_public_hex']})
    if normal_cold:
        overrides['OCTOSENSE_HOME'] = str(g.RUNTIME / 'normal-cold-home')
        overrides['OCTOSENSE_APP_DATA'] = str(g.RUNTIME / 'normal-cold-apps')
    if empty:
        core = g.RUNTIME / (label + '-empty-core')
        core.mkdir(exist_ok=False)
        overrides['OCTOS_APP_CORE_DIR'] = str(core)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('OCTOS', 'MAKEPAD', 'RINX_'))}
    env.update(overrides)
    exe = g.ROOT / 'runtime/rc2/octosense.exe'
    cmd = [str(exe)] if normal_cold else [str(exe), '--test-action', 'launch-apphub']
    log = (g.RUN / (label + '-shell.log')).open('x', encoding='utf-8')
    p = subprocess.Popen(cmd, cwd=exe.parent, env=env, stdout=log, stderr=subprocess.STDOUT,
                         creationflags=subprocess.CREATE_NO_WINDOW)
    g.save(label + '-process.json', {'at_utc': g.now(), 'pid': p.pid, 'command': cmd,
                                    'environment': overrides, 'shell_sha256': hashlib.sha256(exe.read_bytes()).hexdigest()})
    g.log('launch_official_shell', {'label': label, 'pid': p.pid, 'command': cmd, 'environment': overrides})
    for _ in range(30):
        if p.poll() is not None:
            raise RuntimeError('Shell exited')
        try:
            g.request(8155, '/s')
            break
        except Exception:
            time.sleep(.3)
    print(label, p.pid)


if __name__ == '__main__':
    mode, label = sys.argv[1:3]
    if mode == 'capture':
        capture(label, sys.argv[sys.argv.index('--turn-id') + 1] if '--turn-id' in sys.argv else None)
    elif mode == 'usage':
        usage(label, quota='--quota' in sys.argv)
    elif mode == 'state':
        state(label)
    elif mode == 'start':
        start(label, empty='--empty-core' in sys.argv, quota='--quota' in sys.argv, normal_cold='--normal-cold' in sys.argv)
    else:
        raise ValueError(mode)
