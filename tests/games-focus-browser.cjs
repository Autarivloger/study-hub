// Fresh browser/profile only: native fullscreen, Focus controls and normal-layout restoration.
const fs=require('fs'),os=require('os'),path=require('path'),assert=require('assert/strict');
const {spawn}=require('child_process'),{pathToFileURL}=require('url');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-fullscreen-')),fixture=path.join(profile,'study-hub.html');
fs.writeFileSync(fixture,fs.readFileSync(path.resolve(__dirname,'../study-hub.html'),'utf8').replace('\nboot();\n','window.__courseTestEval=function(expression){return eval(expression);};\nboot();\n'));
const browser=spawn('C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',['--headless=new','--disable-gpu','--no-sandbox','--no-first-run','--remote-debugging-port=0','--user-data-dir='+profile,pathToFileURL(fixture).href],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));let ws;
async function main(){
 let port;for(let i=0;i<100;i++){const p=path.join(profile,'DevToolsActivePort');if(fs.existsSync(p)){port=Number(fs.readFileSync(p,'utf8').split('\n')[0]);break;}await sleep(100);}assert(port,'Chrome startup');
 const tabs=await(await fetch('http://127.0.0.1:'+port+'/json/list')).json();ws=new WebSocket(tabs.find(t=>t.type==='page').webSocketDebuggerUrl);await new Promise((r,j)=>{ws.onopen=r;ws.onerror=j;});
 let seq=0;const pending=new Map(),errors=[];
 ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.exception?.description||m.params.exceptionDetails.text);if(m.method==='Runtime.consoleAPICalled'&&m.params.type==='error')errors.push(m.params.args.map(a=>a.value||a.description).join(' '));if(m.id&&pending.has(m.id)){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}};
 const send=(method,params={})=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));});
 const evaluate=async (expression,gesture=false)=>{const r=await send('Runtime.evaluate',{expression:'window.__courseTestEval?window.__courseTestEval('+JSON.stringify(expression)+'):eval('+JSON.stringify(expression)+')',returnByValue:true,awaitPromise:true,userGesture:gesture});if(r.exceptionDetails)throw Error(r.exceptionDetails.exception?.description||r.exceptionDetails.text);return r.result.value;};
 async function wait(expression,label){for(let i=0;i<100;i++){if(await evaluate(expression))return;await sleep(50);}throw Error('Did not settle: '+label);}
 const click=selector=>evaluate('document.querySelector('+JSON.stringify(selector)+').click()',true);
 async function enter(name){await evaluate('switchView('+JSON.stringify(name)+')');await click('#view-'+name+' [data-game-focus]');await wait('document.fullscreenElement===document.documentElement&&!!document.querySelector(".gm-focus-screen")','native fullscreen '+name);await sleep(80);}
 async function exit(){await click('.gm-focus-toolbar [data-game-focus]');await wait('!document.fullscreenElement&&!document.body.classList.contains("games-focus")','exit fullscreen');await sleep(100);}
 const bounds='(()=>{const board=document.querySelector(".gm-focus-arena .ch-board,.gm-focus-arena .su-board,.gm-focus-arena .sk-board"),r=board.getBoundingClientRect(),a=document.querySelector(".gm-focus-arena").getBoundingClientRect(),t=document.querySelector(".gm-focus-toolbar").getBoundingClientRect();return {left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height,vw:innerWidth,vh:innerHeight,arena:{right:a.right,bottom:a.bottom},tools:{left:t.left,top:t.top,right:t.right,bottom:t.bottom},overflow:document.documentElement.scrollWidth>innerWidth+1};})()';
 await send('Runtime.enable');await send('Page.enable');await wait('Boolean(window.__studyHubBooted)','boot');
 await evaluate('closeModal();DB=applyDefaults({headNotes:{legacy:"Keep notes"},course:{partsDone:{"43.0.0":"2026-10-17"}},japanese:{done:{"1.1":"2026-10-17"}}});save();switchView("games")');
 for(const [width,height] of [[1366,768],[1024,768],[375,812],[320,568],[812,375]]){
  await send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:width<600});
  for(const name of ['chess','sudoku','sokoban']){
   await evaluate('switchView('+JSON.stringify(name)+');gamesScheduleFit()');await sleep(100);
   const before=await evaluate('JSON.stringify(DB)');
   const normal=await evaluate('(()=>{const r=document.querySelector("#view-'+name+' .ch-board,#view-'+name+' .su-board,#view-'+name+' .sk-board").getBoundingClientRect();return [r.left,r.top,r.width,r.height].map(Math.round);})()');
   await enter(name);const b=await evaluate(bounds);
   assert(!b.overflow&&b.left>=0&&b.top>=0&&b.right<=b.vw+1&&b.bottom<=b.vh+1,'Board fit '+name+' '+width+'x'+height+' '+JSON.stringify(b));
   assert(b.width>100&&b.height>100,'Board too small');
   assert(b.tools.left>=b.arena.right-1||b.tools.top>=b.arena.bottom-1,'Controls overlap board');
   assert(await evaluate('[...document.querySelectorAll(".gm-focus-actions>.btn,.gm-focus-toolbar .gm-header .btn")].every(b=>parseFloat(getComputedStyle(b).fontSize)===15&&b.getBoundingClientRect().height>=40)'),'15px readable controls '+name);
   for(const theme of ['light','dark']){
    await evaluate('document.documentElement.setAttribute("data-theme",'+JSON.stringify(theme)+')');
    if([1366,375,812].includes(width)){const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(path.join(os.tmpdir(),'studyhub-focus-'+name+'-'+width+'-'+theme+'.png'),Buffer.from(shot.data,'base64'));}
   }
   await exit();
   assert.equal(await evaluate('JSON.stringify(DB)'),before,'Focus changed saved data');
   assert(await evaluate('!document.querySelector(".gm-focus-screen")&&!!document.querySelector("#view-'+name+' >.gm-header")'),'Header/controls did not return');
   const restored=await evaluate('(()=>{const r=document.querySelector("#view-'+name+' .ch-board,#view-'+name+' .su-board,#view-'+name+' .sk-board").getBoundingClientRect();return [r.left,r.top,r.width,r.height].map(Math.round);})()');
   assert.deepEqual(restored,normal,'Normal layout changed '+name+' '+width+'x'+height);
  }
 }
 await send('Emulation.setDeviceMetricsOverride',{width:1366,height:768,deviceScaleFactor:1,mobile:false});
 await evaluate('switchView("chess");chessSetMode("local");chessStartGame({side:"w",level:"club"})');await enter('chess');
 await click('[data-ch-square="e2"]');assert(await evaluate('document.activeElement?.dataset.chSquare==="e2"'),'Chess selection focus lost during rerender');
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight'});assert(await evaluate('document.activeElement?.dataset.chSquare==="f2"'),'Chess keyboard navigation failed');
 await click('[data-ch-square="e4"]');await wait('chessState.game.history().length===1&&!!document.querySelector(".gm-focus-actions #chUndo")','chess move rerender');
 await click('#chNew');assert(await evaluate('overlay.classList.contains("open")'),'New-game confirmation missing');
 assert(await evaluate('(()=>{const r=document.getElementById("chCancelNew").getBoundingClientRect();return document.elementFromPoint(r.left+r.width/2,r.top+r.height/2).id==="chCancelNew";})()'),'Modal hidden behind fullscreen layout');await click('#chCancelNew');
 await click('#chUndo');await wait('chessState.game.history().length===0&&!!document.querySelector(".gm-focus-screen")','chess undo');
 await evaluate('chessState.game=chessNewRules("7k/P7/8/8/8/8/8/7K w - - 0 1");chessState.selected=null;renderChess()');await click('[data-ch-square="a7"]');await click('[data-ch-square="a8"]');
 assert(await evaluate('!!document.activeElement?.dataset.chPromote'),'Promotion keyboard focus missing');await click('[data-ch-promote="q"]');assert(await evaluate('chessState.game.get("a8").type==="q"'),'Fullscreen promotion failed');
 await evaluate('chessSetMode("puzzles")');await wait('!!document.querySelector(".gm-focus-actions #chHint")','puzzle controls');await click('#chHint');assert(await evaluate('chessState.hint===1'),'Chess hint failed');
 await evaluate('document.exitFullscreen()');await wait('!document.body.classList.contains("games-focus")&&!document.querySelector(".gm-focus-screen")','browser-initiated fullscreen exit');
 await enter('sudoku');await evaluate('(()=>{const g=DB.sudoku.game,i=g.givens.indexOf("0");window.__testCell=i;sudokuSelect(i);sudokuEnter(Number(g.solution[i]));})()');
 await wait('!!document.querySelector(".gm-focus-actions #suUndo")','Sudoku rerender');await click('#suUndo');assert(await evaluate('DB.sudoku.game.values[window.__testCell]===0'),'Sudoku undo');await click('#suHint');assert(await evaluate('DB.sudoku.game.hints>0'),'Sudoku hint');
 await send('Input.dispatchKeyEvent',{type:'keyDown',key:'Escape',code:'Escape'});await wait('!document.fullscreenElement&&!document.body.classList.contains("games-focus")','Escape');
 await evaluate('switchView("sokoban");sokoStart("sk-001");renderSokoban()');await enter('sokoban');
 await click('[data-sk-direction="R"]');await wait('DB.sokoban.game.moves.length===1&&!!document.querySelector(".gm-focus-actions #skUndo")','Sokoban move rerender');await click('#skUndo');assert(await evaluate('DB.sokoban.game.moves.length===0'),'Sokoban undo');await click('#skHint');await wait('!sokoState.busy','Sokoban hint');assert(await evaluate('DB.sokoban.game.assisted'),'Sokoban hint');
 await click('.gm-focus-toolbar [data-view="games"]');await wait('!document.fullscreenElement&&document.querySelector("#view-games").classList.contains("active")','Back to Games');
 await evaluate('window.__savedRequest=document.documentElement.requestFullscreen;document.documentElement.requestFullscreen=()=>Promise.reject(new DOMException("Test denial","NotAllowedError"));switchView("sudoku")');await click('#view-sudoku [data-game-focus]');await wait('document.body.classList.contains("games-focus")&&!document.querySelector(".gm-focus-notice").hidden','denied fullscreen fallback');assert(!await evaluate('Boolean(document.fullscreenElement)'));
 await click('.gm-focus-toolbar [data-game-focus]');await evaluate('document.documentElement.requestFullscreen=window.__savedRequest');
 await evaluate('switchView("chess")');await click('#view-chess [data-game-focus]');await click('.gm-focus-toolbar [data-game-focus]');await wait('!document.fullscreenElement&&!document.body.classList.contains("games-focus")','rapid exit');
 assert(await evaluate('DB.headNotes.legacy==="Keep notes"&&DB.course.partsDone["43.0.0"]&&DB.japanese.done["1.1"]'),'Legacy progress changed');
 assert.deepEqual(errors,[],'Browser errors');console.log('PASS: actual fullscreen for all3games/5viewports,15px side/bottom controls, exact normal-layout return, moves/undo/hints/promotion-ready keyboard focus, modal layering, native exit/Escape/Back, denied API fallback and saved data unchanged.');
}
main().catch(e=>{console.error(e);process.exitCode=1;}).finally(()=>{ws?.close();browser.kill();});
