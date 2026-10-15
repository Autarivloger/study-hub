// Real loopback FastAPI browser test. Only fictional sessions and disposable profiles.
const fs=require("fs"),os=require("os"),path=require("path"),assert=require("assert/strict");
const {spawn}=require("child_process");
const python="C:\\Users\\vlogerautari\\AppData\\Local\\Temp\\studyhub-w31-venv\\Scripts\\python.exe";
const folder=path.resolve("docs/python-week39");
const instance=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-w39-server-"));
const code="import socket,sys,uvicorn\nfrom learning_api import create_app\nsock=socket.socket();sock.bind((\"127.0.0.1\",0))\nprint(\"http://127.0.0.1:\"+str(sock.getsockname()[1]),flush=True)\nserver=uvicorn.Server(uvicorn.Config(create_app(sys.argv[1]),log_level=\"critical\",access_log=False))\nserver.run(sockets=[sock])";
const server=spawn(python,["-B","-u","-c",code,instance],{cwd:folder,stdio:["ignore","pipe","pipe"]});
let serverOutput="",serverErrors="";
server.stdout.on("data",b=>serverOutput+=b.toString());
server.stderr.on("data",b=>serverErrors+=b.toString());
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let browser,channel;
async function main(){
 for(let i=0;i<100&&!serverOutput.includes("\n");i++)await sleep(100);
 const base=serverOutput.trim().split("\n")[0];
 assert.match(base,/^http:\/\/127\.0\.0\.1:\d+$/,"Local server failed: "+serverErrors);
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-w39-dashboard-"));
 browser=spawn("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",[
  "--headless=new","--disable-gpu","--no-sandbox","--no-first-run",
  "--remote-debugging-port=0","--user-data-dir="+profile,base
 ],{stdio:"ignore"});
 let port;
 for(let i=0;i<100;i++){
  const file=path.join(profile,"DevToolsActivePort");
  if(fs.existsSync(file)){port=Number(fs.readFileSync(file,"utf8").split("\n")[0]);break;}
  await sleep(100);
 }
 assert(port,"Chrome did not start");
 const tabs=await(await fetch("http://127.0.0.1:"+port+"/json/list")).json();
 channel=new WebSocket(tabs.find(t=>t.type==="page").webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{channel.onopen=resolve;channel.onerror=reject;});
 let seq=0;const pending=new Map(),errors=[];
 channel.onmessage=event=>{
  const msg=JSON.parse(event.data);
  if(msg.method==="Runtime.exceptionThrown")errors.push(msg.params.exceptionDetails.text);
  if(msg.method==="Runtime.consoleAPICalled"&&msg.params.type==="error")errors.push(msg.params.args.map(x=>x.value||x.description).join(" "));
  if(msg.id&&pending.has(msg.id)){const p=pending.get(msg.id);pending.delete(msg.id);msg.error?p.reject(Error(JSON.stringify(msg.error))):p.resolve(msg.result);}
 };
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});channel.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{
  const result=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
  if(result.exceptionDetails)throw Error(result.exceptionDetails.exception?.description||result.exceptionDetails.text);
  return result.result.value;
 };
 async function wait(expression,label){
  for(let i=0;i<100;i++){try{if(await evaluate(expression))return;}catch{}await sleep(60);}
  throw Error("Page did not settle: "+label);
 }
 await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
 const external=[];
 const listener=channel.onmessage;
 channel.onmessage=event=>{
  const message=JSON.parse(event.data);
  if(message.method==='Network.requestWillBeSent'){
   const url=message.params.request.url;
   if(!url.startsWith(base+'/')&&!url.startsWith('data:'))external.push(url);
  }
  listener(event);
 };
 await send('Page.navigate',{url:base+'/docs'});
 await wait('document.querySelectorAll("#operations details").length===11','generated explorer operations');
 assert(await evaluate('document.querySelector("#status").textContent.includes("No internet required")'),'Local schema did not load');
 assert(await evaluate('document.styleSheets.length===1'),'Local CSS missing');
 async function call(method,route,body,params={}){
  const key=method+' '+route;
  await evaluate('(()=>{const card=[...document.querySelectorAll("details")].find(c=>c.dataset.operation==='+JSON.stringify(key)+');if(!card)throw Error("Operation missing");card.open=true;'+
   (body===undefined?'':route==='/v1/token'?'const inputs=card.querySelectorAll("input");inputs[0].value='+JSON.stringify(body.username)+';inputs[1].value='+JSON.stringify(body.password)+';':'card.querySelector("textarea").value='+JSON.stringify(JSON.stringify(body))+';')+
   'for(const [name,value] of Object.entries('+JSON.stringify(params)+')){const label=[...card.querySelectorAll("label")].find(l=>l.textContent.endsWith(" · "+name));document.getElementById(label.htmlFor).value=value;}card.querySelector("pre").textContent="Waiting";card.querySelector("button").click();})()');
  const resultExpr='[...document.querySelectorAll("details")].find(c=>c.dataset.operation==='+JSON.stringify(key)+').querySelector("pre").textContent';
  await wait(resultExpr+'!=="Waiting"&&/^\\d{3} /.test('+resultExpr+')',key);
  return await evaluate(resultExpr);
 }
 async function account(name){
  const created=await call('post','/v1/users',{username:name,password:'fictional-learning-passphrase'});
  assert(created.startsWith('201 '),'Registration failed');
  const token=await call('post','/v1/token',{username:name,password:'fictional-learning-passphrase'});
  assert(token.startsWith('200 ')&&token.includes('[kept in this tab only]'),'Token response was not masked');
  assert(await evaluate('document.querySelector("#bearer").type==="password"&&document.querySelector("#bearer").value.length>20'),'Bearer not loaded');
 }
 await account('asha');
 assert(await evaluate('!document.querySelector(\'[data-operation="post /v1/users"] textarea\').value.includes("fictional-learning-passphrase")'),'Registration password not cleared');
 const injection='<script>window.__demoXSS=true</script>';
 let result=await call('post','/v1/notes',{title:'Private browser note',body:injection,completed:false});
 assert(result.startsWith('201 '),'Create failed');
 const note=JSON.parse(result.slice(result.indexOf('\n')+1));
 assert(note.body===injection&&!await evaluate('Boolean(window.__demoXSS)'),'Response text executed');
 result=await call('patch','/v1/notes/{note_id}',{completed:true},{note_id:String(note.id)});
 assert(JSON.parse(result.slice(result.indexOf('\n')+1)).completed===true,'Patch failed');
 result=await call('put','/v1/notes/{note_id}',{title:'Updated browser note',body:'All fields replaced',completed:false},{note_id:String(note.id)});
 assert(JSON.parse(result.slice(result.indexOf('\n')+1)).completed===false,'PUT False lost');
 result=await call('get','/v1/notes',undefined,{q:'Updated'});
 assert(JSON.parse(result.slice(result.indexOf('\n')+1)).total===1,'UI query filtering failed');
 await evaluate('window.__ashaToken=document.querySelector("#bearer").value');
 await account('ben');
 result=await call('get','/v1/notes',undefined,{q:''});
 assert(JSON.parse(result.slice(result.indexOf('\n')+1)).total===0,'Other owner collection leaked');
 assert((await call('get','/v1/notes/{note_id}',undefined,{note_id:String(note.id)})).startsWith('404 '),'Cross-owner read allowed');
 assert((await call('delete','/v1/notes/{note_id}',undefined,{note_id:String(note.id)})).startsWith('404 '),'Cross-owner delete allowed');
 await evaluate('document.querySelector("#bearer").value=window.__ashaToken;document.querySelector("#bearer").dispatchEvent(new Event("input"))');
 assert((await call('delete','/v1/notes/{note_id}',undefined,{note_id:String(note.id)})).startsWith('204 '),'Delete failed');
 assert((await call('post','/v1/logout')).startsWith('204 '),'Logout failed');
 assert(await evaluate('document.querySelector("#bearer").value===""'),'Logout did not clear bearer');
 await evaluate('document.querySelector("#bearer").value=window.__ashaToken');
 assert((await call('get','/v1/me')).startsWith('401 '),'Revoked token replay succeeded');
 await evaluate('document.querySelector("#forget").click();window.__ashaToken=null');
 assert(await evaluate('localStorage.length===0&&sessionStorage.length===0'),'Credentials persisted in web storage');
 await send('Emulation.setDeviceMetricsOverride',{width:1280,height:900,deviceScaleFactor:1,mobile:false});
 await evaluate('scrollTo(0,0)');
 let shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 fs.writeFileSync(path.join(os.tmpdir(),'studyhub-week39-project-desktop.png'),Buffer.from(shot.data,'base64'));
 await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
 for(const scheme of ['light','dark']){
  await send('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:scheme}]});
  assert(await evaluate('(()=>{for(const card of document.querySelectorAll("details"))card.open=true;return document.documentElement.scrollWidth<=innerWidth+1;})()'),'375px explorer overflow in '+scheme);
 }
 await evaluate('scrollTo(0,0)');
 shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 fs.writeFileSync(path.join(os.tmpdir(),'studyhub-week39-project-mobile.png'),Buffer.from(shot.data,'base64'));
 await send('Page.reload',{ignoreCache:true});
 await wait('document.querySelectorAll("#operations details").length===11','reload');
 assert(await evaluate('document.querySelector("#bearer").value===""'),'Reload retained bearer');
 assert.equal(external.length,0,'Explorer requested an external asset');
 assert.equal(errors.length,0,errors.join('; '));
 console.log('PASS: Week39 real loopback original explorer, generated schema, two fictional accounts/private CRUD/search, masked token and cleared passwords, logout replay denial, no web-storage credentials/XSS/external assets, 375px light/dark and no JavaScript errors.');
}
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{channel?.close();browser?.kill();server.kill();});
