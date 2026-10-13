const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const before=cp.execFileSync('git',['show','452ec98:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
const marker='const CYBERSECURITY_TEACH = ';
function split(s){const a=s.indexOf(marker),b=s.indexOf(';\nlet cyberPage',a);assert(a>=0&&b>a);return {prefix:s.slice(0,a+marker.length),data:JSON.parse(s.slice(a+marker.length,b)),suffix:s.slice(b)};}
const old=split(before),current=split(html),week=require('../scripts/cybersecurity-week4-content.cjs');
assert.equal(current.prefix,old.prefix,'Earlier website/app code changed');
assert.equal(current.suffix,old.suffix,'Renderer/storage/navigation or other courses changed');
for(const [id,lesson] of Object.entries(old.data))assert.deepEqual(current.data[id],lesson,'Existing lesson changed: '+id);
assert.deepEqual(Object.keys(current.data).filter(id=>!Object.hasOwn(old.data,id)),['4.1','4.2','4.3','4.4','4.5','4.6','4.7']);
assert.deepEqual(current.data,{...old.data,...week},'Inline content differs from authored source');
let questions=0;
for(const [id,l] of Object.entries(week)){
 assert(l.objective&&l.reflection);
 assert(l.sections.filter(s=>s.t==='h').length>=5,'Missing explanations '+id);
 assert(l.sections.every(s=>['h','p','new','key','tip'].includes(s.t)),'Unrequested coding section '+id);
 assert(!/[\u0900-\u097f]/.test(JSON.stringify(l)),'Non-English lesson '+id);
 assert(l.sections.map(s=>s.v+' '+(s.note||'')).join(' ').split(/\s+/).length>=500,'Thin lesson '+id);
 for(const s of l.sections)if(s.t==='new')assert(s.v&&s.note,'Missing first-use explanation '+id);
 assert(l.checks.length===(id==='4.7'?12:4));
 for(const c of l.checks){questions++;assert(c.q&&c.a&&c.why,'Missing answer/reason '+id);}
 assert(l.references.length>=2&&l.references.every(r=>r.title&&r.url.startsWith('https://')));
}
assert.equal(questions,36);
const text=JSON.stringify(week);
for(const phrase of ['independent','authorisation','recovery','revocation','Base64','Argon2id','SHA-256','HTTPS','localStorage','restore','Python'])assert(text.includes(phrase),'Missing topic '+phrase);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: Week4 seven complete English lessons/36 reasoned checks; first-use terms, full review and primary references; prior21 lessons and all application/storage/course code unchanged; JS valid.');
