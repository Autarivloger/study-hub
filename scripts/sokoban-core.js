/* Original Sokoban rules and bounded push-space solver. No external assets. */
function sokoDirections(){return {U:[0,-1],D:[0,1],L:[-1,0],R:[1,0]};}
function sokoParse(rows){
  if(!Array.isArray(rows)||!rows.length)throw Error('Missing level');
  const width=Math.max(...rows.map(r=>r.length)),height=rows.length,walls=new Set(),goals=new Set(),boxes=[];let player=-1;
  for(let y=0;y<height;y++)for(let x=0;x<width;x++){
    const ch=rows[y][x]||'#',i=y*width+x;
    if(!'# .$@*+'.includes(ch))throw Error('Unknown tile');
    if(ch==='#')walls.add(i);if('.+*'.includes(ch))goals.add(i);if('$*'.includes(ch))boxes.push(i);
    if('@+'.includes(ch)){if(player!==-1)throw Error('Multiple players');player=i;}
    if((x===0||x===width-1||y===0||y===height-1)&&ch!=='#')throw Error('Level must be enclosed');
  }
  if(player<0||!boxes.length||boxes.length!==goals.size)throw Error('Invalid player/box/goal counts');
  return {width,height,walls,goals,start:{player,boxes:boxes.sort((a,b)=>a-b),pushes:0}};
}
function sokoNeighbour(board,index,direction){
  const d=sokoDirections()[direction];if(!d)return -1;
  const x=index%board.width+d[0],y=Math.floor(index/board.width)+d[1];
  return x<0||y<0||x>=board.width||y>=board.height?-1:y*board.width+x;
}
function sokoFloor(board,index){return index>=0&&index<board.width*board.height&&!board.walls.has(index);}
function sokoStep(board,state,direction){
  const next=sokoNeighbour(board,state.player,direction);if(!sokoFloor(board,next))return null;
  const boxes=state.boxes.slice(),index=boxes.indexOf(next);let pushed=false;
  if(index>=0){const beyond=sokoNeighbour(board,next,direction);if(!sokoFloor(board,beyond)||boxes.includes(beyond))return null;boxes[index]=beyond;pushed=true;}
  return {player:next,boxes:boxes.sort((a,b)=>a-b),pushes:(state.pushes||0)+(pushed?1:0)};
}
function sokoWon(board,state){return state.boxes.every(i=>board.goals.has(i));}
function sokoReach(board,state){
  const occupied=new Set(state.boxes),paths=new Map([[state.player,'']]),queue=[state.player];
  for(let h=0;h<queue.length;h++){const p=queue[h];for(const direction of 'UDLR'){const n=sokoNeighbour(board,p,direction);if(sokoFloor(board,n)&&!occupied.has(n)&&!paths.has(n)){paths.set(n,paths.get(p)+direction);queue.push(n);}}}
  return paths;
}
function sokoDeadSquares(board){
  const safe=new Set(board.goals),queue=[...safe];
  for(let h=0;h<queue.length;h++)for(const d of 'UDLR'){
    const previous=sokoNeighbour(board,queue[h],d),behind=sokoNeighbour(board,previous,d);
    if(sokoFloor(board,previous)&&sokoFloor(board,behind)&&!safe.has(previous)){safe.add(previous);queue.push(previous);}
  }
  return new Set(Array.from({length:board.width*board.height},(_,i)=>i).filter(i=>sokoFloor(board,i)&&!safe.has(i)));
}
function sokoSolve(board,start,options={}){
  const maxStates=options.maxStates||40000,deadline=Date.now()+(options.maxMs||1500),dead=sokoDeadSquares(board);
  if(start.boxes.some(p=>dead.has(p)))return {status:'impossible',path:null,states:0};
  const initial=sokoReach(board,start),key=(s,reach)=>s.boxes.join(',')+'|'+Math.min(...reach.keys());
  const seen=new Set([key(start,initial)]),queue=[{state:start,path:'',reach:initial}];
  for(let h=0;h<queue.length;h++){
    if(h>=maxStates||Date.now()>deadline)return {status:'limit',path:null,states:h};
    const node=queue[h];if(sokoWon(board,node.state))return {status:'solved',path:node.path,pushes:node.state.pushes-(start.pushes||0),states:h};
    const occupied=new Set(node.state.boxes);
    for(const box of node.state.boxes)for(const direction of 'UDLR'){
      const opposite={U:'D',D:'U',L:'R',R:'L'}[direction],behind=sokoNeighbour(board,box,opposite),dest=sokoNeighbour(board,box,direction);
      if(!node.reach.has(behind)||!sokoFloor(board,dest)||occupied.has(dest)||dead.has(dest))continue;
      const state={player:box,boxes:node.state.boxes.map(p=>p===box?dest:p).sort((a,b)=>a-b),pushes:(node.state.pushes||0)+1};
      const reach=sokoReach(board,state),id=key(state,reach);if(seen.has(id))continue;seen.add(id);
      queue.push({state,reach,path:node.path+node.reach.get(behind)+direction});
      if(queue.length>maxStates*3)return {status:'limit',path:null,states:h};
    }
  }
  return {status:'impossible',path:null,states:queue.length};
}
if(typeof module==='object'&&module.exports)module.exports={sokoParse,sokoNeighbour,sokoFloor,sokoStep,sokoWon,sokoReach,sokoDeadSquares,sokoSolve};
