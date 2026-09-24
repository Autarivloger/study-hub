const fs = require("fs");
const os = require("os");
const path = require("path");
const {spawn} = require("child_process");
const {pathToFileURL} = require("url");

const chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile = fs.mkdtempSync(path.join(os.tmpdir(), "studyhub-jp-"));
const browser = spawn(chromePath, [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--no-first-run",
  "--remote-debugging-port=0", "--user-data-dir=" + profile,
  pathToFileURL(path.resolve(__dirname, "..", "study-hub.html")).href
], {stdio:"ignore"});
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
async function main(){
  let port;
  for(let i=0;i<100;i++){
    const active = path.join(profile, "DevToolsActivePort");
    if(fs.existsSync(active)){ port=Number(fs.readFileSync(active,"utf8").split("\n")[0]); break; }
    await sleep(100);
  }
  if(!port) throw new Error("Chrome debugging port did not start");
  const tabs = await (await fetch("http://127.0.0.1:"+port+"/json/list")).json();
  const page = tabs.find(x=>x.type==="page");
  if(!page) throw new Error("No browser page");
  const ws = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{ws.onopen=resolve;ws.onerror=reject;});
  let nextId=0;
  const pending=new Map(), errors=[];
  ws.onmessage = ev=>{
    const msg=JSON.parse(ev.data);
    if(msg.method==="Runtime.exceptionThrown"){
      const e=msg.params.exceptionDetails;
      errors.push((e.exception && e.exception.description) || (e.text+" at "+e.url+":"+e.lineNumber));
    }
    if(msg.id && pending.has(msg.id)){
      const p=pending.get(msg.id);pending.delete(msg.id);
      if(msg.error) p.reject(new Error(JSON.stringify(msg.error))); else p.resolve(msg.result);
    }
  };
  function send(method,params={}){
    return new Promise((resolve,reject)=>{
      const id=++nextId;pending.set(id,{resolve,reject});
      ws.send(JSON.stringify({id,method,params}));
    });
  }
  async function evalJs(expression){
    const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});
    if(r.exceptionDetails) throw new Error((r.exceptionDetails.exception && r.exceptionDetails.exception.description) || r.exceptionDetails.text);
    return r.result.value;
  }
  function assert(value,message){if(!value)throw new Error(message);}
  await send("Runtime.enable");
  await send("Page.enable");
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));
  assert(await evalJs("document.querySelectorAll('#tabnav [data-view]').length === 11"),"Navigation lost a tab");
  await evalJs("localStorage.studyHubData_v1=JSON.stringify({japanese:{done:{'1.1':'2025-01-01T00:00:00.000Z','1.2':'2025-01-02T00:00:00.000Z','1.3':'2025-01-03T00:00:00.000Z','1.4':'2025-01-04T00:00:00.000Z','1.5':'2025-01-05T00:00:00.000Z','1.6':'2025-01-06T00:00:00.000Z','2.1':'2025-02-01','2.2':'2025-02-02','2.3':'2025-02-03','2.4':'2025-02-04','2.5':'2025-02-05','2.6':'2025-02-06'},quizScores:{'1.1':100,'1.2':50,'1.3':50,'1.4':50,'1.5':50,'1.6':50,'2.1':50,'2.2':50,'2.3':50,'2.4':50,'2.5':50,'2.6':50},notes:{'1.1':'Old kana note','1.2':'Old topic note','1.3':'Old particles note','1.4':'Old polite note','1.5':'Old te-form note','1.6':'Old reading note','2.1':'Old W2D1 note','2.2':'Old W2D2 note','2.3':'Old W2D3 note','2.4':'Old W2D4 note','2.5':'Old W2D5 note','2.6':'Old W2D6 note'},checks:{}},decks:[{id:'jp-vocabulary-v1',name:'Japanese',created:'2025-01-01'}],cards:[{id:'jp-1.1-0',deckId:'jp-vocabulary-v1',front:'切手（きって）',back:'stamp',ease:2.5,interval:0,reps:0,due:'2025-01-01'}]})");
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click()");
  assert(await evalJs("document.querySelector('#view-japanese').classList.contains('active')"),"Japanese view did not open");
  assert(await evalJs("document.querySelectorAll('.jp-week-card').length === 36"),"Roadmap is incomplete");
  assert(await evalJs("document.querySelector('.jp-hero [data-jp-lesson=\"1.1\"]') !== null && document.querySelector('.jp-progress').getAttribute('aria-valuenow') === '0'"),"Old kana completion falsely completed new Day 1");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-desktop.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('[data-jp-week=\"1\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length === 7 && !!document.querySelector('[data-jp-lesson=\"1.7\"]')"),"Week 1 lessons or Day 7 review missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  assert(await evalJs("document.querySelector('h2').textContent.includes('て-form') || document.querySelector('.jp-hero h2').textContent.includes('て-form')"),"Day 1 did not become te-form");
  assert(await evalJs("document.querySelectorAll('.jp-q').length === 8 && document.querySelectorAll('.jp-vocab')[0].children.length === 10 && document.querySelectorAll('.jp-vocab')[1].children.length === 11"),"Day 1 vocabulary, kanji or quiz missing");
  assert(await evalJs("document.querySelectorAll('.jp-rule-card').length === 3 && document.querySelectorAll('.jp-old-review .jp-example').length >= 3 && document.querySelectorAll('.jp-reading').length === 2"),"Te-form rules or old kana content missing");
  assert(await evalJs("[...document.querySelectorAll('[data-jp-jump]')].length === 8 && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump)) && !!document.querySelector('#jp-day1-summary')"),"Day 1 section navigation or summary missing");
  assert(await evalJs("document.querySelector('.jp-old-review').textContent.includes('Old kana note') && document.querySelector('.jp-old-review').textContent.includes('Best quiz: 100%')"),"Old Kana note or score is not visible");
  await evalJs("document.querySelector('.jp-vocab [data-jp-hard-type=v]').click()");
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).japanese.checks).filter(x=>x && x.hard).length === 1"),"Hard vocabulary did not save");
  await evalJs("document.querySelector('[data-jp-hard-folder]').click()");
  assert(await evalJs("document.querySelector('.jp-hero h2').textContent === 'Hard to remember' && document.querySelectorAll('.jp-study-item').length === 1"),"Hard folder did not show item");
  await evalJs("document.querySelector('.jp-study-item [data-jp-hard-type]').click()");
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).japanese.checks).filter(x=>x && x.hard).length === 0 && document.querySelectorAll('.jp-study-item').length === 0"),"Remembered word did not leave folder");
  await evalJs("document.querySelector('[data-jp-lesson=\"1.1\"]').click();document.querySelector('.jp-vocab [data-jp-hard-type=k]').click()");
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).japanese.checks).filter(x=>x && x.hard && x.type==='k').length === 1"),"Hard kanji did not save");
  await evalJs("document.querySelector('[data-jp-cards]').click();document.querySelector('[data-jp-cards]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.id.startsWith('jp-1.1-te-')).length === 10 && JSON.parse(localStorage.studyHubData_v1).cards.some(x=>x.id==='jp-1.1-0' && x.front.includes('切手'))"),"New cards missing or old cards overwritten");
  await evalJs("document.querySelector('#jpNotes').value='My Japanese practice';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}))");
  await evalJs("document.querySelector('[data-jp-check=read]').click()");
  await evalJs("[1,0,2,1,1,0,1,0].forEach((a,i)=>document.querySelector('input[name=jpq'+i+'][value=\"'+a+'\"]').click())");
  await evalJs("document.querySelector('[data-jp-quiz]').click()");
  assert(await evalJs("document.querySelector('.jp-result').textContent.includes('8 / 8 correct')"),"Day 1 quiz score wrong");
  await evalJs("document.querySelector('[data-jp-done]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1.te'] !== undefined && JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1'] === '2025-01-01T00:00:00.000Z'"),"New completion lost or overwrote old completion");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['1.1.te'] === 100 && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['1.1'] === 100"),"New or old quiz score lost");
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.1.te'] === 'My Japanese practice' && JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.1'] === 'Old kana note'"),"New or old note did not survive reload");
  assert(await evalJs("Object.values(JSON.parse(localStorage.studyHubData_v1).japanese.checks).filter(x=>x && x.hard && x.type==='k').length === 1"),"Hard kanji did not survive reload");
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-week=\"1\"]').click();document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  assert(await evalJs("document.querySelector('#jpNotes').value === 'My Japanese practice'"),"Note did not render after reload");
  const answers=[[1,0,2,1,1,0,1,0],[1,2,0,0,1,1,2,1],[1,0,2,0,1,1,1,0],
    [0,1,1,0,0,0,1,1],[1,0,2,0,1,2,0,0],[0,1,1,0,1,2,0,0,1,1],[1,0,1,0,1,1,0,2,1,0,0,2],
    [1,0,1,1,1,0,0,1],[1,0,0,1,1,1,0,0],[1,1,0,0,0,0,0,1],[1,0,1,1,1,0,1,0],
    [1,0,0,1,2,0,0,1],[0,1,0,0,1,0,0,0,0,0],[0,1,1,0,1,0,1,1,2,0,0,0],
    [0,1,1,1,0,1],[1,1,0,0,0,1],[0,1,1,1,0,1],[1,0,0,0,0,1],[1,0,1,0,1,0],[1,0,0,1,0,1],[0,1,1,1,1,0,1,0,1,1],
    [1,1,0,0,0,1],[0,1,1,0,1,1],[1,0,1,0,0,1],[1,0,1,1,0,1],[1,0,0,1,0,1],[0,1,1,2,0,1],[0,0,1,1,0,1,0,1,1,1],
    [0,0,1,0,1,1],[1,1,0,0,1,1],[0,1,0,0,1,2],[0,1,0,0,0,1],[0,0,0,0,1,1],[0,0,0,0,0,1],[0,0,1,0,0,0,0,0,0,1],
    [0,1,1,0,1,1],[1,1,1,0,0,1],[1,0,1,1,0,1],[0,1,1,0,1,1],[0,1,1,0,0,1],[0,1,0,0,0,2],[0,1,1,1,1,0,0,1,1,1]];
  for(let i=0;i<42;i++){
    if(i===1){
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent.includes('ておく') && document.querySelectorAll('.jp-vocab')[0].children.length === 10 && document.querySelectorAll('.jp-vocab')[1].children.length === 5 && document.querySelectorAll('.jp-q').length === 8"),"New Day 2 content missing");
      assert(await evalJs("document.querySelector('.jp-old-review').textContent.includes('Old topic note') && document.querySelector('.jp-old-review').textContent.includes('Best quiz: 50%') && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Old Day 2 data or section navigation missing");
      await evalJs("document.querySelector('.jp-vocab [data-jp-hard-type=k]').click();document.querySelector('[data-jp-cards]').click()");
      assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.id.startsWith('jp-1.2-n4-te-')).length === 10"),"Day 2 cards missing");
    }
    if(i===2){
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent.includes('たり') && document.querySelectorAll('.jp-vocab')[0].children.length === 10 && document.querySelectorAll('.jp-vocab')[1].children.length === 5 && document.querySelectorAll('.jp-q').length === 8"),"New Day 3 content missing");
      assert(await evalJs("document.querySelectorAll('.jp-rule-card').length === 2 && document.querySelector('.jp-old-review').textContent.includes('Old particles note') && document.querySelector('.jp-old-review').textContent.includes('Best quiz: 50%') && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Day 3 forms, old lesson or navigation missing");
      await evalJs("document.querySelector('.jp-vocab [data-jp-hard-type=k]').click();document.querySelector('[data-jp-cards]').click()");
      assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.id.startsWith('jp-1.3-n4-actions-')).length === 10"),"Day 3 cards missing");
    }
    if(i>=3 && i<=6){
      const title=['permission','must do','read, explain','review and check'][i-3];
      const count=[8,8,10,12][i-3];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent.includes('"+title+"') && document.querySelectorAll('.jp-vocab')[0].children.length === 10 && document.querySelectorAll('.jp-vocab')[1].children.length === 5 && document.querySelectorAll('.jp-q').length === "+count+" && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Day "+(i+1)+" teaching or navigation missing");
      if(i<6) assert(await evalJs("document.querySelector('.jp-old-review').textContent.includes('"+['Old polite note','Old te-form note','Old reading note'][i-3]+"')"),"Original Day "+(i+1)+" content lost");
      else assert(await evalJs("!document.querySelector('[data-jp-cards]') && !document.querySelector('.jp-old-review')"),"Day 7 review duplicated cards or earlier lesson");
    }
    if(i>=7 && i<=13){
      const day=i-6, expectedQuiz=[8,8,8,8,8,10,12][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Week 2 Day "+day+" title, content, 20 words or navigation missing");
      if(day<7) assert(await evalJs("document.querySelector('.jp-old-review').textContent.includes('Old W2D"+day+" note') && document.querySelector('.jp-old-review').textContent.includes('Best quiz: 50%')"),"Original Week 2 Day "+day+" data lost");
      else assert(await evalJs("!document.querySelector('[data-jp-cards]') && !document.querySelector('.jp-old-review')"),"Week 2 review duplicated cards or old content");
    }
    if(i>=14 && i<=20){
      const day=i-13, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Week 3 Day "+day+" title, content, 20 words or navigation missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 3 review should not duplicate flashcards");
    }
    if(i>=21 && i<=27){
      const day=i-20, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump)) && document.querySelectorAll('.jp-panel').length>=12"),"Week 4 Day "+day+" title, teaching blocks, words, kanji or quiz missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 4 review should not duplicate flashcards");
    }
    if(i>=28 && i<=34){
      const day=i-27, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:')"),"Week 5 Day "+day+" content, On/Kun readings, words, kanji or quiz missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 5 review should not duplicate flashcards");
    }
    if(i>=35 && i<=41){
      const day=i-34, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:') && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Week 6 Day "+day+" content, navigation, On/Kun readings, words, kanji or quiz missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 6 review should not duplicate flashcards");
    }
    await evalJs("["+answers[i].join(",")+"].forEach((a,j)=>document.querySelector('input[name=jpq'+j+'][value=\"'+a+'\"]').click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+answers[i].length+" / "+answers[i].length+" correct')"),"Quiz failed for lesson "+(i+1));
    if(i===1){
      await evalJs("document.querySelector('#jpNotes').value='N4 Day 2 note';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.2.n4-te'] && !!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.2'] && JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.2']==='Old topic note'"),"New Day 2 completion overwrote old progress");
    }
    if(i===2){
      await evalJs("document.querySelector('#jpNotes').value='N4 Day 3 note';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.3.n4-actions'] && !!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.3'] && JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.3']==='Old particles note'"),"New Day 3 completion overwrote old progress");
    }
    if(i>=3 && i<=6){
      await evalJs("document.querySelector('#jpNotes').value='Week 1 new note '+"+(i+1)+";document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['"+['1.4.rules','1.5.obligation','1.6.integration','1.7'][i-3]+"']"),"Day "+(i+1)+" completion did not save");
    }
    if(i>=7 && i<=13){
      const day=i-6, key=day===7?'2.7':'2.'+day+'.n4';
      await evalJs("document.querySelector('#jpNotes').value='Week 2 new note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['"+key+"']"),"Week 2 Day "+day+" completion did not save");
    }
    if(i>=14 && i<=20){
      const day=i-13;
      await evalJs("document.querySelector('#jpNotes').value='Week 3 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['3."+day+"']"),"Week 3 Day "+day+" completion did not save");
    }
    if(i>=21 && i<=27){
      const day=i-20;
      await evalJs("document.querySelector('#jpNotes').value='Week 4 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['4."+day+"']"),"Week 4 Day "+day+" completion did not save");
    }
    if(i>=28 && i<=34){
      const day=i-27;
      await evalJs("document.querySelector('#jpNotes').value='Week 5 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['5."+day+"']"),"Week 5 Day "+day+" completion did not save");
    }
    if(i>=35 && i<=41){
      const day=i-34;
      await evalJs("document.querySelector('#jpNotes').value='Week 6 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['6."+day+"']"),"Week 6 Day "+day+" completion did not save");
    }
    if(i<41) await evalJs("document.querySelector('.jp-actions [data-jp-lesson]:last-child').click()");
  }
  assert(await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19.1\"]') === null"),"Core path unexpectedly jumps to advanced preview");
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-hero [data-jp-lesson=\"1.1\"]') !== null && document.querySelector('.jp-progress').getAttribute('aria-valuenow') === '42' && !document.body.textContent.includes('Your weekly rhythm')"),"Week 6 completion count or removed rhythm panel changed");
  await evalJs("document.querySelector('[data-jp-lesson=\"19.1\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-panel h3').length >= 10"),"Imported grammar sections missing");
  assert(await evalJs("document.body.textContent.includes('Natural conversation') && document.body.textContent.includes('Write and compare')"),"Imported conversation or writing practice missing");
  assert(await evalJs("document.querySelectorAll('.jp-vocab')[0].children.length === 10 && document.querySelectorAll('.jp-vocab')[1].children.length === 10"),"Day 16 vocabulary or kanji missing");
  assert(await evalJs("document.querySelectorAll('.jp-q').length === 4"),"Day 16 quiz missing");
  await evalJs("document.querySelector('#jpNotes').value='Contrast needs review';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}))");
  await evalJs("document.querySelector('[data-jp-cards]').click();document.querySelector('[data-jp-cards]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.id.startsWith('jp-19.1-')).length === 10"),"Imported flashcards missing or duplicated");
  await evalJs("[0,0,0,1].forEach((a,i)=>document.querySelector('input[name=jpq'+i+'][value=\"'+a+'\"]').click());document.querySelector('[data-jp-quiz]').click()");
  assert(await evalJs("document.querySelector('.jp-result').textContent.includes('4 / 4 correct')"),"Day 16 quiz failed");
  await evalJs("document.querySelector('[data-jp-done]').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.done['19.1'] !== undefined"),"Day 16 completion not saved");
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19.2\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-panel h3').length >= 9 && document.querySelectorAll('.jp-q').length === 4"),"Day 17 content missing");
  await evalJs("[0,1,1,0].forEach((a,i)=>document.querySelector('input[name=jpq'+i+'][value=\"'+a+'\"]').click());document.querySelector('[data-jp-quiz]').click()");
  assert(await evalJs("document.querySelector('.jp-result').textContent.includes('4 / 4 correct')"),"Day 17 quiz failed");
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.notes['19.1'] === 'Contrast needs review'"),"Imported note did not survive reload");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.2.n4-te'] === 'N4 Day 2 note' && !!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.2.n4-te'] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['1.2.n4-te'] === 100"),"Day 2 progress did not survive reload");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.notes['1.3.n4-actions'] === 'N4 Day 3 note' && !!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.3.n4-actions'] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['1.3.n4-actions'] === 100"),"Day 3 progress did not survive reload");
  assert(await evalJs("['1.4.rules','1.5.obligation','1.6.integration','1.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 1 new note '+(i+4)) && ['1.4','1.5','1.6'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Week 1 new or old progress did not survive reload");
  assert(await evalJs("['2.1.n4','2.2.n4','2.3.n4','2.4.n4','2.5.n4','2.6.n4','2.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 2 new note '+(i+1)) && ['2.1','2.2','2.3','2.4','2.5','2.6'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Week 2 new or original progress did not survive reload");
  assert(await evalJs("['3.1','3.2','3.3','3.4','3.5','3.6','3.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 3 note '+(i+1))"),"Week 3 progress did not survive reload");
  assert(await evalJs("['4.1','4.2','4.3','4.4','4.5','4.6','4.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 4 note '+(i+1))"),"Week 4 progress did not survive reload");
  assert(await evalJs("['5.1','5.2','5.3','5.4','5.5','5.6','5.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 5 note '+(i+1))"),"Week 5 progress did not survive reload");
  assert(await evalJs("['6.1','6.2','6.3','6.4','6.5','6.6','6.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 6 note '+(i+1))"),"Week 6 progress did not survive reload");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.quizScores['19.2'] === 100"),"Day 17 score did not survive reload");
  await evalJs("document.querySelector('#sidebar [data-view=course]').click()");
  assert(await evalJs("document.querySelector('#view-course').classList.contains('active')"),"Python course navigation failed");
  await evalJs("document.querySelector('#sidebar [data-view=typing]').click()");
  assert(await evalJs("document.querySelector('#view-typing').classList.contains('active')"),"Typing navigation failed");
  await evalJs("document.querySelector('#themeBtn').click()");
  assert(await evalJs("document.documentElement.hasAttribute('data-theme')"),"Theme did not toggle");
  await send("Emulation.setDeviceMetricsOverride",{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await evalJs("document.querySelector('#tabnav [data-view=japanese]').click()");
  assert(await evalJs("document.querySelector('#view-japanese').classList.contains('active')"),"Mobile Japanese navigation failed");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile layout overflows horizontally");
  await evalJs("document.querySelector('[data-jp-week=\"1\"]').click();document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile lesson overflows horizontally");
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"1.2\"]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelector('.jp-old-review').textContent.includes('Old topic note')"),"Mobile Day 2 overflows or old review missing");
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"1.3\"]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelector('.jp-old-review').textContent.includes('Old particles note')"),"Mobile Day 3 overflows or old review missing");
  for(const n of [4,5,6,7]){
    await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"1."+n+"\"]').click()");
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile Week 1 Day "+n+" overflows horizontally");
  }
  await evalJs("document.querySelector('[data-jp-week=\"1\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && !!document.querySelector('[data-jp-lesson=\"1.7\"]')"),"Mobile Week 1 review link missing");
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"2\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && !!document.querySelector('[data-jp-lesson=\"2.7\"]')"),"Mobile Week 2 short titles, lessons or review missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"2.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20"),"Mobile Week 2 Day "+n+" overflow or word count failure");
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"2."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"5\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1))"),"Mobile Week 5 short titles or lessons missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"5.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5"),"Mobile Week 5 Day "+n+" overflow or study count failure");
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"5."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"6\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 6 finish line')"),"Mobile Week 6 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"6.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:')"),"Mobile Week 6 Day "+n+" overflow, reading or study count failure");
    if(process.env.JP_SHOTS && n===1){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week6-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"6."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"3\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && !!document.querySelector('[data-jp-lesson=\"3.7\"]')"),"Mobile Week 3 short titles, lessons or review missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"3.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20"),"Mobile Week 3 Day "+n+" overflow or word count failure");
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"3."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"4\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && !!document.querySelector('[data-jp-lesson=\"4.7\"]')"),"Mobile Week 4 short titles, lessons or review missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"4.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5"),"Mobile Week 4 Day "+n+" overflow, word or kanji count failure");
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"4."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"1\"]').click()");
  await evalJs("document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  await evalJs("document.querySelector('[data-jp-hard-folder]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile hard folder overflows horizontally");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-hard-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-lesson=\"19.1\"]').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Mobile advanced lesson overflows horizontally");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-advanced-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"1\"]').click();document.querySelector('[data-jp-lesson=\"1.1\"]').click()");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("(()=>{const data={notes:[{id:'old-note',title:'Old note',body:'preserved'}],course:{done:{'1.0':'2024-01-01'}},japanese:{checks:{'hard:v:起きる':{type:'v',word:'起きる',reading:'おきる',meaning:'wake up',hard:true,at:'2020-01-01T00:00:00.000Z'},'hard:k:起':{type:'k',word:'起',reading:'おきる',meaning:'wake up',hard:false,at:'2099-01-01T00:00:00.000Z'}}}};const f=new File([JSON.stringify(data)],'old-backup.json',{type:'application/json'});const dt=new DataTransfer();dt.items.add(f);const input=document.querySelector('#importFile');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));})()");
  for(let i=0;i<30;i++){
    if(await evalJs("!!document.querySelector('#impMerge')")) break;
    await sleep(100);
  }
  assert(await evalJs("!!document.querySelector('#impMerge')"),"Import dialog did not open");
  await evalJs("document.querySelector('#impMerge').click()");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).notes.some(x=>x.id==='old-note')"),"Old backup did not merge");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1']"),"Import erased Japanese progress");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1.te']"),"Import erased new Day 1 progress");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.2.n4-te'] && !!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.2']"),"Import erased Day 2 progress");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.3.n4-actions'] && !!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.3']"),"Import erased Day 3 progress");
  assert(await evalJs("['1.4.rules','1.5.obligation','1.6.integration','1.7','1.4','1.5','1.6'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 1 progress");
  assert(await evalJs("['2.1.n4','2.2.n4','2.3.n4','2.4.n4','2.5.n4','2.6.n4','2.7','2.1','2.2','2.3','2.4','2.5','2.6'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 2 progress");
  assert(await evalJs("['3.1','3.2','3.3','3.4','3.5','3.6','3.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 3 progress");
  assert(await evalJs("['4.1','4.2','4.3','4.4','4.5','4.6','4.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 4 progress");
  assert(await evalJs("['5.1','5.2','5.3','5.4','5.5','5.6','5.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 5 progress");
  assert(await evalJs("['6.1','6.2','6.3','6.4','6.5','6.6','6.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 6 progress");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.checks['hard:v:起きる'].hard === false && JSON.parse(localStorage.studyHubData_v1).japanese.checks['hard:k:起'].hard === false"),"Hard removal failed to merge or stale mark returned");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['19.1']"),"Import erased imported lesson progress");
  await evalJs("document.querySelector('#exportBtn').click()");
  for(let i=0;i<20;i++){
    if(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).lastBackup")) break;
    await sleep(100);
  }
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).lastBackup"),"Export did not finish");
  assert(await evalJs("!!document.querySelector('#exportBtn') && !!document.querySelector('#importBtn')"),"Backup controls missing");
  await evalJs("document.querySelector('#syncBtn').click()");
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1"),"Sync dialog overflows on mobile");
  assert(await evalJs("!document.querySelector('#syRemember').checked"),"New tokens should default to session-only storage");
  assert(await evalJs("document.querySelector('#syTok').getAttribute('value') === null"),"Token should not appear in HTML markup");
  await evalJs("document.querySelector('#syTok').value='synthetic-test-token-123456';document.querySelector('#syClose').click()");
  assert(await evalJs("!JSON.parse(localStorage.studyHubSync).token"),"Session-only token leaked into persistent storage");
  assert(await evalJs("sessionStorage.studyHubSyncSessionToken === 'synthetic-test-token-123456'"),"Session token was not available for sync");
  await evalJs("window.__syncBody='';window.fetch=async(url,opts)=>{const method=opts.method;if(method==='POST'){window.__syncBody=opts.body;return new Response(JSON.stringify({id:'0123456789abcdef0123456789abcdef'}),{status:201,headers:{'Content-Type':'application/json'}});}if(method==='GET'){const remote={notes:[{id:'remote-note',title:'From another phone',body:'Hello'}],japanese:{checks:{'hard:v:寝る':{type:'v',word:'寝る',reading:'ねる',meaning:'sleep',hard:true,at:'2020-01-01T00:00:00.000Z'}}}};return new Response(JSON.stringify({files:{'study-hub-progress.json':{content:JSON.stringify({data:remote})}}}),{status:200,headers:{'Content-Type':'application/json'}});}return new Response(JSON.stringify({id:'0123456789abcdef0123456789abcdef'}),{status:200,headers:{'Content-Type':'application/json'}});}");
  await evalJs("document.querySelector('#syncBtn').click();document.querySelector('#syPush').click()");
  for(let i=0;i<30;i++){
    if(await evalJs("JSON.parse(localStorage.studyHubSync).gistId === '0123456789abcdef0123456789abcdef'")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubSync).gistId === '0123456789abcdef0123456789abcdef'"),"First Push did not create a Gist");
  assert(await evalJs("window.__syncBody.includes('old-note') && !window.__syncBody.includes('synthetic-test-token-123456')"),"Push payload lost notes or contained token");
  await evalJs("document.querySelector('#syPull').click()");
  for(let i=0;i<30;i++){
    if(await evalJs("JSON.parse(localStorage.studyHubData_v1).notes.some(x=>x.id==='remote-note')")) break;
    await sleep(100);
  }
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).notes.some(x=>x.id==='remote-note')"),"Pull did not merge remote writing");
  assert(await evalJs("JSON.parse(localStorage.studyHubData_v1).japanese.checks['hard:v:寝る'].hard === true"),"Pull did not merge remote Hard word");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1']"),"Pull erased local progress");
  await evalJs("window.fetch=async()=>new Response('{}',{status:403,headers:{'Content-Type':'application/json'}});document.querySelector('#syncBtn').click();document.querySelector('#syPush').click()");
  for(let i=0;i<30;i++){
    if(await evalJs("document.querySelector('#syStatus').textContent.includes('Gists')")) break;
    await sleep(100);
  }
  assert(await evalJs("document.querySelector('#syStatus').textContent.includes('Gists')"),"403 did not show an actionable error");
  await evalJs("document.querySelector('#syClose').click();localStorage.studyHubSync=JSON.stringify({token:'synthetic-legacy-token-123456',gistId:'0123456789abcdef0123456789abcdef',auto:false});sessionStorage.removeItem('studyHubSyncSessionToken')");
  await evalJs("document.querySelector('#syncBtn').click()");
  assert(await evalJs("document.querySelector('#syRemember').checked"),"Existing saved token stopped working");
  await evalJs("document.querySelector('#syRemember').click();document.querySelector('#syClose').click()");
  assert(await evalJs("!JSON.parse(localStorage.studyHubSync).token && sessionStorage.studyHubSyncSessionToken === 'synthetic-legacy-token-123456'"),"Unchecking Remember did not remove persistent token");
  await evalJs("document.querySelector('#syncBtn').click();document.querySelector('#syForget').click()");
  assert(await evalJs("!JSON.parse(localStorage.studyHubSync).token && !sessionStorage.studyHubSyncSessionToken"),"Forget did not clear token");
  assert(await evalJs("JSON.parse(localStorage.studyHubSync).gistId === '0123456789abcdef0123456789abcdef'"),"Forget erased Gist ID");
  assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['1.1']"),"Forget erased writing");
  assert(errors.length===0,"JavaScript errors: "+errors.join("; "));
  console.log("PASS: Japanese Weeks 1–6, On/Kun readings, short titles, 20-word Week 2–6 days, progress, mobile, dark mode, backup, mock Gist sync, no JS exceptions");
  ws.close();
}
main().catch(err=>{console.error(err);process.exitCode=1;}).finally(()=>{browser.kill();});
