"""Add an offline beginner roadmap without changing learner storage or existing lessons."""
from pathlib import Path
import json
import os
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')
assert '/* WEB DEVELOPMENT DATA START */' not in source

def once(old, new):
    global source
    assert source.count(old) == 1, old[:120]
    source = source.replace(old, new, 1)

weeks = []
for line in (root / 'scripts/web-development-plan.txt').read_text(encoding='utf-8').splitlines():
    if not line or line.startswith('#'):
        continue
    fields = line.split('|')
    assert len(fields) == 9, fields[0]
    number, title = int(fields[0]), fields[1]
    days = []
    for index, value in enumerate(fields[2:8]):
        focus, separator, topics = value.partition(' ~ ')
        assert separator and focus and topics
        days.append({'day': index+1, 'focus': focus, 'topics': topics.split('; ')})
    days.append({'day': 7, 'focus': 'Review, rebuild and catch up', 'topics': [
        'Recall and connect: ' + '; '.join(day['focus'] for day in days[:5]),
        'Rebuild or improve: ' + days[5]['focus'],
        'Readiness check: ' + fields[8],
        'Revisit unclear topics and finish unfinished work before moving on'
    ]})
    weeks.append({'week': number, 'title': title, 'checkpoint': fields[8], 'days': days})
assert [week['week'] for week in weeks] == list(range(1, 157))
path = json.loads((root / 'scripts/web-development-path.json').read_text(encoding='utf-8'))
encode = lambda value: json.dumps(value, ensure_ascii=False, indent=2).replace('</', '<\\/')

# Native navigation follows the existing single delegated view handler.
desktop = '    <button type="button" class="nav-item" data-view="webdev"><span class="ic" aria-hidden="true">·</span>Web Development</button>\n'
mobile = '  <button type="button" data-view="webdev" aria-label="Web Development"><span class="ic" aria-hidden="true">·</span>Web Dev</button>\n'
once('    <button type="button" class="nav-item" data-view="japanese">', desktop + '    <button type="button" class="nav-item" data-view="japanese">')
once('  <button type="button" class="" data-view="japanese">', mobile + '  <button type="button" class="" data-view="japanese">')
once('    <!-- COURSE VIEW -->', '    <!-- WEB DEVELOPMENT ROADMAP -->\n    <div class="view" id="view-webdev"><div id="webDevelopmentBody"></div></div>\n\n    <!-- COURSE VIEW -->')
once('const views = ["games",', 'const views = ["webdev","games",')
once('course:"Python Course", lessons:', 'course:"Python Course", webdev:"Web Development", lessons:')
once('  if(name==="course") renderCourse();', '  if(name==="course") renderCourse();\n  if(name==="webdev") renderWebDevelopment();')

# Reuse the year/phase/week component; Cybersecurity retains identical output.
old_helper = (root / 'scripts/cybersecurity-three-year-navigation.js').read_text(encoding='utf-8')
wrapper = "function cyberRoadmapOverviewHtml(){\n  return roadmapYearsHtml(CYBERSECURITY_PATH,CYBERSECURITY_ROADMAP,cyberPage.week,'cyber',item=>Boolean(CYBERSECURITY_TEACH[item.week+'.1']));\n}\n"
once(old_helper, wrapper)
old_css = (root / 'scripts/cybersecurity-three-year.css').read_text(encoding='utf-8')
shared_css = old_css.replace('#cybersecurityBody', ':is(#cybersecurityBody,#webDevelopmentBody)')
once(old_css, shared_css)

shell_file = root / 'scripts/premium-shell.js'
shell = shell_file.read_text(encoding='utf-8')
icon = "    webdev:'M3 4h18v16H3z M3 8h18 M9 12l-3 3 3 3 M15 12l3 3-3 3',\n"
assert shell.count("    japanese:") == 1
shell = shell.replace("    japanese:", icon + "    japanese:", 1)
once("    japanese:'M4 5h12", icon + "    japanese:'M4 5h12")

css = (root / 'scripts/web-development.css').read_text(encoding='utf-8')
source = source.replace('</style>', css + '\n</style>', 1)
shared = (root / 'scripts/roadmap-years.js').read_text(encoding='utf-8')
view = (root / 'scripts/web-development-view.js').read_text(encoding='utf-8')
module = ('/* WEB DEVELOPMENT DATA START */\nconst WEBDEV_PATH = ' + encode(path) +
          ';\nconst WEBDEV_ROADMAP = ' + encode(weeks) + ';\n/* WEB DEVELOPMENT DATA END */\n' +
          '/* WEB DEVELOPMENT VIEW START */\n' + view + '/* WEB DEVELOPMENT VIEW END */\n')
once('\nboot();\n', '\n' + shared + '\n' + module + '\nboot();\n')

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
atomic_write(shell_file, shell)
atomic_write(root / 'scripts/web-development-roadmap.json', encode(weeks) + '\n')
atomic_write(root / 'scripts/cybersecurity-three-year-navigation.js', wrapper)
atomic_write(root / 'scripts/cybersecurity-three-year.css', shared_css)
print('Added Web Development to Learn:156 beginner weeks/1092 day plans; shared existing roadmap component; learner storage unchanged.')
