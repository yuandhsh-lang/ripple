"""Check retained experiment sources without launching a host or calling a model."""
import ast
import json
from pathlib import Path

WORK = Path(__file__).resolve().parent.parent
BUNDLES = [WORK / 'phase1' / name / 'bundle' for name in (
    'probe', 'probe-repaired', 'probe-quota', 'probe-authority', 'probe-authority-timely'
)] + [WORK / 'phase2/readonly-prep/bundle']
LOCAL_REPORT_ASSEMBLERS = {
    'finalize_reports.py', 'finalize_continuation.py', 'finalize_convergence.py', 'write_evidence.py'
}


def main():
    scripts = []
    for folder in ('phase1', 'stage1', 'stage2'):
        for path in sorted((WORK / folder).glob('*.py')):
            if path.name in LOCAL_REPORT_ASSEMBLERS:
                continue
            # Parse only: several historical drivers perform operations on import.
            ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))
            scripts.append(path)
    for bundle in BUNDLES:
        manifest = json.loads((bundle / 'manifest.json').read_text(encoding='utf-8'))
        tools = json.loads((bundle / 'tools.json').read_text(encoding='utf-8'))['tools']
        listing = json.loads((bundle / 'listing.json').read_text(encoding='utf-8'))
        if 'script-tools-v1' not in manifest['requires']:
            raise ValueError(f'{bundle}: required script-tools ABI is missing')
        instructions = bundle / manifest['agent']['instructions']
        if not instructions.is_file() or not (bundle / 'main.splash').is_file():
            raise ValueError(f'{bundle}: missing Agent instructions or Splash source')
        if len({tool['name'] for tool in tools}) != len(tools):
            raise ValueError(f'{bundle}: duplicate tool names')
        for tool in tools:
            if tool['implemented_by'] != 'app' or tool['risk'] != 'read':
                raise ValueError(f'{bundle}: historical probe must keep read-only app tools')
            if tool['input_schema']['type'] != 'object':
                raise ValueError(f'{bundle}: invalid tool input schema')
        if not (bundle / listing['icon']).is_file():
            raise ValueError(f'{bundle}: missing source icon')
    print(f'Python syntax: {len(scripts)} scripts; experiment manifests/tools/listings: {len(BUNDLES)} bundles.')


if __name__ == '__main__':
    main()
