/* STUDY HUB FLOATING BACK START — delegates existing navigation; no learner storage. */
function initFloatingBack(){
  const button=document.createElement('button');
  button.id='floatingBack';button.type='button';button.hidden=true;
  button.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M19 12H5m7-7-7 7 7 7"/></svg>';
  button.setAttribute('aria-label','Back');document.body.append(button);
  let frame=0;
  const rendered=node=>Boolean(node?.isConnected&&node.getClientRects().length&&getComputedStyle(node).visibility!=='hidden'&&!node.disabled);
  function source(){
    const view=document.querySelector('.view.active');if(!view)return null;
    // Prefer the immediate parent over a broader breadcrumb. Never use Previous,
    // Undo, month arrows, or arbitrary links as a substitute for a Back action.
    const selectors=['[data-safety-folder]','.jp-actions > [data-jp-lesson="19.5.core"]','.back-link',
      '.jp-actions > [data-jp-week]','.jp-actions > [data-jp-meanings]',
      '[data-jp-quick-exit]','.jp-actions > [data-jp-home]',
      '.gm-crumb[data-view="games"]','#prExit','#exitStudyBtn','#doneStudyBtn'];
    for(const selector of selectors){
      const target=Array.from(view.querySelectorAll(selector)).find(rendered);
      if(target)return target;
    }
    if(view.id==='view-lessons'&&view.querySelector('.yoga-compact')){
      const home=view.querySelector('#lessonsHomeBtn');if(rendered(home))return home;
    }
    // Split-view mobile Back is already in the sticky topbar and stays reachable.
    return null;
  }
  function topEdge(target){
    let edge=0;
    for(const id of ['topbar','tabnav']){
      const node=document.getElementById(id);if(!rendered(node))continue;
      const rect=node.getBoundingClientRect();
      if(rect.top<=edge+1&&rect.bottom>edge)edge=rect.bottom;
    }
    for(let node=target.parentElement;node&&node!==document.body;node=node.parentElement){
      if(/auto|scroll|hidden|clip/.test(getComputedStyle(node).overflowY))edge=Math.max(edge,node.getBoundingClientRect().top+node.clientTop);
    }
    return edge;
  }
  function update(){
    frame=0;
    const blocked=document.body.classList.contains('games-focus')||document.querySelector('#modalOverlay.open');
    const target=blocked?null:source();
    // A control farther down the page is not a scrolled-away Back button.
    const show=Boolean(target&&target.getBoundingClientRect().bottom<=topEdge(target)+2);
    if(show){
      const label=(target.getAttribute('aria-label')||target.textContent).replace(/^[←\s]+/,'').trim();
      const description=/^back\b/i.test(label)?label:'Back: '+label;
      if(button.getAttribute('aria-label')!==description){button.setAttribute('aria-label',description);button.title=description;}
    }
    if(button.hidden===show)button.hidden=!show;
  }
  function schedule(){if(!frame)frame=requestAnimationFrame(update);}
  button.addEventListener('click',()=>{
    const target=source();
    if(button.hidden||!target||document.body.classList.contains('games-focus')||document.querySelector('#modalOverlay.open'))return;
    const ancestors=[];
    for(let node=target.parentElement;node&&node!==document.body;node=node.parentElement)ancestors.push(node);
    button.hidden=true;
    target.click();
    // Back from deep in a lesson should reveal the parent page's heading.
    for(const node of ancestors)if(node.isConnected&&node.scrollTop)node.scrollTop=0;
    window.scrollTo(0,0);document.getElementById('content').focus({preventScroll:true});schedule();
  });
  document.addEventListener('scroll',schedule,{capture:true,passive:true});
  window.addEventListener('resize',schedule,{passive:true});
  window.visualViewport?.addEventListener('resize',schedule,{passive:true});
  const observer=new MutationObserver(schedule);
  const options={childList:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden','disabled']};
  observer.observe(document.getElementById('content'),options);
  observer.observe(document.getElementById('topbar'),options);
  observer.observe(document.getElementById('modalOverlay'),{attributes:true,attributeFilter:['class']});
  observer.observe(document.body,{attributes:true,attributeFilter:['class']});
  schedule();
}
initFloatingBack();
/* STUDY HUB FLOATING BACK END */
