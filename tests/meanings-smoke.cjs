const fs=require("fs");
const os=require("os");
const path=require("path");
const {spawn}=require("child_process");
const {pathToFileURL}=require("url");

const chromePath="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const profile=fs.mkdtempSync(path.join(os.tmpdir(),"studyhub-review-"));
const browser=spawn(chromePath,["--headless=new","--disable-gpu","--no-sandbox","--no-first-run","--remote-debugging-port=0","--user-data-dir="+profile,pathToFileURL(path.resolve(__dirname,"..","study-hub.html")).href],{stdio:"ignore"});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
  let port;
  for(let i=0;i<100;i++){const f=path.join(profile,"DevToolsActivePort");if(fs.existsSync(f)){port=Number(fs.readFileSync(f,"utf8").split("\n")[0]);break;}await sleep(100);}
  if(!port)throw Error("Chrome did not start");
  const tabs=await(await fetch("http://127.0.0.1:"+port+"/json/list")).json(),page=tabs.find(x=>x.type==="page");
  const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  let seq=0;const pending=new Map(),errors=[];
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==="Runtime.exceptionThrown"){const d=m.params.exceptionDetails;errors.push((d.exception&&d.exception.description)||d.text);}if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((res,rej)=>{const id=++seq;pending.set(id,{resolve:res,reject:rej});ws.send(JSON.stringify({id,method,params}));});
  const evalJs=async expression=>{const r=await send("Runtime.evaluate",{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error((r.exceptionDetails.exception&&r.exceptionDetails.exception.description)||r.exceptionDetails.text);return r.result.value;};
  const assert=(v,m)=>{if(!v)throw Error(m);};
  await send("Runtime.enable");await send("Page.enable");
  for(let i=0;i<50;i++){if(await evalJs("Boolean(window.__studyHubBooted)"))break;await sleep(100);}
  assert(await evalJs("window.__studyHubBooted"),"App did not boot: "+errors.join("; "));

  await evalJs(`localStorage.studyHubData_v1=JSON.stringify({notes:[{id:'old',title:'Preserve',body:'original'}],japanese:{done:{'1.1':'2026-01-01'},notes:{'1.1':'saved lesson note'},checks:{},quizScores:{}}})`);
  await send('Page.reload',{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  await evalJs(`document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-meanings=home]').click()`);
  assert(await evalJs(`document.querySelector('.jp-hero h2').textContent==='Meaning Folder'&&document.querySelectorAll('[data-jp-meanings]').length===4`),'Meaning folder navigation missing');
  await evalJs(`document.querySelector('[data-jp-meanings=opposites]').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-pair').length===100&&document.querySelectorAll('.jp-meaning-pair .jp-study-item').length===200`),'Opposites count incorrect');
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-pair details[open]').length===0`),'Answers shown before reveal');
  await evalJs(`document.querySelector('[data-jp-furigana]').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-pair ruby rt').length===200`),'Furigana readings missing');
  for(const query of ['おおきい','expensive','महँगो']){
    await evalJs(`document.querySelector('#jpMeaningSearch').value=${JSON.stringify(query)};document.querySelector('#jpMeaningSearch').dispatchEvent(new Event('input',{bubbles:true}))`);
    assert(await evalJs(`document.querySelectorAll('.jp-meaning-pair').length===1`),'Search failed '+query);
  }
  await evalJs(`document.querySelector('#jpMeaningSearch').value='';document.querySelector('#jpMeaningSearch').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('[data-jp-hard-word="大きい"]').click();document.querySelector('[data-jp-meaning-add]').click();document.querySelector('[data-jp-meaning-add]').click()`);
  assert(await evalJs(`(()=>{const d=JSON.parse(localStorage.studyHubData_v1),deck=d.decks.find(x=>x.jpMeaningFolder==='opposites');return deck&&d.cards.filter(x=>x.deckId===deck.id).length===100&&d.japanese.checks['hard:v:大きい'].hard;})()`),'Hard marking or duplicate-safe flashcards failed');
  await evalJs(`document.querySelector('[data-jp-meanings=synonyms]').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-pair').length===30&&document.querySelector('.jp-meaning-context').textContent.includes('grammar')`),'Synonym content/notes missing');
  await evalJs(`document.querySelector('[data-jp-meaning-add]').click();document.querySelector('[data-jp-meanings=uploads]').click();document.querySelector('[data-jp-meaning-import]').click()`);
  assert(await evalJs(`document.querySelector('#csvDeckName').value.startsWith('Japanese · Meanings')`),'Shared importer default absent');
  const csv='front,back\r\n"花","はな · flower, फूल\nNear synonym context"\r\n"猫","ねこ · cat <img src=x onerror=alert(1)>"\r\n"花","はな · flower, फूल\nNear synonym context"';
  const upload=async text=>{
    await evalJs(`(()=>{const f=new File([${JSON.stringify(text)}],'meaning-test.csv',{type:'text/csv'}),dt=new DataTransfer();dt.items.add(f);const el=document.querySelector('#csvCardFile');el.files=dt.files;el.dispatchEvent(new Event('change',{bubbles:true}));})()`);
    for(let i=0;i<40;i++){if(await evalJs(`document.querySelector('#csvImportPreview').style.display==='block'`))break;await sleep(50);}
  };
  await upload(csv);
  assert(await evalJs(`!document.querySelector('#csvImport').disabled&&document.querySelector('#csvImportPreview').textContent.includes('3 cards ready')&&!document.querySelector('#csvImportPreview img')`),'CSV preview quoting/multiline or escaping failed');
  await evalJs(`document.querySelector('#csvDeckName').value='Meaning upload test';document.querySelector('#csvImport').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-upload').length===2&&!document.querySelector('.jp-meaning-upload img')`),'Imported duplicate handling or rendering failed');
  assert(await evalJs(`(()=>{const d=JSON.parse(localStorage.studyHubData_v1),deck=d.decks.find(x=>x.name==='Meaning upload test');return deck.jpMeaningFolder==='uploaded'&&d.cards.filter(x=>x.deckId===deck.id).length===2&&d.notes[0].body==='original'&&d.japanese.notes['1.1']==='saved lesson note';})()`),'Upload did not preserve existing data');
  await evalJs(`document.querySelector('[data-jp-meaning-import]').click()`);
  await upload(csv);
  await evalJs(`document.querySelector('#csvDeckName').value='Meaning upload test';document.querySelector('#csvImport').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-upload').length===2`),'Repeat upload duplicated words');
  await evalJs(`document.querySelector('[data-jp-meaning-import]').click()`);
  await upload('front,back\nempty,');
  assert(await evalJs(`document.querySelector('#csvImport').disabled&&document.querySelector('#csvImportPreview').textContent.includes('No valid cards')`),'Invalid CSV was accepted');
  await evalJs(`document.querySelector('#csvCancel').click();document.querySelector('[data-jp-meaning-manage]').click()`);
  assert(await evalJs(`document.querySelector('#modalBox').textContent.includes('Meaning upload test')`),'Manage uploaded words missing');
  await evalJs(`document.querySelector('#modalOverlay').click()`);
  await send('Page.reload',{ignoreCache:true});
  for(let i=0;i<50;i++){if(await evalJs('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  await evalJs(`document.querySelector('#sidebar [data-view=japanese]').click();document.querySelector('[data-jp-meanings=home]').click();document.querySelector('[data-jp-meanings=uploads]').click()`);
  assert(await evalJs(`document.querySelectorAll('[data-jp-meaning-deck]').length===1`),'Upload folder lost after reload');
  await evalJs(`document.querySelector('[data-jp-meaning-deck]').click()`);
  assert(await evalJs(`document.querySelectorAll('.jp-meaning-upload').length===2`),'Upload words lost after reload');
  await evalJs(`document.querySelector('[data-jp-meaning-study]').click()`);
  assert(await evalJs(`document.querySelector('#view-flashcards').classList.contains('active')&&!!document.querySelector('#flashcardEl')&&!document.querySelector('#flashcardEl').textContent.includes(' · ')`),'Study button did not open visible Kanji-front flashcards');
  await evalJs(`document.querySelector('#flashcardEl').click()`);
  assert(await evalJs(`document.querySelector('#flashcardEl').textContent.includes(' · ')`),'Flashcard answer did not flip');
  await evalJs(`document.querySelector('#exitStudyBtn').click();document.querySelector('#sidebar [data-view=japanese]').click()`);
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  for(const type of ['opposites','synonyms','uploads']){
    await evalJs(`document.querySelector('[data-jp-meanings=${type}]').click()`);
    assert(await evalJs(`document.documentElement.scrollWidth<=innerWidth+1`),'Mobile overflow '+type);
  }
  await evalJs(`document.querySelector('[data-jp-meanings=opposites]').click();document.querySelector('.jp-study-reveal').open=true;document.querySelector('.jp-meaning-context').open=true;document.querySelector('#themeBtn').click()`);
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-meanings-mobile.png'),Buffer.from(shot.data,'base64'));
  await evalJs(`document.querySelector('.jp-meaning-pair').scrollIntoView()`);
  const pairShot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  fs.writeFileSync(path.join(os.tmpdir(),'studyhub-meanings-pair-mobile.png'),Buffer.from(pairShot.data,'base64'));
  await evalJs(`(()=>{const dt=new DataTransfer();dt.items.add(new File([JSON.stringify({notes:[{id:'backup-note',body:'merge'}]})],'backup.json',{type:'application/json'}));const input=document.querySelector('#importFile');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));})()`);
  for(let i=0;i<40;i++){if(await evalJs(`!!document.querySelector('#impMerge')`))break;await sleep(50);}
  await evalJs(`document.querySelector('#impMerge').click()`);
  assert(await evalJs(`(()=>{const d=JSON.parse(localStorage.studyHubData_v1),deck=d.decks.find(x=>x.name==='Meaning upload test');return deck.jpMeaningFolder==='uploaded'&&d.cards.filter(x=>x.deckId===deck.id).length===2&&d.notes.some(x=>x.id==='backup-note')&&d.japanese.notes['1.1']==='saved lesson note';})()`),'Backup merge lost uploaded words or existing progress');
  await evalJs(`document.querySelector('[data-jp-meanings=uploads]').click();document.querySelector('[data-jp-meaning-deck]').click();document.querySelector('[data-jp-meaning-manage]').click();document.querySelector('[data-delcard]').click();document.querySelector('[data-delcard]').click();document.querySelector('#mdClose').click()`);
  assert(await evalJs(`document.querySelectorAll('[data-jp-meaning-deck]').length===0&&document.querySelector('#jpMeaningResults').textContent.includes('No uploaded words')`),'Empty folder did not disappear after deleting words');
  assert(errors.length===0,'JavaScript errors: '+errors.join('; '));
  console.log('PASS: 100 opposites, 30 synonyms, meanings search, hidden answers, Furigana, hard words, flashcards, CSV preview/import/dedup/escaping, reload, backup merge, mobile and theme, no JS errors');
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
