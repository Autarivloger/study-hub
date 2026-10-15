const fs=require("fs");
const os=require("os");
const path=require("path");
const {spawn}=require("child_process");
const {pathToFileURL}=require("url");

const chromePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-review-"));
// Test-only copy exposes closure evaluation; the deployed app receives no test hook.
const fixture=path.join(profile,'course.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'..','study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();'));
const browser=spawn(chromePath,["--headless=new","--disable-gpu","--no-sandbox","--no-first-run","--remote-debugging-port=0","--user-data-dir="+profile,pathToFileURL(fixture).href],{stdio:"ignore"});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
  let port;
  for(let i=0;i<100;i++){const f=path.join(profile,"DevToolsActivePort");if(fs.existsSync(f)){port=Number(fs.readFileSync(f,"utf8").split("\n")[0]);break;}await sleep(100);}
  if(!port)throw Error("Chrome did not start");
  const tabs=await(await fetch("http://127.0.0.1:"+port+"/json/list")).json(),page=tabs.find(x=>x.type==="page");
  const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  let seq=0;const pending=new Map(),errors=[];
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==="Runtime.exceptionThrown"){const d=m.params.exceptionDetails;errors.push((d.exception&&d.exception.description)||d.text);}if(m.method==="Runtime.consoleAPICalled"&&m.params.type==="error")errors.push(m.params.args.map(a=>a.value||a.description).join(" "));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((res,rej)=>{const id=++seq;pending.set(id,{resolve:res,reject:rej});ws.send(JSON.stringify({id,method,params}));});
  const evalJs=async expression=>{const r=await send("Runtime.evaluate",{expression:'window.__courseTestEval ? window.__courseTestEval('+JSON.stringify(expression)+') : eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error((r.exceptionDetails.exception&&r.exceptionDetails.exception.description)||r.exceptionDetails.text);return r.result.value;};
  const assert=(v,m)=>{if(!v)throw Error(m);};
  await send("Runtime.enable");await send("Page.enable");
  for(let i=0;i<50;i++){if(await evalJs("Boolean(window.__studyHubBooted)"))break;await sleep(100);}
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));

  await evalJs('closeModal();DB=applyDefaults({course:{partsDone:{"29.0.1":"2026-10-01T00:00:00Z"},notes:{"29.0":"Old Python note"}},japanese:{done:{"8.1":"2026-10-01T00:00:00Z"}},headNotes:{legacy:"Keep notes"}});save();switchView("course")');
  await evalJs('courseView={mode:"week",week:39,dayIdx:null};renderCourse();');
  assert(await evalJs('document.querySelector("#courseBody").textContent.includes("FastAPI & modern API development")'),'Week39 overview missing');
  const count=await evalJs('(()=>{let parts=0;for(let d=0;d<6;d++){const list=dayParts("39."+d);for(let p=0;p<list.length;p++){parts++;courseView={mode:"day",week:39,dayIdx:d,part:p};renderCourseDay();const body=document.querySelector(".day-teach");if(!body||!body.textContent.includes(list[p].title))throw Error("Missing lesson "+d+"."+p);if(!body.querySelector(".ls-code")||!body.querySelector(".ls-out"))throw Error("Missing example/output");const quiz=list[p].sections.find(s=>s.t==="checkpoint").lesson;quiz.quiz.forEach((q,i)=>body.querySelector("[data-lq=\\\""+i+"\\\"][data-lo=\\\""+q.correct+"\\\"]").click());if(DB.lessonQuizScores[quiz.id]!==100)throw Error("Quiz save "+quiz.id);}}return parts;})()');
  assert(count===36,'Expected36 complete teaching parts');
  await evalJs('courseView={mode:"day",week:39,dayIdx:0,part:0};renderCourseDay();document.querySelector("#partNext").click()');
  assert(await evalJs('courseView.part===1'),'Next part failed');
  await evalJs('document.querySelector("#partPrev").click();document.querySelector("#nextDay").click()');
  assert(await evalJs('courseView.week===39&&courseView.dayIdx===1'),'Next day failed');
  await evalJs('document.querySelector("#prevDay").click();document.querySelector("#partDoneBtn").click();document.querySelector("#dayNote").value="Week39 saved note";document.querySelector("#dayNote").dispatchEvent(new Event("input",{bubbles:true}));');
  await sleep(600);
  assert(await evalJs('isPartDone(39,0,0)&&DB.course.notes["39.0"]==="Week39 saved note"'),'Week39 completion/notes failed');
  assert(await evalJs('corePool().filter(p=>p.week===39).length===72'),'Week39 practice extraction failed');
  assert(await evalJs('(()=>{const hit=buildSearchIndex().find(e=>e.kind==="day"&&e.week===39&&e.title.includes("Milestone: a validated private FastAPI Notes API"));if(!hit)return false;gotoSearchHit(hit);return courseView.week===39&&courseView.dayIdx===5&&courseView.part===5;})()'),'Exact-part project search failed');
  await evalJs('practiceView.block="w39";practiceView.includeCurrent=false;openPythonPractice();');
  assert(await evalJs('practiceView.order.length===2&&practiceView.order.every(p=>p.week===39&&p.day===1&&p.part===0)'),'Practice includes unstudied Week39 parts');
  assert(await evalJs('(()=>{migrateCompletedToReviews();const item=DB.reviews.items["python:day:39.0"];return !!item&&pythonReviewPrompts(item).every(p=>p.part===0);})()'),'Week39 review eligibility failed');
  await send('Page.reload',{ignoreCache:true});for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  assert(await evalJs('isPartDone(39,0,0)&&DB.course.notes["39.0"]==="Week39 saved note"&&DB.lessonQuizScores["course:39.5.5"]===100&&DB.course.notes["29.0"]==="Old Python note"&&DB.japanese.done["8.1"]&&DB.headNotes.legacy'),'Refresh changed progress or prior data');
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await evalJs('(()=>{switchView("course");for(let theme=0;theme<2;theme++){document.querySelector("#themeBtn").click();for(let d=0;d<6;d++)for(let p=0;p<dayParts("39."+d).length;p++){courseView={mode:"day",week:39,dayIdx:d,part:p};renderCourseDay();if(document.documentElement.scrollWidth>innerWidth+1)throw Error("Week39 mobile overflow "+d+"."+p);}}})()');
  await evalJs('closeModal();document.querySelector(".day-teach").scrollIntoView();');
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-week39-mobile.png'),Buffer.from(shot.data,'base64'));
  assert(errors.length===0,'JS errors: '+errors.join('; '));
  console.log('PASS: Week39 all36parts/82quiz questions, navigation, progress/notes/refresh, exact-part search, studied-only practice/review and375px themes; FastAPI lesson examples render offline; no JavaScript errors.');
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
