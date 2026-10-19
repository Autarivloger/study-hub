const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const original=cp.execFileSync('git',['show','8c7dea0:study-hub.html'],{encoding:'utf8',maxBuffer:50e6}),html=fs.readFileSync('study-hub.html','utf8');
const css=fs.readFileSync('scripts/compact-workspace.css','utf8'),js=fs.readFileSync('scripts/compact-workspace.js','utf8');
assert(html.includes(css));assert(html.includes(js));let restored=html.replace(css+'\n','').replace(js+'\n','');
function sidebar(s){const a=s.indexOf('  <div id="sidebar"'),b=s.indexOf('\n  <div id="content"',a);return s.slice(a,b);}
assert.equal((sidebar(html).match(/class="nav-label"/g)||[]).length,14,'All existing names retain their own label');
assert(sidebar(html).includes('id="sidebarNavigation"')&&sidebar(html).includes('id="sidebarToggle"'));
restored=restored.replace(sidebar(restored),sidebar(original));
assert(restored===original,'Unexpected change to study materials, navigation functions, storage, data or existing features');
assert(js.includes("const key='studyHubSidebarCompact'"));assert(!/\bDB\b|\bsave\(/.test(js),'Layout must not write learner data');
for(const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/.test(match[1])&&!/\bsrc=/.test(match[1]))new Function(match[2]);
console.log('PASS: presentation-only CSS/controller plus sidebar wrapper/labels/toggle; all existing course content, storage and behaviour byte-identical; separate UI preference; JavaScript valid.');
