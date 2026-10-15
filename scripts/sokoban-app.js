/* Original Study Hub Sokoban UI, using existing save/import/sync and Games focus. */
function sokoDefaults(value){
  const d=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  if(!d.completed||typeof d.completed!=='object'||Array.isArray(d.completed))d.completed={};
  Object.keys(d.completed).forEach(id=>{
    const r=d.completed[id];
    if(!/^sk-\d{3}$/.test(id)||!r||!Number.isInteger(r.moves)||r.moves<1||!Number.isInteger(r.pushes)||r.pushes<1||r.pushes>r.moves){delete d.completed[id];return;}
    d.completed[id]={moves:r.moves,pushes:r.pushes,assisted:!!r.assisted,at:typeof r.at==='string'?r.at:''};
  });
  const g=d.game;
  // Safe during DB loading, before the level bank or UI state is initialized.
  if(!g||typeof g!=='object'||!/^sk-\d{3}$/.test(g.level)||typeof g.moves!=='string'||!/^[UDLR]{0,10000}$/.test(g.moves))d.game=null;
  if(d.game){d.game.assisted=!!g.assisted;d.game.at=typeof g.at==='string'?g.at:'';}
  return d;
}
function sokoBetter(a,b){
  if(!a)return b;if(!b)return a;
  if(!!a.assisted!==!!b.assisted)return a.assisted?b:a;
  return b.pushes<a.pushes||(b.pushes===a.pushes&&b.moves<a.moves)?b:a;
}
function sokoMerge(incoming){
  const other=sokoDefaults(incoming),mine=DB.sokoban;
  Object.keys(other.completed).forEach(id=>{
    const x=other.completed[id];if(!/^sk-\d{3}$/.test(id)||!x||!Number.isInteger(x.moves)||x.moves<1||!Number.isInteger(x.pushes)||x.pushes<1||x.pushes>x.moves)return;
    mine.completed[id]=sokoBetter(mine.completed[id],{moves:x.moves,pushes:x.pushes,assisted:!!x.assisted,at:typeof x.at==='string'?x.at:''});
  });
  if(other.game&&(!mine.game||other.game.at>mine.game.at))mine.game=other.game;
}
const sokoState={levels:null,board:null,position:null,history:[],source:null,level:null,message:'',tone:'',hint:null,worker:null,job:0,timer:null,busy:false,pack:'all',pointer:null,suppressClick:false};
function sokoLevels(){if(!sokoState.levels)sokoState.levels=JSON.parse(document.getElementById('sokobanLevelData').textContent).levels;return sokoState.levels;}
function sokoCancelHint(){
  const s=sokoState;s.job++;if(s.worker)s.worker.terminate();s.worker=null;clearTimeout(s.timer);s.timer=null;s.busy=false;s.hint=null;
}
function sokoStart(id){
  sokoCancelHint();const level=sokoLevels().find(l=>l.id===id)||sokoLevels()[0];
  DB.sokoban.game={level:level.id,moves:'',assisted:false,at:nowISO()};sokoState.source=null;sokoEnsure();save();
}
function sokoEnsure(){
  const s=sokoState;if(!DB.sokoban.game){const first=sokoLevels()[0];DB.sokoban.game={level:first.id,moves:'',assisted:false,at:nowISO()};save();}
  if(s.source===DB.sokoban.game)return;
  sokoCancelHint();const g=DB.sokoban.game;s.level=sokoLevels().find(l=>l.id===g.level)||sokoLevels()[0];
  if(g.level!==s.level.id){g.level=s.level.id;g.moves='';g.assisted=false;}
  s.board=sokoParse(s.level.map);s.position=s.board.start;s.history=[];
  try{for(const direction of g.moves){const next=sokoStep(s.board,s.position,direction);if(!next||sokoWon(s.board,s.position))throw Error('Invalid saved route');s.history.push(s.position);s.position=next;}s.message='Push every crate onto a glowing goal. You can push one crate at a time.';s.tone='';}
  catch(error){g.level=s.level.id;g.moves='';g.assisted=false;s.position=s.board.start;s.history=[];s.message='This saved route could not be restored. The level is ready again; completed levels are still saved.';s.tone='';}
  s.source=g;
}
function sokoSave(){DB.sokoban.game.at=nowISO();sokoState.source=DB.sokoban.game;save();}
function sokoRecordWin(){
  const s=sokoState,g=DB.sokoban.game;
  const record={at:nowISO(),moves:g.moves.length,pushes:s.position.pushes,assisted:!!g.assisted};
  DB.sokoban.completed[g.level]=sokoBetter(DB.sokoban.completed[g.level],record);
  s.message=g.assisted?'Delivery complete — practised with a hint. Try the next warehouse when you are ready.':'Delivery complete! Every crate is home. Choose Next level when you are ready.';s.tone='good';
}
function sokoMove(direction){
  sokoEnsure();const s=sokoState,g=DB.sokoban.game;
  if(sokoWon(s.board,s.position))return;
  sokoCancelHint();const next=sokoStep(s.board,s.position,direction);
  if(!next){s.message='That way is blocked. Crates need an empty square beyond them.';s.tone='';sokoUpdateStatus();return false;}
  s.history.push(s.position);s.position=next;g.moves+=direction;
  const dead=sokoDeadSquares(s.board);
  if(s.position.boxes.some(p=>dead.has(p))){s.message='A crate is trapped away from a goal. Undo this move and find another approach.';s.tone='warn';}
  else{s.message='Good planning leaves room to stand behind the next crate.';s.tone='';}
  if(sokoWon(s.board,s.position))sokoRecordWin();sokoSave();renderSokoban();return true;
}
function sokoUndo(){
  sokoCancelHint();const s=sokoState,previous=s.history.pop();if(!previous)return;
  s.position=previous;DB.sokoban.game.moves=DB.sokoban.game.moves.slice(0,-1);s.message='Last move undone. Your route is yours to rethink.';s.tone='';sokoSave();renderSokoban();
}
function sokoRequestLevel(id,restart=false){
  const g=DB.sokoban.game;
  const start=()=>{sokoStart(id);renderSokoban();};
  if(g&&g.moves.length&&!sokoWon(sokoState.board,sokoState.position)){
    openModal('<h2>'+(restart?'Restart this level?':'Change warehouse?')+'</h2><p>This starts a fresh route. Completed levels and best results stay saved.</p><div class="modal-actions"><button type="button" class="btn secondary" id="skKeep">Keep playing</button><button type="button" class="btn" id="skConfirm">'+(restart?'Restart level':'Change level')+'</button></div>');
    document.getElementById('skKeep').onclick=closeModal;document.getElementById('skConfirm').onclick=()=>{closeModal();start();};
  }else start();
}
function sokoHintWorker(){self.onmessage=event=>{try{const {map,position}=event.data;self.postMessage(sokoSolve(sokoParse(map),position,{maxStates:40000,maxMs:1600}));}catch(error){self.postMessage({status:'error',path:null});}};}
function sokoHint(){
  const s=sokoState;if(s.busy||sokoWon(s.board,s.position))return;
  sokoCancelHint();s.busy=true;const job=s.job;s.message='Looking for a safe route…';s.tone='';sokoUpdateStatus();
  const finish=result=>{
    if(job!==s.job)return;if(s.worker)s.worker.terminate();s.worker=null;clearTimeout(s.timer);s.timer=null;s.busy=false;
    if(result.status==='solved'&&result.path){s.hint=result.path[0];DB.sokoban.game.assisted=true;sokoSave();s.message='Hint: move '+{U:'up ↑',D:'down ↓',L:'left ←',R:'right →'}[s.hint]+'. This attempt is marked as practised with help.';s.tone='';}
    else{s.message=result.status==='impossible'?'There is no finish from this position. Use Undo or restart to free your crates.':'A hint was not found within the short thinking time. Try Undo or restart, and keep a route behind each crate.';s.tone=result.status==='impossible'?'warn':'';}
    renderSokoban();
  };
  try{
    const source=document.getElementById('sokobanRules').textContent+'\n('+sokoHintWorker.toString()+')();';
    const url=URL.createObjectURL(new Blob([source],{type:'text/javascript'}));try{s.worker=new Worker(url);}finally{URL.revokeObjectURL(url);}
    s.worker.onmessage=event=>finish(event.data);s.worker.onerror=event=>{event.preventDefault();finish({status:'error'});};
    s.worker.postMessage({map:s.level.map,position:s.position});s.timer=setTimeout(()=>finish({status:'limit'}),2600);
  }catch(error){finish({status:'error'});}
}
function sokoUpdateStatus(){
  const node=document.getElementById('skStatus');if(node){node.textContent=sokoState.message;node.dataset.tone=sokoState.tone;}
  const hint=document.getElementById('skHint');if(hint){hint.disabled=sokoState.busy;hint.textContent=sokoState.busy?'Thinking…':'One hint';}
  gamesScheduleFit();
}
function sokoWorkerArt(){return '<svg class="sk-worker" viewBox="0 0 60 60" aria-hidden="true"><ellipse cx="30" cy="52" rx="17" ry="4" fill="#183f3b" opacity=".16"/><path d="M12 49q1-18 18-18t18 18" fill="#17645a"/><rect x="19" y="17" width="22" height="22" rx="10" fill="#f3ce99"/><path d="M16 23q-2-16 14-16t14 16z" fill="#f4b84c"/><path d="M13 23h34" stroke="#cf9131" stroke-width="4" stroke-linecap="round"/><path d="M30 9v10" stroke="#ffe09a" stroke-width="4" stroke-linecap="round"/><circle cx="25" cy="28" r="1.6" fill="#284338"/><circle cx="35" cy="28" r="1.6" fill="#284338"/><path d="M27 33q3 2 6 0" fill="none" stroke="#9f6a41" stroke-width="1.4" stroke-linecap="round"/></svg>';}
function renderSokoban(){
  sokoEnsure();const s=sokoState,b=s.board,p=s.position,g=DB.sokoban.game,levels=sokoLevels(),index=levels.indexOf(s.level),won=sokoWon(b,p),best=DB.sokoban.completed[g.level];
  const delivered=p.boxes.filter(i=>b.goals.has(i)).length,boxes=new Set(p.boxes),hint=s.hint?sokoNeighbour(b,p.player,s.hint):-1;
  let tiles='';for(let i=0;i<b.width*b.height;i++){
    const wall=b.walls.has(i),goal=b.goals.has(i),box=boxes.has(i),player=p.player===i;
    tiles+='<div class="sk-tile '+(wall?'sk-wall':'sk-floor')+(goal?' sk-goal':'')+(hint===i?' sk-hint':'')+'" data-sk-tile="'+i+'" aria-hidden="true">'+(goal?'<span class="sk-target"></span>':'')+(box?'<span class="sk-crate '+(goal?'sk-delivered':'')+'">'+(goal?'<span>✓</span>':'')+'</span>':'')+(player?sokoWorkerArt():'')+'</div>';
  }
  const packNames=[...new Set(levels.map(l=>l.pack))],shown=levels.filter(l=>s.pack==='all'||l.pack===s.pack);
  const title=(won?'All crates delivered':'Level '+(index+1))+' · '+s.level.title;
  document.getElementById('sokobanBody').innerHTML='<div class="sk-wrap"><div class="sk-layout"><div class="sk-main"><div class="sk-hud"><div><small>MOVES</small><strong>'+g.moves.length+'</strong></div><div><small>PUSHES</small><strong>'+p.pushes+'</strong></div><div><small>DELIVERED</small><strong>'+delivered+'<span> / '+b.goals.size+'</span></strong></div></div><div class="sk-stage"><div class="sk-board" tabindex="0" role="group" aria-label="Sokoban warehouse. '+delivered+' of '+b.goals.size+' crates on goals. Player row '+(Math.floor(p.player/b.width)+1)+', column '+(p.player%b.width+1)+'. Arrow keys or W A S D move." aria-describedby="skStatus" style="--sk-cols:'+b.width+';--sk-rows:'+b.height+'">'+tiles+'</div></div><div class="sk-controls"><div class="sk-dpad" aria-label="Movement controls"><button type="button" data-sk-direction="U" aria-label="Move up"'+(won?' disabled':'')+'>↑</button><button type="button" data-sk-direction="L" aria-label="Move left"'+(won?' disabled':'')+'>←</button><span aria-hidden="true">✦</span><button type="button" data-sk-direction="R" aria-label="Move right"'+(won?' disabled':'')+'>→</button><button type="button" data-sk-direction="D" aria-label="Move down"'+(won?' disabled':'')+'>↓</button></div><div class="sk-tools"><button type="button" class="btn secondary" id="skUndo"'+(!g.moves.length?' disabled':'')+'>↶ Undo</button><button type="button" class="btn secondary" id="skRestart">↺ Restart</button><button type="button" class="btn secondary" id="skHint"'+(won||s.busy?' disabled':'')+'>'+(s.busy?'Thinking…':'One hint')+'</button><button type="button" class="btn" id="skNext"'+(index===levels.length-1?' disabled':'')+'>'+(won?'Next level →':'Next →')+'</button></div></div><p class="sk-status" id="skStatus" role="status" aria-live="polite" data-tone="'+s.tone+'">'+escapeHtml(s.message)+'</p></div><aside class="sk-aside"><section class="sk-card sk-overview"><span class="gm-eyebrow">'+escapeHtml(s.level.pack.toUpperCase())+'</span><h2>'+escapeHtml(title)+'</h2><p>Push the wooden crates onto the glowing circles. Plan your way back before each push.</p><div class="sk-legend"><span><i class="sk-legend-crate"></i>Crate</span><span><i class="sk-legend-goal"></i>Goal</span><span><i class="sk-legend-done">✓</i>Delivered</span></div><div class="sk-best">'+(best?'Your best: <strong>'+best.moves+' moves · '+best.pushes+' pushes</strong><br>'+(best.assisted?'Practised with help':'Solved independently'):'A fresh warehouse. Find your own route.')+'</div><p class="sk-caption">'+(g.assisted?'This attempt uses a hint.':'Independent attempt.')+' Your route saves automatically.</p></section><section class="sk-card"><div class="sk-level-heading"><h3>Choose a warehouse</h3><span>'+Object.keys(DB.sokoban.completed).filter(id=>levels.some(l=>l.id===id)).length+' / '+levels.length+' done</span></div><label class="sk-pack-label">Level pack<select id="skPack"><option value="all"'+(s.pack==='all'?' selected':'')+'>All 40 levels</option>'+packNames.map(name=>'<option'+(s.pack===name?' selected':'')+'>'+escapeHtml(name)+'</option>').join('')+'</select></label><div class="sk-levels">'+shown.map(l=>{const number=levels.indexOf(l)+1,record=DB.sokoban.completed[l.id];return '<button type="button" data-sk-level="'+l.id+'" class="'+(l.id===g.level?'sk-current ':'')+(record?'sk-cleared':'')+'" aria-label="Level '+number+': '+escapeHtml(l.title)+(record?', completed':'')+'" aria-current="'+(l.id===g.level?'step':'false')+'"><span>'+number+'</span>'+(record?'<small>'+(record.assisted?'·':'✓')+'</small>':'')+'</button>';}).join('')+'</div><p class="sk-caption">Every level is open. A check means independently solved; a dot means practised with help.</p></section><details class="sk-card sk-help"><summary>How to play</summary><p>Use arrow keys, W A S D, the on-screen arrows, or swipe on the board. You can also tap the square directly beside the worker.</p><p>Push one crate at a time. You cannot pull a crate, move through walls, or push two crates together. A crate in a corner without a goal can get stuck. Undo is always there for a rethink.</p><p>Put all crates on circles to finish. Completed levels stay saved; you choose when to advance. A hint marks the attempt as practised with help.</p><p>Focus view clears the surrounding navigation and fits the board to your screen. Exit focus or Escape brings it back. Undo: Z. Restart: R. These keys work only while this game is open.</p><p>40 original Study Hub levels and original artwork. Inspired by the box-pushing game in <a href="https://github.com/paskhaver/sokoban" target="_blank" rel="noopener noreferrer">paskhaver/sokoban</a>.</p></details></aside></div></div>';
  const body=document.getElementById('sokobanBody');body.querySelectorAll('[data-sk-direction]').forEach(button=>button.onclick=()=>sokoMove(button.dataset.skDirection));
  body.querySelector('#skUndo').onclick=sokoUndo;body.querySelector('#skRestart').onclick=()=>sokoRequestLevel(g.level,true);body.querySelector('#skHint').onclick=sokoHint;
  body.querySelector('#skNext').onclick=()=>sokoRequestLevel(levels[index+1].id);
  body.querySelector('#skPack').onchange=event=>{s.pack=event.target.value;renderSokoban();};
  body.querySelectorAll('[data-sk-level]').forEach(button=>button.onclick=()=>{if(button.dataset.skLevel!==g.level)sokoRequestLevel(button.dataset.skLevel);});
  const board=body.querySelector('.sk-board');
  board.onclick=event=>{if(s.suppressClick){s.suppressClick=false;return;}const tile=event.target.closest('[data-sk-tile]');if(!tile)return;const i=Number(tile.dataset.skTile);for(const direction of 'UDLR')if(sokoNeighbour(b,s.position.player,direction)===i){sokoMove(direction);return;}board.focus({preventScroll:true});};
  board.onpointerdown=event=>{s.pointer={x:event.clientX,y:event.clientY};s.suppressClick=false;};
  board.onpointerup=event=>{if(!s.pointer)return;const dx=event.clientX-s.pointer.x,dy=event.clientY-s.pointer.y;s.pointer=null;if(Math.max(Math.abs(dx),Math.abs(dy))>=20){s.suppressClick=true;sokoMove(Math.abs(dx)>Math.abs(dy)?dx>0?'R':'L':dy>0?'D':'U');}gamesScheduleFit();};
  board.onpointercancel=()=>{s.pointer=null;gamesScheduleFit();};
  gamesScheduleFit();
}
function sokoFitBoard(){
  if(sokoState.pointer)return; // Keep the board still underneath an active swipe.
  const wrap=document.querySelector('#view-sokoban .sk-wrap'),board=document.querySelector('#view-sokoban .sk-board'),main=document.querySelector('#view-sokoban .sk-main');if(!wrap||!board||!sokoState.board)return;
  const b=sokoState.board,style=getComputedStyle(wrap),width=wrap.clientWidth-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight);
  const wide=innerWidth>1080||(document.body.classList.contains('games-focus')&&innerWidth>=650&&innerHeight<=540);
  const maxWidth=Math.max(90,Math.min(600,wide?width-294:width));
  wrap.style.setProperty('--sk-board-width',Math.floor(maxWidth)+'px');
  const height=window.visualViewport?Math.min(innerHeight,window.visualViewport.height):innerHeight;
  for(let pass=0;pass<3;pass++){
    const rect=board.getBoundingClientRect(),mainRect=main.getBoundingClientRect(),after=Math.max(0,mainRect.bottom-rect.bottom);
    const available=Math.max(b.height*8,height-rect.top-window.scrollY-after-14),tile=Math.max(8,Math.floor(Math.min(maxWidth/b.width,available/b.height)));
    wrap.style.setProperty('--sk-board-width',tile*b.width+'px');
  }
}
document.addEventListener('keydown',event=>{
  if(!document.getElementById('view-sokoban').classList.contains('active')||overlay.classList.contains('open')||event.ctrlKey||event.metaKey||event.altKey||event.target.closest('input,textarea,select,[contenteditable=true]'))return;
  const key=event.key.toLowerCase(),direction={arrowup:'U',arrowdown:'D',arrowleft:'L',arrowright:'R',w:'U',s:'D',a:'L',d:'R'}[key];
  if(direction){event.preventDefault();sokoMove(direction);document.querySelector('#view-sokoban .sk-board').focus({preventScroll:true});}else if(key==='z'){event.preventDefault();sokoUndo();}else if(key==='r'&&!event.repeat){event.preventDefault();sokoRequestLevel(DB.sokoban.game.level,true);}
});
