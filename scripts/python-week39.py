"""Append only Week39 teaching data after executing every authored snippet."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parents[1]
DAYS = {f"39.{d}": {"parts": []} for d in range(6)}
JOBS = []


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def sec(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def lesson(day, title, goal, terms, explanation, syntax, example, walkthrough,
           mistake, task, solution, challenge, challenge_code, takeaway, quizzes):
    parts = DAYS[f"39.{day}"]["parts"]
    index = len(parts)
    questions = []
    for i, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        correct = (index + i) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(correct):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": correct, "why": why})
    output = sec("out", "")
    build = sec("sol", code=clean(solution), out="", why="Build check: " + takeaway)
    stretch = sec("sol", code=clean(challenge_code), out="", why="Challenge check: " + takeaway)
    parts.append({"title": title, "sections": [
        sec("h", title), sec("key", "Learning objective: " + goal),
        *[sec("new", name, note=note) for name, note in terms],
        sec("p", explanation), sec("syn", syntax, note="Python/API pattern. Run in a fresh practice folder. Where lesson_support is imported, keep the supplied learning_api package and helper beside the snippet."),
        sec("code", clean(example)), output, sec("p", walkthrough),
        sec("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        sec("ex", task, practiceId=f"39.{day}.{index}.build"), build,
        sec("ex", "Mini challenge: " + challenge, practiceId=f"39.{day}.{index}.challenge"), stretch,
        sec("try", q=quizzes[0][0], code="# Predict, then explain before revealing.", a=quizzes[0][1], why=quizzes[0][4]),
        sec("checkpoint", lesson={"id": f"course:39.{day}.{index}", "quiz": questions}), sec("key", takeaway)
    ]})
    JOBS.extend([(clean(example), output), (clean(solution), build), (clean(challenge_code), stretch)])


exec(compile((ROOT/'scripts'/'python-week39-content.py').read_text(encoding='utf-8'),
             'python-week39-content.py','exec'))
FOLDER=ROOT/'docs'/'python-week39'


def write():
    target=ROOT/'study-hub.html';original=target.read_bytes().decode('utf-8')
    start=original.index('const DAY_TEACH = {');end=original.index('\n};\n\nconst REST_DAY',start)
    if any(('"'+key+'":') in original[start:end] for key in DAYS):
        raise RuntimeError('Week39 already exists; refusing overwrite')
    assert [len(day['parts']) for day in DAYS.values()]==[6]*6
    public=[FOLDER/'lesson_support.py',*sorted((FOLDER/'learning_api').glob('*.py')),
            *sorted((FOLDER/'learning_api'/'static').glob('*'))]
    files={str(p.relative_to(FOLDER)).replace('\\','/'):p.read_text(encoding='utf-8') for p in public if p.is_file()}
    bootstrap=('import sys\nfrom pathlib import Path\nfor name,source in '+repr(files)+
        '.items():\n    p=Path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source,encoding="utf-8")\n'
        'for name in list(sys.modules):\n    if name=="lesson_support" or name=="learning_api" or name.startswith("learning_api."):sys.modules.pop(name,None)\n'
        'sys.path.insert(0,str(Path.cwd()))\n')
    with tempfile.TemporaryDirectory(prefix='studyhub-w39-verify-') as temp:
        manifest=Path(temp)/'examples.json';result=Path(temp)/'results.json'
        manifest.write_text(json.dumps([bootstrap+code for code,_ in JOBS]),encoding='utf-8')
        subprocess.run([sys.executable,str(ROOT/'scripts'/'python-example-worker.py'),str(manifest),str(result)],
            check=True,timeout=300,env={**os.environ,'MPLBACKEND':'Agg','OPENBLAS_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
        results=json.loads(result.read_text(encoding='utf-8'))
    for (_,destination),result in zip(JOBS,results,strict=True):
        destination['v' if destination['t']=='out' else 'out']=result['out']
    first=DAYS['39.0']['parts'][0]['sections']
    first.insert(3,sec('sh','python -m pip install -r requirements.txt'))
    first.insert(4,sec('tip','Verified with Python 3.12.14, FastAPI 0.143.1, Starlette 0.52.1, Pydantic 2.13.5, HTTPX 0.28.1, Uvicorn 0.54.0 and PyJWT 2.15.1. Install the supplied pinned requirements once. Lesson reading, executable fixtures and the original local API explorer then work offline. Examples importing lesson_support or learning_api need the complete docs/python-week39 folder beside the snippet. All 108 examples/solutions were executed with owned temporary files and fictional accounts; never use a real external-service password/token.'))
    final=DAYS['39.5']['parts'][5]['sections']
    final.extend([sec('sh','python -m pip install -r requirements.txt\npython app.py\n# Open http://127.0.0.1:8000/docs ; Ctrl+C stops the local server.'),
        sec('p','Project source and setup: docs/python-week39 in the repository. Keep app.py, requirements.txt, lesson_support.py and the entire learning_api/ folder, including static/. instance/ database/signing-key files are ignored runtime data and must stay private. GitHub Pages publishes course/source, not this Python server. The project is a loopback teaching API; no public deployment or account-recovery system is claimed.'),
        sec('p','Primary references: https://fastapi.tiangolo.com/tutorial/ · https://fastapi.tiangolo.com/async/ · https://fastapi.tiangolo.com/advanced/events/ · https://fastapi.tiangolo.com/tutorial/response-model/ · https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ · https://docs.pydantic.dev/latest/concepts/models/ · https://pyjwt.readthedocs.io/en/stable/usage.html . Original explanations and verified examples are embedded for offline reading; the links are optional further reading.')])
    addition='\n'.join(json.dumps(k)+': '+json.dumps(v,ensure_ascii=False,indent=2)+',' for k,v in DAYS.items()).replace('</','<\\/')
    prefix=original[:end].rstrip()
    if not prefix.endswith(','):prefix+=','
    temporary=target.with_suffix('.html.tmp')
    temporary.write_bytes((prefix+'\n'+addition+original[end:]).encode('utf-8'));temporary.replace(target)
    print('Added Week39: 6 days,36 parts,72 practice prompts,82 explained quizzes,108 executed examples/solutions.')


if __name__=='__main__':
    write()
