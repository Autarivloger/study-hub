const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const before=cp.execFileSync('git',['show','c61419d:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
const marker='const CYBERSECURITY_TEACH = ';
function split(s){const a=s.indexOf(marker),b=s.indexOf(';\nlet cyberPage',a);assert(a>=0&&b>a);return {prefix:s.slice(0,a+marker.length),data:JSON.parse(s.slice(a+marker.length,b)),suffix:s.slice(b)};}
const old=split(before),current=split(html),week=require('../scripts/cybersecurity-week8-content.cjs');
assert.equal(current.prefix,old.prefix,'Earlier website/app code changed');
assert.equal(current.suffix,old.suffix,'Renderer/storage/navigation or other courses changed');
for(const [id,lesson] of Object.entries(old.data))assert.deepEqual(current.data[id],lesson,'Existing lesson changed: '+id);
assert.deepEqual(Object.keys(current.data).filter(id=>!Object.hasOwn(old.data,id)),['8.1','8.2','8.3','8.4','8.5','8.6','8.7']);
assert.deepEqual(current.data,{...old.data,...week},'Inline content differs from authored source');
let questions=0;
for(const [id,l] of Object.entries(week)){
 assert(l.objective&&l.reflection);
 assert(l.sections.filter(s=>s.t==='h').length>=5,'Missing explanations '+id);
 assert(l.sections.every(s=>['h','p','new','key','tip'].includes(s.t)),'Unrequested coding section '+id);
 assert(!/[\u0900-\u097f]/.test(JSON.stringify(l)),'Non-English lesson '+id);
 assert(l.sections.map(s=>s.v+' '+(s.note||'')).join(' ').split(/\s+/).length>=500,'Thin lesson '+id);
 for(const s of l.sections)if(s.t==='new')assert(s.v&&s.note,'Missing first-use explanation '+id);
 assert(l.checks.length===(id==='8.7'?20:4));
 for(const c of l.checks){questions++;assert(c.q&&c.a&&c.why,'Missing answer/reason '+id);}
 assert(l.references.length>=2&&l.references.every(r=>r.title&&(r.url.startsWith('https://')||['docs/cybersecurity-week5/request-lab.html','docs/cybersecurity-week7/sample-events.json','docs/cybersecurity-week7/case-notes.txt','docs/cybersecurity-week8/assessment-workbook.txt','docs/cybersecurity-week8/worked-example.txt'].includes(r.url))));
}
assert.equal(questions,44);
assert.equal(Object.keys(current.data).length,56,'Eight-week foundation incomplete');
for(let w=1;w<=8;w++)for(let d=1;d<=7;d++)assert(current.data[w+'.'+d],'Missing day '+w+'.'+d);
const allowedHandouts=['docs/cybersecurity-week5/request-lab.html','docs/cybersecurity-week7/sample-events.json','docs/cybersecurity-week7/case-notes.txt','docs/cybersecurity-week8/assessment-workbook.txt','docs/cybersecurity-week8/worked-example.txt'];
for(const lesson of Object.values(week))for(const r of lesson.references)if(r.url.startsWith('docs/'))assert(allowedHandouts.includes(r.url)&&fs.existsSync(r.url),'Broken local reference '+r.url);
for(const file of ['docs/cybersecurity-week5/request-lab.html','docs/cybersecurity-week7/sample-events.json','docs/cybersecurity-week7/case-notes.txt','docs/cybersecurity-week7/digest-manifest.json']){
 const original=cp.execFileSync('git',['show','c61419d:'+file],{maxBuffer:32e6});
 assert(fs.readFileSync(file).equals(original),'Earlier companion file changed: '+file);
}
const example=fs.readFileSync('docs/cybersecurity-week8/worked-example.txt','utf8');
assert(example.includes('Status: planned, not verified resolved.')&&example.includes('active build/restart not verified'),'Example invented verification');
const sample=JSON.parse(fs.readFileSync('docs/cybersecurity-week7/sample-events.json','utf8'));
assert.equal(sample.events.length,12);assert.equal(new Set(sample.events.map(e=>e.source+'|'+e.event_id)).size,11);
assert.equal([...new Map(sample.events.map(e=>[e.source+'|'+e.event_id,e])).values()].filter(e=>e.action==='login.failed').length,4);
const text=JSON.stringify(week);
for(const phrase of ['Govern','Identify','Protect','Detect','Respond','Recover','RPO','RTO','Python','scope','portfolio','readiness'])assert(text.includes(phrase),'Missing topic '+phrase);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: Week8 seven complete English lessons/44 reasoned checks; first-use terms, full review and primary references; prior49 lessons and all application/storage/course code unchanged; JS valid.');
console.log('PASS: all8 weeks/56 days; handout paths valid; earlier lab/log/digest bytes unchanged; worked example retains untested/unknown status and consistent prepared counts.');
