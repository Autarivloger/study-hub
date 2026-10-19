// Extend the existing roadmap and append teaching; retain all other content.
const fs=require('fs'),path=require('path'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),target=path.join(root,'study-hub.html');
const extension=require('./cybersecurity-next-roadmap.cjs');
const lessons=require('./cybersecurity-week9-content.cjs');
let html=fs.readFileSync(target,'utf8');
function region(marker,end){const a=html.indexOf(marker),b=html.indexOf(end,a+marker.length);if(a<0||b<0)throw Error('Missing data boundary');return {a:a+marker.length,b,data:JSON.parse(html.slice(a+marker.length,b))};}
const roadmap=region('const CYBERSECURITY_ROADMAP = ',';\nconst CYBERSECURITY_TEACH');
const teaching=region('const CYBERSECURITY_TEACH = ',';\nlet cyberPage');
if(roadmap.data.length!==8||teaching.data['9.1'])throw Error('Unexpected starting curriculum; refusing overwrite');
for(const lesson of Object.values(lessons)){
 for(let i=0;i<lesson.sections.length;i++){
  const section=lesson.sections[i];
  if(!['code','sol'].includes(section.t))continue;
  const result=cp.spawnSync(process.env.STUDY_HUB_PYTHON||'python',['-c',section.t==='code'?section.v:section.code],{
   cwd:path.join(root,'docs/cybersecurity-week9'),encoding:'utf8',timeout:20000,
   env:{...process.env,PYTHONDONTWRITEBYTECODE:'1',PYTHONUTF8:'1'}});
  if(result.status!==0||result.stderr.trim())throw Error('Snippet failed: '+(result.stderr||result.error));
  const output=result.stdout.replace(/\r\n/g,'\n').trimEnd();
  if(section.t==='sol')section.out=output;
  else {if(lesson.sections[i+1].t!=='out')throw Error('Output destination missing');lesson.sections[i+1].v=output;}
 }
}
const json=data=>JSON.stringify(data,null,2).replace(/<\//g,'<\\/');
// Replace later region first so the earlier offsets remain valid.
html=html.slice(0,teaching.a)+json({...teaching.data,...lessons})+html.slice(teaching.b);
html=html.slice(0,roadmap.a)+json([...roadmap.data,...extension])+html.slice(roadmap.b);
const changes=[
 ['2 months · 8 weeks · Start from scratch',"' + CYBERSECURITY_ROADMAP.length + ' weeks · Foundations → Defensive Python · Study at your own pace"],
 ["'<span class=\"wc-prog\">Day 1–Day 7</span></button>';","'<span class=\"wc-prog\">Day 1–Day 7 · ' + (CYBERSECURITY_TEACH[item.week+\".1\"] ? 'Lessons ready' : 'Roadmap') + '</span></button>';"],
 ["(lesson ? cyberLessonHtml(lesson,\"cyber:\"+week.week+\".\"+day.day) : '')", "(lesson ? cyberLessonHtml(lesson,\"cyber:\"+week.week+\".\"+day.day) : '<p class=\"ls-box ls-tip\">Roadmap only. This day lists the next learning goals; its full teaching lesson will be added later.</p>')"],
 ['position===55','position===CYBERSECURITY_ROADMAP.length*7-1'],
 ['position>=56','position>=CYBERSECURITY_ROADMAP.length*7']
];
for(const [old,next] of changes){if(html.split(old).length!==2)throw Error('Unexpected renderer source: '+old);html=html.replace(old,next);}
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/i.test(m[1])&&!/\bsrc=/.test(m[1]))new Function(m[2]);
const roadmapFile=path.join(__dirname,'cybersecurity-roadmap.json');
const source=JSON.parse(fs.readFileSync(roadmapFile,'utf8'));
if(JSON.stringify(source)!==JSON.stringify(roadmap.data))throw Error('Roadmap source mismatch');
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
fs.writeFileSync(roadmapFile+'.tmp',JSON.stringify([...source,...extension],null,2)+'\n','utf8');fs.renameSync(roadmapFile+'.tmp',roadmapFile);
// Save the actually executed outputs as authoring evidence, not browser state.
fs.writeFileSync(path.join(root,'docs/cybersecurity-week9/verified-outputs.json'),JSON.stringify(Object.fromEntries(Object.entries(lessons).map(([id,l])=>[id,l.sections.filter(x=>x.t==='code'||x.t==='sol').map(x=>({code:x.t==='code'?x.v:x.code,out:x.t==='sol'?x.out:l.sections[l.sections.indexOf(x)+1].v}))])),null,2)+'\n');
console.log('Added Week9–16 daily roadmap and Week9 teaching: 7 lessons,21 executed Python snippets,14 practice/challenges,52 explained self-checks.');
