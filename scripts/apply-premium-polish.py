"""Embed the shared polish stylesheet for offline use; never alter app JavaScript/data."""
from pathlib import Path
import os
import re
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')
css = (root / 'scripts/premium-polish.css').read_text(encoding='utf-8').rstrip()
start, end = '/* PREMIUM POLISH STYLE START', '/* PREMIUM POLISH STYLE END */'
if start in source:
    source, count = re.subn(re.escape(start) + r'.*?' + re.escape(end), lambda _: css, source, flags=re.S)
    assert count == 1
else:
    assert '</style>' in source
    source = source.replace('</style>', css + '\n</style>', 1)

temporary = target.with_suffix('.html.tmp')
for attempt in range(12):
    try:
        temporary.write_text(source, encoding='utf-8', newline='')
        os.replace(temporary, target)
        break
    except OSError:
        if attempt == 11:
            raise
        time.sleep(.2)
print('Embedded shared typography, panels and compact practice/quiz spacing.')
