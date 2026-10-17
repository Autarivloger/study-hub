/* Additive saved data. The app's existing export/import/sync owns persistence. */
function sudokuDefaults(value){
  const d=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  if(!d.completed||typeof d.completed!=='object'||Array.isArray(d.completed))d.completed={};
  if(!sudokuValidGame(d.game))d.game=null;
  if(d.game){d.game.hints=Math.max(0,Math.min(10000,Number(d.game.hints)||0));d.game.assisted=!!d.game.assisted;}
  if(!d.saved||typeof d.saved!=='object'||Array.isArray(d.saved))d.saved={};
  for(const id of Object.keys(d.saved)){
    if(!sudokuValidSavedId(id)||!sudokuValidGame(d.saved[id])||d.saved[id].id!==id)delete d.saved[id];
    else d.saved[id]=sudokuCopyGame(d.saved[id]);
  }
  sudokuArchiveGame(d.game,d);
  return d;
}
function sudokuValidSavedId(id){
  const match=/^sh\d{3}-(\d{1,10})$/.exec(id);
  return !!match&&Number(match[1])<=4294967295;
}
function sudokuCopyGame(g){
  return {id:g.id,level:g.level,givens:g.givens,solution:g.solution,values:g.values.slice(),notes:g.notes.slice(),at:typeof g.at==='string'?g.at:'',assisted:!!g.assisted,hints:Math.max(0,Math.min(10000,Number(g.hints)||0))};
}
function sudokuArchiveGame(g,store=DB.sudoku){
  if(!sudokuValidGame(g)||!sudokuValidSavedId(g.id))return;
  const previous=store.saved[g.id];
  if(!previous||String(g.at||'')>=String(previous.at||''))store.saved[g.id]=sudokuCopyGame(g);
}
function sudokuNextTime(id){
  // Keep an intentional local edit newer than an imported/device-clock timestamp.
  let time=Date.parse(nowISO());
  for(const at of [DB.sudoku.game?.at,DB.sudoku.saved[id]?.at]){const previous=Date.parse(at);if(Number.isFinite(previous)&&previous<8640000000000000)time=Math.max(time,previous+1);}
  return new Date(time).toISOString();
}
function sudokuValidGame(g){
  // Called while the old DB loads, before later UI constants are initialized.
  return !!g&&typeof g==='object'&&typeof g.id==='string'&&g.id.length<80&&['easy','medium','hard','expert'].includes(g.level)&&/^[0-9]{81}$/.test(g.givens)&&/^[1-9]{81}$/.test(g.solution)&&Array.isArray(g.values)&&g.values.length===81&&g.values.every((n,i)=>Number.isInteger(n)&&n>=0&&n<=9&&(!Number(g.givens[i])||(n===Number(g.givens[i])&&n===Number(g.solution[i]))))&&Array.isArray(g.notes)&&g.notes.length===81&&g.notes.every(n=>Number.isInteger(n)&&n>=0&&n<=511);
}
function sudokuMerge(incoming){
  const other=sudokuDefaults(incoming),mine=DB.sudoku;
  sudokuArchiveGame(mine.game,mine);
  for(const g of Object.values(other.saved))sudokuArchiveGame(g,mine);
  Object.keys(other.completed).forEach(id=>{
    if(!/^sh\d{3}-\d{1,10}$/.test(id))return;
    const entry=other.completed[id];if(!entry||!SUDOKU_LEVELS[entry.level])return;
    const local=mine.completed[id];if(!local||(local.assisted&&!entry.assisted))mine.completed[id]=entry;
  });
  if(other.game&&(!mine.game||String(other.game.at||'')>String(mine.game.at||'')))mine.game=sudokuCopyGame(other.game);
}
const sudokuState={selected:0,notesMode:false,level:'easy',message:'Choose an empty square, then enter a number.',wrong:[],undo:[],source:null,bank:null,savedPage:0};
function sudokuBank(){if(!sudokuState.bank)sudokuState.bank=JSON.parse(document.getElementById('sudokuPuzzleData').textContent).puzzles;return sudokuState.bank;}
function sudokuEnsure(){
  if(!DB.sudoku.game)sudokuStart('easy');
  if(sudokuState.source!==DB.sudoku.game){sudokuState.source=DB.sudoku.game;sudokuState.undo=[];sudokuState.wrong=[];sudokuState.notesMode=false;sudokuState.level=DB.sudoku.game.level;sudokuState.selected=DB.sudoku.game.givens.indexOf('0');}
}
function sudokuStart(level){
  const pool=sudokuBank().filter(p=>p[1]===level),previous=DB.sudoku.game;
  sudokuArchiveGame(previous);
  const choices=pool.filter(p=>!previous||!previous.id.startsWith(p[0]+'-'));
  const p=choices[Math.floor(Math.random()*choices.length)],seed=Math.floor(Math.random()*4294967296);
  const transformed=sudokuTransform(p[2],p[3],seed);
  const id=p[0]+'-'+seed;
  DB.sudoku.game={id,level,givens:transformed.givens.join(''),solution:transformed.solution.join(''),values:transformed.givens.slice(),notes:Array(81).fill(0),at:sudokuNextTime(id),assisted:false,hints:0};
  sudokuArchiveGame(DB.sudoku.game);sudokuState.savedPage=0;
  sudokuState.source=null;sudokuState.message='Your '+SUDOKU_LEVELS[level].label.toLowerCase()+' puzzle is ready. Find an empty square to begin.';save();
}
function sudokuSave(){DB.sudoku.game.at=sudokuNextTime(DB.sudoku.game.id);sudokuArchiveGame(DB.sudoku.game);sudokuState.source=DB.sudoku.game;save();}
function sudokuGetSaved(id){
  const saved=DB.sudoku.saved[id];
  if(sudokuValidGame(saved)&&saved.id===id)return sudokuCopyGame(saved);
  // Older completion records already contain the original layout id + seed.
  // Reconstruct only the requested puzzle, retaining the exact transformation.
  if(!sudokuValidSavedId(id))return null;
  const record=DB.sudoku.completed[id],cut=id.lastIndexOf('-');
  if(!record||!SUDOKU_LEVELS[record.level])return null;
  const original=sudokuBank().find(p=>p[0]===id.slice(0,cut)&&p[1]===record.level);if(!original)return null;
  const grid=sudokuTransform(original[2],original[3],Number(id.slice(cut+1)));
  return {id,level:record.level,givens:grid.givens.join(''),solution:grid.solution.join(''),values:grid.givens.slice(),notes:Array(81).fill(0),at:record.at||'',assisted:false,hints:0};
}
function sudokuOpenSaved(id,replay=false){
  const game=sudokuGetSaved(id);if(!game){toast('This saved puzzle could not be opened.');return;}
  sudokuArchiveGame(DB.sudoku.game);
  if(replay){game.values=game.givens.split('').map(Number);game.notes=Array(81).fill(0);game.assisted=false;game.hints=0;}
  game.at=sudokuNextTime(id);DB.sudoku.game=game;sudokuArchiveGame(game);
  sudokuState.source=null;sudokuState.savedPage=0;sudokuState.message=replay?'Same puzzle, fresh attempt. Your completion records are kept.':'Saved puzzle restored, including your numbers and pencil notes.';
  save();renderSudoku();sudokuFocusCell();
}
function sudokuReplayPrompt(id=DB.sudoku.game.id){
  const game=sudokuGetSaved(id);if(!game){toast('This saved puzzle could not be opened.');return;}
  const progress=game.values.some((n,i)=>n&&game.givens[i]==='0')||game.notes.some(Boolean);
  if(progress&&game.values.join('')!==game.solution){
    openModal('<h2>Play this puzzle again?</h2><p>This resets this puzzle’s entered numbers, pencil notes and hints for a fresh attempt. Your completion records and other saved puzzles stay saved.</p><div class="modal-actions"><button class="btn secondary" type="button" id="suCancelReplay">Keep saved puzzle</button><button class="btn" type="button" id="suConfirmReplay">Play again</button></div>');
    document.getElementById('suCancelReplay').onclick=closeModal;
    document.getElementById('suConfirmReplay').onclick=()=>{closeModal();sudokuOpenSaved(id,true);};
  }else sudokuOpenSaved(id,true);
}
function sudokuSavedHTML(){
  const all=[...new Set([...Object.keys(DB.sudoku.saved),...Object.keys(DB.sudoku.completed)])].filter(id=>sudokuValidSavedId(id)&&(sudokuValidGame(DB.sudoku.saved[id])||SUDOKU_LEVELS[DB.sudoku.completed[id]?.level]));
  const at=id=>String(DB.sudoku.saved[id]?.at||DB.sudoku.completed[id]?.at||'');
  all.sort((a,b)=>at(b).localeCompare(at(a))||a.localeCompare(b));
  const perPage=6,pages=Math.max(1,Math.ceil(all.length/perPage));sudokuState.savedPage=Math.max(0,Math.min(sudokuState.savedPage,pages-1));
  const shown=all.slice(sudokuState.savedPage*perPage,(sudokuState.savedPage+1)*perPage);
  const rows=shown.map(id=>{
    const g=DB.sudoku.saved[id],record=DB.sudoku.completed[id],level=g?.level||record.level,current=id===DB.sudoku.game.id;
    const solved=g&&g.values.join('')===g.solution,entries=g?g.values.filter((n,i)=>n&&g.givens[i]==='0').length:0;
    const status=solved?'Completed':g?'In progress · '+entries+' entered':'Completed before · replay available';
    const date=at(id),when=Number.isFinite(Date.parse(date))?fmtDate(date):'Saved puzzle';
    return '<article class="su-saved-row"><div class="su-saved-heading"><strong>'+SUDOKU_LEVELS[level].label+'</strong>'+(current?'<span class="gm-tag">Current</span>':'')+'</div><p>'+escapeHtml(status)+(record&&!solved&&g?' · completed before':'')+'</p><small>'+escapeHtml(when)+' · '+escapeHtml(id)+'</small><div class="su-saved-actions">'+(g?'<button class="btn secondary" type="button" data-su-resume="'+escapeHtml(id)+'"'+(current?' disabled':'')+'>'+(current?'Current puzzle':solved?'View saved':'Continue')+'</button>':'')+'<button class="btn secondary" type="button" data-su-replay="'+escapeHtml(id)+'">Play again</button></div></article>';
  }).join('');
  return '<section class="su-card su-saved"><div class="su-saved-title"><h3>Saved puzzles</h3><span>'+all.length+'</span></div><p class="su-caption">Your puzzles save automatically. Continue a saved board or replay the exact same puzzle.</p><div class="su-saved-list">'+(rows||'<p>Your first puzzle will appear here.</p>')+'</div>'+(pages>1?'<nav class="su-saved-pager" aria-label="Saved puzzle pages"><button class="btn secondary" type="button" id="suSavedPrev"'+(sudokuState.savedPage===0?' disabled':'')+'>← Previous</button><span>'+(sudokuState.savedPage+1)+' / '+pages+'</span><button class="btn secondary" type="button" id="suSavedNext"'+(sudokuState.savedPage===pages-1?' disabled':'')+'>Next →</button></nav>':'')+'</section>';
}
function sudokuSnapshot(){
  const g=DB.sudoku.game;sudokuState.undo.push({values:g.values.slice(),notes:g.notes.slice()});if(sudokuState.undo.length>100)sudokuState.undo.shift();
}
function sudokuConflicts(values){
  const conflicts=new Set();for(let i=0;i<81;i++)if(values[i]&&sudokuPeers(i).some(p=>values[p]===values[i]))conflicts.add(i);return conflicts;
}
function sudokuComplete(){
  const g=DB.sudoku.game;if(g.values.join('')!==g.solution)return false;
  const old=DB.sudoku.completed[g.id];
  if(!old||(old.assisted&&!g.assisted))DB.sudoku.completed[g.id]={at:nowISO(),level:g.level,assisted:!!g.assisted};
  sudokuState.message=g.assisted?'Puzzle complete — reviewed with hints. Well done!':'Puzzle solved independently. Beautiful work!';return true;
}
function sudokuEnter(number){
  const s=sudokuState,g=DB.sudoku.game,index=s.selected;
  if(Number(g.givens[index])){s.message='That is a starting clue. Choose an empty square.';renderSudoku();return;}
  if(g.values.join('')===g.solution){s.message='This puzzle is complete. Start a new one whenever you are ready.';renderSudoku();return;}
  sudokuSnapshot();s.wrong=[];
  if(s.notesMode&&number){g.values[index]=0;g.notes[index]^=1<<(number-1);s.message='Pencil note '+number+' '+(g.notes[index]&(1<<(number-1))?'added.':'removed.');}
  else{g.values[index]=number;g.notes[index]=0;if(number)for(const p of sudokuPeers(index))g.notes[p]&=~(1<<(number-1));s.message=number?'Number '+number+' placed.':'Square cleared.';}
  sudokuComplete();sudokuSave();renderSudoku();sudokuFocusCell();
}
function sudokuFocusCell(){const cell=document.querySelector('[data-su-cell="'+sudokuState.selected+'"]');if(cell)cell.focus({preventScroll:true});}
function sudokuSelect(index){sudokuState.selected=index;renderSudoku();sudokuFocusCell();}
function sudokuKey(event){
  if(/^[1-9]$/.test(event.key)){event.preventDefault();sudokuEnter(Number(event.key));return;}
  if(['Backspace','Delete','0'].includes(event.key)){event.preventDefault();sudokuEnter(0);return;}
  if(event.key.toLowerCase()==='n'){event.preventDefault();sudokuState.notesMode=!sudokuState.notesMode;renderSudoku();sudokuFocusCell();return;}
  const index=sudokuState.selected,step={ArrowLeft:-1,ArrowRight:1,ArrowUp:-9,ArrowDown:9}[event.key];
  if(step===undefined)return;event.preventDefault();const next=index+step;
  if(next<0||next>=81||(Math.abs(step)===1&&Math.floor(next/9)!==Math.floor(index/9)))return;sudokuSelect(next);
}
function sudokuHint(){
  const s=sudokuState,g=DB.sudoku.game;
  let index=s.selected;if(g.givens[index]!=='0'||g.values[index]===Number(g.solution[index]))index=g.values.findIndex((v,i)=>v!==Number(g.solution[i]));
  if(index<0){s.message='You have already completed this puzzle.';renderSudoku();return;}
  sudokuSnapshot();g.assisted=true;g.hints=(g.hints||0)+1;s.selected=index;s.notesMode=false;g.values[index]=Number(g.solution[index]);g.notes[index]=0;
  for(const p of sudokuPeers(index))g.notes[p]&=~(1<<(g.values[index]-1));
  s.wrong=[];s.message='Hint: row '+(Math.floor(index/9)+1)+', column '+(index%9+1)+' is '+g.values[index]+'. This puzzle will count as reviewed with help.';
  sudokuComplete();sudokuSave();renderSudoku();
}
function sudokuCheck(){
  const s=sudokuState,g=DB.sudoku.game;s.wrong=g.values.flatMap((v,i)=>v&&v!==Number(g.solution[i])?[i]:[]);
  if(s.wrong.length)s.message=s.wrong.length+' '+(s.wrong.length===1?'entry needs':'entries need')+' another look. Marked squares are highlighted.';
  else if(!sudokuComplete())s.message='All your filled answers are correct so far. Keep going!';
  sudokuSave();renderSudoku();
}
function sudokuAutoNotes(){
  const s=sudokuState,g=DB.sudoku.game;sudokuSnapshot();g.notes=g.values.map((v,i)=>v?0:sudokuCandidates(g.values,i));s.message='Possible candidates added from the current row, column and box. These are notes, not answers.';sudokuSave();renderSudoku();
}
function sudokuNewPrompt(){
  const level=sudokuState.level,g=DB.sudoku.game;
  const start=()=>{sudokuStart(level);renderSudoku();};
  if((g.values.some((n,i)=>n&&g.givens[i]==='0')||g.notes.some(Boolean))&&g.values.join('')!==g.solution){
    openModal('<h2>Start a fresh Sudoku?</h2><p>Your unfinished puzzle will stay in Saved puzzles, including your numbers and pencil notes.</p><div class="modal-actions"><button class="btn secondary" type="button" id="suKeep">Keep playing</button><button class="btn" type="button" id="suFresh">New puzzle</button></div>');
    document.getElementById('suKeep').onclick=closeModal;document.getElementById('suFresh').onclick=()=>{closeModal();start();};
  }else start();
}
function renderSudoku(){
  gamesRestoreFocusLayout();
  sudokuEnsure();const s=sudokuState,g=DB.sudoku.game,index=s.selected,selected=g.values[index],peers=new Set(sudokuPeers(index)),conflicts=sudokuConflicts(g.values);
  const filled=g.values.filter(Boolean).length,finished=g.values.join('')===g.solution,completed=Object.values(DB.sudoku.completed);
  let cells='';for(let i=0;i<81;i++){
    const row=Math.floor(i/9),col=i%9,value=g.values[i],given=g.givens[i]!=='0',notes=g.notes[i];
    const classes=['su-cell',given?'su-given':'',peers.has(i)?'su-peer':'',selected&&value===selected?'su-same':'',index===i?'su-selected':'',conflicts.has(i)||s.wrong.includes(i)?'su-wrong':'',col===2||col===5?'su-box-right':'',row===2||row===5?'su-box-bottom':''].filter(Boolean).join(' ');
    const label='Row '+(row+1)+', column '+(col+1)+(value?', '+value+(given?', starting clue':''):notes?', notes '+Array.from({length:9},(_,k)=>notes&(1<<k)?k+1:'').filter(Boolean).join(', '):', empty');
    cells+='<button type="button" class="'+classes+'" data-su-cell="'+i+'" tabindex="'+(i===index?'0':'-1')+'" aria-label="'+label+'" aria-pressed="'+(i===index)+'">'+(value?'<span class="su-digit">'+value+'</span>':notes?'<span class="su-notes" aria-hidden="true">'+Array.from({length:9},(_,k)=>'<span>'+(notes&(1<<k)?k+1:'')+'</span>').join('')+'</span>':'')+'</button>';
  }
  document.getElementById('sudokuBody').innerHTML='<div class="su-wrap"><div class="su-layout"><div class="su-main"><div class="su-board-meta"><span>'+SUDOKU_LEVELS[g.level].label+' <span class="gm-tag">'+g.givens.replace(/0/g,'').length+' clues</span></span><span>'+filled+' / 81 filled</span></div><div class="su-board" role="group" aria-label="Sudoku grid. Arrow keys navigate, 1 to 9 enter numbers, N toggles notes.">'+cells+'</div><div class="su-pad" aria-label="Enter a number">'+Array.from({length:9},(_,i)=>{const n=i+1,left=Math.max(0,9-g.values.filter(v=>v===n).length);return '<button type="button" data-su-number="'+n+'" aria-label="Enter '+n+'"'+(finished?' disabled':'')+'><strong>'+n+'</strong><small>'+left+' left</small></button>';}).join('')+'</div><div class="su-quick"><button type="button" class="btn secondary" id="suNotes" aria-pressed="'+s.notesMode+'">✎ Notes '+(s.notesMode?'on':'off')+'</button><button type="button" class="btn secondary" id="suErase">Erase</button><button type="button" class="btn secondary" id="suUndo"'+(s.undo.length?'':' disabled')+'>Undo</button></div><p class="su-status" role="status" aria-live="polite">'+escapeHtml(finished?(g.assisted?'Puzzle complete — reviewed with help.':'Puzzle solved independently. Well done!'):s.message)+'</p></div><aside class="su-aside"><section class="su-card"><span class="gm-eyebrow">ONE SQUARE AT A TIME</span><h2>'+(finished?'You found the pattern.':'Find your next number.')+'</h2><p>Every row, column and 3 × 3 box needs the digits 1–9 exactly once.</p><label class="su-level">Your next puzzle<select id="suLevel">'+Object.entries(SUDOKU_LEVELS).map(([key,v])=>'<option value="'+key+'"'+(key===s.level?' selected':'')+'>'+v.label+' · '+v.clues+' clues</option>').join('')+'</select></label><button type="button" class="btn su-new" id="suNew">New puzzle ↗</button><div class="su-tool-grid"><button type="button" class="btn secondary" id="suCheck">Check answers</button><button type="button" class="btn secondary" id="suHint">One hint</button><button type="button" class="btn secondary" id="suAutoNotes">Auto notes</button></div><p class="su-caption">Hints used: '+(g.hints||0)+' · '+(g.assisted?'Reviewed with help':'Independent attempt')+'</p></section><section class="su-card su-achievements"><h3>Your small victories</h3><div><strong>'+completed.filter(p=>!p.assisted).length+'</strong><span>solved independently</span></div><div><strong>'+completed.filter(p=>p.assisted).length+'</strong><span>reviewed with hints</span></div><p class="su-caption">Your current puzzle saves as you play.</p></section><details class="su-card su-help"><summary>How to play</summary><p>Select an empty square, then use the number pad or your keyboard. Arrow keys move between squares. Backspace erases; N toggles pencil notes.</p><p>Starting clues stay fixed. Matching numbers and related squares light up. Repeated numbers in a row, column or box are marked; Check answers also finds entries that disagree with the solution.</p><p>Use notes to keep possible numbers in a square. Auto notes uses your current entries. Undo restores the previous entries and pencil marks.</p><p>Each puzzle has exactly one solution. Levels are based on starting clue counts; the logical techniques needed can vary. New puzzles mix 200 original layouts into fresh variations.</p><p>Focus view gives the board more room. Press Escape or Exit focus to return. Puzzle and completion progress are included in Study Hub backup and sync.</p></details></aside></div></div>';
  const body=document.getElementById('sudokuBody');
  body.querySelector('.su-aside .su-card').insertAdjacentHTML('beforeend','<div class="su-save-actions"><button class="btn secondary" type="button" id="suSave">Save puzzle</button><button class="btn secondary" type="button" id="suReplay">Play again</button></div>');
  body.querySelector('.su-achievements').insertAdjacentHTML('beforebegin',sudokuSavedHTML());
  body.querySelectorAll('[data-su-cell]').forEach(b=>{b.onclick=()=>sudokuSelect(Number(b.dataset.suCell));b.onkeydown=sudokuKey;});
  body.querySelectorAll('[data-su-number]').forEach(b=>b.onclick=()=>sudokuEnter(Number(b.dataset.suNumber)));
  body.querySelector('#suNotes').onclick=()=>{s.notesMode=!s.notesMode;renderSudoku();};
  body.querySelector('#suErase').onclick=()=>sudokuEnter(0);
  body.querySelector('#suUndo').onclick=()=>{const prev=s.undo.pop();if(!prev)return;g.values=prev.values;g.notes=prev.notes;s.wrong=[];s.message='Last step undone.';sudokuSave();renderSudoku();};
  body.querySelector('#suCheck').onclick=sudokuCheck;body.querySelector('#suHint').onclick=sudokuHint;body.querySelector('#suAutoNotes').onclick=sudokuAutoNotes;
  body.querySelector('#suLevel').onchange=e=>{s.level=e.target.value;};body.querySelector('#suNew').onclick=sudokuNewPrompt;
  body.querySelector('#suSave').onclick=()=>{sudokuSave();s.savedPage=0;s.message='Puzzle saved. Find it in Saved puzzles to continue or play again.';renderSudoku();};
  body.querySelector('#suReplay').onclick=()=>sudokuReplayPrompt();
  body.querySelectorAll('[data-su-resume]').forEach(button=>button.onclick=()=>sudokuOpenSaved(button.dataset.suResume));
  body.querySelectorAll('[data-su-replay]').forEach(button=>button.onclick=()=>sudokuReplayPrompt(button.dataset.suReplay));
  for(const [id,step] of [['suSavedPrev',-1],['suSavedNext',1]]){const button=body.querySelector('#'+id);if(button)button.onclick=()=>{s.savedPage+=step;renderSudoku();document.querySelector('#view-sudoku .su-saved').scrollIntoView({block:'nearest'});};}
  gamesPrepareFocusLayout();gamesScheduleFit();
}
