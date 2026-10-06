const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8').replace(/\r\n/g,'\n');
const before=cp.execFileSync('git',['show','a572ff3:study-hub.html'],{encoding:'utf8',maxBuffer:40e6}).replace(/\r\n/g,'\n');
function days(s){const a=s.indexOf('const DAY_TEACH = ')+18,b=s.indexOf('\n};\n\nconst REST_DAY',a);return Function('return ('+s.slice(a,b+2)+')')();}
const old=days(before),current=days(html);
for(const k of Object.keys(old))assert.deepEqual(current[k],old[k],'Old teaching changed '+k);
// Yoga now extends the UI; this test pins original Python teaching.
let count=0;const ids=new Set();
for(let d=0;d<6;d++){const lesson=current['20.'+d];assert(lesson.parts.length>=2);for(const p of lesson.parts){count++;for(const s of p.sections){if(s.t==='ex'){assert(s.practiceId);assert(!ids.has(s.practiceId));ids.add(s.practiceId);}if(s.t==='checkpoint')assert(s.lesson.quiz.length);}}}
assert.equal(count,13);assert.equal(ids.size,19);
console.log('PASS: Week20 13 parts,19 exercises; preceding Python teaching unchanged');
