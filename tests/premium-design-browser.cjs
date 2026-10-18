// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-design-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-design-profile-'));
const fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=expression=>eval(expression);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const p=path.join(profile,'DevToolsActivePort');if(fs.existsSync(p)){port=Number(fs.readFileSync(p,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome startup');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const shot=async name=>{await sleep(120);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));};
 await send('Runtime.enable');await send('Page.enable');
 for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('Boolean(window.__studyHubBooted)'),'Boot');
 if(!before){
  await evaluate('closeModal();courseView={mode:"overview",week:null,dayIdx:null};switchView("course");document.getElementById("goResumeBtn").click()');
  assert(await evaluate('courseView.mode==="day"&&courseView.week===1&&courseView.dayIdx===0'),'Fresh learner resume must open first day directly');
 }
 await evaluate('closeModal();DB=applyDefaults({course:{done:{"1.0":"2026-10-18","1.1":"2026-10-18"},partsDone:{"50.0.0":"2026-10-18"},notes:{"50.0":"Keep my study note"}},headNotes:{legacy:"Keep heading notes"},lastSeen:{kind:"day",week:50,dayIdx:0,part:1,title:"Concurrency & parallelism",at:"2026-10-18T12:00:00Z"}});save();courseView={mode:"overview",week:null,dayIdx:null};switchView("course")');
 for(const [width,height] of [[1440,1000],[375,812]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.setAttribute("data-theme",'+JSON.stringify(theme)+');courseView={mode:"overview",week:null,dayIdx:null};switchView("course");window.scrollTo(0,0)');
   await shot('course-'+width+'-'+theme);
  }
 }
 if(before){console.log('Baseline screenshots:',out);return;}
 const sections=['course','japanese','quiz','reviews','typing','timer','flashcards','todo','lessons','journal','wisdom','liked','games'];
 for(const [width,height] of [[1440,1000],[1024,768],[768,1024],[375,812],[320,568]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  await send('Emulation.setTouchEmulationEnabled',{enabled:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.setAttribute("data-theme",'+JSON.stringify(theme)+')');
   for(const section of sections){
    await evaluate('switchView('+JSON.stringify(section)+');window.scrollTo(0,0)');
    const layout=await evaluate('({width:innerWidth,scroll:document.documentElement.scrollWidth,header:document.getElementById("topbar").getBoundingClientRect().bottom})');
    assert(layout.scroll<=layout.width+1,section+' overflow '+width+' '+theme+' '+JSON.stringify(layout));
    assert(await evaluate('!!document.querySelector("#view-'+section+'.active")'),'View activated');
   }
  }
  await evaluate('document.querySelector("#workspaceTools summary").click()');
  const menu=await evaluate('(()=>{const r=document.querySelector(".workspace-menu").getBoundingClientRect();return {left:r.left,right:r.right,bottom:r.bottom,height:innerHeight,width:innerWidth};})()');
  assert(menu.left>=0&&menu.right<=menu.width+1&&menu.bottom<=menu.height+1,'Tools fit '+width);
  assert(await evaluate('["exportBtn","importBtn","syncBtn","transferBtn","diagBtn"].every(id=>document.getElementById(id).getBoundingClientRect().height>=40)'),'Backup and sync touch targets');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});
  assert(await evaluate('!document.getElementById("workspaceTools").open&&document.activeElement===document.querySelector("#workspaceTools summary")'),'Tools Escape and focus');
 }
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await evaluate('document.documentElement.setAttribute("data-theme","light");courseView={mode:"overview",week:null,dayIdx:null};switchView("course");document.querySelector("#goResumeBtn").click()');
 assert(await evaluate('courseView.mode==="day"&&courseView.week===50&&courseView.part===1'),'Resume exact location');
 assert(await evaluate('DB.course.notes["50.0"]==="Keep my study note"&&DB.headNotes.legacy==="Keep heading notes"'),'Saved notes unchanged');
 await evaluate('window.scrollTo(0,0)');await shot('lesson-desktop');
 await evaluate('document.querySelector("#searchBtn").click()');assert(await evaluate('overlay.classList.contains("open")&&!!document.getElementById("searchInput")'),'Search reachable');await evaluate('closeModal()');
 await evaluate('document.querySelector("#workspaceTools summary").click();document.querySelector("#syncBtn").click()');assert(await evaluate('overlay.classList.contains("open")&&!document.getElementById("workspaceTools").open'),'Sync opens and tools close');await evaluate('closeModal()');
 for(const section of ['japanese','todo','games']){await evaluate('switchView('+JSON.stringify(section)+');window.scrollTo(0,0)');await shot(section+'-desktop');}
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
 await evaluate('courseView={mode:"day",week:50,dayIdx:0,part:1};switchView("course");window.scrollTo(0,0)');await shot('lesson-mobile');
 await evaluate('document.querySelector("#workspaceTools summary").click()');await shot('tools-mobile');
 assert.deepEqual(errors,[],'Browser errors');
 console.log('PASS: 13 sections at 5 widths in both themes; tools, keyboard dismissal/focus, search, sync, exact resume and preserved notes. Screenshots:',out);
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{ws?.close();browser.kill();});
