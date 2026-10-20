const fs=require('fs'),assert=require('assert/strict');let html=fs.readFileSync('study-hub.html','utf8');
const js=fs.readFileSync('scripts/spelling.js','utf8'),css=fs.readFileSync('scripts/spelling.css','utf8');
const jr=/\/\* STUDY HUB SPELLING START[\s\S]*?\/\* STUDY HUB SPELLING END \*\/\n?/;
if(jr.test(html))html=html.replace(jr,()=>js);else{assert(html.includes('\nboot();\n'));html=html.replace('\nboot();\n',()=>js+'\nboot();\n');}
const cr=/\/\* STUDY HUB SPELLING STYLE START \*\/[\s\S]*?\/\* STUDY HUB SPELLING STYLE END \*\/\n?/;
if(cr.test(html))html=html.replace(cr,()=>css);else html=html.replace('</style>',()=>css+'\n</style>');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
fs.writeFileSync('study-hub.html.tmp',html);for(let i=0;;i++){try{fs.renameSync('study-hub.html.tmp','study-hub.html');break;}catch(e){if(i===10)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,200);}}
console.log('Added shared offline English spelling: suggestions only; existing editors and storage retained.');
