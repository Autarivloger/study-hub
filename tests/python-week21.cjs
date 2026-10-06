const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8').replace(/\r\n/g,'\n');
const before=cp.execFileSync('git',['show','1cdebf9:study-hub.html'],{encoding:'utf8',maxBuffer:40e6}).replace(/\r\n/g,'\n');
function days(s){const a=s.indexOf('const DAY_TEACH = ')+18,b=s.indexOf('\n};\n\nconst REST_DAY',a);return Function('return ('+s.slice(a,b+2)+')')();}
const old=days(before),current=days(html);
for(const k of Object.keys(old))assert.deepEqual(current[k],old[k],'Old teaching changed '+k);
// Yoga now extends the UI; this test pins original Python teaching.
let count=0,quizCount=0;const ids=new Set(),answers=new Set();
for(let d=0;d<6;d++){
 const lesson=current['21.'+d];assert(lesson.parts.length>=3);
 for(const p of lesson.parts){count++;for(const kind of ['h','key','new','p','syn','code','out','mis','ex','sol','try','checkpoint'])assert(p.sections.some(s=>s.t===kind),'Missing '+kind+' in '+p.title);
  for(const s of p.sections){if(s.t==='ex'){assert(s.practiceId);assert(!ids.has(s.practiceId));ids.add(s.practiceId);}if(s.t==='checkpoint'){quizCount++;for(const q of s.lesson.quiz){assert(q.options[q.correct]);assert.equal(new Set(q.options).size,q.options.length);answers.add(q.correct);}}}
 }
}
assert.equal(count,19);assert.equal(ids.size,38);assert.equal(quizCount,19);assert.equal(answers.size,3);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: Week21 19 parts,38 exercises,19 rotated quizzes; preceding Python teaching unchanged');
