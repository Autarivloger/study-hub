const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..');
const dataPath=path.join(__dirname,'cybersecurity-roadmap.json');
const weeks=JSON.parse(fs.readFileSync(dataPath,'utf8'));
if(weeks.some(w=>w.days))throw Error('Daily roadmap exists; refusing to duplicate.');
const focus=[
 ['What cybersecurity is','Assets and CIA','Threats, vulnerabilities and risk','Common cyber threats','How security works','Learning scope and lab','Review & rest'],
 ['Internet and local networks','Network addresses','DNS and DHCP','Protocols, ports and services','HTTPS and firewalls','Diagrams and sample traffic','Review & rest'],
 ['Windows/Linux and running software','Users and file permissions','Terminal basics','Logs and timestamps','Updates and a learning lab','Personal device security','Review & rest'],
 ['Identity and passwords','MFA, sessions and permissions','Phishing awareness','Encryption, hashing and encoding','Checksums and secure connections','Backups and sensitive data','Review & rest'],
 ['Web requests and login flow','Application boundaries and input','Access control','Injection awareness','Browser risks and OWASP overview','A local request journey','Review & rest'],
 ['Security baselines and updates','Vulnerabilities, prioritisation and exposure','Network and endpoint controls','Cloud accounts and responsibility','Repository security and backups','Findings and remediation','Review & rest'],
 ['Monitoring and security events','Normal behaviour and log sources','Time and event ordering','Incident triage','Recovery and evidence','A simulated incident','Review & rest'],
 ['Foundations and request flow','Personal security and control review','Connected logs','Learning-lab assessment','Recovery planning and portfolio','Next-stage readiness','Review & rest']
];
const groups=[[0,1],[2,3],[4],[5],[6,7],[8]];
const pythonDays=[[1,5],[1,5],[1,3],[3,5],[0,3],[0,5],[3,5],[3,5]];
weeks.forEach((week,index)=>{
 week.days=groups.map((indexes,day)=>({
  day:day+1,focus:focus[index][day],
  topics:indexes.map(i=>week.topics[i]),
  python:week.python.filter((topic,i)=>pythonDays[index][i]===day)
 }));
 week.days.push({day:7,focus:focus[index][6],
  topics:['Review Week '+week.week+' topics','Review this week’s terms and connections','Revisit topics that are still unclear'],
  python:[]});
});
const target=path.join(root,'study-hub.html');let html=fs.readFileSync(target,'utf8');
const start=html.indexOf('const CYBERSECURITY_ROADMAP = '),end=html.indexOf('document.getElementById("cyberBack").onclick = renderCybersecurityRoadmap;',start);
if(start<0||end<0)throw Error('Missing cybersecurity boundaries');
const block='const CYBERSECURITY_ROADMAP = '+JSON.stringify(weeks,null,2)+';\n'+
 fs.readFileSync(path.join(__dirname,'cybersecurity-course-view.txt'),'utf8')+'\n';
html=html.slice(0,start)+block+html.slice(end);
const oldStart=html.indexOf('/* Cybersecurity roadmap: existing theme colours. */');
const oldEnd=html.indexOf('</style>',oldStart);
if(oldStart<0||oldEnd<0)throw Error('Missing roadmap style boundary');
const css=[
'/* Cybersecurity roadmap: reuse Python week/day components. */',
'#cybersecurityBody{max-width:1100px;margin:0 auto;padding:18px 16px;}',
'.cyber-heading{margin-bottom:20px;}',
'.cyber-heading h1{font-size:25px;margin:0 0 6px;}',
'.cyber-subtitle{margin:0;color:var(--text-dim);font-size:14px;}',
'.cyber-python{background:var(--bg-soft);border-radius:10px;padding:14px 16px;margin-top:20px;}',
'.cyber-python h3,.cyber-day-topics h3{font-size:15px;margin:0 0 12px;}',
'.cyber-python h3{color:var(--accent);}',
'.cyber-day-topics{background:var(--bg-elev);border:1px solid var(--border);border-radius:var(--radius);padding:18px;}',
'.cyber-day-topics li,.cyber-python li{overflow-wrap:anywhere;}',
'.cyber-day-navigation{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-top:24px;}',
'.cyber-footer{display:flex;gap:16px;justify-content:space-between;align-items:center;flex-wrap:wrap;margin-top:24px;}',
'.cyber-references{color:var(--text-dim);font-size:13px;}',
'#cyberBack{margin-bottom:14px;}',
'@media(max-width:700px){.cyber-heading h1{font-size:22px;}}'
].join('\n')+'\n';
html=html.slice(0,oldStart)+css+html.slice(oldEnd);
for(const m of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
fs.writeFileSync(dataPath,JSON.stringify(weeks,null,2)+'\n','utf8');
console.log('Added Week → Day → topics navigation: 8 weeks × 7 days, all existing topics and Python roles retained.');
