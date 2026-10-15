/* Games hub and shared viewport sizing. Original Study Hub interface. */
let gamesFitFrame=0;
function renderGames(){
  const chessSolved=Object.values(DB.chess.solved).filter(x=>x&&x.solvedAt).length;
  const sudokuSolved=Object.values(DB.sudoku.completed).filter(x=>x&&!x.assisted).length;
  document.getElementById('gamesBody').innerHTML='<div class="gm-home"><div class="gm-hero"><span class="gm-eyebrow">YOUR PLAY ROOM · READY OFFLINE</span><h2>Your next good move.</h2><p>Pick a board and keep going from where you left off.</p></div><div class="gm-cards"><article class="gm-card gm-chess"><div class="gm-preview gm-chess-preview" aria-hidden="true"><span>♞</span><span>♔</span><span>♟</span></div><div class="gm-card-copy"><span class="gm-eyebrow">STRATEGY &amp; TACTICS</span><h3>Chess</h3><p>Play a friend on this device, take on the computer, or spot the quickest checkmate.</p><div class="gm-chips"><span>2 players</span><span>3 bot levels</span><span>10,000 puzzles</span></div><div class="gm-progress">'+chessSolved.toLocaleString()+' checkmate puzzles solved'+(DB.chess.game&&DB.chess.game.moves.length?' · Saved game ready':'')+'</div><div class="gm-card-actions"><button type="button" class="btn" data-view="chess">'+(DB.chess.game&&DB.chess.game.moves.length?'Continue Chess':'Play Chess')+' <span aria-hidden="true">↗</span></button><button type="button" class="btn secondary" id="gmPuzzles">Puzzles</button></div></div></article><article class="gm-card gm-sudoku"><div class="gm-preview gm-sudoku-preview" aria-hidden="true">'+[5,'',9,'',3,'',8,'',2].map(n=>'<span>'+n+'</span>').join('')+'</div><div class="gm-card-copy"><span class="gm-eyebrow">LOGIC &amp; PATIENCE</span><h3>Sudoku</h3><p>Find the pattern, make pencil notes, and work your way from Easy to Expert.</p><div class="gm-chips"><span>Easy → Expert</span><span>Pencil notes</span><span>Fresh variations</span></div><div class="gm-progress">'+sudokuSolved.toLocaleString()+' puzzles solved independently'+(DB.sudoku.game?' · Saved puzzle ready':'')+'</div><div class="gm-card-actions"><button type="button" class="btn" data-view="sudoku">'+(DB.sudoku.game?'Continue Sudoku':'Play Sudoku')+' <span aria-hidden="true">↗</span></button></div></div></article></div><p class="gm-foot">Your place is saved automatically. Use your usual Study Hub backup or sync to take it with you.</p></div>';
  document.getElementById('gmPuzzles').onclick=()=>{switchView('chess');chessSetMode('puzzles');};
}
function gamesFocus(){
  document.body.classList.toggle('games-focus');gamesSyncFocusButtons();gamesScheduleFit();
  window.scrollTo(0,0);
}
function gamesSyncFocusButtons(){
  const focused=document.body.classList.contains('games-focus');
  document.querySelectorAll('[data-game-focus]').forEach(b=>{b.textContent=focused?'Exit focus ↙':'Focus view ↗';b.setAttribute('aria-pressed',String(focused));});
}
function gamesNavigate(name){
  if(!['chess','sudoku'].includes(name))document.body.classList.remove('games-focus');
  if(['games','chess','sudoku'].includes(name))window.scrollTo(0,0);
  gamesSyncFocusButtons();
}
function gamesScheduleFit(){
  cancelAnimationFrame(gamesFitFrame);
  gamesFitFrame=requestAnimationFrame(()=>{gamesFitBoards();gamesFitFrame=requestAnimationFrame(gamesFitBoards);});
}
function gamesFitBoards(){
  const view=document.querySelector('.view.active');if(!view||!['view-chess','view-sudoku'].includes(view.id))return;
  const board=view.querySelector('.ch-board,.su-board'),main=view.querySelector('.ch-main,.su-main'),wrap=view.querySelector('.ch-wrap,.su-wrap');
  if(!board||!main||!wrap)return;
  const width=wrap.clientWidth-parseFloat(getComputedStyle(wrap).paddingLeft)-parseFloat(getComputedStyle(wrap).paddingRight);
  const landscape=document.body.classList.contains('games-focus')&&innerHeight<=500&&innerWidth>=600;
  const room=innerWidth>1080||landscape?width-280:width;
  const maximum=Math.max(90,Math.min(560,room));
  // Reset before measuring: a narrow previous board can wrap its labels and
  // otherwise keep shrinking when the viewport grows or Focus is entered.
  wrap.style.setProperty('--game-board-size',Math.floor(maximum)+'px');
  const viewport=window.visualViewport?Math.min(innerHeight,window.visualViewport.height):innerHeight;
  for(let pass=0;pass<3;pass++){
    const rect=board.getBoundingClientRect(),mainRect=main.getBoundingClientRect();
    const after=Math.max(0,mainRect.bottom-rect.bottom);
    const available=viewport-(rect.top+window.scrollY)-after-16;
    const size=Math.max(90,Math.floor(Math.min(maximum,available)));
    wrap.style.setProperty('--game-board-size',size+'px');
  }
}
window.addEventListener('resize',gamesScheduleFit);
if(window.visualViewport)window.visualViewport.addEventListener('resize',gamesScheduleFit);
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&document.body.classList.contains('games-focus')){document.body.classList.remove('games-focus');gamesSyncFocusButtons();gamesScheduleFit();}});
