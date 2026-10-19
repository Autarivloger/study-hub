"""Reapply the navigation styles/controller; leave authored lessons and saved-data code alone."""
from pathlib import Path
import os
import re
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')

def atomic_write(path, text):
    temporary = path.with_suffix(path.suffix + '.tmp')
    for attempt in range(12):
        try:
            temporary.write_text(text, encoding='utf-8', newline='')
            os.replace(temporary, path)
            return
        except OSError:
            if attempt == 11:
                raise
            time.sleep(.2)

old = 'return html + (lessons.every(function(l){return l.optional;})'
if old in source:
    assert source.count(old) == 1
    source = source.replace(old, "return html + '</div>' + (lessons.every(function(l){return l.optional;})", 1)

for function, end_marker, prefix in [
    ('renderCybersecurityRoadmap', '\ndocument.getElementById("cyberBack")', 'cyber'),
    ('renderWebDevelopment', '\n/* WEB DEVELOPMENT VIEW END */', 'webdev'),
]:
    start = source.index('function ' + function + '(){')
    end = source.index(end_marker, start)
    block = source[start:end]
    if 'lesson-day-grid' not in block:
        assert block.count('class="day-list"') == 1
        block = block.replace('class="day-list"', 'class="day-list lesson-day-grid" aria-label="Choose a daily lesson"')
        if prefix == 'cyber':
            old = '''data-cyber-day="' + day.day + '">'''
            new = '''data-cyber-day="' + day.day + '" title="' + escapeAttr("Day "+day.day+": "+day.focus) + '">'''
        else:
            old = '''data-webdev-day="'+day.day+'">'''
            new = '''data-webdev-day="'+day.day+'" title="'+escapeAttr("Day "+day.day+": "+day.focus)+'">'''
        assert block.count(old) == 1
        block = block.replace(old, new).replace('class="dr-title">Day ', 'class="dr-title day-card-number">Day ')
        source = source[:start] + block + source[end:]
    if prefix == 'webdev':
        view = root / 'scripts/web-development-view.js'
        previous = view.read_text(encoding='utf-8')
        atomic_write(view, previous[:previous.index('function renderWebDevelopment(){')] + block + '\n')

for filename, start, end, anchor in [
    ('learning-navigation.css', '/* LEARNING NAVIGATION STYLE START */', '/* LEARNING NAVIGATION STYLE END */', '</style>'),
    ('learning-navigation.js', '/* LEARNING NAVIGATION START', '/* LEARNING NAVIGATION END */', '\nboot();\n'),
]:
    content = (root / 'scripts' / filename).read_text(encoding='utf-8').rstrip()
    if start in source:
        source, count = re.subn(re.escape(start) + r'.*?' + re.escape(end), lambda _: content, source, flags=re.S)
        assert count == 1
    else:
        assert source.count(anchor) >= 1 if anchor == '</style>' else source.count(anchor) == 1
        source = source.replace(anchor, content + '\n' + anchor, 1)

atomic_write(target, source)
print('Applied compact day grids and native group disclosure presentation.')
