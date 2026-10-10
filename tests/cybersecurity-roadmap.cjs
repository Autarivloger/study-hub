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
weeks.forEach((week,index)=>{
 assert.deepEqual(week.topics,previous[index].topics,'Weekly topics changed');
 assert.deepEqual(week.python,previous[index].python,'Python roles changed');
 assert.deepEqual(week.days.map(d=>d.day),[1,2,3,4,5,6,7]);
 assert.deepEqual(week.days.slice(0,6).flatMap(d=>d.topics),week.topics,'Daily topics lost or duplicated');
 assert.deepEqual(week.days.flatMap(d=>d.python),week.python,'Python roles lost or duplicated');
 assert(week.days.every(d=>d.focus&&d.topics.length));
});
assert(!JSON.stringify(weeks).includes('Python exercise'));
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: 8 weeks × 7 days, all original topics/Python roles retained; existing teaching, quizzes and storage/sync unchanged; JS valid.');
