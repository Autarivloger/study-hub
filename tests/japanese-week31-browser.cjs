// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-japanese-week31-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-design-profile-'));
const fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=expression=>eval(expression);\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const watchdog=setTimeout(()=>{console.error('Design check timed out');browser.kill();process.exit(1);},180000);
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

 await evaluate('closeModal();DB=applyDefaults({japanese:{done:{"1.1.te":"2026-10-18"},notes:{"1.1.te":"Keep old Japanese note"},checks:{},quizScores:{"1.1.te":75}},course:{done:{"1.0":"2026-10-18"},notes:{"1.0":"Keep Python note"}},headNotes:{legacy:"Keep heading note"}});save();switchView("japanese");closeModal()');
 await evaluate('document.querySelector("[data-jp-week=\\"31\\"]").click()');
 assert(await evaluate('jpPage.week===31&&jpWeekLessons(31).length===7&&new Set([...document.querySelectorAll("[data-jp-lesson^=\\"31.\\"]")].map(b=>b.dataset.jpLesson)).size===7'),'Week 31 seven day buttons');
 await evaluate('document.querySelector("[data-jp-lesson=\\"31.1\\"]").click()');
 assert(await evaluate('!DB.japanese.done["31.1"]'),'Opening must not auto-complete');
 // Controlled speech adapter verifies offline selection and lifecycle; no claim of audible output.
 await evaluate(`window.__jpVoices=[];window.__jpSpoken=[];window.__jpCancels=0;
 Object.defineProperty(window,'SpeechSynthesisUtterance',{configurable:true,value:function(text){this.text=text;}});
 Object.defineProperty(window,'speechSynthesis',{configurable:true,value:{getVoices:()=>window.__jpVoices,cancel:()=>window.__jpCancels++,speak:u=>window.__jpSpoken.push(u)}});undefined;`);
 assert(await evaluate('!document.querySelector(".jp-listening-transcript").open&&window.__jpSpoken.length===0'),'Transcript closed; no autoplay');
 await evaluate('document.querySelector("[data-jp-listen=\\"1\\"]").click()');
 assert(await evaluate('window.__jpSpoken.length===0&&document.getElementById("jpListeningStatus").textContent.includes("No offline Japanese")'),'No voice fallback');
 await evaluate('window.__jpVoices=[{lang:"ja-JP",localService:false,name:"Remote Japanese"}];document.querySelector("[data-jp-listen=\\"1\\"]").click()');
 assert.equal(await evaluate('window.__jpSpoken.length'),0,'Remote voice must never be used');
 await evaluate('window.__jpVoices.push({lang:"ja-JP",localService:true,name:"Installed Japanese"});document.querySelector("[data-jp-listen=\\"1\\"]").click()');
 assert(await evaluate('window.__jpSpoken.at(-1).text===JP_LESSONS.find(l=>l.id==="31.1").reading&&window.__jpSpoken.at(-1).rate===1&&window.__jpSpoken.at(-1).voice.localService&&!document.querySelector(".jp-listening-transcript").open'),'Local-only playback and hidden transcript');
 await evaluate('document.querySelector("[data-jp-listen=\\"0.8\\"]").click()');
 assert(await evaluate('window.__jpSpoken.at(-1).rate===.8'),'Slow speed');
 await evaluate('document.querySelector("[data-jp-stop]").click()');
 assert(await evaluate('jpSpeechCurrent===null&&document.getElementById("jpListeningStatus").textContent.startsWith("Stopped")'),'Stop');
 await evaluate('document.querySelector("[data-jp-listen=\\"1\\"]").click();window.__jpSpoken.at(-1).onend()');
 assert(await evaluate('jpSpeechCurrent===null&&document.getElementById("jpListeningStatus").textContent.startsWith("Finished")'),'Completion status');
 await evaluate('document.querySelector("[data-jp-listen=\\"1\\"]").click();window.__jpSpoken.at(-1).onerror()');
 assert(await evaluate('jpSpeechCurrent===null&&document.getElementById("jpListeningStatus").textContent.includes("failed")'),'Failure status');
 await evaluate('document.querySelector("[data-jp-listen=\\"1\\"]").click();switchView("course")');
 assert(await evaluate('jpSpeechCurrent===null'),'Leaving Japanese stops playback');
 await evaluate('switchView("japanese");jpPage={mode:"lesson",week:30,lesson:"30.1"};renderJapanese()');
 assert(await evaluate('!document.querySelector(".jp-listening-transcript")&&!!document.querySelector(".jp-reading")'),'Earlier lessons keep visible reading');
 await evaluate('document.querySelector("[data-jp-sound]").click()');
 assert(await evaluate('window.__jpSpoken.at(-1).rate===.82&&window.__jpSpoken.at(-1).text===JP_LESSONS.find(l=>l.id==="30.1").reading'),'Earlier listen button uses shared helper');
 await evaluate('jpPage={mode:"lesson",week:31,lesson:"31.1"};renderJapanese()');
 assert(await evaluate('jpSpeechCurrent===null&&!DB.japanese.done["31.1"]'),'Render stops playback; listening never auto-completes');
 if(!await evaluate('jpFuriganaOn'))await evaluate('document.querySelector("[data-jp-furigana]").click()');
 const coverage=[];
 for(let day=1;day<=7;day++){
  await evaluate('jpPage={mode:"lesson",week:31,lesson:"31.'+day+'"};renderJapanese()');
  const result=await evaluate(`(()=>{
   const root=document.getElementById('japaneseBody'),bad=[];
   const walk=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;
   while(node=walk.nextNode()){
    if(node.parentElement.closest('ruby,h2,h3,h4,.jp-muted,.jp-kicker,.jp-gloss,.jp-study-item,button,summary,textarea,.jp-hard-btn,.jp-notes'))continue;
    if(/[\u3400-\u9fff々]/.test(node.data))bad.push(node.data);
   }
   const v=[...document.querySelectorAll('.jp-vocab')];
   return {day:${day},bad:[...new Set(bad)],kanji:v[1]?.querySelectorAll('.jp-kanji-readings').length,vocab:v[0]?.children.length,
    ruby:[...document.querySelector('.jp-reading').querySelectorAll('ruby')].map(r=>[r.firstChild.textContent,r.querySelector('rt').textContent])};
  })()`);
  coverage.push(result);
  assert(await evaluate('!document.querySelector(".jp-listening-transcript").open'),'Transcript initially hidden '+day);
  await evaluate('document.querySelector(".jp-listening-transcript > summary").click()');
  assert(await evaluate('document.querySelector(".jp-listening-transcript").open'),'Transcript reveal '+day);
  assert(await evaluate('document.querySelector("#jpNotes")&&document.querySelector("[data-jp-done]")&&document.querySelector("[data-jp-quiz]")&&document.querySelector("[data-jp-furigana]")'),'Daily controls '+day);
 }
 fs.writeFileSync(path.join(out,'coverage.json'),JSON.stringify(coverage,null,2));
 if(process.argv.includes('--audit')){console.log(JSON.stringify(coverage.map(x=>({day:x.day,bad:x.bad,kanji:x.kanji,vocab:x.vocab})),null,2));console.log('Reading ruby audit:',path.join(out,'coverage.json'));ws.close();return;}
 for(const r of coverage){assert.deepEqual(r.bad,[],'Uncovered visible Furigana Day '+r.day);assert.equal(r.kanji,r.day===7?12:5);assert.equal(r.vocab,r.day===7?12:20);}
 await evaluate('const hit=searchAll("料理の種類より","japanese").find(x=>x.lessonId==="31.6");if(!hit)throw Error("Week 31 search missing");gotoSearchHit(hit)');
 assert.equal(await evaluate('jpPage.lesson'),'31.6','Search opens matching new lesson');

 // Actual daily and weekly quiz submissions; correct answers must save to their own key.
 for(const day of [1,7]){
  await evaluate('jpPage={mode:"lesson",week:31,lesson:"31.'+day+'"};renderJapanese();const lesson=JP_LESSONS.find(l=>l.id===jpPage.lesson);lesson.quiz.forEach((q,i)=>document.querySelector("input[name=jpq"+i+"][value=\\""+q[2]+"\\"]").checked=true);document.querySelector("[data-jp-quiz]").click()');
  assert.equal(await evaluate('DB.japanese.quizScores["31.'+day+'"]'),100,'Quiz save '+day);
  assert(await evaluate('document.querySelector(".jp-result").textContent.includes("correct")'),'Quiz feedback '+day);
 }
 await evaluate('jpPage={mode:"lesson",week:31,lesson:"31.1"};renderJapanese();document.querySelector("#jpNotes").value="My deadline vs result reminder";document.querySelector("#jpNotes").dispatchEvent(new Event("input",{bubbles:true}));document.querySelector("[data-jp-check=read]").click();document.querySelector("[data-jp-done]").click()');
 assert(await evaluate('DB.japanese.done["31.1"]&&DB.japanese.checks["31.1"].read&&DB.japanese.notes["31.1"]==="My deadline vs result reminder"'),'Notes/checks/completion');
 await evaluate('document.querySelector("[data-jp-hard-type=v]").click()');assert(await evaluate('jpHardItems().some(x=>x.word==="指示")'),'Hard add');
 await evaluate('document.querySelector("[data-jp-hard-type=v]").click()');assert(await evaluate('!jpHardItems().some(x=>x.word==="指示")'),'Hard remove');
 await evaluate('document.querySelector("[data-jp-cards=vocab]").click();document.querySelector("[data-jp-cards=kanji]").click()');
 const cards=await evaluate('DB.cards.filter(c=>String(c.deckId).includes("31"))');
 assert.equal(cards.length,25,'Separate Week 31 vocab and kanji cards');
 assert(cards.some(c=>c.front==='指示')&&cards.some(c=>c.front==='指'),'Kanji-only/word-only fronts');
 assert(await evaluate('DB.decks.filter(d=>String(d.id).includes("31")).length===2'),'Two weekly decks');

 // Navigation remains in sequence at the old/new boundary; folder Back keeps the parent.
 await evaluate('document.querySelector(".jp-actions [data-jp-lesson=\\"30.7\\"]").click()');assert.equal(await evaluate('jpPage.lesson'),'30.7');
 await evaluate('document.querySelector(".jp-actions [data-jp-lesson=\\"31.1\\"]").click();document.querySelector(".jp-actions [data-jp-week=\\"31\\"]").click()');
 assert.equal(await evaluate('jpPage.mode'),'week');
 assert(await evaluate('jpWeekLessons(31).length===7&&document.getElementById("japaneseBody").textContent.includes("Week 31 finish line")'),'Week finish line');

 for(const [width,height] of [[1440,950],[768,1024],[375,812],[320,700]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const day of [0,1,4,7]){
    await evaluate('closeModal();jpPage={mode:'+JSON.stringify(day?'lesson':'week')+',week:31,lesson:"31.'+(day||1)+'"};renderJapanese();window.scrollTo(0,0)');
    const layout=await evaluate('(()=>{const r=document.querySelector("[data-jp-furigana]")?.getBoundingClientRect();return {width:innerWidth,scroll:document.documentElement.scrollWidth,float:r?{left:r.left,right:r.right}:null};})()');
    assert(layout.width<=width+1&&layout.scroll<=width+1,'Overflow/expanded viewport '+width+' '+theme+' '+day+': '+JSON.stringify(layout));
    if(layout.float)assert(layout.float.left>=0&&layout.float.right<=width+1,'Furigana clipped '+width+' '+theme+' '+day);
    if(day&&width<600){const sizes=await evaluate('[...document.querySelectorAll(".jp-listening .btn")].map(b=>({label:b.textContent,height:b.getBoundingClientRect().height,min:getComputedStyle(b).minHeight}))');assert(sizes.every(b=>b.height>=44),'Listening touch controls '+width+' day '+day+': '+JSON.stringify(sizes));}
   }
   if(width===1440||width===375)await shot('review-'+width+'-'+theme);
  }
 }
 // Use the same export/import controls as the learner, in a fresh synthetic profile.
 await evaluate('window.__jp30Blob=null;const originalURL=URL.createObjectURL;URL.createObjectURL=blob=>{window.__jp30Blob=blob;return originalURL(blob);};document.getElementById("exportBtn").click()');
 const backup=await evaluate('window.__jp30Blob.text()'),saved=JSON.parse(backup);
 await evaluate('DB.japanese=applyDefaults({}).japanese;save()');
 await evaluate('(()=>{const file=new File(['+JSON.stringify(backup)+'],"week31-backup.json",{type:"application/json"}),transfer=new DataTransfer();transfer.items.add(file);const input=document.getElementById("importFile");input.files=transfer.files;input.dispatchEvent(new Event("change",{bubbles:true}));})()');
 for(let i=0;i<50&&!await evaluate('!!document.getElementById("impMerge")');i++)await sleep(80);
 await evaluate('document.getElementById("impMerge").click()');
 assert.equal(await evaluate('DB.japanese.notes["31.1"]'),saved.japanese.notes['31.1'],'Actual merge import');
 await evaluate('DB.japanese=applyDefaults({}).japanese;confirmMerge('+backup+');document.getElementById("impReplace").click()');
 assert.equal(await evaluate('DB.japanese.quizScores["31.7"]'),100,'Actual replace import');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<100&&!await evaluate('Boolean(window.__studyHubBooted)');i++)await sleep(80);
 assert(await evaluate('DB.japanese.notes["31.1"]==="My deadline vs result reminder"&&DB.japanese.done["31.1"]&&DB.japanese.checks["31.1"].read&&DB.japanese.quizScores["31.7"]===100'),'Refresh saves new progress');
 assert(await evaluate('DB.japanese.notes["1.1.te"]==="Keep old Japanese note"&&DB.japanese.quizScores["1.1.te"]===75&&DB.course.notes["1.0"]==="Keep Python note"&&DB.headNotes.legacy==="Keep heading note"'),'Existing learning data preserved');
 assert.deepEqual(errors,[],'Browser console errors');
 console.log('PASS: all 7 lessons and complete visible Furigana; local-only speech adapter, rates, Stop/end/error, navigation cancellation, missing/remote voice fallback and hidden transcript; earlier reading/audio behavior; daily/review quizzes; notes, checks, completion and reload; Hard add/remove; separate weekly decks and card fronts; 30↔31 navigation; mobile/tablet/desktop light+dark; actual backup/import merge+replace; old progress preserved; no JavaScript errors. Physical audio not verified. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

