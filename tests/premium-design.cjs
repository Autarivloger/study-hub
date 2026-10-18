// The redesign may change presentation, not curriculum, storage or unrelated logic.
const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const current=fs.readFileSync('study-hub.html','utf8');
const baseline=cp.execFileSync('git',['show','588bed5:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
function between(text,start,end){const a=text.indexOf(start),b=text.indexOf(end,a);assert(a>=0&&b>a,start);return text.slice(a,b);}
let restored=current;
for(const [name,file] of [['THEME','scripts/premium-theme.css'],['SHELL','scripts/premium-shell.js']]){
 const start='/* STUDY HUB PREMIUM '+name+' START',end='/* STUDY HUB PREMIUM '+name+' END */';
 const a=restored.indexOf(start),b=restored.indexOf(end,a)+end.length;assert(a>=0&&b>a);
 assert.equal(restored.slice(a,b).trim(),fs.readFileSync(file,'utf8').trim(),'Embedded source drift');
 restored=restored.slice(0,a)+restored.slice(b+2);
}
restored=restored.replace('<meta name="theme-color" content="#22664e">','<meta name="theme-color" content="#33507c">');
const shell=between(restored,'<a class="skip-link"','<div id="content"');
restored=restored.replace(shell,between(baseline,'<div id="topbar">','<div id="content"'));
restored=restored.replace('<div id="content" role="main" tabindex="-1">','<div id="content">');
restored=restored.replace(between(restored,'function renderCourseOverview(){','function renderCourseWeek(){'),between(baseline,'function renderCourseOverview(){','function renderCourseWeek(){'));
for(const selector of ['#sidebar .nav-item','#tabnav button']){
 restored=restored.replace(`document.querySelectorAll("${selector}").forEach(b=>{const active=b.dataset.view===navigationName;b.classList.toggle("active",active);b.setAttribute("aria-current",active?"page":"false");});`,`document.querySelectorAll("${selector}").forEach(b=> b.classList.toggle("active", b.dataset.view===navigationName));`);
}
if(restored!==baseline){let i=0;while(restored[i]===baseline[i]&&i<baseline.length)i++;throw Error('Presentation scope mismatch at '+i+': '+JSON.stringify(restored.slice(i-50,i+100))+' expected '+JSON.stringify(baseline.slice(i-50,i+100)));}
for(const match of current.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/.test(match[1]))new Function(match[2]);
assert(!fs.readFileSync('scripts/premium-theme.css','utf8').includes('@import'),'No external styling dependency');
assert(!fs.readFileSync('scripts/premium-shell.js','utf8').includes('localStorage'),'Shell must not change learner storage');
console.log('PASS: every previous lesson, data structure, feature and unrelated function is byte-identical; presentation sources match the offline embed; JavaScript valid.');
