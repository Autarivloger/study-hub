"""Append only Week42 after running every authored Python example/solution."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import time

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT/'docs/python-week42'
DAYS={f'42.{d}':{'parts':[]} for d in range(6)}
JOBS=[]

def clean(code):return textwrap.dedent(code).strip()+'\n'
def S(t,v=None,**extra):return {'t':t,**({'v':v} if v is not None else {}),**extra}
def L(day,title,goal,terms,text,example,task,solution,challenge,stretch,quiz,wrong,right,why,syntax=None,shell=None):
    parts=DAYS[f'42.{day}']['parts'];index=len(parts)
    out=S('out','');answer=S('sol',code=clean(solution),out='',why=why);extra=S('sol',code=clean(stretch),out='',why=why)
    questions=[]
    for n,(q,a,b,c,reason) in enumerate(quiz):
        correct=(index+n)%3;options=[a,b,c]
        for _ in range(correct):options.insert(0,options.pop())
        questions.append({'q':q,'options':options,'correct':correct,'why':reason})
    sections=[S('h',title),S('key','Learning objective: '+goal)]
    sections.extend(S('new',name,note=note) for name,note in terms)
    sections.extend(S('p',p) for p in text.split('\n\n'))
    if syntax:sections.append(S('syn',syntax,note='Read this pattern before the worked example.'))
    else:sections.append(S('syn',right,note='The corrected pattern used in this part.'))
    if shell:sections.append(S('sh',shell))
    sections.extend([S('code',clean(example)),out,S('p',why),S('mis',wrong=wrong,right=right,why=why),S('ex',task,practiceId=f'42.{day}.{index}.build'),answer,S('ex','Mini challenge: '+challenge,practiceId=f'42.{day}.{index}.challenge'),extra,S('try',q=quiz[0][0],code='# Explain your reasoning before revealing.',a=quiz[0][1],why=quiz[0][4]),S('checkpoint',lesson={'id':f'course:42.{day}.{index}','quiz':questions}),S('key',goal)])
    parts.append({'title':title,'sections':sections});JOBS.extend([(clean(example),out),(clean(solution),answer),(clean(stretch),extra)])

for name in ['python-week42-a.py','python-week42-b.py','python-week42-c.py']:
    exec(compile((ROOT/'scripts'/name).read_text(encoding='utf-8'),name,'exec'))

def write():
    target=ROOT/'study-hub.html';original=target.read_text(encoding='utf-8');start=original.index('const DAY_TEACH = {');end=original.index('\n};\n\nconst REST_DAY',start)
    if any(json.dumps(key)+':' in original[start:end] for key in DAYS):raise RuntimeError('Week42 already exists; refusing overwrite')
    assert [len(v['parts']) for v in DAYS.values()]==[6]*6
    for number,(code,_) in enumerate(JOBS,1):
        compile(code,f'Week42 example {number}','exec')
    public=[PROJECT/n for n in ['app.py','server.py','manage.py','healthcheck.py','ops.py','lesson_support.py','Dockerfile','.dockerignore','.gitignore','compose.yaml','alembic.ini','requirements.txt','requirements-dev.txt','pyproject.toml','postgres/init-db.sh','container_smoke.py']]
    for folder in ['orm_api','migrations','tests']:
        public.extend(p for p in (PROJECT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in {'.py','.mako','.html','.css','.js'})
    files={str(p.relative_to(PROJECT)).replace('\\','/'):p.read_text(encoding='utf-8') for p in public}
    bootstrap='import sys\nfrom pathlib import Path\nfor name,source in '+repr(files)+'.items():\n    p=Path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(source,encoding="utf-8")\nfor name in list(sys.modules):\n    if name in {"orm_api","lesson_support","ops","healthcheck","server"} or name.startswith("orm_api."):sys.modules.pop(name,None)\nsys.path.insert(0,str(Path.cwd()))\n'
    with tempfile.TemporaryDirectory(prefix='studyhub-w42-verify-') as folder:
        source=Path(folder)/'examples.json';output=Path(folder)/'results.json';source.write_text(json.dumps([bootstrap+code for code,_ in JOBS]),encoding='utf-8')
        subprocess.run([sys.executable,str(ROOT/'scripts/python-example-worker.py'),str(source),str(output)],check=True,timeout=450,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','MPLBACKEND':'Agg','OPENBLAS_NUM_THREADS':'1'})
        results=json.loads(output.read_text(encoding='utf-8'))
    for (_,destination),result in zip(JOBS,results,strict=True):destination['v' if destination['t']=='out' else 'out']=result['out']
    DAYS['42.0']['parts'][0]['sections'].insert(2,S('tip','Keep docs/python-week42 as a separate practice folder. Python examples and their outputs are executed in fresh owned temporary folders with that project supplied. Terminal blocks are real Docker/hosting exercises, not simulated command output. Docker commands need Docker Engine/Desktop and downloaded images. The local authoring machine has no Docker; the Week42 GitHub workflow builds and tests actual containers. Study Hub itself remains an offline HTML learning app.'))
    final=DAYS['42.5']['parts'][5]['sections']
    final.extend([S('p','Practice project: docs/python-week42. Start with its README, install requirements-dev.txt, run python ops.py init-secrets, then docker compose up --build -d --wait api. Open http://127.0.0.1:8042/docs. Compose runs PostgreSQL, one migration job and the Notes API. This recipe does not create a paid hosting account or deploy your learner data. Use fictional staging data when following the public-host checklist.'),S('p','Primary references: https://docs.docker.com/get-started/docker-overview/ · https://docs.docker.com/build/building/best-practices/ · https://docs.docker.com/compose/how-tos/startup-order/ · https://docs.docker.com/compose/how-tos/use-secrets/ · https://fastapi.tiangolo.com/deployment/docker/ · https://render.com/docs/deploy-fastapi · https://www.postgresql.org/docs/17/backup-dump.html . Original explanations and examples are embedded for offline reading; links are optional further reading.')])
    addition='\n'.join(json.dumps(k)+': '+json.dumps(v,ensure_ascii=False,indent=2)+',' for k,v in DAYS.items()).replace('</','<\\/')
    prefix=original[:end].rstrip();prefix+=',' if not prefix.endswith(',') else ''
    temp=target.with_suffix('.html.tmp');temp.write_text(prefix+'\n'+addition+original[end:],encoding='utf-8',newline='')
    for attempt in range(9):
        try:temp.replace(target);break
        except PermissionError:
            if attempt==8:raise
            time.sleep(.15)
    print('Added Week42: 6 days, 36 parts, 72 exercises, 72 explained quiz questions, 108 executed Python examples/solutions.')

if __name__=='__main__':write()
