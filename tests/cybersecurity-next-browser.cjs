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
  assert(await evalJs('CYBERSECURITY_ROADMAP.length===16'), 'Expanded roadmap missing');
  await run(function(){
    closeModal();sessionStorage.setItem('studyHubReviewNotice','1');
    DB=applyDefaults({headNotes:{'cyber:7.1|day-notes':'Keep Week7 notes',legacy:'Keep heading notes'},
      course:{partsDone:{'30.0.0':'2026-10-01T00:00:00Z'},notes:{'30.0':'Keep Python notes'}},
      japanese:{done:{'8.1':'2026-10-01T00:00:00Z'}},
      quizzes:[{id:'cyber-legacy',name:'Saved quiz',questions:[{id:'q1',text:'Saved question',options:['Yes','No'],correct:0}],lastScore:67}]});
    save();document.querySelector('#sidebar [data-view=quiz]').click();
    document.querySelector('[data-cyber-week="9"]').click();
  });
  assert(await run(function(){return document.querySelector('#cybersecurityBody .section-label').textContent==='Daily lessons'&&document.querySelectorAll('[data-cyber-day]').length===7;}),'Week9 daily lesson list failed');
  for(let day=1;day<=7;day++){
    await evalJs('cyberPage={mode:"day",week:9,day:'+day+'};renderCybersecurityRoadmap()');
    assert(await run(function(){
      const body=document.querySelector('#cybersecurityBody'),L=CYBERSECURITY_TEACH['9.'+cyberPage.day];
      return body.querySelector('.cyber-teaching').textContent.includes(L.objective)&&
        body.querySelectorAll('.cyber-teaching>.ls-h').length>=5&&
        body.querySelectorAll('.cyber-check').length===L.checks.length&&
        !/[\u0900-\u097f]/.test(body.textContent)&&body.querySelectorAll('.cyber-teaching>.ls-code').length>=1&&
        [...body.querySelectorAll('.cyber-references a')].every(a=>a.protocol==='https:'||['docs/cybersecurity-week9/README.md'].includes(a.getAttribute('href')));
    }),'Lesson/English/checks/references failed Day'+day);
    await run(function(){
      for(const button of document.querySelectorAll('.cyber-check [data-reveal]')){
        const answer=document.querySelector('#tryA'+button.dataset.reveal);
        if(!answer.hidden)throw Error('Answer shown before attempt');
        button.click();if(answer.hidden||!answer.querySelector('.ls-try-ans').textContent||!answer.querySelector('.ls-try-why').textContent)throw Error('Answer/reason absent');
        button.click();if(!answer.hidden)throw Error('Answer hide failed');
      }
      for(const button of document.querySelectorAll('.cyber-teaching [data-sol]')){
        const answer=document.querySelector('#solB'+button.dataset.sol);
        if(!answer.hidden)throw Error('Solution visible before attempt');
        button.click();if(answer.hidden||!answer.textContent.includes('How it works')||!answer.querySelector('.ls-out'))throw Error('Missing executed solution');
        button.click();if(!answer.hidden)throw Error('Solution hide failed');
      }
      const notes=document.querySelector('#cyberDayNotes'),box=notes.querySelector('.hn-box');
      if(box.hidden)throw Error('Daily notes not visible');
      const input=notes.querySelector('textarea');
      if(!input.getAttribute('aria-label').endsWith('Day '+cyberPage.day))throw Error('Wrong notes label');
      input.value='Week9 Day'+cyberPage.day+' note <b>literal</b>';
      input.dispatchEvent(new Event('input',{bubbles:true}));
      notes.querySelector('[data-hn]').click();if(!box.hidden)throw Error('Hide notes failed');
      document.querySelector('[data-cyber-notes]').click();
      if(box.hidden||document.activeElement!==input)throw Error('Show/focus notes failed');
    });
    await sleep(600);
    assert(await evalJs('DB.headNotes["cyber:9.'+day+'|day-notes"]==="Week9 Day'+day+' note <b>literal</b>"'),'Notes saving failed Day'+day);
  }
  await run(function(){cyberPage={mode:'day',week:9,day:1};renderCybersecurityRoadmap();document.querySelector('[data-cyber-step="-1"]').click();});
  assert(await run(function(){return cyberPage.week===8&&cyberPage.day===7&&!!document.querySelector('.cyber-teaching');}),'Previous-week boundary failed');
  await run(function(){document.querySelector('[data-cyber-step="1"]').click();});
  assert(await run(function(){return cyberPage.week===9&&cyberPage.day===1;}),'Next-week return failed');
  await run(function(){
    cyberPage={mode:'day',week:9,day:7};renderCybersecurityRoadmap();
    if(document.querySelectorAll('.cyber-check').length!==16)throw Error('Missing complete review');
    document.querySelector('[data-cyber-step="1"]').click();
    if(cyberPage.week!==10||cyberPage.day!==1||!document.querySelector('#cybersecurityBody').textContent.includes('Roadmap only'))throw Error('Week9→10 boundary');
    for(let w=9;w<=16;w++)for(let d=1;d<=7;d++){
      cyberPage={mode:'day',week:w,day:d};renderCybersecurityRoadmap();
      const text=document.querySelector('#cybersecurityBody').textContent;
      if(!text.includes(CYBERSECURITY_ROADMAP[w-1].days[d-1].focus)||!text.includes('Where Python helps'))throw Error('Missing roadmap day '+w+'.'+d);
      if(w>9&&(document.querySelector('.cyber-teaching')||!text.includes('Roadmap only')))throw Error('Unwritten lesson presented as ready');
    }
    cyberPage={mode:'day',week:16,day:7};renderCybersecurityRoadmap();
    if(!document.querySelector('[data-cyber-step="1"]').disabled)throw Error('Final Next enabled');
    document.querySelector('[data-cyber-step="1"]').click();
    if(cyberPage.week!==16||cyberPage.day!==7)throw Error('Escaped roadmap');
  });
  await run(function(){document.querySelector('[data-cyber-step="-1"]').click();document.querySelector('#cyberOldQuizzes').click();document.querySelector('#quizList [data-id=cyber-legacy]').click();});
  assert(await run(function(){return document.querySelector('#quizDetail').textContent.includes('Saved question')&&DB.quizzes[0].lastScore===67;}),'Existing quiz inaccessible');
  await run(function(){document.querySelector('#cyberBack').click();});
  await send('Page.reload',{ignoreCache:true});for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  assert(await run(function(){return Array.from({length:7},(_,i)=>DB.headNotes['cyber:9.'+(i+1)+'|day-notes']===('Week9 Day'+(i+1)+' note <b>literal</b>')).every(Boolean)&&DB.headNotes['cyber:7.1|day-notes']==='Keep Week7 notes'&&DB.course.notes['30.0']==='Keep Python notes'&&isPartDone(30,0,0)&&DB.japanese.done['8.1']&&DB.headNotes.legacy;}),'Refresh changed old/new notes or progress');
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await run(function(){
    closeModal();switchView('quiz');
    for(let theme=0;theme<2;theme++){
      document.querySelector('#themeBtn').click();
      for(let day=1;day<=7;day++){
        cyberPage={mode:'day',week:9,day};renderCybersecurityRoadmap();
        for(const button of document.querySelectorAll('.cyber-check [data-reveal]'))button.click();
        if(document.documentElement.scrollWidth>innerWidth+1)throw Error('Mobile overflow Day'+day);
      }
    }
    cyberPage={mode:'day',week:9,day:1};renderCybersecurityRoadmap();
    document.querySelector('.cyber-teaching').scrollIntoView();
  });
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-cybersecurity-week9-mobile.png'),Buffer.from(shot.data,'base64'));
  assert(errors.length===0,'JavaScript errors: '+errors.join('; '));
  console.log('PASS: all7 Week9 lessons/52 checks/14 solution show-hide controls and all56 new roadmap days, daily note labels/save/hide/show/refresh, previous-next boundaries, old quizzes, existing progress and375px themes; no JavaScript errors.');
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
