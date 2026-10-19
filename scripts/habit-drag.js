function habitBindDrag(pane,month){
  pane.querySelectorAll('[data-habit-drag]').forEach(handle=>{
    handle.onkeydown=e=>{
      if(!['ArrowUp','ArrowDown'].includes(e.key))return;
      e.preventDefault();
      const ids=habitRows(month).map(item=>item.id),from=ids.indexOf(handle.dataset.habitDrag),to=from+(e.key==='ArrowUp'?-1:1);
      if(to<0 || to>=ids.length)return;
      [ids[from],ids[to]]=[ids[to],ids[from]];habitSaveOrder(month,ids);
      const next=pane.querySelector('[data-habit-drag="'+handle.dataset.habitDrag+'"]');
      next.focus({preventScroll:true});
      next.scrollIntoView({block:'nearest',inline:'nearest'});
    };
    handle.onpointerdown=e=>{
      if(e.button!==0 || !e.isPrimary)return;
      e.preventDefault();
      const row=handle.closest('[data-habit-row]'),body=row.parentElement,grid=pane.querySelector('.ht-table-scroll'),startY=e.clientY;
      let moved=false,finished=false,frame=0,lastTime=0,pointerY=e.clientY;
      handle.focus({preventScroll:true});
      grid.setPointerCapture(e.pointerId);
      function visibleBounds(){
        let headerBottom=0;
        for(const id of ['topbar','tabnav']){
          const header=document.getElementById(id);
          if(header && header.getClientRects().length)headerBottom=Math.max(headerBottom,header.getBoundingClientRect().bottom);
        }
        const bounds=grid.getBoundingClientRect();
        return {top:Math.max(bounds.top+2,headerBottom+4),bottom:Math.min(bounds.bottom-2,innerHeight-8)};
      }
      function reorder(){
        const bounds=visibleBounds();
        if(bounds.bottom<=bounds.top)return;
        const y=Math.max(bounds.top,Math.min(pointerY,bounds.bottom));
        const target=[...body.children].find(other=>{
          if(other===row)return false;
          const rect=other.getBoundingClientRect();
          return y<rect.top+rect.height/2;
        });
        if(target!==row.nextElementSibling && (target || row!==body.lastElementChild))body.insertBefore(row,target||null);
      }
      function tick(time){
        frame=0;
        if(finished)return;
        if(!grid.isConnected){finish({type:'pointercancel'});return;}
        const dt=Math.min(32,lastTime?time-lastTime:16);lastTime=time;
        const bounds=visibleBounds(),zone=Math.min(52,(bounds.bottom-bounds.top)/3);
        let speed=0;
        if(zone>0){
          if(pointerY<bounds.top+zone)speed=-Math.min(1,(bounds.top+zone-pointerY)/zone);
          else if(pointerY>bounds.bottom-zone)speed=Math.min(1,(pointerY-bounds.bottom+zone)/zone);
        }
        if(speed){
          const distance=speed*dt*.75,previous=grid.scrollTop;
          grid.scrollTop+=distance;
          // Once this scroll container reaches its end, continue with the page.
          // Use the visible screen edge, including the sticky navigation above.
          if(Math.abs(grid.scrollTop-previous)<.5){
            const page=document.scrollingElement;
            if(page)page.scrollTop+=distance;
          }
        }
        reorder();
        frame=requestAnimationFrame(tick);
      }
      grid.onpointermove=event=>{
        if(event.pointerId!==e.pointerId)return;
        pointerY=event.clientY;
        if(Math.abs(pointerY-startY)<6&&!moved)return;
        if(!moved){moved=true;row.classList.add('ht-dragging');frame=requestAnimationFrame(tick);}
        // Apply the current pointer immediately; the frame loop continues even
        // while the pointer stays still near an edge (mouse or touch).
        reorder();
      };
      function finish(event){
        if(finished || (event.pointerId!==undefined && event.pointerId!==e.pointerId))return;
        finished=true;cancelAnimationFrame(frame);
        window.removeEventListener('blur',cancel);
        document.removeEventListener('keydown',escape);
        document.removeEventListener('visibilitychange',hidden);
        grid.onpointermove=null;grid.onpointerup=null;grid.onpointercancel=null;grid.onlostpointercapture=null;
        if(grid.hasPointerCapture(e.pointerId))grid.releasePointerCapture(e.pointerId);
        row.classList.remove('ht-dragging');
        if(event.type==='pointerup' && moved)habitSaveOrder(month,[...body.querySelectorAll('[data-habit-row]')].map(item=>item.dataset.habitRow));
        else if(moved)renderTodos();
      }
      function cancel(){finish({type:'pointercancel'});}
      function escape(event){if(event.key==='Escape'){event.preventDefault();cancel();}}
      function hidden(){if(document.hidden)cancel();}
      window.addEventListener('blur',cancel);
      document.addEventListener('keydown',escape);
      document.addEventListener('visibilitychange',hidden);
      grid.onpointerup=finish;grid.onpointercancel=finish;grid.onlostpointercapture=finish;
    };
  });
}
