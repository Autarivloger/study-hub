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
    if(msg.method==="Runtime.exceptionThrown"){
      const e=msg.params.exceptionDetails;
      errors.push((e.exception && e.exception.description) || (e.text+" at "+e.url+":"+e.lineNumber));
    }
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
    if(r.exceptionDetails) throw new Error((r.exceptionDetails.exception && r.exceptionDetails.exception.description) || r.exceptionDetails.text);
    return r.result.value;
  }
  function assert(value,message){if(!value)throw new Error(message);}
  async function furiganaCoverage(){
    return evalJs(`(()=>{const roots=[...document.querySelectorAll('.jp-jp,.jp-reading,.jp-pattern,p[lang=ja],.jp-q legend,.jp-choice,.jp-rule-card [lang=ja],.jp-panel>p:not(.jp-muted)')];const bad=[];for(const root of roots){const walk=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;while(node=walk.nextNode()){if(node.parentElement.closest('ruby'))continue;if(/[\\u3400-\\u9fff々]/.test(node.data))bad.push(node.data)}}const voc=[...document.querySelectorAll('.jp-vocab')][0],kan=[...document.querySelectorAll('.jp-vocab')][1];return {bad:bad.slice(0,100),vocab:!!voc&&[...voc.children].every(x=>!!x.querySelector('ruby rt')),kanji:!!kan&&[...kan.children].every(x=>!!x.querySelector('.jp-kanji-readings'))};})()`);
  }
  await send("Runtime.enable");
  await send("Page.enable");
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));
  assert(await evalJs("document.querySelectorAll('#tabnav [data-view]').length === 12"),"Navigation lost a tab");

  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-week=\"28\"]').click();document.querySelector('[data-jp-lesson=\"28.1\"]').click()");
  if(await evalJs("localStorage.getItem('studyHubJapaneseFurigana')!=='1'"))await evalJs("document.querySelector('[data-jp-furigana]').click()");
  for(let day=1;day<=7;day++){
    if(day>1)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"28."+day+"\"]').click()");
    const f=await furiganaCoverage();assert(f.bad.length===0&&f.vocab&&f.kanji,'Furigana Day '+day+': '+JSON.stringify(f));
  }
  console.log('PASS: Week 28 all seven days, complete visible Furigana coverage and kanji readings');
  ws.close();
}
main().catch(err=>{console.error(err);process.exitCode=1;}).finally(()=>browser.kill());
