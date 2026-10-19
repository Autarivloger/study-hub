// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-japanese-design-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
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

 await evaluate('closeModal();DB=applyDefaults({japanese:{done:{"1.1.te":"2026-10-18","1.2.n4-te":"2026-10-18"},notes:{"1.1.te":"Keep my Japanese note","19.1":"Keep original reference"},checks:{},quizScores:{"1.1.te":75}},course:{done:{"1.0":"2026-10-18"}},headNotes:{legacy:"Keep other notes"}});save();switchView("japanese");closeModal()');
 for(const [width,height] of [[1440,1000],[375,900]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme)+';jpPage.mode="home";renderJapanese();closeModal();window.scrollTo(0,0)');
   await shot('home-'+width+'-'+theme);
   await evaluate('jpPage={mode:"week",week:1};renderJapanese();window.scrollTo(0,0)');
   await shot('week-'+width+'-'+theme);
   await evaluate('jpPage={mode:"lesson",week:1,lesson:"1.1"};renderJapanese();window.scrollTo(0,0)');
   await shot('lesson-'+width+'-'+theme);
  }
 }
 if(before){console.log('Before screenshots:',out);ws.close();return;}
 // Every type of Japanese screen at small phone, phone, tablet and desktop widths.
 const pages=[['home'],['week',1],['week',19],['week',36],['lesson','1.1'],['lesson','19.5.core'],['lesson','19.1'],['lesson','29.6'],['hard'],['meanings','home'],['meanings','opposites'],['meanings','synonyms'],['meanings','uploads'],['quick']];
 for(const [width,height] of [[1440,1000],[1024,900],[768,1024],[375,812],[320,640]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const [mode,value] of pages){
    await evaluate('closeModal();jpPage={mode:'+JSON.stringify(mode)+',week:19,lesson:'+JSON.stringify(mode==='lesson'?value:'1.1')+'};'+(mode==='week'?'jpPage.week='+value+';':'')+(mode==='meanings'?'JP_MEANING_STATE.tab='+JSON.stringify(value)+';JP_MEANING_STATE.query="";':'')+'renderJapanese();window.scrollTo(0,0)');
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Overflow '+width+' '+theme+' '+mode+' '+value);
    if(mode==='lesson')assert(await evaluate('!!document.querySelector("#jpNotes")&&!!document.querySelector("[data-jp-quiz]")&&!!document.querySelector("[data-jp-furigana]")'),'Lesson controls missing');
   }
  }
 }
 await evaluate('jpPage.mode="home";renderJapanese();window.scrollTo(0,0)');
 assert(await evaluate('document.querySelectorAll("[data-jp-week]").length===36&&!!document.querySelector("[data-jp-quick-start]")&&!!document.querySelector("[data-jp-meanings=home]")&&!!document.querySelector("[data-jp-hard-folder]")'),'Home learning actions/weeks missing');
 await evaluate('document.querySelector("[data-jp-quick-start]").click()');
 assert(await evaluate('jpPage.mode==="quick"&&!!document.querySelector("[data-jp-quick-exit]")'),'Quick review broken');
 await evaluate('document.querySelector("[data-jp-quick-exit]").click();document.querySelector("[data-jp-week=\\"1\\"]").click();document.querySelector("[data-jp-lesson=\\"1.1\\"]").click()');
 assert(await evaluate('document.querySelector("#jpNotes").value==="Keep my Japanese note"'),'Old notes lost');
 await evaluate('document.querySelector("[data-jp-furigana]").click()');
 assert(await evaluate('document.querySelectorAll("ruby rt").length>0'),'Furigana missing');
 await evaluate('document.querySelector(".jp-study-reveal").open=true;document.querySelector("[data-jp-hard-type]").click()');
 assert(await evaluate('!!document.querySelector(".jp-hard-btn.is-hard")'),'Hard marking broken');
 await evaluate('document.querySelector("#jpNotes").value="Updated Japanese note";document.querySelector("#jpNotes").dispatchEvent(new Event("input",{bubbles:true}));document.querySelector("[data-jp-check=read]").click()');
 assert(await evaluate('DB.japanese.notes["1.1.te"]==="Updated Japanese note"&&DB.japanese.quizScores["1.1.te"]===75&&DB.course.done["1.0"]&&DB.headNotes.legacy==="Keep other notes"'),'Saved data changed');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('DB.japanese.notes["1.1.te"]==="Updated Japanese note"&&DB.japanese.notes["19.1"]==="Keep original reference"&&DB.japanese.checks["1.1.te"].read'),'Refresh did not preserve notes/checks');
 assert(errors.length===0,'JS errors: '+errors.join('; '));
 console.log('PASS: Japanese home/week/lesson/hard/meanings/review at1440/1024/768/375/320 in both themes;36 weeks and study controls; Furigana/Hard/notes/checks/refresh; no JavaScript errors. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});
