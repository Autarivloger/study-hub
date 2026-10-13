const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const before=cp.execFileSync('git',['show','f882966:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
function span(s,start,end){const a=s.indexOf(start),b=s.indexOf(end,a);assert(a>=0&&b>a);return s.slice(a,b);}
const raw=span(html,'const DAY_TEACH = {','\n};\n\nconst REST_DAY')+'\n}';
assert.equal(raw,span(before,'const DAY_TEACH = {','\n};\n\nconst REST_DAY')+'\n}','Course content changed');
assert.equal(span(html,'function applyDefaults(','/* Every key that holds progress'),span(before,'function applyDefaults(','/* Every key that holds progress'),'Stored data defaults/schema changed');
const days=Function('return ('+raw.slice('const DAY_TEACH = '.length)+')')();
const parts=key=>{const d=days[key];return !d?[]:Array.isArray(d)?[{sections:d}]:d.parts;};
const taught=[...new Set(Object.keys(days).map(k=>+k.split('.')[0]))].sort((a,b)=>a-b);
const original=[];
// Original ordinal fallback increments for every exercise, including explicit IDs.
for(const w of taught)for(let d=0;d<7;d++){
 let n=0;for(const part of parts(w+'.'+d))for(const s of part.sections||[])if(s.t==='ex'){original.push(s.practiceId||w+'.'+d+'.'+n);n++;}
}
const source=span(html,'function corePool(){','/* Practice filters,');
const pool=Function('corePoolCache','taughtWeeks','dayParts','dayTitleFor',source+'return corePool();')(null,()=>taught,parts,()=> 'Topic');
assert.deepEqual(pool.map(p=>p.id),original,'Existing solved practice identities changed');
assert(pool.every(p=>Number.isInteger(p.part)&&parts(p.week+'.'+(p.day-1))[p.part].sections.includes(p.ex)));
const promptSource=span(html,'function pythonSectionsPrompts(','function pythonPartPrompts(');
const prompts=Function(promptSource+'return pythonSectionsPrompts;')();
const sections=[{t:'key',v:'Learning objective: metadata'}];
for(let n=0;n<10;n++)sections.push({t:'new',v:'Concept'+n,note:'Explanation'+n});
sections.push({t:'code',v:'print(2 + 3)'},{t:'try',q:'Predict the output',code:'print(2 + 3)',a:'5',why:'Addition'},
 {t:'ex',v:'Write code that adds 4 and 5.'},{t:'sol',code:'print(4+5)',out:'9',why:'Add then print.'},
 {t:'mis',wrong:'print("a" + 1)',right:'print("a" + str(1))',why:'Convert deliberately.'},
 {t:'try',q:'What is this concept?',code:'# Predict and explain',a:'An answer'},
 {t:'checkpoint',lesson:{id:'fixture',quiz:[{q:'What is this concept?',options:['An answer','Wrong'],correct:0,why:'Reason'},
 {q:'Which result is correct?',options:['6','5'],correct:1,why:'Addition'}]}});
const result=prompts(sections,'Fixture');
assert(result.some(p=>p.kind==='exercise'&&p.answerCode==='print(4+5)'&&p.answerOut==='9'));
assert(result.some(p=>p.kind==='predict'&&p.code==='print(2 + 3)'));
assert(result.some(p=>p.kind==='debug'&&p.answerCode.includes('str(1)')));
assert(result.some(p=>p.options&&p.a==='5'));
assert.equal(result.filter(p=>p.q==='What is this concept?').length,1);
assert(!result.some(p=>p.q.includes('Learning objective')||p.code==='# Predict and explain'));
assert(result.length>8,'Useful prompts beyond the first introductory sections were lost');
for(const script of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(script[1]);
console.log('PASS: curriculum/default storage unchanged; '+pool.length+' stable exercise identities; complete meaningful prompt extraction, code/solutions, deduplication and valid JavaScript.');
