const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..'),file=path.join(root,'study-hub.html');
function atomic(target,value){fs.writeFileSync(target+'.tmp',value,'utf8');for(let i=0;;i++){try{fs.renameSync(target+'.tmp',target);break;}catch(e){if(i>=12)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,200);}}}
const weeks=process.argv.slice(2).map(Number);assert(weeks.length&&weeks.every(w=>w>=2&&w<=5),'Specify weeks 2 through 5 to add.');
let html=fs.readFileSync(file,'utf8');
const pattern=/const WEBDEV_TEACH = ([\s\S]*?);\n\/\* WEB DEVELOPMENT TEACHING END \*\//;
const match=html.match(pattern);assert(match,'Existing teaching map required.');const data=JSON.parse(match[1]);
for(const week of weeks){
 const {lessons,examples={}}=require('./web-development-week'+week+'-content.cjs');
 assert.equal(Object.keys(lessons).length,7);
 for(let day=1;day<=7;day++){const id=week+'.'+day,l=lessons[id];assert.equal(l.id,'webdev:'+id);assert(l.sections.length>=25&&l.quiz.length>=6);data[id]=l;}
 const dir=path.join(root,'docs/web-development-week'+week+'/examples');fs.mkdirSync(dir,{recursive:true});
 for(const [name,value] of Object.entries(examples))atomic(path.join(dir,name+'.html'),value+'\n');
}
html=html.replace(pattern,()=> 'const WEBDEV_TEACH = '+JSON.stringify(data,null,2).replace(/<\//g,'<\\/')+';\n/* WEB DEVELOPMENT TEACHING END */');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
atomic(file,html);console.log('Added weeks '+weeks.join(', ')+'. Existing lesson IDs and all storage functions preserved.');
