// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-premium-polish-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-design-profile-'));
const fixture=path.join(profile,'study-hub.html');
const source=before?require('child_process').execFileSync('git',['show','e2d2aa6:study-hub.html'],{encoding:'utf8',maxBuffer:50e6}):fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8');
fs.writeFileSync(fixture,source.replace('\nboot();\n','window.__courseTestEval=expression=>eval(expression);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const watchdog=setTimeout(()=>{console.error('Design check timed out');browser.kill();process.exit(1);},180000);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const p=path.join(profile,'DevToolsActivePort');if(fs.existsSync(p)){port=Number(fs.readFileSync(p,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome startup');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Browser command timed out: '+method));},20000);pending.set(id,{resolve:value=>{clearTimeout(timer);resolve(value);},reject:error=>{clearTimeout(timer);reject(error);}});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const shot=async name=>{await sleep(120);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));};
 await send('Runtime.enable');await send('Page.enable');
 for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('Boolean(window.__studyHubBooted)'),'Boot');

 await evaluate('closeModal();DB=applyDefaults({course:{startDate:"2026-10-01T00:00:00Z",done:{"1.0":"2026-10-18"},notes:{"19.0":"Keep Python notes"},partsDone:{"19.0.0":"2026-10-18"}},japanese:{done:{"1.1.te":"2026-10-18"},notes:{"30.1":"Keep Japanese notes"},quizScores:{"30.1":86}},headNotes:{"cyber:9.1|day-notes":"Keep cyber notes"}});save();closeModal()');
 async function page(name){
  const code={
   home:'courseView={mode:"overview",week:null,dayIdx:null};switchView("course");renderCourse()',
   week:'courseView={mode:"week",week:19,dayIdx:null};switchView("course");renderCourse()',
   python:'courseView={mode:"day",week:19,dayIdx:0,part:0};switchView("course");renderCourse()',
   japanese:'jpPage={mode:"home"};switchView("japanese");renderJapanese()',
   jpweek:'jpPage={mode:"week",week:30};switchView("japanese");renderJapanese()',
   jpquiz:'jpPage={mode:"lesson",week:30,lesson:"30.1"};jpFuriganaOn=true;switchView("japanese");renderJapanese()',
   jpreview:'jpPage={mode:"lesson",week:30,lesson:"30.7"};jpFuriganaOn=true;switchView("japanese");renderJapanese()',
   cyber:'cyberPage={mode:"day",week:9,day:1};switchView("quiz");renderCybersecurityRoadmap()',
   webdev:'webDevPage={mode:"overview",week:1,day:1};switchView("webdev");renderWebDevelopment()',
   webday:'webDevPage={mode:"day",week:1,day:1};switchView("webdev");renderWebDevelopment()'
  }[name]||'switchView('+JSON.stringify(name)+')';
  await evaluate('closeModal();'+code+';window.scrollTo(0,0)');
 }
 if(process.argv.includes('--audit')){
  await page('jpquiz');
  console.dir(await evaluate('(()=>{const p=[...document.querySelectorAll(".jp-panel")].find(x=>x.querySelector("h3")?.textContent.startsWith("Write and compare"));function style(e){const s=getComputedStyle(e),r=e.getBoundingClientRect();return {tag:e.tagName,class:e.className,height:r.height,font:s.fontFamily,size:s.fontSize,line:s.lineHeight,padding:s.padding,margin:s.margin,display:s.display}}return {body:style(document.body),heading:style(p.querySelector("h3")),panel:style(p),rows:[...p.querySelectorAll(".jp-example")].slice(0,3).map(e=>({row:style(e),q:style(e.querySelector("b")),details:style(e.querySelector("details")),summary:style(e.querySelector("summary"))}))};})()'),{depth:8});
  ws.close();return;
 }
 const measurements=[];
 for(const [width,height] of [[1480,900],[375,812]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const name of ['home','week','japanese','jpweek','jpquiz','jpreview','python','cyber','webdev','webday']){
    await page(name);
    if(name==='jpquiz'){
     const m=await evaluate('(()=>{const q=document.querySelector(".jp-q"),choices=[...q.querySelectorAll(".jp-choice")],p=[...document.querySelectorAll(".jp-panel")].find(x=>x.querySelector("h3")?.textContent.startsWith("Write and compare")),labels=choices.map(x=>x.getBoundingClientRect());return {questionHeight:q.getBoundingClientRect().height,choiceHeight:labels[0].height,choiceGap:labels[1].top-labels[0].bottom,practiceHeight:p.getBoundingClientRect().height,readingFont:parseFloat(getComputedStyle(document.querySelector(".jp-reading")).fontSize),kanjiFont:parseFloat(getComputedStyle(document.querySelector(".jp-study-item>b")).fontSize),practiceRows:p.querySelectorAll(".jp-example").length,quizRows:document.querySelectorAll(".jp-q").length};})()');
     measurements.push({width,theme,...m});
     await evaluate('document.querySelector(".jp-q").scrollIntoView({block:"start"});window.scrollBy(0,-190)');
    }
    if(name==='jpreview')await evaluate('document.querySelector(".jp-review-drill-grid").scrollIntoView({block:"start"});window.scrollBy(0,-190)');
    if((width===1480&&theme==='light')||((name==='home'||name==='jpquiz')&&theme==='dark'))await shot(name+'-'+width+'-'+theme);
   }
  }
 }
 fs.writeFileSync(path.join(out,'measurements.json'),JSON.stringify(measurements,null,2));
 if(before){console.log('Before spacing:',JSON.stringify(measurements));console.log('Screenshots:',out);ws.close();return;}

 const baselinePath=path.join(os.tmpdir(),'studyhub-premium-polish-before','measurements.json');
 assert(fs.existsSync(baselinePath),'Collect --before measurements first');
 const baseline=JSON.parse(fs.readFileSync(baselinePath,'utf8'));
 for(const m of measurements){
  const b=baseline.find(x=>x.width===m.width&&x.theme===m.theme);
  assert(m.questionHeight<b.questionHeight*.8,'Quiz question spacing not reduced '+JSON.stringify({m,b}));
  assert(m.choiceGap<=5,'Excess option gaps '+JSON.stringify(m));
  assert(m.practiceHeight<b.practiceHeight*.86,'Practice spacing not reduced '+JSON.stringify({m,b}));
  assert.equal(m.practiceRows,b.practiceRows,'Practice content removed');assert.equal(m.quizRows,14);
  assert(m.readingFont>=20&&m.kanjiFont>=20,'Kanji reading too small');
 }
 // All major views and lesson types fit phones/tablets/desktops in both themes.
 const pages=['home','week','python','japanese','jpweek','jpquiz','jpreview','cyber','webdev','webday','reviews','typing','timer','flashcards','todo','lessons','journal','wisdom','liked','games'];
 for(const [width,height] of [[1480,900],[1024,768],[768,1024],[375,812],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  await send('Emulation.setTouchEmulationEnabled',{enabled:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const name of pages){
    await page(name);
    const size=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth})');
    assert(size.width<=width+1&&size.scroll<=width+1,'Overflow '+name+' '+width+' '+theme+': '+JSON.stringify(size));
    if(name==='python')assert(await evaluate('parseFloat(getComputedStyle(document.querySelector(".ls-p")).fontSize)>=15'),'Python reading shrunk');
    if(name==='jpquiz'){
     assert(await evaluate('document.querySelectorAll(".jp-choice").length===42&&document.querySelectorAll("ruby rt").length>50'),'Questions/Furigana lost');
     if(width<761)assert(await evaluate('[...document.querySelectorAll(".jp-choice")].every(x=>x.getBoundingClientRect().height>=44)'),'Answer touch targets');
    }
   }
  }
 }
 // Selection, reveal answers, scoring and notes retain their original behavior.
 await page('jpquiz');
 assert(await evaluate('[...document.querySelectorAll(".jp-example details")].every(d=>!d.open)'),'Answers should start hidden');
 await evaluate('document.querySelector(".jp-example details summary").click()');assert(await evaluate('document.querySelector(".jp-example details").open'),'Reveal answer');
 await evaluate('const lesson=JP_LESSONS.find(l=>l.id==="30.1");lesson.quiz.forEach((q,i)=>document.querySelector("input[name=jpq"+i+"][value=\\""+q[2]+"\\"]").click());document.querySelector("[data-jp-quiz]").click()');
 assert.equal(await evaluate('DB.japanese.quizScores["30.1"]'),100,'Quiz score');
 await evaluate('document.getElementById("jpNotes").value="Notes after compact styling";document.getElementById("jpNotes").dispatchEvent(new Event("input",{bubbles:true}))');
 assert(await evaluate('getComputedStyle(document.querySelector(".jp-reading")).userSelect!=="none"'),'Reading text cannot be copied');
 assert(await evaluate('DB.course.notes["19.0"]==="Keep Python notes"&&DB.course.partsDone["19.0.0"]&&DB.headNotes["cyber:9.1|day-notes"]==="Keep cyber notes"'),'Existing data');
 assert.deepEqual(errors,[],'Browser console errors');
 console.log('PASS: reduced quiz/practice spacing with all questions retained; readable Kanji/Furigana/Python; 20 screens at 5 widths in both themes; native answer selection/reveal, quiz scoring and notes; no JavaScript errors. Spacing:',JSON.stringify(measurements));
 console.log('Screenshots:',out);ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

