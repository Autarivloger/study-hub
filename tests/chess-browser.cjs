const fs=require('fs'),os=require('os'),path=require('path');
const {spawn}=require('child_process');const {pathToFileURL}=require('url');
const assert=require('assert/strict');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-chess-'));
const fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'..','study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
  let port;for(let i=0;i<100;i++){const f=path.join(profile,'DevToolsActivePort');if(fs.existsSync(f)){port=Number(fs.readFileSync(f,'utf8').split('\n')[0]);break;}await sleep(100);}
  assert(port,'Chrome did not start');
  const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json(),page=tabs.find(t=>t.type==='page');
  const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
  let seq=0;const pending=new Map(),errors=[];
  ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',awaitPromise:true,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
  const run=fn=>evaluate('('+fn.toString()+')()');
  await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
  for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  assert(await evaluate('window.__studyHubBooted'),'App boot');
  // Disconnect the browser before Chess is opened: no CDN or runtime fetch is allowed.
  await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await run(function(){closeModal();DB=applyDefaults({headNotes:{legacy:'Keep notes'},course:{done:{'1.0':'2026-01-01'},notes:{'1.0':'Keep lesson'}},japanese:{done:{'1.1':'2026-01-01'}}});save();document.getElementById('chessHeadBtn').click();chessSetMode('local');});
  assert.equal(await evaluate('document.querySelectorAll("[data-ch-square]").length'),64);
  await run(function(){document.querySelector('[data-ch-square="e2"]').click();document.querySelector('[data-ch-square="e4"]').click();document.querySelector('[data-ch-square="e7"]').click();document.querySelector('[data-ch-square="e5"]').click();});
  assert(await evaluate('chessState.game.history().join(" ")==="e4 e5"&&DB.chess.game.moves.join(" ")==="e2e4 e7e5"'),'Local game/persistence');
  await send('Page.reload',{ignoreCache:true});
  for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  await evaluate('closeModal();switchView("chess")');
  assert(await evaluate('chessState.game.history().join(" ")==="e4 e5"'),'Resume saved game');
  await evaluate('document.getElementById("chUndo").click()');assert.equal(await evaluate('chessState.game.history().join(" ")'),'e4');
  // Promotion must offer all four choices and preserve the chosen underpromotion.
  await run(function(){chessState.game=chessNewRules('7k/P7/8/8/8/8/8/7K w - - 0 1');renderChess();chessSelect('a7');chessSelect('a8');});
  assert.equal(await evaluate('document.querySelectorAll("[data-ch-promote]").length'),4);
  await evaluate('document.querySelector("[data-ch-promote=n]").click()');assert.equal(await evaluate('chessState.game.get("a8").type'),'n');
  await evaluate('chessStartGame({side:"w",level:"club"});chessSetMode("bot");chessSelect("e2");chessSelect("e4")');
  for(let i=0;i<100;i++){if(await evaluate('!chessState.busy&&chessState.game.history().length===2'))break;await sleep(100);}
  assert(await evaluate('chessState.game.history().length===2&&!chessState.busy&&!chessState.message.includes("blocked")'),'Real offline bot worker');
  await evaluate('chessUndo()');assert.equal(await evaluate('chessState.game.history().length'),0);
  // A cancelled bot must never inject a stale move into another mode.
  await evaluate('chessPlay({from:"e2",to:"e4"});chessSetMode("puzzles")');
  const puzzleFen=await evaluate('chessState.game.fen()');await sleep(2200);assert.equal(await evaluate('chessState.game.fen()'),puzzleFen);
  assert.equal(await evaluate('chessLoadPuzzles().length'),10000);
  // Wrong legal answer leaves the board intact. Solve all three puzzle lengths through the UI.
  await run(function(){
    const p=chessLoadPuzzles().find(p=>p[4]===1);chessLoadPuzzle(p);const fen=chessState.game.fen();
    const wrong=chessState.game.moves({verbose:true}).find(m=>{chessState.game.move(m);const mate=chessState.game.isCheckmate();chessState.game.undo();return !mate;});
    if(wrong){if(chessPlay(wrong)!==false||chessState.game.fen()!==fen)throw Error('Wrong puzzle move changed board');}
  });
  for(const n of [1,2,3]){
    await evaluate('chessLoadPuzzle(chessLoadPuzzles().find(p=>p[4]==='+n+'))');
    for(let i=0;i<n;i++){
      await run(function(){const m=chessState.puzzle[2].split(' ')[chessState.step];chessSelect(m.slice(0,2));chessSelect(m.slice(2,4));if(m[4])document.querySelector('[data-ch-promote="'+m[4]+'"]').click();});
      if(i<n-1)await sleep(500);
    }
    assert(await evaluate('chessState.finished&&chessState.game.isCheckmate()&&!!DB.chess.solved[chessState.puzzle[0]].solvedAt'),'Solve mate-in-'+n);
  }
  await run(function(){const p=chessLoadPuzzles().find(p=>p[4]===1&&!DB.chess.solved[p[0]]);chessLoadPuzzle(p);chessHint();chessReveal();const m=p[2].split(' ')[0];chessPlay({from:m.slice(0,2),to:m.slice(2,4),...(m[4]?{promotion:m[4]}:{})});if(DB.chess.solved[p[0]].solvedAt)throw Error('Hint counted independent');if(!document.querySelector('.ch-solution'))throw Error('Solution absent');chessLoadPuzzle(p);chessPlay({from:m.slice(0,2),to:m.slice(2,4),...(m[4]?{promotion:m[4]}:{})});if(!DB.chess.solved[p[0]].solvedAt)throw Error('Independent retry missing');});
  await run(function(){
    chessState.mate='2';chessState.difficulty='easy';chessState.onlyUnsolved=true;
    const pool=chessPuzzlePool();if(!pool.length||pool.some(p=>p[4]!==2||p[3]>=1200||DB.chess.solved[p[0]]?.solvedAt))throw Error('Puzzle filters');
    const game=DB.chess.game;const legacy=JSON.stringify([DB.course.done,DB.headNotes,DB.japanese.done]);
    mergeIntoDB({chess:{game:{at:'2099-01-01T00:00:00Z',mode:'local',side:'w',level:'casual',moves:['d2d4']},solved:{zzzzz:{solvedAt:'2026-01-01'}}}});
    if(!DB.chess.solved.zzzzz?.solvedAt||DB.chess.game.moves[0]!=='d2d4')throw Error('Chess union merge');
    if(JSON.stringify([DB.course.done,DB.headNotes,DB.japanese.done])!==legacy)throw Error('Legacy data changed');
    mergeIntoDB({headNotes:{oldBackup:'Old backup works'}});if(!DB.chess.solved.zzzzz)throw Error('Old backup removed chess');
    const backup=JSON.stringify(DB);DB=applyDefaults(JSON.parse(backup));renderEverything();save();
    if(!DB.headNotes.legacy||!DB.japanese.done['1.1']||!DB.course.done['1.0'])throw Error('Backup lost existing activity');
  });
  // Exercise the real export/import UI with chess data, not just JSON serialization.
  await run(function(){const original=URL.createObjectURL;URL.createObjectURL=function(blob){window.__chessBackup=blob;return original(blob);};document.getElementById('exportBtn').click();});
  const backup=await run(async function(){return await window.__chessBackup.text();});
  assert(JSON.parse(backup).chess.solved.zzzzz,'Export omitted Chess');
  await run(function(){DB=applyDefaults({headNotes:{mergeLocal:'Keep local note'},chess:{solved:{yyyyy:{solvedAt:'2026-02-01'}}}});save();});
  await evaluate('('+function(data){const dt=new DataTransfer();dt.items.add(new File([data],'chess-backup.json',{type:'application/json'}));const input=document.getElementById('importFile');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));}.toString()+')('+JSON.stringify(backup)+')');
  for(let i=0;i<50;i++){if(await evaluate('!!document.querySelector("#impMerge")'))break;await sleep(100);}
  await evaluate('document.getElementById("impMerge").click()');
  assert(await evaluate('DB.chess.solved.zzzzz&&DB.chess.solved.yyyyy&&DB.headNotes.mergeLocal&&DB.chess.game.moves[0]==="d2d4"'),'Actual merge import lost Chess data');
  await evaluate('confirmMerge('+backup+');document.getElementById("impReplace").click()');
  assert(await evaluate('DB.chess.solved.zzzzz&&!DB.chess.solved.yyyyy&&DB.headNotes.legacy&&DB.chess.game.moves[0]==="d2d4"'),'Actual replace import lost Chess data');
  await evaluate('switchView("chess");document.getElementById("chFlip").click();document.querySelector("[data-ch-square=e2]").focus();');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight'});
  assert.equal(await evaluate('document.activeElement.dataset.chSquare'),'d2','Keyboard navigation follows flipped board');
  await send('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
  await evaluate('scrollTo(0,0)');
  assert(await evaluate('document.getElementById("chessHeadBtn").getBoundingClientRect().width>0&&document.documentElement.scrollWidth<=innerWidth+1'),'Desktop header or layout');
  const desktop=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-chess-desktop.png'),Buffer.from(desktop.data,'base64'));
  // All existing panes remain navigable and both themes fit a phone.
  await run(function(){for(const name of views){switchView(name);if(!document.getElementById('view-'+name).classList.contains('active'))throw Error(name);}});
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await run(function(){closeModal();switchView('chess');for(const theme of ['light','dark']){document.documentElement.setAttribute('data-theme',theme);for(const mode of ['local','bot','puzzles']){chessSetMode(mode);if(document.documentElement.scrollWidth>innerWidth+1)throw Error('Mobile overflow '+theme+' '+mode);const box=document.querySelector('.ch-board').getBoundingClientRect();if(Math.abs(box.width-box.height)>2||box.width<290)throw Error('Board layout');}}});
  const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-chess-mobile.png'),Buffer.from(shot.data,'base64'));
  assert.deepEqual(errors,[],'Browser console errors');
  console.log('PASS: offline file boot, header entry, two-player, save/refresh/undo, four promotions, real bot worker/cancellation, mate1/2/3, wrong moves, hints/solutions/retry, filters, merge/backup, all legacy views, 375px themes; no JS errors.');
  ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
