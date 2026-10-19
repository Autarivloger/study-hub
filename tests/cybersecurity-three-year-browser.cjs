// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-cyber-three-year-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-design-profile-'));
const fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=expression=>eval(expression);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const watchdog=setTimeout(()=>{console.error('Design check timed out');browser.kill();process.exit(1);},120000);
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

 await evaluate('closeModal();DB=applyDefaults({headNotes:{"cyber:9.1|day-notes":"Keep Week9 notes",legacy:"Keep heading notes"},course:{done:{"1.0":"2026-10-01"},notes:{"1.0":"Keep Python notes"}},japanese:{notes:{"1.1.te":"Keep Japanese notes"}},quizzes:[{id:"cyber-legacy",name:"Saved quiz",questions:[{id:"q1",text:"Saved question",options:["Yes","No"],correct:0}],lastScore:67}]});save();cyberPage={mode:"overview",week:1,day:1};switchView("quiz");closeModal();window.__beforeCyberRoadmap=JSON.stringify([DB.headNotes,DB.course,DB.japanese,DB.quizzes])');
 assert(await evaluate('document.querySelectorAll("[data-cyber-year]").length===3&&document.querySelectorAll("[data-cyber-week]").length===156&&document.querySelectorAll(".cyber-phase").length===39'),'Missing years/weeks/phases');
 assert(await evaluate('document.querySelector("[data-cyber-year=\\"1\\"]").open&&!document.querySelector("[data-cyber-year=\\"2\\"]").open&&!document.querySelector("[data-cyber-year=\\"3\\"]").open'),'Initial year grouping');
 assert(await evaluate('Array.from(document.querySelectorAll(".cyber-year")).every(year=>year.querySelectorAll("[data-cyber-week]").length===52)'),'Year ranges');
 // Render every week and every roadmap day; all new content stays a plan only.
 await evaluate('(()=>{for(const week of CYBERSECURITY_ROADMAP){cyberPage={mode:"week",week:week.week,day:1};renderCybersecurityRoadmap();if(document.querySelectorAll("[data-cyber-day]").length!==7)throw Error("Week list "+week.week);if(!document.querySelector(".week-header h2").textContent.includes(week.title))throw Error("Week title "+week.week);}})()');
 for(let start=10;start<=156;start+=25){
  await evaluate('(()=>{for(let w='+start+';w<=Math.min(156,'+(start+24)+');w++){for(let d=1;d<=7;d++){cyberPage={mode:"day",week:w,day:d};renderCybersecurityRoadmap();const day=CYBERSECURITY_ROADMAP[w-1].days[d-1],text=document.getElementById("cybersecurityBody").textContent;if(!text.includes(day.focus)||!day.topics.every(t=>text.includes(t)))throw Error("Missing topic "+w+"."+d);if(document.querySelector(".cyber-teaching")||document.querySelector("#cyberDayNotes"))throw Error("Unrequested lesson "+w+"."+d);if(day.python.length&&!document.querySelector(".cyber-python"))throw Error("Python support missing "+w+"."+d);if(!document.querySelector("[data-cyber-step=\\"1\\"]")||!document.querySelector("[data-cyber-week]"))throw Error("Navigation missing "+w+"."+d);}}})()');
 }
 // Existing teaching, self-checks and automatically saved notes still work.
 await evaluate('cyberPage={mode:"day",week:9,day:1};renderCybersecurityRoadmap()');
 assert(await evaluate('!!document.querySelector(".cyber-teaching")&&document.querySelector("#cyberDayNotes textarea").value==="Keep Week9 notes"&&document.querySelectorAll(".cyber-check").length>0'),'Existing Week9 lesson/notes');
 await evaluate('document.querySelector(".cyber-check [data-reveal]").click()');
 assert(await evaluate('!document.querySelector(".cyber-check .ls-try-a").hidden'),'Existing self-check reveal');
 await evaluate('document.querySelector("#cyberDayNotes textarea").value="Saved after three-year update";document.querySelector("#cyberDayNotes textarea").dispatchEvent(new Event("input",{bubbles:true}))');await sleep(650);
 assert(await evaluate('DB.headNotes["cyber:9.1|day-notes"]==="Saved after three-year update"'),'Notes saving');
 // Previous/Next moves across every year boundary and stops at the final day.
 for(const last of [16,52,104,155]){
  await evaluate('cyberPage={mode:"day",week:'+last+',day:7};renderCybersecurityRoadmap();document.querySelector("[data-cyber-step=\\"1\\"]").click()');
  assert(await evaluate('cyberPage.week==='+(last+1)+'&&cyberPage.day===1'),'Next boundary '+last);
  await evaluate('document.querySelector("[data-cyber-step=\\"-1\\"]").click()');
  assert(await evaluate('cyberPage.week==='+last+'&&cyberPage.day===7'),'Previous boundary '+last);
 }
 await evaluate('cyberPage={mode:"day",week:156,day:7};renderCybersecurityRoadmap()');
 assert(await evaluate('document.querySelector("[data-cyber-step=\\"1\\"]").disabled'),'Final Next must be disabled');
 await evaluate('document.querySelector("[data-cyber-step=\\"1\\"]").click()');assert(await evaluate('cyberPage.week===156&&cyberPage.day===7'),'Beyond final day');
 await evaluate('cyberPage={mode:"day",week:1,day:1};renderCybersecurityRoadmap()');assert(await evaluate('document.querySelector("[data-cyber-step=\\"-1\\"]").disabled'),'First Previous');
 // Actual Year -> Week -> Day -> Back flow, including remembered year context.
 await evaluate('cyberPage={mode:"overview",week:1,day:1};renderCybersecurityRoadmap();document.querySelector("[data-cyber-year=\\"3\\"] > summary").click();document.querySelector("[data-cyber-week=\\"156\\"]").click();document.querySelector("[data-cyber-day=\\"7\\"]").click()');
 assert(await evaluate('cyberPage.mode==="day"&&cyberPage.week===156&&cyberPage.day===7'),'Year navigation');
 await evaluate('document.querySelector("[data-cyber-week]").click();document.querySelector("[data-cyber-all]").click()');
 assert(await evaluate('cyberPage.mode==="overview"&&document.querySelector("[data-cyber-year=\\"3\\"]").open'),'Back preserves year context');
 // Mobile/desktop and theme coverage for the new layout and late roadmap days.
 for(const [width,height] of [[1440,900],[900,768],[375,812],[320,640]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const year of [1,2,3]){
    await evaluate('cyberPage={mode:"overview",week:'+(year*52)+',day:1};renderCybersecurityRoadmap();window.scrollTo(0,0)');
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Overview overflow '+year+' '+width+' '+theme);
    if(year===3&&(width===1440||width===375))await shot('year3-'+width+'-'+theme);
   }
   for(const w of [17,52,53,104,105,140,149,156]){
    await evaluate('cyberPage={mode:"week",week:'+w+',day:1};renderCybersecurityRoadmap();window.scrollTo(0,0)');
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Week overflow '+w+' '+width);
    await evaluate('document.querySelector("[data-cyber-day=\\"6\\"]").click()');
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Day overflow '+w+' '+width);
   }
  }
 }
 // Floating Back delegates the same parent for the new weeks.
 await evaluate('cyberPage={mode:"day",week:156,day:6};renderCybersecurityRoadmap();(()=>{const space=document.createElement("div");space.style.height="1200px";document.getElementById("cybersecurityBody").append(space);window.scrollTo(0,600);})()');await sleep(100);
 assert(await evaluate('!document.getElementById("floatingBack").hidden'),'Floating Back on late roadmap');
 await evaluate('document.getElementById("floatingBack").click()');assert(await evaluate('cyberPage.mode==="week"&&cyberPage.week===156'),'Floating Back target');
 // Both existing Online Safety and saved legacy quizzes remain available.
 await evaluate('cyberPage.mode="overview";renderCybersecurityRoadmap();document.querySelector("[data-safety-open]").click();document.querySelector("[data-safety-lesson=\\"1\\"]").click()');
 assert(await evaluate('cyberPage.mode==="safety-lesson"&&!!document.querySelector(".safety-teaching")'),'Online Safety unchanged');
 await evaluate('cyberPage.mode="overview";renderCybersecurityRoadmap();document.getElementById("cyberOldQuizzes").click();document.querySelector("#quizList [data-id=cyber-legacy]").click()');
 assert(await evaluate('document.getElementById("quizDetail").textContent.includes("Saved question")&&DB.quizzes[0].lastScore===67'),'Saved quizzes');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('DB.headNotes["cyber:9.1|day-notes"]==="Saved after three-year update"&&DB.headNotes.legacy==="Keep heading notes"&&DB.course.notes["1.0"]==="Keep Python notes"&&DB.japanese.notes["1.1.te"]==="Keep Japanese notes"&&DB.course.done["1.0"]&&DB.quizzes[0].lastScore===67'),'Saved data after reload');
 assert.deepEqual(errors,[],'Browser errors');
 console.log('PASS:156 week lists and all1029 roadmap-only days render; year/week/day/Back and year boundaries; final guards; old teaching, notes saving/refresh, Online Safety and quizzes; four widths/light+dark; floating Back; no console errors. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

