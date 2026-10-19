// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-web-development-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
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

 await evaluate('closeModal();DB=applyDefaults({course:{done:{"1.0":"2026-10-01"},notes:{"1.0":"Keep Python notes"}},japanese:{notes:{"1.1.te":"Keep Japanese notes"}},headNotes:{legacy:"Keep heading notes"},exerciseTracker:{entries:{"keep-entry":{id:"keep-entry",exerciseId:"keep-exercise",exerciseName:"Push-up",date:"2026-10-19",quantity:20,unit:"reps",sets:2,notes:"Keep activity",createdAt:"2026-10-19T12:00:00.000Z",updatedAt:"2026-10-19T12:00:00.000Z",deleted:false}}}});save();window.__beforeWebDevelopment=JSON.stringify(DB);document.querySelector("#sidebar [data-view=webdev] svg path").dispatchEvent(new MouseEvent("click",{bubbles:true}));window.scrollTo(0,0)');
 assert(await evaluate('document.getElementById("view-webdev").classList.contains("active")&&document.getElementById("brandTitle").textContent==="Web Development"'),'Desktop navigation/icon activation');
 assert(await evaluate('document.querySelectorAll(".view.active").length===1&&document.querySelectorAll("#sidebar [aria-current=page]").length===1&&document.querySelectorAll("#tabnav [aria-current=page]").length===1'),'Active view/navigation');
 assert(await evaluate('document.querySelectorAll("[data-webdev-year]").length===3&&document.querySelectorAll("#webDevelopmentBody .cyber-phase").length===39&&document.querySelectorAll(".cyber-phase [data-webdev-week]").length===156'),'Complete path grouping');
 assert(await evaluate('document.querySelector("[data-webdev-year=\\"1\\"]").open&&document.querySelector("#webDevelopmentBody").textContent.includes("No previous HTML")'),'Beginner starting point');
 // Every roadmap day remains; only authored days also show full lessons.
 await evaluate('(()=>{for(const week of WEBDEV_ROADMAP){webDevPage={mode:"week",week:week.week,day:1};renderWebDevelopment();if(document.querySelectorAll("[data-webdev-day]").length!==7)throw Error("Missing week days "+week.week);if(!document.getElementById("webDevelopmentBody").textContent.includes(week.checkpoint))throw Error("Missing readiness check "+week.week);}})()');
 for(let start=1;start<=156;start+=26){
  await evaluate('(()=>{for(let w='+start+';w<=Math.min(156,'+(start+25)+');w++)for(let d=1;d<=7;d++){webDevPage={mode:"day",week:w,day:d};renderWebDevelopment();const day=WEBDEV_ROADMAP[w-1].days[d-1],text=document.getElementById("webDevelopmentBody").textContent,ready=Boolean(WEBDEV_TEACH[w+"."+d]);if(!text.includes(day.focus)||!day.topics.every(topic=>text.includes(topic)))throw Error("Missing day content "+w+"."+d);if(Boolean(document.querySelector(".webdev-teaching"))!==ready||Boolean(document.querySelector(".webdev-roadmap-label"))===ready)throw Error("Lesson readiness mismatch "+w+"."+d);if(document.querySelectorAll("[data-webdev-step]").length!==2)throw Error("Missing navigation "+w+"."+d);}})()');
 }
 // Actual control flow: starter, day navigation, cross-year boundaries and Back.
 await evaluate('webDevPage={mode:"overview",week:1,day:1};renderWebDevelopment();document.querySelector(".webdev-start [data-webdev-week]").click();document.querySelector("[data-webdev-day=\\"1\\"]").click()');
 assert(await evaluate('webDevPage.week===1&&webDevPage.day===1&&document.getElementById("webDevelopmentBody").textContent.includes("Files and folders")'),'Start Week1 Day1');
 assert(await evaluate('document.querySelector("[data-webdev-step=\\"-1\\"]").disabled'),'First Previous guard');
 for(const last of [1,24,52,68,72,104,128,155]){
  await evaluate('webDevPage={mode:"day",week:'+last+',day:7};renderWebDevelopment();document.querySelector("[data-webdev-step=\\"1\\"]").click()');
  assert(await evaluate('webDevPage.week==='+(last+1)+'&&webDevPage.day===1'),'Next boundary '+last);
  await evaluate('document.querySelector("[data-webdev-step=\\"-1\\"]").click()');assert(await evaluate('webDevPage.week==='+last+'&&webDevPage.day===7'),'Previous boundary '+last);
 }
 await evaluate('webDevPage={mode:"day",week:156,day:7};renderWebDevelopment()');assert(await evaluate('document.querySelector("[data-webdev-step=\\"1\\"]").disabled'),'Final Next guard');
 await evaluate('document.querySelector("[data-webdev-step=\\"1\\"]").click()');assert(await evaluate('webDevPage.week===156&&webDevPage.day===7'),'Beyond roadmap');
 await evaluate('document.querySelector("[data-webdev-week]").click();document.querySelector("[data-webdev-all]").click()');assert(await evaluate('document.querySelector("[data-webdev-year=\\"3\\"]").open'),'Back keeps year context');
 // Both the new route and old routes stay separate and select their own navigation.
 for(const name of ['course','japanese','quiz','todo','webdev']){
  await evaluate('document.querySelector("#sidebar [data-view='+name+']").click()');
  assert(await evaluate('document.querySelector(".view.active").id==="view-'+name+'"&&document.querySelector("#sidebar [data-view='+name+']").getAttribute("aria-current")==="page"'),'Existing route '+name);
 }
 // Layout in each year, weeks and days across phone, tablet and desktop themes.
 for(const [width,height] of [[1440,950],[900,768],[768,900],[375,812],[320,640]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const year of [1,2,3]){
    await evaluate('webDevPage={mode:"overview",week:'+(year===1?1:year*52)+',day:1};switchView("webdev");window.scrollTo(0,0)');
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Overview overflow '+year+' '+width+' '+theme);
    if(year===1&&(width===1440||width===375))await shot('home-'+width+'-'+theme);
   }
   for(const w of [1,12,25,52,53,57,72,73,104,105,128,156]){
    await evaluate('webDevPage={mode:"week",week:'+w+',day:1};renderWebDevelopment();window.scrollTo(0,0)');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Week overflow '+w+' '+width);
    await evaluate('document.querySelector("[data-webdev-day=\\"7\\"]").click()');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Day overflow '+w+' '+width);
   }
  }
 }
 // Real mobile navigation uses the same tap/click path as the existing sections.
 await evaluate('switchView("course");document.querySelector("#tabnav [data-view=webdev]").scrollIntoView({block:"nearest",inline:"nearest"})');
 const point=await evaluate('(()=>{const r=document.querySelector("#tabnav [data-view=webdev]").getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()');
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...point,id:1}]});await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await sleep(100);
 assert(await evaluate('document.querySelector("#view-webdev").classList.contains("active")'),'Mobile tap navigation');
 // Existing floating Back finds the new view's normal .back-link automatically.
 await evaluate('webDevPage={mode:"day",week:73,day:1};renderWebDevelopment();(()=>{const space=document.createElement("div");space.style.height="1200px";document.getElementById("webDevelopmentBody").append(space);window.scrollTo(0,600);})()');await sleep(100);
 assert(await evaluate('!document.getElementById("floatingBack").hidden'),'Floating Back on Web Development');
 await evaluate('document.getElementById("floatingBack").click()');assert(await evaluate('webDevPage.mode==="week"&&webDevPage.week===73&&window.scrollY===0'),'Floating Back parent');
 assert(await evaluate('JSON.stringify(DB)===window.__beforeWebDevelopment'),'Read-only roadmap changed saved data');
 // The original Cybersecurity component still opens later years and retains lessons.
 await evaluate('cyberPage={mode:"overview",week:156,day:1};switchView("quiz")');
 assert(await evaluate('document.querySelectorAll("[data-cyber-week]").length===156&&document.querySelector("[data-cyber-year=\\"3\\"]").open'),'Shared Cybersecurity overview');
 await evaluate('cyberPage={mode:"day",week:9,day:1};renderCybersecurityRoadmap()');assert(await evaluate('!!document.querySelector(".cyber-teaching")&&!!document.querySelector("#cyberDayNotes")'),'Existing teaching preserved');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('DB.exerciseTracker.entries["keep-entry"].quantity===20&&DB.course.notes["1.0"]==="Keep Python notes"&&DB.japanese.notes["1.1.te"]==="Keep Japanese notes"&&DB.headNotes.legacy==="Keep heading notes"'),'Existing data after reload');
 await evaluate('closeModal();document.querySelector("#sidebar [data-view=webdev]").click()');assert(await evaluate('document.querySelectorAll(".cyber-phase [data-webdev-week]").length===156'),'Roadmap available after reload');
 assert.deepEqual(errors,[],'Browser errors');
 console.log('PASS:156 weeks/all1092 days, readiness/project/review goals; desktop/icon/mobile-tap navigation, boundaries and floating Back;5widths/light+dark; shared Cybersecurity lessons and routes preserved; no data writes, refresh or console errors. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

