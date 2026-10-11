"""Resolve optional local source caches without embedding a machine's paths."""
import os
from pathlib import Path
import subprocess

WORK = Path(__file__).resolve().parent.parent


def original_repository():
    configured = os.environ.get('RIPPLE_ORIGINAL_REPO')
    if configured:
        return Path(configured).resolve()
    # The first worktree is Git's primary checkout. A fresh standalone clone
    # can audit itself; a linked experiment worktree audits the primary checkout.
    lines = subprocess.check_output(
        ['git', 'worktree', 'list', '--porcelain'], cwd=WORK, encoding='utf-8'
    ).splitlines()
    return Path(next(line[9:] for line in lines if line.startswith('worktree '))).resolve()


ORIGINAL = original_repository()
HOST_WORKSPACE = Path(os.environ.get(
    'RIPPLE_HOST_WORKSPACE', str(ORIGINAL / '.host/octo-workspace')
)).resolve()
