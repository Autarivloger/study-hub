"""Package tracked public files for Pages; do not read browser/user storage."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ('index.html', 'study-hub.html', 'sw.js', 'manifest.webmanifest', 'icon.svg')


def public_paths(root: Path) -> list[str]:
    tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root)
    paths = [item.decode('utf-8') for item in tracked.split(b'\0') if item]
    # Match static-site hidden-file conventions. Keep the existing no-Jekyll marker.
    return [name for name in paths if name == '.nojekyll' or
            not any(part.startswith('.') for part in Path(name).parts)]


def package_site(root: Path, output: Path, revision: str) -> dict:
    root, output = root.resolve(), output.resolve()
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Expected a full Git commit SHA')
    # The publishing directory is new: never clear or replace an existing directory.
    if output == root or output in root.parents or output.exists():
        raise ValueError('Output must be a new dedicated directory')
    paths = public_paths(root)
    if not set(REQUIRED).issubset(paths):
        raise ValueError('Required site entry files are missing from Git')
    for name in paths:
        source = root / name
        if not source.resolve().is_relative_to(root) or source.is_symlink() or not source.is_file():
            raise ValueError('Unsupported tracked path: ' + name)
    output.mkdir(parents=True)
    for name in paths:
        destination = output / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root / name, destination)
    info = {'commit': revision,
            'htmlSha256': hashlib.sha256((output / 'study-hub.html').read_bytes()).hexdigest()}
    (output / 'build-info.json').write_text(json.dumps(info) + '\n', encoding='utf-8')
    return {'files': len(paths), **info}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(json.dumps(package_site(ROOT, args.output, revision)))
