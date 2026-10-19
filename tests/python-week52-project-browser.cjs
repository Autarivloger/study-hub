// Owned localhost server and disposable Chrome profile; synthetic records only.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process');
const project=path.resolve(__dirname,'../docs/python-week52');
const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub52-project-'));
const python=process.env.STUDY_HUB_PYTHON||'python';
const environment={...process.env,CAPSTONE_DB:path.join(temporary,'browser.sqlite'),PYTHONUTF8:'1'};
delete environment.CAPSTONE_TOKEN;delete environment.CAPSTONE_PUBLIC;delete environment.PYTHONPATH;
const server=spawn(python,['-m','uvicorn','capstone.main:app','--host','127.0.0.1','--port','0'],{cwd:project,env:environment,stdio:['ignore','ignore','pipe']});
let serverLog='',browser,ws;server.stderr.on('data',data=>{serverLog=(serverLog+data).slice(-16000);});
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const watchdog=setTimeout(()=>{console.error('Capstone browser test timed out');browser?.kill();server.kill();process.exit(1);},120000);
async function main(){
 let port;for(let i=0;i<100;i++){const match=serverLog.match(/http:\/\/127\.0\.0\.1:(\d+)/);if(match){port=Number(match[1]);break;}if(server.exitCode!==null)throw Error(serverLog);await sleep(100);}assert(port,'Server startup');
 const profile=path.join(temporary,'chrome');
 browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,'http://127.0.0.1:'+port],{stdio:'ignore'});
 let debugPort;for(let i=0;i<100;i++){const file=path.join(profile,'DevToolsActivePort');if(fs.existsSync(file)){debugPort=Number(fs.readFileSync(file,'utf8').split('\n')[0]);break;}await sleep(100);}assert(debugPort,'Chrome startup');
 const tabs=await(await fetch('http://127.0.0.1:'+debugPort+'/json/list')).json();ws=new WebSocket(tabs.find(tab=>tab.type==='page').webSocketDebuggerUrl);await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
 let seq=0,dialogAccept=true,dialogs=0;const pending=new Map(),errors=[];
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq,timer=setTimeout(()=>{pending.delete(id);reject(Error('Timed out: '+method));},15000);pending.set(id,{resolve:value=>{clearTimeout(timer);resolve(value);},reject:error=>{clearTimeout(timer);reject(error);}});ws.send(JSON.stringify({id,method,params}));});
 ws.onmessage=event=>{const message=JSON.parse(event.data);if(message.method==='Runtime.exceptionThrown')errors.push(message.params.exceptionDetails.exception?.description||message.params.exceptionDetails.text);if(message.method==='Runtime.consoleAPICalled'&&message.params.type==='error')errors.push(message.params.args.map(value=>value.value||value.description).join(' '));if(message.method==='Page.javascriptDialogOpening'){dialogs++;send('Page.handleJavaScriptDialog',{accept:dialogAccept}).catch(error=>errors.push(error.message));}if(message.id&&pending.has(message.id)){const handler=pending.get(message.id);pending.delete(message.id);message.error?handler.reject(Error(JSON.stringify(message.error))):handler.resolve(message.result);}};
 const evaluate=async expression=>{const result=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture:true});if(result.exceptionDetails)throw Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text);return result.result.value;};
 async function wait(expression,label){for(let i=0;i<100;i++){if(await evaluate(expression))return;await sleep(60);}throw Error('Did not settle: '+label);}
 await send('Runtime.enable');await send('Page.enable');
 await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
 await wait('document.getElementById("totals")?.textContent.includes("0 sessions")','empty state');
 const hostile='<img src=x onerror="window.__unwanted=1">';
 await evaluate('document.getElementById("day").value="2026-10-19";document.getElementById("subject").value="Python";document.getElementById("minutes").value="25";document.getElementById("note").value='+JSON.stringify(hostile)+';document.getElementById("sessionForm").requestSubmit()');
 await wait('document.getElementById("totals").textContent.includes("1 sessions")&&document.querySelector(".session")?.textContent.includes("25 min")','saved row');
 assert(await evaluate('document.querySelector(".session p").textContent==='+JSON.stringify(hostile)+'&&!document.querySelector("#sessions img")&&window.__unwanted===undefined'),'Saved note became HTML');
 await evaluate('document.querySelector(".session button").click();document.getElementById("minutes").value="30";document.getElementById("sessionForm").requestSubmit()');
 await wait('document.querySelector(".session")?.textContent.includes("30 min")&&document.getElementById("totals").textContent.includes("30 minutes")','edit');
 await evaluate('document.querySelector(".session button").click();document.getElementById("subject").value="Not saved";document.getElementById("cancelEdit").click()');
 assert(await evaluate('document.getElementById("subject").value===""&&document.getElementById("cancelEdit").hidden'),'Cancel edit');
 await evaluate('document.getElementById("filterDay").value="2026-10-20";document.getElementById("filter").click()');
 await wait('document.getElementById("totals").textContent.includes("0 sessions")&&!document.querySelector(".session")','date filter');
 await evaluate('document.getElementById("clearFilter").click()');await wait('!!document.querySelector(".session")','clear filter');
 await evaluate('(async()=>{for(let i=0;i<11;i++){const r=await fetch("/api/sessions",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({day:"2026-10-18",subject:"Fixture "+i,minutes:5})});if(!r.ok)throw Error("fixture creation");}document.getElementById("clearFilter").click();})()');
 await wait('document.querySelectorAll(".session").length===10&&document.getElementById("totals").textContent.includes("12 sessions")','page one');
 await evaluate('document.getElementById("next").click()');await wait('document.querySelectorAll(".session").length===2&&document.getElementById("pageLabel").textContent==="Page 2"','page two');
 await evaluate('document.getElementById("previous").click()');await wait('document.getElementById("pageLabel").textContent==="Page 1"','return page');
 dialogAccept=false;await evaluate('document.querySelectorAll(".session button")[1].click()');assert(dialogs===1,'Delete confirmation missing');
 assert(await evaluate('document.getElementById("totals").textContent.includes("12 sessions")'),'Cancelled delete removed data');
 dialogAccept=true;await evaluate('document.querySelectorAll(".session button")[1].click()');await wait('document.getElementById("totals").textContent.includes("11 sessions")','confirmed delete');
 await send('Page.reload',{ignoreCache:true});await wait('document.getElementById("totals")?.textContent.includes("11 sessions")','refresh persistence');
 for(const [width,height] of [[1440,1000],[375,812],[320,568]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  await send('Emulation.setTouchEmulationEnabled',{enabled:width<600});
  for(const theme of ['light','dark']){
   await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:theme}]});
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Layout overflow '+width+' '+theme);
   assert(await evaluate('[...document.querySelectorAll("button")].filter(e=>e.getBoundingClientRect().height>0).every(e=>e.getBoundingClientRect().height>=44)'),'Small touch button');
   if(width!==320){const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-week52-project-'+width+'-'+theme+'.png'),Buffer.from(shot.data,'base64'));}
  }
 }
 assert.deepEqual(errors,[],'Browser errors');
 console.log('PASS: real capstone UI create/edit/cancel/filter/pagination/delete-confirmation/refresh, inert note text, 3 widths, light/dark and accessible touch sizes; no JS errors.');
}
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);ws?.close();browser?.kill();server.kill();});
