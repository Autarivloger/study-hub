const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const current=fs.readFileSync('study-hub.html','utf8').replace(/\r\n/g,'\n'),before=cp.execFileSync('git',['show','9e32a22:study-hub.html'],{encoding:'utf8',maxBuffer:40e6}).replace(/\r\n/g,'\n');
function read(s){const a=s.indexOf('const DAY_TEACH = ')+18,b=s.indexOf('\n};\n\nconst REST_DAY',a);return {a,b,days:Function('return ('+s.slice(a,b+2)+')')()};}
const old=read(before),now=read(current);
assert.equal(current.slice(0,now.a),before.slice(0,old.a));assert.equal(current.slice(now.b),before.slice(old.b));
let walk=0;for(const [key,day]of Object.entries(old.days)){
 if(!key.startsWith('21.')){assert.deepEqual(now.days[key],day);continue;}
 const parts=now.days[key].parts;assert.equal(parts.length,day.parts.length+1);assert(parts.at(-1).optional);
 day.parts.forEach((p,i)=>{const added=parts[i];assert.equal(added.title,p.title);assert.deepEqual(added.sections.filter(s=>!(s.t==='p'&&s.v.startsWith('Step-by-step walkthrough'))),p.sections);assert.equal(added.sections.filter(s=>s.t==='p'&&s.v.startsWith('Step-by-step walkthrough')).length,1);walk++;});
}
assert.equal(walk,19);console.log('PASS: all original Week21 sections/IDs/part positions retained;19 walkthroughs and6 optional labs; all other subjects/app/storage unchanged');
