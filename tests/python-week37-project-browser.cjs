// Real loopback Flask browser test. Only fictional sessions and disposable profiles.
const fs=require("fs"),os=require("os"),path=require("path"),assert=require("assert/strict");
const {spawn}=require("child_process");
const python="C:\\Users\\vlogerautari\\AppData\\Local\\Temp\\studyhub-w31-venv\\Scripts\\python.exe";
const folder=path.resolve("docs/python-week37");
const code=[
 "from app import create_app",
 "from werkzeug.serving import make_server,WSGIRequestHandler",
 "class Quiet(WSGIRequestHandler):",
 "    def log(self,*args,**kwargs): pass",
 "server=make_server('127.0.0.1',0,create_app(),request_handler=Quiet)",
 "print('http://127.0.0.1:'+str(server.server_port),flush=True)",
 "server.serve_forever()"
].join("\n");
const server=spawn(python,["-u","-c",code],{cwd:folder,stdio:["ignore","pipe","pipe"]});
let serverOutput="",serverErrors="";
server.stdout.on("data",b=>serverOutput+=b.toString());
server.stderr.on("data",b=>serverErrors+=b.toString());
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let browser,channel;
async function main(){
 for(let i=0;i<100&&!serverOutput.includes("\n");i++)await sleep(100);
 const base=serverOutput.trim().split("\n")[0];
 assert.match(base,/^http:\/\/127\.0\.0\.1:\d+$/,"Local server failed: "+serverErrors);
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-w37-dashboard-"));
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
 const go=async(target,heading)=>{
  await send("Page.navigate",{url:base+target});
  await wait('document.readyState==="complete"&&document.querySelector("h1")?.textContent.includes('+JSON.stringify(heading)+')',target);
 };
 const submit=async(selector,heading)=>{
  await evaluate('document.querySelector('+JSON.stringify(selector)+').requestSubmit()');
  await wait('document.readyState==="complete"&&document.querySelector("h1")?.textContent.includes('+JSON.stringify(heading)+')',heading);
 };
 await send("Runtime.enable");await send("Page.enable");
 await send("Emulation.setDeviceMetricsOverride",{width:1280,height:900,deviceScaleFactor:1,mobile:false});
 await go("/","A small desk");
 assert(await evaluate('document.styleSheets.length===1&&getComputedStyle(document.body).fontFamily.includes("system-ui")'),"Local CSS missing");
 assert(await evaluate('document.querySelector(".skip").getAttribute("href")==="#main"'),"Skip link missing");
 let shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
 fs.writeFileSync(path.join(os.tmpdir(),"studyhub-week37-project-desktop.png"),Buffer.from(shot.data,"base64"));
 await go("/lessons","Find a sample");
 await evaluate('document.querySelector("#q").value="HTTP"');
 await evaluate('document.querySelector(".search").requestSubmit()');
 await wait('location.search==="?q=HTTP"&&document.readyState==="complete"&&document.querySelectorAll(".grid article").length===1',"search results");
 assert(await evaluate('document.querySelector(".grid").textContent.includes("HTTP request cycle")&&!document.querySelector(".grid").textContent.includes("SQL joins")'));
 await go("/enter","Open the demo");
 assert(await evaluate('document.querySelector("#display_name").labels.length===1'),"Entry field has no label");
 await evaluate('document.querySelector("#display_name").value="Asha"');
 await submit('form[action="/enter"]',"practice planner");
 assert(await evaluate('location.pathname==="/planner"'),"Entry did not redirect");
 const malicious="<script>window.__demoXSS=true</script>";
 await evaluate('document.querySelector("#body").value='+JSON.stringify(malicious));
 await evaluate('document.querySelector("form[action=\\"/notes\\"]").requestSubmit()');
 await wait('document.readyState==="complete"&&document.querySelector(".note")?.textContent.includes('+JSON.stringify(malicious)+')',"saved note");
 assert(await evaluate('!window.__demoXSS&&document.querySelectorAll(".note").length===1'),"User text executed or note missing");
 await go("/settings","Demo display");
 await evaluate('document.querySelector("#theme").value="dark";document.querySelector("form[action=\\"/settings\\"]").requestSubmit()');
 await wait('document.readyState==="complete"&&document.documentElement.dataset.theme==="dark"',"dark preference");
 assert(await evaluate('getComputedStyle(document.body).backgroundColor==="rgb(20, 32, 29)"'),"Dark CSS not applied");
 await send("Emulation.setDeviceMetricsOverride",{width:375,height:812,deviceScaleFactor:1,mobile:true});
 for(const [target,heading] of [["/","A small desk"],["/lessons","Find a sample"],["/lessons/1","HTTP request cycle"],["/planner","practice planner"],["/settings","Demo display"],["/about","Small pieces"]]){
  await go(target,heading);
  assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),"Mobile overflow "+target);
 }
 await go("/planner","practice planner");
 shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
 fs.writeFileSync(path.join(os.tmpdir(),"studyhub-week37-project-mobile.png"),Buffer.from(shot.data,"base64"));
 await evaluate('document.querySelector("form[action=\\"/leave\\"]").requestSubmit()');
 await wait('document.readyState==="complete"&&location.pathname==="/"&&!document.querySelector(".leave-form")',"leave demo");
 await send("Page.navigate",{url:base+"/planner"});
 await wait('document.readyState==="complete"&&location.pathname==="/enter"',"gate after leave");
 assert.equal(errors.length,0,errors.join("; "));
 console.log("PASS: actual loopback Flask browser navigation/search/detail/CSRF entry/note/escaping/theme/leave, local CSS, labels/skip link, 375px dashboard pages and no JavaScript errors.");
}
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{channel?.close();browser?.kill();server.kill();});
