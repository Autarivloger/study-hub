"""Append Week 48 only after executing every authored example and solution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / 'docs/python-week48'
DAYS = {f'48.{day}': {'parts': []} for day in range(6)}
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
    parts = DAYS[f'48.{day}']['parts']
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
        S('ex', task, practiceId=f'48.{day}.{index}.build'), answer,
        S('ex', 'Mini challenge: ' + challenge, practiceId=f'48.{day}.{index}.challenge'), extra,
        S('try', q=quiz[0][0], code='# Explain your prediction before revealing.', a=quiz[0][1], why=quiz[0][4]),
        S('checkpoint', lesson={'id': f'course:48.{day}.{index}', 'quiz': questions}),
        S('key', goal)
    ])
    parts.append({'title': title, 'sections': sections})
    JOBS.extend([(clean(example), out, picture), (clean(solution), answer, None), (clean(stretch), extra, None)])


for name in ['python-week48-a.py', 'python-week48-b.py', 'python-week48-c.py']:
    exec(compile((ROOT / 'scripts' / name).read_text(encoding='utf-8'), name, 'exec'))


def write():
    target = ROOT / 'study-hub.html'
    original = target.read_text(encoding='utf-8')
    start = original.index('const DAY_TEACH = {')
    end = original.index('\n};\n\nconst REST_DAY', start)
    if any(json.dumps(key) + ':' in original[start:end] for key in DAYS):
        raise RuntimeError('Week48 already exists; refusing overwrite')
    assert [len(day['parts']) for day in DAYS.values()] == [6] * 6
    for number, (code, _, _) in enumerate(JOBS, 1):
        compile(code, f'Week48 example {number}', 'exec')
    files = {name: (PROJECT / name).read_text(encoding='utf-8') for name in ['lab.py','neural.py']}
    bootstrap = ('import sys\nfrom pathlib import Path\n'
                 'for name,source in ' + repr(files) + '.items():\n    Path(name).write_text(source,encoding="utf-8")\n'
                 'for name in ["lab","neural"]:sys.modules.pop(name,None)\n'
                 'sys.path.insert(0,str(Path.cwd()))\n')
    with tempfile.TemporaryDirectory(prefix='studyhub-w48-verify-') as folder:
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
    DAYS['48.0']['parts'][0]['sections'].insert(2, S('tip',
        'Build on Weeks 44–47. Use as many study sessions as needed. Every authored Python example and solution was executed. '
        'Install docs/python-week48/requirements-dev.txt once; supplied lab.py and neural.py helpers belong beside your practice script. '
        'The lesson text, outputs and eight charts are embedded offline. The practice project runs on CPU without accounts or dataset downloads. '
        'Simulated customer/fault data and bundled digits never read your learner progress.'))
    DAYS['48.5']['parts'][5]['sections'].extend([
        S('p', 'Practice folder: docs/python-week48. Follow README.md, run python -m pytest -q, then python lab.py --output artifacts. '
          'Reports preserve split definitions, selection rules, profiles, predictions and limitations. Reading final evidence consumes its untouched status; '
          'rerunning a fixed simulation is a reproducibility check, not new independent evidence. Week 49 explores advanced Python language features.'),
        S('p', 'Optional primary references: https://scikit-learn.org/stable/modules/clustering.html · '
          'https://scikit-learn.org/stable/modules/decomposition.html · https://scikit-learn.org/stable/modules/manifold.html · '
          'https://umap-learn.readthedocs.io/en/latest/parameters.html · https://scikit-learn.org/stable/modules/outlier_detection.html · '
          'https://docs.pytorch.org/tutorials/beginner/basics/intro.html · https://docs.pytorch.org/docs/stable/notes/randomness.html . '
          'Original explanations, checked outputs and charts remain readable offline.')])
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
    print('Added Week48: 6 days, 36 parts, 72 exercises, 72 explained quiz questions, 108 executed snippets, 8 embedded charts.')


if __name__ == '__main__':
    write()
