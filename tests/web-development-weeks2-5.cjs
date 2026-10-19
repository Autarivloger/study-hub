const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8'),pattern=/const WEBDEV_TEACH = ([\s\S]*?);\n\/\* WEB DEVELOPMENT TEACHING END \*\//;
const data=JSON.parse(html.match(pattern)[1]),counts={lessons:0,quizzes:0,exercises:0,examples:0,terms:0};
const baseline=cp.execFileSync('git',['show','5bf1f6b:study-hub.html'],{encoding:'utf8',maxBuffer:45e6});
assert.equal(html.replace(pattern,'TEACHING MAP'),baseline.replace(pattern,'TEACHING MAP'),'Unexpected change outside teaching content: original courses, UI, storage and roadmap must be identical');
const oldData=JSON.parse(baseline.match(pattern)[1]);
for(const [id,l] of Object.entries(oldData))assert.deepEqual(data[id],l,'Existing lesson changed: '+id);
assert.equal(Object.keys(data).length,Object.keys(oldData).length+28);
for(let w=2;w<=5;w++){
 const {lessons,examples}=require('../scripts/web-development-week'+w+'-content.cjs');
 assert.deepEqual(Object.keys(lessons),Array.from({length:7},(_,i)=>w+'.'+(i+1)));
 for(const [id,l] of Object.entries(lessons)){
  assert.deepEqual(data[id],l);assert.equal(l.id,'webdev:'+id);assert(l.objective&&l.reflection);
  assert(l.sections.filter(s=>s.t==='h'&&s.v.startsWith('Part ')).length>=3);
  assert(l.sections.filter(s=>s.t==='try').length>=(id.endsWith('.7')?18:5));
  assert(l.sections.some(s=>s.t==='sol'));assert(l.sections.some(s=>s.t==='key'));
  assert(l.quiz.length>=(id.endsWith('.7')?12:6));
  for(const q of l.quiz){assert.equal(new Set(q.options).size,3);assert(q.q&&q.why);assert(q.correct>=0&&q.correct<3);}
  for(const s of l.sections){
   assert(!/\b(TODO CONTENT|PLACEHOLDER|lorem ipsum)\b/i.test(JSON.stringify(s)));
   if(['code','try','sol','mis'].includes(s.t))assert(['text','html'].includes(s.lang),'Untaught executable syntax '+id);
  }
  counts.lessons++;counts.quizzes+=l.quiz.length;counts.exercises+=l.sections.filter(s=>s.t==='try').length;counts.terms+=l.sections.filter(s=>s.t==='new').length;
 }
 for(const [name,source] of Object.entries(examples)){
  assert.equal(fs.readFileSync('docs/web-development-week'+w+'/examples/'+name+'.html','utf8').trimEnd(),source);
  assert(source.startsWith('<!doctype html>'));assert(!/<script\b|https?:\/\/|<link\b/i.test(source),'Examples must work offline without scripts/external assets');counts.examples++;
 }
}
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
console.log('PASS: original HTML outside teaching map byte-identical; Week1 unchanged; all 156-week roadmap and storage functions unchanged. New teaching totals:',counts);
