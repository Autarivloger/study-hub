const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-sokoban-')),fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
  let port;for(let i=0;i<100;i++){const file=path.join(profile,'DevToolsActivePort');if(fs.existsSync(file)){port=Number(fs.readFileSync(file,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome startup');
  const pages=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json(),ws=new WebSocket(pages.find(p=>p.type==='page').webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});let seq=0;const pending=new Map(),errors=[];
  ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
  const run=fn=>evaluate('('+fn.toString()+')()');
  await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
  for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}assert(await evaluate('window.__studyHubBooted'));
  await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await run(function(){closeModal();DB=applyDefaults({headNotes:{legacy:'Keep writing'},course:{done:{'1.0':'2026-01-01'}},japanese:{done:{'1.1':'2026-01-01'}},chess:{game:{at:'2026-01-01',mode:'local',side:'w',level:'club',moves:['e2e4']}}});save();switchView('sudoku');switchView('games');document.querySelector('#gamesBody [data-view=sokoban]').click();});
  assert.equal(await evaluate('document.querySelectorAll(".sk-levels button").length'),40);
  await evaluate('document.querySelector("[data-sk-direction=R]").click()');
  assert(await evaluate('DB.sokoban.game.moves==="R"&&sokoState.position.pushes===1'),'D-pad push');
  const saved=await evaluate('JSON.stringify(DB.sokoban.game)');
  await send('Page.reload',{ignoreCache:true});for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  await evaluate('closeModal();switchView("sokoban")');assert.equal(await evaluate('JSON.stringify(DB.sokoban.game)'),saved);
  assert(await evaluate('sokoState.position.pushes===1&&sokoState.history.length===1&&DB.headNotes.legacy&&DB.course.done["1.0"]&&DB.sudoku.game&&DB.chess.game.moves[0]==="e2e4"'),'Reload preserved all data');
  await evaluate('document.getElementById("skUndo").click()');assert.equal(await evaluate('DB.sokoban.game.moves'),'', 'Undo after refresh');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight'});assert.equal(await evaluate('DB.sokoban.game.moves'),'R');
  await evaluate('document.getElementById("skRestart").click()');assert(await evaluate('!!document.getElementById("skKeep")'),'Restart confirmation');
  await evaluate('document.getElementById("skKeep").click()');assert.equal(await evaluate('DB.sokoban.game.moves'),'R');
  await evaluate('document.getElementById("skRestart").click();document.getElementById("skConfirm").click()');assert.equal(await evaluate('DB.sokoban.game.moves'),'');
  // Adjacent tile taps and swipe gestures each move only once.
  await run(function(){const b=sokoState.board,target=sokoNeighbour(b,sokoState.position.player,'R');document.querySelector('[data-sk-tile="'+target+'"]').click();});assert.equal(await evaluate('DB.sokoban.game.moves'),'R');
  await evaluate('sokoUndo();');await sleep(180);
  const rect=await evaluate('(()=>{const r=document.querySelector(".sk-board").getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height};})()');
  await send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:rect.x+rect.width*.35,y:rect.y+rect.height*.5}]});
  await send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:rect.x+rect.width*.65,y:rect.y+rect.height*.5}]});
  await send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});await sleep(100);assert.equal(await evaluate('DB.sokoban.game.moves'),'R','Swipe must move once');
  await evaluate('document.querySelector("[data-sk-direction=R]").click()');assert(await evaluate('sokoWon(sokoState.board,sokoState.position)&&DB.sokoban.completed["sk-001"].pushes===2&&!DB.sokoban.completed["sk-001"].assisted'),'Win/save');
  await evaluate('document.getElementById("skNext").click()');assert.equal(await evaluate('DB.sokoban.game.level'),'sk-002');
  await evaluate('document.getElementById("skHint").click()');for(let i=0;i<60;i++){if(await evaluate('!sokoState.busy'))break;await sleep(100);}assert(await evaluate('!!sokoState.hint&&DB.sokoban.game.assisted'),'Real offline hint worker');
  await run(function(){for(const d of sokoState.level.solution)sokoMove(d);if(!DB.sokoban.completed['sk-002'].assisted)throw Error('Assisted finish not labelled');});
  // All level layouts render, and each pack has a working solved route.
  await run(function(){for(const level of sokoLevels()){sokoStart(level.id);renderSokoban();if(document.querySelectorAll('[data-sk-tile]').length!==sokoState.board.width*sokoState.board.height)throw Error('Level layout '+level.id);}for(const i of [10,20,30,39]){sokoStart(sokoLevels()[i].id);renderSokoban();for(const d of sokoState.level.solution)sokoMove(d);if(!sokoWon(sokoState.board,sokoState.position))throw Error('Route failed '+i);}});
  await evaluate('sokoStart("sk-001");renderSokoban();sokoHint();switchView("games")');const route=await evaluate('DB.sokoban.game.moves');await sleep(1700);assert.equal(await evaluate('DB.sokoban.game.moves'),route,'Cancelled hint mutated game');
  await run(function(){const original=URL.createObjectURL;URL.createObjectURL=function(blob){window.__sokoBackup=blob;return original(blob);};document.getElementById('exportBtn').click();});
  const backup=await run(async function(){return await window.__sokoBackup.text();});assert(JSON.parse(backup).sokoban.completed['sk-001']);
  await run(function(){DB=applyDefaults({headNotes:{local:'Keep local'},sokoban:{completed:{'sk-010':{moves:50,pushes:10,assisted:false,at:'2026-01-01'}}}});save();});
  await evaluate('('+function(data){const dt=new DataTransfer();dt.items.add(new File([data],'sokoban-backup.json',{type:'application/json'}));const input=document.getElementById('importFile');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));}.toString()+')('+JSON.stringify(backup)+')');
  for(let i=0;i<50;i++){if(await evaluate('!!document.getElementById("impMerge")'))break;await sleep(100);}
  await evaluate('document.getElementById("impMerge").click()');assert(await evaluate('DB.sokoban.completed["sk-001"]&&DB.sokoban.completed["sk-010"]&&DB.headNotes.local&&DB.sudoku.game&&DB.chess.game'),'Real merge import');
  await evaluate('confirmMerge('+backup+');document.getElementById("impReplace").click()');assert(await evaluate('DB.sokoban.completed["sk-001"]&&!DB.sokoban.completed["sk-010"]&&DB.headNotes.legacy&&DB.sudoku.game&&DB.chess.game'),'Real replace import');
  await run(function(){const incoming=JSON.parse(JSON.stringify(DB));incoming.sokoban.game={level:'sk-001',moves:'R',at:'2099-01-01',assisted:false};incoming.sokoban.completed['sk-002']={moves:100,pushes:30,assisted:false,at:'2099-01-01'};mergeIntoDB(incoming);if(DB.sokoban.game.moves!=='R'||DB.sokoban.completed['sk-002'].assisted)throw Error('Sync merge');mergeIntoDB({headNotes:{oldBackup:'Works'}});if(!DB.sokoban.game)throw Error('Old backup removed progress');});
  for(const [width,height] of [[1440,900],[1366,768],[375,812],[320,568],[812,375]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
    for(const focus of [false,true]){
      await evaluate('closeModal();switchView("sokoban");document.body.classList.remove("games-focus");gamesSyncFocusButtons();sokoStart("sk-040");renderSokoban();'+(focus?'document.querySelector("#view-sokoban [data-game-focus]").click();':''));await sleep(180);
      // Landscape needs Focus to retain usable tiles; portrait/default must fit too.
      if(height<500&&!focus)continue;
      const bounds=await run(function(){const b=document.querySelector('.sk-board').getBoundingClientRect(),m=document.querySelector('.sk-main').getBoundingClientRect(),c=document.querySelector('.sk-controls').getBoundingClientRect();return {top:b.top,bottom:b.bottom,left:b.left,right:b.right,mainBottom:m.bottom,controlsBottom:c.bottom,overflow:document.documentElement.scrollWidth>innerWidth+1};});
      assert(!bounds.overflow&&bounds.top>=0&&bounds.bottom<=height+1&&bounds.mainBottom<=height+2&&bounds.controlsBottom<=height+2,'Board/controls fit '+width+'x'+height+' focus='+focus+' '+JSON.stringify(bounds));
      for(const theme of ['light','dark']){await evaluate('document.documentElement.setAttribute("data-theme",'+JSON.stringify(theme)+')');if(focus&&[1366,375,812].includes(width)){const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-sokoban-'+width+'-'+theme+'.png'),Buffer.from(shot.data,'base64'));}}
      await evaluate('switchView("games")');assert(await evaluate('!document.body.classList.contains("games-focus")'),'Focus leaked');
    }
  }
  await evaluate('switchView("sokoban");gamesFocus()');await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});assert(await evaluate('!document.body.classList.contains("games-focus")'),'Exit focus/Escape');
  await evaluate('switchView("course")');const unchanged=await evaluate('DB.sokoban.game.moves');await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight'});assert.equal(await evaluate('DB.sokoban.game.moves'),unchanged,'Game stole course keyboard');
  assert.deepEqual(errors,[],'Browser console errors');console.log('PASS: Sokoban Games entry, 40 layouts, pack solutions, push rules, keyboard/tap/swipe, undo/restart/next, actual hint worker/cancel, independent/assisted progress, refresh/backup/import/sync, mobile/desktop/focus/landscape themes; no JS errors.');ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
