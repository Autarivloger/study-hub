const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const original=cp.execFileSync('git',['show','7f0b7da:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
function region(source,start,end){const a=source.indexOf(start),b=source.indexOf(end,a+start.length);assert(a>=0&&b>a,start);return source.slice(a,b);}
function data(source,start,end){return JSON.parse(region(source,start,end).slice(start.length));}
const marker='const CYBERSECURITY_ROADMAP = ',boundary=';\nconst CYBERSECURITY_TEACH';
const roadmap=data(html,marker,boundary),before=data(original,marker,boundary);
assert.equal(roadmap.length,156);assert.deepEqual(roadmap.slice(0,16),before,'Existing16 weeks changed');
assert.deepEqual(roadmap,JSON.parse(fs.readFileSync('scripts/cybersecurity-roadmap.json','utf8')),'Authoring data differs');
assert.equal(new Set(roadmap.map(w=>w.title)).size,156,'Duplicate week titles');
let days=0;
roadmap.forEach((week,index)=>{
 assert.equal(week.week,index+1);assert.deepEqual(week.days.map(d=>d.day),[1,2,3,4,5,6,7]);
 for(const day of week.days){
  assert(day.focus.trim());assert(Array.isArray(day.topics)&&day.topics.length);
  assert(day.topics.every(x=>typeof x==='string'&&x.trim()));assert(Array.isArray(day.python));days++;
 }
 if(week.week>16){
  assert(week.days.slice(0,6).every(day=>day.topics.length>=2));
  assert(week.days[5].python.length===1);assert(week.days[6].focus.includes('Review'));
  assert(week.days[6].topics.some(topic=>topic.includes(week.days[0].focus)));
 }
});
assert.equal(days,1092);
const path=data(html,'const CYBERSECURITY_PATH = ',';\nfunction cyberRoadmapOverviewHtml');
assert.deepEqual(path,JSON.parse(fs.readFileSync('scripts/cybersecurity-path.json','utf8')));
assert.equal(path.years.length,3);assert.equal(path.phases.length,39);
for(let index=0;index<3;index++){
 const year=path.years[index];assert.equal(year.year,index+1);assert.equal(year.start,index*52+1);assert.equal(year.end,(index+1)*52);
 const phases=path.phases.filter(p=>p.start>=year.start&&p.end<=year.end);assert.equal(phases.length,13);
 assert.deepEqual(phases.flatMap(p=>Array.from({length:p.end-p.start+1},(_,i)=>p.start+i)),Array.from({length:52},(_,i)=>year.start+i));
}
assert(path.references.every(r=>r.url.startsWith('https://')));
// Undo only the scoped additions and the one renderer to prove the rest is untouched.
let restored=html;
const css=fs.readFileSync('scripts/cybersecurity-three-year.css','utf8');assert(html.includes(css));restored=restored.replace(css+'\n','');
const navigation=fs.readFileSync('scripts/cybersecurity-three-year-navigation.js','utf8');assert(html.includes(navigation));
restored=restored.replace(region(restored,'/* CYBERSECURITY THREE YEAR PATH START */','function renderCybersecurityRoadmap(){'),'');
restored=restored.replace(region(restored,marker,boundary),region(original,marker,boundary));
const render='function renderCybersecurityRoadmap(){',end='document.getElementById("cyberBack").onclick';
restored=restored.replace(region(restored,render,end),region(original,render,end));
assert.equal(restored,original,'Unexpected changes to teaching, storage, notes, themes, backup/import or other features');
for(const block of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))
 if(!/type=["']application\/json/.test(block[1])&&!/\bsrc=/.test(block[1]))new Function(block[2]);
console.log('PASS:156 sequential weeks/1092 days,3 years/39 phases; original16 weeks and all teaching intact; complete day topics and Python support; only roadmap data, scoped CSS/helpers and one renderer changed; JavaScript valid.');
