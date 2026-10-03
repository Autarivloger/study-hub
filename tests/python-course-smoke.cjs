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
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==="Runtime.exceptionThrown"){const d=m.params.exceptionDetails;errors.push((d.exception&&d.exception.description)||d.text);}if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((res,rej)=>{const id=++seq;pending.set(id,{resolve:res,reject:rej});ws.send(JSON.stringify({id,method,params}));});
  const evalJs=async expression=>{const r=await send("Runtime.evaluate",{expression:'window.__courseTestEval ? window.__courseTestEval('+JSON.stringify(expression)+') : eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error((r.exceptionDetails.exception&&r.exceptionDetails.exception.description)||r.exceptionDetails.text);return r.result.value;};
  const assert=(v,m)=>{if(!v)throw Error(m);};
  await send("Runtime.enable");await send("Page.enable");
  for(let i=0;i<50;i++){if(await evalJs("Boolean(window.__studyHubBooted)"))break;await sleep(100);}
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));


  assert(await evalJs('LESSONS.length===0 && LEGACY_PYTHON_LESSONS.length===8'), 'Lessons not migrated');
  await evalJs('switchView("lessons");renderLessons()');
  assert(await evalJs('document.querySelectorAll(".lesson-card").length===0 && document.querySelector("#openPythonCourse")'), 'Lessons not empty');
  const rendered=await evalJs('(()=>{let count=0;switchView("course");for(const key of Object.keys(DAY_TEACH)){const [w,d]=key.split(".").map(Number);for(let p=0;p<dayParts(key).length;p++){courseView={mode:"day",week:w,dayIdx:d,part:p};renderCourseDay();if(!document.querySelector(".day-teach"))throw Error("Missing teaching "+key);count++;}}return count;})()');
  assert(rendered>=114,'Not all days rendered');
  await evalJs('courseView={mode:"day",week:1,dayIdx:0,part:0};renderCourseDay();document.querySelector("[data-lo=\\"1\\"]").click()');
  assert(await evalJs('DB.lessonQuizScores["course:1.0"]===100 && !document.querySelector("[data-quiz-why]").hidden'), 'Course quiz did not save/explain');
  await evalJs('DB.course.done["9.2"]=nowISO();DB.course.practice.solved["1.5.1"]=nowISO();DB.lessonsDone.strings=nowISO();DB.lessonQuizScores.strings=67;DB.headNotes["lstrings|every-method-is-a-function-on-a-value"]= "Keep my note";save();');
  const id=await evalJs('corePool().find(p=>p.id==="1.5.1")?.week');assert(id>=9,'Moved practice kept in Week 1');
  assert(await evalJs('(()=>{const p=dayParts("9.2").findIndex(p=>p.optional);togglePartDone(9,2,p);return !!DB.course.done["9.2"];})()'),'Supplement erased old day completion');
  await evalJs('activeLessonId="strings";renderLessons()');assert(await evalJs('courseView.week===2 && courseView.dayIdx===3'),'Legacy Resume did not redirect to Course');
  await evalJs('courseView={mode:"day",week:1,dayIdx:5,part:0};renderCourseDay();document.querySelector("[data-python-path]").click()');
  assert(await evalJs('courseView.week>1 && courseView.part>0'),'Prerequisite link did not open exact part');
  const hit=await evalJs('(()=>{const h=buildSearchIndex().find(e=>e.kind==="day" && e.part>0 && e.text.includes("def "));if(!h)throw Error("Missing moved search result");gotoSearchHit(h);return courseView.part===h.part;})()');assert(hit,'Search opened wrong part');
  await evalJs('courseView={mode:"day",week:1,dayIdx:0,part:0};renderCourseDay();practiceView.block="all";practiceView.size=0;practiceView.readyOnly=true;practiceView.order=null;renderCorePractice()');
  assert(await evalJs('practiceView.order.every(p=>p.week===1 && p.day===1)'), 'Practice jumps ahead');
  await evalJs('document.querySelector("#pracReady").click()');assert(await evalJs('practiceView.order.some(p=>p.week>1)'), 'Exploration filter cannot be disabled');
  await evalJs('courseView={mode:"day",week:2,dayIdx:3,part:0};renderCourseDay();document.querySelector("#dayNote").value="Saved day note";document.querySelector("#dayNote").dispatchEvent(new Event("input",{bubbles:true}));');await sleep(600);
  await send('Page.reload',{ignoreCache:true});for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  assert(await evalJs('DB.lessonQuizScores.strings===67 && DB.lessonsDone.strings && DB.course.notes["2.3"]==="Saved day note" && DB.course.practice.solved["1.5.1"] && DB.lessonQuizScores["course:1.0"]===100'),'Saved data failed reload');
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await evalJs('document.querySelector("#themeBtn").click();switchView("course");courseView={mode:"day",week:1,dayIdx:5,part:0};renderCourseDay()');
  assert(await evalJs('document.documentElement.scrollWidth<=window.innerWidth+1'), 'Mobile Course overflow');
  await evalJs('switchView("lessons");renderLessons()');assert(await evalJs('document.documentElement.scrollWidth<=window.innerWidth+1'),'Mobile Lessons overflow');
  await evalJs('switchView("course");courseView={mode:"day",week:2,dayIdx:3,part:0};renderCourseDay()');
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-python-course-mobile.png'),Buffer.from(shot.data,'base64'));
  assert(errors.length===0,'JS errors: '+errors.join('; '));console.log('PASS: '+rendered+' course parts, empty Lessons, quizzes, stable moved practice, existing progress, saved notes, Resume, exact-part links/search, practice filter, refresh, mobile/dark, no JS errors');ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());

