/* Runs in a disposable Worker. No network, DOM, or learner data. */
function chessBotWorker(){
  self.onmessage=function(event){
    const {fen,level}=event.data;
    const game=new self.StudyHubChessRules.Chess(fen);
    const limits={casual:[1,180],club:[3,650],challenge:[4,1800]};
    const [maxDepth,ms]=limits[level]||limits.club;
    const deadline=Date.now()+ms, values={p:100,n:320,b:335,r:500,q:900,k:0};
    const timeout={};let nodes=0;
    function ordered(){
      return game.moves({verbose:true}).sort((a,b)=>rank(b)-rank(a));
    }
    function rank(m){return (m.captured?10*values[m.captured]-values[m.piece]:0)+(m.promotion?values[m.promotion]:0)+(m.san.includes('+')?40:0)+(m.san.includes('#')?100000:0);}
    function evaluation(){
      let score=0;
      for(const row of game.board())for(const p of row)if(p){
        const file=p.square.charCodeAt(0)-97,rank=Number(p.square[1])-1;
        const forward=p.color==='w'?rank:7-rank;
        const center=7-Math.abs(file-3.5)-Math.abs(rank-3.5);
        const position=p.type==='p'?forward*7+center*2:p.type==='k'?-center*3:center*8;
        score+=(p.color==='w'?1:-1)*(values[p.type]+position);
      }
      return score*(game.turn()==='w'?1:-1);
    }
    function search(depth,alpha,beta,ply,quiet){
      if((++nodes&31)===0&&Date.now()>=deadline)throw timeout;
      const moves=ordered();
      if(!moves.length)return game.isCheck()?-100000+ply:0;
      if(game.isDraw())return 0;
      const check=game.isCheck();
      if(depth<=0){
        if(quiet<=0)return evaluation();
        if(!check){const stand=evaluation();if(stand>=beta)return stand;alpha=Math.max(alpha,stand);}
      }
      const candidates=depth>0||check?moves:moves.filter(m=>m.captured||m.promotion);
      for(const m of candidates){
        game.move(m);let score;
        try{score=-search(depth-1,-beta,-alpha,ply+1,depth<=0?quiet-1:quiet);}finally{game.undo();}
        if(score>=beta)return score;
        alpha=Math.max(alpha,score);
      }
      return alpha;
    }
    const legal=ordered();
    if(!legal.length){self.postMessage({fen,move:null});return;}
    // An immediate mate must never be missed, even at the lightest setting.
    for(const m of legal){game.move(m);const mate=game.isCheckmate();game.undo();if(mate){self.postMessage({fen,move:{from:m.from,to:m.to,promotion:m.promotion}});return;}}
    let best=legal[0],completedDepth=0;
    for(let depth=1;depth<=maxDepth;depth++){
      let candidate=best,bestScore=-Infinity;
      const sorted=[best,...legal.filter(m=>m!==best)];
      try{
        for(const m of sorted){
          if(Date.now()>=deadline)throw timeout;
          game.move(m);let score;
          try{score=-search(depth-1,-Infinity,-bestScore,1,2);}finally{game.undo();}
          if(score>bestScore){bestScore=score;candidate=m;}
        }
        best=candidate;completedDepth=depth;
      }catch(error){if(error!==timeout)throw error;break;}
    }
    self.postMessage({fen,move:{from:best.from,to:best.to,promotion:best.promotion},depth:completedDepth,nodes});
  };
}
