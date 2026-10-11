"""Admit a minimal Phase 1 repair through unchanged official Hub gates.

Original probe, mirror, catalog and failure evidence remain untouched.
Signing identities below are ephemeral local rehearsal identities, not official.
"""
import datetime
import json
import pathlib
import shutil
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
E = ROOT / 'evidence/phase2-gate-20261010-1027'
HUB = ROOT / 'toolchain/OctoSense-App-Hub/target/release/hub.exe'
M = ROOT / 'runtime/lab-mirror-repaired-v1'
B = ROOT / 'runtime/bootstrap-bundle-repaired-v1'
P = ROOT / 'runtime/lab-probe-repaired-v1'
M.mkdir(exist_ok=False)
shutil.copytree(ROOT / 'baseline-bundle', B)
mf = json.loads((B / 'manifest.json').read_text(encoding='utf-8'))
mf['id'] = 'phase1.bootstrap'
mf['name'] = 'Ripple Baseline Runner Bootstrap'
mf['integrity'] = {'bundle_blake3': ''}
(B / 'manifest.json').write_text(json.dumps(mf, indent=2), encoding='utf-8')
shutil.copytree(ROOT / 'probe-repaired/bundle', P)
commands = []


def run(*args):
    cmd = [str(HUB), *map(str, args)]
    p = subprocess.run(cmd, text=True, encoding='utf-8', capture_output=True)
    commands.append({'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     'command': cmd, 'exit_code': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    (E / 'repaired-mirror-commands.json').write_text(json.dumps(commands, indent=2), encoding='utf-8')
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    return p.stdout.strip()


with tempfile.TemporaryDirectory(prefix='RipplePhase1EphemeralTrustRepair-') as tmp:
    keys = pathlib.Path(tmp)
    anchor = run('keygen', keys / 'anchor.key')
    run('keygen', keys / 'working.key')
    signer = run('keygen', keys / 'fixture.key')
    cert = run('certify', '--anchor', keys / 'anchor.key', '--working', keys / 'working.key')
    for bundle in (B, P):
        run('stamp', bundle)
        run('sign-manifest', bundle, '--key', keys / 'fixture.key', '--key-id', 'phase1-synthetic-test')
        run('publish', bundle, '--catalog', M / 'catalog.json', '--key', keys / 'working.key',
            '--anchor-cert', cert, '--publisher', 'phase1-synthetic-test',
            '--publisher-key', 'phase1-synthetic-test=' + signer, '--out', M, '--anchor', anchor)
    run('verify', M / 'catalog.json', '--anchor', anchor)
receipt = {'classification': 'local rehearsal only; original probe/mirror preserved',
           'mirror': str(M), 'anchor_public_hex': anchor, 'private_keys_deleted_after_use': True,
           'probe_version': '0.1.2-phase1', 'source': str(ROOT / 'probe-repaired/bundle')}
(E / 'repaired-mirror-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print('Official gates signed/published/verified local repair rehearsal; no official toolchain changes.')
