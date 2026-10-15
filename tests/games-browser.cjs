const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-games-')),fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function main(){
  let port;for(let i=0;i<100;i++){const file=path.join(profile,'DevToolsActivePort');if(fs.existsSync(file)){port=Number(fs.readFileSync(file,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome startup');
  const pages=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();const ws=new WebSocket(pages.find(p=>p.type==='page').pageWebSocketDebuggerUrl||pages.find(p=>p.type==='page').webSocketDebuggerUrl);
  await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});let seq=0;const pending=new Map(),errors=[];
  ws.onmessage=event=>{const m=JSON.parse(event.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
  const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
  const evaluate=async expression=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
  const run=fn=>evaluate('('+fn.toString()+')()');
  await send('Runtime.enable');await send('Page.enable');await send('Network.enable');
  for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}assert(await evaluate('window.__studyHubBooted'));
  await send('Network.emulateNetworkConditions',{offline:true,latency:0,downloadThroughput:0,uploadThroughput:0});
  await run(function(){closeModal();DB=applyDefaults({headNotes:{legacy:'Keep all notes'},course:{done:{'1.0':'2026-01-01'}},chess:{game:{at:'2026-01-01',mode:'local',side:'w',level:'club',moves:['e2e4']},solved:{abcde:{solvedAt:'2026-01-01'}}},japanese:{done:{'1.1':'2026-01-01'}}});save();document.getElementById('chessHeadBtn').click();});
  assert(await evaluate('document.getElementById("view-games").classList.contains("active")&&document.querySelectorAll(".gm-card").length===3'),'Games folder/header');
  await evaluate('document.querySelector("#gamesBody [data-view=sudoku]").click()');
  assert.equal(await evaluate('document.querySelectorAll("[data-su-cell]").length'),81);
  await run(function(){
    const g=DB.sudoku.game,i=g.givens.indexOf('0');window.__suIndex=i;sudokuSelect(i);document.getElementById('suNotes').click();document.querySelector('[data-su-number="'+g.solution[i]+'"]').click();
    if(!(g.notes[i]&(1<<(Number(g.solution[i])-1))))throw Error('Pencil note missing');
    document.getElementById('suUndo').click();if(g.notes[i])throw Error('Note undo failed');
    document.getElementById('suNotes').click();document.querySelector('[data-su-number="'+g.solution[i]+'"]').click();if(g.values[i]!==Number(g.solution[i]))throw Error('Number input failed');
    document.getElementById('suErase').click();if(g.values[i])throw Error('Erase failed');document.getElementById('suUndo').click();
    const fixed=g.givens.split('').findIndex(x=>x!=='0'),before=g.values[fixed];sudokuSelect(fixed);sudokuEnter(1);if(g.values[fixed]!==before)throw Error('Starting clue editable');
    sudokuSelect(i);document.getElementById('suAutoNotes').click();if(!g.notes.some(Boolean))throw Error('Auto notes missing');
  });
  const snapshot=await evaluate('JSON.stringify(DB.sudoku.game)');
  await send('Page.reload',{ignoreCache:true});for(let i=0;i<100;i++){if(await evaluate('Boolean(window.__studyHubBooted)'))break;await sleep(100);}
  await evaluate('closeModal();switchView("sudoku")');
  assert.equal(await evaluate('JSON.stringify(DB.sudoku.game)'),snapshot,'Saved puzzle/notes changed on reload');
  assert(await evaluate('DB.headNotes.legacy&&DB.course.done["1.0"]&&DB.japanese.done["1.1"]&&DB.chess.game.moves[0]==="e2e4"'),'Reload lost legacy data');
  await run(function(){
    const g=DB.sudoku.game,i=g.givens.indexOf('0');sudokuSelect(i);sudokuState.notesMode=false;sudokuEnter(Number(g.solution[i])%9+1);sudokuCheck();if(!document.querySelector('.su-wrong'))throw Error('Check did not mark wrong answer');
    sudokuHint();if(g.values[i]!==Number(g.solution[i])||!g.assisted||g.hints!==1)throw Error('Hint failed');
    g.values=g.solution.split('').map(Number);sudokuComplete();sudokuSave();if(!DB.sudoku.completed[g.id].assisted)throw Error('Assisted completion missing');
    sudokuStart('expert');sudokuEnsure();const g2=DB.sudoku.game;
    if(g2.givens.replace(/0/g,'').length!==25)throw Error('Expert clue count');g2.values=g2.solution.split('').map(Number);sudokuComplete();sudokuSave();renderSudoku();if(DB.sudoku.completed[g2.id].assisted)throw Error('Independent marked assisted');
  });
  // New-puzzle confirmation and keyboard input use the actual interface.
  await run(function(){sudokuStart('medium');renderSudoku();const g=DB.sudoku.game,i=g.givens.indexOf('0');sudokuSelect(i);sudokuEnter(Number(g.solution[i]));window.__beforeNew=g.id;document.getElementById('suNew').click();});
  assert(await evaluate('!!document.getElementById("suKeep")'),'Unfinished puzzle confirmation');
  await evaluate('document.getElementById("suKeep").click()');assert.equal(await evaluate('DB.sudoku.game.id===window.__beforeNew'),true);
  await evaluate('sudokuSelect(DB.sudoku.game.givens.indexOf("0"));');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'n',code:'KeyN'});assert(await evaluate('sudokuState.notesMode'),'Keyboard notes toggle');
  await send('Input.dispatchKeyEvent',{type:'keyDown',key:'4',code:'Digit4'});assert(await evaluate('!!(DB.sudoku.game.notes[sudokuState.selected]&8)'),'Keyboard digit entry');
  await run(function(){const original=URL.createObjectURL;URL.createObjectURL=function(blob){window.__gamesBackup=blob;return original(blob);};document.getElementById('exportBtn').click();});
  const backup=await run(async function(){return await window.__gamesBackup.text();});assert(JSON.parse(backup).sudoku.game,'Export omitted Sudoku');
  await run(function(){DB=applyDefaults({headNotes:{local:'Keep local'}});save();});
  await evaluate('('+function(data){const dt=new DataTransfer();dt.items.add(new File([data],'games-backup.json',{type:'application/json'}));const input=document.getElementById('importFile');input.files=dt.files;input.dispatchEvent(new Event('change',{bubbles:true}));}.toString()+')('+JSON.stringify(backup)+')');
  for(let i=0;i<50;i++){if(await evaluate('!!document.getElementById("impMerge")'))break;await sleep(100);}
  await evaluate('document.getElementById("impMerge").click()');assert(await evaluate('DB.sudoku.game&&Object.keys(DB.sudoku.completed).length===2&&DB.headNotes.local&&DB.chess.solved.abcde'),'Merge import lost game progress');
  await evaluate('confirmMerge('+backup+');document.getElementById("impReplace").click()');assert(await evaluate('DB.sudoku.game&&Object.keys(DB.sudoku.completed).length===2&&DB.headNotes.legacy&&DB.chess.solved.abcde'),'Replace import lost game progress');
  // Conflict merge preserves both completions and prefers the newer active game.
  await run(function(){const incoming=JSON.parse(JSON.stringify(DB));incoming.sudoku.game.at='2099-01-01';incoming.sudoku.game.notes[0]=3;const id=Object.keys(incoming.sudoku.completed)[0];DB.sudoku.completed[id].assisted=true;incoming.sudoku.completed[id].assisted=false;mergeIntoDB(incoming);if(DB.sudoku.game.notes[0]!==3||DB.sudoku.completed[id].assisted)throw Error('Sudoku sync merge');mergeIntoDB({headNotes:{oldBackup:'Still works'}});if(!DB.sudoku.game||!DB.chess.game)throw Error('Old backup removed games');});
  for(const [width,height] of [[1440,900],[1366,768],[375,812],[320,568],[812,375]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
    for(const mode of ['chess','sudoku']){
      await evaluate('closeModal();switchView('+JSON.stringify(mode)+');'+(mode==='chess'?'chessSetMode("local");':''));
      if(height<500)await evaluate('gamesFocus()');await sleep(150);
      const bounds=await run(function(){const b=document.querySelector('.view.active .ch-board,.view.active .su-board').getBoundingClientRect(),el=document.querySelector('.view.active .ch-main,.view.active .su-main'),m=el.getBoundingClientRect(),w=document.querySelector('.view.active .ch-wrap,.view.active .su-wrap');return {top:b.top,bottom:b.bottom,width:b.width,height:b.height,mainBottom:m.bottom,overflow:document.documentElement.scrollWidth>innerWidth+1,fit:w.style.getPropertyValue('--game-board-size'),mainMax:getComputedStyle(el).maxWidth,innerHeight,scrollY,visual:window.visualViewport.height};});
      assert(!bounds.overflow,'Horizontal overflow '+mode+' '+width+' '+height);
      assert(Math.abs(bounds.width-bounds.height)<2,'Board not square');
      assert(bounds.top>=0&&bounds.bottom<=height+1,'Board outside viewport '+mode+' '+width+' '+height+' '+JSON.stringify(bounds));
      assert(bounds.mainBottom<=height+3,'Board controls outside viewport '+mode+' '+width+' '+height+' '+JSON.stringify(bounds));
      for(const theme of ['light','dark']){await evaluate('document.documentElement.setAttribute("data-theme",'+JSON.stringify(theme)+')');if((width===1366||width===375)&&mode==='sudoku'){const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-sudoku-'+width+'-'+theme+'.png'),Buffer.from(shot.data,'base64'));}}
      await evaluate('switchView("games")');assert(await evaluate('!document.body.classList.contains("games-focus")'),'Focus leaked to Games home');
    }
  }
  await send('Emulation.setDeviceMetricsOverride',{width:375,height:812,deviceScaleFactor:1,mobile:true});
  await evaluate('switchView("chess");chessSetMode("puzzles");chessHint()');await sleep(150);
  assert(await evaluate('document.querySelector(".ch-board").getBoundingClientRect().bottom<=innerHeight&&document.querySelector(".ch-main").getBoundingClientRect().bottom<=innerHeight'),'Puzzle mode with hint must fit');
  for(const [width,height] of [[1366,768],[375,812]]){
    await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});await evaluate('switchView("games")');await sleep(80);
    assert(await evaluate('document.documentElement.scrollWidth<=innerWidth+1'),'Games home overflow');const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-games-'+width+'.png'),Buffer.from(shot.data,'base64'));
  }
  await evaluate('switchView("chess");gamesFocus()');await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});assert(await evaluate('!document.body.classList.contains("games-focus")'),'Escape did not exit focus');
  await run(function(){for(const name of views){switchView(name);if(!document.getElementById('view-'+name).classList.contains('active'))throw Error('Navigation '+name);}});
  assert.deepEqual(errors,[],'Browser console errors');
  console.log('PASS: Games hub; offline Sudoku input/notes/erase/undo/auto-notes/hints/check/completion, refresh preserving legacy progress, keyboard, actual backup merge/replace and sync; Chess/Sudoku boards and controls fit 5 viewport sizes, focus/Escape, themes and all navigation; no JS errors.');ws.close();
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>browser.kill());
