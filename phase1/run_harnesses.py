"""Run existing SDK/VM tests in fresh jails; no Provider or app-state reuse."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

WORK = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain', default='1.97.1')
    args = parser.parse_args()
    evidence = WORK / 'phase1/evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='source-check-', dir=evidence))
    env = os.environ.copy()
    env.update(MAKEPAD='headless', RIPPLE_TEST_ROOT=str(WORK))
    # Reuse build outputs only; every test jail and receipt is new.
    env['CARGO_TARGET_DIR'] = str(WORK / 'phase1/business-harness/target')
    results = []
    for name in ('business-harness', 'reliability-harness'):
        jail = run / name
        jail.mkdir()
        env['RIPPLE_TEST_EVIDENCE'] = str(jail)
        if name == 'reliability-harness':
            shutil.copyfile(WORK / 'phase1/business-harness/time-vectors.json', jail / 'time-vectors-input.json')
        command = ['cargo', '+' + args.toolchain, 'test', '--locked', '--offline',
                   '--manifest-path', str(WORK / 'phase1' / name / 'Cargo.toml'),
                   '--', '--test-threads=1']
        log = run / (name + '.log')
        with log.open('x', encoding='utf-8') as out:
            result = subprocess.run(command, cwd=WORK, env=env, stdout=out, stderr=subprocess.STDOUT)
        results.append({'command': command, 'exit_code': result.returncode, 'log': str(log)})
        (run / 'commands.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
        print(f'{name}: exit {result.returncode}; log {log}', flush=True)
        if result.returncode:
            return result.returncode
    print('Both SDK/VM harnesses passed; model calls and cold Shell installation were not tested.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
