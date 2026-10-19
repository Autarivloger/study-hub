"""Embed the shared Back control while keeping the offline HTML standalone."""
from pathlib import Path
import os
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')
assert '/* STUDY HUB FLOATING BACK START' not in source
assert source.count('\nboot();\n') == 1
css = (root / 'scripts/floating-back.css').read_text(encoding='utf-8')
js = (root / 'scripts/floating-back.js').read_text(encoding='utf-8')
source = source.replace('</style>', css + '\n</style>', 1)
source = source.replace('\nboot();\n', '\n' + js + '\nboot();\n', 1)
temporary = target.with_suffix('.html.tmp')
temporary.write_text(source, encoding='utf-8', newline='')
for attempt in range(12):
    try:
        os.replace(temporary, target)
        break
    except PermissionError:
        if attempt == 11:
            raise
        time.sleep(.2)
print('Added shared floating Back control; existing application preserved.')
