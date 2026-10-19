const fs=require('fs'),os=require('os'),path=require('path'),{spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-habits-')),fixture=path.join(profile,'habits.html');
fs.writeFileSync(fixture,fs.readFileSync('study-hub.html','utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const f=path.join(profile,'DevToolsActivePort');if(fs.existsSync(f)){port=Number(fs.readFileSync(f,'utf8').split('\n')[0]);break;}await sleep(100);}if(!port)throw Error('Chrome did not start');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval ? window.__courseTestEval('+JSON.stringify(expression)+') : eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 const assert=(v,m)=>{if(!v)throw Error(m);};
 await send('Runtime.enable');await send('Page.enable');for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}assert(await evaluate('window.__studyHubBooted'),'Boot failed');

 await evaluate(`closeModal();DB=applyDefaults({notes:[{id:'old-note',body:'Keep personal notes'}],decks:[{id:'old-pairs',name:'Japanese · Meanings · 100 Opposites',jpMeaningFolder:'opposites'}],cards:[{id:'old-card',deckId:'old-pairs',front:'大きい',back:'old studied answer',ease:2.7,interval:10,reps:5,due:'2026-11-01'}],japanese:{done:{'19.1':'2026-10-01'},notes:{'19.1':'Keep source lesson'},quizScores:{'19.1':75},checks:{}},course:{done:{'1.0':'2026-10-01'}}});save();switchView('japanese');jpPage.mode='meanings';JP_MEANING_STATE.tab='home';renderJapanese();closeModal()`);
 assert(await evaluate(`document.querySelectorAll('.jp-week-card[data-jp-meanings]').length===3`),'Folder home missing');
 await evaluate(`document.querySelector('[data-jp-meanings=opposites]').click()`);
 assert(await evaluate(`!document.querySelector('.jp-week-card[data-jp-meanings]')&&document.querySelectorAll('.jp-study-reveal[open]').length===200&&!!document.querySelector('[data-jp-meanings=home]')`),'Folder is not isolated / meanings not visible');
 const original=await evaluate('JSON.stringify(JP_MEANING_DATA)'),before=await evaluate('JSON.stringify(DB)');
 await evaluate(`document.querySelector('[data-jp-pair-add]').click();document.querySelector('#mpField0').value='Discard';document.querySelector('#jpPairCancel').click()`);
 assert(await evaluate('JSON.stringify(DB)')===before,'Cancel saved a draft');
 async function fill(values){await evaluate(`(${JSON.stringify(values)}).forEach((v,i)=>document.querySelector('#mpField'+i).value=v);document.querySelector('#jpPairForm').requestSubmit()`);}
 const opposite=['学習開始','がくしゅうかいし','start studying · पढाइ सुरु','学習終了','がくしゅうしゅうりょう','finish studying · पढाइ अन्त्य','Opposing stages in this practice example.'];
 await evaluate(`document.querySelector('[data-jp-pair-add]').click()`);await fill(opposite);
 assert(await evaluate(`jpMeaningPairs('opposites').length===101&&document.querySelectorAll('.jp-meaning-pair').length===101&&Object.keys(DB.japanese.meaningPairs).length===1`),'Custom opposite not saved');
 const custom=await evaluate(`jpMeaningPairs('opposites').at(-1).key`);
 await evaluate(`document.querySelector('[data-jp-pair-edit="opposites:b:0"]').click()`);
 assert(await evaluate(`document.querySelector('#mpField0').value==='大きい'&&document.querySelector('#mpField3').value==='小さい'`),'Edit did not prefill original');
 await fill(['大きい','おおきい','big · ठूलो (my note)','小さい','ちいさい','small · सानो','Literal <img src=x onerror=alert(1)>']);
 assert(await evaluate(`JP_MEANING_DATA.opposites[0][2]==='big · ठूलो'&&jpMeaningPairs('opposites')[0].pair[2].includes('my note')&&!document.querySelector('.jp-meaning-context img')`),'Built-in edit mutated source / injected markup');
 await evaluate(`document.querySelector('[data-jp-pair-edit="${custom}"]').click();document.querySelector('#mpField2').value='start study · revised';document.querySelector('#jpPairForm').requestSubmit()`);
 assert(await evaluate(`jpMeaningPairs('opposites').length===101&&DB.cards.length===1&&DB.cards[0].reps===5`),'Custom edit duplicated rows or changed flashcards');
 await evaluate(`document.querySelector('[data-jp-pair-add]').click();document.querySelector('#jpPairForm').requestSubmit()`);
 assert(await evaluate(`!!document.querySelector('#jpPairForm')&&Object.keys(DB.japanese.meaningPairs).length===2`),'Empty pair was accepted');await evaluate('closeModal()');
 await evaluate(`document.querySelector('[data-jp-meanings=home]').click();document.querySelector('[data-jp-meanings=synonyms]').click();document.querySelector('[data-jp-pair-add]').click()`);
 await fill(['学習','がくしゅう','learning · अध्ययन','勉強','べんきょう','study · पढाइ','Related activities; context determines interchangeability.']);
 await evaluate(`document.querySelector('[data-jp-pair-edit="synonyms:b:0"]').click();document.querySelector('#mpField2').value='My synonym meaning';document.querySelector('#jpPairForm').requestSubmit()`);
 assert(await evaluate(`jpMeaningPairs('synonyms').length===31&&Object.keys(DB.japanese.meaningPairs).length===4&&!document.querySelector('.jp-week-card[data-jp-meanings]')`),'Synonym add/edit or folder isolation failed');
 assert(await evaluate(`jpMeaningCsv(jpMeaningCards('opposites')).includes('start study · revised')&&jpMeaningCsv(jpMeaningCards('opposites')).includes('big · ठूलो (my note)')`),'CSV export ignores saved pair changes');
 for(const width of [1440,375,320]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:850,deviceScaleFactor:1,mobile:width<600});
  for(const theme of ['light','dark']){
   await evaluate(`document.documentElement.dataset.theme='${theme}';jpFuriganaOn=true;renderJapanese()`);
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'List overflow '+width+' '+theme);
   await evaluate(`document.querySelector('[data-jp-pair-add]').click()`);
   assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Form overflow '+width+' '+theme);await evaluate('closeModal()');
  }
 }
 await evaluate(`document.querySelector('[data-jp-meanings=home]').click();document.querySelector('[data-jp-meanings=opposites]').click();document.querySelector('[data-jp-meaning-add]').click()`);
 assert(await evaluate(`DB.decks.filter(d=>d.jpMeaningFolder==='opposites').length===1&&DB.cards.find(c=>c.id==='old-card').reps===5&&DB.cards.some(c=>c.front==='学習開始'&&c.back.includes('revised'))`),'Flashcards lost history / duplicated deck / omitted new pair');
 const saved=await evaluate('JSON.stringify(DB.japanese.meaningPairs)');
 await send('Page.reload',{ignoreCache:true});for(let i=0;i<60;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
 assert(await evaluate('JSON.stringify(DB.japanese.meaningPairs)')===saved,'Pair changes lost on refresh');
 await evaluate(`closeModal();window.__pairBackup=null;const oldURL=URL.createObjectURL;URL.createObjectURL=function(blob){window.__pairBackup=blob;return oldURL(blob);};document.querySelector('#exportBtn').click()`);
 const backup=await evaluate('window.__pairBackup.text()');
 assert(Object.keys(JSON.parse(backup).japanese.meaningPairs).length===4,'Backup omitted pair records');
 await evaluate(`DB.japanese.meaningPairs={};save();const f=new File([${JSON.stringify(backup)}],'pair-backup.json',{type:'application/json'}),dt=new DataTransfer();dt.items.add(f);document.querySelector('#importFile').files=dt.files;document.querySelector('#importFile').dispatchEvent(new Event('change',{bubbles:true}));`);
 for(let i=0;i<40;i++){if(await evaluate('Boolean(document.querySelector("#impMerge"))'))break;await sleep(60);}await evaluate(`document.querySelector('#impMerge').click()`);
 assert(await evaluate('JSON.stringify(DB.japanese.meaningPairs)')===saved,'Actual merge import omitted pair changes');
 await evaluate(`DB.japanese.meaningPairs={};confirmMerge(${backup});document.querySelector('#impReplace').click()`);
 assert(await evaluate('JSON.stringify(DB.japanese.meaningPairs)')===saved,'Replace import omitted pair changes');
 await evaluate(`(()=>{const incoming=JSON.parse(JSON.stringify(DB));DB.japanese.meaningPairs['opposites:b:0'].updatedAt='2099-02-01T00:00:00Z';DB.japanese.meaningPairs['opposites:b:0'].pair[2]='Newer local';incoming.japanese.meaningPairs['opposites:b:0'].updatedAt='2000-01-01T00:00:00Z';incoming.japanese.meaningPairs['opposites:b:0'].pair[2]='Older remote';incoming.japanese.meaningPairs['opposites:u:remote']={type:'opposites',baseIndex:null,pair:['前','まえ','front','後ろ','うしろ','behind','Fixture'],updatedAt:nowISO()};incoming.japanese.meaningPairs.bad={pair:[]};mergeIntoDB(incoming);})()`);
 assert(await evaluate(`DB.japanese.meaningPairs['opposites:b:0'].pair[2]==='Newer local'&&DB.japanese.meaningPairs['opposites:u:remote']&&!DB.japanese.meaningPairs.bad`),'Per-pair merge lost a newer edit or independent addition');
 await evaluate(`(()=>{const stamp='2099-03-01T00:00:00Z',a=JSON.parse(JSON.stringify(DB)),b=JSON.parse(JSON.stringify(DB));a.japanese.meaningPairs['synonyms:b:0'].pair[2]='AAA';b.japanese.meaningPairs['synonyms:b:0'].pair[2]='ZZZ';a.japanese.meaningPairs['synonyms:b:0'].updatedAt=stamp;b.japanese.meaningPairs['synonyms:b:0'].updatedAt=stamp;DB=applyDefaults(a);mergeIntoDB(b);const left=JSON.stringify(DB.japanese.meaningPairs);DB=applyDefaults(b);mergeIntoDB(a);if(JSON.stringify(DB.japanese.meaningPairs)!==left)throw Error('Equal-time merge did not converge');save();})()`);
 assert(await evaluate('JSON.stringify(JP_MEANING_DATA)')===original,'Original course pairs changed');
 assert(await evaluate(`DB.notes[0].body==='Keep personal notes'&&DB.japanese.notes['19.1']==='Keep source lesson'&&DB.japanese.quizScores['19.1']===75&&DB.course.done['1.0']&&DB.cards.find(c=>c.id==='old-card').reps===5`),'Other saved data changed');
 await evaluate(`switchView('japanese');jpPage.mode='meanings';JP_MEANING_STATE.tab='opposites';renderJapanese();document.querySelector('.jp-meaning-pair').scrollIntoView({block:'center'});closeModal()`);
 const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-meaning-pairs-edit-mobile.png'),Buffer.from(shot.data,'base64'));
 assert(errors.length===0,'JS errors: '+errors.join('; '));
 console.log('PASS: isolated folders, visible meanings, opposite/synonym add/edit/cancel/validation, immutable defaults, live CSV/flashcard additions, existing SRS history, refresh, actual merge/replace backups, conflict-safe per-pair merge,320px forms/themes; no JS errors.');
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{if(ws)ws.close();browser.kill();});
