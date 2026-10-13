// Add only this week's data; reuse the current renderer, notes and storage.
const fs=require('fs'),path=require('path');
const target=path.join(__dirname,'..','study-hub.html');
const html=fs.readFileSync(target,'utf8'),marker='const CYBERSECURITY_TEACH = ';
const start=html.indexOf(marker),end=html.indexOf(';\nlet cyberPage',start);
if(start<0||end<0)throw Error('Cybersecurity teaching boundaries missing');
const old=JSON.parse(html.slice(start+marker.length,end));
const addition=require('./cybersecurity-week5-content.cjs');
for(const [id,lesson] of Object.entries(addition)){
 if(!/^5\.[1-7]$/.test(id)||old[id])throw Error('Wrong or existing lesson: '+id);
 if(!lesson.objective||!lesson.reflection||!lesson.checks?.length)throw Error('Incomplete lesson: '+id);
}
const data={...old,...addition};
const replacement=JSON.stringify(data,null,2).replace(/<\//g,'<\\/');
const changed=html.slice(0,start+marker.length)+replacement+html.slice(end);
for(const m of changed.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync(target+'.tmp',changed,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Added Week5:7 English lessons, '+Object.values(addition).reduce((n,l)=>n+l.checks.length,0)+' reasoned self-checks; previous content and existing functions preserved.');
