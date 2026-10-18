"""Append Week 50 only after executing every authored example and solution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'docs/python-week50'
DAYS = {f'50.{day}': {'parts': []} for day in range(6)}
JOBS = []
DIAGRAMS = []


def clean(code):
    return textwrap.dedent(code).strip() + '\n'


def S(t, v=None, **extra):
    return {'t': t, **({'v': v} if v is not None else {}), **extra}


def prose(text):
    return text


def L(day, title, goal, terms, text, example, task, solution, challenge, stretch,
      quiz, wrong, right, why, syntax=None, shell=None, figure=None, diagram=None):
    if diagram:
        assert figure is None
        figure = (diagram[0], diagram[2])
    goal, text, task, challenge, wrong, right, why = map(prose, [goal, text, task, challenge, wrong, right, why])
    quiz = [tuple(prose(value) for value in question) for question in quiz]
    terms = [(name, prose(note)) for name, note in terms]
    if figure:
        figure = tuple(prose(value) for value in figure)
    parts = DAYS[f'50.{day}']['parts']
    index = len(parts)
    out = S('out', '')
    answer = S('sol', code=clean(solution), out='', why='Practice check: ' + why)
    extra = S('sol', code=clean(stretch), out='', why='Challenge check: ' + why)
    picture = S('figure', src='', alt=figure[0], note=figure[1]) if figure else None
    questions = []
    for number, (q, a, b, c, reason) in enumerate(quiz):
        correct = (index + number) % 3
        options = [a, b, c]
        for _ in range(correct):
            options.insert(0, options.pop())
        questions.append(dict(q=q, options=options, correct=correct, why=reason))
    sections = [S('h', title), S('key', 'Learning objective: ' + goal)]
    sections.extend(S('new', name, note=note) for name, note in terms)
    sections.extend(S('p', paragraph) for paragraph in text.split('\n\n'))
    sections.append(S('syn', syntax or right, note='Pattern to understand before running the complete example.'))
    if shell:
        sections.append(S('sh', shell))
    sections.extend([S('code', clean(example)), out])
    if picture:
        sections.append(picture)
    sections.extend([
        S('p', why), S('mis', wrong=wrong, right=right, why=why),
        S('ex', task, practiceId=f'50.{day}.{index}.build'), answer,
        S('ex', 'Mini challenge: ' + challenge, practiceId=f'50.{day}.{index}.challenge'), extra,
        S('try', q=quiz[0][0], code='# Explain your prediction before revealing.', a=quiz[0][1], why=quiz[0][4]),
        S('checkpoint', lesson={'id': f'course:50.{day}.{index}', 'quiz': questions}),
        S('key', goal)
    ])
    parts.append({'title': title, 'sections': sections})
    if diagram:
        DIAGRAMS.append((picture, diagram[0], diagram[1]))
    JOBS.extend([(clean(example), out, None if diagram else picture), (clean(solution), answer, None), (clean(stretch), extra, None)])


for name in ['python-week50-a.py', 'python-week50-b.py', 'python-week50-c.py']:
    exec(compile((ROOT / 'scripts' / name).read_text(encoding='utf-8'), name, 'exec'))


def write():
    target = ROOT / 'study-hub.html'
    original = target.read_text(encoding='utf-8')
    start = original.index('const DAY_TEACH = {')
    end = original.index('\n};\n\nconst REST_DAY', start)
    if any(json.dumps(key) + ':' in original[start:end] for key in DAYS):
        raise RuntimeError('Week50 already exists; refusing overwrite')
    assert [len(day['parts']) for day in DAYS.values()] == [6] * 6
    for number, (code, _, _) in enumerate(JOBS, 1):
        compile(code, f'Week50 example {number}', 'exec')
    import base64
    import io
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    for picture, title, steps in DIAGRAMS:
        fig, ax = plt.subplots(figsize=(6.3, 4.6))
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis('off')
        ax.set_title(textwrap.fill(title, 54), fontsize=12, pad=14)
        spacing = 0.84 / len(steps)
        for index, step in enumerate(steps):
            y = .92 - spacing * index
            ax.add_patch(FancyBboxPatch((.07, y-.09), .86, .095,
                boxstyle='round,pad=0.012', facecolor='#e5f0f4', edgecolor='#247ba0'))
            ax.text(.5, y-.042, textwrap.fill(step, 52), ha='center', va='center', fontsize=10)
            if index:
                ax.annotate('', xy=(.5, y+.014), xytext=(.5, y+spacing-.105),
                    arrowprops={'arrowstyle':'->','color':'#cf6e27','lw':1.5})
        fig.tight_layout()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=110)
        plt.close(fig)
        picture['src'] = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')
    files = {name: (PROJECT / name).read_text(encoding='utf-8') for name in ['lab.py','collector.py','workers.py','sources.py']}
    bootstrap = ('import sys\nfrom pathlib import Path\n'
                 'for name,source in ' + repr(files) + '.items():\n    Path(name).write_text(source,encoding="utf-8")\n'
                 'for name in ["lab","collector","workers","sources"]:sys.modules.pop(name,None)\n'
                 'sys.path.insert(0,str(Path.cwd()))\n')
    with tempfile.TemporaryDirectory(prefix='studyhub-w50-verify-') as folder:
        source, output = Path(folder) / 'examples.json', Path(folder) / 'results.json'
        source.write_text(json.dumps([bootstrap + code for code, _, _ in JOBS]), encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'scripts/python-week50-worker.py'), str(source), str(output)],
                       check=True, timeout=600, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                       'MPLBACKEND': 'Agg', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1'})
        results = json.loads(output.read_text(encoding='utf-8'))
    for (_, destination, picture), result in zip(JOBS, results, strict=True):
        destination['v' if destination['t'] == 'out' else 'out'] = result['out']
        if picture:
            assert result['png'], 'Missing authored chart'
            picture['src'] = 'data:image/png;base64,' + result['png']
        else:
            assert not result['png'], 'Unexpected unembedded chart'
    DAYS['50.0']['parts'][0]['sections'].insert(2, S('tip',
        'Take as many sessions as needed. All 108 authored examples/solutions were executed, with five original diagrams and one measured timing chart embedded offline. '
        'Install docs/python-week50/requirements-dev.txt once. HTTP examples use the supplied owned loopback server; no external API, account or learner data is involved. '
        'Imports of collector, workers, sources and lab refer to those supplied files. Spawn-based worker functions must remain in their importable module. '
        'Use a saved script with an if __name__ == "__main__": guard for process-pool entry, especially on Windows. '
        'Recorded timings are observations for the declared fixture, not guaranteed speedups. The plotted example additionally uses requirements-authoring.txt.'))
    DAYS['50.5']['parts'][5]['sections'].extend([
        S('p', 'Practice folder: docs/python-week50. Follow README.md, run python -m pytest -q, then python lab.py --output artifacts. '
          'The default compares three complete collectors on 100 owned local URLs plus a separate pure-Python CPU experiment. '
          'Errors, cancellation, queue bounds, cleanup and equal outputs are tested; time ratios may favor a simpler method. '
          'Reports/results are per-run practice artifacts, not transactional Study Hub backups. Week 51 covers profiling, packaging and professional practice.'),
        S('p', 'Optional primary references: https://docs.python.org/3.12/library/threading.html · '
          'https://docs.python.org/3.12/library/multiprocessing.html · https://docs.python.org/3.12/library/concurrent.futures.html · '
          'https://docs.python.org/3.12/library/asyncio-task.html · https://docs.python.org/3.12/library/asyncio-queue.html · '
          'https://docs.python.org/3.13/howto/free-threading-python.html · https://www.python-httpx.org/async/ . '
          'Original explanations, checked outputs and figures remain readable offline.')])
    addition = '\n'.join(json.dumps(key) + ': ' + json.dumps(day, ensure_ascii=False, indent=2) + ','
                         for key, day in DAYS.items()).replace('</', '<\\/')
    prefix = original[:end].rstrip()
    prefix += ',' if not prefix.endswith(',') else ''
    temp = target.with_suffix('.html.tmp')
    temp.write_text(prefix + '\n' + addition + original[end:], encoding='utf-8', newline='')
    for attempt in range(9):
        try:
            temp.replace(target)
            break
        except PermissionError:
            if attempt == 8:
                raise
            time.sleep(.15)
    print('Added Week50: 6 days, 36 parts, 72 exercises, 72 explained quiz questions, 108 executed snippets, 6 embedded visuals.')


if __name__ == '__main__':
    write()
