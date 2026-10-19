// A presentation refresh must never rewrite learning data or storage behaviour.
const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const before=cp.execFileSync('git',['show','028b072:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const html=fs.readFileSync('study-hub.html','utf8');let restored=html;
const css=fs.readFileSync('scripts/japanese-theme.css','utf8').trimEnd();
assert.equal(restored.split(css).length,2,'Offline theme differs from authoring source');
restored=restored.replace(css+'\n\n','');
for(const name of ['jpRenderHome','jpRenderWeek','renderJapanese']){
 const marker='function '+name+'(',a=restored.indexOf(marker),b=restored.indexOf('\nfunction ',a+1),oa=before.indexOf(marker),ob=before.indexOf('\nfunction ',oa+1);
 assert(a>=0&&b>a&&oa>=0&&ob>oa);
 restored=restored.slice(0,a)+before.slice(oa,ob)+restored.slice(b);
}
assert.equal(restored,before,'Content, lesson rendering, storage or unrelated app logic changed');
assert(!/@import|https?:|url\(/i.test(css),'No external theme assets');
assert(!/user-select\s*:\s*none|text-overflow\s*:\s*ellipsis|line-clamp/i.test(css),'Study text must remain readable/selectable');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/.test(m[1])&&!/\bsrc=/.test(m[1]))new Function(m[2]);
console.log('PASS: Japanese design source matches offline embed; all curriculum, lesson examples, quizzes, storage, backup/sync and unrelated code byte-identical; JavaScript valid.');
