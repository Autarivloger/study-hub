"""Apply the presentation refresh without rewriting curriculum or saved data."""
from pathlib import Path
import os
import time

ROOT = Path(__file__).resolve().parents[1]
target = ROOT / "study-hub.html"
source = target.read_text(encoding="utf-8")
if "STUDY HUB PREMIUM THEME START" in source:
    raise SystemExit("The presentation refresh is already applied")

groups = [
    ("Learn", [("course", "Python Course", "Python"), ("japanese", "Japanese Language", "Japanese"), ("quiz", "Cybersecurity", "Cybersecurity")]),
    ("Practise", [("reviews", "Today's Review", "Reviews"), ("flashcards", "Flashcards", "Cards"), ("typing", "Typing", "Typing"), ("games", "Games", "Games")]),
    ("Your space", [("todo", "To-Do", "To-Do"), ("timer", "Focus Timer", "Timer"), ("journal", "Daily Journal", "Journal"), ("lessons", "Yoga &amp; Meditation", "Yoga"), ("wisdom", "Life Lessons", "Life"), ("liked", "I Liked", "I Liked")]),
]

header = '''<a class="skip-link" href="#content">Skip to content</a>
<div id="topbar">
  <button type="button" id="backBtn" class="icon-btn" title="Back" aria-label="Back">←</button>
  <div class="brand"><span class="brand-mark" aria-hidden="true"><svg class="ui-icon" viewBox="0 0 24 24"><path d="M4 5h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v14h-6a3 3 0 0 0-2 1 3 3 0 0 0-2-1H4z M12 6v14"/></svg></span><span class="brand-name">Study Hub</span></div>
  <span id="brandTitle">Python Course</span>
  <button type="button" class="icon-btn" id="searchBtn" title="Search Python and Japanese (press /)" aria-label="Search Python and Japanese"><span data-ui-icon="search">⌕</span><span class="search-caption">Search your learning</span><kbd aria-hidden="true">/</kbd></button>
  <span class="local-badge">Offline learning</span>
  <button type="button" class="icon-btn" id="themeBtn" title="Toggle light or dark theme" aria-label="Toggle light or dark theme"><span data-ui-icon="theme">◐</span></button>
  <details id="workspaceTools">
    <summary class="icon-btn" title="Workspace tools" aria-label="Workspace tools"><span data-ui-icon="more">···</span></summary>
    <div class="workspace-menu">
      <div class="workspace-menu-label">Workspace tools</div>
      <button type="button" id="syncBtn" title="Sync across devices"><span data-ui-icon="sync">☁</span>Sync across devices</button>
      <button type="button" id="exportBtn" title="Export backup"><span data-ui-icon="export">⇩</span>Export backup</button>
      <button type="button" id="importBtn" title="Import backup"><span data-ui-icon="import">⇧</span>Import backup</button>
      <input type="file" id="importFile" accept="application/json" style="display:none">
      <button type="button" id="transferBtn" title="Move to another device"><span data-ui-icon="transfer">⇄</span>Move to another device</button>
      <hr>
      <button type="button" id="typingHeadBtn" data-view="typing" title="Typing practice"><span data-ui-icon="typing">⌨</span>Typing practice</button>
      <button type="button" id="chessHeadBtn" data-view="games" title="Open Games"><span data-ui-icon="games">▦</span>Open games</button>
      <button type="button" id="diagBtn" title="Diagnostics"><span data-ui-icon="help">?</span>Help &amp; diagnostics</button>
    </div>
  </details>
</div>

'''
start = source.index('<div id="topbar">')
end = source.index('<nav id="tabnav"', start)
source = source[:start] + header + source[end:]

tabs = '<nav id="tabnav" aria-label="Sections">\n'
side = '<div id="sidebar" role="navigation" aria-label="Workspace sections">\n'
for group, entries in groups:
    side += '    <div class="nav-group-label">' + group + '</div>\n'
    for key, title, mobile in entries:
        active = ' active' if key == 'course' else ''
        current = ' aria-current="page"' if key == 'course' else ''
        side += f'    <button type="button" class="nav-item{active}" data-view="{key}"{current}><span class="ic" aria-hidden="true">·</span>{title}</button>\n'
        tabs += f'  <button type="button" class="{active.strip()}" data-view="{key}"{current}><span class="ic" aria-hidden="true">·</span>{mobile}</button>\n'
