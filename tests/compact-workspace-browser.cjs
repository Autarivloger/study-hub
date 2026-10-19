// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-compact-workspace-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
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

 await evaluate('closeModal();DB=applyDefaults({course:{done:{"1.0":"2026-10-18","1.1":"2026-10-18"},partsDone:{"50.0.0":"2026-10-18"},notes:{"50.0":"Keep study notes"}},headNotes:{legacy:"Keep heading notes"},lastSeen:{kind:"day",week:50,dayIdx:0,part:1,title:"Concurrency & parallelism",at:"2026-10-18T12:00:00Z"}});save();courseView={mode:"overview",week:null,dayIdx:null};switchView("course");window.scrollTo(0,0)');
 const settle=()=>sleep(100);
 async function click(selector){
  const p=await evaluate('(()=>{const r=document.querySelector('+JSON.stringify(selector)+').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()');
  await send('Input.dispatchMouseEvent',{type:'mousePressed',...p,button:'left',clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseReleased',...p,button:'left',clickCount:1});await settle();
 }
 const compactCSS=fs.readFileSync(path.resolve(__dirname,'../scripts/compact-workspace.css'),'utf8');
 const measurements=[];
 for(const [width,height] of [[1440,1000],[900,768],[375,812]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  await evaluate('document.documentElement.classList.remove("sidebar-compact");courseView={mode:"overview",week:null,dayIdx:null};switchView("course");window.scrollTo(0,0);window.__completeStyles=document.querySelector("style").textContent');
  await evaluate('document.querySelector("style").textContent=window.__completeStyles.replace('+JSON.stringify(compactCSS+'\n')+',"")');await settle();
  const baseline=await evaluate('({dashboard:document.querySelector(".learning-dashboard").getBoundingClientRect().height,firstWeek:document.querySelector(".phase-list [data-week]").getBoundingClientRect().top})');
  await evaluate('document.querySelector("style").textContent=window.__completeStyles');await settle();
  const current=await evaluate('({dashboard:document.querySelector(".learning-dashboard").getBoundingClientRect().height,firstWeek:document.querySelector(".phase-list [data-week]").getBoundingClientRect().top})');
  measurements.push({width,before:baseline,after:current});
  assert(current.dashboard<baseline.dashboard,'Dashboard did not shrink '+width+' '+JSON.stringify({baseline,current}));
  assert(current.firstWeek<baseline.firstWeek-60,'Learning path did not move up '+width+' '+JSON.stringify({baseline,current}));
 }
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 await evaluate('document.documentElement.classList.remove("sidebar-compact");window.scrollTo(0,0);window.__layoutDataBefore=JSON.stringify(DB)');
 assert(await evaluate('document.getElementById("sidebarToggle").getAttribute("aria-expanded")==="true"'),'Initial expanded state');
 const expandedWidth=await evaluate('document.getElementById("content").getBoundingClientRect().width');
 await click('#sidebarToggle');
 assert(await evaluate('document.documentElement.classList.contains("sidebar-compact")&&document.getElementById("sidebar").getBoundingClientRect().width===72'),'Icon rail width');
 assert(await evaluate('document.querySelectorAll("#sidebar .nav-item svg").length===14&&[...document.querySelectorAll("#sidebar .nav-label")].every(label=>getComputedStyle(label).display==="none")'),'Only icons in compact sidebar');
 assert(await evaluate('[...document.querySelectorAll("#sidebar .nav-item")].every(button=>button.title&&button.getAttribute("aria-label")===button.querySelector(".nav-label").textContent.trim())'),'Hidden names need accessible labels and hover titles');
 assert(await evaluate('document.getElementById("content").getBoundingClientRect().width')>expandedWidth+140,'Collapsed rail did not free page space');
 assert(await evaluate('localStorage.getItem("studyHubSidebarCompact")==="1"&&document.getElementById("sidebarToggle").getAttribute("aria-label")==="Expand sidebar"'),'Preference/expand label');
 assert(await evaluate('JSON.stringify(DB)===window.__layoutDataBefore'),'Layout toggle changed learner data');
 // Every icon remains a working navigation target while labels are hidden.
 for(const name of ['webdev','japanese','quiz','reviews','flashcards','typing','games','todo','timer','journal','lessons','wisdom','liked','course']){
  await evaluate('document.querySelector("#sidebar [data-view='+name+']").scrollIntoView({block:"nearest"})');
  await click('#sidebar [data-view='+name+']');
  assert(await evaluate('document.querySelector(".view.active").id==="view-'+name+'"&&document.querySelector("#sidebar [data-view='+name+']").getAttribute("aria-current")==="page"'),'Icon navigation '+name);
 }
 // The bottom toggle stays reachable while both the page and nav list scroll.
 await evaluate('window.scrollTo(0,1800);document.getElementById("sidebarNavigation").scrollTop=99999');await settle();
 assert(await evaluate('(()=>{const r=document.getElementById("sidebarToggle").getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.top>=0&&r.bottom<=innerHeight&&document.getElementById("sidebarToggle").contains(hit);})()'),'Pinned bottom toggle is unreachable');
 await click('#sidebarToggle');assert(await evaluate('!document.documentElement.classList.contains("sidebar-compact")&&document.getElementById("sidebar").getBoundingClientRect().width===232'),'Expand restores full width');
 // Native keyboard activation does not lose focus or require a mouse.
 await evaluate('document.getElementById("sidebarToggle").focus()');
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r'});await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await settle();
 assert(await evaluate('document.documentElement.classList.contains("sidebar-compact")&&document.activeElement.id==="sidebarToggle"'),'Keyboard collapse/focus');
 // A real reload restores the rail preference without modifying course notes.
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('document.documentElement.classList.contains("sidebar-compact")&&document.getElementById("sidebarToggle").getAttribute("aria-expanded")==="false"'),'Preference after refresh');
 assert(await evaluate('DB.course.notes["50.0"]==="Keep study notes"&&DB.headNotes.legacy==="Keep heading notes"'),'Study data after refresh');
 await evaluate('closeModal()');
 // Desktop/tablet/mobile layouts and both themes, expanded and icon-only.
 const pages=['course','webdev','japanese','quiz','reviews','flashcards','typing','games','todo','timer','journal','lessons','wisdom','liked'];
 for(const [width,height] of [[1440,900],[1024,768],[900,700],[768,800],[375,812],[320,640]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const collapsed of [false,true]){
    await evaluate('if(document.documentElement.classList.contains("sidebar-compact")!=='+collapsed+')document.getElementById("sidebarToggle").click()');
    for(const name of pages){
     await evaluate('switchView('+JSON.stringify(name)+');window.scrollTo(0,0)');
     assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Overflow '+name+' '+width+' '+theme+' '+collapsed);
    }
    await evaluate('courseView={mode:"overview",week:null,dayIdx:null};switchView("course");window.scrollTo(0,0)');
    if(width===1440||width===375)await shot('course-'+width+'-'+theme+'-'+(collapsed?'icons':'names'));
    if(width<761){
     assert(await evaluate('!document.getElementById("sidebar").getClientRects().length&&document.getElementById("tabnav").getClientRects().length>0'),'Mobile navigation changed');
    }else{
     assert(await evaluate('(()=>{const r=document.getElementById("sidebarToggle").getBoundingClientRect();return r.top>=0&&r.bottom<=innerHeight&&r.width>=44&&r.height>=40;})()'),'Toggle fit '+width);
     assert(await evaluate('document.getElementById("sidebar").getBoundingClientRect().width')===(collapsed?72:width<=1000?196:232),'Sidebar width '+width);
    }
   }
  }
 }
 // Floating Back follows the new sidebar boundary rather than its old position.
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:900,deviceScaleFactor:1,mobile:false});
 for(const collapsed of [false,true]){
  await evaluate('if(document.documentElement.classList.contains("sidebar-compact")!=='+collapsed+')document.getElementById("sidebarToggle").click();courseView={mode:"day",week:50,dayIdx:0,part:1};switchView("course");window.scrollTo(0,800)');await settle();
  assert(await evaluate('(()=>{const back=document.getElementById("floatingBack"),rail=document.getElementById("sidebar").getBoundingClientRect();return !back.hidden&&Math.abs(back.getBoundingClientRect().left-rail.right-18)<=1;})()'),'Floating Back boundary '+collapsed);
  await click('#floatingBack');assert(await evaluate('courseView.mode==="week"&&courseView.week===50'),'Floating Back target');
 }
 // Readability and all overview actions survive the size reduction.
 await evaluate('courseView={mode:"overview",week:null,dayIdx:null};switchView("course");window.scrollTo(0,0)');
 assert(await evaluate('document.querySelectorAll(".phase-list [data-week]").length===52&&!!document.getElementById("goResumeBtn")&&!!document.getElementById("pythonPracticeHome")&&!!document.querySelector(".learning-shortcuts [data-view=reviews]")'),'Missing course controls/content');
 await evaluate('document.getElementById("goResumeBtn").click()');assert(await evaluate('courseView.mode==="day"&&courseView.week===50&&courseView.part===1'),'Exact resume');
 assert(await evaluate('parseFloat(getComputedStyle(document.querySelector(".day-teach .ls-p")).fontSize)>=16'),'Desktop lesson text shrunk');
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
 assert(await evaluate('parseFloat(getComputedStyle(document.querySelector(".day-teach .ls-p")).fontSize)>=15'),'Mobile lesson text shrunk');
 assert.deepEqual(errors,[],'Console errors');
 console.log('PASS: pinned icon/name toggle,14 icon routes,keyboard/persistence,6 widths/2 themes/both states, floating Back realignment, all course actions and readable lesson text; original data and console clean. Size measurements:',JSON.stringify(measurements),'Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

