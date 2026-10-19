// Isolated visual/regression checks. Never opens the learner's browser profile.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const before=process.argv.includes('--before');
const out=path.join(os.tmpdir(),'studyhub-floating-back-'+(before?'before':'after'));fs.mkdirSync(out,{recursive:true});
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

 await evaluate('closeModal();DB=applyDefaults({course:{done:{"1.0":"2026-10-01"}},japanese:{notes:{"1.1.te":"Keep Japanese notes"}},headNotes:{legacy:"Keep heading notes"}});save();window.__savedNotes=JSON.stringify([DB.course.done,DB.japanese.notes,DB.headNotes])');
 const visible='!document.getElementById("floatingBack").hidden';
 async function settled(){await sleep(100);}
 async function scrollDown(selector){
  await evaluate('document.getElementById("__scrollSpace")?.remove();(()=>{const space=document.createElement("div");space.id="__scrollSpace";space.style.height="1600px";document.querySelector(".view.active").append(space);})()');
  await evaluate('(()=>{const r=document.querySelector('+JSON.stringify(selector)+').getBoundingClientRect();window.scrollTo(0,window.scrollY+r.bottom+200);})()');
  await settled();assert(await evaluate(visible),'Floating Back missing for '+selector);
 }
 async function nativeClick(selector){
  const point=await evaluate('(()=>{const r=document.querySelector('+JSON.stringify(selector)+').getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2};})()');
  await send('Input.dispatchMouseEvent',{type:'mousePressed',...point,button:'left',clickCount:1});
  await send('Input.dispatchMouseEvent',{type:'mouseReleased',...point,button:'left',clickCount:1});await settled();
 }
 const cases=[
  ['Python lesson','courseView={mode:"day",week:1,dayIdx:0,part:0};switchView("course")','#backWeek','courseView.mode==="week"&&courseView.week===1'],
  ['Python week','courseView={mode:"week",week:1,dayIdx:null};switchView("course")','#backOverview','courseView.mode==="overview"'],
  ['Python practice','switchView("course");document.getElementById("coursePracticeBtn").click()','#backFromPractice','courseView.mode==="overview"'],
  ['Japanese week','jpPage={mode:"week",week:1};switchView("japanese")','[data-jp-home]','jpPage.mode==="home"'],
  ['Japanese lesson','jpPage={mode:"lesson",week:1,lesson:"1.1"};switchView("japanese")','[data-jp-week]','jpPage.mode==="week"&&jpPage.week===1'],
  ['Japanese reference','jpPage={mode:"lesson",week:19,lesson:"19.1"};switchView("japanese")','[data-jp-lesson="19.5.core"]','jpPage.mode==="lesson"&&jpPage.lesson==="19.5.core"'],
  ['Japanese hard folder','jpPage={mode:"hard"};switchView("japanese")','[data-jp-home]','jpPage.mode==="home"'],
  ['Opposites','jpPage={mode:"meanings"};JP_MEANING_STATE.tab="opposites";switchView("japanese")','[data-jp-meanings="home"]','JP_MEANING_STATE.tab==="home"'],
  ['Synonyms','jpPage={mode:"meanings"};JP_MEANING_STATE.tab="synonyms";switchView("japanese")','[data-jp-meanings="home"]','JP_MEANING_STATE.tab==="home"'],
  ['Cybersecurity week','cyberPage={mode:"week",week:1,day:1};switchView("quiz")','[data-cyber-all]','cyberPage.mode==="overview"'],
  ['Cybersecurity lesson','cyberPage={mode:"day",week:1,day:1};switchView("quiz")','[data-cyber-week]','cyberPage.mode==="week"&&cyberPage.week===1'],
  ['Online Safety folder','cyberPage={mode:"safety-folder",lesson:1};switchView("quiz")','[data-safety-home]','cyberPage.mode==="overview"'],
  ['Online Safety lesson','cyberPage={mode:"safety-lesson",lesson:1};switchView("quiz")','[data-safety-folder]','cyberPage.mode==="safety-folder"'],
  ['Yoga session','yogaPage={mode:"session",id:YOGA_COURSE.sessions[0].id,duration:20};switchView("lessons")','#lessonsHomeBtn','yogaPage.mode==="home"'],
  ['Yoga poses','yogaPage.mode="poses";switchView("lessons")','#lessonsHomeBtn','yogaPage.mode==="home"'],
  ...['chess','sudoku','sokoban'].map(name=>[name+' game','switchView('+JSON.stringify(name)+')','#view-'+name+' .gm-crumb','document.getElementById("view-games").classList.contains("active")'])
 ];
 for(const [width,height] of (process.argv.includes('--tail')?[]:[[1440,800],[900,700],[375,812],[320,640]])){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<761});
  for(const theme of ['light','dark']){
   await evaluate('document.documentElement.dataset.theme='+JSON.stringify(theme));
   for(const [name,setup,selector,result] of cases){
    await evaluate('document.getElementById("__scrollSpace")?.remove();'+setup+';closeModal();window.scrollTo(0,0)');await settled();
    assert(!await evaluate(visible),'Floating arrow must be hidden at top: '+name);
    await scrollDown(selector);
    assert(await evaluate('(()=>{const b=document.getElementById("floatingBack"),r=b.getBoundingClientRect(),sidebar=document.getElementById("sidebar");return r.width===44&&r.height===44&&r.left>=0&&r.right<=innerWidth&&r.bottom<=innerHeight&&(!sidebar.getClientRects().length||r.left>=sidebar.getBoundingClientRect().right)&&!b.textContent.trim();})()'),'Compact button layout '+name+' '+width);
    if(name==='Opposites'&&width===375){
     await shot('floating-back-'+theme);
     await evaluate('openModal("<h2>Test modal</h2>")');await settled();assert(!await evaluate(visible),'Hidden while modal open');
     await evaluate('closeModal()');await settled();assert(await evaluate(visible),'Restored after modal close');
    }
    await evaluate('window.scrollTo(0,0)');await settled();assert(!await evaluate(visible),'Hide when returning to top: '+name);
    await scrollDown(selector);await nativeClick('#floatingBack');
    assert(await evaluate(result),'Wrong parent for '+name+' at '+width+' '+theme);
    assert(await evaluate('window.scrollY===0'),'Parent heading not visible: '+name);
   }
  }
 }
 await send('Emulation.setDeviceMetricsOverride',{width:320,height:640,deviceScaleFactor:1,mobile:true});
 // Existing split-view mobile Back stays in its sticky header, with no duplicate.
 await evaluate('switchView("notes");openDetailMobile();window.scrollTo(0,0)');await settled();
 assert(!await evaluate(visible),'Sticky mobile Back must not have a duplicate');
 // Refresh roots: no stale arrow from a previous lesson or made-up Back destination.
 for(const name of ['course','japanese','quiz','games','todo','typing','timer','liked','journal','wisdom','lessons','flashcards','reviews']){
  await evaluate('courseView.mode="overview";jpPage.mode="home";cyberPage.mode="overview";yogaPage.mode="home";switchView('+JSON.stringify(name)+');window.scrollTo(0,0)');await settled();
  await evaluate('(()=>{const space=document.createElement("div");space.id="__scrollSpace";space.style.height="1600px";document.querySelector(".view.active").append(space);window.scrollTo(0,800);})()');await settled();
  assert(!await evaluate(visible),'Stale/invalid Back on '+name);
  await evaluate('document.getElementById("__scrollSpace").remove()');
 }
 // Scroll an internal panel: its clipping boundary also hides the original Back.
 await evaluate('courseView={mode:"day",week:1,dayIdx:0,part:0};switchView("course");window.scrollTo(0,0);(()=>{const panel=document.createElement("div");panel.id="testScrollPanel";panel.style.cssText="height:250px;overflow-y:auto";const body=document.getElementById("courseBody");body.before(panel);panel.append(body);panel.scrollTop=400;})()');await settled();
 assert(await evaluate(visible),'Nested scroll panel should have floating Back');await nativeClick('#floatingBack');
 assert(await evaluate('courseView.mode==="week"&&document.getElementById("testScrollPanel").scrollTop===0'),'Nested panel Back/reset');
 await evaluate('(()=>{const panel=document.getElementById("testScrollPanel");panel.before(document.getElementById("courseBody"));panel.remove();})()');
 // Keyboard activation: a real native button, not a click-only decoration.
 await evaluate('jpPage={mode:"week",week:1};switchView("japanese");window.scrollTo(0,0)');await scrollDown('[data-jp-home]');
 await evaluate('document.getElementById("floatingBack").focus()');
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r'});
 await send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});await settled();
 assert(await evaluate('jpPage.mode==="home"&&document.activeElement.id==="content"'),'Keyboard Back and focus: '+JSON.stringify(await evaluate('({mode:jpPage.mode,focus:document.activeElement.id,hidden:document.getElementById("floatingBack").hidden})')));
 // Review and flashcard sessions use their own existing exit controls.
 await evaluate('migrateCompletedToReviews();switchView("reviews");reviewStart([DB.reviews.items["python:day:1.0"]]);window.scrollTo(0,0)');await scrollDown('[data-review-exit]');await nativeClick('#floatingBack');
 assert(await evaluate('reviewView.mode==="dashboard"'),'Review Back');
 await evaluate('DB.decks.push({id:"test-deck",name:"Test deck"});DB.cards.push({id:"test-card",deckId:"test-deck",front:"Question",back:"Answer",due:"2000-01-01",reps:0,interval:0,ease:2.5});switchView("flashcards");startStudy("test-deck");window.scrollTo(0,0)');await scrollDown('#exitStudyBtn');await nativeClick('#floatingBack');
 assert(await evaluate('!document.getElementById("exitStudyBtn")&&document.querySelector("#deckGrid")'),'Flashcard Back');
 // Existing game focus already provides its Back alongside the board.
 await evaluate('switchView("sudoku");window.scrollTo(0,0);gamesFocus();gamesFocusFallback()');await settled();
 assert(!await evaluate(visible),'Duplicate arrow in game focus');
 await evaluate('gamesExitFocus(false);switchView("course")');
 assert(await evaluate('JSON.stringify([DB.course.done,DB.japanese.notes,DB.headNotes])===window.__savedNotes'),'Learning progress/notes changed');
 assert.deepEqual(errors,[],'Console errors');
 console.log('PASS: '+(process.argv.includes('--tail')?'remaining mobile, root, nested-scroll and session checks':'18 parent routes, four widths, light/dark; top/floating transitions and pointer Back')+'; keyboard, review/flashcards, modal/focus handling, no stale arrows on 13 roots; existing progress/notes and console clean. Screenshots:',out);
 ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{clearTimeout(watchdog);if(ws)ws.close();browser.kill();});