tabs += '</nav>'
side += '''    <div class="side-footer"><div class="workspace-note">At your own pace.</div><div class="stat" id="sideStats">Loading…</div></div>
  </div>

  '''
start = source.index('<nav id="tabnav"')
end = source.index('</nav>', start) + len('</nav>')
source = source[:start] + tabs + source[end:]
start = source.index('<div id="sidebar">')
end = source.index('<div id="content">', start)
source = source[:start] + side + source[end:]
source = source.replace('<div id="content">', '<div id="content" role="main" tabindex="-1">', 1)

start = source.index('function renderCourseOverview(){')
end = source.index('function renderCourseWeek(){', start)
old = source[start:end]
begin = old.index('    ${reviewHomeCardHtml()}')
stop = old.index('    <div class="phase-list">', begin)
new = old[:begin] + '''    <div class="workspace-welcome">
      <div><div class="workspace-eyebrow">Your learning space</div><h2>Your Python journey.</h2><p>One lesson at a time. At your own pace.</p></div>
      <span class="workspace-week">Week ${curWeek} of 52</span>
    </div>
    <div class="learning-dashboard">
      <div class="learning-resume">
        ${resumeCard()}
        <svg class="learning-art" viewBox="0 0 180 180" aria-hidden="true" focusable="false" fill="none" stroke="currentColor" stroke-width="1.2"><circle cx="137" cy="112" r="65"/><circle cx="137" cy="112" r="46"/><path d="M38 124l50-29 51 29-51 29z M38 135l50 29 51-29 M38 146l50 29 51-29 M107 32l16-9 16 9-16 9z M123 23v34 M159 56v18 M150 65h18"/></svg>
      </div>
      <div class="course-hero">
        <div class="ch-label">Your progress</div>
        <div class="ch-big"><b>${done}</b> <span>of 364 lessons complete</span></div>
        ${progressBar(done, 364)}
        <div class="ch-sub">${phase ? escapeHtml(phase.name) : "Python course"} · Week ${curWeek} of 52</div>
      </div>
    </div>
    <div class="learning-shortcuts">
      ${reviewHomeCardHtml()}
      <div class="review-panel python-practice-link"><div class="practice-kicker">Put it into practice</div><h3>Make your learning stick.</h3><p>Revisit exercises from the lesson parts you have studied. Choose a topic or shuffle a fresh set.</p><button type="button" class="btn secondary" id="pythonPracticeHome">Open Python Practice →</button></div>
    </div>
    <div class="learning-path-title"><h3>Your learning path</h3><span>12 months · 52 weeks</span></div>

''' + old[stop:]
# The first unfinished-day resume also has data-week. Only week chips open a week.
new = new.replace('el.querySelectorAll("[data-week]")', 'el.querySelectorAll(".week-chip[data-week]")')
source = source[:start] + new + source[end:]

for selector in ['#sidebar .nav-item', '#tabnav button']:
    old = f'document.querySelectorAll("{selector}").forEach(b=> b.classList.toggle("active", b.dataset.view===navigationName));'
    new = f'document.querySelectorAll("{selector}").forEach(b=>{{const active=b.dataset.view===navigationName;b.classList.toggle("active",active);b.setAttribute("aria-current",active?"page":"false");}});'
    assert old in source
    source = source.replace(old, new, 1)

css = (ROOT / 'scripts/premium-theme.css').read_text(encoding='utf-8')
shell = (ROOT / 'scripts/premium-shell.js').read_text(encoding='utf-8')
source = source.replace('</style>', css + '\n</style>', 1)
assert source.count('\nboot();\n') == 1
source = source.replace('\nboot();\n', '\n' + shell + '\nboot();\n', 1)
source = source.replace('<meta name="theme-color" content="#33507c">', '<meta name="theme-color" content="#22664e">', 1)

temporary = target.with_suffix('.html.tmp')
temporary.write_text(source, encoding='utf-8', newline='')
for attempt in range(9):
    try:
        os.replace(temporary, target)
        break
    except PermissionError:
        if attempt == 8:
            raise
        time.sleep(.15)
print('Applied offline theme, workspace navigation and course overview; existing curriculum and storage preserved.')
