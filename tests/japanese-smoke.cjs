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
  async function furiganaCoverage(){
    return evalJs(`(()=>{const roots=[...document.querySelectorAll('.jp-jp,.jp-reading,.jp-pattern,p[lang=ja],.jp-q legend,.jp-choice,.jp-rule-card [lang=ja],.jp-panel>p:not(.jp-muted)')];const bad=[];for(const root of roots){const walk=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node;while(node=walk.nextNode()){if(node.parentElement.closest('ruby'))continue;if(/[\\u3400-\\u9fff々]/.test(node.data))bad.push(node.data)}}const voc=[...document.querySelectorAll('.jp-vocab')][0],kan=[...document.querySelectorAll('.jp-vocab')][1];return {bad:bad.slice(0,5),vocab:!!voc&&[...voc.children].every(x=>!!x.querySelector('ruby rt')),kanji:!!kan&&[...kan.children].every(x=>!!x.querySelector('.jp-kanji-readings'))};})()`);
  }
  await send("Runtime.enable");
  await send("Page.enable");
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));
  assert(await evalJs("document.querySelectorAll('#tabnav [data-view]').length === 12"),"Navigation lost a tab");
  await evalJs("localStorage.studyHubData_v1=JSON.stringify({japanese:{done:{'1.1':'2025-01-01T00:00:00.000Z','1.2':'2025-01-02T00:00:00.000Z','1.3':'2025-01-03T00:00:00.000Z','1.4':'2025-01-04T00:00:00.000Z','1.5':'2025-01-05T00:00:00.000Z','1.6':'2025-01-06T00:00:00.000Z','2.1':'2025-02-01','2.2':'2025-02-02','2.3':'2025-02-03','2.4':'2025-02-04','2.5':'2025-02-05','2.6':'2025-02-06'},quizScores:{'1.1':100,'1.2':50,'1.3':50,'1.4':50,'1.5':50,'1.6':50,'2.1':50,'2.2':50,'2.3':50,'2.4':50,'2.5':50,'2.6':50},notes:{'1.1':'Old kana note','1.2':'Old topic note','1.3':'Old particles note','1.4':'Old polite note','1.5':'Old te-form note','1.6':'Old reading note','2.1':'Old W2D1 note','2.2':'Old W2D2 note','2.3':'Old W2D3 note','2.4':'Old W2D4 note','2.5':'Old W2D5 note','2.6':'Old W2D6 note'},checks:{}},decks:[{id:'jp-vocabulary-v1',name:'Japanese',created:'2025-01-01'}],cards:[{id:'jp-1.1-0',deckId:'jp-vocabulary-v1',front:'切手（きって）',back:'stamp',ease:2.5,interval:0,reps:0,due:'2025-01-01'}]})");
  await send("Page.reload",{ignoreCache:true});
  for(let i=0;i<50;i++){
    if(await evalJs("Boolean(window.__studyHubBooted)")) break;
    await sleep(100);
  }
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click()");
  assert(await evalJs("document.querySelector('#view-japanese').classList.contains('active')"),"Japanese view did not open");
  assert(await evalJs("document.querySelector('.jp-hero:first-child').textContent.includes('5-minute Random Review') && !!document.querySelector('[data-jp-quick-start]')"),"5-minute random review is not the first Japanese home action");
  assert(await evalJs("!!document.querySelector('[data-jp-search]')"),"Japanese search button is missing");
  await evalJs("document.querySelector('[data-jp-search]').click();document.querySelector('#searchInput').value='開';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  const jpSearchProbe=await evalJs("({count:document.querySelectorAll('#searchResults .sr-item').length,kinds:[...document.querySelectorAll('#searchResults .sr-kind')].map(x=>x.textContent)})");
  assert(jpSearchProbe.count>0 && jpSearchProbe.kinds.every(x=>x.includes("Japanese")),"Japanese single-character search failed or leaked Python results: "+JSON.stringify(jpSearchProbe));
  await evalJs("document.querySelector('#searchInput').value='銀色の水筒';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 9')"),"Japanese sentence search did not find Week 9");
  await evalJs("document.querySelector('#searchResults .sr-item').click()");
  assert(await evalJs("document.querySelector('#view-japanese').classList.contains('active') && document.querySelector('.jp-hero h2').textContent==='Day 7' && document.body.textContent.includes('銀色の水筒')"),"Japanese search result did not open its lesson");
  await evalJs("document.querySelector('[data-jp-home]').click()");
  await evalJs("document.querySelector('#searchBtn').click();document.querySelector('#searchInput').value='dictionary';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("[...document.querySelectorAll('#searchResults .sr-kind')].some(x=>!x.textContent.includes('Japanese'))"),"Global search stopped finding Python content");
  await evalJs("document.querySelector('#searchInput').value='財布';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("[...document.querySelectorAll('#searchResults .sr-kind')].some(x=>x.textContent.includes('Japanese'))"),"Global search does not include Japanese content");
  await evalJs("document.querySelector('#searchInput').value='振替輸送';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 11')"),"Japanese search does not index Week 11 content");
  await evalJs("document.querySelector('#searchInput').value='試験運転';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 12')"),"Japanese search does not index Week 12 content");
  await evalJs("document.querySelector('#searchInput').value='異なる目的';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 13')"),"Japanese search does not index Week 13 content");
  await evalJs("document.querySelector('#searchInput').value='習慣化する';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 14')"),"Japanese search does not index Week 14 content");
  await evalJs("document.querySelector('#searchInput').value='転機';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 15')"),"Japanese search does not index Week 15 content");
  await evalJs("document.querySelector('#searchInput').value='観察日記';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 16')"),"Japanese search does not index Week 16 content");
  await evalJs("document.querySelector('#searchInput').value='臨時休業';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 17')"),"Japanese search does not index Week 17 content");
  await evalJs("document.querySelector('#searchInput').value='業務日誌';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 18')"),"Japanese search does not index Week 18 content");
  await evalJs("document.querySelector('#searchInput').value='自転車共有制度';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 19')"),"Japanese search does not index Week 19 content");
    await evalJs("document.querySelector('#searchInput').value='市立病院';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 20')"),"Japanese search does not index Week 20 content");
  await evalJs("document.querySelector('#searchInput').value='在宅勤務';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.querySelectorAll('#searchResults .sr-item').length>0 && document.querySelector('#searchResults').textContent.includes('Week 21')"),"Japanese search does not index Week 21 content");
  await evalJs("document.querySelector('#modalOverlay').click()");
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
  assert(await evalJs("document.querySelectorAll('.jp-study-reveal').length >= 21 && [...document.querySelectorAll('.jp-study-reveal')].every(x=>!x.open)"),"Vocabulary or kanji reading and meaning is open before reveal");
  await evalJs("document.querySelector('.jp-study-reveal summary').click()");
  assert(await evalJs("document.querySelector('.jp-study-reveal').open && document.querySelector('.jp-study-reveal small').getClientRects().length>0"),"Vocabulary reading and meaning did not reveal");
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
  await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=vocab]').click()");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),cards=d.cards.filter(x=>x.deckId==='jp-week-1-vocab'),old=cards.find(x=>x.id==='jp-1.1-0');return d.cards.filter(x=>x.id.startsWith('jp-1.1-te-')).length===10 && cards.every(x=>!x.front.includes('（')&&x.back.includes(' · ')) && old.front==='切手' && old.back.startsWith('きって · ') && old.ease===2.5 && d.decks.some(x=>x.id==='jp-week-1-vocab' && x.name==='Japanese · Week 1 · Vocabulary') && !d.decks.some(x=>x.id==='jp-vocabulary-v1') && !d.decks.some(x=>x.id==='jp-week-1-kanji') && !d.decks.some(x=>x.id==='jp-week-2-vocab');})()"),"Kanji-only vocabulary fronts, reading backs, deck migration, or scheduling preservation failed");
  await evalJs("document.querySelector('[data-jp-cards=kanji]').click();document.querySelector('[data-jp-cards=kanji]').click()");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return d.cards.filter(x=>x.deckId==='jp-week-1-kanji').length===11 && d.cards.filter(x=>x.deckId==='jp-week-1-kanji').every(x=>x.id.includes('-kanji-') && x.back.includes(' · ')) && d.decks.some(x=>x.id==='jp-week-1-kanji' && x.name==='Japanese · Week 1 · Kanji');})()"),"Kanji week deck or cards failed");
  await evalJs("document.querySelector('#sidebar [data-view=flashcards]').click();document.querySelector('#importCardsBtn').click()");
  assert(await evalJs("!!document.querySelector('#csvCardFile') && !!document.querySelector('#csvDeckName') && document.querySelector('#csvImport').disabled"),"CSV import dialog is missing required controls");
  await evalJs("(()=>{const text='term,definition\\n\"学校\",\"がっこう · school, विद्यालय\"\\n\"猫\",\"ねこ · cat, बिरालो\"';const file=new File([text],'CSV Import Test.csv',{type:'text/csv'}),input=document.querySelector('#csvCardFile');Object.defineProperty(input,'files',{value:[file],configurable:true});input.dispatchEvent(new Event('change',{bubbles:true}));})()");
  await sleep(250);
  assert(await evalJs("document.querySelector('#csvImportPreview').textContent.includes('2 cards ready') && document.querySelector('#csvImportPreview').textContent.includes('school, विद्यालय') && document.querySelector('#csvDeckName').value==='CSV Import Test' && !document.querySelector('#csvImport').disabled"),"Quizlet-style quoted CSV preview failed");
  await evalJs("document.querySelector('#csvImport').click()");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),deck=d.decks.find(x=>x.name==='CSV Import Test'),cards=deck?d.cards.filter(x=>x.deckId===deck.id):[];return cards.length===2&&cards.some(x=>x.front==='学校'&&x.back==='がっこう · school, विद्यालय');})()"),"CSV cards were not imported correctly");
  await evalJs("document.querySelector('#importCardsBtn').click();document.querySelector('#csvDeckName').value='CSV Import Test';(()=>{const file=new File(['term\\tdefinition\\n学校\\tがっこう · school, विद्यालय'],'repeat.tsv',{type:'text/tab-separated-values'}),input=document.querySelector('#csvCardFile');Object.defineProperty(input,'files',{value:[file],configurable:true});input.dispatchEvent(new Event('change',{bubbles:true}));})()");
  await sleep(250);
  await evalJs("document.querySelector('#csvImport').click()");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),deck=d.decks.find(x=>x.name==='CSV Import Test');return d.cards.filter(x=>x.deckId===deck.id).length===2;})()"),"TSV parsing or duplicate prevention failed");
  await evalJs("document.querySelector('[data-study=\"jp-week-1-vocab\"]').click()");
  assert(await evalJs("!document.querySelector('#flashcardEl').textContent.includes('（') && document.body.textContent.includes('Tap card to reveal answer')"),"Vocabulary flashcard front reveals the reading");
  await evalJs("document.querySelector('#flashcardEl').click()");
  assert(await evalJs("document.querySelector('#flashcardEl').textContent.includes(' · ') && document.body.textContent.includes('Answer')"),"Vocabulary flashcard back does not show reading and meaning");
  await evalJs("document.querySelector('#exitStudyBtn').click();document.querySelector('[data-manage=\"jp-week-1-kanji\"]').click()");
  const removableKanji=await evalJs("JSON.parse(localStorage.studyHubData_v1).cards.filter(x=>x.deckId==='jp-week-1-kanji').length");
  for(let i=0;i<removableKanji;i++) await evalJs("document.querySelector('[data-delcard]').click()");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return !d.decks.some(x=>x.id==='jp-week-1-kanji') && !d.cards.some(x=>x.deckId==='jp-week-1-kanji') && !document.querySelector('[data-manage=\"jp-week-1-kanji\"]');})()"),"Empty generated kanji deck did not disappear");
  await evalJs("document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-cards=kanji]').click()");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return d.decks.some(x=>x.id==='jp-week-1-kanji') && d.cards.filter(x=>x.deckId==='jp-week-1-kanji').length===11;})()"),"Removed kanji deck did not reappear after adding cards again");
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
    [0,1,1,0,1,1],[1,1,1,0,0,1],[1,0,1,1,0,1],[0,1,1,0,1,1],[0,1,1,0,0,1],[0,1,0,0,0,2],[0,1,1,1,1,0,0,1,1,1],
    [0,1,1,0,1,1],[0,1,0,0,1,1],[0,1,0,0,0,1],[0,1,0,0,1,1],[0,1,0,0,1,1],[0,0,0,0,1,1],[0,0,0,0,0,0,0,0,0,1],
    [0,0,1,0,0,1],[0,1,0,0,1,0],[1,0,1,0,1,0],[0,1,0,0,0,1],[0,0,0,0,0,1],[0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0],
    [0,0,1,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0]];
  for(let i=0;i<63;i++){
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
    if(i>=42 && i<=48){
      const day=i-41, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:') && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Week 7 Day "+day+" content, navigation, On/Kun readings, words, kanji or quiz missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 7 review should not duplicate flashcards");
    }
    if(i>=49 && i<=55){
      const day=i-48, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:') && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Week 8 Day "+day+" content, navigation, On/Kun readings, words, kanji or quiz missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 8 review should not duplicate flashcards");
    }
    if(i>=56 && i<=62){
      const day=i-55, expectedQuiz=[6,6,6,6,6,6,10][day-1];
      assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:') && [...document.querySelectorAll('[data-jp-jump]')].every(x=>document.getElementById(x.dataset.jpJump))"),"Week 9 Day "+day+" content, navigation, On/Kun readings, words, kanji or quiz missing");
      if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 9 review should not duplicate flashcards");
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
    if(i>=42 && i<=48){
      const day=i-41;
      await evalJs("document.querySelector('#jpNotes').value='Week 7 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['7."+day+"']"),"Week 7 Day "+day+" completion did not save");
    }
    if(i>=49 && i<=55){
      const day=i-48;
      await evalJs("document.querySelector('#jpNotes').value='Week 8 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['8."+day+"']"),"Week 8 Day "+day+" completion did not save");
    }
    if(i>=56 && i<=62){
      const day=i-55;
      await evalJs("document.querySelector('#jpNotes').value='Week 9 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
      assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['9."+day+"']"),"Week 9 Day "+day+" completion did not save");
    }
    if(i<62) await evalJs("document.querySelector('.jp-actions [data-jp-lesson]:last-child').click()");
  }
  assert(await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19.1\"]') === null"),"Core path unexpectedly jumps to advanced preview");
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"10.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?10:6;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:')"),"Week 10 Day "+day+" content, words, kanji or quiz missing");
    if(day===1){
      assert(await evalJs("!!document.querySelector('[data-jp-furigana]') && getComputedStyle(document.querySelector('[data-jp-furigana]')).position==='fixed' && document.querySelectorAll('ruby').length===0"),"Floating Furigana button missing or started unexpectedly");
      await evalJs("document.scrollingElement.scrollTop=Math.min(1400,document.scrollingElement.scrollHeight-window.innerHeight);window.__furiganaY=document.scrollingElement.scrollTop;document.querySelector('[data-jp-furigana]').click()");
      assert(await evalJs("localStorage.studyHubJapaneseFurigana==='1' && document.querySelector('[data-jp-furigana]').getAttribute('aria-pressed')==='true' && document.querySelectorAll('ruby rt').length>5 && window.__furiganaY>500 && Math.abs(document.scrollingElement.scrollTop-window.__furiganaY)<10 && document.querySelector('[data-jp-furigana]').getBoundingClientRect().top>=55"),"Floating Furigana did not render, save, or preserve reading position");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 10 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 10 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['10."+day+"']"),"Week 10 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 10 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"10."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"11.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?10:6;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:') && document.querySelectorAll('.jp-panel').length>=12"),"Week 11 Day "+day+" content, words, kanji, teaching blocks or quiz missing");
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return d.cards.filter(x=>x.deckId==='jp-week-11-vocab').length===20 && d.cards.filter(x=>x.deckId==='jp-week-11-kanji').length===5 && d.decks.some(x=>x.id==='jp-week-11-vocab') && d.decks.some(x=>x.id==='jp-week-11-kanji');})()"),"Week 11 vocabulary or kanji flashcards failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 11 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 11 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['11."+day+"']"),"Week 11 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 11 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"11."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"12.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?10:6;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 12 Day "+day+" content, words, kanji, teaching blocks or quiz missing");
    const f=await furiganaCoverage();
    assert(f.bad.length===0 && f.vocab && f.kanji,"Week 12 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===2) assert(await evalJs("!document.body.textContent.includes('Pस्वरूप')"),"Week 12 contains a broken Nepali gloss");
    if(day===4) assert(await evalJs("(()=>{const read=w=>{const r=[...document.querySelectorAll('ruby')].find(x=>x.childNodes[0]&&x.childNodes[0].nodeValue===w);return r&&r.querySelector('rt').textContent};return read('十時半')==='じゅうじはん'&&read('十分')==='じゅっぷん'&&read('触らないで')==='さわらないで'&&read('十時二十分')==='じゅうじにじゅっぷん';})()"),"Week 12 time, counter, or verb Furigana is incorrect");
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return d.cards.filter(x=>x.deckId==='jp-week-12-vocab').length===20 && d.cards.filter(x=>x.deckId==='jp-week-12-kanji').length===5;})()"),"Week 12 vocabulary or kanji flashcards failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 12 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 12 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['12."+day+"']"),"Week 12 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 12 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"12."+(day+1)+"\"]').click()");
  }
  for(let week=1;week<=21;week++){
    const lessonId=day=>week===19 ? "19."+day+".core" : week+"."+day;
    await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\""+week+"\"]').click();document.querySelector('[data-jp-lesson=\""+lessonId(1)+"\"]').click()");
    for(let day=1;day<=7;day++){
      const f=await furiganaCoverage();
      assert(f.bad.length===0 && f.vocab && f.kanji,"Week "+week+" Day "+day+" incomplete Furigana: "+JSON.stringify(f));
      if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length>=3 && document.querySelectorAll('.jp-review-drill details').length>=18"),"Week "+week+" review day lacks weekly vocabulary, kanji, and grammar retrieval drills");
      if((week===5&&day===5)||(week===8&&day===4)) assert(await evalJs("(()=>{const r=[...document.querySelectorAll('ruby')].find(x=>x.childNodes[0]&&x.childNodes[0].nodeValue==='十分');return !!r&&r.querySelector('rt').textContent==='じゅうぶん';})()"),"十分 meaning 'enough' has the wrong Furigana in Week "+week+" Day "+day);
      if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\""+lessonId(day+1)+"\"]').click()");
    }
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-hero [data-jp-lesson=\"13.1\"]') !== null && document.querySelector('.jp-progress').getAttribute('aria-valuenow') === '84' && !document.body.textContent.includes('Your weekly rhythm')"),"Week 12 completion count, Week 13 continuation, or removed rhythm panel changed");
  assert(await evalJs("!document.querySelector('[data-jp-quick-start]').disabled"),"5-minute random review stayed disabled after lessons were completed");
  await evalJs("document.querySelector('[data-jp-quick-start]').click()");
  assert(await evalJs("!!document.querySelector('#jpQuickTime') && document.querySelectorAll('[data-jp-quick-answer]').length>=3 && document.body.textContent.includes('Question 1 of')"),"5-minute random review did not start");
  await evalJs("document.querySelector('[data-jp-quick-answer]').click()");
  assert(await evalJs("!!document.querySelector('.jp-result') && !!document.querySelector('[data-jp-quick-next]')"),"Random review did not reveal feedback");
  await evalJs("document.querySelector('[data-jp-quick-exit]').click()");
  assert(await evalJs("!!document.querySelector('[data-jp-quick-start]') && !document.querySelector('#jpQuickTime')"),"Random review did not return to Japanese home");
  await evalJs("document.querySelector('[data-jp-week=\"13\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1))"),"Week 13 day list or short titles are incorrect");
  await evalJs("document.querySelector('[data-jp-lesson=\"13.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 13 Day "+day+" content, vocabulary, kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 13 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 13 review lacks grouped vocabulary, kanji, grammar, or reading drills");
    const f=await furiganaCoverage();
    assert(f.bad.length===0 && f.vocab && f.kanji,"Week 13 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1);return d.cards.filter(x=>x.deckId==='jp-week-13-vocab').length===20 && d.cards.filter(x=>x.deckId==='jp-week-13-kanji').length===5;})()"),"Week 13 flashcard decks failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 13 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 13 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['13."+day+"']"),"Week 13 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 13 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"13."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='91' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147' && !!document.querySelector('[data-jp-lesson=\"14.1\"]')"),"Week 13 completion total or Week 14 continuation is incorrect");
  await evalJs("document.querySelector('[data-jp-week=\"14\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 14 finish line')"),"Week 14 day list, short titles, or finish line is missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"14.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 14 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 14 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 14 review lacks 40 grouped vocabulary, Kanji, grammar, and reading drills");
    const f=await furiganaCoverage();
    assert(f.bad.length===0 && f.vocab && f.kanji,"Week 14 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-14-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-14-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '))&&k.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 14 flashcard decks or front/back format failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 14 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 14 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['14."+day+"']"),"Week 14 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 14 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"14."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='98' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147' && !!document.querySelector('[data-jp-lesson=\"15.1\"]')"),"Week 14 completion total or Week 15 continuation is incorrect");
  await evalJs("document.querySelector('[data-jp-week=\"15\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 15 finish line')"),"Week 15 day list, short titles, or finish line is missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"15.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 15 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 15 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 15 review lacks 40 grouped drills");
    const f=await furiganaCoverage();
    assert(f.bad.length===0 && f.vocab && f.kanji,"Week 15 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-15-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-15-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 15 flashcards or front/back format failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 15 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 15 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['15."+day+"']"),"Week 15 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 15 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"15."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='105' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147' && !!document.querySelector('[data-jp-lesson=\"16.1\"]')"),"Week 15 completion total or Week 16 continuation is incorrect");
  await evalJs("document.querySelector('[data-jp-week=\"16\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 16 finish line')"),"Week 16 day list, short titles, or finish line is missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"16.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 16 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 16 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 16 review lacks 40 grouped drills");
    const f=await furiganaCoverage();
    assert(f.bad.length===0 && f.vocab && f.kanji,"Week 16 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-16-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-16-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 16 flashcards or front/back format failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 16 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 16 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['16."+day+"']"),"Week 16 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 16 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"16."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='112' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147' && !!document.querySelector('[data-jp-lesson=\"17.1\"]')"),"Week 16 completion total or Week 17 continuation is incorrect");
  await evalJs("document.querySelector('[data-jp-week=\"17\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 17 finish line')"),"Week 17 day list, short titles, or finish line is missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"17.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 17 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 17 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 17 review lacks 40 grouped drills");
    const f=await furiganaCoverage();
    assert(f.bad.length===0 && f.vocab && f.kanji,"Week 17 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){
      await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");
      assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-17-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-17-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 17 flashcards or front/back format failed");
    }
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 17 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 17 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['17."+day+"']"),"Week 17 Day "+day+" completion did not save");
    if(day===7) assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 17 review should not duplicate flashcards");
    if(day<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"17."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='119' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147' && !!document.querySelector('[data-jp-lesson=\"18.1\"]')"),"Week 17 completion total or Week 18 continuation is incorrect");
  await evalJs("document.querySelector('[data-jp-week=\"18\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 18 finish line')"),"Week 18 day list, short titles, or finish line is missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"18.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 18 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 18 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 18 review lacks 40 grouped drills");
    const f=await furiganaCoverage();assert(f.bad.length===0&&f.vocab&&f.kanji,"Week 18 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-18-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-18-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 18 flashcards or front/back format failed");}
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 18 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 18 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['18."+day+"']"),"Week 18 Day "+day+" completion did not save");
    if(day===7)assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 18 review should not duplicate flashcards");
    if(day<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"18."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='126' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147'"),"Week 18 completion total is incorrect");
  assert(await evalJs("!!document.querySelector('[data-jp-lesson=\"19.1.core\"]')"),"Week 18 does not continue to Week 19 core");
  await evalJs("document.querySelector('[data-jp-week=\"19\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 19 finish line')"),"Week 19 day list, short titles, or finish line is missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"19.1.core\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 19 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7) assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 19 Day "+day+" does not have ten written exercises");
    if(day===7) assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 19 review lacks 40 grouped drills");
    const f=await furiganaCoverage();assert(f.bad.length===0&&f.vocab&&f.kanji,"Week 19 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-19-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-19-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 19 flashcards or front/back format failed");}
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 19 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 19 core note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['19."+day+".core']"),"Week 19 Day "+day+" completion did not save");
    if(day===7)assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 19 review should not duplicate flashcards");
    if(day<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19."+(day+1)+".core\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='133' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147'"),"Week 19 completion total is incorrect");
  assert(await evalJs("!!document.querySelector('[data-jp-lesson=\"20.1\"]')"),"Week 19 does not continue to Week 20");
  await evalJs("document.querySelector('[data-jp-week=\"20\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 20 finish line')"),"Week 20 day list, titles, or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"20.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 20 Day "+day+" content, vocabulary, Kanji, panels, or quiz missing");
    if(day<7)assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 20 Day "+day+" lacks ten written exercises");
    if(day===7)assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 20 review lacks 40 drills");
    const f=await furiganaCoverage();assert(f.bad.length===0&&f.vocab&&f.kanji,"Week 20 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-20-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-20-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 20 flashcards failed");}
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 20 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 20 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['20."+day+"']"),"Week 20 Day "+day+" completion did not save");
    if(day===7)assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 20 review should not duplicate flashcards");
    if(day<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"20."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='140' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147'"),"Week 20 completion total is incorrect");
  assert(await evalJs("!!document.querySelector('[data-jp-lesson=\"21.1\"]')"),"Week 20 does not continue to Week 21");
  await evalJs("document.querySelector('[data-jp-week=\"21\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 21 finish line')"),"Week 21 lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"21.1\"]').click()");
  for(let day=1;day<=7;day++){
    const expectedQuiz=day===7?20:8;
    assert(await evalJs("document.querySelector('.jp-hero h2').textContent==='Day "+day+"' && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('.jp-q').length==="+expectedQuiz+" && document.querySelectorAll('.jp-panel').length>=12"),"Week 21 Day "+day+" content missing");
    if(day<7)assert(await evalJs("[...document.querySelectorAll('.jp-panel')].some(x=>x.querySelector('h3')&&x.querySelector('h3').textContent.includes('Write and compare')&&x.querySelectorAll('.jp-example').length>=10)"),"Week 21 Day "+day+" lacks ten exercises");
    if(day===7)assert(await evalJs("document.querySelectorAll('.jp-review-drill').length===4 && document.querySelectorAll('.jp-review-drill details').length===40"),"Week 21 review lacks 40 drills");
    const f=await furiganaCoverage();assert(f.bad.length===0&&f.vocab&&f.kanji,"Week 21 Day "+day+" Furigana coverage failed: "+JSON.stringify(f));
    if(day===1){await evalJs("document.querySelector('[data-jp-cards=vocab]').click();document.querySelector('[data-jp-cards=kanji]').click()");assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),v=d.cards.filter(x=>x.deckId==='jp-week-21-vocab'),k=d.cards.filter(x=>x.deckId==='jp-week-21-kanji');return v.length===20&&k.length===5&&v.every(x=>!x.front.includes('（')&&x.back.includes(' · '));})()"),"Week 21 flashcards failed");}
    await evalJs("Array.from({length:"+expectedQuiz+"},(_,j)=>document.querySelector('input[name=jpq'+j+'][value=\"0\"]')).forEach(x=>x.click());document.querySelector('[data-jp-quiz]').click()");
    assert(await evalJs("document.querySelector('.jp-result').textContent.includes('"+expectedQuiz+" / "+expectedQuiz+" correct')"),"Week 21 Day "+day+" quiz failed");
    await evalJs("document.querySelector('#jpNotes').value='Week 21 note "+day+"';document.querySelector('#jpNotes').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-done]').click()");
    assert(await evalJs("!!JSON.parse(localStorage.studyHubData_v1).japanese.done['21."+day+"']"),"Week 21 Day "+day+" completion failed");
    if(day===7)assert(await evalJs("!document.querySelector('[data-jp-cards]')"),"Week 21 review duplicates flashcards");
    if(day<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"21."+(day+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click()");
  assert(await evalJs("document.querySelector('.jp-progress').getAttribute('aria-valuenow')==='147' && document.querySelector('.jp-progress').getAttribute('aria-valuemax')==='147'"),"Week 21 completion total incorrect");
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
  assert(await evalJs("['7.1','7.2','7.3','7.4','7.5','7.6','7.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 7 note '+(i+1))"),"Week 7 progress did not survive reload");
  assert(await evalJs("['8.1','8.2','8.3','8.4','8.5','8.6','8.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 8 note '+(i+1))"),"Week 8 progress did not survive reload");
  assert(await evalJs("['9.1','9.2','9.3','9.4','9.5','9.6','9.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 9 note '+(i+1))"),"Week 9 progress did not survive reload");
  assert(await evalJs("['10.1','10.2','10.3','10.4','10.5','10.6','10.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 10 note '+(i+1)) && localStorage.studyHubJapaneseFurigana==='1'"),"Week 10 progress or Furigana preference did not survive reload");
  assert(await evalJs("['11.1','11.2','11.3','11.4','11.5','11.6','11.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 11 note '+(i+1))"),"Week 11 progress did not survive reload");
  assert(await evalJs("['12.1','12.2','12.3','12.4','12.5','12.6','12.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 12 note '+(i+1))"),"Week 12 progress did not survive reload");
  assert(await evalJs("['13.1','13.2','13.3','13.4','13.5','13.6','13.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 13 note '+(i+1))"),"Week 13 progress did not survive reload");
  assert(await evalJs("['14.1','14.2','14.3','14.4','14.5','14.6','14.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 14 note '+(i+1))"),"Week 14 progress did not survive reload");
  assert(await evalJs("['15.1','15.2','15.3','15.4','15.5','15.6','15.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 15 note '+(i+1))"),"Week 15 progress did not survive reload");
  assert(await evalJs("['16.1','16.2','16.3','16.4','16.5','16.6','16.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 16 note '+(i+1))"),"Week 16 progress did not survive reload");
  assert(await evalJs("['17.1','17.2','17.3','17.4','17.5','17.6','17.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 17 note '+(i+1))"),"Week 17 progress did not survive reload");
  assert(await evalJs("['18.1','18.2','18.3','18.4','18.5','18.6','18.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 18 note '+(i+1))"),"Week 18 progress did not survive reload");
  assert(await evalJs("['19.1.core','19.2.core','19.3.core','19.4.core','19.5.core','19.6.core','19.7.core'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 19 core note '+(i+1))"),"Week 19 core progress did not survive reload");
  assert(await evalJs("['20.1','20.2','20.3','20.4','20.5','20.6','20.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 20 note '+(i+1))"),"Week 20 progress did not survive reload");
  assert(await evalJs("['21.1','21.2','21.3','21.4','21.5','21.6','21.7'].every((k,i)=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k] && JSON.parse(localStorage.studyHubData_v1).japanese.quizScores[k]===100 && JSON.parse(localStorage.studyHubData_v1).japanese.notes[k]==='Week 21 note '+(i+1))"),"Week 21 progress did not survive reload");
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
  await evalJs("document.querySelector('[data-jp-search]').click();document.querySelector('#searchInput').value='てある';document.querySelector('#searchInput').dispatchEvent(new Event('input',{bubbles:true}))");
  await sleep(220);
  assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelector('#modalBox').getBoundingClientRect().right<=window.innerWidth && document.querySelectorAll('#searchResults .sr-item').length>0"),"Japanese search modal overflows or has no mobile results");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-search-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('#modalOverlay').click()");
  assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelector('.jp-hero:first-child').textContent.includes('5-minute Random Review')"),"Mobile 5-minute review home card overflows or is missing");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-quick-review-mobile.png"),Buffer.from(shot.data,"base64"));
  }
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
      await evalJs("(()=>{const r=document.querySelector('.jp-reading').getBoundingClientRect();window.scrollTo(0,Math.max(0,window.scrollY+r.top-190));})() ");
      assert(await evalJs("document.querySelector('[data-jp-furigana]').getBoundingClientRect().top>=120 && document.querySelector('[data-jp-furigana]').getBoundingClientRect().bottom<window.innerHeight"),"Mobile floating Furigana control is not visible while reading");
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week6-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"6."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"7\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 7 finish line')"),"Mobile Week 7 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"7.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:')"),"Mobile Week 7 Day "+n+" overflow, reading or study count failure");
    if(process.env.JP_SHOTS && n===1){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week7-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"7."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"8\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 8 finish line')"),"Mobile Week 8 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"8.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:')"),"Mobile Week 8 Day "+n+" overflow, reading or study count failure");
    if(process.env.JP_SHOTS && n===1){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week8-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"8."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"9\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 9 finish line')"),"Mobile Week 9 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"9.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.body.textContent.includes('On:') && document.body.textContent.includes('Kun:')"),"Mobile Week 9 Day "+n+" overflow, reading or study count failure");
    if(process.env.JP_SHOTS && n===1){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week9-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"9."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"10\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 10 finish line')"),"Mobile Week 10 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"10.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>5"),"Mobile Week 10 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS && n===1){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week10-furigana-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"10."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"11\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 11 finish line')"),"Mobile Week 11 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"11.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>5"),"Mobile Week 11 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS && n===1){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week11-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"11."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"12\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 12 finish line')"),"Mobile Week 12 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"12.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 12 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS && n===6){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week12-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"12."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"13\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 13 finish line')"),"Mobile Week 13 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"13.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 13 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS && n===7){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week13-review-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"13."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"14\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 14 finish line')"),"Mobile Week 14 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"14.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth <= window.innerWidth + 1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 14 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS && n===7){
      const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
      fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week14-review-mobile.png"),Buffer.from(shot.data,"base64"));
    }
    if(n<7) await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"14."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"15\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 15 finish line')"),"Mobile Week 15 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"15.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 15 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week15-review-mobile.png"),Buffer.from(shot.data,"base64"));}
    if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"15."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"16\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 16 finish line')"),"Mobile Week 16 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"16.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 16 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week16-review-mobile.png"),Buffer.from(shot.data,"base64"));}
    if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"16."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"17\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 17 finish line')"),"Mobile Week 17 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"17.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){
    assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 17 Day "+n+" overflow, content or Furigana failure");
    if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week17-review-mobile.png"),Buffer.from(shot.data,"base64"));}
    if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"17."+(n+1)+"\"]').click()");
  }
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"18\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 18 finish line')"),"Mobile Week 18 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"18.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 18 Day "+n+" overflow, content or Furigana failure");if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week18-review-mobile.png"),Buffer.from(shot.data,"base64"));}if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"18."+(n+1)+"\"]').click()");}
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"19\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && [...document.querySelectorAll('.jp-day-card strong')].every((x,i)=>x.textContent==='Day '+(i+1)) && document.body.textContent.includes('Week 19 finish line')"),"Mobile Week 19 short titles, lessons or finish line missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"19.1.core\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20 && document.querySelectorAll('.jp-kanji-readings').length===5"),"Mobile Week 19 Day "+n+" overflow, content or Furigana failure");if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week19-review-mobile.png"),Buffer.from(shot.data,"base64"));}if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"19."+(n+1)+".core\"]').click()");}
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"20\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && document.body.textContent.includes('Week 20 finish line')"),"Mobile Week 20 lessons missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"20.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20"),"Mobile Week 20 Day "+n+" failed");if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week20-review-mobile.png"),Buffer.from(shot.data,"base64"));}if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"20."+(n+1)+"\"]').click()");}
  await evalJs("document.querySelector('[data-jp-home]').click();document.querySelector('[data-jp-week=\"21\"]').click()");
  assert(await evalJs("document.querySelectorAll('.jp-day-card').length===7 && document.body.textContent.includes('Week 21 finish line')"),"Mobile Week 21 lessons missing");
  await evalJs("document.querySelector('[data-jp-lesson=\"21.1\"]').click()");
  for(const n of [1,2,3,4,5,6,7]){assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelectorAll('.jp-vocab')[0].children.length===20 && document.querySelectorAll('.jp-vocab')[1].children.length===5 && document.querySelectorAll('ruby rt').length>20"),"Mobile Week 21 Day "+n+" failed");if(process.env.JP_SHOTS&&n===7){const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),"studyhub-japanese-week21-review-mobile.png"),Buffer.from(shot.data,"base64"));}if(n<7)await evalJs("document.querySelector('.jp-actions [data-jp-lesson=\"21."+(n+1)+"\"]').click()");}
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
  assert(await evalJs("['7.1','7.2','7.3','7.4','7.5','7.6','7.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 7 progress");
  assert(await evalJs("['8.1','8.2','8.3','8.4','8.5','8.6','8.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 8 progress");
  assert(await evalJs("['9.1','9.2','9.3','9.4','9.5','9.6','9.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 9 progress");
  assert(await evalJs("['10.1','10.2','10.3','10.4','10.5','10.6','10.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 10 progress");
  assert(await evalJs("['11.1','11.2','11.3','11.4','11.5','11.6','11.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 11 progress");
  assert(await evalJs("['12.1','12.2','12.3','12.4','12.5','12.6','12.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 12 progress");
  assert(await evalJs("['13.1','13.2','13.3','13.4','13.5','13.6','13.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 13 progress");
  assert(await evalJs("['14.1','14.2','14.3','14.4','14.5','14.6','14.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 14 progress");
  assert(await evalJs("['15.1','15.2','15.3','15.4','15.5','15.6','15.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 15 progress");
  assert(await evalJs("['16.1','16.2','16.3','16.4','16.5','16.6','16.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 16 progress");
  assert(await evalJs("['17.1','17.2','17.3','17.4','17.5','17.6','17.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 17 progress");
  assert(await evalJs("['18.1','18.2','18.3','18.4','18.5','18.6','18.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 18 progress");
  assert(await evalJs("['19.1.core','19.2.core','19.3.core','19.4.core','19.5.core','19.6.core','19.7.core'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 19 core progress");
  assert(await evalJs("['20.1','20.2','20.3','20.4','20.5','20.6','20.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 20 progress");
  assert(await evalJs("['21.1','21.2','21.3','21.4','21.5','21.6','21.7'].every(k=>!!JSON.parse(localStorage.studyHubData_v1).japanese.done[k])"),"Import erased Week 21 progress");
  assert(await evalJs("(()=>{const d=JSON.parse(localStorage.studyHubData_v1),deck=d.decks.find(x=>x.name==='CSV Import Test');return !!deck&&d.cards.filter(x=>x.deckId===deck.id).length===2;})()"),"Backup/import erased CSV flashcards");
  assert(await evalJs("Object.keys(JSON.parse(localStorage.studyHubData_v1).reviews.items).length >= 84"),"Import erased spaced-review records");
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
  assert(await evalJs("window.__syncBody.includes('old-note') && window.__syncBody.includes('reviews') && !window.__syncBody.includes('synthetic-test-token-123456')"),"Push payload lost notes/reviews or contained token");
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
  await evalJs("document.querySelector('#sidebar [data-view=flashcards]').click();document.querySelector('#importCardsBtn').click()");
  assert(await evalJs("document.documentElement.scrollWidth<=window.innerWidth+1 && document.querySelector('#modalBox').getBoundingClientRect().right<=window.innerWidth && !!document.querySelector('#csvCardFile')"),"CSV import dialog overflows or is missing on mobile");
  if(process.env.JP_SHOTS){
    const shot=await send("Page.captureScreenshot",{format:"png",captureBeyondViewport:false});
    fs.writeFileSync(path.join(os.tmpdir(),"studyhub-flashcard-csv-mobile.png"),Buffer.from(shot.data,"base64"));
  }
  await evalJs("document.querySelector('#csvCancel').click()");
  assert(errors.length===0,"JavaScript errors: "+errors.join("; "));
  console.log("PASS: Japanese Weeks 1–21, Kanji-only flashcard fronts, CSV/TSV import, 5-minute random review, weekly retrieval drills, Furigana, search, progress, mobile, dark mode, backup, mock Gist sync, no JS exceptions");
  ws.close();
}
main().catch(err=>{console.error(err);process.exitCode=1;}).finally(()=>{browser.kill();});
