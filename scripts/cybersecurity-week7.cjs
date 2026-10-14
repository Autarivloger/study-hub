// Add only this week's data; reuse the current renderer, notes and storage.
const fs=require('fs'),path=require('path');
const target=path.join(__dirname,'..','study-hub.html');
const html=fs.readFileSync(target,'utf8'),marker='const CYBERSECURITY_TEACH = ';
const start=html.indexOf(marker),end=html.indexOf(';\nlet cyberPage',start);
if(start<0||end<0)throw Error('Cybersecurity teaching boundaries missing');
const old=JSON.parse(html.slice(start+marker.length,end));
const addition=require('./cybersecurity-week7-content.cjs');
for(const [id,lesson] of Object.entries(addition)){
 if(!/^7\.[1-7]$/.test(id)||old[id])throw Error('Wrong or existing lesson: '+id);
 if(!lesson.objective||!lesson.reflection||!lesson.checks?.length)throw Error('Incomplete lesson: '+id);
}
const data={...old,...addition};
const replacement=JSON.stringify(data,null,2).replace(/<\//g,'<\\/');
const changed=html.slice(0,start+marker.length)+replacement+html.slice(end);
for(const m of changed.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
const crypto=require('crypto');
const sample=require('./cybersecurity-week7-samples.cjs');
const folder=path.join(__dirname,'..','docs','cybersecurity-week7');
const raw=JSON.stringify(sample,null,2)+'\n';
const notes=[sample.context.title,'','FICTIONAL CLASSROOM RECORDS ONLY',sample.context.scope,'',
 'Raw identity: source + event_id. Collector cutoff: 2026-10-01T00:08:30Z.',
 'Original delivery order follows. Read event time separately from receipt time.','',
 ...sample.events.map(e=>JSON.stringify(e)), '', 'CONTEXT / LIMITATIONS',
 ...sample.context.limitations.map(v=>'- '+v),'','EXERCISES (attempt before reading Day6 answers)',
 '1. Count deliveries, unique source events and unique auth failures in [00:00,00:03) UTC.',
 '2. Build an offset-aware UTC event order. Keep undocumented-time X01 unordered.',
 '3. Explain duplicate A03 and late A04, and compare alert versus final cutoff.',
 '4. State facts, two hypotheses, missing evidence and authorised next questions.',
 '5. Draft a handling record, a bounded report and recovery/verification criteria.',
 '6. Separate an application log claim from independently verified stored state.',
 'No actual containment or account change was performed. IPs are documentation placeholders.',
 'Reference digests check exact teaching-file bytes, not truth or forensic/legal sufficiency.',''].join('\n');
const files={'sample-events.json':raw,'case-notes.txt':notes};
const manifest={algorithm:'SHA-256',purpose:'Reference for exact bytes of this fictional teaching package, not a signed forensic record',
 files:Object.entries(files).map(([file,content])=>({file,bytes:Buffer.byteLength(content,'utf8'),sha256:crypto.createHash('sha256').update(content,'utf8').digest('hex')}))};
files['digest-manifest.json']=JSON.stringify(manifest,null,2)+'\n';
fs.mkdirSync(folder,{recursive:true});
for(const [name,content] of Object.entries(files)){const file=path.join(folder,name);fs.writeFileSync(file+'.tmp',content,'utf8');fs.renameSync(file+'.tmp',file);}
fs.writeFileSync(target+'.tmp',changed,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Added Week7:7 English lessons, '+Object.values(addition).reduce((n,l)=>n+l.checks.length,0)+' reasoned self-checks; previous content and existing functions preserved.');
