const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict'),vm=require('vm');
const current=fs.readFileSync('study-hub.html','utf8'),old=cp.execFileSync('git',['show','b9cca81:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const expected=old.replace('</style>',()=>fs.readFileSync('scripts/spelling.css','utf8')+'\n</style>').replace('\nboot();\n',()=>fs.readFileSync('scripts/spelling.js','utf8')+'\nboot();\n');assert.equal(current,expected,'Only shared spelling additions may change the application');
const oldSw=cp.execFileSync('git',['show','b9cca81:sw.js'],{encoding:'utf8'});assert.equal(fs.readFileSync('sw.js','utf8'),oldSw.replace('  "./study-hub.html",','  "./study-hub.html",\n  "./vendor/spelling/english-v1.js",'),'Precache dictionary without changing existing cache or strategies');
const sandbox={window:{}};vm.runInNewContext(fs.readFileSync('vendor/spelling/english-v1.js','utf8'),sandbox);let message;
const worker={self:{postMessage:m=>message=m}};vm.runInNewContext(sandbox.window.STUDY_HUB_SPELLING_SOURCE,worker);assert(message.ready&&message.words.length>100000);
for(const [word,expected] of [['speling','spelling'],['recieve','receive'],['langauge','language'],['becuase','because'],['definately','definitely'],['Recieve','Receive']]){worker.self.onmessage({data:{id:1,word}});assert(!message.correct&&message.suggestions.includes(expected),'Missing suggestion for '+word);}
for(const word of ['learning','Learning','studying','children',"don't"]){worker.self.onmessage({data:{id:2,word}});assert(message.correct,'Correct word rejected: '+word);}
for(const m of current.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
console.log('PASS:exact preservation outside spelling blocks;unchanged cache strategy plus offline asset;123k+ dictionary forms;real spelling/case/inflection checks;all JS/JSON valid.');
