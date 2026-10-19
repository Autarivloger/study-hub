const fs=require("fs");
const os=require("os");
const path=require("path");
const {spawn}=require("child_process");
const {pathToFileURL}=require("url");

const chromePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-review-"));
const browser=spawn(chromePath,["--headless=new","--disable-gpu","--no-sandbox","--no-first-run","--remote-debugging-port=0","--user-data-dir="+profile,pathToFileURL(path.resolve(__dirname,"..","study-hub.html")).href],{stdio:"ignore"});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
  let port;
  for(let i=0;i<100;i++){const f=path.join(profile,"DevToolsActivePort");if(fs.existsSync(f)){port=Number(fs.readFileSync(f,"utf8").split("\n")[0]);break;}await sleep(100);}
  if(!port)throw Error("Chrome did not start");
  const tabs=await(await fetch("http://127.0.0.1:"+port+"/json/list")).json(),page=tabs.find(x=>x.type==="page");
  const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  let seq=0;const pending=new Map(),errors=[];
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==="Runtime.exceptionThrown"){const d=m.params.exceptionDetails;errors.push((d.exception&&d.exception.description)||d.text);}if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((res,rej)=>{const id=++seq;pending.set(id,{resolve:res,reject:rej});ws.send(JSON.stringify({id,method,params}));});
  const evalJs=async expression=>{const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error((r.exceptionDetails.exception&&r.exceptionDetails.exception.description)||r.exceptionDetails.text);return r.result.value;};
  const assert=(v,m)=>{if(!v)throw Error(m);};
  await send("Runtime.enable");await send("Page.enable");
  for(let i=0;i<50;i++){if(await evalJs("Boolean(window.__studyHubBooted)"))break;await sleep(100);}
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));


  await evalJs(`localStorage.studyHubData_v1=JSON.stringify({notes:[{id:'keep',body:'Keep other notes'}],japanese:{done:{'19.1':'2026-10-01','19.2':'2026-10-02','19.1.core':'2026-10-03'},notes:{'19.1':'Old Day16 note','19.2':'Old Day17 note','19.5.core':'Keep core note'},checks:{},quizScores:{'19.1':75,'19.2':50}}})`);
  await send('Page.reload',{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  await evalJs(`document.querySelector('#modalOverlay').click();document.querySelector('#sidebar [data-view=japanese]').click()`);
  assert(await evalJs(`!document.querySelector('#japaneseBody').textContent.includes('advanced preview')&&!document.querySelector('[data-jp-lesson="19.1"]')&&!document.querySelector('[data-jp-lesson="19.2"]')`),'Home preview was not removed');
  await evalJs(`document.querySelector('[data-jp-week="19"]').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-day-card').length===7`),'Core week day count changed');
  await evalJs(`document.querySelector('[data-jp-lesson="19.5.core"]').click()`);
  assert(await evalJs(`document.querySelector('.jp-contrast-extras').querySelectorAll('[data-jp-lesson]').length===2&&document.querySelector('#jpNotes').value==='Keep core note'`),'Related practice or core note missing');
  for(const id of ['19.1','19.2']){
    await evalJs(`document.querySelector('.jp-contrast-extras [data-jp-lesson="${id}"]').click()`);
    assert(await evalJs(`document.querySelectorAll('.jp-vocab')[0].children.length===10&&(document.querySelectorAll('.jp-vocab').length===${id==='19.1'?2:1})&&(${id==='19.1'?"document.querySelectorAll('.jp-vocab')[1].children.length===10":'true'})&&document.querySelectorAll('.jp-q').length===4&&document.querySelector('#jpNotes').value===${JSON.stringify(id==='19.1'?'Old Day16 note':'Old Day17 note')}`),'Saved content/note missing '+id);
    await evalJs(`document.querySelector('#jpNotes').value=${JSON.stringify('Retained extra '+id)};document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}))`);
    const correct=id==='19.1'?[0,0,0,1]:[0,1,1,0];
    await evalJs(`(${JSON.stringify(correct)}).forEach((a,i)=>document.querySelector('input[name=jpq'+i+'][value="'+a+'"]').click());document.querySelector('[data-jp-quiz]').click()`);
    assert(await evalJs(`document.querySelector('.jp-result').textContent.includes('4 / 4 correct')`),'Extra quiz broken '+id);
    await evalJs(`document.querySelector('.jp-actions [data-jp-lesson="19.5.core"]').click()`);
    assert(await evalJs(`!!document.querySelector('.jp-contrast-extras')&&document.querySelector('#jpNotes').value==='Keep core note'`),'Return to correct parent failed');
  }
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  for(let theme=0;theme<2;theme++){
    await evalJs(`document.querySelector('#themeBtn').click()`);
    assert(await evalJs(`document.documentElement.scrollWidth<=innerWidth+1`),'Parent mobile overflow');
    for(const id of ['19.1','19.2']){
      await evalJs(`document.querySelector('.jp-contrast-extras [data-jp-lesson="${id}"]').click()`);
      assert(await evalJs(`document.documentElement.scrollWidth<=innerWidth+1`),'Extra mobile overflow '+id);
      await evalJs(`document.querySelector('.jp-actions [data-jp-lesson="19.5.core"]').click()`);
    }
  }
  await evalJs(`document.querySelector('#modalOverlay').click();document.querySelector('.jp-contrast-extras').scrollIntoView({block:'center'})`);
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-japanese-extra-practice-mobile.png'),Buffer.from(shot.data,'base64'));
  await send('Page.reload',{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  assert(await evalJs(`(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return d.japanese.notes['19.1']==='Retained extra 19.1'&&d.japanese.notes['19.2']==='Retained extra 19.2'&&d.japanese.quizScores['19.1']===100&&d.japanese.quizScores['19.2']===100&&d.japanese.done['19.1']&&d.japanese.done['19.2']&&d.japanese.done['19.1.core']&&d.notes[0].body==='Keep other notes';})()`),'Refresh changed saved data');
  assert(errors.length===0,'JavaScript errors: '+errors.join('; '));
  console.log('PASS: home preview removed; Week19 Day5 extra lessons and return links; all vocab/kanji/quiz content, old notes/scores/completions and core week structure preserved; mobile light/dark; no JavaScript errors.');
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
