// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-exercise-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-design-profile-'));
const fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=expression=>eval(expression);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const watchdog=setTimeout(()=>{console.error('Design check timed out');browser.kill();process.exit(1);},120000);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const p=path.join(profile,'DevToolsActivePort');if(fs.existsSync(p)){port=Number(fs.readFileSync(p,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome startup');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Browser command timed out: '+method));},20000);pending.set(id,{resolve:value=>{clearTimeout(timer);resolve(value);},reject:error=>{clearTimeout(timer);reject(error);}});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const shot=async name=>{await sleep(120);const r=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(out,name+'.png'),Buffer.from(r.data,'base64'));};
 await send('Runtime.enable');await send('Page.enable');
 for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('Boolean(window.__studyHubBooted)'),'Boot');

 await evaluate('closeModal();DB=applyDefaults({todos:[{id:"keep-task",title:"Keep existing task",done:false,priority:"medium"}],course:{done:{"1.0":"2026-10-01"},notes:{"1.0":"Keep Python note"}},japanese:{notes:{"1.1.te":"Keep Japanese note"}},headNotes:{legacy:"Keep heading note"}});save();switchView("todo");document.querySelector("[data-todo-mode=exercise]").click()');
 assert(await evaluate('!document.getElementById("exercisePane").hidden&&document.getElementById("habitPane").hidden&&document.getElementById("taskPane").hidden&&document.getElementById("newTodoBtn").hidden'),'Exercise tab isolation');
 assert(await evaluate('Object.keys(DB.exerciseTracker.entries).length===0&&Object.keys(DB.exerciseTracker.exercises).length===0'),'Invented activity records');
 await evaluate('exerciseSelectDate("2026-10-19");window.__originalOtherStores=JSON.stringify([DB.todos,DB.course,DB.japanese,DB.headNotes,DB.habitTracker])');
 async function template(name,unit,sets){
  await evaluate('document.getElementById("exerciseAdd").click();document.getElementById("exerciseName").value='+JSON.stringify(name)+';document.getElementById("exerciseUnit").value='+JSON.stringify(unit)+';document.getElementById("exerciseUnit").dispatchEvent(new Event("change"));document.getElementById("exerciseSets").value='+sets+';document.getElementById("exerciseTemplateForm").requestSubmit()');
  assert(await evaluate('!document.getElementById("exerciseTemplateForm")'),'Template form rejected '+name);
 }
 async function log(name,amount){
  await evaluate('(()=>{const id=exerciseTemplates().find(item=>item.name==='+JSON.stringify(name)+').id;document.querySelector("[data-exercise-log=\\""+id+"\\"]").click();document.getElementById("exerciseQuantity").value='+amount+';document.getElementById("exerciseEntryForm").requestSubmit();})()');
  assert(await evaluate('!document.getElementById("exerciseEntryForm")'),'Log form rejected '+name);
 }
 for(const [name,amount,unit,sets] of [['Push-up',20,'reps',2],['Squat',20,'reps',2],['Plank',40,'sec',2],['Pull-up',10,'reps',2],['Meditation',20,'min',1],['Surya Namaskar',12,'sets',1]]){
  await template(name,unit,sets);await log(name,amount);
 }
 assert(await evaluate('exerciseEntries("2026-10-19").length===6&&document.querySelectorAll(".exercise-log-row").length===6'),'Six example activities');
 assert.deepEqual(await evaluate('exerciseEntries("2026-10-19").map(exerciseAmount)'),['20 reps × 2 sets','20 reps × 2 sets','40 sec × 2 sets','10 reps × 2 sets','20 min','12 sets'],'Reps/time/sets labels');
 assert(await evaluate('JSON.stringify([DB.todos,DB.course,DB.japanese,DB.headNotes,DB.habitTracker])===window.__originalOtherStores'),'Exercise changed other stores');
 const beforeCancel=await evaluate('JSON.stringify(DB.exerciseTracker)');
 await evaluate('document.getElementById("exerciseAdd").click();document.getElementById("exerciseName").value="Cancelled";document.getElementById("exerciseCancel").click()');
 assert.equal(await evaluate('JSON.stringify(DB.exerciseTracker)'),beforeCancel,'Cancel wrote data');
 // Boundary validation and fractional duration, with no fractional repetitions.
 await evaluate('document.getElementById("exerciseLog").click();document.getElementById("exerciseQuantity").value="0";document.getElementById("exerciseEntryForm").requestSubmit()');
 assert(await evaluate('!!document.getElementById("exerciseEntryForm")&&document.getElementById("exerciseFormError").textContent.length>0'),'Zero activity accepted');
 await evaluate('document.getElementById("exerciseUnit").value="reps";document.getElementById("exerciseUnit").dispatchEvent(new Event("change"));document.getElementById("exerciseQuantity").value="1.5";document.getElementById("exerciseEntryForm").requestSubmit()');
 assert(await evaluate('!!document.getElementById("exerciseEntryForm")'),'Fractional reps accepted');
 await evaluate('document.getElementById("exerciseCancel").click();exerciseEditEntry(null,exerciseTemplates().find(e=>e.name==="Meditation").id);document.getElementById("exerciseQuantity").value="2.5";document.getElementById("exerciseEntryForm").requestSubmit()');
 assert(await evaluate('exerciseEntries("2026-10-19").some(e=>e.quantity===2.5&&e.unit==="min")'),'Fractional minutes rejected');
 // Consecutive dates, month boundaries and leap-day handling.
 await evaluate('document.getElementById("exerciseNext").click()');
 assert(await evaluate('exerciseDate()==="2026-10-20"&&exerciseEntries(exerciseDate()).length===0&&exerciseTemplates().length===6'),'Next date copied completed activity');
 await log('Push-up',15);
 await evaluate('document.getElementById("exercisePrev").click()');
 assert(await evaluate('exerciseDate()==="2026-10-19"&&exerciseEntries(exerciseDate()).length===7&&document.querySelectorAll(".exercise-history-day").length===2'),'Previous date/history');
 await evaluate('exerciseSelectDate("2028-02-28");exerciseMoveDate(1)');assert(await evaluate('exerciseDate()==="2028-02-29"'),'Leap day');
 await evaluate('exerciseMoveDate(1)');assert(await evaluate('exerciseDate()==="2028-03-01"'),'Leap month boundary');
 await evaluate('exerciseSelectDate("2026-04-30");exerciseMoveDate(1)');assert(await evaluate('exerciseDate()==="2026-05-01"'),'30-day boundary');
 await evaluate('exerciseSelectDate("2026-10-19");window.__pushEntry=exerciseEntries(exerciseDate()).find(e=>e.exerciseName==="Push-up").id;window.__pushTemplate=exerciseTemplates().find(e=>e.name==="Push-up").id');
 // Edits preserve the other dates and the name originally recorded in history.
 await evaluate('document.querySelector("[data-exercise-edit=\\""+window.__pushEntry+"\\"]").click();document.getElementById("exerciseQuantity").value="25";document.getElementById("exerciseLogNotes").value="Set 1: 25, set 2: 25 <b>literal note</b>";document.getElementById("exerciseEntryForm").requestSubmit()');
 assert(await evaluate('DB.exerciseTracker.entries[window.__pushEntry].quantity===25&&exerciseEntries("2026-10-20")[0].quantity===15&&!document.querySelector(".exercise-note b")'),'Entry edit or escaping');
 await evaluate('document.querySelector("[data-exercise-edit=\\""+window.__pushTemplate+"\\"]").click();document.getElementById("exerciseName").value="Push-up renamed";document.getElementById("exerciseTemplateForm").requestSubmit()');
 assert(await evaluate('DB.exerciseTracker.entries[window.__pushEntry].exerciseName==="Push-up"&&exerciseTemplates().some(e=>e.name==="Push-up renamed")'),'Template rename rewrote history');
 // Archive/restore uses tombstones; cancelled confirmations leave history alone.
 await evaluate('document.querySelector("[data-exercise-remove=\\""+window.__pushEntry+"\\"]").click();document.getElementById("cdNo").click()');assert(await evaluate('!DB.exerciseTracker.entries[window.__pushEntry].deleted'),'Cancelled removal');
 await evaluate('document.querySelector("[data-exercise-remove=\\""+window.__pushEntry+"\\"]").click();document.getElementById("cdYes").click()');assert(await evaluate('DB.exerciseTracker.entries[window.__pushEntry].deleted&&exerciseEntries(exerciseDate(),true).length===1'),'Remove activity');
 await evaluate('document.querySelector("[data-exercise-restore=\\""+window.__pushEntry+"\\"]").click()');assert(await evaluate('!DB.exerciseTracker.entries[window.__pushEntry].deleted'),'Restore activity');
 await evaluate('document.querySelector("[data-exercise-remove=\\""+window.__pushTemplate+"\\"]").click();document.getElementById("cdYes").click()');
 assert(await evaluate('DB.exerciseTracker.exercises[window.__pushTemplate].deleted&&exerciseEntries(exerciseDate()).length===7'),'Removing exercise lost history');
 await evaluate('document.querySelector("[data-exercise-edit=\\""+window.__pushEntry+"\\"]").click();document.getElementById("exerciseSets").value="3";document.getElementById("exerciseEntryForm").requestSubmit()');
 assert(await evaluate('DB.exerciseTracker.entries[window.__pushEntry].sets===3'),'Cannot edit history of an archived exercise');
 await evaluate('document.querySelector("[data-exercise-restore=\\""+window.__pushTemplate+"\\"]").click()');
 // Cross-device merge keeps independent entries, latest edits and deletions.
 await evaluate('(()=>{const incoming=JSON.parse(JSON.stringify(DB)),entry=incoming.exerciseTracker.entries[window.__pushEntry];entry.quantity=30;entry.updatedAt="2099-01-01T00:00:00.000Z";const remote={...entry,id:"remote-entry",exerciseName:"Remote fixture",quantity:5};incoming.exerciseTracker.entries[remote.id]=remote;mergeIntoDB(incoming);save();renderTodos();})()');
 assert(await evaluate('DB.exerciseTracker.entries[window.__pushEntry].quantity===30&&!!DB.exerciseTracker.entries["remote-entry"]'),'Remote changes/independent entry');
 await evaluate('(()=>{window.__staleExerciseBackup=JSON.parse(JSON.stringify(DB));const entry=DB.exerciseTracker.entries[window.__pushEntry];entry.deleted=true;entry.updatedAt="2099-02-01T00:00:00.000Z";mergeIntoDB(window.__staleExerciseBackup);save();renderTodos();})()');
 assert(await evaluate('DB.exerciseTracker.entries[window.__pushEntry].deleted'),'Stale backup resurrected an activity');
 await evaluate('document.querySelector("[data-exercise-restore=\\""+window.__pushEntry+"\\"]").click()');
 assert(await evaluate('Date.parse(DB.exerciseTracker.entries[window.__pushEntry].updatedAt)>Date.parse("2099-02-01")'),'Local restore must advance the record clock');
 // Actual backup download + file import, not only calls to storage helpers.
 await evaluate('window.__exerciseBlob=null;const previous=URL.createObjectURL;URL.createObjectURL=blob=>{window.__exerciseBlob=blob;return previous(blob);};document.getElementById("exportBtn").click()');
 const backup=await evaluate('window.__exerciseBlob.text()'),saved=JSON.parse(backup).exerciseTracker;
 assert(saved.entries['remote-entry']&&Object.keys(saved.exercises).length===6,'Backup content');
 await evaluate('DB.exerciseTracker=exerciseDefaults({});save()');
 await evaluate('(()=>{const file=new File(['+JSON.stringify(backup)+'],"exercise-backup.json",{type:"application/json"}),transfer=new DataTransfer();transfer.items.add(file);const input=document.getElementById("importFile");input.files=transfer.files;input.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<50&&!await evaluate('!!document.getElementById("impMerge")');i++)await sleep(80);
 await evaluate('document.getElementById("impMerge").click()');assert.deepEqual(await evaluate('DB.exerciseTracker'),saved,'Actual merge import');
 await evaluate('DB.exerciseTracker=exerciseDefaults({});confirmMerge('+backup+');document.getElementById("impReplace").click()');assert.deepEqual(await evaluate('DB.exerciseTracker'),saved,'Replace import');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert.deepEqual(await evaluate('DB.exerciseTracker'),saved,'Refresh persistence');
 assert(await evaluate('DB.todos[0].title==="Keep existing task"&&DB.course.notes["1.0"]==="Keep Python note"&&DB.japanese.notes["1.1.te"]==="Keep Japanese note"&&DB.headNotes.legacy==="Keep heading note"'),'Existing learning/tasks data');
 // Older backups need no migration or exercise key; malformed new records are ignored.
 assert(await evaluate('Object.keys(applyDefaults({todos:[{id:"legacy",title:"Old task"}]}).exerciseTracker.entries).length===0'),'Old backup compatibility');
 await templateSafeAfterReload();
 async function templateSafeAfterReload(){await evaluate('switchView("todo");document.querySelector("[data-todo-mode=exercise]").click();exerciseSelectDate("2026-10-19")');}
 await template('<img src=x onerror=alert(1)>','rounds',1);assert(await evaluate('!document.querySelector(".exercise-template-row img")'),'Name injected HTML');
 // Desktop/phone, both themes, all forms and existing tabs remain usable.
 for(const [width,height] of [[1440,950],[900,768],[375,900],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('closeModal();document.documentElement.dataset.theme='+JSON.stringify(theme)+';todoMode="exercise";switchView("todo");window.scrollTo(0,0)');
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Exercise page overflow '+width+' '+theme);
   if(width===1440||width===375)await shot('exercise-'+width+'-'+theme);
   await evaluate('document.getElementById("exerciseAdd").click()');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Template form overflow');
   await evaluate('closeModal();document.getElementById("exerciseLog").click()');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Activity form overflow');
   await evaluate('closeModal();document.querySelector("[data-todo-mode=tasks]").click()');assert(await evaluate('!document.getElementById("taskPane").hidden&&document.getElementById("exercisePane").hidden&&document.getElementById("todoList").textContent.includes("Keep existing task")'),'Tasks unchanged');
   await evaluate('document.querySelector("[data-todo-mode=habits]").click()');assert(await evaluate('!document.getElementById("habitPane").hidden&&document.getElementById("exercisePane").hidden'),'Habits unchanged');
  }
 }
 assert.deepEqual(errors,[],'Browser errors');
 console.log('PASS: all six requested activity formats; date/history/leap-day isolation; add/edit/cancel/remove/restore; archived exercise history; validation/escaping; cross-device conflict and stale deletion protection; actual backup/import merge+replace and refresh; existing habits/tasks/course data; four widths/light+dark/forms; no console errors. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

