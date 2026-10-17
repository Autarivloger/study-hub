/* Games hub and shared viewport sizing. Original Study Hub interface. */
let gamesFitFrame=0;
let gamesFocusSession=null,gamesFocusLayout=null,gamesFullscreenRequest=null;
function renderGames(){
  const chessSolved=Object.values(DB.chess.solved).filter(x=>x&&x.solvedAt).length;
  const sudokuSolved=Object.values(DB.sudoku.completed).filter(x=>x&&!x.assisted).length;
  document.getElementById('gamesBody').innerHTML='<div class="gm-home"><div class="gm-hero"><span class="gm-eyebrow">YOUR PLAY ROOM · READY OFFLINE</span><h2>Your next good move.</h2><p>Pick a board and keep going from where you left off.</p></div><div class="gm-cards"><article class="gm-card gm-chess"><div class="gm-preview gm-chess-preview" aria-hidden="true"><span>♞</span><span>♔</span><span>♟</span></div><div class="gm-card-copy"><span class="gm-eyebrow">STRATEGY &amp; TACTICS</span><h3>Chess</h3><p>Play a friend on this device, take on the computer, or spot the quickest checkmate.</p><div class="gm-chips"><span>2 players</span><span>3 bot levels</span><span>10,000 puzzles</span></div><div class="gm-progress">'+chessSolved.toLocaleString()+' checkmate puzzles solved'+(DB.chess.game&&DB.chess.game.moves.length?' · Saved game ready':'')+'</div><div class="gm-card-actions"><button type="button" class="btn" data-view="chess">'+(DB.chess.game&&DB.chess.game.moves.length?'Continue Chess':'Play Chess')+' <span aria-hidden="true">↗</span></button><button type="button" class="btn secondary" id="gmPuzzles">Puzzles</button></div></div></article><article class="gm-card gm-sudoku"><div class="gm-preview gm-sudoku-preview" aria-hidden="true">'+[5,'',9,'',3,'',8,'',2].map(n=>'<span>'+n+'</span>').join('')+'</div><div class="gm-card-copy"><span class="gm-eyebrow">LOGIC &amp; PATIENCE</span><h3>Sudoku</h3><p>Find the pattern, make pencil notes, and work your way from Easy to Expert.</p><div class="gm-chips"><span>Easy → Expert</span><span>Pencil notes</span><span>Fresh variations</span></div><div class="gm-progress">'+sudokuSolved.toLocaleString()+' puzzles solved independently'+(DB.sudoku.game?' · Saved puzzle ready':'')+'</div><div class="gm-card-actions"><button type="button" class="btn" data-view="sudoku">'+(DB.sudoku.game?'Continue Sudoku':'Play Sudoku')+' <span aria-hidden="true">↗</span></button></div></div></article></div><p class="gm-foot">Your place is saved automatically. Use your usual Study Hub backup or sync to take it with you.</p></div>';
  document.getElementById('gmPuzzles').onclick=()=>{switchView('chess');chessSetMode('puzzles');};
  const delivered=Object.keys(DB.sokoban.completed).filter(id=>sokoLevels().some(l=>l.id===id)).length;
  const card=document.createElement('article');card.className='gm-card gm-sokoban';
  card.innerHTML='<div class="gm-preview gm-sokoban-preview" aria-hidden="true"><span class="sk-crate"></span><span class="sk-preview-goal">✓</span></div><div class="gm-card-copy"><span class="gm-eyebrow">SPACE &amp; STRATEGY</span><h3>Sokoban</h3><p>Find a route through the warehouse. Push every crate home, one thoughtful move at a time.</p><div class="gm-chips"><span>40 levels</span><span>Undo &amp; hints</span><span>Keyboard &amp; touch</span></div><div class="gm-progress">'+delivered+' / 40 warehouses completed'+(DB.sokoban.game?' · Saved route ready':'')+'</div><div class="gm-card-actions"><button type="button" class="btn" data-view="sokoban">'+(DB.sokoban.game?'Continue Sokoban':'Play Sokoban')+' <span aria-hidden="true">↗</span></button></div></div>';
  document.querySelector('#gamesBody .gm-cards').appendChild(card);
}
function gamesFocus(){
  if(document.body.classList.contains('games-focus')){gamesExitFocus();return;}
  const view=document.querySelector('.view.active');
  if(!view||!['view-chess','view-sudoku','view-sokoban'].includes(view.id))return;
  const session={scrollY:window.scrollY,opener:view.querySelector('[data-game-focus]'),ownsFullscreen:false,sawFullscreen:Boolean(document.fullscreenElement||document.webkitFullscreenElement)};
  gamesFocusSession=session;document.body.classList.add('games-focus');
  gamesSyncFocusButtons();gamesScheduleFit();window.scrollTo(0,0);
  // Ask during the click's user activation. Layout still works where the API
  // is unsupported/denied (including some phone browsers and embedded tabs).
  const root=document.documentElement,request=root.requestFullscreen||root.webkitRequestFullscreen;
  if(!session.sawFullscreen&&request){
    session.requested=true;gamesFullscreenRequest=session;
    try{
      const pending=request.call(root,{navigationUI:'hide'});
      Promise.resolve(pending).then(()=>{
        const fullscreen=document.fullscreenElement||document.webkitFullscreenElement;
        if(fullscreen===root){
          if(gamesFocusSession){gamesFocusSession.ownsFullscreen=true;gamesFocusSession.sawFullscreen=true;}
          else gamesLeaveFullscreen();
          if(gamesFullscreenRequest===session)gamesFullscreenRequest=null;
        }
        gamesScheduleFit();
      }).catch(()=>{if(gamesFullscreenRequest===session)gamesFullscreenRequest=null;if(gamesFocusSession===session)gamesFocusFallback();});
    }catch(error){if(gamesFullscreenRequest===session)gamesFullscreenRequest=null;gamesFocusFallback();}
  }else if(!session.sawFullscreen)gamesFocusFallback();
}
function gamesLeaveFullscreen(){
  const exit=document.exitFullscreen||document.webkitExitFullscreen;
  if(exit&&(document.fullscreenElement||document.webkitFullscreenElement)){
    try{Promise.resolve(exit.call(document)).catch(()=>{});}catch(error){}
  }
}
function gamesExitFocus(restoreScroll=true){
  const session=gamesFocusSession;gamesFocusSession=null;
  document.body.classList.remove('games-focus');gamesRestoreFocusLayout();gamesSyncFocusButtons();gamesScheduleFit();
  if(session&&session.ownsFullscreen)gamesLeaveFullscreen();
  if(restoreScroll&&session){window.scrollTo(0,session.scrollY);if(session.opener?.isConnected)session.opener.focus({preventScroll:true});}
}
function gamesFocusFallback(){
  if(gamesFocusSession)gamesFocusSession.fullscreenUnavailable=true;
  gamesPrepareFocusLayout();
  if(gamesFocusLayout)gamesFocusLayout.screen.querySelector('.gm-focus-notice').hidden=false;
  gamesScheduleFit();
}
function gamesFullscreenChanged(){
  const fullscreen=document.fullscreenElement||document.webkitFullscreenElement,session=gamesFocusSession;
  // Legacy prefixed APIs can return void before their entry event arrives.
  if(fullscreen===document.documentElement&&gamesFullscreenRequest){
    gamesFullscreenRequest=null;
    if(!session){gamesLeaveFullscreen();return;}
    session.ownsFullscreen=true;
  }
  if(fullscreen&&session){session.sawFullscreen=true;if(session.requested&&fullscreen===document.documentElement)session.ownsFullscreen=true;}
  else if(!fullscreen&&session?.sawFullscreen){gamesExitFocus();return;}
  gamesScheduleFit();
}
function gamesRestoreFocusLayout(){
  if(!gamesFocusLayout)return;
  for(const item of gamesFocusLayout.moved.slice().reverse())if(item.marker.isConnected)item.marker.replaceWith(item.node);
  gamesFocusLayout.screen.remove();gamesFocusLayout=null;
}
function gamesPrepareFocusLayout(){
  if(!document.body.classList.contains('games-focus'))return;
  const view=document.querySelector('.view.active');if(!view)return;
  if(gamesFocusLayout?.view===view&&gamesFocusLayout.screen.isConnected)return;
  gamesRestoreFocusLayout();
  const kind=view.id.slice(5),board=view.querySelector('.ch-board,.su-board,.sk-stage');if(!board)return;
  const screen=document.createElement('div'),arena=document.createElement('div'),tools=document.createElement('aside'),actions=document.createElement('div'),extras=document.createElement('div');
  screen.className='gm-focus-screen';screen.dataset.game=kind;arena.className='gm-focus-arena';tools.className='gm-focus-toolbar';tools.setAttribute('aria-label',kind+' game controls');
  actions.className='gm-focus-actions';actions.setAttribute('aria-label','Game actions');extras.className='gm-focus-extras';
  screen.append(arena,tools);view.append(screen);gamesFocusLayout={view,screen,arena,tools,moved:[]};
  const move=(node,parent)=>{if(!node)return;const marker=document.createComment('focus return');node.before(marker);gamesFocusLayout.moved.push({node,marker});parent.append(node);};
  move(view.querySelector('.gm-header'),tools);
  const notice=document.createElement('p');notice.className='gm-focus-notice';notice.setAttribute('role','status');notice.textContent='Fullscreen is unavailable in this browser. Focus view is still ready.';notice.hidden=!gamesFocusSession?.fullscreenUnavailable;tools.append(notice);
  move(board,arena);
  const ids=kind==='chess'?['chUndo','chHint','chRetry','chSolution','chNextPuzzle','chNew','chFlip']:kind==='sudoku'?['suUndo','suHint','suErase','suNotes']:['skUndo','skHint','skRestart','skNext'];
  tools.append(actions);for(const id of ids)move(view.querySelector('#'+id),actions);
  if(kind==='chess'){
    move(view.querySelector('#chPromotion'),tools);move(view.querySelector('.ch-tabs'),tools);move(view.querySelector('.ch-main>.ch-card'),tools);move(view.querySelector('.ch-aside'),extras);
  }else if(kind==='sudoku'){
    move(view.querySelector('.su-pad'),tools);move(view.querySelector('.su-board-meta'),tools);move(view.querySelector('.su-status'),tools);move(view.querySelector('.su-aside'),extras);
    const more=document.createElement('div');more.className='gm-focus-actions';extras.prepend(more);
    for(const id of ['suReplay','suSave','suCheck','suAutoNotes','suNew'])move(view.querySelector('#'+id),more);
  }else{
    move(view.querySelector('.sk-dpad'),tools);move(view.querySelector('.sk-hud'),tools);move(view.querySelector('.sk-status'),tools);move(view.querySelector('.sk-aside'),extras);
  }
  tools.append(extras);
}
function gamesFitFocus(){
  gamesPrepareFocusLayout();const layout=gamesFocusLayout;if(!layout)return;
  if(layout.screen.dataset.game==='sokoban'&&sokoState.pointer)return;
  const arena=layout.arena,board=arena.querySelector('.ch-board,.su-board,.sk-board');if(!board)return;
  const ratio=board.classList.contains('sk-board')&&sokoState.board?sokoState.board.width/sokoState.board.height:1;
  const width=Math.floor(Math.max(40,Math.min(arena.clientWidth-8,(arena.clientHeight-8)*ratio)));
  arena.style.setProperty('--focus-board-size',width+'px');
}
function gamesSyncFocusButtons(){
  const focused=document.body.classList.contains('games-focus');
  document.querySelectorAll('[data-game-focus]').forEach(b=>{b.textContent=focused?'Exit focus ↙':'Focus view ↗';b.setAttribute('aria-pressed',String(focused));});
}
function gamesNavigate(name){
  if(!['chess','sudoku','sokoban'].includes(name))gamesExitFocus(false);
  else if(gamesFocusLayout&&gamesFocusLayout.view.id!=='view-'+name)gamesRestoreFocusLayout();
  if(['games','chess','sudoku','sokoban'].includes(name))window.scrollTo(0,0);
  gamesSyncFocusButtons();
}
function gamesScheduleFit(){
  cancelAnimationFrame(gamesFitFrame);
  gamesFitFrame=requestAnimationFrame(()=>{gamesFitBoards();gamesFitFrame=requestAnimationFrame(gamesFitBoards);});
}
function gamesFitBoards(){
  if(document.body.classList.contains('games-focus')){gamesFitFocus();return;}
  if(document.getElementById('view-sokoban').classList.contains('active')){sokoFitBoard();return;}
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
document.addEventListener('fullscreenchange',gamesFullscreenChanged);
document.addEventListener('webkitfullscreenchange',gamesFullscreenChanged);
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&document.body.classList.contains('games-focus')&&!document.querySelector('#overlay.open,dialog[open]'))gamesExitFocus();});
