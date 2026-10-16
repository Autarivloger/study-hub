"""Create an independent, tracked-source-only Week42 copy of the Week41 lab."""
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'docs/python-week41'
TARGET=ROOT/'docs/python-week42'

if __name__=='__main__':
    if TARGET.exists():
        raise SystemExit('Week42 project already exists; refusing to overwrite')
    files=subprocess.check_output(['git','ls-files','docs/python-week41'],cwd=ROOT,text=True).splitlines()
    for name in files:
        source=ROOT/name
        relative=source.relative_to(SOURCE)
        if str(relative) in {'README.md','quality-workflow.yml'}:continue
        dest=TARGET/relative
        dest.parent.mkdir(parents=True,exist_ok=True)
        text=source.read_text(encoding='utf-8').replace('Week 41','Week 42').replace('week41','week42').replace('w41','w42').replace('w40_','w42_')
        dest.write_text(text,encoding='utf-8')
    print('Copied authored tracked source only; no instance, keys, databases or caches.')
