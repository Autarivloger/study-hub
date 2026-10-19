// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-learning-navigation-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-design-profile-'));
const fixture=path.join(profile,'study-hub.html');
const source=before?require('child_process').execFileSync('git',['show','04e1f73:study-hub.html'],{encoding:'utf8',maxBuffer:50e6}):fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8');
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

 await evaluate('closeModal();DB=applyDefaults({course:{startDate:"2026-10-01T00:00:00Z",done:{"1.0":"2026-10-18"},notes:{"1.0":"Keep Python note"},partsDone:{"19.0.0":"2026-10-18"}},japanese:{done:{"1.1.te":"2026-10-18"},notes:{"30.1":"Keep Japanese note"},quizScores:{"30.1":86}},headNotes:{"cyber:9.1|day-notes":"Keep Cybersecurity note"},todos:[{id:"keep-task",title:"Keep my task",done:false}]});save();closeModal()');
 async function show(subject,week){
  const code=subject==='python'?'courseView={mode:"week",week:'+week+',dayIdx:null};switchView("course");renderCourse()':subject==='japanese'?'jpPage={mode:"week",week:'+week+'};switchView("japanese");renderJapanese()':subject==='cyber'?'cyberPage={mode:"week",week:'+week+',day:1};switchView("quiz");renderCybersecurityRoadmap()':'webDevPage={mode:"week",week:'+week+',day:1};switchView("webdev");renderWebDevelopment()';
  await evaluate('closeModal();'+code+';window.scrollTo(0,0)');
 }
 const measurements=[];
 for(const [width,height] of [[1480,668],[900,768],[375,812]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const subject of ['python','japanese','cyber','webdev']){
   await show(subject,subject==='japanese'?30:1);
   const item=await evaluate('(()=>{const root=document.querySelector(".view.active")||document.getElementById('+JSON.stringify(subject==='python'?'view-course':subject==='japanese'?'view-japanese':subject==='cyber'?'view-quiz':'view-webdev')+');const cards=[...root.querySelectorAll(".lesson-day-grid>.day-row,.jp-day-card")];const fallback=[...root.querySelectorAll(".day-list>.day-row")];const list=cards.length?cards:fallback;const first=list[0]?.getBoundingClientRect(),last=list.at(-1)?.getBoundingClientRect();return {count:list.length,top:Math.round(first?.top||0),gridHeight:Math.round((last?.bottom||0)-(first?.top||0)),last:Math.round(last?.bottom||0),viewport:innerWidth};})()');
   measurements.push({subject,width,viewportHeight:height,...item});
   if(width!==900)await shot(subject+'-'+width);
  }
 }
 fs.writeFileSync(path.join(out,'measurements.json'),JSON.stringify(measurements,null,2));
 if(before){console.log('Before measurements:',JSON.stringify(measurements));ws.close();return;}

 await evaluate('courseView={mode:"overview",week:null,dayIdx:null};switchView("course");renderCourse();window.scrollTo(0,0)');
 const beforeGroups=await evaluate('JSON.stringify(DB)');
 assert(await evaluate('document.querySelectorAll("details.learning-group").length===8&&[...document.querySelectorAll("details.learning-group")].every(d=>!d.open)&&document.querySelectorAll(".phase-list [data-week]").length===52'),'All phases collapsed by default, all 52 weeks retained');
 await evaluate('document.querySelector("[data-learning-group=python-phase-1]>summary").click()');await sleep(100);
 assert(await evaluate('document.querySelector("[data-learning-group=python-phase-1]").open&&document.querySelector("[data-week=\\"13\\"]").getBoundingClientRect().height>0'),'Open Core Python');
 await evaluate('document.querySelector("[data-learning-group=python-phase-1]>summary").click()');await sleep(100);
 const hiddenGroup=await evaluate('(()=>{const d=document.querySelector("[data-learning-group=python-phase-1]");return {open:d.open,height:d.clientHeight,summary:d.querySelector("summary").offsetHeight};})()');
 assert(!hiddenGroup.open&&hiddenGroup.height<=hiddenGroup.summary+2,'Hide Core Python: '+JSON.stringify(hiddenGroup));
 assert.equal(await evaluate('JSON.stringify(DB)'),beforeGroups,'Group toggle changed learner data');
 await evaluate('document.querySelector("[data-learning-group=python-phase-2]>summary").focus()');
 await send('Input.dispatchKeyEvent',{type:'rawKeyDown',key:' ',code:'Space',windowsVirtualKeyCode:32});await send('Input.dispatchKeyEvent',{type:'keyUp',key:' ',code:'Space',windowsVirtualKeyCode:32});await sleep(150);
 const keyboard=await evaluate('({open:document.querySelector("[data-learning-group=python-phase-2]").open,pref:localStorage.getItem("studyHubLearningGroups"),focus:document.activeElement.outerHTML.slice(0,180)})');
 assert(keyboard.open&&JSON.parse(keyboard.pref)["python-phase-2"]===true,'Keyboard open + preference: '+JSON.stringify(keyboard));
 await evaluate('document.querySelector("[data-week=\\"14\\"]").click();document.getElementById("backOverview").click()');
 assert(await evaluate('document.querySelector("[data-learning-group=python-phase-2]").open'),'Back retains expanded group');
 await shot('python-groups-mobile');

 // Every week keeps every day, including roadmaps without authored lessons.
 for(const subject of ['python','japanese','cyber','webdev']){
  const weeks=subject==='python'?[1,13,14,17,19,35,52]:subject==='japanese'?[1,2,10,19,29,30,31,32]:[1,9,16,17,52,53,104,105,156];
  for(const week of weeks){
   await show(subject,week);
   const count=await evaluate('document.querySelectorAll("#'+(subject==='python'?'courseBody':subject==='japanese'?'japaneseBody':subject==='cyber'?'cybersecurityBody':'webDevelopmentBody')+' .lesson-day-grid > *").length');
   assert.equal(count,subject==='japanese'&&week===32?0:7,'Daily choices '+subject+' '+week);
  }
 }
 // Cards still use their original navigation handlers and data keys.
 for(const subject of ['python','japanese','cyber','webdev']){
  await show(subject,subject==='japanese'?30:1);
  for(let day=1;day<=7;day++){
   const selector=subject==='python'?'[data-day="'+(day-1)+'"]':subject==='japanese'?'.jp-day-grid [data-jp-lesson="30.'+day+'"]':subject==='cyber'?'[data-cyber-day="'+day+'"]':'[data-webdev-day="'+day+'"]';
   await evaluate('document.querySelector('+JSON.stringify(selector)+').click()');
   assert(await evaluate(subject==='python'?'courseView.mode==="day"&&courseView.dayIdx==='+(day-1):subject==='japanese'?'jpPage.mode==="lesson"&&jpPage.lesson==="30.'+day+'"':subject==='cyber'?'cyberPage.mode==="day"&&cyberPage.day==='+day:'webDevPage.mode==="day"&&webDevPage.day==='+day),'Card navigation '+subject+' '+day);
   const back=subject==='python'?'#backWeek':subject==='japanese'?'.jp-actions [data-jp-week="30"]':subject==='cyber'?'[data-cyber-week="1"]':'[data-webdev-week="1"]';
   if(subject==='python')await show(subject,1);else await evaluate('document.querySelector('+JSON.stringify(back)+').click()');
  }
 }
 await show('python',1);
 await evaluate('document.querySelector("[data-toggle=\\"1\\"]").click()');
 assert(await evaluate('isDone(1,1)&&document.querySelector("[data-toggle=\\"1\\"]").getAttribute("aria-pressed")==="true"'),'Completion saves');
 await evaluate('document.querySelector("[data-toggle=\\"1\\"]").click()');
 assert(await evaluate('!isDone(1,1)&&isDone(1,0)'),'Completion undo preserves earlier completed day');

 // Real layouts, including actual viewport width (not just document overflow).
 for(const [width,height] of [[1480,668],[1024,768],[900,768],[768,1024],[375,812],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const subject of ['python','japanese','cyber','webdev']){
    await show(subject,subject==='japanese'?30:1);
    const gridSelector='#'+(subject==='python'?'courseBody':subject==='japanese'?'japaneseBody':subject==='cyber'?'cybersecurityBody':'webDevelopmentBody')+' .lesson-day-grid';
    const layout=await evaluate('(()=>{const g=document.querySelector('+JSON.stringify(gridSelector)+'),rect=g.getBoundingClientRect();return {viewport:innerWidth,scroll:document.documentElement.scrollWidth,columns:getComputedStyle(g).gridTemplateColumns.split(" ").length,last:g.lastElementChild.getBoundingClientRect().bottom,height:rect.height};})()');
    assert(layout.viewport<=width+1&&layout.scroll<=width+1,'Overflow '+subject+' '+width+' '+theme+': '+JSON.stringify(layout));
    assert.equal(layout.columns,width<=760?2:width<=1100?3:4,'Responsive columns '+subject+' '+width);
    if(width===1480)assert(layout.last<=height,'Day 7 below desktop screen '+subject+': '+JSON.stringify(layout));
    if(width<761&&subject==='python')assert(await evaluate('[...document.querySelectorAll("#courseBody .lesson-day-grid button")].every(b=>{const r=b.getBoundingClientRect();return r.width>=44&&r.height>=44})'),'Completion/card touch size');
    if((width===1480||width===375)&&theme==='dark')await shot(subject+'-'+width+'-dark');
   }
   await evaluate('courseView={mode:"overview",week:null,dayIdx:null};switchView("course");renderCourse()');
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Disclosure overflow '+width+' '+theme);
  }
 }
 // Check every authored/roadmap week at the desktop size the learner uses.
 await send('Emulation.setDeviceMetricsOverride',{width:1480,height:668,deviceScaleFactor:1,mobile:false});
 const tall=[];
 for(const subject of ['python','japanese','cyber','webdev']){
  await show(subject,1);
  const report=await evaluate('(()=>{const subject='+JSON.stringify(subject)+',max=subject==="python"?52:subject==="japanese"?36:156,id=subject==="python"?"courseBody":subject==="japanese"?"japaneseBody":subject==="cyber"?"cybersecurityBody":"webDevelopmentBody",bad=[];for(let week=1;week<=max;week++){if(subject==="python"){courseView={mode:"week",week,dayIdx:null};renderCourse()}else if(subject==="japanese"){jpPage={mode:"week",week};renderJapanese()}else if(subject==="cyber"){cyberPage={mode:"week",week,day:1};renderCybersecurityRoadmap()}else{webDevPage={mode:"week",week,day:1};renderWebDevelopment()}const g=document.querySelector("#"+id+" .lesson-day-grid");if(g&&g.lastElementChild.getBoundingClientRect().bottom>innerHeight+1)bad.push({week,bottom:g.lastElementChild.getBoundingClientRect().bottom});}return bad;})()');
  if(report.length)tall.push({subject,weeks:report});
 }
 assert.deepEqual(tall,[],'Day 7 must fit desktop across every week');
 // Refresh retains UI preference and existing learning data. No private profile is used.
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 await evaluate('courseView={mode:"overview",week:null,dayIdx:null};switchView("course");renderCourse()');
 assert(await evaluate('document.querySelector("[data-learning-group=python-phase-2]").open&&!document.querySelector("[data-learning-group=python-phase-1]").open'),'Refresh disclosure state');
 assert(await evaluate('DB.course.notes["1.0"]==="Keep Python note"&&DB.course.partsDone["19.0.0"]&&DB.japanese.notes["30.1"]==="Keep Japanese note"&&DB.japanese.quizScores["30.1"]===86&&DB.headNotes["cyber:9.1|day-notes"]==="Keep Cybersecurity note"&&DB.todos[0].title==="Keep my task"'),'Existing data preserved');
 assert.deepEqual(errors,[],'JavaScript errors');
 console.log('PASS: native mouse/keyboard disclosures, remembered state without learner-data changes, all 52 Python weeks, daily cards across four courses and old/new weeks, all 28 card destinations, completion save/undo, six widths and both themes, Day 7 inside desktop viewport, touch controls, notes/progress after refresh, no console errors. Measurements:',JSON.stringify(measurements));
 console.log('Screenshots:',out);ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

