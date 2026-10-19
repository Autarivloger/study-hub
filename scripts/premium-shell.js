/* STUDY HUB PREMIUM SHELL START — presentation only; no learner storage. */
function initWorkspaceShell(){
  const paths={
    course:'M4 5h6a3 3 0 0 1 2 1 3 3 0 0 1 2-1h6v14h-6a3 3 0 0 0-2 1 3 3 0 0 0-2-1H4z M12 6v14',
    webdev:'M3 4h18v16H3z M3 8h18 M9 12l-3 3 3 3 M15 12l3 3-3 3',
    japanese:'M4 5h12 M10 3v3 M6 9c2 5 5 7 9 9 M14 5c-1 6-5 11-10 13 M14 21l4-10 4 10 M16 17h4',
    quiz:'M12 3l8 3v6c0 5-8 9-8 9s-8-4-8-9V6z M8 12l3 3 5-6',
    reviews:'M4 10a8 8 0 1 1 1 8 M4 4v6h6 M12 7v5l3 2',
    typing:'M3 6h18v12H3z M6 9h1 M10 9h1 M14 9h1 M18 9h.01 M6 12h1 M10 12h1 M14 12h1 M18 12h.01 M7 15h10',
    flashcards:'M7 7h13v13H7z M4 16H3V3h13v1 M11 11h5 M11 15h3',
    timer:'M9 3h6 M12 6v2 M18 6l2 2 M12 11v4l2 1 M20 15a8 8 0 1 1-16 0 8 8 0 0 1 16 0',
    todo:'M9 6h11 M9 12h11 M9 18h11 M3 6l1 1 2-3 M3 12l1 1 2-3 M3 18l1 1 2-3',
    journal:'M5 3h14v18H5z M3 7h4 M3 12h4 M3 17h4 M10 7h5 M10 11h5 M10 15h3',
    wisdom:'M5 20C3 7 12 3 21 3c0 12-5 18-13 15 M4 21L16 9',
    lessons:'M7 9c0 6 3 9 5 10 2-1 5-4 5-10-2 0-4 2-5 4-1-2-3-4-5-4z M12 13V4 M10 6l2-3 2 3 M7 13H3c0 6 4 8 9 8s9-2 9-8h-4',
    liked:'M12 20S3 15 3 8a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 7-9 12-9 12z',
    games:'M7 8h10c3 0 5 10 3 11-2 1-4-3-5-3H9c-1 0-3 4-5 3-2-1 0-11 3-11z M7 11v5 M4.5 13.5h5 M16 12h.01 M18 15h.01',
    search:'M10 3a7 7 0 1 0 0 14 7 7 0 0 0 0-14 M15 15l6 6',
    theme:'M20 15A8 8 0 0 1 9 4a8 8 0 1 0 11 11',
    more:'M5 12h.01 M12 12h.01 M19 12h.01',
    sync:'M7 17H6a4 4 0 1 1 1-8 6 6 0 0 1 11 0 4 4 0 0 1 0 8h-1 M9 18l3 3 3-3 M12 12v9',
    export:'M12 3v12 M8 11l4 4 4-4 M4 15v6h16v-6',
    import:'M12 16V4 M8 8l4-4 4 4 M4 15v6h16v-6',
    transfer:'M4 7h16 M16 3l4 4-4 4 M20 17H4 M8 13l-4 4 4 4',
    help:'M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18 M9 9a3 3 0 0 1 6 0c0 2-3 2-3 4 M12 17h.01'
  };
  const icon=name=>'<svg class="ui-icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="'+paths[name]+'"/></svg>';
  document.querySelectorAll('#sidebar [data-view],#tabnav [data-view]').forEach(button=>{
    const slot=button.querySelector('.ic');if(slot&&paths[button.dataset.view])slot.innerHTML=icon(button.dataset.view);
  });
  document.querySelectorAll('[data-ui-icon]').forEach(slot=>{if(paths[slot.dataset.uiIcon])slot.innerHTML=icon(slot.dataset.uiIcon);});
  const menu=document.getElementById('workspaceTools');
  document.addEventListener('click',event=>{
    if(!menu.contains(event.target)||event.target.closest('.workspace-menu button'))menu.open=false;
  });
  document.addEventListener('keydown',event=>{
    if(event.key==='Escape'&&menu.open){menu.open=false;menu.querySelector('summary').focus();}
  });
  document.addEventListener('focusin',event=>{if(menu.open&&!menu.contains(event.target))menu.open=false;});
}
initWorkspaceShell();
/* STUDY HUB PREMIUM SHELL END */
