const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),target=path.join(root,'study-hub.html');
let html=fs.readFileSync(target,'utf8');
if(html.includes('const CYBERSECURITY_ROADMAP = '))throw Error('Roadmap exists; refusing to duplicate it.');
const weeks=JSON.parse(fs.readFileSync(path.join(__dirname,'cybersecurity-roadmap.json'),'utf8'));
if(weeks.length!==8||weeks.some((w,i)=>w.week!==i+1||!w.topics.length||!w.python.length))throw Error('Invalid roadmap.');
function replace(old,value){if(!html.includes(old))throw Error('Missing source: '+old.slice(0,90));html=html.replace(old,value);}
replace('<button type="button" data-view="quiz"><span class="ic">❓</span>Quiz</button>',
 '<button type="button" data-view="quiz"><span class="ic">🛡️</span>Cybersecurity</button>');
replace('<button type="button" class="nav-item" data-view="quiz"><span class="ic">❓</span>Quizzes</button>',
 '<button type="button" class="nav-item" data-view="quiz"><span class="ic">🛡️</span>Cybersecurity</button>');
replace('quiz:"Quizzes"', 'quiz:"Cybersecurity"');
replace('if(name==="quiz") renderQuizList();', 'if(name==="quiz") renderCybersecurityRoadmap();');
replace('<!-- QUIZ VIEW -->', '<!-- CYBERSECURITY ROADMAP / RETAINED QUIZ DATA -->');
replace('<div class="view" id="view-quiz">\n      <div class="split" id="quizSplit">',
 '<div class="view" id="view-quiz">\n      <div id="cybersecurityBody"></div>\n      <div id="legacyQuizArea" hidden>\n        <button type="button" class="btn secondary btn-sm" id="cyberBack">← Cybersecurity roadmap</button>\n      <div class="split" id="quizSplit">');
replace('id="quizDetail"></div>\n      </div>\n    </div>',
 'id="quizDetail"></div>\n      </div>\n      </div>\n    </div>');
const code='const CYBERSECURITY_ROADMAP = '+JSON.stringify(weeks,null,2)+';\n'+
 fs.readFileSync(path.join(__dirname,'cybersecurity-view.txt'),'utf8')+
 '\ndocument.getElementById("cyberBack").onclick = renderCybersecurityRoadmap;\n\n';
replace('/* ================= QUIZZES ================= */',code+'/* ================= QUIZZES ================= */');
const css=[
'/* Cybersecurity roadmap: existing theme colours. */',
'#cybersecurityBody{max-width:1100px;margin:0 auto;padding:18px 16px;}',
'.cyber-heading{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:20px;}',
'.cyber-heading h1{font-size:25px;margin:0 0 6px;}',
'.cyber-subtitle{margin:0;color:var(--text-dim);font-size:14px;}',
'.cyber-week{background:var(--bg-elev);border:1px solid var(--border);border-radius:var(--radius);margin:0 0 12px;overflow:hidden;}',
'.cyber-week summary{cursor:pointer;padding:17px 18px;font-size:16px;font-weight:700;line-height:1.5;}',
'.cyber-week-number{color:var(--accent);display:inline-block;margin-right:14px;}',
'.cyber-week-content{display:grid;grid-template-columns:minmax(0,2fr) minmax(0,1fr);gap:24px;padding:0 20px 20px;}',
'.cyber-week h2{font-size:13px;color:var(--text-dim);margin:4px 0 12px;}',
'.cyber-week ul{margin:0;padding-left:20px;}',
'.cyber-week li{font-size:15px;line-height:1.65;margin:0 0 9px;overflow-wrap:anywhere;}',
'.cyber-python{background:var(--bg-soft);border-radius:10px;padding:14px 16px;align-self:start;}',
'.cyber-python h2{color:var(--accent);}',
'.cyber-footer{display:flex;gap:16px;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-top:22px;}',
'.cyber-references{color:var(--text-dim);font-size:13px;}',
'#cyberBack{margin-bottom:14px;}',
'@media(max-width:700px){.cyber-week-content{grid-template-columns:minmax(0,1fr);gap:12px;padding:0 15px 15px;}.cyber-week summary{padding:15px;}.cyber-heading h1{font-size:22px;}}'
].join('\n');
replace('</style>',css+'\n</style>');
for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(match[1]);
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Added 8-week cybersecurity roadmap; old quizzes and storage retained.');
