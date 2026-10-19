const fs=require('fs'),assert=require('assert/strict');
let html=fs.readFileSync('study-hub.html','utf8');
const content=require('./gita-book-content.cjs');
const block='/* GITA BOOK DATA START */\nconst GITA_BOOK = '+JSON.stringify(content,null,2).replace(/<\//g,'<\\/')+';\n'+fs.readFileSync('scripts/gita-book.js','utf8')+'\n/* GITA BOOK DATA END */\n';
const re=/\/\* GITA BOOK DATA START \*\/[\s\S]*?\/\* GITA BOOK DATA END \*\/\n/;
if(re.test(html))html=html.replace(re,()=>block);else{assert(html.includes('const YOGA_COURSE = '));html=html.replace('const YOGA_COURSE = ',()=>block+'const YOGA_COURSE = ');}
const style=fs.readFileSync('scripts/gita-book.css','utf8');
const sr=/\/\* GITA BOOK STYLE START \*\/[\s\S]*?\/\* GITA BOOK STYLE END \*\/\n?/;
if(sr.test(html))html=html.replace(sr,()=>style);else html=html.replace('</style>',()=>style+'\n</style>');
let view=fs.readFileSync('scripts/yoga-view-english.txt','utf8');
if(!view.includes("yogaPage.mode==='book'")){
 view=view.replace("  const el=document.getElementById('lessonsBody');","  const el=document.getElementById('lessonsBody');\n  if(yogaPage.mode==='book' && typeof renderGitaBook==='function')return renderGitaBook(el);\n  if(typeof gitaBookLeave==='function')gitaBookLeave();");
 view=view.replace("yogaLink('Gita Reflection','gita')","yogaLink('Gita Reflection','gita')+(typeof GITA_BOOK==='object'?yogaLink('Book','book'):'')");
 view=view.replace("  if(yogaPage.mode==='home'){","  if(yogaPage.mode==='home'){\n    if(typeof gitaLibraryHtml==='function')html+=gitaLibraryHtml();");
 view=view.replace('  el.innerHTML=html;','  el.innerHTML=html;\n  if(typeof gitaSourceButtons===\'function\')gitaSourceButtons(el);');
 fs.writeFileSync('scripts/yoga-view-english.txt',view);
}
const va=html.indexOf('/* ================= YOGA & MEDITATION ================= */'),vb=html.indexOf('function renderLessons(){',va);assert(va>=0&&vb>va);
html=html.slice(0,va)+view+html.slice(vb);
if(!html.includes('/* GITA BOOK MERGE */')){
 const anchor='      if(key === "lessonQuizScores"){';assert(html.includes(anchor));
 html=html.replace(anchor,'      /* GITA BOOK MERGE */\n      if(key==="headNotes" && gitaIsRecordKey(k)){\n        DB.headNotes[k]=gitaMergeRecord(DB.headNotes[k],incoming.headNotes[k]);\n      }else '+anchor.trimStart());
}
if(!html.includes('/* GITA BOOK LEAVE */')){
 html=html.replace('function switchView(name){','function switchView(name){\n  /* GITA BOOK LEAVE */ if(name!=="lessons" && typeof gitaBookLeave==="function")gitaBookLeave();');
}
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
fs.writeFileSync('study-hub.html.tmp',html);
for(let i=0;;i++){try{fs.renameSync('study-hub.html.tmp','study-hub.html');break;}catch(e){if(i===10)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,200);}}
console.log('Added Gita Book, '+content.chapters.length+' chapter guides and '+content.daily.length+' original daily reflections; existing storage maps reused.');
