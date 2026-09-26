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

  /* Three old completions exercise the one-time, non-destructive migration. */
  await evalJs(`(()=>{const d=new Date();d.setDate(d.getDate()-10);const iso=d.toISOString();localStorage.studyHubData_v1=JSON.stringify({course:{done:{'1.0':iso},notes:{},practice:{solved:{},attempts:0},partsDone:{}},lessonsDone:{strings:iso},japanese:{done:{'8.1':iso},quizScores:{},notes:{},checks:{}}});sessionStorage.clear();})()`);
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs("Boolean(window.__studyHubBooted)"))break;await sleep(100);}
  assert(await evalJs("Object.keys(JSON.parse(localStorage.studyHubData_v1).reviews.items).length===3"),"Completed lessons did not migrate into reviews");
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).reviews.items).every(x=>x.subject&&x.courseName&&x.lessonName&&x.topic&&x.completedAt&&x.summary&&Array.isArray(x.concepts)&&Array.isArray(x.prompts)&&x.prompts.length&&x.stage===0&&x.nextReview&&Array.isArray(x.history))"),"Review records are incomplete");
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).reviews.items).every(x=>x.nextReview < (()=>{const d=new Date(),y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),a=String(d.getDate()).padStart(2,'0');return y+'-'+m+'-'+a})())"),"Old lessons were not retained as overdue");

  assert(await evalJs("document.querySelector('#view-course .review-hero').textContent.includes('review')"),"Today's Review is not prominent on the homepage");
  await evalJs("document.querySelector('#sidebar [data-view=reviews]').click()");
  assert(await evalJs("document.querySelector('#view-reviews').classList.contains('active') && document.querySelector('.review-count').textContent.includes('3')"),"Review dashboard did not open with due count");
  assert(await evalJs("document.querySelectorAll('.review-calendar .review-cal-day').length===28"),"28-day calendar missing");
  assert(await evalJs("document.querySelectorAll('#reviewSubject option').length===3 && document.querySelectorAll('#reviewStatus option').length===5 && document.querySelectorAll('#reviewDifficulty option').length===5"),"Search filters are incomplete");
  assert(await evalJs("document.querySelectorAll('[data-review-scope]').length===3 && document.querySelectorAll('[data-review-next]').length===2"),"Separate dashboards or next-learning guidance missing");
  await evalJs("document.querySelector('[data-review-scope=japanese]').click()");
  assert(await evalJs("document.querySelector('#view-reviews .review-count').textContent.includes('1')"),"Japanese review dashboard did not separate its queue");
  await evalJs("document.querySelector('[data-review-scope=all]').click()");

  await evalJs("document.querySelector('[data-review-start]').click()");
  assert(await evalJs("!!document.querySelector('.recall-q') && !document.querySelector('.recall-answer')"),"Answer was shown before active recall");
  const firstSubject=await evalJs("document.querySelector('.recall-progress').textContent.includes('Japanese')?'japanese':'python'");
  await evalJs("document.querySelector('[data-review-reveal]').click()");
  assert(await evalJs("!!document.querySelector('.recall-answer') && document.querySelectorAll('[data-grade]').length===4"),"Reveal or difficulty controls missing");
  await evalJs("document.querySelector('[data-grade=forgot]').click()");
  const secondSubject=await evalJs("document.querySelector('.recall-progress').textContent.includes('Japanese')?'japanese':'python'");
  assert(firstSubject!==secondSubject,"Mixed review did not alternate subjects when possible");
  await evalJs("document.querySelector('[data-review-reveal]').click();document.querySelector('[data-grade=hard]').click();document.querySelector('[data-review-reveal]').click();document.querySelector('[data-grade=easy]').click()");
  assert(await evalJs("document.querySelector('#view-reviews .review-hero').textContent.includes('caught up') && !document.querySelector('#view-reviews .recall-q')"),"Session did not return to dashboard");
  assert(await evalJs("(()=>{const a=Object.values(JSON.parse(localStorage.studyHubData_v1).reviews.items);return a.every(x=>x.history.length===1&&x.nextReview>(()=>{const d=new Date(),y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),z=String(d.getDate()).padStart(2,'0');return y+'-'+m+'-'+z})())&&a.some(x=>x.difficulty==='forgot'&&x.stage===0)&&a.some(x=>x.difficulty==='hard')&&a.some(x=>x.difficulty==='easy'&&x.stage===2);})()"),"Adaptive grading did not update stages, dates, and history");
  await evalJs("document.querySelector('[data-review-history]').click()");
  assert(await evalJs("document.querySelector('#modalBox').textContent.includes('Review history') && document.querySelector('#modalBox').textContent.includes('Next review')"),"Per-lesson review history is not visible");
  await evalJs("document.querySelector('#reviewHistoryClose').click()");

  /* A new Python day completion must enroll immediately, not only on reload. */
  await evalJs("document.querySelector('#sidebar [data-view=course]').click();document.querySelector('[data-week=\"1\"]').click();document.querySelectorAll('.day-open')[1].click();document.querySelector('#dayDoneBtn').click()");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).reviews.items['python:day:1.1']"),"New Python completion did not enter reviews");

  /* A new Japanese completion uses the same algorithm and remains separate. */
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-week=\"8\"]').click();document.querySelector('[data-jp-lesson=\"8.2\"]').click();document.querySelector('[data-jp-done]').click()");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).reviews.items['japanese:lesson:8.2']"),"New Japanese completion did not enter reviews");

  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs("Boolean(window.__studyHubBooted)"))break;await sleep(100);}
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).reviews.items).filter(x=>x.history.length).length===3"),"Review history did not survive refresh");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).reviews.migrationVersion===1"),"Migration version missing");

  await evalJs("document.querySelector('#themeBtn').click()");
  assert(await evalJs("document.documentElement.hasAttribute('data-theme')"),"Theme toggle failed with review system installed");
  await send("Emulation.setDeviceMetricsOverride",{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await evalJs("document.querySelector('#tabnav [data-view=reviews]').click()");
  assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1"),"Review dashboard overflows on mobile");
  const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),"studyhub-reviews-mobile.png"),Buffer.from(shot.data,"base64"));
  assert(errors.length===0,"JavaScript errors: "+errors.join("; "));
  console.log("PASS: adaptive Japanese/Python reviews, migration, active recall, mixed queue, history, filters, calendar, refresh, mobile, no JS errors");
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
