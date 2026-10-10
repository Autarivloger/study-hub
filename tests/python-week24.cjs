const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const baseline=cp.execFileSync('git',['show','4a1a694:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
function split(text){
 const start=text.indexOf('const DAY_TEACH = {');
 const end=text.indexOf('\n};\n\nconst REST_DAY',start);
 assert(start>=0&&end>start,'Teaching boundaries');
 return {before:text.slice(0,start),after:text.slice(end),
  days:Function('return ('+text.slice(start+'const DAY_TEACH = '.length,end+2)+')')()};
}
const old=split(baseline),current=split(html);
assert.equal(current.before,old.before,'Application code before teaching changed');
assert.equal(current.after,old.after,'Application code after teaching changed');
for(const [key,value] of Object.entries(old.days))assert.deepEqual(current.days[key],value,'Existing teaching changed: '+key);
assert.deepEqual(Object.keys(current.days).filter(k=>!Object.hasOwn(old.days,k)).sort(),['24.0','24.1','24.2','24.3','24.4','24.5']);
let parts=0,practice=0,questions=0,examples=0;
const ids=new Set(),quizIds=new Set();
for(let d=0;d<6;d++){
 const day=current.days['24.'+d];
 assert(day.parts.length>=3,'Day must be split into sufficient teaching parts');
 for(const part of day.parts){
  parts++;
  const sections=part.sections,types=new Set(sections.map(s=>s.t));
  for(const t of ['h','key','new','p','syn','code','out','mis','ex','sol','try','checkpoint'])assert(types.has(t),'Missing structure: '+part.title+' '+t);
  for(let i=0;i<sections.length;i++){
   const s=sections[i];
   if(s.t==='new')assert(s.v&&s.note,'New concept must be explained');
   if(s.t==='ex'){assert(!ids.has(s.practiceId),'Duplicate practice id');ids.add(s.practiceId);practice++;}
   if((s.t==='code'&&sections[i+1]?.t==='out')||(s.t==='sol'&&s.code&&Object.hasOwn(s,'out')))examples++;
   if(s.t==='checkpoint'){
    assert(!quizIds.has(s.lesson.id),'Duplicate quiz id');quizIds.add(s.lesson.id);
    for(const q of s.lesson.quiz){questions++;assert(q.options.length===3&&q.correct>=0&&q.correct<3&&q.why,'Invalid quiz');}
   }
  }
 }
}
assert.equal(parts,24);assert.equal(practice,48);assert.equal(questions,56);assert.equal(examples,72);
for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(match[1]);
console.log('PASS: Week24 24 parts, 48 practice prompts, 56 questions, 72 runnable outputs; all previous content and application/storage code unchanged; JS syntax valid.');
