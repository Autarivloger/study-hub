const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const baseline=cp.execFileSync('git',['show','966bdb1:study-hub.html'],{encoding:'utf8',maxBuffer:46e6});
function split(text){
 const start=text.indexOf('const DAY_TEACH = {'),end=text.indexOf('\n};\n\nconst REST_DAY',start);
 assert(start>=0&&end>start);
 return {before:text.slice(0,start),after:text.slice(end),days:Function('return ('+text.slice(start+'const DAY_TEACH = '.length,end+2)+')')()};
}
const old=split(baseline),current=split(html);
assert.equal(current.before,old.before,'Application before lessons changed');
assert.equal(current.after,old.after,'Application/storage/renderer code changed');
for(const [key,value] of Object.entries(old.days))assert.deepEqual(current.days[key],value,'Previous lesson changed: '+key);
assert.deepEqual(Object.keys(current.days).filter(k=>!Object.hasOwn(old.days,k)),['51.0','51.1','51.2','51.3','51.4','51.5']);
let parts=0,practice=0,questions=0,examples=0,figures=0;
const ids=new Set(),quizIds=new Set();
for(let day=0;day<6;day++){
 const lesson=current.days['51.'+day]; assert.equal(lesson.parts.length,[6,6,6,6,6,6][day]);
 for(const part of lesson.parts){
  parts++;
  const types=new Set(part.sections.map(s=>s.t));
  for(const type of ['h','key','new','p','syn','code','out','mis','ex','sol','try','checkpoint'])assert(types.has(type),part.title+' missing '+type);
  for(let i=0;i<part.sections.length;i++){
   const s=part.sections[i];
   if(s.t==='new')assert(s.v&&s.note);
   if(s.t==='ex'){assert.equal(part.sections[i+1]?.t,'sol');assert(!ids.has(s.practiceId));ids.add(s.practiceId);practice++;}
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
assert.equal(parts,36);assert.equal(practice,72);assert.equal(questions,72);assert.equal(examples,108);assert.equal(figures,6);
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json/.test(m[1]))continue;new Function(m[2]);}
console.log('PASS: Week51 six days/36 parts/72 practice prompts/72 quiz questions/108 executed outputs/6 embedded visuals; all previous lessons and all application/storage code identical including the premium theme and existing PNG renderer; JS valid.');
const workflow=fs.readFileSync('.github/workflows/python-week51.yml','utf8');
for(const marker of ['contents: read','persist-credentials: false','timeout-minutes: 10','python -m pytest','python -m ruff check .','python -m ruff format --check .','python verify_release.py --output artifacts/release.json'])assert(workflow.includes(marker));
assert(!workflow.includes('secrets.')&&!workflow.includes('pull_request_target')&&!workflow.includes('continue-on-error'));
