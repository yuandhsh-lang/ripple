"""Official local rehearsal only. No network publish or publisher identity.

The throwaway private trust keys exist outside the repository only during this
process; the resulting isolated catalog retains their public keys, never secrets.
"""
import datetime, hashlib, json, pathlib, shutil, subprocess, tempfile

ROOT = pathlib.Path(__file__).resolve().parent
HUB = ROOT / 'toolchain/OctoSense-App-Hub/target/release/hub.exe'
E = ROOT / 'evidence'
MIRROR = ROOT / 'runtime/lab-mirror'
BUNDLE = ROOT / 'runtime/lab-signed-bundle'
if MIRROR.exists() or BUNDLE.exists():
    raise RuntimeError('Existing rehearsal retained; choose new directories')
commands = []

def run(*args):
    command = [str(HUB), *map(str, args)]
    p = subprocess.run(command, text=True, encoding='utf-8', capture_output=True)
    commands.append({'command': command, 'exit_code': p.returncode,
                     'stdout': p.stdout, 'stderr': p.stderr,
                     'at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()})
    (E/'local-mirror-commands.json').write_text(json.dumps(commands, indent=2), encoding='utf-8')
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    return p.stdout.strip()

run('stamp', ROOT/'probe/bundle')
shutil.copytree(ROOT/'probe/bundle', BUNDLE)
MIRROR.mkdir()
with tempfile.TemporaryDirectory(prefix='RipplePhase1EphemeralTrust-') as tmp:
    keys = pathlib.Path(tmp)
    anchor = run('keygen', keys/'anchor.key')
    run('keygen', keys/'working.key')
    signer = run('keygen', keys/'fixture.key')
    cert = run('certify', '--anchor', keys/'anchor.key', '--working', keys/'working.key')
    run('sign-manifest', BUNDLE, '--key', keys/'fixture.key', '--key-id', 'phase1-synthetic-test')
    binding = 'phase1-synthetic-test=' + signer
    run('check', BUNDLE, '--publisher-key', binding, '--json')
    run('publish', BUNDLE, '--catalog', MIRROR/'catalog.json', '--key', keys/'working.key',
        '--anchor-cert', cert, '--publisher', 'phase1-synthetic-test',
        '--publisher-key', binding, '--out', MIRROR)
    run('verify', MIRROR/'catalog.json', '--anchor', anchor)

receipt = {'classification': 'isolated local rehearsal; not public Hub admission',
           'anchor_public_hex': anchor, 'fixture_public_hex': signer,
           'private_keys_deleted_after_use': True, 'mirror': str(MIRROR),
           'requires': ['script-tools-v1'], 'hub_sha256': hashlib.sha256(HUB.read_bytes()).hexdigest(),
           'kernel_profile': 'reuse only explicitly user-configured isolated kernel-core'}
(E/'local-mirror-receipt.json').write_text(json.dumps(receipt, indent=2), encoding='utf-8')
print('Signed local rehearsal prepared and verified; ephemeral private keys removed.')
