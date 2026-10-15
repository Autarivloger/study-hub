const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {sudokuSolve,sudokuCandidates,sudokuTransform,SUDOKU_LEVELS}=require('../scripts/sudoku-core.js');
// Independent, simple MRV solver to verify the generated bank, not only its own generator.
function independentCount(text){
  const grid=text.split('').map(Number);let count=0;
  function possible(i,n){const r=Math.floor(i/9),c=i%9;for(let p=0;p<81;p++)if(grid[p]===n&&(Math.floor(p/9)===r||p%9===c||(Math.floor(p/27)===Math.floor(r/3)&&Math.floor(p%9/3)===Math.floor(c/3))))return false;return true;}
  function search(){let idx=-1,options=null;for(let i=0;i<81;i++)if(!grid[i]){const ns=[1,2,3,4,5,6,7,8,9].filter(n=>possible(i,n));if(!ns.length)return;if(!options||ns.length<options.length){idx=i;options=ns;if(ns.length===1)break;}}if(idx<0){count++;return;}for(const n of options){grid[idx]=n;search();grid[idx]=0;if(count>=2)return;}}
  search();return count;
}
const bank=JSON.parse(fs.readFileSync(path.resolve(__dirname,'../data/sudoku/puzzles.json'),'utf8')).puzzles;
assert.equal(bank.length,200);const ids=new Set(),layouts=new Set(),counts={easy:0,medium:0,hard:0,expert:0};
for(const [id,level,puzzle,solution] of bank){
  assert(!ids.has(id));ids.add(id);assert(!layouts.has(puzzle));layouts.add(puzzle);counts[level]++;
  assert.equal(puzzle.replace(/0/g,'').length,SUDOKU_LEVELS[level].clues);
  assert.equal(independentCount(puzzle),1,id+' unique solution');assert.equal(sudokuSolve(puzzle).solution.join(''),solution);
  for(let i=0;i<81;i++)if(puzzle[i]!=='0')assert.equal(puzzle[i],solution[i]);
  const transformed=sudokuTransform(puzzle,solution,123456789);
  assert.equal(independentCount(transformed.givens.join('')),1);assert.equal(sudokuSolve(transformed.givens).solution.join(''),transformed.solution.join(''));
  const blank=puzzle.indexOf('0');assert(sudokuCandidates(puzzle.split('').map(Number),blank)&(1<<(Number(solution[blank])-1)));
}
assert.deepEqual(counts,{easy:50,medium:50,hard:50,expert:50});
assert.equal(sudokuSolve('11'+'0'.repeat(79)).count,0);assert.equal(sudokuSolve('0'.repeat(81)).count,2);assert.equal(sudokuSolve('x'.repeat(81)).count,0);
console.log('PASS: independently verified 200 original puzzles and 200 transformed variants, unique solutions, all levels/clue counts, candidates, invalid/ambiguous board handling.');
