// Disposable profile and synthetic storage only.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-gita-profile-')),out=path.join(os.tmpdir(),'studyhub-gita-proof');fs.mkdirSync(out,{recursive:true});
const fixture=path.join(profile,'gita-test.html'),base=pathToFileURL(path.resolve('.')+path.sep).href;
fs.writeFileSync(fixture,fs.readFileSync('study-hub.html','utf8').replace('<head>','<head><base href="'+base+'">').replace('\nboot();\n','window.__courseTestEval=e=>eval(e);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
let localServer;
const watchdog=setTimeout(()=>{browser.kill();console.error('Gita test timed out');process.exit(1);},180000);
async function main(){
 let port;for(let i=0;i<100;i++){const f=path.join(profile,'DevToolsActivePort');if(fs.existsSync(f)){port=Number(fs.readFileSync(f,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port);
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 const pending=new Map(),errors=[];let seq=0;
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timeout: '+method));},20000);pending.set(id,{resolve:v=>{clearTimeout(timer);resolve(v);},reject:e=>{clearTimeout(timer);reject(e);}});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 async function ready(){for(let i=0;i<200;i++){if(await evaluate('Boolean(gitaCurrent?.ready)')){await sleep(80);return;}if(await evaluate('Boolean(document.querySelector("#gitaRetry:not([hidden])"))'))throw Error(await evaluate('document.getElementById("gitaStatus").textContent'));await sleep(80);}throw Error('PDF did not render');}
 const shot=async name=>{await sleep(250);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));};
 await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
 for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('Boolean(window.__studyHubBooted)'));
 if(process.argv.includes('--hosted')){
  // Verify the real service worker, using only an allowlisted local HTTP server.
  const http=require('http'),root=path.resolve('.');
  localServer=http.createServer((req,res)=>{
   const u=new URL(req.url,'http://localhost'),name=decodeURIComponent(u.pathname).replace(/^\/+/,'')||'index.html';
   if(name==='favicon.ico'){res.writeHead(204);return res.end();}
   if(!['index.html','study-hub.html','sw.js','manifest.webmanifest','icon.svg'].includes(name)&&!/^books\/[a-z0-9.-]+$/.test(name)&&!/^vendor\/pdfjs-6\.4\.299\/[a-z0-9.-]+$/.test(name)){res.writeHead(404);return res.end();}
   const target=path.resolve(root,name);if(!target.startsWith(root+path.sep)||!fs.existsSync(target)){res.writeHead(404);return res.end();}
   const ext=path.extname(name),types={'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.svg':'image/svg+xml','.webmanifest':'application/manifest+json','.jpg':'image/jpeg'};
   res.writeHead(200,{'Content-Type':types[ext]||'application/octet-stream','Cache-Control':'no-cache'});
   if(name==='study-hub.html')return res.end(fs.readFileSync('study-hub.html','utf8').replace('\nboot();\n','window.__courseTestEval=e=>eval(e);\nboot();\n'));
   fs.createReadStream(target).pipe(res);
  });
  await new Promise(r=>localServer.listen(0,'127.0.0.1',r));
  await send('Page.navigate',{url:'http://127.0.0.1:'+localServer.address().port+'/study-hub.html'});
  for(let i=0;i<200&&!await evaluate('location.protocol==="http:"&&Boolean(window.__studyHubBooted)&&Boolean(navigator.serviceWorker.controller)');i++)await sleep(80);
  assert(await evaluate('Boolean(navigator.serviceWorker.controller)'),'Service worker active');
  await evaluate('closeModal();switchView("lessons");document.querySelector("[data-yoga-mode=book]").click()');await ready();
  for(let i=0;i<100&&!await evaluate('document.getElementById("gitaOfflineStatus").textContent.includes("Book saved")');i++){await evaluate('gitaOfflineStatus()');await sleep(80);}
  assert(await evaluate('document.getElementById("gitaOfflineStatus").textContent.includes("Book saved")'),'Hosted assets cached');
  await evaluate('gitaRenderPage(456,0)');await ready();
  await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await send('Page.reload',{ignoreCache:true});for(let i=0;i<200&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
  await evaluate('closeModal();switchView("lessons");document.querySelector("[data-yoga-mode=book]").click()');await ready();
  assert.equal(await evaluate('gitaCurrent.page'),456,'Hosted offline resume');
  assert.deepEqual(errors,[]);console.log('PASS: real hosted service-worker caches book/PDF.js; internet disabled; application reloads, original page456 renders and saved place resumes offline.');return;
 }
 await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
 await evaluate('closeModal();DB=applyDefaults({course:{notes:{"1.0":"Keep Python"}},japanese:{notes:{"31.1":"Keep Japanese"}},headNotes:{"yoga:intermediate:1.1|reflection":"Keep Yoga","cyber:9.1|day-notes":"Keep Cyber"},lessonsDone:{"webdev:5.7":"2026-10-20"}});save();switchView("lessons")');
 assert(await evaluate('document.querySelectorAll(".yoga-card").length===7&&!!document.querySelector(".gita-library")&&!!document.querySelector(".gita-daily [lang=ne]")'),'Original Yoga and daily card');
 await evaluate('document.querySelector("[data-yoga-mode=book]").click()');await ready();
 console.log('PDF opened',await evaluate('({page:gitaCurrent.page,pages:GITA_BOOK.pages,version:window.StudyHubPdf.version,status:document.getElementById("gitaStatus").textContent})'));
 await shot('book-first-page');
 if(process.argv.includes('--probe')){console.log('Errors',errors);return;}
 // Remaining end-to-end assertions are below; keep probe available for rendering diagnostics.
 assert(await evaluate('document.querySelector("#gitaPaper canvas").width>200&&!!gitaReadRecord("position")'),'Canvas and initial position');
 await evaluate('document.getElementById("gitaPage").value=127;document.getElementById("gitaGo").click()');await ready();
 assert.equal(await evaluate('gitaCurrent.page'),127);
 await shot('book-verse-2-47');
 // Use native browser mouse events to draw a real underline on the visible paper.
 const pos=await evaluate('(()=>{const r=document.getElementById("gitaPaper").getBoundingClientRect();return{x:r.x+r.width*.2,y:Math.max(250,r.y+170),end:r.x+r.width*.6};})()');
 await evaluate('document.getElementById("gitaPencil").click()');
 await send('Input.dispatchMouseEvent',{type:'mousePressed',x:pos.x,y:pos.y,button:'left',buttons:1,clickCount:1});
 for(let i=1;i<=8;i++)await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pos.x+(pos.end-pos.x)*i/8,y:pos.y+1,button:'left',buttons:1});
 await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:pos.end,y:pos.y+1,button:'left',buttons:0,clickCount:1});
 assert(await evaluate('gitaMarks(127).length===1&&document.querySelectorAll("#gitaInk polyline").length===1'),'Mouse underline saved');
 const points=await evaluate('JSON.stringify(gitaMarks(127)[0].value.points)');
 await evaluate('document.getElementById("gitaUndo").click()');assert.equal(await evaluate('gitaMarks(127).length'),0);
 await evaluate('document.getElementById("gitaRedo").click()');assert.equal(await evaluate('gitaMarks(127).length'),1);
 await evaluate('document.getElementById("gitaZoom").value="1.6";document.getElementById("gitaZoom").dispatchEvent(new Event("change"))');await ready();
 assert.equal(await evaluate('JSON.stringify(gitaMarks(127)[0].value.points)'),points,'Zoom must preserve normalised positions');
 assert(await evaluate('document.querySelector("#gitaInk").getAttribute("viewBox")==="0 0 1 1"'),'Coordinate system');
 await evaluate('document.getElementById("gitaZoom").value="1";document.getElementById("gitaZoom").dispatchEvent(new Event("change"))');await ready();
 await evaluate('(()=>{const p=document.getElementById("gitaPaper").getBoundingClientRect();window.scrollBy(0,p.height*.25)})()');await sleep(450);
 const offset=await evaluate('gitaReadRecord("position").offset');assert(offset>.1,'Automatic reading offset');
 await evaluate('document.getElementById("gitaBookmark").click()');
 assert(await evaluate('gitaReadRecord("bookmark").page===127&&gitaReadRecord("bookmark").offset>.1'),'Bookmark');
 await evaluate('document.getElementById("gitaNext").click()');await ready();assert.equal(await evaluate('gitaCurrent.page'),128);
 await evaluate('document.getElementById("gitaBookmarkGo").click()');await ready();
 assert(await evaluate('gitaCurrent.page===127&&gitaMarks(127).length===1'),'Bookmark return and overlay');
 // Existing heading-note component saves literal page notes.
 await evaluate('(()=>{const b=document.querySelector("#gitaPageNotes [data-hn]");b.click();const t=document.querySelector("#gitaPageNotes textarea");t.value="My Gita note <b>literal</b>";t.dispatchEvent(new Event("input",{bubbles:true}));})()');await sleep(550);
 assert.equal(await evaluate('DB.headNotes[GITA_PREFIX+"page-note:127"]'),'My Gita note <b>literal</b>');
 await evaluate('switchView("course")');assert(!await evaluate('Boolean(gitaCurrent)'),'Reader cleanup on navigation');
 await evaluate('switchView("lessons")');await ready();assert(await evaluate('gitaCurrent.page===127&&gitaMarks(127).length===1'),'Resume reader after leaving');
 // All chapter links and daily references are within the verified original PDF.
 assert(await evaluate('GITA_BOOK.chapters.length===18&&GITA_BOOK.daily.every(d=>d.page>=1&&d.page<=GITA_BOOK.pages)&&new Set(GITA_BOOK.daily.map(d=>d.ref)).size===GITA_BOOK.daily.length'),'Reference coverage');
 await evaluate('document.getElementById("gitaStudyGuide").open=true');
 assert.equal(await evaluate('document.querySelectorAll("#gitaStudyGuide details").length'),18);
 await evaluate('document.getElementById("gitaChapter").value="1218"'); // Nonexistent option must not navigate.
 assert.equal(await evaluate('gitaCurrent.page'),127);
 await evaluate('document.getElementById("gitaChapter").value="411";document.getElementById("gitaChapter").dispatchEvent(new Event("change"))');await ready();assert.equal(await evaluate('gitaCurrent.page'),411);
 await evaluate('gitaRenderPage(-999,0)');await ready();assert.equal(await evaluate('gitaCurrent.page'),1);assert(await evaluate('document.getElementById("gitaPrevious").disabled'));
 await evaluate('gitaRenderPage(999999,0)');await ready();assert.equal(await evaluate('gitaCurrent.page'),1296);assert(await evaluate('document.getElementById("gitaNext").disabled'));
 // Real backup/export plus merge/replace and reload. Newer Gita positions win; ordinary notes retain existing rules.
 await evaluate('gitaRenderPage(127,.25)');await ready();
 await evaluate('window.__gitaBlob=null;const original=URL.createObjectURL;URL.createObjectURL=b=>{window.__gitaBlob=b;return original(b)};document.getElementById("exportBtn").click()');
 const backup=await evaluate('window.__gitaBlob.text()');assert(Object.keys(JSON.parse(backup).headNotes).some(k=>k.includes('|mark:')));
 await evaluate('gitaBookLeave();Object.keys(DB.headNotes).filter(k=>k.startsWith(GITA_PREFIX)).forEach(k=>delete DB.headNotes[k]);save();(()=>{const f=new File(['+JSON.stringify(backup)+'],"gita-backup.json",{type:"application/json"}),d=new DataTransfer();d.items.add(f);const i=document.getElementById("importFile");i.files=d.files;i.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<50&&!await evaluate('Boolean(document.getElementById("impMerge"))');i++)await sleep(80);
 await evaluate('document.getElementById("impMerge").click()');assert(await evaluate('gitaMarks(127).length===1&&gitaReadRecord("bookmark").page===127'),'Merge restored marks/bookmark');
 await evaluate('(()=>{const p=gitaReadRecord("position");mergeIntoDB({headNotes:{[GITA_PREFIX+"position"]:JSON.stringify({page:456,offset:.2,updatedAt:p.updatedAt+100})}})})()');
 assert.equal(await evaluate('gitaReadRecord("position").page'),456,'Cross-device newer position');
 await evaluate('confirmMerge('+backup+');document.getElementById("impReplace").click()');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 await evaluate('closeModal();switchView("lessons");document.querySelector("[data-yoga-mode=book]").click()');await ready();
 assert(await evaluate('gitaCurrent.page===127&&gitaMarks(127).length===1&&DB.headNotes[GITA_PREFIX+"page-note:127"].includes("literal")'),'Replace and offline reload');
 assert(await evaluate('DB.course.notes["1.0"]==="Keep Python"&&DB.japanese.notes["31.1"]==="Keep Japanese"&&DB.headNotes["yoga:intermediate:1.1|reflection"]==="Keep Yoga"&&DB.headNotes["cyber:9.1|day-notes"]==="Keep Cyber"&&DB.lessonsDone["webdev:5.7"]'),'Previous data preserved');
 // Check responsive layout, control sizes and both themes with real PDF rendering.
 for(const [width,height] of [[1480,900],[768,1024],[375,812],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});await sleep(300);await ready();
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Overflow '+width);
   assert(await evaluate('[...document.querySelectorAll(".gita-pencil-tools button")].filter(b=>b.getClientRects().length).every(b=>b.getBoundingClientRect().height>=44)'),'Touch sizes');
   await shot('book-'+width+'-'+theme);
  }
 }
 const touch=await evaluate('(()=>{const r=document.getElementById("gitaPaper").getBoundingClientRect(),t=document.getElementById("gitaToolbar").getBoundingClientRect();return{x:r.x+r.width*.15,y:Math.min(innerHeight-100,Math.max(t.bottom+30,r.y+200)),end:r.x+r.width*.6};})()');
 await evaluate('document.getElementById("gitaPencil").click()');
 const beforeTouch=await evaluate('gitaMarks(127).length');
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:touch.x,y:touch.y,id:1}]});
 for(let i=1;i<=5;i++)await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:touch.x+(touch.end-touch.x)*i/5,y:touch.y,id:1}]});
 await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 assert.equal(await evaluate('gitaMarks(127).length'),beforeTouch+1,'Touch underline');
 await evaluate('document.getElementById("gitaPencil").click()');
 assert(await evaluate('getComputedStyle(document.getElementById("gitaInk")).pointerEvents==="none"'),'Reading mode restores normal scrolling');
 assert.deepEqual(errors,[],'JavaScript errors');
 console.log('PASS: original PDF renders offline; pencil/undo/redo/zoom; automatic place/bookmark/resume; chapter/page bounds; page notes; backup merge/replace/reload; newer synced records; all old data;4widths/both themes; no JS errors. Proof:',out);
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();if(localServer)localServer.close();});
