const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict'),vm=require('vm');
const html=fs.readFileSync('study-hub.html','utf8'),old=cp.execFileSync('git',['show','22c63dd:study-hub.html'],{encoding:'utf8',maxBuffer:45e6});
function section(text,key){const a=text.indexOf('/* STUDY HUB '+key+' START */'),b=text.indexOf('/* STUDY HUB '+key+' END */',a);assert(a>=0&&b>a);return {a,b:b+('/* STUDY HUB '+key+' END */').length};}
function unrelated(text){for(const key of ['GAMES CSS','GAMES APP','CHESS APP']){const {a,b}=section(text,key);text=text.slice(0,a)+text.slice(b);}return text.replace(/\r\n/g,'\n');}
assert.equal(unrelated(html),unrelated(old),'Learning content, storage, game banks or unrelated source changed');
const read=p=>fs.readFileSync(p,'utf8').replace(/\r\n/g,'\n');
for(const file of ['scripts/games-app.js','scripts/games-focus.css','scripts/sudoku-app.js','scripts/sokoban-app.js','scripts/chess-app.js'])assert(html.includes(read(file)),file+' is not embedded exactly');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/application\/json/.test(m[1]))new vm.Script(m[2]);
console.log('PASS: self-contained Focus sources match; all course content, storage, data banks and unrelated app source unchanged; executable JavaScript parses.');
