// Real browser + real loopback API, with owned temporary files and fictional users.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict'),{spawn}=require('child_process');
const python=process.env.PYTHON||(process.platform==='win32'?'C:\\Users\\vlogerautari\\AppData\\Local\\Temp\\studyhub-w31-venv\\Scripts\\python.exe':'python');
const chrome=process.env.CHROME_PATH||(process.platform==='win32'?'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe':'/usr/bin/google-chrome');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-w43-browser-'));
const code='import socket,sys,uvicorn\nfrom orm_api import create_app\nsock=socket.socket();sock.bind(("127.0.0.1",0))\nprint("http://127.0.0.1:"+str(sock.getsockname()[1]),flush=True)\nuvicorn.Server(uvicorn.Config(create_app(sys.argv[1]),log_level="critical",access_log=False)).run(sockets=[sock])';
const server=spawn(python,['-B','-u','-c',code,path.join(profile,'instance')],{cwd:__dirname,stdio:['ignore','pipe','pipe']});
let output='',serverError='',browser,ws;
server.stdout.on('data',b=>output+=b);server.stderr.on('data',b=>serverError+=b);
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
 for(let i=0;i<100&&!output.includes('\n');i++)await sleep(100);
 const base=output.trim().split('\n')[0];assert.match(base,/^http:\/\/127\.0\.0\.1:\d+$/,'Owned server failed: '+serverError);
 browser=spawn(chrome,['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+path.join(profile,'chrome'),base],{stdio:'ignore'});
 let port;for(let i=0;i<100;i++){const p=path.join(profile,'chrome','DevToolsActivePort');if(fs.existsSync(p)){port=Number(fs.readFileSync(p,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome did not start');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0,failWrite=false,failTags=false,holdRead=false,held=null;const pending=new Map(),errors=[],external=[];
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 ws.onmessage=event=>{
  const m=JSON.parse(event.data);
  if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}
  if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);
  if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));
  if(m.method==='Network.requestWillBeSent'){const u=m.params.request.url;if(!u.startsWith(base+'/')&&!u.startsWith('data:'))external.push(u);}
  if(m.method==='Fetch.requestPaused'){
   const p=m.params,r=p.request;
   if(holdRead&&r.method==='GET'&&r.url.includes('q=slow')){held=p.requestId;holdRead=false;return;}
   if((failWrite&&r.method==='POST')||(failTags&&r.method==='PUT'&&r.url.includes('/tags'))){failWrite=false;failTags=false;send('Fetch.fulfillRequest',{requestId:p.requestId,responseCode:503,responseHeaders:[{name:'Content-Type',value:'application/json'}],body:Buffer.from('{"detail":"fictional unavailable"}').toString('base64')}).catch(e=>errors.push(e.message));}
   else send('Fetch.continueRequest',{requestId:p.requestId}).catch(e=>errors.push(e.message));
  }
 };
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 async function wait(expression,label){for(let i=0;i<180;i++){try{if(await evaluate(expression))return;}catch{}await sleep(70);}throw Error('Did not settle: '+label+'; '+await evaluate('document.querySelector("#message")?.textContent'));}
 const click=selector=>evaluate('document.querySelector('+JSON.stringify(selector)+').click()');
 const fill=(id,value)=>evaluate('document.getElementById('+JSON.stringify(id)+').value='+JSON.stringify(value));
 const idle=()=>wait('!document.querySelector("#editorFields").disabled','mutation completed');
 const rows=()=>evaluate('document.querySelectorAll(".note").length');
 async function auth(name,register=true){await fill('username',name);await fill('password','fictional-learning-passphrase');if(register)await click('#register');else await evaluate('document.querySelector("#authForm").requestSubmit()');await wait('!document.querySelector("#workspace").hidden&&!document.querySelector("#editorFields").disabled','sign in');}
 async function search(q='',completed=''){await fill('query',q);await fill('completion',completed);await evaluate('document.querySelector("#searchForm").requestSubmit()');await wait('document.querySelector("#notes").getAttribute("aria-busy")==="false"','search');}
 async function save(title,body='A fictional thought'){await fill('noteTitle',title);await fill('noteBody',body);await evaluate('document.querySelector("#noteForm").requestSubmit()');await idle();}
 await send('Runtime.enable');await send('Page.enable');await send('Network.enable');await send('Fetch.enable',{patterns:[{urlPattern:'*/v1/notes*',requestStage:'Request'}]});await send('Page.navigate',{url:base+'/'});
 await wait('document.querySelector("#authForm")','dashboard');await auth('asha');assert.equal(await rows(),0);
 const injection='<img src=x onerror="window.demoXSS=true">';await save('100% learning',injection);assert.equal(await rows(),1);assert(!await evaluate('Boolean(window.demoXSS)'),'Stored text executed');
 await click('.note [data-action="edit"]');await idle();await evaluate('document.querySelector("#noteTags").options[1].selected=true');await save('100% revised',injection);
 await click('.note [data-action="edit"]');await idle();assert(await evaluate('document.querySelector("#noteTags").options[1].selected'),'Tags not retained');await click('#cancelEdit');
 await search('%');assert.equal(await rows(),1);await search('_');assert.equal(await rows(),0);await search('','false');assert.equal(await rows(),1);await click('.note [data-action="toggle"]');await idle();assert.equal(await rows(),0);await search('','true');assert.equal(await rows(),1);await search();
 await click('.note [data-action="delete"]');assert(await evaluate('document.querySelector("#deleteDialog").open'));await click('#cancelDelete');assert.equal(await rows(),1);
 failWrite=true;await save('Retry me');assert(await evaluate('document.querySelector("#noteTitle").value==="Retry me"&&document.querySelector("#message").dataset.error==="true"'),'Failed write lost draft');assert.equal(await rows(),1);
 failTags=true;await save('Retry me');assert.equal(await rows(),2);assert(await evaluate('document.querySelector("#message").textContent.includes("note was saved")'),'Partial save unclear');await save('Retry me');assert.equal(await rows(),2,'Retry duplicated note');
 holdRead=true;await fill('query','slow');await evaluate('document.querySelector("#searchForm").requestSubmit()');for(let i=0;i<100&&!held;i++)await sleep(50);assert(held,'Slow read not held');await click('#logout');await wait('!document.querySelector("#auth").hidden&&!document.querySelector("#authFields").disabled','sign out');
 await send('Fetch.fulfillRequest',{requestId:held,responseCode:200,responseHeaders:[{name:'Content-Type',value:'application/json'}],body:Buffer.from(JSON.stringify({total:1,offset:0,limit:5,items:[{id:99,title:'OLD PRIVATE ROW',body:'old',completed:false}]})).toString('base64')});await sleep(100);assert.equal(await rows(),0,'Old response repopulated signed-out UI');
 await auth('ben');assert.equal(await rows(),0,'Other owner saw notes');
 const tokenResponse=await fetch(base+'/v1/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({username:'ben',password:'fictional-learning-passphrase'})});const other=(await tokenResponse.json()).access_token;
 assert.equal((await fetch(base+'/v1/notes/1',{headers:{Authorization:'Bearer '+other}})).status,404,'Other owner read allowed');
 await click('#logout');await idle();await auth('asha',false);assert.equal(await rows(),2);
 const login=await fetch(base+'/v1/token',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams({username:'asha',password:'fictional-learning-passphrase'})});const token=(await login.json()).access_token;
 for(let n=0;n<6;n++)assert.equal((await fetch(base+'/v1/notes',{method:'POST',headers:{Authorization:'Bearer '+token,'Content-Type':'application/json'},body:JSON.stringify({title:'Page fixture '+n,body:'Pagination practice'})})).status,201);
 await search();assert.equal(await rows(),5);await click('#next');await wait('document.querySelector("#pageLabel").textContent==="Page 2 of 2"','second page');assert.equal(await rows(),3);
 for(let n=0;n<3;n++){await click('.note [data-action="delete"]');await click('#confirmDelete');await idle();}
 assert(await evaluate('document.querySelector("#pageLabel").textContent==="Page 1 of 1"'),'Deleting last page did not recover');assert.equal(await rows(),5);
 await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});await evaluate('scrollTo(0,0)');let shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-week43-project-desktop.png'),Buffer.from(shot.data,'base64'));
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});for(const theme of ['dark','light']){await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Mobile overflow '+theme);}await evaluate('document.querySelector("#workspace").scrollIntoView()');shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-week43-project-mobile.png'),Buffer.from(shot.data,'base64'));
 await send('Page.reload',{ignoreCache:true});await wait('document.querySelector("#authForm")','reload');assert(await evaluate('!document.querySelector("#auth").hidden&&localStorage.length===0&&sessionStorage.length===0'),'Credentials persisted');
 assert.equal(external.length,0,'External asset requested');assert.equal(errors.length,0,errors.join('; '));
 console.log('PASS: real Week43 dashboard/auth/CRUD/tags/literal search/filter/pagination; two-owner denial; XSS text; failed-write draft and partial-save retry; stale read after logout; reload credentials cleared;375px themes and no JS errors.');
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{ws?.close();browser?.kill();server.kill();});
