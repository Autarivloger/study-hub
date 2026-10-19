"""Append Week 52 only after executing every authored example and solution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'docs/python-week52'
DAYS = {f'52.{day}': {'parts': []} for day in range(6)}
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
    parts = DAYS[f'52.{day}']['parts']
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
        S('ex', task, practiceId=f'52.{day}.{index}.build'), answer,
        S('ex', 'Mini challenge: ' + challenge, practiceId=f'52.{day}.{index}.challenge'), extra,
        S('try', q=quiz[0][0], code='# Explain your prediction before revealing.', a=quiz[0][1], why=quiz[0][4]),
        S('checkpoint', lesson={'id': f'course:52.{day}.{index}', 'quiz': questions}),
        S('key', goal)
    ])
    parts.append({'title': title, 'sections': sections})
    if diagram:
        DIAGRAMS.append((picture, diagram[0], diagram[1]))
    JOBS.extend([(clean(example), out, None if diagram else picture), (clean(solution), answer, None), (clean(stretch), extra, None)])


for name in ['python-week52-a.py', 'python-week52-b.py', 'python-week52-c.py']:
    exec(compile((ROOT / 'scripts' / name).read_text(encoding='utf-8'), name, 'exec'))


def render_diagrams():
    import base64
    import io
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    for picture, title, steps in DIAGRAMS:
        fig, ax = plt.subplots(figsize=(4.6, 5.9))
        ax.set(xlim=(0, 1), ylim=(0, 1))
        ax.axis('off')
        ax.set_title(textwrap.fill(title, 37), fontsize=13, pad=14)
        spacing = 0.84 / len(steps)
        for index, step in enumerate(steps):
            y = .92 - spacing * index
            ax.add_patch(FancyBboxPatch((.07, y-.115), .86, .12,
                boxstyle='round,pad=0.012', facecolor='#e5f0f4', edgecolor='#247ba0'))
            ax.text(.5, y-.055, textwrap.fill(step, 33), ha='center', va='center', fontsize=12)
            if index:
                ax.annotate('', xy=(.5, y+.012), xytext=(.5, y+spacing-.12),
                    arrowprops={'arrowstyle':'->','color':'#cf6e27','lw':1.5})
        fig.tight_layout()
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=110)
        plt.close(fig)
        picture['src'] = 'data:image/png;base64,' + base64.b64encode(buffer.getvalue()).decode('ascii')


def write():
    target = ROOT / 'study-hub.html'
    original = target.read_text(encoding='utf-8')
    start = original.index('const DAY_TEACH = {')
    end = original.index('\n};\n\nconst REST_DAY', start)
    if any(json.dumps(key) + ':' in original[start:end] for key in DAYS):
        raise RuntimeError('Week52 already exists; refusing overwrite')
    assert [len(day['parts']) for day in DAYS.values()] == [6] * 6
    for number, (code, _, _) in enumerate(JOBS, 1):
        compile(code, f'Week52 example {number}', 'exec')
    render_diagrams()
    files = {str(path.relative_to(PROJECT)).replace('\\', '/'): path.read_text(encoding='utf-8')
             for path in PROJECT.rglob('*')
             if path.is_file() and (path.suffix in {'.py', '.toml', '.md', '.yml', '.txt', '.html'} or path.name in {'LICENSE', 'Dockerfile'})
             and not any(piece.startswith('.') or piece in {'site', 'dist', 'build', 'artifacts', '__pycache__'}
                         or piece.endswith('.egg-info') for piece in path.relative_to(PROJECT).parts)}
    bootstrap = ('import sys\nfrom pathlib import Path\n'
                 'for name,source in ' + repr(files) + '.items():\n'
                 '    p=Path(name); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(source,encoding="utf-8")\n'
                 'for name in list(sys.modules):\n'
                 '    if name in {"smoke","release_check","capstone"} or name.startswith("capstone."): sys.modules.pop(name,None)\n'
                 'sys.path.insert(0,str(Path.cwd()))\n')
    with tempfile.TemporaryDirectory(prefix='studyhub-w52-verify-') as folder:
        source, output = Path(folder) / 'examples.json', Path(folder) / 'results.json'
        source.write_text(json.dumps([bootstrap + code for code, _, _ in JOBS]), encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'scripts/python-example-worker.py'), str(source), str(output)],
                       check=True, timeout=600, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1',
                       'MPLBACKEND': 'Agg', 'OPENBLAS_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1',
                       'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'PYTHONUTF8': '1'})
        results = json.loads(output.read_text(encoding='utf-8'))
    for (_, destination, picture), result in zip(JOBS, results, strict=True):
        destination['v' if destination['t'] == 'out' else 'out'] = result['out']
        if picture:
            assert result['png'], 'Missing authored chart'
            picture['src'] = 'data:image/png;base64,' + result['png']
        else:
            assert not result['png'], 'Unexpected unembedded chart'
    DAYS['52.0']['parts'][0]['sections'].insert(2, S('tip',
        'The final week is a sequence of milestones, not a seven-day deadline. Use as many sessions as you need. '
        'All 108 authored Python examples and solutions below were executed. Five process diagrams and a measured local-query chart are embedded offline. '
        'Run examples from docs/python-week52 after following its README environment setup. Imports of capstone, smoke and release_check refer to the supplied original project. '
        'The reference app uses SQLite, FastAPI and Uvicorn, with its own database and browser interface; it does not read or modify Study Hub storage. '
        'HTTP and restore checks run on owned localhost services with synthetic data. The wheel-consumer exercise may download dependencies once '
        'unless you supply a prepared wheelhouse; the installed app and lesson reading work offline. '
        'Container and remote/second-device deployment steps are manual exercises, not claims that they have already run. '
        'Keep credentials out of source and notes. Distinguish completing a lesson from independently demonstrating the project.'))
    DAYS['52.5']['parts'][5]['sections'].extend([
        S('p', 'Capstone folder: docs/python-week52. Start with README.md and SPEC.md. Run tests, smoke.py for actual HTTP/restart/restore, '
          'and release_check.py for an installed-wheel rehearsal. ARCHITECTURE.md explains the design; DEPLOYMENT.md gives deliberate local/remote steps; '
          'RETROSPECTIVE.md includes a six-month practice plan. A localhost test does not prove a public or second-device deployment. '
          'Your final evidence is the behavior you can reproduce, explain, change and maintain. Existing Day 7 remains the course review/rest day.'),
        S('p', 'Primary references for further study: https://docs.python.org/3.12/library/sqlite3.html · '
          'https://fastapi.tiangolo.com/tutorial/testing/ · https://fastapi.tiangolo.com/tutorial/dependencies/ · '
          'https://fastapi.tiangolo.com/deployment/concepts/ · https://docs.pydantic.dev/latest/concepts/strict_mode/ · '
          'https://www.uvicorn.org/settings/ · https://docs.docker.com/engine/containers/run/ · '
          'https://packaging.python.org/en/latest/tutorials/packaging-projects/ . '
          'The original teaching text, runnable examples, recorded outputs and figures remain available offline.')])
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
    print('Added Week52: 6 days, 36 parts, 72 exercises, 72 explained quiz questions, 108 executed snippets, 6 embedded visuals.')


if __name__ == '__main__':
    write()
