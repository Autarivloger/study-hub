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

  // Real mouse input: plain reading text supports drag selection; reveal
  // labels act as controls, not selectable reading text.
  await evalJs('jpPage={mode:"lesson",week:1,lesson:"1.1"};switchView("japanese");renderJapanese();');
  const reading=await evalJs('(()=>{const e=document.querySelector("#jp-day1-reading .jp-reading");e.scrollIntoView({block:"center"});const text=[...e.childNodes].find(n=>n.nodeType===3&&n.textContent.trim());const r=document.createRange();r.setStart(text,0);r.setEnd(text,Math.min(12,text.length));const box=r.getClientRects()[0];return {x:box.x+2,y:box.y+box.height/2,end:box.right-2};})()');
  await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:reading.x,y:reading.y});
  await send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',buttons:1,clickCount:1,x:reading.x,y:reading.y});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',buttons:0,clickCount:1,x:reading.x,y:reading.y});
  assert(await evalJs('window.getSelection().toString()===""'),'A single reading click selected text');
  await send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',buttons:1,clickCount:1,x:reading.x,y:reading.y});
  for(let step=1;step<=8;step++)await send('Input.dispatchMouseEvent',{type:'mouseMoved',button:'left',buttons:1,x:reading.x+(reading.end-reading.x)*step/8,y:reading.y});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',buttons:0,clickCount:1,x:reading.end,y:reading.y});
  assert(await evalJs('window.getSelection().toString().length>3 && jpPage.lesson==="1.1"'),'Mouse drag failed to select Japanese reading');
  for(let attempt=0;attempt<6;attempt++){
    const point=await evalJs('(()=>{const e=document.querySelector("#jp-day1-kanji summary");e.scrollIntoView({block:"center"});const b=e.getBoundingClientRect();return {x:b.x+b.width/2,y:b.y+b.height/2};})()');
    await send('Input.dispatchMouseEvent',{type:'mousePressed',button:'left',buttons:1,clickCount:1,...point});
    await send('Input.dispatchMouseEvent',{type:'mouseReleased',button:'left',buttons:0,clickCount:1,...point});
    assert(await evalJs('document.querySelector("#jp-day1-kanji details").open')===(attempt%2===0),'On/Kun single-click toggle failed '+attempt);
    assert(await evalJs('getComputedStyle(document.querySelector("#jp-day1-kanji summary")).userSelect==="none"'),'Reveal label remains selectable');
  }


  assert(await evalJs('LESSONS.length===0 && LEGACY_PYTHON_LESSONS.length===8'), 'Lessons not migrated');
  await evalJs('switchView("lessons");renderLessons()');
  assert(await evalJs('document.querySelectorAll(".lesson-card").length===0 && document.querySelectorAll(".yoga-card").length===7'), 'Yoga replacement or legacy course migration failed');
  const rendered=await evalJs('(()=>{let count=0;switchView("course");for(const key of Object.keys(DAY_TEACH)){const [w,d]=key.split(".").map(Number);for(let p=0;p<dayParts(key).length;p++){courseView={mode:"day",week:w,dayIdx:d,part:p};renderCourseDay();if(!document.querySelector(".day-teach"))throw Error("Missing teaching "+key);count++;}}return count;})()');
  assert(rendered>=114,'Not all days rendered');
  if(await evalJs('Boolean(DAY_TEACH["21.0"])')){
    await evalJs('switchView("course");courseView={mode:"day",week:21,dayIdx:0,part:0};renderCourseDay();document.querySelector("#partNext").click()');
    assert(await evalJs('courseView.part===1'),'Week21 next part failed');
    await evalJs('document.querySelector("#partPrev").click();document.querySelector("#nextDay").click()');
    assert(await evalJs('courseView.week===21 && courseView.dayIdx===1'),'Week21 next day failed');
    await evalJs('document.querySelector("#prevDay").click()');
    assert(await evalJs('courseView.dayIdx===0'),'Week21 previous day failed');
    await evalJs('(()=>{for(let d=0;d<6;d++)for(let p=0;p<dayParts("21."+d).length;p++){courseView={mode:"day",week:21,dayIdx:d,part:p};renderCourseDay();const quiz=dayParts("21."+d)[p].sections.find(s=>s.t==="checkpoint").lesson;quiz.quiz.forEach((q,i)=>document.querySelector(".day-teach [data-lq=\\""+i+"\\"][data-lo=\\""+q.correct+"\\"]").click());if(DB.lessonQuizScores[quiz.id]!==100)throw Error("Week21 quiz saving "+quiz.id);}})()');
    await evalJs('courseView={mode:"day",week:21,dayIdx:0,part:0};renderCourseDay();document.querySelector("#partDoneBtn").click();document.querySelector("#dayNote").value="Week21 saved note";document.querySelector("#dayNote").dispatchEvent(new Event("input",{bubbles:true}));save()');
    assert(await evalJs('isPartDone(21,0,0)'),'Week21 part completion failed');
  }
  if(await evalJs('Boolean(DAY_TEACH["22.0"])')){
    await evalJs('switchView("course");courseView={mode:"day",week:22,dayIdx:0,part:0};renderCourseDay();document.querySelector("#partNext").click()');
    assert(await evalJs('courseView.part===1'),'Week22 next part failed');
    await evalJs('document.querySelector("#partPrev").click();document.querySelector("#nextDay").click()');
    assert(await evalJs('courseView.week===22 && courseView.dayIdx===1'),'Week22 next day failed');
    await evalJs('document.querySelector("#prevDay").click()');
    assert(await evalJs('courseView.dayIdx===0'),'Week22 previous day failed');
    await evalJs('(()=>{for(let d=0;d<6;d++)for(let p=0;p<dayParts("22."+d).length;p++){courseView={mode:"day",week:22,dayIdx:d,part:p};renderCourseDay();const quiz=dayParts("22."+d)[p].sections.find(s=>s.t==="checkpoint").lesson;quiz.quiz.forEach((q,i)=>document.querySelector(".day-teach [data-lq=\\\""+i+"\\\"][data-lo=\\\""+q.correct+"\\\"]").click());if(DB.lessonQuizScores[quiz.id]!==100)throw Error("Week22 quiz saving "+quiz.id);}})()');
    await evalJs('courseView={mode:"day",week:22,dayIdx:0,part:0};renderCourseDay();document.querySelector("#partDoneBtn").click();document.querySelector("#dayNote").value="Week22 saved note";document.querySelector("#dayNote").dispatchEvent(new Event("input",{bubbles:true}));save()');
    assert(await evalJs('isPartDone(22,0,0)'),'Week22 part completion failed');
    assert(await evalJs('corePool().filter(p=>p.week===22).length===48'),'Week22 practice pool failed');
    assert(await evalJs('(()=>{const hit=buildSearchIndex().find(e=>e.kind==="day"&&e.week===22&&e.text.includes("Lookbehind"));if(!hit)return false;gotoSearchHit(hit);return courseView.week===22&&courseView.part===hit.part;})()'),'Week22 search exact-part navigation failed');
  }
  if(await evalJs('Boolean(DAY_TEACH["20.0"])')){
    await evalJs('courseView={mode:"day",week:20,dayIdx:0,part:0};renderCourseDay();document.querySelector("[data-lo]").click()');
    assert(await evalJs('DB.lessonQuizScores["course:20.0.0"]===100'),'Week 20 quiz did not save');
  }
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
  if(await evalJs('Boolean(DAY_TEACH["21.0"])'))assert(await evalJs('isPartDone(21,0,0) && DB.lessonQuizScores["course:21.0.0"]===100 && DB.course.notes["21.0"]==="Week21 saved note"'),'Week21 progress/quiz/note failed reload');
  if(await evalJs('Boolean(DAY_TEACH["22.0"])'))assert(await evalJs('isPartDone(22,0,0) && DB.lessonQuizScores["course:22.0.0"]===100 && DB.course.notes["22.0"]==="Week22 saved note"'),'Week22 progress/quiz/note failed reload');
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  if(await evalJs('Boolean(DAY_TEACH["22.0"])'))await evalJs('(()=>{switchView("course");for(let theme=0;theme<2;theme++){document.querySelector("#themeBtn").click();for(let d=0;d<6;d++)for(let p=0;p<dayParts("22."+d).length;p++){courseView={mode:"day",week:22,dayIdx:d,part:p};renderCourseDay();if(document.documentElement.scrollWidth>window.innerWidth+1)throw Error("Week22 mobile overflow "+d+"."+p);}}})()');
  if(await evalJs('Boolean(DAY_TEACH["21.0"])'))await evalJs('(()=>{switchView("course");for(let theme=0;theme<2;theme++){document.querySelector("#themeBtn").click();for(let d=0;d<6;d++)for(let p=0;p<dayParts("21."+d).length;p++){courseView={mode:"day",week:21,dayIdx:d,part:p};renderCourseDay();if(document.documentElement.scrollWidth>window.innerWidth+1)throw Error("Week21 mobile overflow "+d+"."+p);}}})()');
  if(await evalJs('Boolean(DAY_TEACH["20.0"])'))await evalJs('(()=>{switchView("course");for(let d=0;d<6;d++)for(let p=0;p<dayParts("20."+d).length;p++){courseView={mode:"day",week:20,dayIdx:d,part:p};renderCourseDay();if(document.documentElement.scrollWidth>window.innerWidth+1)throw Error("Week 20 overflow "+d+"."+p);}})()');
  await evalJs('document.querySelector("#themeBtn").click();switchView("course");courseView={mode:"day",week:1,dayIdx:5,part:0};renderCourseDay()');
  assert(await evalJs('document.documentElement.scrollWidth<=window.innerWidth+1'), 'Mobile Course overflow');
  await evalJs('switchView("lessons");renderLessons()');assert(await evalJs('document.documentElement.scrollWidth<=window.innerWidth+1'),'Mobile Lessons overflow');
  await evalJs('switchView("course");courseView={mode:"day",week:2,dayIdx:3,part:0};renderCourseDay()');
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-python-course-mobile.png'),Buffer.from(shot.data,'base64'));
  assert(errors.length===0,'JS errors: '+errors.join('; '));console.log('PASS: '+rendered+' course parts, Yoga tab replacement, quizzes, stable moved practice, existing progress, saved notes, Resume, exact-part links/search, practice filter, refresh, mobile/dark, no JS errors');ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());

