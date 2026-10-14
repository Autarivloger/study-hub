const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const before=cp.execFileSync('git',['show','c1cf3f0:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
const marker='const CYBERSECURITY_TEACH = ';
function split(s){const a=s.indexOf(marker),b=s.indexOf(';\nlet cyberPage',a);assert(a>=0&&b>a);return {prefix:s.slice(0,a+marker.length),data:JSON.parse(s.slice(a+marker.length,b)),suffix:s.slice(b)};}
const old=split(before),current=split(html),week=require('../scripts/cybersecurity-week7-content.cjs');
assert.equal(current.prefix,old.prefix,'Earlier website/app code changed');
assert.equal(current.suffix,old.suffix,'Renderer/storage/navigation or other courses changed');
for(const [id,lesson] of Object.entries(old.data))assert.deepEqual(current.data[id],lesson,'Existing lesson changed: '+id);
assert.deepEqual(Object.keys(current.data).filter(id=>!Object.hasOwn(old.data,id)),['7.1','7.2','7.3','7.4','7.5','7.6','7.7']);
assert.deepEqual(current.data,{...old.data,...week},'Inline content differs from authored source');
let questions=0;
for(const [id,l] of Object.entries(week)){
 assert(l.objective&&l.reflection);
 assert(l.sections.filter(s=>s.t==='h').length>=5,'Missing explanations '+id);
 assert(l.sections.every(s=>['h','p','new','key','tip'].includes(s.t)),'Unrequested coding section '+id);
 assert(!/[\u0900-\u097f]/.test(JSON.stringify(l)),'Non-English lesson '+id);
 assert(l.sections.map(s=>s.v+' '+(s.note||'')).join(' ').split(/\s+/).length>=500,'Thin lesson '+id);
 for(const s of l.sections)if(s.t==='new')assert(s.v&&s.note,'Missing first-use explanation '+id);
 assert(l.checks.length===(id==='7.7'?12:4));
 for(const c of l.checks){questions++;assert(c.q&&c.a&&c.why,'Missing answer/reason '+id);}
 assert(l.references.length>=2&&l.references.every(r=>r.title&&(r.url.startsWith('https://')||['docs/cybersecurity-week7/sample-events.json','docs/cybersecurity-week7/case-notes.txt','docs/cybersecurity-week7/digest-manifest.json'].includes(r.url))));
}
assert.equal(questions,36);
const text=JSON.stringify(week);
for(const phrase of ['SOC','SIEM','false positive','receipt','triage','Containment','SHA-256','A04','X01','Python'])assert(text.includes(phrase),'Missing topic '+phrase);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
const crypto=require('crypto'),path=require('path');
const folder='docs/cybersecurity-week7';
const sample=JSON.parse(fs.readFileSync(path.join(folder,'sample-events.json'),'utf8'));
assert.deepEqual(sample,require('../scripts/cybersecurity-week7-samples.cjs'),'Handout differs from prepared source');
assert.equal(sample.events.length,12);
assert.equal(new Set(sample.events.map(e=>e.record)).size,12);
const unique=new Map();
for(const e of sample.events){
 const id=e.source+'|'+e.event_id;
 if(unique.has(id)){
  const first=unique.get(id);assert.equal(first.record,'L03');assert.equal(e.record,'L04');
  for(const k of ['event_time','account','action','result','source_ip'])assert.equal(e[k],first[k],'Conflicting duplicate field '+k);
 }else unique.set(id,e);
}
assert.equal(unique.size,11);
const hasOffset=e=>/(Z|[+-]\d\d:\d\d)$/.test(e.event_time);
const known=[...unique.values()].filter(hasOffset).sort((a,b)=>Date.parse(a.event_time)-Date.parse(b.event_time));
assert.equal(known.length,10);
assert.deepEqual(known.map(e=>e.event_id),['A01','A02','A04','A03','A10','N01','P01','P02','E01','Z01']);
assert.deepEqual([...unique.values()].filter(e=>!hasOffset(e)).map(e=>e.event_id),['X01']);
assert.equal(Date.parse('2026-10-01T09:00:00+09:00'),Date.parse('2026-10-01T00:00:00Z'));
const failures=known.filter(e=>e.source==='auth'&&e.account==='maya'&&e.action==='login.failed'&&Date.parse(e.event_time)>=Date.parse('2026-10-01T00:00:00Z')&&Date.parse(e.event_time)<Date.parse('2026-10-01T00:03:00Z'));
assert.deepEqual(failures.map(e=>e.event_id),['A01','A02','A04','A03']);
const earlier=failures.filter(e=>Date.parse(e.received_time)<=Date.parse('2026-10-01T00:07:00Z'));
assert.deepEqual(earlier.map(e=>e.event_id),['A01','A02','A03']);
const alert=sample.events.find(e=>e.event_id==='Z01');assert.deepEqual(alert.observed_event_ids,earlier.map(e=>e.event_id));
assert(sample.events.filter(e=>e.source==='auth'&&e.action==='login.failed').length===5,'Raw failure-delivery count');
const denied=sample.events.find(e=>e.event_id==='P01'),saved=sample.events.find(e=>e.event_id==='P02');
assert(denied.status===403&&denied.write_performed===false&&denied.resource==='N2');
assert(saved.status===200&&saved.write_performed===true&&saved.resource==='N1');
const manifest=JSON.parse(fs.readFileSync(path.join(folder,'digest-manifest.json'),'utf8'));
assert.equal(manifest.algorithm,'SHA-256');
assert.deepEqual(manifest.files.map(f=>f.file),['sample-events.json','case-notes.txt']);
for(const f of manifest.files){
 const bytes=fs.readFileSync(path.join(folder,f.file));
 assert.equal(bytes.length,f.bytes);assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),f.sha256);
 assert.notEqual(crypto.createHash('sha256').update(Buffer.concat([bytes,Buffer.from(' ')] )).digest('hex'),f.sha256,'Byte change must alter reference comparison');
}
console.log('PASS: Week7 seven complete English lessons/36 reasoned checks; first-use terms, full review and primary references; prior42 lessons and all application/storage/course code unchanged; JS valid.');
console.log('PASS: exact handout bytes/digests;12 deliveries,11 unique events,10 ordered/1 unknown-time;4 unique failures vs3 at alert cutoff; refused/persisted sample results coherent.');
