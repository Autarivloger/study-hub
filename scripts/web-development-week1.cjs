const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..'),file=path.join(root,'study-hub.html');
const {lessons,examples}=require('./web-development-week1-content.cjs');
let html=fs.readFileSync(file,'utf8');
const json=x=>JSON.stringify(x,null,2).replace(/<\//g,'<\\/');
function atomic(target,value){fs.writeFileSync(target+'.tmp',value,'utf8');for(let i=0;;i++){try{fs.renameSync(target+'.tmp',target);break;}catch(e){if(i>=12)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,200);}}}
const start='/* WEB DEVELOPMENT TEACHING START */',end='/* WEB DEVELOPMENT TEACHING END */';
// Revising Week 1 must retain teaching authored for every other week.
const oldBlock=html.match(/const WEBDEV_TEACH = ([\s\S]*?);\n\/\* WEB DEVELOPMENT TEACHING END \*\//);
const existing=oldBlock?JSON.parse(oldBlock[1]):{};
const block=start+'\nconst WEBDEV_TEACH = '+json({...existing,...lessons})+';\n'+end+'\n';
if(html.includes(start)){
 assert(process.argv.includes('--update'),'Week 1 already exists. Use --update to revise it.');
 const a=html.indexOf(start),b=html.indexOf(end,a)+end.length;assert(b>a);html=html.slice(0,a)+block.trimEnd()+html.slice(b);
}else{
 const anchor='/* WEB DEVELOPMENT VIEW START */';assert(html.includes(anchor));html=html.replace(anchor,()=>block+anchor);
}
const vs='/* WEB DEVELOPMENT VIEW START */',ve='/* WEB DEVELOPMENT VIEW END */';
const a=html.indexOf(vs),b=html.indexOf(ve,a);assert(a>=0&&b>a);
html=html.slice(0,a+vs.length)+'\n'+fs.readFileSync(path.join(root,'scripts/web-development-view.js'),'utf8').trimEnd()+'\n'+html.slice(b);
// Only opt-in language sections change. Existing Python sections retain the same markup/highlighter.
const helper='function teachingCodeHtml(value,language){\n  return language && language!=="python" ? escapeHtml(value) : highlightPy(value);\n}\n';
if(!html.includes('function teachingCodeHtml(')){
 const ra=html.indexOf('function renderSections(sections, ctx){'),rb=html.indexOf('\nfunction renderLessonDetail(){',ra);assert(ra>=0&&rb>ra);
 let renderer=html.slice(ra,rb).replaceAll('highlightPy(s.v)','teachingCodeHtml(s.v,s.lang)').replaceAll('highlightPy(s.wrong)','teachingCodeHtml(s.wrong,s.lang)').replaceAll('highlightPy(s.right)','teachingCodeHtml(s.right,s.lang)').replaceAll('highlightPy(s.code)','teachingCodeHtml(s.code,s.lang)');
 const old='<div class="ls-code-tag">python</div>',next='<div class="ls-code-tag">${escapeHtml(s.lang || "python")}</div>';assert(renderer.includes(old));renderer=renderer.replace(old,next);
 html=html.slice(0,ra)+helper+renderer+html.slice(rb);
}
const css=`\n/* WEB DEVELOPMENT TEACHING STYLE START */
#webDevelopmentBody:has(.webdev-teaching){max-width:1040px;}
.webdev-teaching{margin-top:22px;min-width:0;}
.webdev-teaching .ls-code,.webdev-teaching .ls-out{min-width:0;max-width:100%;}
.webdev-teaching pre{overflow-x:auto;max-width:100%;}
.webdev-completion{display:flex;align-items:center;flex-wrap:wrap;gap:12px;margin:20px 0;}
.webdev-completion span{max-width:60ch;color:var(--text-dim);font-size:12px;line-height:1.6;}
.webdev-week-progress{color:var(--accent);font-weight:600;}
@media(max-width:760px){#webDevelopmentBody .webdev-teaching .btn,#webDevelopmentBody .webdev-teaching .ls-quiz-opt,#webDevelopmentBody .webdev-completion .btn{min-height:44px;}}
/* WEB DEVELOPMENT TEACHING STYLE END */\n`;
if(!html.includes('/* WEB DEVELOPMENT TEACHING STYLE START */'))html=html.replace('</style>',()=>css+'</style>');
for(const [id,l] of Object.entries(lessons)){assert.equal(l.id,'webdev:'+id);assert(l.sections.length>=20);assert(l.quiz.length>=5);}
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
atomic(file,html);
const dir=path.join(root,'docs/web-development-week1/examples');fs.mkdirSync(dir,{recursive:true});
for(const [name,value] of Object.entries(examples))atomic(path.join(dir,name+'.html'),value+'\n');
console.log('Added Web Development Week 1: 7 complete lessons, '+Object.values(lessons).reduce((n,l)=>n+l.quiz.length,0)+' explained quiz questions; shared sections, notes, quiz and storage maps reused.');
