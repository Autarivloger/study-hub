// Add the folder without rewriting the existing weeks, storage or shared renderer.
const fs=require('fs'),assert=require('assert/strict');
const path=require('path'),root=path.resolve(__dirname,'..'),target=path.join(root,'study-hub.html');
let html=fs.readFileSync(target,'utf8');
assert(!html.includes('const CYBER_ONLINE_SAFETY = '),'Online Safety already exists');
const lessons=JSON.parse(fs.readFileSync(path.join(__dirname,'cybersecurity-online-safety-content.json'),'utf8'));
const view=fs.readFileSync(path.join(__dirname,'cybersecurity-online-safety-view.txt'),'utf8');
const marker='function renderCybersecurityRoadmap(){';
assert(html.includes(marker));
html=html.replace(marker,'const CYBER_ONLINE_SAFETY = '+JSON.stringify(lessons,null,2).replace(/<\//g,'<\\/')+';\n'+view+'\n'+marker);
const route='  body.hidden = false;\n  let week = CYBERSECURITY_ROADMAP';
assert(html.includes(route));
html=html.replace(route,'  body.hidden = false;\n  if(cyberPage.mode==="safety-folder" || cyberPage.mode==="safety-lesson"){renderCyberSafety(body);return;}\n  let week = CYBERSECURITY_ROADMAP');
const overview="      '<div class=\"section-label\">Choose a week</div><div class=\"week-grid\">' +";
assert(html.includes(overview));
html=html.replace(overview,"      '<div class=\"section-label\">Your lesson folders</div><button type=\"button\" class=\"safety-folder-card\" data-safety-open><span class=\"dr-title\">📁 Online Safety</span><span class=\"dr-meta\">Lesson 1–7 · Accounts, passwords, MFA, passkeys, phishing and updates →</span></button>' +\n"+overview);
const binding='  function update(){ renderCybersecurityRoadmap(); body.scrollIntoView({block:"start"}); }';
assert(html.includes(binding));
html=html.replace(binding,binding+'\n  const safetyFolder=body.querySelector("[data-safety-open]");\n  if(safetyFolder)safetyFolder.onclick=function(){cyberPage.mode="safety-folder";update();};');
html=html.replace('</style>',`.safety-folder-card{display:flex;flex-direction:column;gap:8px;text-align:left;width:100%;padding:20px;margin:0 0 24px;border:1px solid var(--border);border-radius:var(--radius);background:var(--bg-elev);color:var(--text);font:inherit;cursor:pointer;overflow-wrap:anywhere}
.safety-folder-card:hover{border-color:var(--accent)}
.safety-folder-card:focus-visible,.safety-self-check summary:focus-visible{outline:2px solid var(--accent);outline-offset:3px}
.safety-teaching h1,.safety-teaching h2{overflow-wrap:anywhere}
.safety-exercise,.safety-self-check{padding:18px;border:1px solid var(--border);border-radius:var(--radius);margin:24px 0;background:var(--bg-elev)}
.safety-self-check summary{cursor:pointer;font-weight:700;line-height:1.6}
.safety-progress button{flex:1;white-space:normal}
.safety-references{margin-top:28px;overflow-wrap:anywhere}
</style>`);
const temporary=target+'.tmp';fs.writeFileSync(temporary,html);fs.renameSync(temporary,target);
console.log('Added Cybersecurity > Online Safety > seven separate lessons; existing maps/components reused.');
