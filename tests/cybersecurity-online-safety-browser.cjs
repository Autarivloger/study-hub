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
    closeModal();sessionStorage.setItem('studyHubReviewNotice','1');
    DB=applyDefaults({headNotes:{'cyber:8.1|day-notes':'Keep roadmap notes',legacy:'Keep old notes'},
      lessonsDone:{old_lesson:'2026-10-01T00:00:00Z'},
      course:{partsDone:{'40.0.0':'2026-10-01T00:00:00Z'},notes:{'40.0':'Keep Python note'}},
      japanese:{done:{'8.1':'2026-10-01T00:00:00Z'}},
      quizzes:[{id:'old-quiz',name:'Saved quiz',questions:[],lastScore:67}]});
    save();switchView('quiz');
    if(document.querySelectorAll('[data-cyber-week]').length!==8)throw Error('Existing weeks missing');
    document.querySelector('[data-safety-open]').click();
  });
  assert(await run(function(){return document.querySelectorAll('[data-safety-lesson]').length===7&&document.querySelector('#cybersecurityBody h1').textContent==='Online Safety'&&Object.keys(DB.lessonsDone).length===1;}),'Folder/provenance/progress failed');
  for(let lesson=1;lesson<=7;lesson++){
    await evalJs('document.querySelector(\'[data-safety-lesson="'+lesson+'"]\').click()');
    assert(await run(function(){
      const body=document.querySelector('#cybersecurityBody'),lesson=CYBER_ONLINE_SAFETY.find(l=>l.number===cyberPage.lesson);
      return body.querySelector('h1').textContent===lesson.title&&body.querySelectorAll('.safety-exercise').length===1&&
        body.querySelector('.safety-self-check').open===false&&body.textContent.includes(lesson.objective)&&
        body.querySelectorAll('[data-safety-complete]').length===2;
    }),'Lesson/exercise/self-check failed '+lesson);
    await run(function(){
      const body=document.querySelector('#cybersecurityBody');
      body.querySelector('.safety-self-check').open=true;
      body.querySelector('#safetyNotes [data-hn]').click();
      const input=body.querySelector('#safetyNotes textarea');
      input.value='Safety Lesson '+cyberPage.lesson+' note <b>literal</b>';
      input.dispatchEvent(new Event('input',{bubbles:true}));
      body.querySelector('[data-safety-complete="read"]').click();
      if(!input.isConnected||!body.querySelector('.safety-self-check').open)throw Error('Progress reset reading/input state');
      if(DB.lessonsDone[safetyProgressKey(cyberPage.lesson,'exercise')])throw Error('Reading marked exercise complete');
      if(cyberPage.lesson===2)body.querySelector('[data-safety-complete="exercise"]').click();
    });
    await sleep(650);
    assert(await evalJs('DB.headNotes["cyber:online-safety:'+lesson+'|lesson-notes"]==="Safety Lesson '+lesson+' note <b>literal</b>"'),'Lesson note save failed');
    await run(function(){document.querySelector('[data-safety-folder]').click();});
  }
  assert(await run(function(){return document.querySelector('#cybersecurityBody').textContent.includes('7 of 7 read · 1 exercise completed');}),'Folder progress totals incorrect');
  await run(function(){
    document.querySelector('[data-safety-lesson="1"]').click();
    if(!document.querySelector('[data-safety-step="-1"]').disabled)throw Error('First Previous enabled');
    document.querySelector('[data-safety-step="1"]').click();
    if(cyberPage.lesson!==2)throw Error('Next lesson failed');
    document.querySelector('[data-safety-step="-1"]').click();
    if(cyberPage.lesson!==1)throw Error('Previous lesson failed');
    document.querySelector('[data-safety-complete="read"]').click();
    if(DB.lessonsDone[safetyProgressKey(1,'read')])throw Error('Undo read failed');
    document.querySelector('[data-safety-complete="read"]').click();
    document.querySelector('[data-safety-home]').click();
    document.querySelector('[data-cyber-week="8"]').click();document.querySelector('[data-cyber-day="1"]').click();
    if(!document.querySelector('.cyber-teaching'))throw Error('Existing roadmap broken');
    document.querySelector('#cyberOldQuizzes').click();
    if(!document.querySelector('#quizList').textContent.includes('Saved quiz'))throw Error('Legacy quizzes missing');
    document.querySelector('#cyberBack').click();
    const backup=JSON.parse(JSON.stringify(DB));DB=applyDefaults({});mergeIntoDB(backup);save();
    if(!DB.lessonsDone[safetyProgressKey(2,'exercise')]||DB.headNotes['cyber:online-safety:7|lesson-notes']!=='Safety Lesson 7 note <b>literal</b>')throw Error('New data merge failed');
  });
  await send('Page.reload',{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  assert(await run(function(){return DB.lessonsDone[safetyProgressKey(2,'exercise')]&&DB.lessonsDone.old_lesson&&DB.headNotes['cyber:8.1|day-notes']==='Keep roadmap notes'&&DB.course.notes['40.0']==='Keep Python note'&&isPartDone(40,0,0)&&DB.japanese.done['8.1']&&DB.headNotes.legacy==='Keep old notes';}),'Refresh lost old/new data');
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await run(function(){
    closeModal();switchView('quiz');
    for(let theme=0;theme<2;theme++){
      document.querySelector('#themeBtn').click();
      cyberPage.mode='safety-folder';renderCybersecurityRoadmap();
      if(document.documentElement.scrollWidth>innerWidth+1)throw Error('Folder overflow');
      for(let lesson=1;lesson<=7;lesson++){
        cyberPage.mode='safety-lesson';cyberPage.lesson=lesson;renderCybersecurityRoadmap();
        document.querySelector('.safety-self-check').open=true;
        if(document.documentElement.scrollWidth>innerWidth+1)throw Error('Lesson overflow '+lesson);
      }
    }
    if(!document.querySelector('[data-safety-step="1"]').disabled)throw Error('Last Next enabled');
    cyberPage.mode='safety-folder';renderCybersecurityRoadmap();document.querySelector('#cybersecurityBody').scrollIntoView();
  });
  let shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-online-safety-folder-mobile.png'),Buffer.from(shot.data,'base64'));
  await run(function(){cyberPage.mode='safety-lesson';cyberPage.lesson=2;renderCybersecurityRoadmap();document.querySelector('.safety-teaching').scrollIntoView();});
  shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-online-safety-lesson-mobile.png'),Buffer.from(shot.data,'base64'));
  assert(errors.length===0,'JavaScript errors: '+errors.join('; '));
  console.log('PASS: Online Safety folder/seven lessons, isolated notes/read/exercise saves/undo/merge/refresh, reveal, previous/next, existing roadmap/quizzes, mobile themes and no JavaScript errors.');
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
