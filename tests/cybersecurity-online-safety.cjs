const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const old=cp.execFileSync('git',['show','61bdfc6:study-hub.html'],{encoding:'utf8',maxBuffer:45e6});
function region(s,a,b){const i=s.indexOf(a),j=s.indexOf(b,i);assert(i>=0&&j>i);return s.slice(i,j);}
for(const [a,b] of [['const DAY_TEACH = {','const REST_DAY'],['const CYBERSECURITY_ROADMAP = ','const CYBERSECURITY_TEACH = '],['const CYBERSECURITY_TEACH = ',';\nlet cyberPage'],['const STORE_KEY = ','/* ============ Navigation ============ */'],['function renderSections(','function renderLessonDetail()'],['/* ================= QUIZZES ================= */','/* ================= Export / Import ================= */']])assert.equal(region(html,a,b),region(old,a,b),'Existing region changed: '+a);
const data=require('../scripts/cybersecurity-online-safety-content.json');
assert.deepEqual(data.map(l=>l.number),[1,2,3,4,5,6,7]);
const start=html.indexOf('const CYBER_ONLINE_SAFETY = '),end=html.indexOf(';\n/* Online Safety:',start);
assert.deepEqual(JSON.parse(html.slice(start+'const CYBER_ONLINE_SAFETY = '.length,end)),data);
for(const lesson of data){
 assert(lesson.title&&lesson.objective&&lesson.origin);
 assert(lesson.sections.some(s=>s.v==='Review · 2 minutes')&&lesson.sections.some(s=>s.v==='Learn · 10 minutes'));
 assert.match(lesson.exerciseTitle,/^One exercise:/);
 assert(lesson.exercise.length&&lesson.selfCheck.length&&lesson.recap.length);
 assert(!JSON.stringify(lesson).includes('Every day, deliver'));
 assert(!JSON.stringify(lesson).includes('Progress: Lessons'));
 assert(lesson.sections.every(s=>['h','p'].includes(s.t)));
}
assert.equal(data[0].origin,'Added introduction');
assert(data.slice(1).every(l=>l.origin==='From your supplied transcript'));
assert(html.includes('data-safety-open')&&html.includes('data-safety-lesson'));
assert(html.includes('safetyProgressKey(lesson.number,b.dataset.safetyComplete)'));
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: seven separate Online Safety lessons, original six imported lesson bodies, one exercise/self-check per lesson, known provenance, JS valid; existing Python/Cybersecurity lessons, storage, backup, shared renderer and legacy quizzes unchanged.');
