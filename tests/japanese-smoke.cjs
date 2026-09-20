const fs = require("fs");
const os = require("os");
const path = require("path");
const {spawn} = require("child_process");
const {pathToFileURL} = require("url");

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "studyhub-jp-"));
const browser = spawn(chromePath, [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
  "--remote-debugging-port=0", "--user-data-dir=" + profile,
  pathToFileURL(path.resolve(__dirname, "..", "study-hub.html")).href
], {stdio:"ignore"});
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function main(){
  let port;
  for(let i=0;i<100;i++){
    const active = path.join(profile, "DevToolsActivePort");
    if(fs.existsSync(active)){ port=Number(fs.readFileSync(active,"utf8").split("\n")[0]); break; }
    await sleep(100);
  }
  if(!port) throw new Error("Chrome debugging port did not start");
  const tabs = await (await fetch("http://127.0.0.1:"+port+"/json/list")).json();
  const page = tabs.find(x=>x.type==="page");
  if(!page) throw new Error("No browser page");
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
  let nextId=0;
  const pending=new Map(), errors=[];
  ws.onmessage = ev=>{
    const msg=JSON.parse(ev.data);
    if(msg.method==="Runtime.exceptionThrown") errors.push(msg.params.exceptionDetails.text);
    if(msg.id && pending.has(msg.id)){
      const p=pending.get(msg.id);pending.delete(msg.id);
      if(msg.error) p.reject(new Error(JSON.stringify(msg.error))); else p.resolve(msg.result);
    }
  };
  function send(method,params={}){
    return new Promise((resolve,reject)=>{
      const id=++nextId;pending.set(id,{resolve,reject});
      ws.send(JSON.stringify({id,method,params}));
    });
  }
  async function evalJs(expression){
    const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
    if(r.exceptionDetails) throw new Error(r.exceptionDetails.text);
    return r.result.value;
  }
  function assert(value,message){if(!value)throw new Error(message);}
  await send("Runtime.enable");
  await send("Page.enable");
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("window.__studyHubBooted"),"App did not boot");
  assert(await evalJs("document.querySelectorAll('#tabnav [data-view]').length === 11"),"Navigation lost a tab");
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click()");
  assert(await evalJs("document.querySelector('#view-japanese').classList.contains('active')"),"Japanese view did not open");
  assert(await evalJs("document.querySelectorAll('.jp-week-card').length === 36"),"Roadmap is incomplete");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-desktop.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('[data-jp-week=\"1\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length === 6"),"Week 1 lessons missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-q').length === 2"),"Lesson quiz missing");
  await evalJs("document.querySelector('[data-jp-cards]').click();document.querySelector('[data-jp-cards]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.deckId==='jp-vocabulary-v1').length === 3"),"Vocabulary cards missing or duplicated");
  await evalJs("document.querySelector('#jpNotes').value='My Japanese practice';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}))");
  await evalJs("document.querySelector('[data-jp-check=read]').click()");
  await evalJs("document.querySelector('input[name=jpq0][value=\"1\"]').click();document.querySelector('input[name=jpq1][value=\"1\"]').click()");
  await evalJs("document.querySelector('[data-jp-quiz]').click()");
  assert(await evalJs("document.querySelector('.jp-result').textContent.includes('2 / 2 correct')"),"Quiz score wrong");
  await evalJs("document.querySelector('[data-jp-done]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1'] !== undefined"),"Completion did not save");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['1.1'] === 100"),"Quiz did not save");
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.1'] === 'My Japanese practice'"),"Note did not survive reload");
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-week=\"1\"]').click();document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  assert(await evalJs("document.querySelector('#jpNotes').value === 'My Japanese practice'"),"Note did not render after reload");
  const answers=[[1,1],[1,0],[1,0],[1,2],[1,0],[1,0],[1,1],[0,0],[1,1],[1,0],[1,2],[1,0]];
  for(let i=0;i<12;i++){
    await evalJs("document.querySelector('input[name=jpq0][value=\""+answers[i][0]+"\"]').click();document.querySelector('input[name=jpq1][value=\""+answers[i][1]+"\"]').click();document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('2 / 2 correct')"),"Quiz failed for lesson "+(i+1));
    if(i<11) await evalJs("document.querySelector('.jp-actions [data-jp-lesson]:last-child').click()");
  }
  assert(await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19.1\"]') === null"),"Core path unexpectedly jumps to advanced preview");
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-hero [data-jp-lesson=\"1.2\"]') !== null"),"Continue path changed after core completion");
  await evalJs("document.querySelector('[data-jp-lesson=\"19.1\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-panel h3').length >= 10"),"Imported grammar sections missing");
  assert(await evalJs("document.body.textContent.includes('Natural conversation') && document.body.textContent.includes('Write and compare')"),"Imported conversation or writing practice missing");
  assert(await evalJs("document.querySelectorAll('.jp-vocab')[0].children.length === 10 && document.querySelectorAll('.jp-vocab')[1].children.length === 10"),"Day 16 vocabulary or kanji missing");
  assert(await evalJs("document.querySelectorAll('.jp-q').length === 4"),"Day 16 quiz missing");
  await evalJs("document.querySelector('#jpNotes').value='Contrast needs review';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}))");
  await evalJs("document.querySelector('[data-jp-cards]').click();document.querySelector('[data-jp-cards]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.id.startsWith('jp-19.1-')).length === 10"),"Imported flashcards missing or duplicated");
  await evalJs("[0,0,0,1].forEach((a,i)=>document.querySelector('input[name=jpq'+i+'][value=\"'+a+'\"]').click());document.querySelector('[data-jp-quiz]').click()");
  assert(await evalJs("document.querySelector('.jp-result').textContent.includes('4 / 4 correct')"),"Day 16 quiz failed");
  await evalJs("document.querySelector('[data-jp-done]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.done['19.1'] !== undefined"),"Day 16 completion not saved");
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19.2\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-panel h3').length >= 9 && document.querySelectorAll('.jp-q').length === 4"),"Day 17 content missing");
  await evalJs("[0,1,1,0].forEach((a,i)=>document.querySelector('input[name=jpq'+i+'][value=\"'+a+'\"]').click());document.querySelector('[data-jp-quiz]').click()");
  assert(await evalJs("document.querySelector('.jp-result').textContent.includes('4 / 4 correct')"),"Day 17 quiz failed");
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.notes['19.1'] === 'Contrast needs review'"),"Imported note did not survive reload");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['19.2'] === 100"),"Day 17 score did not survive reload");
  await evalJs("document.querySelector('#sidebar [data-view=course]').click()");
  assert(await evalJs("document.querySelector('#view-course').classList.contains('active')"),"Python course navigation failed");
  await evalJs("document.querySelector('#sidebar [data-view=typing]').click()");
  assert(await evalJs("document.querySelector('#view-typing').classList.contains('active')"),"Typing navigation failed");
  await evalJs("document.querySelector('#themeBtn').click()");
  assert(await evalJs("document.documentElement.hasAttribute('data-theme')"),"Theme did not toggle");
  await send("Emulation.setDeviceMetricsOverride",{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await evalJs("document.querySelector('#tabnav [data-view=japanese]').click()");
  assert(await evalJs("document.querySelector('#view-japanese').classList.contains('active')"),"Mobile Japanese navigation failed");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile layout overflows horizontally");
  await evalJs("document.querySelector('[data-jp-week=\"1\"]').click();document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile lesson overflows horizontally");
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-lesson=\"19.1\"]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile advanced lesson overflows horizontally");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-advanced-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"1\"]').click();document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("(()=>{const data={notes:[{id:'old-note',title:'Old note',body:'preserved'}],course:{done:{'1.0':'2024-01-01'}}};const f=new File([JSON.stringify(data)],'old-backup.json',{type:'application/json'});const dt=new DataTransfer();dt.items.add(f);const input=document.querySelector('#importFile');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));})()");
  for(let i=0;i<30;i++){
    if(await evalJs("!!document.querySelector('#impMerge')")) break;
    await sleep(100);
  }
  assert(await evalJs("!!document.querySelector('#impMerge')"),"Import dialog did not open");
  await evalJs("document.querySelector('#impMerge').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).notes.some(x=>x.id==='old-note')"),"Old backup did not merge");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1']"),"Import erased Japanese progress");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['19.1']"),"Import erased imported lesson progress");
  await evalJs("document.querySelector('#exportBtn').click()");
  for(let i=0;i<20;i++){
    if(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).lastBackup")) break;
    await sleep(100);
  }
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).lastBackup"),"Export did not finish");
  assert(await evalJs("!!document.querySelector('#exportBtn') && !!document.querySelector('#importBtn')"),"Backup controls missing");
  await evalJs("document.querySelector('#syncBtn').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Sync dialog overflows on mobile");
  assert(await evalJs("!document.querySelector('#syRemember').checked"),"New tokens should default to session-only storage");
  assert(await evalJs("document.querySelector('#syTok').getAttribute('value') === null"),"Token should not appear in HTML markup");
  await evalJs("document.querySelector('#syTok').value='synthetic-test-token-123456';document.querySelector('#syClose').click()");
  assert(await evalJs("!JSON.parse(localStorage.studyHubSync).token"),"Session-only token leaked into persistent storage");
  assert(await evalJs("sessionStorage.studyHubSyncSessionToken === 'synthetic-test-token-123456'"),"Session token was not available for sync");
  await evalJs("window.__syncBody='';window.fetch=async(url,opts)=>{const method=opts.method;if(method==='POST'){window.__syncBody=opts.body;return new Response(JSON.stringify({id:'0123456789abcdef0123456789abcdef'}),{status:201,headers:{'Content-Type':'application/json'}});}if(method==='GET'){const remote={notes:[{id:'remote-note',title:'From another phone',body:'Hello'}]};return new Response(JSON.stringify({files:{'study-hub-progress.json':{content:JSON.stringify({data:remote})}}}),{status:200,headers:{'Content-Type':'application/json'}});}return new Response(JSON.stringify({id:'0123456789abcdef0123456789abcdef'}),{status:200,headers:{'Content-Type':'application/json'}});}");
  await evalJs("document.querySelector('#syncBtn').click();document.querySelector('#syPush').click()");
  for(let i=0;i<30;i++){
    if(await evalJs("JSON.parse(localStorage.studyHubSync).gistId === '0123456789abcdef0123456789abcdef'")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubSync).gistId === '0123456789abcdef0123456789abcdef'"),"First Push did not create a Gist");
  assert(await evalJs("window.__syncBody.includes('old-note') && !window.__syncBody.includes('synthetic-test-token-123456')"),"Push payload lost notes or contained token");
  await evalJs("document.querySelector('#syPull').click()");
  for(let i=0;i<30;i++){
    if(await evalJs("JSON.parse(localStorage.studyHubData_v1).notes.some(x=>x.id==='remote-note')")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).notes.some(x=>x.id==='remote-note')"),"Pull did not merge remote writing");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1']"),"Pull erased local progress");
  await evalJs("window.fetch=async()=>new Response('{}',{status:403,headers:{'Content-Type':'application/json'}});document.querySelector('#syncBtn').click();document.querySelector('#syPush').click()");
  for(let i=0;i<30;i++){
    if(await evalJs("document.querySelector('#syStatus').textContent.includes('Gists')")) break;
    await sleep(100);
  }
  assert(await evalJs("document.querySelector('#syStatus').textContent.includes('Gists')"),"403 did not show an actionable error");
  await evalJs("document.querySelector('#syClose').click();localStorage.studyHubSync=JSON.stringify({token:'synthetic-legacy-token-123456',gistId:'0123456789abcdef0123456789abcdef',auto:false});sessionStorage.removeItem('studyHubSyncSessionToken')");
  await evalJs("document.querySelector('#syncBtn').click()");
  assert(await evalJs("document.querySelector('#syRemember').checked"),"Existing saved token stopped working");
  await evalJs("document.querySelector('#syRemember').click();document.querySelector('#syClose').click()");
  assert(await evalJs("!JSON.parse(localStorage.studyHubSync).token && sessionStorage.studyHubSyncSessionToken === 'synthetic-legacy-token-123456'"),"Unchecking Remember did not remove persistent token");
  await evalJs("document.querySelector('#syncBtn').click();document.querySelector('#syForget').click()");
  assert(await evalJs("!JSON.parse(localStorage.studyHubSync).token && !sessionStorage.studyHubSyncSessionToken"),"Forget did not clear token");
  assert(await evalJs("JSON.parse(localStorage.studyHubSync).gistId === '0123456789abcdef0123456789abcdef'"),"Forget erased Gist ID");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1']"),"Forget erased writing");
  assert(errors.length===0,"JavaScript errors: "+errors.join("; "));
  console.log("PASS: lessons, notes, progress, mobile, dark mode, backup, mock Gist Push/Pull, session-only token, legacy token, Forget, 403 guidance, no JS exceptions");
  ws.close();
}
main().catch(err=>{console.error(err);process.exitCode=1;}).finally(()=>{browser.kill();});
