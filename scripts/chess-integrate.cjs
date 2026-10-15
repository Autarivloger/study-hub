/* Authoring command. The distributed study-hub.html remains self-contained. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const root=path.resolve(__dirname,'..');
const {Chess}=require('../vendor/chess.js/chess.cjs');
const read=p=>fs.readFileSync(path.join(root,p),'utf8');
const raw=JSON.parse(read('data/chess/puzzles-source.json'));
const seen=new Set(),ids=new Set(),counts={1:0,2:0,3:0};
const puzzles=raw.puzzles.map(([id,fen,moves,rating,mate])=>{
  assert(!ids.has(id));ids.add(id);
  const game=new Chess(fen),line=moves.split(' ');
  const play=uci=>game.move({from:uci.slice(0,2),to:uci.slice(2,4),...(uci[4]?{promotion:uci[4]}:{})});
  play(line.shift());const start=game.fen();
  const position=start.split(' ').slice(0,4).join(' ');
  assert(!seen.has(position),'Duplicate puzzle position: '+id);seen.add(position);
  assert(!game.isGameOver());assert.equal(line.length,2*mate-1);
  for(const move of line){assert(!game.isGameOver());play(move);}
  assert(game.isCheckmate(),'Not checkmate: '+id);counts[mate]++;
  return [id,start,line.join(' '),rating,mate];
});
assert.equal(puzzles.length,10000);assert.deepEqual(counts,{1:4000,2:4000,3:2000});
const data=JSON.stringify({license:'CC0-1.0',source:'https://database.lichess.org/#puzzles',puzzles});
const css=read('scripts/chess.css');
const app=read('scripts/chess-bot.js')+'\n'+read('scripts/chess-app.js');
const license=read('vendor/chess.js/LICENSE');
const rules=read('vendor/chess.js/chess.cjs').replace(/\/\/# sourceMappingURL=.*$/m,'').replace(/^[ \t]+/gm,s=>s.replace(/\t/g,'  '));
const assets='<!-- STUDY HUB CHESS ASSETS START -->\n<script id="chessRules">\n/* chess.js 1.4.0 · BSD-2-Clause\n'+license+'\n*/\nwindow.StudyHubChessRules=(function(){const exports={};\n'+rules+'\nreturn exports;})();\n</script>\n<script id="chessPuzzleData" type="application/json">'+data+'</script>\n<!-- STUDY HUB CHESS ASSETS END -->\n';
const target=path.join(root,'study-hub.html');let html=read('study-hub.html');
function once(from,to){assert.equal(html.split(from).length,2,'Expected one integration target: '+from.slice(0,85));html=html.replace(from,()=>to);}
if(!html.includes('<!-- STUDY HUB CHESS ASSETS START -->')){
  once('</style>\n</head>','/* STUDY HUB CHESS CSS START */\n'+css+'\n/* STUDY HUB CHESS CSS END */\n</style>\n</head>');
  once('  <button type="button" class="icon-btn" id="typingHeadBtn"','  <button type="button" class="icon-btn" id="chessHeadBtn" data-view="chess" title="Play Chess">♟ Chess</button>\n  <button type="button" class="icon-btn" id="typingHeadBtn"');
  once('<nav id="tabnav" aria-label="Sections">','<nav id="tabnav" aria-label="Sections">\n  <button type="button" data-view="chess"><span class="ic">♟</span>Chess</button>');
  once('  <div id="sidebar">','  <div id="sidebar">\n    <button type="button" class="nav-item" data-view="chess"><span class="ic">♟</span>Chess</button>');
  once('    <!-- TYPING VIEW -->','    <!-- CHESS VIEW -->\n    <div class="view" id="view-chess">\n      <div class="pane-header"><h1>♟ Chess</h1></div>\n      <div id="chessBody"></div>\n    </div>\n\n    <!-- TYPING VIEW -->');
  once('const views = ["course",','const views = ["chess","course",');
  once('{course:"Python Course", lessons:','{chess:"Chess", course:"Python Course", lessons:');
  once('  if(name!=="typing") typingLeave();','  if(name!=="chess") chessLeave();\n  if(name==="chess") renderChess();\n  if(name!=="typing") typingLeave();');
  once('  d.typingHistory = d.typingHistory || [];','  d.chess = chessDefaults(d.chess); // Additive: saved match and independent puzzle completions.\n  d.typingHistory = d.typingHistory || [];');
  once('  habitMerge(incoming.habitTracker);','  chessMerge(incoming.chess);\n  habitMerge(incoming.habitTracker);');
  once('function renderEverything(){','function renderEverything(){\n  chessLeave();\n  if(document.getElementById("view-chess").classList.contains("active")){ chessRestore(); renderChess(); }');
  once('\nboot();\n','\n/* STUDY HUB CHESS APP START */\n'+app+'\n/* STUDY HUB CHESS APP END */\n\nboot();\n');
  // Load rules before the existing app closure, with no external requests.
  const first=html.indexOf('<script>');assert(first>0);html=html.slice(0,first)+assets+html.slice(first);
}else{
  html=html.replace(/<!-- STUDY HUB CHESS ASSETS START -->[\s\S]*?<!-- STUDY HUB CHESS ASSETS END -->\n/,()=>assets);
  html=html.replace(/\/\* STUDY HUB CHESS CSS START \*\/[\s\S]*?\/\* STUDY HUB CHESS CSS END \*\//,()=>'/* STUDY HUB CHESS CSS START */\n'+css+'\n/* STUDY HUB CHESS CSS END */');
  html=html.replace(/\/\* STUDY HUB CHESS APP START \*\/[\s\S]*?\/\* STUDY HUB CHESS APP END \*\//,()=>'/* STUDY HUB CHESS APP START */\n'+app+'\n/* STUDY HUB CHESS APP END */');
}
// Parse every executable inline script before replacing the real file.
let scripts=0;
for(const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){
  if(/application\/json/.test(match[1]))continue;
  new (require('vm').Script)(match[2]);scripts++;
}
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Validated and embedded '+puzzles.length+' unique mate puzzles '+JSON.stringify(counts)+'; '+scripts+' scripts parsed.');
