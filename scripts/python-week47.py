"""Append Week 47 only after executing every authored example and solution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'docs/python-week47'
DAYS = {f'47.{day}': {'parts': []} for day in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + '\n'


def S(t, v=None, **extra):
    return {'t': t, **({'v': v} if v is not None else {}), **extra}


def prose(text):
    return text


def L(day, title, goal, terms, text, example, task, solution, challenge, stretch,
      quiz, wrong, right, why, syntax=None, shell=None, figure=None):
    goal, text, task, challenge, wrong, right, why = map(prose, [goal, text, task, challenge, wrong, right, why])
    quiz = [tuple(prose(value) for value in question) for question in quiz]
    terms = [(name, prose(note)) for name, note in terms]
    if figure:
        figure = tuple(prose(value) for value in figure)
    parts = DAYS[f'47.{day}']['parts']
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
        S('ex', task, practiceId=f'47.{day}.{index}.build'), answer,
        S('ex', 'Mini challenge: ' + challenge, practiceId=f'47.{day}.{index}.challenge'), extra,
        S('try', q=quiz[0][0], code='# Explain your prediction before revealing.', a=quiz[0][1], why=quiz[0][4]),
        S('checkpoint', lesson={'id': f'course:47.{day}.{index}', 'quiz': questions}),
        S('key', goal)
    ])
    parts.append({'title': title, 'sections': sections})
    JOBS.extend([(clean(example), out, picture), (clean(solution), answer, None), (clean(stretch), extra, None)])


for name in ['python-week47-a.py', 'python-week47-day2.py', 'python-week47-b.py', 'python-week47-c.py']:
    exec(compile((ROOT / 'scripts' / name).read_text(encoding='utf-8'), name, 'exec'))


def write():
    target = ROOT / 'study-hub.html'
    original = target.read_text(encoding='utf-8')
    start = original.index('const DAY_TEACH = {')
    end = original.index('\n};\n\nconst REST_DAY', start)
    if any(json.dumps(key) + ':' in original[start:end] for key in DAYS):
        raise RuntimeError('Week47 already exists; refusing overwrite')
    assert [len(day['parts']) for day in DAYS.values()] == [6] * 6
    for number, (code, _, _) in enumerate(JOBS, 1):
        compile(code, f'Week47 example {number}', 'exec')
    files = {name: (PROJECT / name).read_text(encoding='utf-8') for name in ['lab.py','bundle.py','api.py','lesson_support.py']}
    bootstrap = ('import sys\nfrom pathlib import Path\n'
                 'for name,source in ' + repr(files) + '.items():\n    Path(name).write_text(source,encoding="utf-8")\n'
                 'for name in ["lab","bundle","api","lesson_support"]:sys.modules.pop(name,None)\n'
                 'sys.path.insert(0,str(Path.cwd()))\n')
    with tempfile.TemporaryDirectory(prefix='studyhub-w47-verify-') as folder:
        source, output = Path(folder) / 'examples.json', Path(folder) / 'results.json'
        source.write_text(json.dumps([bootstrap + code for code, _, _ in JOBS]), encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'scripts/python-example-worker.py'), str(source), str(output)],
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
    DAYS['47.0']['parts'][0]['sections'].insert(2, S('tip',
        'Build on Weeks 44–46. Take as many sessions as needed. Every Python example and solution below was executed in an owned temporary folder. '
        'Use docs/python-week47/README.md for one-time setup; text, outputs and six charts are embedded for offline reading. '
        'Examples importing lab, bundle, api or lesson_support use those supplied project files beside your practice script. '
        'The dataset is a new fixed simulation, not your progress or actual customer evidence. The optional inference service runs only on your own loopback interface.'))
    DAYS['47.5']['parts'][5]['sections'].extend([
        S('p', 'Practice folder: docs/python-week47. Install requirements-dev.txt once, run python lab.py --output artifacts, then python api.py --bundle artifacts/model.json --port 8047. '
          'Open http://127.0.0.1:8047/docs locally. This is a tested local inference release; GitHub Pages hosts the lessons and does not run a Python service. '
          'The simulator cannot establish real customer performance. Week 48 continues with unsupervised learning and neural-network foundations.'),
        S('p', 'Optional primary references: https://scikit-learn.org/stable/modules/cross_validation.html · '
          'https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html · '
          'https://scikit-learn.org/stable/modules/grid_search.html · '
          'https://scikit-learn.org/stable/modules/classification_threshold.html · '
          'https://shap.readthedocs.io/en/stable/generated/shap.LinearExplainer.html · '
          'https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html · '
          'https://scikit-learn.org/stable/model_persistence.html · https://fastapi.tiangolo.com/tutorial/body/ . '
          'Original lesson explanations and executed outputs remain embedded offline.')])
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
    print('Added Week47: 6 days, 36 parts, 72 exercises, 72 explained quiz questions, 108 executed snippets, 6 embedded charts.')


if __name__ == '__main__':
    write()
