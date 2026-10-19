"""Append roadmap topics only; keep the first 16 weeks and all teaching intact."""
from pathlib import Path
import json
import os
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')
assert '/* CYBERSECURITY THREE YEAR PATH START */' not in source
marker = 'const CYBERSECURITY_ROADMAP = '
start = source.index(marker) + len(marker)
end = source.index(';\nconst CYBERSECURITY_TEACH', start)
existing = json.loads(source[start:end])
roadmap_file = root / 'scripts/cybersecurity-roadmap.json'
assert existing == json.loads(roadmap_file.read_text(encoding='utf-8'))
assert [week['week'] for week in existing] == list(range(1, 17))

def day_entry(number, value):
    focus, separator, topics = value.partition(' ~ ')
    assert separator, value
    return {'day': number, 'focus': focus, 'topics': topics.split('; '), 'python': []}

extension = []
for row in (root / 'scripts/cybersecurity-three-year-plan.txt').read_text(encoding='utf-8').splitlines():
    if not row or row.startswith('#'):
        continue
    fields = row.split('|')
    assert len(fields) == 9, fields[0]
    number, title = int(fields[0]), fields[1]
    days = [day_entry(index + 1, item) for index, item in enumerate(fields[2:8])]
    days[5]['python'] = [fields[8]]
    days.append({'day': 7, 'focus': 'Review and consolidation', 'topics': [
        'Recall and connect: ' + '; '.join(day['focus'] for day in days[:5]),
        'Recheck the project: ' + days[5]['focus'],
        'Revisit weak topics, check evidence and finish unfinished work'
    ], 'python': []})
    extension.append({'week': number, 'title': title,
                      'topics': [day['focus'] for day in days[:6]],
                      'python': [fields[8]], 'days': days})
assert [week['week'] for week in extension] == list(range(17, 157))
full = existing + extension
encode = lambda value: json.dumps(value, ensure_ascii=False, indent=2).replace('</', '<\\/')
source = source[:start] + encode(full) + source[end:]

path = json.loads((root / 'scripts/cybersecurity-path.json').read_text(encoding='utf-8'))
helper = (root / 'scripts/cybersecurity-three-year-navigation.js').read_text(encoding='utf-8')
block = ('/* CYBERSECURITY THREE YEAR PATH START */\nconst CYBERSECURITY_PATH = ' +
         encode(path) + ';\n' + helper + '/* CYBERSECURITY THREE YEAR PATH END */\n')
source = source.replace('function renderCybersecurityRoadmap(){', block + 'function renderCybersecurityRoadmap(){', 1)

def once(old, new):
    global source
    assert source.count(old) == 1, old[:100]
    source = source.replace(old, new, 1)

once("' + CYBERSECURITY_ROADMAP.length + ' weeks · Foundations → Defensive Python · Study at your own pace",
     "3 years · ' + CYBERSECURITY_ROADMAP.length + ' weeks · Study at your own pace")
old_start = source.index("      '<div class=\"section-label\">Choose a week</div><div class=\"week-grid\">' +", source.index('function renderCybersecurityRoadmap(){'))
old_end = source.index("      }).join('') + '</div>';", old_start) + len("      }).join('') + '</div>';")
source = source[:old_start] + "      '<div class=\"section-label\">Choose a year, then a week</div>' + cyberRoadmapOverviewHtml();" + source[old_end:]
once("'<div class=\"week-header\"><div class=\"wh-eyebrow\">Week ' + week.week + ' · Cybersecurity</div>' +",
     "'<div class=\"week-header\"><div class=\"wh-eyebrow\">Year ' + Math.ceil(week.week/52) + ' · Week ' + week.week + ' · Cybersecurity</div>' +")
once("'<div class=\"week-header\"><div class=\"wh-eyebrow\">Week ' + week.week + ' · Day ' + day.day + ' of 7</div>' +",
     "'<div class=\"week-header\"><div class=\"wh-eyebrow\">Year ' + Math.ceil(week.week/52) + ' · Week ' + week.week + ' · Day ' + day.day + ' of 7</div>' +")
once("'<a href=\"https://www.nist.gov/cyberframework\" target=\"_blank\" rel=\"noopener noreferrer\">NIST</a> · ' +\n    '<a href=\"https://owasp.org/projects/top-ten\" target=\"_blank\" rel=\"noopener noreferrer\">OWASP</a>' +",
     "CYBERSECURITY_PATH.references.map(function(item){return '<a href=\"'+escapeAttr(item.url)+'\" target=\"_blank\" rel=\"noopener noreferrer\">'+escapeHtml(item.title)+'</a>';}).join(' · ') +")

css = (root / 'scripts/cybersecurity-three-year.css').read_text(encoding='utf-8')
source = source.replace('</style>', css + '\n</style>', 1)

def atomic_write(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(value, encoding='utf-8', newline='')
    for attempt in range(12):
        try:
            os.replace(temporary, path)
            return
        except PermissionError:
            if attempt == 11:
                raise
            time.sleep(.2)

atomic_write(target, source)
atomic_write(roadmap_file, encode(full) + '\n')
print('Added roadmap only: 156 weeks / 1092 day plans, grouped into 3 years. Existing 16 weeks and all teaching retained.')
