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

 await evaluate(`closeModal();DB=applyDefaults({headNotes:{legacy:'Keep notes'},course:{done:{'1.0':'2026-10-01'}},habitTracker:{months:{'2026-10':{updatedAt:nowISO()},'2026-11':{updatedAt:nowISO()}},items:{},checks:{},selectedMonth:{value:'2026-10',updatedAt:nowISO()}}});
 for(let i=0;i<36;i++){for(const month of ['2026-10','2026-11']){const id='drag-'+i;DB.habitTracker.items[habitRecordKey(month,id)]={id,month,title:'Habit '+String(i+1).padStart(2,'0'),category:'Practice',goalMode:'daily',goalDays:31,deleted:false,order:i,createdAt:nowISO(),updatedAt:nowISO()};}}
 DB.habitTracker.checks[habitDayKey('2026-10','drag-4',3)]={done:true,updatedAt:nowISO()};save();switchView('todo');`);
 const ticks=await evaluate('JSON.stringify(DB.habitTracker.checks)'),otherMonth=await evaluate('JSON.stringify(habitRows("2026-11"))');
 const positions=id=>evaluate(`(()=>{const r=document.querySelector('[data-habit-drag="${id}"]').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()`);
 async function prepare(width,height,bottom){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  await evaluate(`renderTodos();const grid=document.querySelector('.ht-table-scroll');grid.scrollLeft=0;grid.scrollTop=${bottom?'grid.scrollHeight':'0'};grid.scrollIntoView({block:'${bottom?'end':'start'}'});${bottom?'':'window.scrollBy(0,-145);'}`);
  await sleep(100);
 }
 async function edge(direction){return evaluate(`(()=>{const r=document.querySelector('.ht-table-scroll').getBoundingClientRect();let top=0;for(const id of ['topbar','tabnav']){const h=document.getElementById(id);if(h&&h.getClientRects().length)top=Math.max(top,h.getBoundingClientRect().bottom);}return ${direction>0?'Math.min(innerHeight-12,r.bottom-5)':'Math.max(top+7,r.top+5)'};})()`);}
 async function until(expression,label){for(let i=0;i<70;i++){if(await evaluate(expression))return;await sleep(75);}throw Error(label);}
 async function mouseStart(id,y){const pos=await positions(id);assert(pos.y>0&&pos.y<await evaluate('innerHeight'),'Drag start outside screen');await send('Input.dispatchMouseEvent',{type:'mouseMoved',...pos});await send('Input.dispatchMouseEvent',{type:'mousePressed',...pos,button:'left',buttons:1,clickCount:1});await send('Input.dispatchMouseEvent',{type:'mouseMoved',x:pos.x,y,button:'left',buttons:1});return pos.x;}
 async function release(x,y){await send('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button:'left',buttons:0,clickCount:1});}
 async function stable(){const a=await evaluate('JSON.stringify([scrollY,document.querySelector(".ht-table-scroll").scrollTop])');await sleep(250);assert(await evaluate('JSON.stringify([scrollY,document.querySelector(".ht-table-scroll").scrollTop])')===a,'Auto-scroll continued after drag finished');}
 // One pointer move, then hold still: cross rows outside both the grid and viewport.
 await prepare(1440,650,false);
 const gridLimit=await evaluate('document.querySelector(".ht-table-scroll").scrollHeight-document.querySelector(".ht-table-scroll").clientHeight');
 let y=await edge(1),x=await mouseStart('drag-0',y);
 await until('document.querySelector("tbody").lastElementChild.dataset.habitRow==="drag-0"','Stationary mouse failed to reach last offscreen row');
 assert(await evaluate('document.querySelector(".ht-table-scroll").scrollTop')>=gridLimit-2,'Did not scroll through inner grid');
 await release(x,y);await stable();
 assert(await evaluate('habitRows("2026-10").at(-1).id==="drag-0"'),'Downward drop not saved');
 await prepare(1440,650,true);y=await edge(-1);x=await mouseStart('drag-0',y);
 await until('document.querySelector("tbody").firstElementChild.dataset.habitRow==="drag-0"','Stationary mouse failed to reach first offscreen row');
 await release(x,y);await stable();
 assert(await evaluate('habitRows("2026-10")[0].id==="drag-0"'),'Upward drop not saved');
 // Cancelling restores saved order and stops every scheduled animation frame.
 const order=await evaluate('habitRows("2026-10").map(r=>r.id).join(",")');
 await prepare(1440,650,false);y=await edge(1);x=await mouseStart('drag-0',y);await sleep(200);
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});await release(x,y);await stable();
 assert(await evaluate('habitRows("2026-10").map(r=>r.id).join(",")')===order,'Escape committed a cancelled order');
 // The same continuous loop must work for a touch pointer at a small viewport.
 await prepare(375,650,false);let pos=await positions('drag-0');y=await edge(1);
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...pos,id:1}]});
 await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:pos.x,y,id:1}]});
 await until('document.querySelector("tbody").lastElementChild.dataset.habitRow==="drag-0"','Stationary touch failed to reach last offscreen row');
 await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await stable();
 assert(await evaluate('habitRows("2026-10").at(-1).id==="drag-0"'),'Touch drop not saved');
 // Touch cancellation must not commit partially rearranged DOM order.
 const touchOrder=await evaluate('habitRows("2026-10").map(r=>r.id).join(",")');
 await prepare(375,650,true);pos=await positions('drag-0');y=await edge(-1);
 await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{...pos,id:2}]});
 await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:pos.x,y,id:2}]});await sleep(200);
 await send('Input.dispatchTouchEvent',{type:'touchCancel',touchPoints:[]});await stable();
 assert(await evaluate('habitRows("2026-10").map(r=>r.id).join(",")')===touchOrder,'Touch cancel committed reordered data');
 // Short grid: the page itself must scroll when the inner grid has no overflow.
 await evaluate('for(let i=9;i<36;i++)DB.habitTracker.items[habitRecordKey("2026-10","drag-"+i)].deleted=true;save();renderTodos()');
 await prepare(375,500,false);const beforePage=await evaluate('scrollY');pos=await positions('drag-1');y=await edge(1);x=await mouseStart('drag-1',y);
 await until('scrollY>'+beforePage+'+25','Outer page did not auto-scroll');
 await release(x,y);await stable();
 assert(await evaluate('JSON.stringify(DB.habitTracker.checks)')===ticks,'Drag modified ticks');
 assert(await evaluate('JSON.stringify(habitRows("2026-11"))')===otherMonth,'Drag modified another month');
 assert(await evaluate('!document.querySelector(".ht-dragging")&&DB.headNotes.legacy==="Keep notes"&&DB.course.done["1.0"]'),'Cleanup or prior data failed');
 const saved=await evaluate('habitRows("2026-10").map(r=>r.id).join(",")');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
 await evaluate('switchView("todo")');assert(await evaluate('habitRows("2026-10").map(r=>r.id).join(",")')===saved,'Drop order lost on refresh');
 assert(errors.length===0,'JS errors: '+errors.join('; '));
 console.log('PASS: stationary mouse up/down and touch across36 offscreen rows, inner-grid plus page auto-scroll, Escape/touch cancellation, stop on release, saved order/refresh, ticks and other-month preservation; no JS errors.');
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{if(ws)ws.close();browser.kill();});
