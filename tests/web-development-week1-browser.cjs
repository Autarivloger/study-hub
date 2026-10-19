// Fresh synthetic profile only. Never reads the learner's browser storage.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const {lessons,examples}=require('../scripts/web-development-week1-content.cjs');
const out=path.join(os.tmpdir(),'studyhub-webdev-week1');fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-webdev-profile-')),fixture=path.join(profile,'study-hub.html');
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
 await evaluate('closeModal();DB=applyDefaults({course:{done:{"1.0":"2026-10-19"},notes:{"1.0":"Keep Python note"}},japanese:{done:{"31.1":"2026-10-20"},notes:{"31.1":"Keep Japanese note"}},lessonsDone:{"old-session":"2026-10-19"},lessonQuizScores:{"old-quiz":75},headNotes:{legacy:"Keep heading note","cyber:9.1|day-notes":"Keep Cyber note"}});save();switchView("webdev");closeModal()');
 assert(await evaluate('document.querySelectorAll(".cyber-phase [data-webdev-week]").length===156&&[...document.querySelectorAll(".cyber-phase [data-webdev-week]")].filter(b=>b.textContent.includes("Lessons ready")).length===new Set(Object.keys(WEBDEV_TEACH).map(id=>id.split(".")[0])).size'),'Roadmap and authored readiness intact');
 await evaluate('document.querySelector(".webdev-start [data-webdev-week]").click()');
 assert(await evaluate('document.querySelectorAll("[data-webdev-day]").length===7&&document.querySelector(".webdev-week-progress").textContent.includes("0 / 7")'),'Week grid and progress');
 for(let day=1;day<=7;day++){
  await evaluate('document.querySelector("[data-webdev-day=\\"'+day+'\\"]").click()');
  assert(await evaluate('webDevPage.day==='+day+'&&!!document.querySelector(".webdev-teaching")&&!document.querySelector(".webdev-roadmap-label")'),'Lesson '+day);
  assert(await evaluate('!DB.lessonsDone["webdev:1.'+day+'"]'),'Opening must not complete '+day);
  assert(await evaluate('[...document.querySelectorAll(".webdev-teaching .ls-code-tag")].every(t=>t.textContent!=="python")'),'Correct code labels '+day);
  await evaluate('(()=>{const body=document.getElementById("webDevelopmentBody");for(const b of body.querySelectorAll("[data-reveal]")){const a=body.querySelector("#tryA"+b.dataset.reveal);if(!a.hidden)throw Error("Premature answer");b.click();if(a.hidden)throw Error("No answer");b.click();if(!a.hidden)throw Error("No hide");}for(const b of body.querySelectorAll("[data-sol]")){const a=body.querySelector("#solB"+b.dataset.sol);if(!a.hidden)throw Error("Premature solution");b.click();if(a.hidden||!a.textContent.includes("How it works"))throw Error("Solution missing");b.click();}})()');
  await evaluate('WEBDEV_TEACH["1.'+day+'"].quiz.forEach((q,i)=>document.querySelector(".webdev-teaching [data-lq=\\""+i+"\\"][data-lo=\\""+q.correct+"\\"]").click())');
  assert.equal(await evaluate('DB.lessonQuizScores["webdev:1.'+day+'"]'),100,'Quiz save '+day);
  await evaluate('(()=>{const n=document.querySelector("#webdevDayNotes"),b=n.querySelector(".hn-box"),t=n.querySelector("textarea");if(b.hidden)throw Error("Hidden daily note");t.value="Web Week1 Day'+day+' <b>literal note</b>";t.dispatchEvent(new Event("input",{bubbles:true}));n.querySelector("[data-hn]").click();document.querySelector("[data-webdev-notes]").click();if(b.hidden||document.activeElement!==t)throw Error("Note jump/focus");document.querySelector("[data-webdev-done]").click();})()');
  await sleep(550);
  assert(await evaluate('DB.headNotes["webdev:1.'+day+'|day-notes"]==="Web Week1 Day'+day+' <b>literal note</b>"&&!!DB.lessonsDone["webdev:1.'+day+'"]'),'Notes and completion '+day);
  await evaluate('document.querySelector("[data-webdev-week]").click()');
 }
 assert(await evaluate('document.querySelector(".webdev-week-progress").textContent.includes("7 / 7")'),'Weekly progress');
 await evaluate('document.querySelector("[data-webdev-day=\\"4\\"]").click();document.querySelector("[data-webdev-done]").click()');
 assert(await evaluate('!DB.lessonsDone["webdev:1.4"]&&document.querySelector("[data-webdev-done]").getAttribute("aria-pressed")==="false"'),'Undo completion');
 // Heading-specific notes use a separate stable key and literal text escaping.
 await evaluate('(()=>{const h=document.querySelector(".webdev-teaching .hn-head [data-hn]");h.click();const box=document.querySelector("#hnBox"+h.dataset.hnBox),t=box.querySelector("textarea");window.__webHeadingKey=t.dataset.hnKey;t.value="Remember UTF-8 <script>literal</script>";t.dispatchEvent(new Event("input",{bubbles:true}));})()');await sleep(550);
 await evaluate('renderWebDevelopment();document.querySelector("[data-webdev-done]").click();WEBDEV_TEACH["1.4"].quiz.forEach((q,i)=>document.querySelector(".webdev-teaching [data-lq=\\""+i+"\\"][data-lo=\\""+((q.correct+1)%3)+"\\"]").click())');
 assert.equal(await evaluate('DB.lessonQuizScores["webdev:1.4"]'),100,'Best score not lowered');
 assert(await evaluate('DB.headNotes[window.__webHeadingKey]==="Remember UTF-8 <script>literal</script>"&&[...document.querySelectorAll(".webdev-teaching textarea")].some(t=>t.value.includes("<script>literal</script>"))'),'Heading note literal round trip');
 await evaluate('webDevPage={mode:"day",week:1,day:1};renderWebDevelopment()');assert(await evaluate('document.querySelector("[data-webdev-step=\\"-1\\"]").disabled'),'First boundary');
 await evaluate('webDevPage={mode:"day",week:1,day:7};renderWebDevelopment();document.querySelector("[data-webdev-step=\\"1\\"]").click()');assert(await evaluate('webDevPage.week===2&&webDevPage.day===1&&Boolean(document.querySelector(".webdev-teaching"))===Boolean(WEBDEV_TEACH["2.1"])'),'Next week readiness');
 await evaluate('document.querySelector("[data-webdev-step=\\"-1\\"]").click()');assert(await evaluate('webDevPage.week===1&&webDevPage.day===7&&!!document.querySelector(".webdev-teaching")'),'Return to authored week');
 for(const [width,height] of [[1480,900],[900,768],[768,1024],[375,812],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(let day=0;day<=7;day++){
    await evaluate('webDevPage={mode:'+JSON.stringify(day?'day':'week')+',week:1,day:'+(day||1)+'};renderWebDevelopment();window.scrollTo(0,0)');
    const r=await evaluate('({w:innerWidth,scroll:document.documentElement.scrollWidth})');assert(r.w<=width+1&&r.scroll<=width+1,'Layout '+width+' '+day+': '+JSON.stringify(r));
    if(day&&width<761)assert(await evaluate('[...document.querySelectorAll(".webdev-teaching .btn,.webdev-teaching .ls-quiz-opt")].every(b=>b.getBoundingClientRect().height>=44)'),'Touch targets '+width+' '+day);
   }
   if(width===1480||width===375){await evaluate('webDevPage={mode:"day",week:1,day:4};renderWebDevelopment();document.querySelector(".webdev-teaching").scrollIntoView({block:"start"})');await shot('lesson-'+width+'-'+theme);}
  }
 }
 await evaluate('window.__webBlob=null;const create=URL.createObjectURL;URL.createObjectURL=b=>{window.__webBlob=b;return create(b);};document.getElementById("exportBtn").click()');
 const backup=await evaluate('window.__webBlob.text()');
 await evaluate('delete DB.headNotes["webdev:1.1|day-notes"];delete DB.lessonsDone["webdev:1.1"];save();(()=>{const f=new File(['+JSON.stringify(backup)+'],"web-backup.json",{type:"application/json"}),d=new DataTransfer();d.items.add(f);const input=document.getElementById("importFile");input.files=d.files;input.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<50&&!await evaluate('!!document.getElementById("impMerge")');i++)await sleep(80);
 await evaluate('document.getElementById("impMerge").click()');assert(await evaluate('!!DB.lessonsDone["webdev:1.1"]&&DB.headNotes["webdev:1.1|day-notes"].includes("Day1")'),'Actual merge import');
 await evaluate('confirmMerge('+backup+');document.getElementById("impReplace").click()');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('DB.lessonQuizScores["webdev:1.7"]===100&&Array.from({length:7},(_,i)=>!!DB.lessonsDone["webdev:1."+(i+1)]&&DB.headNotes["webdev:1."+(i+1)+"|day-notes"].includes("Day"+(i+1))).every(Boolean)'),'Replace import and refresh');
 assert(await evaluate('DB.course.notes["1.0"]==="Keep Python note"&&DB.japanese.notes["31.1"]==="Keep Japanese note"&&DB.headNotes["cyber:9.1|day-notes"]==="Keep Cyber note"&&DB.lessonsDone["old-session"]&&DB.lessonQuizScores["old-quiz"]===75'),'Existing records preserved');
 // Load the authored pages themselves in a real offline browser, not just a parser.
 await send('Network.enable');await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 for(const [name,source] of Object.entries(examples)){
  const url=pathToFileURL(path.resolve('docs/web-development-week1/examples/'+name+'.html')).href;
  await send('Page.navigate',{url});for(let i=0;i<100&&!await evaluate('location.href==='+JSON.stringify(url)+'&&document.readyState==="complete"');i++)await sleep(50);
  const result=await evaluate('({mode:document.compatMode,title:document.title,h1:[...document.querySelectorAll("h1")].map(n=>n.textContent),h2:document.querySelectorAll("h2").length,charset:document.characterSet,viewport:document.querySelector("meta[name=viewport]")?.content,text:document.body.textContent})');
  assert.equal(result.mode,'CSS1Compat',name);assert.equal(result.title,source.match(/<title>(.*?)<\/title>/)[1]);assert.equal(result.h1.length,1);assert.equal(result.charset,'UTF-8');assert(result.viewport.includes('width=device-width'));assert(!result.text.includes('<h1>'));if(name==='project')assert.equal(result.h2,2);
 }
 assert.deepEqual(errors,[],'Browser console errors');
 console.log('PASS:7 lessons; all answers/solutions;43-question quizzes and best-score saving; per-heading/daily notes, hide/show, completion/undo, reload; Week1↔2 boundaries;5widths/both themes and touch sizes; actual backup merge/replace; old progress retained;4 authored HTML files opened offline with correct document mode/title/structure; no JS errors. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});
