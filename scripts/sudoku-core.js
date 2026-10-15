/* Original Study Hub Sudoku utilities: no external API, assets or credentials. */
const SUDOKU_LEVELS={easy:{label:'Easy',clues:40},medium:{label:'Medium',clues:34},hard:{label:'Hard',clues:29},expert:{label:'Expert',clues:25}};
function sudokuPeers(index){
  const row=Math.floor(index/9),col=index%9,peers=[];
  for(let i=0;i<81;i++)if(i!==index&&(Math.floor(i/9)===row||i%9===col||(Math.floor(i/27)===Math.floor(row/3)&&Math.floor(i%9/3)===Math.floor(col/3))))peers.push(i);
  return peers;
}
function sudokuCandidates(values,index){
  if(values[index])return 0;
  let mask=511;for(const peer of sudokuPeers(index))if(values[peer])mask&=~(1<<(values[peer]-1));return mask;
}
function sudokuSolve(input,limit=2){
  const values=Array.isArray(input)?input.slice():String(input).split('').map(Number);
  if(values.length!==81||values.some(n=>!Number.isInteger(n)||n<0||n>9))return {count:0,solution:null};
  const rows=Array(9).fill(0),cols=Array(9).fill(0),boxes=Array(9).fill(0);let count=0,solution=null,nodes=0;
  for(let i=0;i<81;i++)if(values[i]){const r=Math.floor(i/9),c=i%9,b=Math.floor(r/3)*3+Math.floor(c/3),bit=1<<(values[i]-1);if((rows[r]|cols[c]|boxes[b])&bit)return {count:0,solution:null};rows[r]|=bit;cols[c]|=bit;boxes[b]|=bit;}
  function search(){
    nodes++;let best=-1,bestMask=0,bestCount=10;
    for(let i=0;i<81;i++)if(!values[i]){
      const r=Math.floor(i/9),c=i%9,b=Math.floor(r/3)*3+Math.floor(c/3),mask=511&~(rows[r]|cols[c]|boxes[b]);
      let n=0;for(let x=mask;x;x&=x-1)n++;
      if(!n)return;if(n<bestCount){best=i;bestMask=mask;bestCount=n;if(n===1)break;}
    }
    if(best<0){count++;if(!solution)solution=values.slice();return;}
    const r=Math.floor(best/9),c=best%9,b=Math.floor(r/3)*3+Math.floor(c/3);
    for(let n=1;n<=9;n++){const bit=1<<(n-1);if(!(bestMask&bit))continue;
      values[best]=n;rows[r]|=bit;cols[c]|=bit;boxes[b]|=bit;search();values[best]=0;rows[r]&=~bit;cols[c]&=~bit;boxes[b]&=~bit;if(count>=limit)return;
    }
  }
  search();return {count,solution,nodes};
}
function sudokuRandom(seed){
  let state=seed>>>0;
  return ()=>{state+=0x6D2B79F5;let t=state;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};
}
function sudokuShuffle(array,random){
  const out=array.slice();for(let i=out.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;
}
function sudokuTransform(puzzle,solution,seed){
  const random=sudokuRandom(seed),digits=[0,...sudokuShuffle([1,2,3,4,5,6,7,8,9],random)],groups=[0,1,2];
  const order=()=>sudokuShuffle(groups,random).flatMap(g=>sudokuShuffle(groups,random).map(i=>g*3+i));
  const rows=order(),cols=order(),transpose=random()<0.5;
  const transform=grid=>Array.from({length:81},(_,i)=>{const r=rows[Math.floor(i/9)],c=cols[i%9];return digits[Number(grid[transpose?c*9+r:r*9+c])];});
  return {givens:transform(puzzle),solution:transform(solution)};
}
if(typeof module==='object'&&module.exports)module.exports={SUDOKU_LEVELS,sudokuPeers,sudokuCandidates,sudokuSolve,sudokuRandom,sudokuShuffle,sudokuTransform};
