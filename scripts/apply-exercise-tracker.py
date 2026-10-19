"""Embed an additive exercise log into the existing offline To-Do view."""
from pathlib import Path
import os
import time

root = Path(__file__).resolve().parent.parent
target = root / 'study-hub.html'
source = target.read_text(encoding='utf-8')
assert '/* EXERCISE TRACKER START' not in source

def once(old, new):
    global source
    assert source.count(old) == 1, old[:100]
    source = source.replace(old, new, 1)

once('data-todo-mode="tasks" aria-pressed="false">Tasks</button></div>', 'data-todo-mode="tasks" aria-pressed="false">Tasks</button><button type="button" class="btn secondary btn-sm" data-todo-mode="exercise" aria-pressed="false">Exercise</button></div>')
once('      <div id="taskPane" hidden><div id="todoList"></div></div>', '      <div id="taskPane" hidden><div id="todoList"></div></div>\n      <div id="exercisePane" hidden></div>')
once('  d.timerSettings = d.timerSettings ||', '  d.exerciseTracker = exerciseDefaults(d.exerciseTracker);\n  d.timerSettings = d.timerSettings ||')
once('  habitMerge(incoming.habitTracker);', '  habitMerge(incoming.habitTracker);\n  exerciseMerge(incoming.exerciseTracker);')
once('  renderHabitTracker();renderTaskList();', '  renderHabitTracker();renderTaskList();\n  if(todoMode==="exercise")renderExerciseTracker();\n  document.getElementById("exercisePane").hidden=todoMode!=="exercise";')
css = (root / 'scripts/exercise-tracker.css').read_text(encoding='utf-8')
js = (root / 'scripts/exercise-tracker.js').read_text(encoding='utf-8')
source = source.replace('</style>', css + '\n</style>', 1)
once('/* ============ Storage ============ */', js + '\n/* ============ Storage ============ */')
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
print('Added Exercise tab, exercise names and dated logs with additive backup/sync records.')
