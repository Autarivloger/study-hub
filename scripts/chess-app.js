/* Study Hub Chess. Kept inside the existing application closure on embedding. */
function chessDefaults(value){
  const d=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  if(!d.solved||typeof d.solved!=='object'||Array.isArray(d.solved))d.solved={};
  if(!d.game||typeof d.game!=='object'||!Array.isArray(d.game.moves))d.game=null;
  return d;
}
function chessMerge(incoming){
  const theirs=chessDefaults(incoming),mine=DB.chess;
  Object.keys(theirs.solved).forEach(id=>{
    if(!/^[A-Za-z0-9]{5}$/.test(id))return;
    const a=mine.solved[id]||{},b=theirs.solved[id]||{};
    mine.solved[id]={solvedAt:a.solvedAt||b.solvedAt||null,assistedAt:a.assistedAt||b.assistedAt||null};
  });
  if(theirs.game&&(!mine.game||String(theirs.game.at||'')>String(mine.game.at||'')))mine.game=theirs.game;
}
const chessState={ready:false,game:null,mode:'bot',side:'w',level:'club',flipped:false,selected:null,promotion:null,worker:null,job:0,timer:null,busy:false,message:'',tone:'',puzzles:null,puzzle:null,step:0,assisted:false,finished:false,mate:'all',difficulty:'all',onlyUnsolved:true,hint:0,solution:false,sourceRecord:null};
const CHESS_PIECES={k:'♚',q:'♛',r:'♜',b:'♝',n:'♞',p:'♟'};
const CHESS_NAMES={k:'king',q:'queen',r:'rook',b:'bishop',n:'knight',p:'pawn'};
function chessNewRules(fen){return new window.StudyHubChessRules.Chess(fen);}
function chessMoveUci(game,uci){return game.move({from:uci.slice(0,2),to:uci.slice(2,4),...(uci[4]?{promotion:uci[4]}:{})});}
function chessUci(move){return move.from+move.to+(move.promotion||'');}
function chessStop(){
  const s=chessState;s.job++;
  if(s.worker){s.worker.terminate();s.worker=null;}
  clearTimeout(s.timer);s.timer=null;s.busy=false;s.promotion=null;
}
function chessRestore(){
  chessStop();const s=chessState,record=DB.chess.game;
  s.game=chessNewRules();s.mode=record&&record.mode==='local'?'local':'bot';
  s.side=record&&record.side==='b'?'b':'w';s.level=record&&['casual','club','challenge'].includes(record.level)?record.level:'club';
  s.message='Select a piece, then select a highlighted square.';s.tone='';
  if(record){
    try{for(const move of record.moves.slice(0,2000))chessMoveUci(s.game,move);}
    catch(error){s.game=chessNewRules();s.message='The saved game could not be restored. A fresh board is ready; puzzle progress is safe.';}
  }
  s.selected=null;s.puzzle=null;s.flipped=s.mode==='bot'&&s.side==='b';s.sourceRecord=record;s.ready=true;
}
function chessEnsure(){
  if(!chessState.ready||(chessState.mode!=='puzzles'&&chessState.sourceRecord!==DB.chess.game))chessRestore();
}
function chessSaveGame(){
  const s=chessState;if(s.mode==='puzzles')return;
  DB.chess.game={at:nowISO(),mode:s.mode,side:s.side,level:s.level,moves:s.game.history({verbose:true}).map(chessUci)};
  s.sourceRecord=DB.chess.game;save();
}
function chessStatus(){
  const s=chessState,g=s.game;
  if(s.mode==='puzzles'&&s.finished)return s.assisted?'Checkmate — reviewed with help':'Checkmate — puzzle solved!';
  if(g.isCheckmate())return (g.turn()==='w'?'Black':'White')+' wins by checkmate';
  if(g.isStalemate())return 'Draw — stalemate';
  if(g.isThreefoldRepetition())return 'Draw — threefold repetition';
  if(g.isInsufficientMaterial())return 'Draw — insufficient material';
  if(g.isDrawByFiftyMoves())return 'Draw — 50-move rule';
  if(s.busy)return s.mode==='puzzles'?'Opponent is replying…':'Computer is thinking…';
  return (g.turn()==='w'?'White':'Black')+' to move'+(g.isCheck()?' — check!':'');
}
function chessOptions(values,current){return values.map(([value,label])=>'<option value="'+value+'"'+(String(current)===String(value)?' selected':'')+'>'+label+'</option>').join('');}
function chessCount(){
  let solved=0,assisted=0;
  if(chessState.puzzles)for(const p of chessState.puzzles){const x=DB.chess.solved[p[0]];if(x&&x.solvedAt)solved++;else if(x&&x.assistedAt)assisted++;}
  return {solved,assisted};
}
function chessBoardHTML(){
  const s=chessState,g=s.game,files=s.flipped?'hgfedcba':'abcdefgh',ranks=s.flipped?'12345678':'87654321';
  const legal=s.selected?g.moves({square:s.selected,verbose:true}):[];
  const targets=new Set(legal.map(m=>m.to)),history=g.history({verbose:true}),last=history[history.length-1];
  const checking=g.isCheck()?g.board().flat().find(p=>p&&p.type==='k'&&p.color===g.turn()):null;
  const hintMove=s.mode==='puzzles'&&s.hint&&s.puzzle?s.puzzle[2].split(' ')[s.step]:null;
  let html='';
  for(let r=0;r<8;r++)for(let f=0;f<8;f++){
    const sq=files[f]+ranks[r],piece=g.get(sq);
    const dark=(files.charCodeAt(f)-97+Number(ranks[r]))%2===0;
    const isTarget=targets.has(sq);
    const classes=['ch-square',dark?'ch-dark':'',last&&(last.from===sq||last.to===sq)?'ch-last':'',s.selected===sq?'ch-selected':'',isTarget?'ch-legal':'',checking&&checking.square===sq?'ch-check':'',hintMove&&(sq===hintMove.slice(0,2)||(s.hint>1&&sq===hintMove.slice(2,4)))?'ch-hint':''].filter(Boolean).join(' ');
    const label=sq+(piece?', '+(piece.color==='w'?'White ':'Black ')+CHESS_NAMES[piece.type]:', empty')+(isTarget?', legal destination':'');
    html+='<button type="button" class="'+classes+'" data-ch-square="'+sq+'" tabindex="'+((s.selected||'e2')===sq?'0':'-1')+'" aria-label="'+label+'" aria-pressed="'+(s.selected===sq)+'">'+(piece?'<span aria-hidden="true" class="ch-piece '+(piece.color==='w'?'ch-white':'')+'">'+CHESS_PIECES[piece.type]+'</span>':'')+(f===0?'<span class="ch-coord ch-rank" aria-hidden="true">'+ranks[r]+'</span>':'')+(r===7?'<span class="ch-coord ch-file" aria-hidden="true">'+files[f]+'</span>':'')+'</button>';
  }
  return html;
}
function renderChess(){
  if(typeof gamesRestoreFocusLayout==='function')gamesRestoreFocusLayout();
  chessEnsure();const s=chessState,puzzleMode=s.mode==='puzzles',counts=chessCount();
  const body=document.getElementById('chessBody');
  const tabs=[['local','Two players'],['bot','Play computer'],['puzzles','Checkmate puzzles']].map(([mode,label])=>'<button class="btn secondary" type="button" data-ch-mode="'+mode+'" aria-pressed="'+(mode===s.mode)+'">'+label+'</button>').join('');
  const filters=puzzleMode?'<div class="ch-card"><h2>Find the quickest checkmate</h2><div class="ch-controls"><label>Mate in<select id="chMate">'+chessOptions([['all','1, 2 or 3 moves'],['1','1 move · 4,000 puzzles'],['2','2 moves · 4,000 puzzles'],['3','3 moves · 2,000 puzzles']],s.mate)+'</select></label><label>Difficulty<select id="chDifficulty">'+chessOptions([['all','All ratings'],['easy','Under 1200'],['medium','1200–1799'],['hard','1800+']],s.difficulty)+'</select></label></div><p class="ch-meta"><label><input id="chUnsolved" type="checkbox"'+(s.onlyUnsolved?' checked':'')+'> Unsolved puzzles only</label></p><div class="ch-actions"><button class="btn" id="chNextPuzzle" type="button">Next random puzzle</button></div><progress class="ch-progress" max="10000" value="'+counts.solved+'" aria-label="Puzzles solved independently"></progress><div class="ch-meta">'+counts.solved.toLocaleString()+' / 10,000 solved independently · '+counts.assisted.toLocaleString()+' reviewed with help</div></div>':'<div class="ch-card"><h2>'+(s.mode==='local'?'Two players · same device':'Your computer opponent')+'</h2>'+(s.mode==='bot'?'<div class="ch-controls"><label>You play<select id="chSide">'+chessOptions([['w','White · first move'],['b','Black · second move']],s.side)+'</select></label><label>Bot level<select id="chLevel">'+chessOptions([['casual','Casual'],['club','Medium'],['challenge','Challenge']],s.level)+'</select></label></div><p class="ch-meta">An offline practice bot. Higher levels think longer; these are not Elo ratings. Side and level apply when you start a new game.</p>':'<p class="ch-meta">Take turns on this screen. White moves first. No sign-in needed.</p>')+'<div class="ch-actions"><button class="btn" id="chNew" type="button">New game</button><button class="btn secondary" id="chUndo" type="button"'+(!s.game.history().length?' disabled':'')+'>Undo turn</button></div><p class="ch-meta">Your game saves after each move. Come back to continue.</p></div>';
  let puzzleInfo='';
  if(puzzleMode&&s.puzzle){
    const p=s.puzzle,record=DB.chess.solved[p[0]]||{};
    puzzleInfo='<div class="ch-card"><h2>Mate in '+p[4]+' <span class="ch-badge">'+(s.solver==='w'?'White':'Black')+' to play</span></h2><p class="ch-meta">Puzzle '+p[0]+' · rating '+p[3]+' · '+(record.solvedAt?'Previously solved':record.assistedAt?'Previously reviewed':'New challenge')+'</p><p class="ch-meta">Mate in '+p[4]+' means checkmate within '+p[4]+' of <strong>your</strong> moves. The opponent replies automatically.</p><div class="ch-actions"><button class="btn secondary" id="chHint" type="button"'+(s.finished?' disabled':'')+'>Hint</button><button class="btn secondary" id="chSolution" type="button">Show solution</button><button class="btn secondary" id="chRetry" type="button">Try again</button></div>'+(s.solution?'<div class="ch-solution">'+chessSolutionText()+'</div><p class="ch-meta">This attempt counts as reviewed with help. Solve it again without hints to earn independent completion.</p>':'')+'<p class="ch-meta"><a href="https://lichess.org/training/'+p[0]+'" target="_blank" rel="noopener noreferrer">Original puzzle ↗</a></p></div>';
  }
  const history=s.game.history({verbose:true});let historyHTML='';
  for(let i=0;i<history.length;i++){
    const m=history[i],number=m.before.split(' ')[5];
    if(i===0||m.color==='w')historyHTML+='<li value="'+number+'">'+(m.color==='b'?'<span>…</span>':'');
    historyHTML+='<span>'+escapeHtml(m.san)+'</span>';
    if(m.color==='b'||i===history.length-1)historyHTML+='</li>';
  }
  body.innerHTML='<div class="ch-wrap"><p class="ch-intro">A quiet place to play, think and spot the finish. All three modes work offline.</p><div class="ch-tabs" aria-label="Chess mode">'+tabs+'</div><div class="ch-layout"><div class="ch-main"><div class="ch-player"><span>'+(s.flipped?'White':'Black')+'</span><span>'+(puzzleMode?'Checkmate training':s.mode==='local'?'Same-device match':'Offline match')+'</span></div><div class="ch-board" role="group" aria-label="Chessboard. Select a piece and its destination. Arrow keys move focus.">'+chessBoardHTML()+'</div><div class="ch-player"><span>'+(s.flipped?'Black':'White')+'</span><button class="btn secondary btn-sm" type="button" id="chFlip">Flip board</button></div><div id="chPromotion"></div><div class="ch-card" role="status" aria-live="polite"><p class="ch-turn">'+chessStatus()+'</p><p class="ch-message '+(s.tone==='good'?'ch-good':s.tone==='warn'?'ch-warn':'')+'">'+escapeHtml(s.message)+'</p></div></div><aside class="ch-aside">'+filters+puzzleInfo+'<div class="ch-card"><h2>Moves</h2>'+(historyHTML?'<ol class="ch-history">'+historyHTML+'</ol>':'<p class="ch-meta">Your moves will appear here.</p>')+(!puzzleMode?'<div class="ch-actions"><button class="btn secondary" id="chPgn" type="button">Download game (PGN)</button></div>':'')+'</div><details class="ch-card ch-help"><summary>How to play &amp; puzzle tips</summary><p>Tap or click a piece, then a marked destination. On a keyboard, use arrows to move between squares and Enter to select. Escape clears your selection.</p><p>Castling: select the king, then its destination two squares across. En passant, promotion, check and draws follow standard chess rules. When a pawn reaches the last rank, choose queen, rook, bishop or knight.</p><p>For puzzles, look for checks first. Checkmate means the king is attacked and has no legal escape, capture or block. A wrong move stays on the same position so you can try again. Hint and Show solution mark an assisted review.</p><p>Study Hub uses its own board and practice bot, with <a href="https://github.com/jhlywa/chess.js" target="_blank" rel="noopener noreferrer">chess.js 1.4.0 (BSD-2-Clause)</a> for rules and 10,000 <a href="https://database.lichess.org/#puzzles" target="_blank" rel="noopener noreferrer">Lichess CC0 puzzles</a>. No Lichess branding or server code is included. Game and puzzle progress are included in your existing backup and sync.</p></details></aside></div></div>';
  body.querySelectorAll('[data-ch-mode]').forEach(b=>b.onclick=()=>chessSetMode(b.dataset.chMode));
  body.querySelectorAll('[data-ch-square]').forEach(b=>{b.onclick=()=>chessSelect(b.dataset.chSquare);b.onkeydown=chessBoardKey;});
  body.querySelector('#chFlip').onclick=()=>{s.flipped=!s.flipped;renderChess();};
  if(puzzleMode){
    body.querySelector('#chNextPuzzle').onclick=()=>chessNextPuzzle();
    body.querySelector('#chMate').onchange=e=>{s.mate=e.target.value;chessNextPuzzle();};
    body.querySelector('#chDifficulty').onchange=e=>{s.difficulty=e.target.value;chessNextPuzzle();};
    body.querySelector('#chUnsolved').onchange=e=>{s.onlyUnsolved=e.target.checked;chessNextPuzzle();};
    if(s.puzzle){body.querySelector('#chHint').onclick=chessHint;body.querySelector('#chSolution').onclick=chessReveal;body.querySelector('#chRetry').onclick=()=>chessLoadPuzzle(s.puzzle);}
  }else{
    body.querySelector('#chNew').onclick=()=>{
      const side=body.querySelector('#chSide'),level=body.querySelector('#chLevel');
      const settings={side:side?side.value:s.side,level:level?level.value:s.level};
      const start=()=>chessStartGame(settings);
      if(s.game.history().length&&!s.game.isGameOver()){
        openModal('<h2>Start a new game?</h2><p>This replaces the current saved match. Download its PGN first if you want to keep it.</p><div class="modal-actions"><button class="btn secondary" id="chCancelNew" type="button">Keep playing</button><button class="btn" id="chConfirmNew" type="button">Start new game</button></div>');
        document.getElementById('chCancelNew').onclick=closeModal;document.getElementById('chConfirmNew').onclick=()=>{closeModal();start();};
      }else start();
    };
    body.querySelector('#chUndo').onclick=chessUndo;
    body.querySelector('#chPgn').onclick=chessDownload;
  }
  if(typeof gamesPrepareFocusLayout==='function')gamesPrepareFocusLayout();
  if(s.promotion)chessRenderPromotion();
  const list=body.querySelector('.ch-history');if(list)list.scrollTop=list.scrollHeight;
  if(!puzzleMode)chessScheduleBot();
  if(typeof gamesScheduleFit==='function')gamesScheduleFit();
}
function chessBoardKey(event){
  const buttons=[...document.querySelectorAll('[data-ch-square]')],idx=buttons.indexOf(event.currentTarget);
  if(event.key==='Escape'){chessState.selected=null;chessState.promotion=null;renderChess();return;}
  const step={ArrowLeft:-1,ArrowRight:1,ArrowUp:-8,ArrowDown:8}[event.key];
  if(step===undefined)return;
  event.preventDefault();const next=idx+step;
  if(next<0||next>=64||(Math.abs(step)===1&&Math.floor(next/8)!==Math.floor(idx/8)))return;
  buttons.forEach(b=>b.tabIndex=-1);buttons[next].tabIndex=0;buttons[next].focus();
}
function chessSetMode(mode){
  const s=chessState;if(mode===s.mode)return;
  chessStop();s.selected=null;s.message='';s.tone='';
  if(mode==='puzzles'){s.mode=mode;chessNextPuzzle();return;}
  // A puzzle never overwrites a saved normal game.
  if(s.mode==='puzzles')chessRestore();
  s.mode=mode;s.puzzle=null;s.flipped=mode==='bot'&&s.side==='b';
  chessSaveGame();renderChess();
}
function chessStartGame(settings){
  chessStop();const s=chessState;s.side=settings.side;s.level=settings.level;
  s.game=chessNewRules();s.selected=null;s.flipped=s.mode==='bot'&&s.side==='b';s.message='Select a piece, then a highlighted square.';s.tone='';
  chessSaveGame();renderChess();
}
function chessSelect(square){
  const s=chessState,g=s.game;if(s.busy||s.promotion||g.isGameOver()||(s.mode==='puzzles'&&s.finished))return;
  if(s.mode==='bot'&&g.turn()!==s.side)return;
  const piece=g.get(square);
  if(s.selected){
    const moves=g.moves({square:s.selected,verbose:true}).filter(m=>m.to===square);
    if(moves.length){
      if(moves.some(m=>m.promotion)){s.promotion={from:s.selected,to:square};chessRenderPromotion();return;}
      chessPlay({from:s.selected,to:square});return;
    }
    if(s.selected===square){s.selected=null;renderChess();return;}
  }
  if(piece&&piece.color===g.turn()){s.selected=square;s.message=CHESS_NAMES[piece.type]+' on '+square+': choose a highlighted square.';s.tone='';}
  else{s.selected=null;s.message='Choose a '+(g.turn()==='w'?'White':'Black')+' piece first.';s.tone='';}
  renderChess();
  const selected=document.querySelector('[data-ch-square="'+square+'"]');if(selected)selected.focus({preventScroll:true});
}
function chessRenderPromotion(){
  const holder=document.getElementById('chPromotion');if(!holder||!chessState.promotion)return;
  holder.innerHTML='<div class="ch-promo" role="group" aria-label="Choose promotion"><strong>Promote your pawn</strong>'+['q','r','b','n'].map(p=>'<button class="btn secondary" type="button" data-ch-promote="'+p+'">'+CHESS_NAMES[p]+'</button>').join('')+'<button class="btn secondary" id="chCancelPromo" type="button">Cancel</button></div>';
  holder.querySelectorAll('[data-ch-promote]').forEach(b=>b.onclick=()=>{const m=chessState.promotion;chessState.promotion=null;chessPlay({...m,promotion:b.dataset.chPromote});});
  holder.querySelector('#chCancelPromo').onclick=()=>{chessState.promotion=null;renderChess();};
  holder.querySelector('button').focus({preventScroll:true});
  if(document.body.classList.contains('games-focus'))holder.scrollIntoView({block:'nearest',inline:'nearest'});
}
function chessPlay(move){
  const s=chessState,g=s.game;let played;
  try{played=g.move(move);}catch(error){s.message='That move is not legal. Your king must stay safe.';s.tone='warn';renderChess();return false;}
  s.selected=null;s.promotion=null;s.tone='';
  if(s.mode==='puzzles'){
    const expected=s.puzzle[2].split(' ')[s.step];
    if(chessUci(played)!==expected&&!g.isCheckmate()){
      g.undo();s.message='That is not the puzzle’s mating line. Look for a forcing check and try again.';s.tone='warn';renderChess();return false;
    }
    s.step++;s.hint=0;
    if(g.isCheckmate()){chessCompletePuzzle();return true;}
    s.message='Good move: '+played.san+'. Now look at the opponent’s reply.';s.tone='good';s.busy=true;
    const job=++s.job;renderChess();
    s.timer=setTimeout(()=>{
      if(job!==s.job||s.mode!=='puzzles')return;
      chessPuzzleReply();
    },420);
  }else{
    s.message=played.san+(g.isCheckmate()?' — checkmate!':g.isCheck()?' — check.':'');
    chessSaveGame();renderChess();
  }
  return true;
}
function chessPuzzleReply(){
  const s=chessState,moves=s.puzzle[2].split(' '),reply=moves[s.step];
  s.busy=false;s.timer=null;
  if(!reply){s.message='The training line ended. Choose another puzzle.';s.tone='warn';renderChess();return;}
  try{const move=chessMoveUci(s.game,reply);s.step++;s.message='Opponent played '+move.san+'. Find your next move.';s.tone='';}
  catch(error){s.message='This puzzle could not continue. Choose the next puzzle.';s.tone='warn';}
  renderChess();
}
function chessCompletePuzzle(){
  const s=chessState;s.finished=true;s.busy=false;
  const record=DB.chess.solved[s.puzzle[0]]||{};
  if(s.assisted)record.assistedAt=record.assistedAt||nowISO();else record.solvedAt=record.solvedAt||nowISO();
  DB.chess.solved[s.puzzle[0]]=record;save();
  s.message=s.assisted?'Nice finish. Try it again without help, or choose another puzzle.':'You found the finish! Choose Next random puzzle for another challenge.';s.tone='good';renderChess();
}
function chessScheduleBot(){
  const s=chessState;
  if(s.mode!=='bot'||s.game.turn()===s.side||s.game.isGameOver()||s.busy||!document.getElementById('view-chess').classList.contains('active'))return;
  const fen=s.game.fen(),job=++s.job;s.busy=true;
  const fail=()=>{
    if(job!==s.job)return;
    if(s.worker)s.worker.terminate();s.worker=null;s.busy=false;clearTimeout(s.timer);s.timer=null;
    // Honest, legal fallback for browsers that disable Workers (not another long main-thread search).
    const moves=s.game.moves({verbose:true});
    if(moves.length){const mate=moves.find(m=>m.san.endsWith('#'));const move=mate||moves[Math.floor(Math.random()*moves.length)];s.game.move(move);chessSaveGame();}
    s.message='This browser blocked the thinking engine. The computer used a simple legal move for this turn.';s.tone='';renderChess();
  };
  try{
    const code='var window=self;\n'+document.getElementById('chessRules').textContent+'\n('+chessBotWorker.toString()+')();';
    const url=URL.createObjectURL(new Blob([code],{type:'text/javascript'}));
    try{s.worker=new Worker(url);}finally{URL.revokeObjectURL(url);}
    s.worker.onmessage=e=>{
      if(job!==s.job||s.mode!=='bot'||s.game.fen()!==fen)return;
      s.worker.terminate();s.worker=null;clearTimeout(s.timer);s.timer=null;s.busy=false;
      try{s.game.move(e.data.move);s.message='Computer moved. Your turn.';s.tone='';chessSaveGame();}catch(error){fail();return;}
      renderChess();
    };
    s.worker.onerror=event=>{event.preventDefault();fail();};
    s.worker.postMessage({fen,level:s.level});s.timer=setTimeout(fail,5500);
  }catch(error){fail();return;}
  const title=document.querySelector('#chessBody .ch-turn');if(title)title.textContent=chessStatus();
}
function chessUndo(){
  chessStop();const s=chessState;s.game.undo();
  if(s.mode==='bot'&&s.game.turn()!==s.side&&s.game.history().length)s.game.undo();
  s.selected=null;s.message='Turn taken back.';s.tone='';chessSaveGame();renderChess();
}
function chessLeave(){
  if(!chessState.ready)return;
  // Finish a pending scripted reply before hiding, so resuming never strands a puzzle.
  const s=chessState,replyPending=s.mode==='puzzles'&&s.busy;
  chessStop();s.selected=null;
  if(replyPending){const move=s.puzzle[2].split(' ')[s.step];if(move){chessMoveUci(s.game,move);s.step++;s.message='Your move. Find the next check.';}}
}
function chessLoadPuzzles(){
  if(!chessState.puzzles)chessState.puzzles=JSON.parse(document.getElementById('chessPuzzleData').textContent).puzzles;
  return chessState.puzzles;
}
function chessPuzzlePool(){
  const s=chessState;
  return chessLoadPuzzles().filter(p=>(s.mate==='all'||p[4]===Number(s.mate))&&(s.difficulty==='all'||(s.difficulty==='easy'?p[3]<1200:s.difficulty==='medium'?p[3]>=1200&&p[3]<1800:p[3]>=1800))&&(!s.onlyUnsolved||!(DB.chess.solved[p[0]]||{}).solvedAt));
}
function chessNextPuzzle(){
  chessStop();const s=chessState,pool=chessPuzzlePool();
  if(!pool.length){
    s.message='No unsolved puzzles match these filters. Try another difficulty or turn off Unsolved puzzles only.';s.tone='';renderChess();return;
  }
  const choices=pool.length>1&&s.puzzle?pool.filter(p=>p[0]!==s.puzzle[0]):pool;
  chessLoadPuzzle(choices[Math.floor(Math.random()*choices.length)]);
}
function chessLoadPuzzle(puzzle){
  chessStop();const s=chessState;s.mode='puzzles';s.puzzle=puzzle;s.game=chessNewRules(puzzle[1]);s.solver=s.game.turn();s.flipped=s.solver==='b';
  s.step=0;s.assisted=false;s.finished=false;s.hint=0;s.solution=false;s.selected=null;
  s.message='Find checkmate in '+puzzle[4]+(puzzle[4]===1?' move.':' moves. Start with a forcing move.');s.tone='';renderChess();
}
function chessMarkAssisted(){
  const s=chessState;s.assisted=true;
  const record=DB.chess.solved[s.puzzle[0]]||{};
  record.assistedAt=record.assistedAt||nowISO();DB.chess.solved[s.puzzle[0]]=record;save();
}
function chessHint(){
  const s=chessState;if(s.busy||s.finished)return;
  chessMarkAssisted();s.hint=Math.min(2,s.hint+1);
  const move=s.puzzle[2].split(' ')[s.step],piece=s.game.get(move.slice(0,2));
  s.message=s.hint===1?'Look at your '+CHESS_NAMES[piece.type]+' on '+move.slice(0,2)+'.':'Try '+move.slice(0,2)+' → '+move.slice(2,4)+(move[4]?' and promote to '+CHESS_NAMES[move[4]]:'')+'.';
  s.tone='';renderChess();
}
function chessSolutionText(){
  const s=chessState,g=chessNewRules(s.puzzle[1]),parts=[];
  for(const uci of s.puzzle[2].split(' ')){
    const number=g.fen().split(' ')[5],side=g.turn(),m=chessMoveUci(g,uci);
    parts.push(number+(side==='w'?'. ':'… ')+m.san);
  }
  return parts.join('  ');
}
function chessReveal(){
  const s=chessState;if(s.busy)return;
  chessMarkAssisted();s.solution=true;s.message='The complete mating line is shown below. Play the moves on the board to practise.';s.tone='';renderChess();
}
function chessDownload(){
  const s=chessState;s.game.header('Event','Study Hub offline chess','White',s.mode==='bot'&&s.side==='b'?'Study Hub computer':'Player White','Black',s.mode==='bot'&&s.side==='w'?'Study Hub computer':'Player Black');
  const g=s.game,result=g.isCheckmate()?(g.turn()==='w'?'0-1':'1-0'):g.isDraw()?'1/2-1/2':'*';g.header('Result',result);
  const url=URL.createObjectURL(new Blob([g.pgn()],{type:'application/x-chess-pgn'}));
  const a=document.createElement('a');a.href=url;a.download='study-hub-chess.pgn';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
