const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert/strict');
const {Chess}=require('../vendor/chess.js/chess.cjs');
const root=path.resolve(__dirname,'..');
function perft(g,n){if(!n)return 1;let sum=0;for(const m of g.moves({verbose:true})){g.move(m);sum+=perft(g,n-1);g.undo();}return sum;}
assert.equal(perft(new Chess(),3),8902,'Initial move-tree legality');
const castle=new Chess('r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1');
castle.move('O-O');assert.equal(castle.get('f1').type,'r');castle.undo();castle.move('O-O-O');assert.equal(castle.get('d1').type,'r');
const throughCheck=new Chess('r3k2r/8/8/8/8/5r2/8/R3K2R w KQkq - 0 1');assert(!throughCheck.moves().includes('O-O'));
const ep=new Chess();for(const m of ['e4','a6','e5','d5'])ep.move(m);ep.move('exd6');assert(!ep.get('d5'));assert.equal(ep.get('d6').type,'p');
const pinnedEP=new Chess('4r1k1/8/8/3pP3/8/8/8/4K3 w - d6 0 1');assert(!pinnedEP.moves().includes('exd6'));
const promotion=new Chess('7k/P7/8/8/8/8/8/7K w - - 0 1');
assert.equal(promotion.moves({square:'a7',verbose:true}).filter(m=>m.to==='a8').length,4);promotion.move({from:'a7',to:'a8',promotion:'n'});assert.equal(promotion.get('a8').type,'n');
const mate=new Chess();for(const m of ['f3','e5','g4','Qh4#'])mate.move(m);assert(mate.isCheckmate());
assert(new Chess('7k/5Q2/6K1/8/8/8/8/8 b - - 0 1').isStalemate());
assert(new Chess('7k/8/8/8/8/8/8/K7 w - - 0 1').isInsufficientMaterial());
const rep=new Chess();for(const m of ['Nf3','Nf6','Ng1','Ng8','Nf3','Nf6','Ng1','Ng8'])rep.move(m);assert(rep.isThreefoldRepetition());
assert(new Chess('7k/8/8/8/8/8/R7/K7 w - - 100 70').isDrawByFiftyMoves());
const worker=fs.readFileSync(path.join(root,'scripts/chess-bot.js'),'utf8');
function bot(fen,level){let result;const self={StudyHubChessRules:{Chess},postMessage:m=>result=m};vm.runInNewContext(worker+';chessBotWorker();',{self,Date});self.onmessage({data:{fen,level}});assert(result&&result.move,'Bot returned a move');const g=new Chess(fen);g.move(result.move);return g;}
const win=new Chess();for(const m of ['f3','e5','g4'])win.move(m);for(const level of ['casual','club','challenge'])assert(bot(win.fen(),level).isCheckmate(),'Bot must find mate in one');
for(const level of ['casual','club','challenge'])bot(new Chess().fen(),level);
const html=fs.readFileSync(path.join(root,'study-hub.html'),'utf8');
const raw=JSON.parse(html.match(/<script id="chessPuzzleData" type="application\/json">([\s\S]*?)<\/script>/)[1]);
assert.equal(raw.puzzles.length,10000);const seen=new Set(),counts={1:0,2:0,3:0};
for(const [id,fen,line,,n] of raw.puzzles){
  const position=fen.split(' ').slice(0,4).join(' ');
  assert(!seen.has(position));seen.add(position);const g=new Chess(fen),moves=line.split(' ');assert.equal(moves.length,2*n-1);
  for(const u of moves){assert(!g.isGameOver(),id);g.move({from:u.slice(0,2),to:u.slice(2,4),...(u[4]?{promotion:u[4]}:{})});}
  assert(g.isCheckmate(),id);counts[n]++;
}
assert.deepEqual(counts,{1:4000,2:4000,3:2000});
console.log('PASS: perft8902, castling/through-check, en passant/pin, all promotions, mate/stalemate/repetition/draw; all bot levels legal and find mate; every one of 10,000 unique puzzle lines ends in legal checkmate.');
