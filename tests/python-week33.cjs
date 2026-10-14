const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const baseline=cp.execFileSync('git',['show','c6c58c0:study-hub.html'],{encoding:'utf8',maxBuffer:33e6});
function split(text){
 const start=text.indexOf('const DAY_TEACH = {'),end=text.indexOf('\n};\n\nconst REST_DAY',start);
 assert(start>=0&&end>start);
 return {before:text.slice(0,start),after:text.slice(end),days:Function('return ('+text.slice(start+'const DAY_TEACH = '.length,end+2)+')')()};
}
const old=split(baseline),current=split(html);
assert.equal(current.before,old.before,'Application before lessons changed');
assert.equal(current.after,old.after,'Application/storage/renderer code changed');
for(const [key,value] of Object.entries(old.days))assert.deepEqual(current.days[key],value,'Previous lesson changed: '+key);
assert.deepEqual(Object.keys(current.days).filter(k=>!Object.hasOwn(old.days,k)),['33.0','33.1','33.2','33.3','33.4','33.5']);
let parts=0,practice=0,questions=0,examples=0,figures=0;
const ids=new Set(),quizIds=new Set();
for(let day=0;day<6;day++){
 const lesson=current.days['33.'+day]; assert.equal(lesson.parts.length,[5,4,4,5,5,5][day]);
 for(const part of lesson.parts){
  parts++;
  const types=new Set(part.sections.map(s=>s.t));
  for(const type of ['h','key','new','p','syn','code','out','figure','mis','ex','sol','try','checkpoint'])assert(types.has(type),part.title+' missing '+type);
  for(let i=0;i<part.sections.length;i++){
   const s=part.sections[i];
   if(s.t==='new')assert(s.v&&s.note);
   if(s.t==='ex'){assert(!ids.has(s.practiceId));ids.add(s.practiceId);practice++;}
   if(s.t==='figure'){
    figures++; assert.match(s.src,/^data:image\/png;base64,[A-Za-z0-9+/=]+$/);
    const png=Buffer.from(s.src.split(',')[1],'base64');
    assert.equal(png.subarray(1,4).toString(),'PNG'); assert(png.readUInt32BE(16)>300&&png.readUInt32BE(20)>100); assert(s.alt&&s.note);
   }
   if((s.t==='code'&&part.sections[i+1]?.t==='out')||(s.t==='sol'&&s.code&&Object.hasOwn(s,'out')))examples++;
   if(s.t==='checkpoint'){
    assert(!quizIds.has(s.lesson.id));quizIds.add(s.lesson.id);
    for(const q of s.lesson.quiz){questions++;assert(q.options.length===3&&q.correct>=0&&q.correct<3&&q.why);}
   }
  }
 }
}
assert.equal(parts,28);assert.equal(practice,56);assert.equal(questions,66);assert.equal(examples,84);assert.equal(figures,28);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: Week33 six days/28 parts/56 practice prompts/66 quiz questions/84 outputs/28 embedded PNGs; all previous lessons and all application/storage code identical including the existing PNG renderer; JS valid.');
