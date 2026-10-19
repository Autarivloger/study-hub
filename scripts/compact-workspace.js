/* COMPACT WORKSPACE START — device-only layout preference; no learner data. */
function initCompactWorkspace(){
  const root=document.documentElement,button=document.getElementById('sidebarToggle');
  const key='studyHubSidebarCompact';
  document.querySelectorAll('#sidebar .nav-item').forEach(item=>{
    const label=item.querySelector('.nav-label').textContent.trim();
    item.setAttribute('aria-label',label);item.title=label;
  });
  function apply(collapsed){
    root.classList.toggle('sidebar-compact',collapsed);
    const label=collapsed?'Expand sidebar':'Collapse sidebar';
    button.setAttribute('aria-expanded',String(!collapsed));button.setAttribute('aria-label',label);button.title=label;
    button.querySelector('.sidebar-toggle-label').textContent=label;
    // Existing game fitting and floating-Back listeners can remeasure the layout.
    window.dispatchEvent(new Event('resize'));
  }
  let collapsed=false;try{collapsed=localStorage.getItem(key)==='1';}catch(error){}
  apply(collapsed);
  button.addEventListener('click',()=>{
    const next=!root.classList.contains('sidebar-compact');apply(next);
    try{localStorage.setItem(key,next?'1':'0');}catch(error){}
  });
  window.addEventListener('storage',event=>{if(event.key===key)apply(event.newValue==='1');});
}
initCompactWorkspace();
/* COMPACT WORKSPACE END */
