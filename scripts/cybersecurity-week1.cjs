const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),target=path.join(root,'study-hub.html');
const weeks=JSON.parse(fs.readFileSync(path.join(__dirname,'cybersecurity-roadmap.json'),'utf8'));
const lessons=require('./cybersecurity-week1-content.cjs');
weeks[0].topics[0]='What cybersecurity is and what it protects';
weeks[0].days[0].topics[0]=weeks[0].topics[0];
let html=fs.readFileSync(target,'utf8');
const start=html.indexOf('const CYBERSECURITY_ROADMAP = ');
const end=html.indexOf('document.getElementById("cyberBack").onclick = renderCybersecurityRoadmap;',start);
if(start<0||end<0)throw Error('Missing cybersecurity boundaries');
const block='const CYBERSECURITY_ROADMAP = '+JSON.stringify(weeks,null,2)+';\n'+
 'const CYBERSECURITY_TEACH = '+JSON.stringify(lessons,null,2)+';\n'+
 fs.readFileSync(path.join(__dirname,'cybersecurity-course-view.txt'),'utf8')+'\n';
html=html.slice(0,start)+block+html.slice(end);
if(!html.includes('/* Cybersecurity Week 1 teaching */')){
 const marker='.cyber-day-navigation{';
 const offset=html.indexOf(marker);if(offset<0)throw Error('Missing cybersecurity CSS');
 const css=[
  '/* Cybersecurity Week 1 teaching */',
  '.cyber-teaching{margin:24px 0;max-width:850px;overflow-wrap:anywhere;}',
  '.cyber-teaching>.ls-h{margin-top:32px;}',
  '.cyber-teaching>.ls-p{line-height:1.85;}',
  '.cyber-teaching>.ls-obj{margin-bottom:16px;}',
  '.cyber-check-number{display:block;color:var(--text-dim);font-size:12px;margin-bottom:8px;}',
  '.cyber-checks{margin-top:28px;}',
  '.cyber-check .ls-try-q,.cyber-check .ls-try-ans,.cyber-check .ls-try-why{white-space:pre-line;}',
  '.cyber-day-notes{max-width:850px;margin-top:24px;border:1px solid var(--border);border-radius:var(--radius);padding:16px;background:var(--bg-elev);}',
  '.cyber-day-notes textarea{min-height:180px;}',
  '.cyber-day-notes .hn-head{margin-top:8px;}'
 ].join('\n')+'\n';
 html=html.slice(0,offset)+css+html.slice(offset);
}
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
const dataPath=path.join(__dirname,'cybersecurity-roadmap.json');
fs.writeFileSync(dataPath+'.tmp',JSON.stringify(weeks,null,2)+'\n','utf8');fs.renameSync(dataPath+'.tmp',dataPath);
console.log('Added seven English cybersecurity lessons with '+Object.values(lessons).reduce((n,l)=>n+l.checks.length,0)+' self-checks and stable day notes.');
