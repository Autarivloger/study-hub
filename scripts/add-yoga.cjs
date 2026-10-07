const fs=require('fs');
let html=fs.readFileSync('study-hub.html','utf8').replace(/\r\n/g,'\n');
if(html.includes('const YOGA_COURSE = '))throw Error('Yoga already exists; refuse duplicate authoring');
function replace(old,value){if(!html.includes(old))throw Error('Missing expected code: '+old.slice(0,70));html=html.replace(old,value);}
html=html.replace(/(<button[^>]+data-view="lessons"[^>]*><span class="ic">)[\s\S]*?(<\/span>)Lessons(<\/button>)/g,'$1🧘$2Yoga &amp; Meditation$3');
replace('<h1>Lessons</h1>','<h1>Yoga &amp; Meditation</h1>');
replace('id="lessonsHomeBtn">All lessons','id="lessonsHomeBtn">Practice home');
replace('lessons:"Lessons"','lessons:"Yoga & Meditation"');
replace('Object.keys(DB.lessonsDone||{}).forEach(function(k){const id=reviewId("python","lesson",k);','Object.keys(DB.lessonsDone||{}).forEach(function(k){if(!LEGACY_PYTHON_LESSONS.some(function(l){return l.id===k;}))return;const id=reviewId("python","lesson",k);');
const data=require('./yoga-english-content.cjs');
replace('function renderLessons(){','const YOGA_COURSE = '+JSON.stringify(data,null,2)+';\n\n'+fs.readFileSync('scripts/yoga-view-english.txt','utf8')+'function renderLessons(){');
const empty='  const empty=document.getElementById("lessonsBody");empty.innerHTML=';
const start=html.indexOf(empty),end=html.indexOf('\n',start);
if(start<0||end<0)throw Error('Legacy empty state missing');
html=html.slice(0,start)+'  return renderYoga();'+html.slice(end);
replace('  activeLessonId = null; renderLessons();\n});','  activeLessonId = null; yogaPage.mode="home"; yogaPage.id=null; renderLessons();\n});');
replace('/* Lessons */','/* Yoga uses the existing Lessons view identifier for legacy links. */');
const css=`\n/* Yoga & Meditation: use the app theme and existing controls. */
.yoga-wrap{max-width:920px;margin:0 auto;line-height:1.75}
.yoga-wrap .card{background:var(--bg-elev);border:1px solid var(--border);border-radius:var(--radius);box-shadow:var(--shadow);padding:20px;margin-bottom:18px}
.yoga-wrap h2,.yoga-wrap h3{line-height:1.4;overflow-wrap:anywhere}
.yoga-wrap .yoga-intro{border-top:3px solid var(--accent);margin-bottom:18px}
.yoga-wrap .yoga-compact{padding:6px 16px}
.yoga-compact>h2,.yoga-compact>p{display:none}
.yoga-eyebrow{font-size:.8rem;font-weight:700;letter-spacing:.04em;color:var(--accent)}
.yoga-actions{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:14px 0}
.yoga-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:18px 0}
.yoga-card{text-align:left;cursor:pointer;width:100%;color:inherit;font:inherit}
.yoga-card:hover{border-color:var(--accent)}
.yoga-guide{border:1px solid var(--border);border-radius:12px;padding:14px;margin:12px 0;background:var(--bg-elev)}
.yoga-guide summary{cursor:pointer;font-weight:700;line-height:1.6}
.yoga-guide summary span,.yoga-muted{font-size:.85rem;color:var(--text-dim)}
.yoga-guide summary span{display:block;font-weight:400}
.yoga-guide li,.yoga-practice li{padding:5px 0}
.yoga-practice{margin:18px 0}.yoga-stages{padding-left:24px}.yoga-stages li{padding:8px 0}
.yoga-wrap a{overflow-wrap:anywhere}.yoga-wrap .ls-key{padding:12px;border-radius:8px}
#yogaPracticeNotes .hn-btn{width:auto;min-width:90px;padding:0 10px;white-space:nowrap;font-size:12px}
#yogaPracticeNotes .hn-text{min-height:150px}
#yogaPracticeNotes{scroll-margin-top:150px}
#yogaPracticeNotes .hn-btn{width:auto;min-width:90px;padding:0 10px;white-space:nowrap;font-size:12px}
#yogaPracticeNotes .hn-text{min-height:150px}
#yogaPracticeNotes{scroll-margin-top:150px}
@media(max-width:600px){.yoga-grid{grid-template-columns:1fr}.yoga-guide{padding:12px}.yoga-wrap ol{padding-left:22px}.yoga-actions .btn{white-space:normal}}
`;
replace('</style>',css+'\n</style>');
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync('study-hub.html.tmp',html,'utf8');fs.renameSync('study-hub.html.tmp','study-hub.html');
console.log('Yoga added: 7 sessions,10 pose guides,5 meditation/breath guides,4 Gita reflections; existing storage maps reused.');
