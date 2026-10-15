// Real loopback Flask browser test. Only fictional sessions and disposable profiles.
const fs=require("fs"),os=require("os"),path=require("path"),assert=require("assert/strict");
const {spawn}=require("child_process");
const python="C:\\Users\\vlogerautari\\AppData\\Local\\Temp\\studyhub-w31-venv\\Scripts\\python.exe";
const folder=path.resolve("docs/python-week38");
const instance=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-w38-server-"));
const code=[
 "import sys",
 "from study_app import create_app",
 "from werkzeug.serving import make_server,WSGIRequestHandler",
 "class Quiet(WSGIRequestHandler):",
 "    def log(self,*args,**kwargs): pass",
 "app=create_app(instance_path=sys.argv[1])",
 "result=app.test_cli_runner().invoke(args=['init-db'])",
 "assert result.exit_code==0,result.output",
 "server=make_server('127.0.0.1',0,app,request_handler=Quiet)",
 "print('http://127.0.0.1:'+str(server.server_port),flush=True)",
 "server.serve_forever()"
].join("\n");
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
 const profile=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-w38-dashboard-"));
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
 await go("/","Your learning notes");
 assert(await evaluate('document.styleSheets.length===1&&document.querySelector(".skip").getAttribute("href")==="#main"'),"Local CSS/skip target missing");
 let shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
 fs.writeFileSync(path.join(os.tmpdir(),"studyhub-week38-project-desktop.png"),Buffer.from(shot.data,"base64"));
 async function account(name){
  await go("/auth/register","Create a practice account");
  await evaluate('document.querySelector("#username").value='+JSON.stringify(name)+';document.querySelector("#password").value="fictional-learning-passphrase"');
  await submit("form.stack","Sign in to your journal");
  await evaluate('document.querySelector("#username").value='+JSON.stringify(name)+';document.querySelector("#password").value="fictional-learning-passphrase"');
  await submit("form.stack","My learning posts");
 }
 await account("asha");
 await go("/posts/create","Write a learning post");
 assert(await evaluate('document.querySelector("#title").labels.length===1&&document.querySelector("#body").labels.length===1'),"Form labels missing");
 const scriptText="<script>window.__demoXSS=true</script>";
 await evaluate('document.querySelector("#title").value="Asha private post";document.querySelector("#body").value='+JSON.stringify(scriptText)+';document.querySelector("input[value=sql]").checked=true');
 await submit("form.stack","Asha private post");
 const firstPath=await evaluate('location.pathname');
 assert(await evaluate('!window.__demoXSS&&document.querySelector(".post-body").textContent.includes("<script>")'),"Stored text not safe");
 await go(firstPath+"/edit","Edit your post");
 await evaluate('document.querySelector("#title").value="Asha updated post";document.querySelector("#body").value="Persistent approved text"');
 await submit("form.stack","Asha updated post");
 await go("/posts/","My learning posts");
 await evaluate('document.querySelector("#q").value="updated";document.querySelector(".search").requestSubmit()');
 await wait('document.readyState==="complete"&&location.search==="?q=updated"&&document.querySelector(".grid").textContent.includes("Asha updated post")',"search");
 await evaluate('document.querySelector(".leave-form").requestSubmit()');
 await wait('document.readyState==="complete"&&location.pathname==="/"&&!document.querySelector(".leave-form")',"logout");
 await account("ben");
 assert(await evaluate('!document.querySelector("main").textContent.includes("Asha updated post")'),"Private list leaked");
 await go(firstPath,"Request 404");
 await go("/posts/create","Write a learning post");
 await evaluate('document.querySelector("#title").value="Ben local post";document.querySelector("#body").value="Only Ben can edit this."');
 await submit("form.stack","Ben local post");
 const benPath=await evaluate('location.pathname');
 await send("Emulation.setDeviceMetricsOverride",{width:375,height:812,deviceScaleFactor:1,mobile:true});
 for(const [target,heading] of [["/","Your learning notes"],["/posts/","My learning posts"],[benPath,"Ben local post"],[benPath+"/edit","Edit your post"],["/posts/create","Write a learning post"]]){
  await go(target,heading);assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),"Mobile overflow "+target);
 }
 await go(benPath,"Ben local post");
 shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
 fs.writeFileSync(path.join(os.tmpdir(),"studyhub-week38-project-mobile.png"),Buffer.from(shot.data,"base64"));
 await evaluate('document.querySelector("details").open=true;document.querySelector("details form").requestSubmit()');
 await wait('document.readyState==="complete"&&document.querySelector("h1")?.textContent.includes("My learning posts")',"delete redirect");
 await go(benPath,"Request 404");
 assert.equal(errors.length,0,errors.join("; "));
 console.log("PASS: Week38 actual loopback two-account registration/login, private CRUD/search/escaping/logout, other-owner denial, local CSS/labels, 375px pages and no JavaScript errors.");
}
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(()=>{channel?.close();browser?.kill();server.kill();});
