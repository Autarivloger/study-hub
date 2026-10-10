const fs=require('fs'),os=require('os'),path=require('path'),{spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-yoga-')),fixture=path.join(profile,'yoga.html');
fs.writeFileSync(fixture,fs.readFileSync('study-hub.html','utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const f=path.join(profile,'DevToolsActivePort');if(fs.existsSync(f)){port=Number(fs.readFileSync(f,'utf8').split('\n')[0]);break;}await sleep(100);}if(!port)throw Error('Chrome did not start');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval ? window.__courseTestEval('+JSON.stringify(expression)+') : eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const assert=(v,m)=>{if(!v)throw Error(m);};
 await send('Runtime.enable');await send('Page.enable');for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}assert(await evaluate('window.__studyHubBooted'),'Boot failed');
 await evaluate('document.querySelector("#sidebar [data-view=lessons]").click()');
 assert(await evaluate('document.querySelector("#brandTitle").textContent==="Yoga & Meditation" && document.querySelectorAll(".yoga-card").length===7'),'Yoga tab/home failed');
 assert(await evaluate('(()=>{for(const item of YOGA_COURSE.sessions)for(const duration of [20,30])if(yogaStages(item,duration).reduce((n,s)=>n+s.minutes,0)!==duration)return false;return true;})()'),'Suggested times do not add up');
 await evaluate('DB.course.done["1.0"]="2025-01-01";DB.japanese.done["1.1"]="2025-01-01";DB.headNotes.legacy="Old note";DB.headNotes["cyber:1.3|day-notes"]="Risk is contextual";save();');
 for(let day=1;day<=7;day++){
  await evaluate('yogaPage={mode:"session",id:"yoga:intermediate:1.'+day+'",duration:20};renderLessons()');
  assert(await evaluate('document.querySelectorAll(".yoga-stages>li").length===8 && document.querySelectorAll(".yoga-guide").length>=4'),'Session '+day+' missing guidance');
  assert(await evaluate('!document.querySelector("#yogaPracticeNotes .hn-box").hidden && document.querySelector("#yogaPracticeNotes textarea").getAttribute("aria-label").includes("Session")'),'Session '+day+' notes are not visible/labeled');
  await evaluate('document.querySelector("#yogaPracticeNotes [data-hn]").click()');
  assert(await evaluate('document.querySelector("#yogaPracticeNotes .hn-box").hidden'),'Hide notes failed');
  await evaluate('document.querySelector("[data-yoga-notes]").click()');
  assert(await evaluate('!document.querySelector("#yogaPracticeNotes .hn-box").hidden && document.activeElement===document.querySelector("#yogaPracticeNotes textarea")'),'Jump/show notes failed');
  await evaluate('document.querySelector("[data-yoga-duration=\\"30\\"]").click()');
  assert(await evaluate('yogaPage.duration===30'),'Duration switch failed');
  await evaluate('(()=>{const quiz=yogaSession(yogaPage.id).quiz;for(let i=0;i<quiz.quiz.length;i++){document.querySelector("#lessonsBody [data-lq=\\""+i+"\\"][data-lo=\\""+quiz.quiz[i].correct+"\\"]").click();}})()');
  assert(await evaluate('DB.lessonQuizScores["yoga:quiz:1.'+day+'"]===100'),'Yoga quiz saving '+day);
 }
 await evaluate('DB.headNotes["yoga:intermediate:1.1|reflection"]="Existing reflection note";yogaPage={mode:"session",id:"yoga:intermediate:1.1",duration:20};renderLessons()');
 assert(await evaluate('document.querySelector("#yogaPracticeNotes textarea").value==="Existing reflection note"'),'Existing note did not appear after translation');
 await evaluate('document.querySelector("#lessonsBody .hn-text").value="Breath felt steady <script>not executed</script>";document.querySelector("#lessonsBody .hn-text").dispatchEvent(new Event("input",{bubbles:true}));');await sleep(650);
 await evaluate('document.querySelector("[data-yoga-complete]").click()');
 assert(await evaluate('lessonDone("yoga:intermediate:1.1") && !Object.keys(DB.reviews.items).some(k=>k.includes("yoga:"))'),'Yoga completion contaminated Python review');
 await evaluate('document.querySelector("[data-yoga-complete]").click()');assert(await evaluate('!lessonDone("yoga:intermediate:1.1")'),'Undo failed');await evaluate('document.querySelector("[data-yoga-complete]").click()');
 await evaluate('document.querySelector("[data-yoga-id=\\"yoga:intermediate:1.2\\"]").click()');assert(await evaluate('yogaPage.id==="yoga:intermediate:1.2"'),'Next session failed');
 await evaluate('document.querySelector("[data-yoga-id=\\"yoga:intermediate:1.1\\"]").click()');assert(await evaluate('yogaPage.id==="yoga:intermediate:1.1"'),'Previous session failed');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
 assert(await evaluate('lessonDone("yoga:intermediate:1.1") && DB.lessonQuizScores["yoga:quiz:1.7"]===100 && DB.headNotes["yoga:intermediate:1.1|reflection"].includes("Breath felt steady")'),'Yoga progress/notes/quiz failed reload');
 await evaluate('document.querySelector("#sidebar [data-view=lessons]").click();document.querySelector("#lessonsBody [data-yoga-mode=session]").click()');assert(await evaluate('yogaPage.id==="yoga:intermediate:1.2"'),'Continue did not find first incomplete session');
 // Exercise the existing backup download and file import UI with isolated test data.
 await evaluate('window.__yogaBlob=null;window.__oldURL=URL.createObjectURL;URL.createObjectURL=function(blob){window.__yogaBlob=blob;return window.__oldURL(blob);};document.querySelector("#exportBtn").click()');
 const backup=await evaluate('window.__yogaBlob.text()');assert(JSON.parse(backup).lessonsDone['yoga:intermediate:1.1'],'Export lost Yoga progress');
 assert(JSON.parse(backup).headNotes['cyber:1.3|day-notes']==='Risk is contextual','Export lost cybersecurity notes');
 await evaluate('delete DB.lessonsDone["yoga:intermediate:1.1"];delete DB.headNotes["yoga:intermediate:1.1|reflection"];delete DB.headNotes["cyber:1.3|day-notes"];save();');
 await evaluate('(()=>{const file=new File(['+JSON.stringify(backup)+'],"yoga-backup.json",{type:"application/json"});const dt=new DataTransfer();dt.items.add(file);const input=document.querySelector("#importFile");input.files=dt.files;input.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<40;i++){if(await evaluate('Boolean(document.querySelector("#impMerge"))'))break;await sleep(100);}await evaluate('document.querySelector("#impMerge").click()');
 assert(await evaluate('lessonDone("yoga:intermediate:1.1") && DB.headNotes["yoga:intermediate:1.1|reflection"] && DB.course.done["1.0"] && DB.japanese.done["1.1"] && DB.headNotes.legacy==="Old note"'),'Merge import lost Yoga or legacy data');
 assert(await evaluate('DB.headNotes["cyber:1.3|day-notes"]==="Risk is contextual"'),'Merge import lost cybersecurity notes');
 await evaluate('confirmMerge('+JSON.stringify(JSON.parse(backup))+');document.querySelector("#impReplace").click()');assert(await evaluate('lessonDone("yoga:intermediate:1.1") && DB.lessonQuizScores["yoga:quiz:1.7"]===100'),'Replace import lost Yoga data');
 assert(await evaluate('migrateCompletedToReviews()===false'),'Unknown Yoga keys trigger endless Python review migration');
 assert(await evaluate('DB.headNotes["cyber:1.3|day-notes"]==="Risk is contextual"'),'Replace import lost cybersecurity notes');
 for(const width of [375,768,1280]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:812,deviceScaleFactor:1,mobile:width<600});
  for(let theme=0;theme<2;theme++){
   await evaluate('document.querySelector("#themeBtn").click();switchView("lessons")');
   for(const mode of ['home','poses','meditations','gita']){await evaluate('yogaPage.mode='+JSON.stringify(mode)+';renderLessons()');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Yoga overflow '+width+' '+mode);}
   for(let day=1;day<=7;day++){await evaluate('yogaPage={mode:"session",id:"yoga:intermediate:1.'+day+'",duration:30};renderLessons();document.querySelector(".yoga-guide").open=true');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Session overflow '+width+' '+day);}
  }
 }
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});await evaluate('document.documentElement.dataset.theme="light";yogaPage.mode="home";renderLessons();window.scrollTo(0,0)');
 let shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-yoga-mobile-light.png'),Buffer.from(shot.data,'base64'));
 await evaluate('document.documentElement.dataset.theme="dark";yogaPage={mode:"session",id:"yoga:intermediate:1.1",duration:20};renderLessons();window.scrollTo(0,0)');
 shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-yoga-mobile-dark.png'),Buffer.from(shot.data,'base64'));
 await evaluate('document.querySelector("[data-yoga-notes]").click()');
 shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-yoga-mobile-notes.png'),Buffer.from(shot.data,'base64'));
 assert(errors.length===0,'JS errors: '+errors.join('; '));console.log('PASS: Yoga 7 sessions,21 answers,20/30-minute plans,notes,completion/undo,continue,refresh,export/import merge+replace,mobile/tablet/desktop,light/dark,no JS errors');
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{if(ws)ws.close();browser.kill();});
