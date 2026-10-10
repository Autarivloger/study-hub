const fs=require('fs'),os=require('os'),path=require('path'),{spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-habits-')),fixture=path.join(profile,'habits.html');
fs.writeFileSync(fixture,fs.readFileSync('study-hub.html','utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const f=path.join(profile,'DevToolsActivePort');if(fs.existsSync(f)){port=Number(fs.readFileSync(f,'utf8').split('\n')[0]);break;}await sleep(100);}if(!port)throw Error('Chrome did not start');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval ? window.__courseTestEval('+JSON.stringify(expression)+') : eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const assert=(v,m)=>{if(!v)throw Error(m);};
 await send('Runtime.enable');await send('Page.enable');for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}assert(await evaluate('window.__studyHubBooted'),'Boot failed');
 await evaluate('switchView("todo")');
 assert(await evaluate('!document.querySelector("#habitPane").hidden && document.querySelector("#taskPane").hidden && Object.keys(DB.habitTracker.months).length===0'),'Opening empty tracker wrote records or failed');
 assert(await evaluate('habitDays("2028-02")===29&&habitDays("2027-02")===28&&habitDays("2100-02")===28&&habitDays("2000-02")===29&&habitDays("2026-04")===30&&habitDays("2026-10")===31'),'Calendar dates incorrect');
 await evaluate('DB.course.done["1.0"]="2026-01-01";DB.japanese.done["1.1"]="2026-01-01";DB.headNotes.legacy="Keep this note";save();habitSelectMonth("2026-10")');
 async function add(title,goal){await evaluate('document.querySelector("#habitAdd").click();document.querySelector("#habitTitle").value='+JSON.stringify(title)+';document.querySelector("#habitCategory").value="Learning";document.querySelector("#habitGoal").value='+goal+';document.querySelector("#habitForm").requestSubmit()');}
 await add('Reading',2);await add('Practice',31);
 assert(await evaluate('habitRows("2026-10").length===2&&document.querySelectorAll("[data-habit-check]").length===62'),'Add/month grid failed');
 const firstId=await evaluate('habitRows("2026-10")[0].id');
 const secondId=await evaluate('habitRows("2026-10")[1].id');
 await evaluate('document.querySelector("[data-habit-check][data-day=\\"1\\"]").click()');
 assert(await evaluate('habitStats("2026-10").total===1&&habitStats("2026-10").percent===3&&document.querySelector("#habitPercent").textContent==="3%"'),'First checkbox/chart calculation wrong');
 await evaluate('document.querySelector("[data-habit-check][data-day=\\"2\\"]").click();document.querySelector("[data-habit-check][data-day=\\"3\\"]").click()');
 assert(await evaluate('habitStats("2026-10").total===3&&habitStats("2026-10").earned===2&&habitStats("2026-10").percent===6'),'Extra days incorrectly compensate another habit goal');
 await evaluate('document.querySelector("[data-habit-check][data-day=\\"3\\"]").click()');
 assert(await evaluate('DB.habitTracker.checks[habitDayKey("2026-10",'+JSON.stringify(firstId)+',3)].done===false'),'Unchecked state was not retained');
 await evaluate('document.querySelector("[data-habit-edit]").click();document.querySelector("#habitTitle").value="Reading <img src=x onerror=alert(1)>";document.querySelector("#habitForm").requestSubmit()');
 assert(await evaluate('habitCount(habitRows("2026-10")[0],"2026-10")===2&&!document.querySelector(".ht-name img")'),'Edit lost checks or inserted untrusted markup');
 await evaluate('document.querySelector("#habitNext").click()');
 assert(await evaluate('habitMonth()==="2026-11"&&habitRows("2026-11").length===2&&habitStats("2026-11").total===0&&habitRows("2026-11")[1].goalMode==="daily"&&habitGoal(habitRows("2026-11")[1],"2026-11")===30'),'Next month did not copy names/adjust daily goal/reset checks');
 await evaluate('document.querySelector("[data-habit-check][data-day=\\"1\\"]").click();document.querySelector("[data-habit-edit]").click();document.querySelector("#habitTitle").value="November reading";document.querySelector("#habitForm").requestSubmit()');
 assert(await evaluate('habitRows("2026-10")[0].title.startsWith("Reading")&&habitStats("2026-10").total===2'),'Month edit/check changed another month');
 await evaluate('document.querySelector("#habitPrev").click()');
 assert(await evaluate('habitMonth()==="2026-10"&&habitStats("2026-10").total===2'),'Prior month did not retain checks');
 await evaluate('document.querySelector("[data-habit-remove]").click();document.querySelector("#cdNo").click()');
 assert(await evaluate('habitRows("2026-10").length===2'),'Cancel removal changed habit');
 await evaluate('document.querySelector("[data-habit-remove]").click();document.querySelector("#cdYes").click()');
 assert(await evaluate('habitRows("2026-10").length===1&&habitRows("2026-10",true).length===1&&habitStats("2026-10").total===0&&habitStats("2026-11").total===1'),'Recoverable removal failed or affected another month');
 await evaluate('document.querySelector("[data-habit-restore]").click()');
 assert(await evaluate('habitRows("2026-10").length===2&&habitStats("2026-10").total===2'),'Restore lost checked days');
 await evaluate('habitSelectMonth("2028-02")');
 assert(await evaluate('document.querySelectorAll("[data-habit-check]").length===58&&habitStats("2028-02").total===0&&habitGoal(habitRows("2028-02")[1],"2028-02")===29'),'Leap month grid/copy failed');
 await evaluate('(()=>{const item=DB.habitTracker.items[habitRecordKey("2028-02",'+JSON.stringify(secondId)+')];item.goalDays=30;item.goalMode="custom";habitEdit(item.id);document.querySelector("#habitTitle").value="Renamed in February";document.querySelector("#habitForm").requestSubmit();})()');
 assert(await evaluate('DB.habitTracker.items[habitRecordKey("2028-02",'+JSON.stringify(secondId)+')].goalDays===30&&DB.habitTracker.items[habitRecordKey("2028-02",'+JSON.stringify(secondId)+')].goalMode==="custom"'),'Name edit changed a shorter-month goal policy');
 await evaluate('habitSelectMonth("2026-12");document.querySelector("#habitNext").click()');
 assert(await evaluate('habitMonth()==="2027-01"'),'Year boundary next failed');
 await evaluate('document.querySelector("#habitPrev").click()');assert(await evaluate('habitMonth()==="2026-12"'),'Year boundary previous failed');
 await evaluate('habitSelectMonth("2026-10");document.querySelector("#habitCopySource").value="2026-11";document.querySelector("#habitCopy").click()');
 assert(await evaluate('habitRows("2026-10").length===2'),'Copy duplicated existing habits');
 await evaluate('habitEdit();document.querySelector("#habitTitle").value="   ";document.querySelector("#habitForm").requestSubmit()');
 assert(await evaluate('habitRows("2026-10").length===2&&document.querySelector("#habitFormError").textContent.length>0'),'Blank title was accepted');await evaluate('closeModal()');
 await evaluate('document.querySelector("[data-todo-mode=tasks]").click();document.querySelector("#newTodoBtn").click();document.querySelector("#todoTitle").value="Existing task works";document.querySelector("#tdSave").click()');
 assert(await evaluate('DB.todos.some(t=>t.title==="Existing task works")&&!document.querySelector("#taskPane").hidden'),'Legacy task add/tab failed');
 await evaluate('document.querySelector("#todoList [data-toggle]").click()');assert(await evaluate('DB.todos.find(t=>t.title==="Existing task works").done'),'Legacy task completion failed');
 await evaluate('document.querySelector("[data-todo-mode=habits]").click();habitSelectMonth("2026-11")');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
 await evaluate('switchView("todo")');
 assert(await evaluate('habitMonth()==="2026-11"&&habitStats("2026-11").total===1&&habitStats("2026-10").total===2&&DB.todos.some(t=>t.done)'),'Selection/history/tasks failed reload');
 // Simulate independent device changes and an older backup without contacting a real account.
 await evaluate('(()=>{const old=JSON.parse(JSON.stringify(DB));DB.habitTracker.checks[habitDayKey("2026-10",'+JSON.stringify(firstId)+',3)]={done:false,updatedAt:"2099-01-01T00:00:00Z"};old.habitTracker.checks[habitDayKey("2026-10",'+JSON.stringify(firstId)+',3)]={done:true,updatedAt:"2000-01-01T00:00:00Z"};old.habitTracker.checks[habitDayKey("2026-10",'+JSON.stringify(secondId)+',5)]={done:true,updatedAt:"2099-01-02T00:00:00Z"};old.habitTracker.items[habitRecordKey("2026-10",'+JSON.stringify(secondId)+')].title="Remote renamed habit";old.habitTracker.items[habitRecordKey("2026-10",'+JSON.stringify(secondId)+')].updatedAt="2099-01-02T00:00:00Z";mergeIntoDB(old);save();})()');
 assert(await evaluate('DB.habitTracker.checks[habitDayKey("2026-10",'+JSON.stringify(firstId)+',3)].done===false&&DB.habitTracker.checks[habitDayKey("2026-10",'+JSON.stringify(secondId)+',5)].done===true&&DB.habitTracker.items[habitRecordKey("2026-10",'+JSON.stringify(secondId)+')].title==="Remote renamed habit"'),'Per-record merge lost independent changes or restored an old tick');
 await evaluate('(()=>{const old=JSON.parse(JSON.stringify(DB)),key=habitRecordKey("2026-10",'+JSON.stringify(firstId)+');DB.habitTracker.items[key].deleted=true;DB.habitTracker.items[key].updatedAt="2099-02-01T00:00:00Z";old.habitTracker.items[key].deleted=false;old.habitTracker.items[key].updatedAt="2000-01-01T00:00:00Z";mergeIntoDB(old);save();})()');
 assert(await evaluate('DB.habitTracker.items[habitRecordKey("2026-10",'+JSON.stringify(firstId)+')].deleted===true'),'Old backup resurrected removed habit');
 await evaluate('window.__habitBackup=null;const original=URL.createObjectURL;URL.createObjectURL=function(blob){window.__habitBackup=blob;return original(blob);};document.querySelector("#exportBtn").click()');
 const backup=await evaluate('window.__habitBackup.text()');assert(JSON.parse(backup).habitTracker.selectedMonth.value==='2026-11','Backup lost month selection');
 await evaluate('DB.habitTracker={months:{},items:{},checks:{},selectedMonth:null};save();');
 await evaluate('(()=>{const file=new File(['+JSON.stringify(backup)+'],"habits-backup.json",{type:"application/json"}),dt=new DataTransfer();dt.items.add(file);const input=document.querySelector("#importFile");input.files=dt.files;input.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<40;i++){if(await evaluate('Boolean(document.querySelector("#impMerge"))'))break;await sleep(100);}await evaluate('document.querySelector("#impMerge").click()');
 assert(await evaluate('habitMonth()==="2026-11"&&habitStats("2026-11").total===1&&DB.course.done["1.0"]&&DB.japanese.done["1.1"]&&DB.headNotes.legacy==="Keep this note"'),'Merge import lost tracker or original course data');
 await evaluate('confirmMerge('+JSON.stringify(JSON.parse(backup))+');document.querySelector("#impReplace").click()');
 assert(await evaluate('habitMonth()==="2026-11"&&habitStats("2026-11").total===1&&DB.todos.some(t=>t.done)'),'Replace import failed');
 // Existing personal tasks are imported locally, never put in published source.
 await evaluate('todoMode="habits";switchView("todo")');
 const tasksBefore=await evaluate('JSON.stringify(DB.todos)');
 assert(await evaluate('Object.keys(DB.habitTracker.months).every(month=>habitRows(month).some(item=>item.title==="Existing task works"))'),'Existing tasks were not filled into every saved month');
 assert(await evaluate('Object.values(DB.habitTracker.checks).filter(check=>check.done).length>0&&habitRows("2026-11").some(item=>item.sourceTodoId)&&habitCount(habitRows("2026-11").find(item=>item.sourceTodoId),"2026-11")===0'),'Completed task incorrectly became daily check-ins');
 for(const [month,days] of [['2027-02',28],['2028-02',29],['2026-04',30],['2026-07',31]]){
  await evaluate('habitSelectMonth('+JSON.stringify(month)+')');
  assert(await evaluate('document.querySelectorAll(".ht-table thead tr:nth-child(2) th").length==='+days+'&&document.querySelectorAll("[data-habit-check]").length===habitRows(habitMonth()).length*'+days+'&&document.querySelector(".ht-day-badge").textContent==="'+days+' days"'),'Rendered calendar incorrect '+month);
 }
 await evaluate('habitSelectMonth("2026-11")');
 // Real mouse pointer drag, followed by keyboard and touch reordering.
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1200,deviceScaleFactor:1,mobile:false});
 await evaluate('document.querySelector(".ht-table-scroll").scrollIntoView({block:"center"})');
 async function positions(){return evaluate('[...document.querySelectorAll("[data-habit-drag]")].map(handle=>{const r=handle.getBoundingClientRect(),row=handle.closest("tr").getBoundingClientRect();return {id:handle.dataset.habitDrag,x:r.left+r.width/2,y:r.top+r.height/2,bottom:row.bottom};})');}
 const beforeDrag=await positions(),dragFirst=beforeDrag[0],dragLast=beforeDrag.at(-1);
 const ticksBefore=await evaluate('JSON.stringify(DB.habitTracker.checks)');
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:dragFirst.x,y:dragFirst.y});
 await send('Input.dispatchMouseEvent',{type:'mousePressed',x:dragFirst.x,y:dragFirst.y,button:'left',buttons:1,clickCount:1});
 await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:dragLast.x,y:dragLast.bottom-8,button:'left',buttons:1});
 await send('Input.dispatchMouseEvent',{type:'mouseReleased',x:dragLast.x,y:dragLast.bottom-8,button:'left',buttons:0,clickCount:1});
 assert(await evaluate('habitRows("2026-11").at(-1).id==='+JSON.stringify(dragFirst.id)),'Mouse drag did not persist row order');
 await evaluate('document.querySelector("[data-habit-drag=\\"'+dragFirst.id+'\\"]").focus()');
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowUp',code:'ArrowUp',windowsVirtualKeyCode:38});
 await send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowUp',code:'ArrowUp',windowsVirtualKeyCode:38});
 assert(await evaluate('habitRows("2026-11").at(-2).id==='+JSON.stringify(dragFirst.id)),'Keyboard reorder failed');
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:950,deviceScaleFactor:1,mobile:true});
 await evaluate('renderTodos();document.querySelector(".ht-table-scroll").scrollLeft=0;document.querySelector(".ht-table-scroll").scrollIntoView({block:"center"})');
 const touchRows=await positions(),touchFirst=touchRows[0],touchLast=touchRows.at(-1);
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:touchFirst.x,y:touchFirst.y,id:1}]});
 await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:touchLast.x,y:touchLast.bottom-8,id:1}]});
 await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
 assert(await evaluate('habitRows("2026-11").at(-1).id==='+JSON.stringify(touchFirst.id)),'Touch drag did not persist row order');
 assert(await evaluate('JSON.stringify(DB.habitTracker.checks)')===ticksBefore,'Reordering changed day checks');
 const orderedIds=await evaluate('habitRows("2026-11").map(item=>item.id).join(",")');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
 await evaluate('switchView("todo")');
 assert(await evaluate('habitRows("2026-11").map(item=>item.id).join(",")')===orderedIds,'Reordered rows did not survive reload');
 await evaluate('window.__habitBackup=null;const captureOriginal=URL.createObjectURL;URL.createObjectURL=function(blob){window.__habitBackup=blob;return captureOriginal(blob);};document.querySelector("#exportBtn").click()');
 const reorderedBackup=JSON.parse(await evaluate('window.__habitBackup.text()'));
 await evaluate('DB.habitTracker={months:{},items:{},checks:{},selectedMonth:null};confirmMerge('+JSON.stringify(reorderedBackup)+');document.querySelector("#impReplace").click();todoMode="habits";switchView("todo")');
 assert(await evaluate('habitRows("2026-11").map(item=>item.id).join(",")')===orderedIds,'Reordered rows did not survive actual backup export/import');
 // All-month editing preserves every day record and adapts daily goals to month lengths.
 await evaluate('habitEdit('+JSON.stringify(secondId)+');document.querySelector("#habitTitle").value="Practice everywhere";document.querySelector("#habitEditScope").value="all";document.querySelector("#habitGoal").value=30;document.querySelector("#habitForm").requestSubmit()');
 assert(await evaluate('Object.values(DB.habitTracker.items).filter(item=>item.id==='+JSON.stringify(secondId)+').every(item=>item.title==="Practice everywhere")'),'All-month name edit failed');
 assert(await evaluate('JSON.stringify(DB.habitTracker.checks)')===ticksBefore,'All-month edits lost ticks');
 await evaluate('habitSelectMonth("2029-02")');
 assert(await evaluate('habitGoal(habitRows("2029-02").find(item=>item.id==='+JSON.stringify(secondId)+'),"2029-02")===28&&habitRows("2029-02").find(item=>item.id==='+JSON.stringify(secondId)+').title==="Practice everywhere"'),'Future month lost all-month edit or goal adaptation');
 await evaluate('habitSelectMonth("2026-11");window.__importedHabit=habitRows(habitMonth()).find(item=>item.sourceTodoId).id;document.querySelector("[data-habit-remove=\\""+window.__importedHabit+"\\"]").click();document.querySelector("#cdYes").click();renderTodos();renderTodos()');
 assert(await evaluate('habitRows("2026-11",true).some(item=>item.id===window.__importedHabit)&&!habitRows("2026-11").some(item=>item.id===window.__importedHabit)'),'Automatic filling resurrected a removed imported task');
 await evaluate('document.querySelector("[data-habit-restore=\\""+window.__importedHabit+"\\"]").click()');
 assert(await evaluate('JSON.stringify(DB.todos)')===tasksBefore,'Import/edit/reorder modified original Tasks records');
 await evaluate('habitEdit();document.querySelector("#habitTitle").value="A new recurring habit";document.querySelector("#habitForm").requestSubmit()');
 assert(await evaluate('Object.keys(DB.habitTracker.months).every(month=>habitRows(month).some(item=>item.title==="A new recurring habit"))'),'New habit was not filled into every saved month');
 const lengthBefore=await evaluate('habitRows("2026-11").length');
 await evaluate('DB.todos.push({id:"duplicate_task",title:"A new recurring habit",done:false});renderTodos();renderTodos()');
 assert(await evaluate('habitRows("2026-11").length')===lengthBefore,'Task with existing habit name was duplicated');
 assert(await evaluate('(()=>{const d=applyDefaults({todos:[{id:"old",title:"Old backup task"}]});return d.todos[0].title==="Old backup task"&&Object.keys(d.habitTracker.items).length===0;})()'),'Old backup compatibility failed');
 for(const width of [375,768,1440]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:950,deviceScaleFactor:1,mobile:width<600});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme)+';todoMode="habits";switchView("todo");habitSelectMonth("2026-11")');
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Tracker page overflows '+width+' '+theme);
   await evaluate('document.querySelector(".ht-table-scroll").scrollLeft=900;window.__habitScroll=document.querySelector(".ht-table-scroll").scrollLeft;document.querySelector("[data-habit-check][data-day=\\"25\\"]").click()');
   assert(await evaluate('Math.abs(document.querySelector(".ht-table-scroll").scrollLeft-window.__habitScroll)<=1'),'Checking a later day reset the scroll position');
   await evaluate('habitEdit();');assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Habit form overflows '+width);await evaluate('closeModal()');
  }
 }
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 // Fictional screenshot data only; no personal sheet contents are copied into source or test fixtures.
 await evaluate('DB.todos=[];DB.habitTracker={months:{},items:{},checks:{},selectedMonth:null};habitSelectMonth("2026-10");');
 for(const title of ['Read','Language practice','Walk','Stretch','Plan tomorrow'])await add(title,31);
 await evaluate('(()=>{for(const [index,item] of habitRows("2026-10").entries())for(let day=1;day<=11;day++)if((day+index)%4!==0)DB.habitTracker.checks[habitDayKey("2026-10",item.id,day)]={done:true,updatedAt:nowISO()};save();renderTodos();document.documentElement.dataset.theme="light";document.querySelector("#toast").classList.remove("show");window.scrollTo(0,0);})()');
 await sleep(350);
 let shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-habits-desktop.png'),Buffer.from(shot.data,'base64'));
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:950,deviceScaleFactor:1,mobile:true});await evaluate('renderTodos();window.scrollTo(0,0)');
 shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-habits-mobile.png'),Buffer.from(shot.data,'base64'));
 assert(errors.length===0,'JS errors: '+errors.join('; '));
 console.log('PASS: automatic task/all-month filling; independent edits and all-month edits; actual 28/29/30/31-day grids; mouse/touch/keyboard reorder + reload; original tasks/checks retained; habit add/edit/check/uncheck/remove/restore; goals/leap years; backup/import merge+replace; mobile/tablet/desktop light+dark; scroll retention; no JS errors');
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{if(ws)ws.close();browser.kill();});
