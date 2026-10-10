const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const before=cp.execFileSync('git',['show','ebace1a:study-hub.html'],{encoding:'utf8',maxBuffer:32e6});
function region(text,start,end){const i=text.indexOf(start);assert(i>=0);const j=text.indexOf(end,i);assert(j>i);return text.slice(i,j);}
assert.equal(region(html,'const DAY_TEACH = {','const REST_DAY'),region(before,'const DAY_TEACH = {','const REST_DAY'),'Python content changed');
assert.equal(region(html,'/* ================= QUIZZES ================= */','/* ================= Export / Import ================= */'),region(before,'/* ================= QUIZZES ================= */','/* ================= Export / Import ================= */'),'Legacy quiz functions changed');
assert.equal(region(html,'const ARRAY_KEYS = ','/* ============ Navigation ============ */'),region(before,'const ARRAY_KEYS = ','/* ============ Navigation ============ */'),'Storage/backup/sync changed');
const weeks=JSON.parse(fs.readFileSync('scripts/cybersecurity-roadmap.json','utf8'));
assert.deepEqual(weeks.map(w=>w.week),[1,2,3,4,5,6,7,8]);
assert(weeks.every(w=>w.topics.length===9&&w.python.length===2));
const previous=JSON.parse(cp.execFileSync('git',['show','b56c782:scripts/cybersecurity-roadmap.json'],{encoding:'utf8'}));
// Week 1 now teaches in English; this is the sole authorised topic translation.
previous[0].topics[0]='What cybersecurity is and what it protects';
weeks.forEach((week,index)=>{
 assert.deepEqual(week.topics,previous[index].topics,'Weekly topics changed');
 assert.deepEqual(week.python,previous[index].python,'Python roles changed');
 assert.deepEqual(week.days.map(d=>d.day),[1,2,3,4,5,6,7]);
 assert.deepEqual(week.days.slice(0,6).flatMap(d=>d.topics),week.topics,'Daily topics lost or duplicated');
 assert.deepEqual(week.days.flatMap(d=>d.python),week.python,'Python roles lost or duplicated');
 assert(week.days.every(d=>d.focus&&d.topics.length));
});
assert(!JSON.stringify(weeks).includes('Python exercise'));
const previousDays=JSON.parse(cp.execFileSync('git',['show','c3e1897:scripts/cybersecurity-roadmap.json'],{encoding:'utf8'}));
assert.deepEqual(weeks.slice(1),previousDays.slice(1),'Weeks 2–8 changed');
const lessons=require('../scripts/cybersecurity-week1-content.cjs');
assert.deepEqual(Object.keys(lessons),['1.1','1.2','1.3','1.4','1.5','1.6','1.7']);
for(const [id,lesson] of Object.entries(lessons)){
 assert(lesson.objective&&lesson.reflection,'Missing objective/reflection '+id);
 assert(lesson.sections.filter(s=>s.t==='h').length>=4,'Thin lesson '+id);
 assert(lesson.checks.length>=3&&lesson.checks.every(c=>c.q&&c.a&&c.why),'Missing reasoned checks '+id);
 assert(lesson.sections.every(s=>['h','p','new','key','tip'].includes(s.t)),'Unexpected code section '+id);
 assert(!/[\u0900-\u097f]/.test(JSON.stringify(lesson)),'Non-English lesson '+id);
 const text=lesson.sections.map(s=>s.v+' '+(s.note||'')).join(' ');
 assert(text.split(/\s+/).length>=450,'Insufficient explanation '+id);
}
const inline=html.slice(html.indexOf('const CYBERSECURITY_TEACH = ')+28,html.indexOf(';\nlet cyberPage'));
assert.deepEqual(JSON.parse(inline),lessons,'Published lesson data differs from source');
assert.equal(lessons['1.7'].checks.length,10,'Incomplete weekly review');
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: 7 English lessons/28 checks; Weeks 2–8 unchanged; existing Python teaching, quizzes and storage/sync unchanged; JS valid.');
