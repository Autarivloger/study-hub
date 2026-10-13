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
  const run=fn=>evalJs('('+fn.toString()+')()');
  await run(function(){
    const old=new Date();old.setDate(old.getDate()-12);window.__learnedAt=old.toISOString();
    DB=applyDefaults({course:{done:{"1.0":window.__learnedAt},partsDone:{"28.0.1":window.__learnedAt,"29.0.3":window.__learnedAt},
      notes:{"1.0":"Keep old day notes"},practice:{solved:{"starter:1.0":true,"1.5.1":true},attempts:7}},
      headNotes:{legacy:"Keep heading notes"},japanese:{done:{"8.1":window.__learnedAt}},
      lastSeen:{kind:"day",week:29,dayIdx:2,part:2,at:nowISO()}});
    migrateCompletedToReviews();
    const item=DB.reviews.items["python:day:28.0"];item.stage=3;item.nextReview="2000-01-01";
    item.history=[{at:"2000-01-01T00:00:00Z",date:"2000-01-01",rating:"good",fromStage:2,toStage:3,nextReview:"2000-01-08"}];
    window.__oldSchedule=JSON.stringify([item.stage,item.nextReview,item.history,item.completedAt]);
    reviewEnrollPythonDay(28,0,nowISO());
    save();
  });
  assert(await run(function(){const x=DB.reviews.items["python:day:28.0"];return JSON.stringify([x.stage,x.nextReview,x.history,x.completedAt])===window.__oldSchedule;}),'Re-enrollment reset old schedules/history');
  assert(await run(function(){return !!DB.reviews.items["python:day:28.0"]&&!DB.course.done["28.0"]&&reviewItems().filter(x=>x.subject==="python").length===3;}),'Partial completion did not enter reviews');
  assert(await run(function(){const p=pythonReviewPrompts(DB.reviews.items["python:day:28.0"]);return p.length>3&&p.every(x=>x.part===1)&&p.some(x=>x.kind==="exercise")&&p.some(x=>x.kind==="debug");}),'Partial-day reviews include unseen parts or lack exercises');
  assert(await run(function(){return !pythonReviewSourceEligible({subject:"python",sourceType:"python-day",sourceId:"29.2"});}),'Opening a lesson enrolled it as completed');
  assert(await run(function(){
    const parts=dayParts("9.2"),optional=parts.findIndex(p=>p.optional);if(optional<0)throw Error("Missing existing optional supplement");
    DB.course.done["9.2"]=window.__learnedAt;
    const excluded=!pythonStudiedParts(9,2,false).some(p=>p.part===optional);
    DB.course.partsDone["9.2."+optional]=window.__learnedAt;
    const included=pythonStudiedParts(9,2,false).some(p=>p.part===optional);
    delete DB.course.done["9.2"];delete DB.course.partsDone["9.2."+optional];
    return excluded&&included;
  }),'Old completed days incorrectly included unread optional supplements');

  await run(function(){switchView("reviews");reviewStart([DB.reviews.items["python:day:29.0"]]);});
  assert(await run(function(){return document.querySelector(".recall-type").textContent.includes("Exercise")&&!document.querySelector(".recall-answer");}),'Fresh review did not start with a real hidden-solution exercise');
  const first=await run(function(){return reviewPickPrompt(DB.reviews.items["python:day:29.0"]).key;});
  await run(function(){document.querySelector("[data-review-another]").click();});
  assert(await run(function(){return reviewPickPrompt(DB.reviews.items["python:day:29.0"]).key;})!==first,'Another question repeated the same prompt');
  const chosen=await run(function(){return reviewPickPrompt(DB.reviews.items["python:day:29.0"]).key;});
  await run(function(){const t=document.querySelector("#reviewAttempt");t.value="my recalled answer";t.dispatchEvent(new Event("input",{bubbles:true}));document.querySelector("[data-review-reveal]").click();});
  assert(await run(function(){return document.querySelector("#reviewAttempt").value==="my recalled answer"&&!!document.querySelector(".recall-answer");}),'Reveal erased the answer draft');
  await run(function(){document.querySelector("[data-grade=good]").click();reviewStart([DB.reviews.items["python:day:29.0"]]);});
  assert(await run(function(){const x=DB.reviews.items["python:day:29.0"];return x.history[0].questionId;})===chosen,'Grading did not record the question actually asked');
  assert(await run(function(){return reviewPickPrompt(DB.reviews.items["python:day:29.0"]).key;})!==chosen,'Next review immediately repeated the last graded question');
  // Every current question is used before repeating; skipping a card does not grade it.
  assert(await run(function(){
    const x=DB.reviews.items["python:day:29.0"],size=pythonReviewPrompts(x).length;
    for(let i=1;i<size;i++){const p=reviewPickPrompt(x);reviewGrade(x,"good");reviewView.pythonOffsets={};}
    return new Set(x.history.map(h=>h.questionId)).size===size;
  }),'Questions repeated before the available learned pool was covered');
  await run(function(){reviewStart([DB.reviews.items["python:day:28.0"]]);});
  for(let i=0;i<25;i++){
    if(await run(function(){return !!document.querySelector("[data-review-option]");}))break;
    await run(function(){document.querySelector("[data-review-another]").click();});
  }
  assert(await run(function(){return !!document.querySelector("[data-review-option]");}),'No interactive lesson quiz reachable');
  await run(function(){
    const p=reviewPickPrompt(DB.reviews.items["python:day:28.0"]),wrong=(p.correct+1)%p.options.length;
    document.querySelector('[data-review-option="'+wrong+'"]').click();document.querySelector("[data-review-reveal]").click();
  });
  assert(await run(function(){return document.querySelectorAll(".recall-card .ls-quiz-opt.correct").length===1&&document.querySelectorAll(".recall-card .ls-quiz-opt.wrong").length===1;}),'Quiz feedback did not show chosen wrong/correct options');
  await run(function(){document.querySelector("[data-review-source]").click();});
  assert(await run(function(){return courseView.week===28&&courseView.dayIdx===0&&courseView.part===1;}),'Review source link did not open the exact completed part');

  await run(function(){
    DB.lastSeen={kind:"day",week:29,dayIdx:2,part:2,at:nowISO()};
    document.querySelector("#coursePracticeBtn").click();
    document.querySelector("#pracSize").value="0";document.querySelector("#pracSize").dispatchEvent(new Event("change"));
  });
  assert(await run(function(){return document.querySelector("#courseBody h2").textContent.includes("Python Practice")&&practiceView.block==="all";}),'Python Practice entry/default mixed scope missing');
  assert(await run(function(){return practiceView.order.some(p=>p.week===29&&p.day===3&&p.part===2)&&practiceView.order.every(p=>pythonStudiedParts(p.week,p.day-1,true).some(s=>s.part===p.part));}),'Current-part scope contains later/unseen parts');
  await run(function(){document.querySelector("#pracCurrent").click();});
  assert(await run(function(){return practiceView.order.every(p=>pythonStudiedParts(p.week,p.day-1,false).some(s=>s.part===p.part))&&!practiceView.order.some(p=>p.week===29&&p.day===3); }),'Completed-only scope includes an uncompleted current day');
  await run(function(){document.querySelector("#pracBlock").value="w28";document.querySelector("#pracBlock").dispatchEvent(new Event("change"));});
  assert(await run(function(){return practiceView.order.length===2&&practiceView.order.every(p=>p.week===28&&p.day===1&&p.part===1); }),'Week filter did not use the completed part only');
  const oldFirst=await run(function(){return practiceView.order[0].id;});
  await run(function(){document.querySelector("#pracNew").click();});
  assert(await run(function(){return practiceView.order[0].id;})!==oldFirst,'Shuffle repeated the first exercise with alternatives available');
  assert(await run(function(){
    const button=document.querySelector("#courseBody [data-sol]"),box=document.querySelector("#courseBody #solB"+button.dataset.sol);
    const hidden=box.hidden;button.click();
    const shown=!box.hidden&&box.textContent.includes(practiceView.order[0].sol.code.trim());
    button.click();return hidden&&shown&&box.hidden;
  }),'Practice solution reveal/hide did not display the actual worked code');
  await run(function(){
    const input=document.querySelector("[data-practice-attempt]");
    window.__attemptKey=input.dataset.practiceAttempt;
    input.value="print('my saved attempt')";input.dispatchEvent(new Event("input",{bubbles:true}));
    window.__solvedId=document.querySelector("[data-solveid]").dataset.solveid;
    document.querySelector("[data-solveid]").click();
  });
  await sleep(600);
  assert(await run(function(){return DB.headNotes[window.__attemptKey]==="print('my saved attempt')"&&DB.course.practice.solved[window.__solvedId]&&DB.course.practice.solved["1.5.1"]&&DB.course.practice.attempts===8;}),'Attempt/solved saving damaged previous progress');
  await run(function(){document.querySelector("#pracUnsolved").click();});
  assert(await run(function(){return practiceView.order.length===1&&!practiceView.order.some(p=>DB.course.practice.solved[p.id]);}),'Only-unsolved filter includes a solved exercise');
  await run(function(){
    const p=practiceView.order[0];window.__sourceExpected=[p.week,p.day-1,p.part];
    document.querySelector("[data-practice-source]").click();
  });
  assert(await run(function(){return JSON.stringify([courseView.week,courseView.dayIdx,courseView.part])===JSON.stringify(window.__sourceExpected); }),'Practice source link lost its part');
  // New single-part ticks enroll immediately, and un-ticks hide the item without deleting history.
  await run(function(){togglePartDone(28,1,2);});
  assert(await run(function(){return reviewItems().some(x=>x.id==="python:day:28.1")&&!DB.course.done["28.1"]; }),'New partial-day completion was not enrolled');
  await run(function(){reviewGrade(DB.reviews.items["python:day:28.1"],"hard");togglePartDone(28,1,2);});
  assert(await run(function(){return !reviewItems().some(x=>x.id==="python:day:28.1")&&DB.reviews.items["python:day:28.1"].history.length===1; }),'Un-ticking a part left unlearned questions active or deleted history');
  await run(function(){togglePartDone(28,1,2);});
  assert(await run(function(){return DB.reviews.items["python:day:28.1"].history.length===1; }),'Re-completion reset history');
  // Export/import actual UI with fictional data, including the new existing-key attempts.
  await run(function(){
    const original=URL.createObjectURL;URL.createObjectURL=function(blob){window.__learningBackup=blob;return original(blob);};
    document.querySelector("#exportBtn").click();
  });
  const backup=await run(async function(){return await window.__learningBackup.text();});
  assert(JSON.parse(backup).course.partsDone["28.0.1"],'Backup omitted completed parts');
  await run(function(){DB=applyDefaults({headNotes:{local:"Local note survives"},course:{partsDone:{"27.0.0":"2000-01-01T00:00:00Z"}}});save();});
  await evalJs('('+function(data){
    const dt=new DataTransfer();dt.items.add(new File([data],"learning-backup.json",{type:"application/json"}));
    const input=document.querySelector("#importFile");input.files=dt.files;input.dispatchEvent(new Event("change",{bubbles:true}));
  }.toString()+')('+JSON.stringify(backup)+')');
  for(let i=0;i<40;i++){if(await run(function(){return !!document.querySelector("#impMerge");}))break;await sleep(100);}
  await run(function(){document.querySelector("#impMerge").click();});
  assert(await run(function(){return DB.course.partsDone["28.0.1"]&&DB.course.partsDone["27.0.0"]&&DB.headNotes.local&&DB.headNotes.legacy&&DB.course.practice.attempts===8&&Object.keys(DB.headNotes).some(k=>k.startsWith("python-practice|"))&&DB.reviews.items["python:day:29.0"].history.some(h=>h.questionId); }),'Merge import lost part flags, attempts, notes or question history');
  assert(await run(function(){
    const incoming=JSON.parse(JSON.stringify(DB)),id="python:day:28.0";
    const a={at:"2001-01-01T00:00:00Z",date:"2001-01-01",rating:"good",nextReview:"2001-01-08",questionId:"fixture-question-A"};
    DB.reviews.items[id].history.push(a);
    incoming.reviews.items[id].history.push(Object.assign({},a,{questionId:"fixture-question-B"}));
    mergeIntoDB(incoming);
    return DB.reviews.items[id].history.some(h=>h.questionId==="fixture-question-A")&&DB.reviews.items[id].history.some(h=>h.questionId==="fixture-question-B");
  }),'Sync collapsed different questions with the same timestamp/rating');
  await evalJs('confirmMerge('+backup+');document.querySelector("#impReplace").click()');
  assert(await run(function(){return DB.course.partsDone["28.0.1"]&&DB.course.notes["1.0"]==="Keep old day notes"&&DB.course.practice.solved["1.5.1"]&&DB.japanese.done["8.1"]; }),'Replace import lost existing learning data');
  const reloadAttemptKey=await run(function(){
    practiceView.block="w28";practiceView.unsolvedOnly=false;openPythonPractice();
    const input=document.querySelector("[data-practice-attempt]");
    input.value="instant reload draft";
    input.dispatchEvent(new Event("input",{bubbles:true}));
    return input.dataset.practiceAttempt;
  });
  await send("Page.reload",{ignoreCache:true});for(let i=0;i<50;i++){if(await evalJs("window.__studyHubBooted"))break;await sleep(100);}
  assert(await evalJs('DB.headNotes['+JSON.stringify(reloadAttemptKey)+']==="instant reload draft"'), 'Immediate refresh lost a practice draft during the debounce window');
  assert(await run(function(){return DB.course.partsDone["28.0.1"]&&Object.keys(DB.headNotes).some(k=>k.startsWith("python-practice|"))&&DB.reviews.items["python:day:29.0"].history.some(h=>h.questionId); }),'Refresh lost saved practice/review data');
  await send("Emulation.setDeviceMetricsOverride",{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await run(function(){openPythonPractice();sessionStorage.removeItem("studyHubReviewNotice");showReviewNotice();});
  assert(await run(function(){return !document.querySelector("#reviewLater");}),'Review reminder interrupted active practice');
  await run(function(){
    for(let theme=0;theme<2;theme++){
      document.querySelector("#themeBtn").click();
      courseView={mode:"overview",week:null,dayIdx:null};switchView("course");renderCourse();
      if(document.documentElement.scrollWidth>innerWidth+1)throw Error("Course entry mobile overflow");
      document.querySelector("#pythonPracticeHome").click();practiceView.block="w29";practiceView.size=5;practiceView.order=null;renderCorePractice();
      if(document.documentElement.scrollWidth>innerWidth+1)throw Error("Practice mobile overflow");
      switchView("reviews");reviewView.mode="dashboard";renderReviews();
      if(document.documentElement.scrollWidth>innerWidth+1)throw Error("Review dashboard mobile overflow");
      reviewStart([DB.reviews.items["python:day:29.0"]]);document.querySelector("[data-review-reveal]").click();
      if(document.documentElement.scrollWidth>innerWidth+1)throw Error("Review answer mobile overflow");
    }
  });
  const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-python-review-mobile.png"),Buffer.from(shot.data,"base64"));
  await run(function(){openPythonPractice();});
  const practiceShot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-python-practice-mobile.png"),Buffer.from(practiceShot.data,"base64"));
  assert(errors.length===0,"JavaScript errors: "+errors.join("; "));
  console.log("PASS: studied-part-only reviews/practice, variety/nonrepeat, code/quiz feedback, exact-part links, partial enrollment/history, shuffle, saved attempts/solved flags, actual backup/import merge+replace, refresh and mobile themes; no JS errors.");
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());

