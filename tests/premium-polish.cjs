const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8'),css=fs.readFileSync('scripts/premium-polish.css','utf8').trimEnd();
const previous=cp.execFileSync('git',['show','e2d2aa6:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const normalize=s=>s.replace(/\r\n/g,'\n');
assert(html.includes(css),'Stylesheet must be inlined for single-file offline use');
assert.equal(normalize(html).replace(css+'\n',''),normalize(previous),'Changes outside the new presentation stylesheet');
assert(!/@import\b|url\(/.test(css),'No online font/assets or requests');
assert(!/display\s*:\s*none/.test(css),'Do not hide learning content');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){
 if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);
}
console.log('PASS: offline stylesheet embedded; every previous byte of HTML, lessons, JavaScript, navigation, progress, backup/import and storage preserved; no hidden study content or external dependencies; script/JSON syntax valid.');
