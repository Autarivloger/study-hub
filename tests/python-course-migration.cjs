const fs=require('fs'),assert=require('assert'),cp=require('child_process'),path=require('path');
const html=fs.readFileSync('study-hub.html','utf8');
const before=cp.execFileSync('git',['show','5c88139:study-hub.html'],{encoding:'utf8',maxBuffer:32e6}).replace(/\r\n/g,'\n');
function read(text,name,ending){const p=text.indexOf('const '+name+' = '),s=p+('const '+name+' = ').length,e=text.indexOf(ending,s);return Function('return ('+text.slice(s,e+2)+')')();}
const old=read(before,'DAY_TEACH','\n};\n\nconst REST_DAY'),days=read(html,'DAY_TEACH','\n};\n\nconst REST_DAY'),lessons=read(before,'LESSONS','\n];');
const sections=d=>Array.isArray(d)?d:d.parts.flatMap(p=>p.sections),all=Object.values(days).flatMap(sections);
const stable=s=>{s={...s};delete s.practiceId;delete s.noteKey;return JSON.stringify(s);};
const available=new Map();for(const s of all){const k=stable(s);available.set(k,(available.get(k)||0)+1);}
function retained(s,where){const k=stable(s);assert(available.get(k)>0,'Content lost: '+where+' '+k.slice(0,100));available.set(k,available.get(k)-1);}
const ids=[];for(const [key,d]of Object.entries(old)){let n=0;for(const s of sections(d)){retained(s,key);if(s.t==='ex')ids.push(key+'.'+n++);}}
for(const l of lessons){for(const s of l.sections)retained(s,l.id);assert(all.some(s=>s.t==='checkpoint'&&s.lesson.id===l.id&&JSON.stringify(s.lesson.quiz)===JSON.stringify(l.quiz)),'Quiz lost: '+l.id);assert(all.some(s=>s.t==='sol'&&s.code===l.challenge.code&&s.out===l.challenge.out),'Challenge lost: '+l.id);for(const m of l.mistakes)assert(all.some(s=>s.t==='mis'&&s.wrong===m.wrong&&s.right===m.right&&s.why===m.why),'Mistake explanation lost: '+l.id);}
const plans=read(before,'WEEKS_A','\n];').filter(w=>w[0]<=9);
const actual=all.filter(s=>s.t==='ex').map(s=>s.practiceId);assert.equal(new Set(actual).size,actual.length,'Practice identities duplicated');assert.equal(ids.length,391);assert(ids.every(id=>actual.includes(id)),'Solved IDs lost');assert.equal(actual.length,391+54+lessons.reduce((n,l)=>n+l.sections.filter(s=>s.t==='ex').length+1,0)+plans.reduce((n,w)=>n+w[4].length+w[5].length+1,0));
for(const w of plans)for(const text of [...w[4].flatMap(d=>[d[1],d[2]]),...w[5],w[6]])assert(all.some(s=>typeof s.v==='string'&&s.v.includes(text)),'Original planning content lost: '+text);
for(const [key,d]of Object.entries(old)){const parts=Array.isArray(d)?[{sections:d}]:d.parts;parts.forEach((p,i)=>{const seen={};for(const s of p.sections.filter(s=>s.t==='h')){const slug=String(s.v).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,48)||'heading';const n=seen[slug]=(seen[slug]||0)+1;assert(all.some(t=>t.noteKey==='d'+key+'.'+i+'|'+slug+(n>1?'~'+n:'')),'Note identity lost');}});}
for(const l of lessons){const seen={};for(const s of l.sections.filter(s=>s.t==='h')){const slug=String(s.v).toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'').slice(0,48)||'heading';const n=seen[slug]=(seen[slug]||0)+1;assert(all.some(t=>t.noteKey==='l'+l.id+'|'+slug+(n>1?'~'+n:'')),'Legacy lesson note identity lost');}}
assert.equal(Object.keys(days).length,114);assert(html.includes('const LESSONS = [];'));assert(!html.includes('id="lsWhy'));
const bundled='C:/Users/vlogerautari/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const codes=[],positions=[];for(const [key,d]of Object.entries(days))for(const s of sections(d)){const code=s.t==='code'||s.t==='syn'?s.v:s.t==='sol'||s.t==='try'?s.code:null;if(code){codes.push(code);positions.push(key.split('.').map(Number));}}
const run=cp.spawnSync(bundled,['scripts/python-prerequisites.py'],{encoding:'utf8',input:JSON.stringify(codes),maxBuffer:32e6});assert.equal(run.status,0,run.stderr);const analyzed=JSON.parse(run.stdout);
const earliest={def:9,parameters:9,return:9,defaults:9,args:10,lambda:10,decorator:10,recursion:10,comprehension:11,generator:11,if:3,for:4,while:4,nested_loop:4,try:14,raise:14,with:15,class:18,inheritance:19};
analyzed.forEach((a,i)=>{for(const f of a.features)if(earliest[f])assert(positions[i][0]>=earliest[f],f+' appeared too early at '+positions[i].join('.'));if(a.features.includes('nested_loop'))assert(positions[i][0]>4||positions[i][1]>=3,'Nested loop before Day 4');});
let examples=0;for(const r of require('../scripts/python-course-starters.cjs')){const ss=days[r.week+'.'+r.day].parts[0].sections;for(const [code,out]of [[r.code,ss.find(s=>s.t==='out').v],[r.solution,ss.find(s=>s.t==='sol').out]]){const run=cp.spawnSync(bundled,['-c',code],{encoding:'utf8',input:r.input,timeout:4000});assert.equal(run.status,0,run.stderr);assert.equal(run.stdout.trimEnd(),out);examples++;}}
// Check every inline script, including bootstrap, without executing the app.
let checked=0;for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g)){new Function(m[1]);checked++;}
console.log(`PASS: all original course/lesson content retained, 391 stable IDs, preserved note keys, prerequisite ordering, ${examples} Python outputs, ${checked} JS scripts`);
