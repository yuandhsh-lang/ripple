"""Run project checks with npm from PATH and preserve fresh, local-only logs."""
import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    npm = shutil.which('npm.cmd' if os.name == 'nt' else 'npm')
    if not npm:
        raise RuntimeError('npm is missing from PATH; install the documented Node runtime.')
    evidence = ROOT / 'evidence'
    evidence.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix='project-check-', dir=evidence))
    results = []
    for script in ('test', 'test:integration', 'lint', 'typecheck', 'build'):
        command = [npm, 'run', script]
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        log = run / ('project-' + script.replace(':', '-') + '.log')
        with log.open('x', encoding='utf-8') as out:
            result = subprocess.run(command, cwd=ROOT.parent, stdout=out, stderr=subprocess.STDOUT)
        results.append({'command': command, 'started_at_utc': started,
                        'exit_code': result.returncode, 'log': str(log.relative_to(ROOT.parent))})
        (run / 'commands.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
        print(f'{script}: exit {result.returncode}; log {log}', flush=True)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
