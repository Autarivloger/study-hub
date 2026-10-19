const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const previous=cp.execFileSync('git',['show','b6ab9aa:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const html=fs.readFileSync('study-hub.html','utf8');
function region(source,start,end){const a=source.indexOf(start),b=source.indexOf(end,a+start.length);assert(a>=0&&b>a,start);return source.slice(a,b);}
function data(start,end){return JSON.parse(region(html,start,end).slice(start.length));}
const weeks=data('const WEBDEV_ROADMAP = ',';\n/* WEB DEVELOPMENT DATA END */');
const path=data('const WEBDEV_PATH = ',';\nconst WEBDEV_ROADMAP = ');
assert.deepEqual(weeks,JSON.parse(fs.readFileSync('scripts/web-development-roadmap.json','utf8')));
assert.deepEqual(path,JSON.parse(fs.readFileSync('scripts/web-development-path.json','utf8')));
assert.equal(weeks.length,156);assert.equal(new Set(weeks.map(w=>w.title)).size,156);
weeks.forEach((week,i)=>{
 assert.equal(week.week,i+1);assert(week.checkpoint.trim());
 assert.deepEqual(week.days.map(d=>d.day),[1,2,3,4,5,6,7]);
 for(const day of week.days){assert(day.focus.trim());assert(day.topics.length>=2&&day.topics.every(t=>typeof t==='string'&&t.trim()));}
 assert(week.days[6].topics.includes('Readiness check: '+week.checkpoint));
});
assert.equal(weeks.flatMap(w=>w.days).length,1092);
assert.equal(path.years.length,3);assert.equal(path.phases.length,39);
for(let i=0;i<3;i++){
 const year=path.years[i];assert.equal(year.start,i*52+1);assert.equal(year.end,(i+1)*52);
 const phases=path.phases.filter(p=>p.start>=year.start&&p.end<=year.end);assert.equal(phases.length,13);
 assert.deepEqual(phases.flatMap(p=>Array.from({length:p.end-p.start+1},(_,j)=>p.start+j)),Array.from({length:52},(_,j)=>year.start+j));
}
assert(weeks[0].title.includes('first web page'));assert(weeks[24].title.includes('JavaScript'));
assert(weeks[27].title.includes('Functions'));assert(weeks[56].title.includes('React'));
assert(weeks[71].days.some(d=>d.focus.includes('classes')),'Python OOP must appear before Django classes');
assert(path.references.every(r=>r.url.startsWith('https://')));
// The shared component must retain byte-identical Cybersecurity HTML.
const oldHelper=cp.execFileSync('git',['show','b6ab9aa:scripts/cybersecurity-three-year-navigation.js'],{encoding:'utf8'});
const shared=fs.readFileSync('scripts/roadmap-years.js','utf8');
const generic=new Function(shared+';return roadmapYearsHtml;\nfunction escapeHtml(v){return String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/\x27/g,"&#39;")}')();
const cyberPath=JSON.parse(fs.readFileSync('scripts/cybersecurity-path.json','utf8'));
const cyberWeeks=JSON.parse(fs.readFileSync('scripts/cybersecurity-roadmap.json','utf8'));
for(const selected of [1,52,53,104,105,156]){
 const expected=new Function('CYBERSECURITY_PATH','CYBERSECURITY_ROADMAP','cyberPage','CYBERSECURITY_TEACH',oldHelper+';return cyberRoadmapOverviewHtml();\nfunction escapeHtml(v){return String(v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/\x27/g,"&#39;")}')(cyberPath,cyberWeeks,{week:selected},{'1.1':{},'9.1':{}});
 assert.equal(generic(cyberPath,cyberWeeks,selected,'cyber',w=>[1,9].includes(w.week)),expected,'Cybersecurity component changed');
}
// Restore only the authorised navigation/presentation additions to verify scope.
let restored=html;
const css=fs.readFileSync('scripts/web-development.css','utf8');assert(restored.includes(css));restored=restored.replace(css+'\n','');
assert(restored.includes(shared));restored=restored.replace(shared+'\n','');
restored=restored.replace('\n'+region(restored,'/* WEB DEVELOPMENT DATA START */','\nboot();\n'),'');
const currentHelper=fs.readFileSync('scripts/cybersecurity-three-year-navigation.js','utf8');assert(restored.includes(currentHelper));restored=restored.replace(currentHelper,oldHelper);
const currentCss=fs.readFileSync('scripts/cybersecurity-three-year.css','utf8');assert(restored.includes(currentCss));restored=restored.replace(currentCss,cp.execFileSync('git',['show','b6ab9aa:scripts/cybersecurity-three-year.css'],{encoding:'utf8'}));
const replacements=[
 ['    <button type="button" class="nav-item" data-view="webdev"><span class="ic" aria-hidden="true">·</span>Web Development</button>\n',''],
 ['  <button type="button" data-view="webdev" aria-label="Web Development"><span class="ic" aria-hidden="true">·</span>Web Dev</button>\n',''],
 ['    <!-- WEB DEVELOPMENT ROADMAP -->\n    <div class="view" id="view-webdev"><div id="webDevelopmentBody"></div></div>\n\n',''],
 ['const views = ["webdev","games",','const views = ["games",'],
 ['course:"Python Course", webdev:"Web Development", lessons:','course:"Python Course", lessons:'],
 ['  if(name==="webdev") renderWebDevelopment();\n',''],
 ["    webdev:'M3 4h18v16H3z M3 8h18 M9 12l-3 3 3 3 M15 12l3 3-3 3',\n",'']
];
for(const [from,to] of replacements){assert.equal(restored.split(from).length,2,from);restored=restored.replace(from,to);}
if(restored!==previous){let i=0;while(restored[i]===previous[i]&&i<previous.length)i++;throw Error('Unexpected change at '+i+': '+JSON.stringify(restored.slice(i-40,i+90))+' versus '+JSON.stringify(previous.slice(i-40,i+90)));}
assert(html.includes(fs.readFileSync('scripts/web-development-view.js','utf8')));
assert(html.includes(fs.readFileSync('scripts/premium-shell.js','utf8')));
for(const script of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/.test(script[1])&&!/\bsrc=/.test(script[1]))new Function(script[2]);
console.log('PASS:156 sequential beginner weeks/1092 days/39 phases; checkpoints and project/review goals; scoped navigation/view only; old storage and curriculum preserved; shared Cybersecurity output identical; all JavaScript parses.');
