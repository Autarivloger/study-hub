/* Embed Games + original Sudoku without changing existing learning content. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict'),vm=require('vm');
const root=path.resolve(__dirname,'..'),target=path.join(root,'study-hub.html');
const read=p=>fs.readFileSync(path.join(root,p),'utf8').replace(/\r\n/g,'\n');
let html=read('study-hub.html');
function once(before,after){assert.equal(html.split(before).length,2,'Expected one Games integration target: '+before.slice(0,90));html=html.replace(before,()=>after);}
const css='/* STUDY HUB GAMES CSS START */\n'+['scripts/games.css','scripts/sokoban.css','scripts/sudoku-saved.css','scripts/games-focus.css'].map(read).join('\n')+'\n/* STUDY HUB GAMES CSS END */';
const app='/* STUDY HUB GAMES APP START */\n'+['scripts/sudoku-core.js','scripts/games-app.js','scripts/sudoku-app.js','scripts/sokoban-app.js'].map(read).join('\n')+'\n/* STUDY HUB GAMES APP END */';
const data='<!-- STUDY HUB SUDOKU DATA START -->\n<script id="sudokuPuzzleData" type="application/json">'+read('data/sudoku/puzzles.json')+'</script>\n<!-- STUDY HUB SUDOKU DATA END -->';
if(!html.includes('/* STUDY HUB GAMES APP START */')){
  once('</style>\n</head>',css+'\n</style>\n</head>');
  once('id="chessHeadBtn" data-view="chess" title="Play Chess">♟ Chess','id="chessHeadBtn" data-view="games" title="Open Games">▦ Games');
  once('<button type="button" data-view="chess"><span class="ic">♟</span>Chess</button>','<button type="button" data-view="games"><span class="ic">▦</span>Games</button>');
  once('<button type="button" class="nav-item" data-view="chess"><span class="ic">♟</span>Chess</button>','<button type="button" class="nav-item" data-view="games"><span class="ic">▦</span>Games</button>');
  once('    <!-- CHESS VIEW -->','    <!-- GAMES HUB -->\n    <div class="view" id="view-games">\n      <div class="pane-header gm-header"><h1>Games</h1><span class="gm-tag">Play at your pace</span></div>\n      <div id="gamesBody"></div>\n    </div>\n    <div class="view" id="view-sudoku">\n      <div class="pane-header gm-header"><button type="button" class="btn secondary gm-crumb" data-view="games">← Games</button><h1>Sudoku</h1><button type="button" class="btn secondary gm-crumb" data-game-focus aria-pressed="false">Focus view ↗</button></div>\n      <div id="sudokuBody"></div>\n    </div>\n\n    <!-- CHESS VIEW -->');
  once('<div class="pane-header"><h1>♟ Chess</h1></div>','<div class="pane-header gm-header"><button type="button" class="btn secondary gm-crumb" data-view="games">← Games</button><h1>Chess</h1><button type="button" class="btn secondary gm-crumb" data-game-focus aria-pressed="false">Focus view ↗</button></div>');
  once('const views = ["chess",','const views = ["games","sudoku","chess",');
  once('function switchView(name){','function switchView(name){\n  const navigationName=["chess","sudoku"].includes(name)?"games":name;');
  once('b.dataset.view===name));\n  document.querySelectorAll("#tabnav button")','b.dataset.view===navigationName));\n  document.querySelectorAll("#tabnav button")');
  once('b.dataset.view===name));\n  document.getElementById("brandTitle")','b.dataset.view===navigationName));\n  document.getElementById("brandTitle")');
  once('{chess:"Chess", course:','{games:"Games", sudoku:"Sudoku", chess:"Chess", course:');
  once('  if(name!=="chess") chessLeave();','  gamesNavigate(name);\n  if(name==="games") renderGames();\n  if(name==="sudoku") renderSudoku();\n  if(name!=="chess") chessLeave();');
  once('  d.chess = chessDefaults(d.chess);','  d.sudoku = sudokuDefaults(d.sudoku);\n  d.chess = chessDefaults(d.chess);');
  once('  chessMerge(incoming.chess);','  sudokuMerge(incoming.sudoku);\n  chessMerge(incoming.chess);');
  once('function renderEverything(){','function renderEverything(){\n  if(document.getElementById("view-games").classList.contains("active"))renderGames();\n  if(document.getElementById("view-sudoku").classList.contains("active"))renderSudoku();');
  once('<!-- STUDY HUB CHESS ASSETS START -->',data+'\n<!-- STUDY HUB CHESS ASSETS START -->');
  once('\nboot();\n','\n'+app+'\n\ndocument.querySelectorAll("[data-game-focus]").forEach(function(button){button.onclick=gamesFocus;});\n\nboot();\n');
}else{
  html=html.replace(/\/\* STUDY HUB GAMES CSS START \*\/[\s\S]*?\/\* STUDY HUB GAMES CSS END \*\//,()=>css);
  html=html.replace(/\/\* STUDY HUB GAMES APP START \*\/[\s\S]*?\/\* STUDY HUB GAMES APP END \*\//,()=>app);
  html=html.replace(/<!-- STUDY HUB SUDOKU DATA START -->[\s\S]*?<!-- STUDY HUB SUDOKU DATA END -->/,()=>data);
}
const sokoCore=require('./sokoban-core.js'),sokoData=JSON.parse(read('data/sokoban/levels.json'));
assert.equal(sokoData.levels.length,40);
for(const level of sokoData.levels){const board=sokoCore.sokoParse(level.map);let position=board.start;for(const direction of level.solution){position=sokoCore.sokoStep(board,position,direction);assert(position,level.id);}assert(sokoCore.sokoWon(board,position),level.id);}
const sokobanAssets='<!-- STUDY HUB SOKOBAN ASSETS START -->\n<script id="sokobanRules">\n'+read('scripts/sokoban-core.js')+'\n</script>\n<script id="sokobanLevelData" type="application/json">'+read('data/sokoban/levels.json')+'</script>\n<!-- STUDY HUB SOKOBAN ASSETS END -->';
if(!html.includes('id="view-sokoban"')){
  once('    <!-- CHESS VIEW -->','    <div class="view" id="view-sokoban">\n      <div class="pane-header gm-header"><button type="button" class="btn secondary gm-crumb" data-view="games">← Games</button><h1>Sokoban</h1><button type="button" class="btn secondary gm-crumb" data-game-focus aria-pressed="false">Focus view ↗</button></div>\n      <div id="sokobanBody"></div>\n    </div>\n\n    <!-- CHESS VIEW -->');
  once('const views = ["games",','const views = ["games","sokoban",');
  once('const navigationName=["chess","sudoku"]','const navigationName=["chess","sudoku","sokoban"]');
  once('{games:"Games", sudoku:','{games:"Games", sokoban:"Sokoban", sudoku:');
  once('  gamesNavigate(name);','  gamesNavigate(name);\n  if(name!=="sokoban")sokoCancelHint();\n  if(name==="sokoban")renderSokoban();');
  once('  d.sudoku = sudokuDefaults(d.sudoku);','  d.sokoban = sokoDefaults(d.sokoban);\n  d.sudoku = sudokuDefaults(d.sudoku);');
  once('  sudokuMerge(incoming.sudoku);','  sokoMerge(incoming.sokoban);\n  sudokuMerge(incoming.sudoku);');
  once('function renderEverything(){','function renderEverything(){\n  if(document.getElementById("view-sokoban").classList.contains("active"))renderSokoban();');
  once('<!-- STUDY HUB SUDOKU DATA START -->',sokobanAssets+'\n<!-- STUDY HUB SUDOKU DATA START -->');
}else html=html.replace(/<!-- STUDY HUB SOKOBAN ASSETS START -->[\s\S]*?<!-- STUDY HUB SOKOBAN ASSETS END -->/,()=>sokobanAssets);
for(const match of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/application\/json/.test(match[1]))new vm.Script(match[2]);
fs.writeFileSync(target+'.tmp',html,'utf8');
for(let attempt=0;;attempt++){
  try{fs.renameSync(target+'.tmp',target);break;}
  catch(error){if(error.code!=='EPERM'||attempt>=8)throw error;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,150);}
}
console.log('Games, Sudoku and 40 verified Sokoban levels embedded; all executable scripts parsed.');
