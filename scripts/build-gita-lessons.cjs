const fs=require('fs'),assert=require('assert/strict');
const counts=[47,72,43,42,29,47,30,28,34,42,55,20,34,27,20,24,28,78];
const text=JSON.parse(fs.readFileSync('books/gita-sanskrit.json','utf8'));
const chapters=require('./gita-lessons/chapters.cjs');
module.exports=chapters.map((ch,i)=>{
 assert.equal(ch.chapter,i+1);const rows=fs.readFileSync('scripts/gita-lessons/'+String(i+1).padStart(2,'0')+'.txt','utf8').trim().split(/\r?\n/);
 assert.equal(rows.length,counts[i],'English verse count: Chapter '+(i+1));
 for(let n=1;n<=counts[i];n++)assert.equal(ch.groups.filter(g=>g.from<=n&&g.to>=n).length,1,'Context coverage: '+(i+1)+'.'+n);
 const verses=rows.map((row,n)=>{
   const cells=row.split('|');assert.equal(cells.length,2,'Expected meaning|practice: '+(i+1)+'.'+(n+1));
   const [meaning,practice]=cells,source=text.filter(v=>v.chapter===i+1&&v.verse===n+1);assert.equal(source.length,1);
   assert(meaning.length>65&&practice.length>40,'Unfinished verse: '+(i+1)+'.'+(n+1));
   assert(/[\u0900-\u097f]/.test(source[0].sanskrit));
   return {verse:n+1,sanskrit:source[0].sanskrit,meaning,practice};
 });
 return {...ch,verses};
});
if(require.main===module)console.log('Verified '+module.exports.length+' chapters, '+module.exports.reduce((n,c)=>n+c.verses.length,0)+' individually authored English meanings/applications, '+module.exports.reduce((n,c)=>n+c.groups.length,0)+' passage guides.');
