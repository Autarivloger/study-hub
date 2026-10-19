const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const old=cp.execFileSync('git',['show','5ad53f1:study-hub.html'],{encoding:'utf8',maxBuffer:40e6});
const end=';\nlet cyberPage';
function data(s,marker,boundary){const a=s.indexOf(marker)+marker.length,b=s.indexOf(boundary,a);assert(a>=marker.length&&b>a);return JSON.parse(s.slice(a,b));}
const marker='const CYBERSECURITY_TEACH = ',road='const CYBERSECURITY_ROADMAP = ';
const lessons=data(html,marker,end),before=data(old,marker,end);
const weeks=data(html,road,';\nconst CYBERSECURITY_TEACH');
assert.deepEqual(weeks.slice(0,8),data(old,road,';\nconst CYBERSECURITY_TEACH'),'Previous8 weeks changed');
assert.deepEqual(weeks,JSON.parse(fs.readFileSync('scripts/cybersecurity-roadmap.json','utf8')));
assert.equal(weeks.length,16);
weeks.forEach((w,i)=>{assert.equal(w.week,i+1);assert.deepEqual(w.days.map(d=>d.day),[1,2,3,4,5,6,7]);for(const d of w.days){assert(d.focus&&d.topics.length);if(w.week>=9)assert(d.python.length);}});
for(const [id,l] of Object.entries(before))assert.deepEqual(lessons[id],l,'Old teaching changed '+id);
assert.deepEqual(Object.keys(lessons).filter(k=>!before[k]),Array.from({length:7},(_,i)=>'9.'+(i+1)));
let normal=html;
for(const [mark,boundary] of [[marker,end],[road,';\nconst CYBERSECURITY_TEACH']]){let a=normal.indexOf(mark)+mark.length,b=normal.indexOf(boundary,a);let oldA=old.indexOf(mark)+mark.length,oldB=old.indexOf(boundary,oldA);normal=normal.slice(0,a)+old.slice(oldA,oldB)+normal.slice(b);}
const changes=[
 ["' + CYBERSECURITY_ROADMAP.length + ' weeks · Foundations → Defensive Python · Study at your own pace",'2 months · 8 weeks · Start from scratch'],
 ["'<span class=\"wc-prog\">Day 1–Day 7 · ' + (CYBERSECURITY_TEACH[item.week+\".1\"] ? 'Lessons ready' : 'Roadmap') + '</span></button>';","'<span class=\"wc-prog\">Day 1–Day 7</span></button>';"],
 ["(lesson ? cyberLessonHtml(lesson,\"cyber:\"+week.week+\".\"+day.day) : '<p class=\"ls-box ls-tip\">Roadmap only. This day lists the next learning goals; its full teaching lesson will be added later.</p>')","(lesson ? cyberLessonHtml(lesson,\"cyber:\"+week.week+\".\"+day.day) : '')"],
 ['position===CYBERSECURITY_ROADMAP.length*7-1','position===55'],['position>=CYBERSECURITY_ROADMAP.length*7','position>=56']
];
for(const [a,b] of changes){assert.equal(normal.split(a).length,2);normal=normal.replace(a,b);}
assert.equal(normal,old,'Unexpected changes outside added data and five exact roadmap/navigation changes');
const authored=require('../scripts/cybersecurity-week9-content.cjs'),outputs=JSON.parse(fs.readFileSync('docs/cybersecurity-week9/verified-outputs.json','utf8'));
let snippets=0,questions=0,practice=0;
for(const [id,l] of Object.entries(authored)){
 assert(l.objective&&l.reflection);assert(l.sections.filter(s=>s.t==='h').length===5);
 const text=l.sections.filter(s=>!['code','out','sol','sh'].includes(s.t)).map(s=>s.v+' '+(s.note||'')).join(' ');
 assert(text.split(/\s+/).length>=550,'Thin teaching '+id);
 assert(!/[\u0900-\u097f]/.test(JSON.stringify(l)));
 let n=0;
 for(let i=0;i<l.sections.length;i++){const s=l.sections[i];if(s.t==='ex')practice++;
  if(s.t==='new')assert(s.note);
  if(!['code','sol'].includes(s.t))continue;
  const result=outputs[id][n++];assert.equal(result.code,s.t==='code'?s.v:s.code);
  const actual=cp.spawnSync(process.env.STUDY_HUB_PYTHON||'python',['-c',result.code],{cwd:'docs/cybersecurity-week9',encoding:'utf8',timeout:20000,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1',PYTHONUTF8:'1'}});
  assert.equal(actual.status,0,actual.stderr);assert.equal(actual.stderr,'');
  assert.equal(actual.stdout.replace(/\r\n/g,'\n').trimEnd(),result.out,'Executed output differs '+id);
  if(s.t==='code')l.sections[i+1].v=result.out;else s.out=result.out;snippets++;
 }
 questions+=l.checks.length;assert(l.checks.every(c=>c.q&&c.a&&c.why));
 assert.deepEqual(lessons[id],l,'Inline differs from authored/evaluated source '+id);
 for(const r of l.references)assert(r.url.startsWith('https://')||fs.existsSync(r.url));
}
assert.equal(snippets,21);assert.equal(practice,14);assert.equal(questions,52);
assert(fs.readFileSync('docs/cybersecurity-week9/sample-events.json').equals(fs.readFileSync('docs/cybersecurity-week7/sample-events.json')));
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/i.test(m[1])&&!/\bsrc=/.test(m[1]))new Function(m[2]);
console.log('PASS:16 weeks/112 roadmap days; Week9 seven English lessons,21 executed outputs,14 practices/challenges,52 reasoned checks. All prior content and storage code preserved; only five exact roadmap/navigation changes.');
