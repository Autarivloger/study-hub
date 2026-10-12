const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const baseline=cp.execFileSync('git',['show','3cb4b65:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
function split(text){
 const start=text.indexOf('const DAY_TEACH = {'),end=text.indexOf('\n};\n\nconst REST_DAY',start);
 assert(start>=0&&end>start);
 return {before:text.slice(0,start),after:text.slice(end),days:Function('return ('+text.slice(start+'const DAY_TEACH = '.length,end+2)+')')()};
}
const old=split(baseline),current=split(html);
assert.equal(current.before,old.before,'Application before teaching changed');
assert.equal(current.after,old.after,'Application after teaching changed');
for(const [key,value] of Object.entries(old.days))assert.deepEqual(current.days[key],value,'Previous course changed: '+key);
assert.deepEqual(Object.keys(current.days).filter(key=>!Object.hasOwn(old.days,key)),['26.0','26.1','26.2','26.3','26.4','26.5']);
let parts=0,practice=0,questions=0,examples=0;
const ids=new Set(),quizIds=new Set();
for(let day=0;day<6;day++){
 const lesson=current.days['26.'+day];assert.equal(lesson.parts.length,4);
 for(const part of lesson.parts){
  parts++;
  const types=new Set(part.sections.map(section=>section.t));
  for(const type of ['h','key','new','p','syn','code','out','mis','ex','sol','try','checkpoint'])assert(types.has(type),'Missing teaching structure '+part.title+' '+type);
  for(let i=0;i<part.sections.length;i++){
   const section=part.sections[i];
   if(section.t==='new')assert(section.v&&section.note);
   if(section.t==='ex'){assert(!ids.has(section.practiceId));ids.add(section.practiceId);practice++;}
   if((section.t==='code'&&part.sections[i+1]?.t==='out')||(section.t==='sol'&&section.code&&Object.hasOwn(section,'out')))examples++;
   if(section.t==='checkpoint'){
    assert(!quizIds.has(section.lesson.id));quizIds.add(section.lesson.id);
    for(const question of section.lesson.quiz){questions++;assert(question.options.length===3&&question.correct>=0&&question.correct<3&&question.why);}
   }
  }
 }
}
assert.equal(parts,24);assert.equal(practice,48);assert.equal(questions,58);assert.equal(examples,72);

for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(match[1]);
console.log('PASS: Week26 6 days/24 parts/48 practice prompts/58 questions/72 runnable outputs; all prior content and application/storage code identical; script boundaries and JS valid.');
