const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8'),old=cp.execFileSync('git',['show','04e1f73:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const css=fs.readFileSync('scripts/learning-navigation.css','utf8').trimEnd(),js=fs.readFileSync('scripts/learning-navigation.js','utf8').trimEnd();
assert(html.includes(css)&&html.includes(js));
const normalize=s=>s.replace(/\r\n/g,'\n');
let restored=normalize(html).replace(css+'\n','').replace(js+'\n','');
const regions=[
 ['function renderCourseOverview(){','\nfunction renderCourseWeek(){'],
 ['function renderCourseWeek(){','\n/* ================= DAY TEACHING'],
 ['function jpRenderWeek(week){','\nfunction jpWeekReviewPractice'],
 ['function renderCybersecurityRoadmap(){','\ndocument.getElementById("cyberBack")'],
 ['function renderWebDevelopment(){','\n/* WEB DEVELOPMENT VIEW END */']
];
function region(source,start,end){const a=source.indexOf(start),b=source.indexOf(end,a);assert(a>=0&&b>a,start);return source.slice(a,b);}
for(const [start,end] of regions)restored=restored.replace(region(restored,start,end),region(normalize(old),start,end));
assert.equal(restored,normalize(old),'Unexpected change to course content, progress, notes, search, storage, import or other views');
assert(!/\bDB\b|\bsave\(/.test(js),'Disclosure preference must not write learning data');
assert(js.includes("'studyHubLearningGroups'"));
assert(html.includes('details class="phase-block learning-group"')&&html.includes('<summary class="phase-head"'),'Native accessible group controls');
const python=region(html,...regions[1]);assert(python.includes('lesson-day-grid')&&python.includes('data-day="6"')&&python.includes('data-toggle="6"'),'All Python days and completion actions retained');
for(const [start,end] of regions.slice(2))assert(region(html,start,end).includes('lesson-day-grid'),'Daily grid '+start);
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){
 if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);
}
assert.equal(fs.readFileSync('scripts/web-development-view.js','utf8').trim(),('let webDevPage={mode:\'overview\',week:1,day:1};\n'+region(normalize(html),...regions[4])).trim(),'Maintained view source matches embedded view');
console.log('PASS: compact day choices in four courses; native Python disclosures; separate device preference; all authored materials and every non-layout function preserved exactly; valid JavaScript/JSON.');
