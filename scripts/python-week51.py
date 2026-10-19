"""Append Week 51 only after executing every authored example and solution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'docs/python-week51'
DAYS = {f'51.{day}': {'parts': []} for day in range(6)}
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
    parts = DAYS[f'51.{day}']['parts']
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
        S('ex', task, practiceId=f'51.{day}.{index}.build'), answer,
        S('ex', 'Mini challenge: ' + challenge, practiceId=f'51.{day}.{index}.challenge'), extra,
        S('try', q=quiz[0][0], code='# Explain your prediction before revealing.', a=quiz[0][1], why=quiz[0][4]),
        S('checkpoint', lesson={'id': f'course:51.{day}.{index}', 'quiz': questions}),
        S('key', goal)
    ])
    parts.append({'title': title, 'sections': sections})
    if diagram:
        DIAGRAMS.append((picture, diagram[0], diagram[1]))
    JOBS.extend([(clean(example), out, None if diagram else picture), (clean(solution), answer, None), (clean(stretch), extra, None)])


for name in ['python-week51-a.py', 'python-week51-b.py', 'python-week51-c.py']:
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
        raise RuntimeError('Week51 already exists; refusing overwrite')
    assert [len(day['parts']) for day in DAYS.values()] == [6] * 6
    for number, (code, _, _) in enumerate(JOBS, 1):
        compile(code, f'Week51 example {number}', 'exec')
    render_diagrams()
    files = {str(path.relative_to(PROJECT)).replace('\\', '/'): path.read_text(encoding='utf-8')
             for path in PROJECT.rglob('*')
             if path.is_file() and (path.suffix in {'.py', '.toml', '.md', '.yml', '.txt'} or path.name == 'LICENSE')
             and not any(piece.startswith('.') or piece in {'site', 'dist', 'build', 'artifacts', '__pycache__'}
                         or piece.endswith('.egg-info') for piece in path.relative_to(PROJECT).parts)}
    bootstrap = ('import sys\nfrom pathlib import Path\n'
                 'for name,source in ' + repr(files) + '.items():\n'
                 '    p=Path(name); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(source,encoding="utf-8")\n'
                 'for name in list(sys.modules):\n'
                 '    if name=="bench" or name=="studyhub_records" or name.startswith("studyhub_records."): sys.modules.pop(name,None)\n'
                 'sys.path.insert(0,str(Path.cwd()))\nsys.path.insert(0,str(Path.cwd()/"src"))\n')
    with tempfile.TemporaryDirectory(prefix='studyhub-w51-verify-') as folder:
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
    DAYS['51.0']['parts'][0]['sections'].insert(2, S('tip',
        'Work through these parts over as many sessions as needed. All 108 Python examples and solutions below were executed. '
        'Five original process diagrams and one measured benchmark chart are embedded offline. '
        'The reference runtime is Python 3.12+; the library itself needs only the standard library. '
        'Start in docs/python-week51 and follow its README setup: install requirements-dev.txt, then run '
        'python -m pip install --no-build-isolation --no-deps -e . using that practice virtual environment. '
        'This editable development install points imports at the supplied source; Day 3 explains why it is not a final wheel test. '
        'Imports of studyhub_records and bench refer to the supplied original practice project. '
        'Terminal blocks describe commands to run yourself; they are not simulated Python outputs. '
        'Timing/memory outputs are recorded observations, not guaranteed values for your device. '
        'Local wheel installation is verified; TestPyPI upload and upstream contribution remain manual online exercises.'))
    DAYS['51.5']['parts'][5]['sections'].extend([
        S('p', 'Practice project: docs/python-week51. Follow README.md for the prepared environment, tests, '
          'benchmark, strict documentation build and verify_release.py. The release verifier builds a wheel from '
          'the source archive and installs it into a fresh environment outside the checkout. It checks API, '
          'doctests, metadata and the installed CLI. It never accesses Study Hub saved data or performs an upload. '
          'Week 52 uses these skills in your final capstone.'),
        S('p', 'Primary references checked for this module: https://docs.python.org/3.12/library/profile.html · '
          'https://docs.python.org/3.12/library/timeit.html · https://docs.python.org/3.12/library/tracemalloc.html · '
          'https://kernprof.readthedocs.io/en/latest/auto/line_profiler.html · '
          'https://packaging.python.org/en/latest/tutorials/packaging-projects/ · '
          'https://packaging.python.org/en/latest/guides/using-testpypi/ · '
          'https://www.mkdocs.org/user-guide/writing-your-docs/ · https://semver.org/ · '
          'https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project . '
          'Original explanations, code, measured outputs and visuals remain available offline.')])
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
    print('Added Week51: 6 days, 36 parts, 72 exercises, 72 explained quiz questions, 108 executed snippets, 6 embedded visuals.')


if __name__ == '__main__':
    write()
