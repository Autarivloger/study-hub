const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const original=cp.execFileSync('git',['show','050aa40:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const html=fs.readFileSync('study-hub.html','utf8');let restored=html;
for(const name of ['css','js']){
 const added=fs.readFileSync('scripts/floating-back.'+name,'utf8');
 assert(html.includes(added),'Offline embedded source matches '+name);
 restored=restored.replace(added+'\n','');
}
assert.equal(restored,original,'Existing application, study materials and storage must remain identical');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))
 if(!/type=["']application\/json/.test(m[1])&&!/\bsrc=/.test(m[1]))new Function(m[2]);
console.log('PASS: existing HTML/content/navigation/storage byte-identical after removing two additions; all JavaScript parses.');
