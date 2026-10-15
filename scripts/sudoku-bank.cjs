/* Authoring only. Generate and independently recheck original unique puzzles. */
const fs=require('fs'),path=require('path'),assert=require('assert/strict');
const {SUDOKU_LEVELS,sudokuSolve,sudokuTransform,sudokuShuffle,sudokuRandom}=require('./sudoku-core.js');
const random=sudokuRandom(20261017),bank=[];
const base=Array.from({length:81},(_,i)=>{const r=Math.floor(i/9),c=i%9;return (r*3+Math.floor(r/3)+c)%9+1;}).join('');
for(const [level,info] of Object.entries(SUDOKU_LEVELS)){
  let attempts=0;
  while(bank.filter(p=>p[1]===level).length<50){
    if(++attempts>3000)throw Error('Generation quota not reached');
    const solution=sudokuTransform(base,base,Math.floor(random()*0xffffffff)).solution;
    const puzzle=solution.slice();let clues=81;
    for(const i of sudokuShuffle(Array.from({length:81},(_,i)=>i),random)){
      if(clues===info.clues)break;const previous=puzzle[i];puzzle[i]=0;
      if(sudokuSolve(puzzle,2).count!==1)puzzle[i]=previous;else clues--;
    }
    if(clues!==info.clues)continue;
    const text=puzzle.join('');if(bank.some(p=>p[2]===text))continue;
    const check=sudokuSolve(puzzle,2);assert.equal(check.count,1);assert.equal(check.solution.join(''),solution.join(''));
    bank.push(['sh'+String(bank.length+1).padStart(3,'0'),level,text,solution.join('')]);
  }
  console.log('Generated 50 '+level+' unique-solution puzzles ('+info.clues+' clues).');
}
const output=path.resolve(__dirname,'../data/sudoku/puzzles.json');fs.mkdirSync(path.dirname(output),{recursive:true});
fs.writeFileSync(output,JSON.stringify({source:'Original Study Hub puzzles',puzzles:bank}));
