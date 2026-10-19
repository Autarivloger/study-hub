// End-to-end checks in a disposable Chrome profile. No learner profile/storage is read.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const out=path.join(os.tmpdir(),'studyhub-webdev-weeks2-5');fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-webdev-w2-5-profile-')),fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync('study-hub.html','utf8').replace('\nboot();\n','window.__courseTestEval=expression=>eval(expression);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
const watchdog=setTimeout(()=>{console.error('Browser check timed out');browser.kill();process.exit(1);},180000);
async function main(){
 let port;for(let i=0;i<100;i++){const p=path.join(profile,'DevToolsActivePort');if(fs.existsSync(p)){port=Number(fs.readFileSync(p,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port);
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timed out: '+method));},20000);pending.set(id,{resolve:v=>{clearTimeout(timer);resolve(v);},reject:e=>{clearTimeout(timer);reject(e);}});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const shot=async name=>{await sleep(100);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));};
 await send('Runtime.enable');await send('Page.enable');
 for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('Boolean(window.__studyHubBooted)'),'Boot');
 // Disable networking before exercising the learning app: content and local saves must work.
 await send('Network.enable');await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 await evaluate('closeModal();DB=applyDefaults({course:{done:{"1.0":"2026-10-19"},notes:{"1.0":"Keep Python"}},japanese:{notes:{"31.1":"Keep Japanese"}},headNotes:{"cyber:9.1|day-notes":"Keep Cyber","webdev:1.1|day-notes":"Keep Week1"},lessonsDone:{"webdev:1.1":"2026-10-19"},lessonQuizScores:{"webdev:1.1":80}});save();switchView("webdev");closeModal()');
 assert(await evaluate('document.querySelectorAll(".cyber-phase [data-webdev-week]").length===156&&[...document.querySelectorAll(".cyber-phase [data-webdev-week]")].filter(b=>b.textContent.includes("Lessons ready")).length===5'),'Five authored weeks; full roadmap preserved');
 for(let w=2;w<=5;w++){
  await evaluate('webDevPage={mode:"overview",week:'+w+',day:1};renderWebDevelopment();document.querySelector(".cyber-phase [data-webdev-week=\\"'+w+'\\"]").click()');
  assert(await evaluate('document.querySelectorAll("[data-webdev-day]").length===7&&document.querySelector(".webdev-week-progress").textContent.includes("0 / 7")'),'Week grid '+w);
  for(let d=1;d<=7;d++){
   const id=w+'.'+d,key='webdev:'+id;
   await evaluate('document.querySelector("[data-webdev-day=\\"'+d+'\\"]").click()');
   assert(await evaluate('webDevPage.week==='+w+'&&webDevPage.day==='+d+'&&!!document.querySelector(".webdev-teaching")&&!document.querySelector(".webdev-roadmap-label")&&!DB.lessonsDone['+JSON.stringify(key)+']'),'Authored lesson, no auto-complete '+id);
   assert(await evaluate('[...document.querySelectorAll(".webdev-teaching .ls-code-tag")].every(t=>t.textContent!=="python")'),'Language labels '+id);
   await evaluate('(()=>{const b=document.getElementById("webDevelopmentBody");for(const t of b.querySelectorAll("[data-reveal]")){const a=b.querySelector("#tryA"+t.dataset.reveal);if(!a.hidden)throw Error("Early answer");t.click();if(a.hidden)throw Error("Missing answer");t.click();if(!a.hidden)throw Error("Hide failed");}for(const t of b.querySelectorAll("[data-sol]")){const a=b.querySelector("#solB"+t.dataset.sol);if(!a.hidden)throw Error("Early solution");t.click();if(a.hidden||!a.textContent.includes("How it works"))throw Error("Missing solution");t.click();}})()');
   await evaluate('WEBDEV_TEACH['+JSON.stringify(id)+'].quiz.forEach((q,i)=>document.querySelector(".webdev-teaching [data-lq=\\""+i+"\\"][data-lo=\\""+q.correct+"\\"]").click())');
   assert.equal(await evaluate('DB.lessonQuizScores['+JSON.stringify(key)+']'),100,'Quiz save '+id);
   const note='Week '+w+' Day '+d+' <b>literal note</b>';
   await evaluate('(()=>{const n=document.querySelector("#webdevDayNotes"),b=n.querySelector(".hn-box"),t=n.querySelector("textarea");if(b.hidden)throw Error("Hidden daily note");t.value='+JSON.stringify(note)+';t.dispatchEvent(new Event("input",{bubbles:true}));n.querySelector("[data-hn]").click();document.querySelector("[data-webdev-notes]").click();if(b.hidden||document.activeElement!==t)throw Error("Note jump");document.querySelector("[data-webdev-done]").click();})()');
   await sleep(550);
   assert(await evaluate('DB.headNotes['+JSON.stringify(key+'|day-notes')+']==='+JSON.stringify(note)+'&&!!DB.lessonsDone['+JSON.stringify(key)+']'),'Note and completion '+id);
   await evaluate('document.querySelector("[data-webdev-week]").click()');
  }
  assert(await evaluate('document.querySelector(".webdev-week-progress").textContent.includes("7 / 7")'),'Complete count '+w);
 }
 // Heading notes, undo, repeat quiz and best score.
 await evaluate('webDevPage={mode:"day",week:4,day:6};renderWebDevelopment();document.querySelector("[data-webdev-done]").click()');
 assert(await evaluate('!DB.lessonsDone["webdev:4.6"]&&document.querySelector("[data-webdev-done]").getAttribute("aria-pressed")==="false"'),'Undo');
 await evaluate('(()=>{const b=document.querySelector(".webdev-teaching .hn-head [data-hn]");b.click();const t=document.querySelector("#hnBox"+b.dataset.hnBox+" textarea");window.__headingKey=t.dataset.hnKey;t.value="<script>literal source note</script>";t.dispatchEvent(new Event("input",{bubbles:true}));})()');await sleep(550);
 await evaluate('renderWebDevelopment();document.querySelector("[data-webdev-done]").click();WEBDEV_TEACH["4.6"].quiz.forEach((q,i)=>document.querySelector("[data-lq=\\""+i+"\\"][data-lo=\\""+((q.correct+1)%3)+"\\"]").click())');
 assert(await evaluate('DB.lessonQuizScores["webdev:4.6"]===100&&DB.headNotes[window.__headingKey]==="<script>literal source note</script>"'),'Best score and safe literal note');
 for(let w=1;w<=5;w++){
  await evaluate('webDevPage={mode:"day",week:'+w+',day:7};renderWebDevelopment();document.querySelector("[data-webdev-step=\\"1\\"]").click()');
  assert(await evaluate('webDevPage.week==='+ (w+1)+'&&webDevPage.day===1&&Boolean(document.querySelector(".webdev-teaching"))==='+String(w<5)),'Next boundary '+w);
  await evaluate('document.querySelector("[data-webdev-step=\\"-1\\"]").click()');assert(await evaluate('webDevPage.week==='+w+'&&webDevPage.day===7'),'Previous boundary '+w);
 }
 for(const [width,height] of [[1480,900],[900,768],[768,1024],[375,812],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(let w=2;w<=5;w++)for(let d=0;d<=7;d++){
    await evaluate('webDevPage={mode:'+JSON.stringify(d?'day':'week')+',week:'+w+',day:'+(d||1)+'};renderWebDevelopment();window.scrollTo(0,0)');
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Overflow '+width+' '+theme+' '+w+'.'+d);
    if(d&&width<761)assert(await evaluate('[...document.querySelectorAll(".webdev-teaching .btn,.webdev-teaching .ls-quiz-opt")].every(b=>b.getBoundingClientRect().height>=44)'),'Touch targets');
   }
   if(width===1480||width===375){await evaluate('webDevPage={mode:"day",week:5,day:6};renderWebDevelopment();document.querySelector(".webdev-teaching").scrollIntoView({block:"start"})');await shot('article-lesson-'+width+'-'+theme);}
  }
 }
 // Use actual export and file-input import routes with synthetic records.
 await evaluate('window.__backupBlob=null;const original=URL.createObjectURL;URL.createObjectURL=b=>{window.__backupBlob=b;return original(b);};document.getElementById("exportBtn").click()');
 const backup=await evaluate('window.__backupBlob.text()');
 await evaluate('delete DB.lessonsDone["webdev:2.1"];delete DB.headNotes["webdev:2.1|day-notes"];save();(()=>{const f=new File(['+JSON.stringify(backup)+'],"test-backup.json",{type:"application/json"}),d=new DataTransfer();d.items.add(f);const i=document.getElementById("importFile");i.files=d.files;i.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<50&&!await evaluate('!!document.getElementById("impMerge")');i++)await sleep(80);
 await evaluate('document.getElementById("impMerge").click()');assert(await evaluate('!!DB.lessonsDone["webdev:2.1"]&&DB.headNotes["webdev:2.1|day-notes"].includes("Week 2")'),'Merge import');
 await evaluate('confirmMerge('+backup+');document.getElementById("impReplace").click()');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('Object.keys(WEBDEV_TEACH).filter(id=>Number(id.split(".")[0])>=2).every(id=>DB.lessonsDone["webdev:"+id]&&DB.lessonQuizScores["webdev:"+id]===100&&DB.headNotes["webdev:"+id+"|day-notes"].includes("Week "))'),'All 28 notes/progress/quizzes survive replace and reload offline');
 assert(await evaluate('DB.course.notes["1.0"]==="Keep Python"&&DB.japanese.notes["31.1"]==="Keep Japanese"&&DB.headNotes["cyber:9.1|day-notes"]==="Keep Cyber"&&DB.headNotes["webdev:1.1|day-notes"]==="Keep Week1"&&DB.lessonQuizScores["webdev:1.1"]===80'),'Prior course records preserved');
 // Open the actual complete HTML examples with network disabled.
 for(let w=2;w<=5;w++)for(const [name,source] of Object.entries(require('../scripts/web-development-week'+w+'-content.cjs').examples)){
  const url=pathToFileURL(path.resolve('docs/web-development-week'+w+'/examples/'+name+'.html')).href;
  await send('Page.navigate',{url});for(let i=0;i<100&&!await evaluate('location.href==='+JSON.stringify(url)+'&&document.readyState==="complete"');i++)await sleep(50);
  const result=await evaluate('({mode:document.compatMode,title:document.title,h1:document.querySelectorAll("h1").length,charset:document.characterSet,viewport:document.querySelector("meta[name=viewport]")?.content,text:document.body.textContent})');
  assert.equal(result.mode,'CSS1Compat','Standards mode: '+w+'/'+name);
  assert.equal(result.title,source.match(/<title>(.*?)<\/title>/)[1]);assert.equal(result.h1,1);assert.equal(result.charset,'UTF-8');assert(result.viewport.includes('width=device-width'));
  if(name==='reading')assert(await evaluate('document.querySelector("p[lang=ja]").textContent==="日本語を勉強しています。"'),'UTF-8 passage');
  if(name==='repaired')assert(await evaluate('document.querySelectorAll("p").length===2&&document.querySelector("#goal").title==="My learning goal"'),'Repaired document result');
  if(name==='comments')assert(!result.text.includes('Next session:'),'Comments are not body text');
  if(name==='lists')assert(await evaluate('document.querySelectorAll("ol > li").length===3&&!!document.querySelector("ul > li > ul")'),'Nested list within li');
  if(name==='article'){
   assert(await evaluate('document.querySelectorAll("main").length===1&&!!document.querySelector("main > article")&&document.querySelectorAll("main h2").length===2&&document.querySelectorAll("ol > li").length===3&&document.querySelectorAll("main ul > li").length===2'),'Article structure');
   for(const id of ['plan','review']){
    await evaluate('document.querySelector("a[href=\\"#'+id+'\\"]").focus()');
    await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
    assert.equal(await evaluate('location.hash'),'#'+id,'Keyboard fragment link');
   }
  }
 }
 assert.deepEqual(errors,[],'Browser console errors');
 console.log('PASS:28 lessons;199 exercise answers;192 quizzes; daily/heading notes, completion/undo, best scores, boundaries;5widths/both themes; actual backup merge+replace and offline reload; old records retained;8 complete examples rendered offline, semantic structure and keyboard links; zero console errors. Screenshots:',out);
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});
