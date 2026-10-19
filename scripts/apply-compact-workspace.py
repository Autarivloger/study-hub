"""Add an icon rail and compact dashboard presentation without changing course logic."""
from pathlib import Path
import os
import re
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')
assert '/* COMPACT WORKSPACE START' not in source
start = source.index('  <div id="sidebar"')
end = source.index('\n  <div id="content"', start)
old = source[start:end]
sidebar = old.replace('    <div class="nav-group-label">Learn</div>', '    <div id="sidebarNavigation">\n    <div class="nav-group-label">Learn</div>', 1)
sidebar, count = re.subn(r'(<button\b[^>]*class="nav-item[^>]*>\s*<span class="ic" aria-hidden="true">.*?</span>)(.*?)(</button>)', r'\1<span class="nav-label">\2</span>\3', sidebar)
assert count == 14, count
toggle = ('    </div>\n    <button type="button" id="sidebarToggle" aria-controls="sidebarNavigation" aria-expanded="true" aria-label="Collapse sidebar">'
          '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 6-6 6 6 6m6-12-6 6 6 6"/></svg>'
          '<span class="sidebar-toggle-label">Collapse sidebar</span></button>\n')
assert sidebar.endswith('  </div>\n')
sidebar = sidebar[:-len('  </div>\n')] + toggle + '  </div>\n'
source = source[:start] + sidebar + source[end:]
css = (root / 'scripts/compact-workspace.css').read_text(encoding='utf-8')
js = (root / 'scripts/compact-workspace.js').read_text(encoding='utf-8')
source = source.replace('</style>', css + '\n</style>', 1)
assert source.count('\nboot();\n') == 1
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
print('Added persistent icon-only sidebar and compact dashboard spacing; all existing course and storage logic preserved.')
