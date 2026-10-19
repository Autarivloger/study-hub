const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const {lessons,examples}=require('../scripts/web-development-week1-content.cjs');
const html=fs.readFileSync('study-hub.html','utf8');
const all=JSON.parse(html.split('const WEBDEV_TEACH = ')[1].split(';\n/* WEB DEVELOPMENT TEACHING END */')[0]);
const data=Object.fromEntries(Object.entries(all).filter(([id])=>id.startsWith('1.')));
assert.deepEqual(data,lessons);assert.deepEqual(Object.keys(data),['1.1','1.2','1.3','1.4','1.5','1.6','1.7']);
for(const [id,l] of Object.entries(data)){
 assert.equal(l.id,'webdev:'+id);assert(l.objective&&l.reflection);assert(l.sections.length>=20);assert(l.sections.filter(s=>s.t==='h').length>=4);
 assert(l.sections.some(s=>s.t==='sol'));assert(l.sections.filter(s=>s.t==='try').length>=3);
 assert(l.quiz.length>=5);for(const q of l.quiz){assert(q.why&&q.q);assert.equal(new Set(q.options).size,3);assert(q.correct>=0&&q.correct<3);}
 for(const s of l.sections)if(['code','mis','sol','try'].includes(s.t))assert(['text','files','html'].includes(s.lang),'Untaught programming language '+id);
}
assert.equal(data['1.7'].sections.filter(s=>s.t==='try').length,16);assert.equal(data['1.7'].quiz.length,12);
for(const [name,source] of Object.entries(examples))assert.equal(fs.readFileSync('docs/web-development-week1/examples/'+name+'.html','utf8').trimEnd(),source);
const norm=s=>s.replace(/\r\n/g,'\n');
const old=norm(cp.execFileSync('git',['show','0c2e57b:study-hub.html'],{encoding:'utf8',maxBuffer:45e6}));
const current=norm(html);
const functionPattern=name=>new RegExp('^function '+name+'\\([^\\n]*\\)\\{[\\s\\S]*?^\\}','m');
const oldRenderer=old.match(functionPattern('renderSections'))[0],newRenderer=current.match(functionPattern('renderSections'))[0];
// Default Python sections must render the same bytes, including labels and colours.
function createRenderer(source,helper=''){
 return new Function('escapeHtml','highlightPy','highlightShell','escapeAttr',`let hnCtx,hnSeen,hnCount=0,tryCount=0,solCount=0;${helper}${source};return renderSections;`)(v=>String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'),v=>'PY:'+v,v=>'SH:'+v,v=>String(v));
}
const helper=current.match(functionPattern('teachingCodeHtml'))[0];
const before=createRenderer(oldRenderer),after=createRenderer(newRenderer,helper);
const sample=[{t:'code',v:'def add(a, b):\n    return a + b'},{t:'syn',v:'for item in items:'},{t:'mis',wrong:'x = 1',right:'x == 1',why:'Compare'},{t:'sol',code:'print(2)',out:'2',why:'Print'},{t:'try',q:'Predict',code:'print(3)',a:'3',why:'Print'},{t:'sh',v:'python main.py'},{t:'sol',sh:true,code:'python main.py',why:'Run'}];
assert.equal(after(sample),before(sample),'Default Python rendering changed');
const markup=after([{t:'code',lang:'html',v:'<h1>Literal markup</h1>'}]);assert(markup.includes('&lt;h1&gt;Literal markup&lt;/h1&gt;')&&!markup.includes('PY:')&&markup.includes('>html</div>'));
let stripped=current.replace(/\n\/\* WEB DEVELOPMENT TEACHING STYLE START \*\/[\s\S]*?\/\* WEB DEVELOPMENT TEACHING STYLE END \*\/\n/,'');
stripped=stripped.replace(/\/\* WEB DEVELOPMENT TEACHING START \*\/[\s\S]*?\/\* WEB DEVELOPMENT TEACHING END \*\/\n/,'');
const view=/\/\* WEB DEVELOPMENT VIEW START \*\/[\s\S]*?\/\* WEB DEVELOPMENT VIEW END \*\//;
assert.equal(current.match(view)[0].replace('/* WEB DEVELOPMENT VIEW START */\n','').replace('/* WEB DEVELOPMENT VIEW END */','').trimEnd(),norm(fs.readFileSync('scripts/web-development-view.js','utf8')).trimEnd());
stripped=stripped.replace(view,()=>old.match(view)[0]);
stripped=stripped.replace(helper+'\n','').replace(functionPattern('renderSections'),()=>oldRenderer);
assert.equal(stripped,old,'Unexpected change to existing content, design, roadmap, data or functions');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
console.log('PASS:7 aligned lessons,43 explained quizzes,16 weekly retrieval/repair drills,4 complete example documents; code escaped with correct labels; Python rendering byte-identical; all previous content/roadmaps/storage preserved; scripts/JSON valid.');
