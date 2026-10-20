/* GITA BOOK READER START */
const GITA_PREFIX='book:gita:v1|';
let gitaPdfPromise=null,gitaRenderTask=null,gitaRenderGeneration=0,gitaReadTimer=null,gitaCurrent=null,gitaDrawing=false,gitaDailyStamp='';
const gitaScriptPromises={};
function gitaReadRecord(key,store){
  try{const v=JSON.parse((store||DB.headNotes)[GITA_PREFIX+key]||'null');return v&&typeof v==='object'&&!Array.isArray(v)?v:null;}catch(e){return null;}
}
function gitaIsRecordKey(key){return /^book:gita:v1\|(position|bookmark|study-position|mark:[a-z0-9-]+)$/.test(key);}
function gitaMergeRecord(mine,theirs){
  try{const a=JSON.parse(mine||'null'),b=JSON.parse(theirs||'null');if(!b||typeof b!=='object'||!Number.isFinite(b.updatedAt))return mine===undefined?theirs:mine;
    if(!a||!Number.isFinite(a.updatedAt)||b.updatedAt>a.updatedAt||(b.updatedAt===a.updatedAt&&String(theirs)>String(mine)))return theirs;
  }catch(e){}return mine===undefined?theirs:mine;
}
function gitaWriteRecord(key,record){
  const old=gitaReadRecord(key),updatedAt=Math.max(Date.now(),(old?.updatedAt||0)+1);
  DB.headNotes[GITA_PREFIX+key]=JSON.stringify(Object.assign({},record,{updatedAt:updatedAt}));save();
}
function gitaMarks(page,includeDeleted){
  return Object.keys(DB.headNotes).filter(k=>k.startsWith(GITA_PREFIX+'mark:')).map(k=>({key:k.slice(GITA_PREFIX.length),value:gitaReadRecord(k.slice(GITA_PREFIX.length))})).filter(x=>x.value&&x.value.page===page&&(includeDeleted||!x.value.deleted)&&Array.isArray(x.value.points)).sort((a,b)=>(a.value.createdAt||0)-(b.value.createdAt||0));
}
function gitaDailyIndex(date){
  const d=date||new Date(),n=Math.floor(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())/86400000);
  return ((n-20746)%GITA_BOOK.daily.length+GITA_BOOK.daily.length)%GITA_BOOK.daily.length;
}
function gitaDailyHtml(){
  gitaDailyStamp=new Date().toDateString();
  const item=GITA_BOOK.daily[gitaDailyIndex()];
  return '<article class="card gita-daily"><p class="yoga-eyebrow">TODAY’S GITA THOUGHT · '+escapeHtml(new Date().toLocaleDateString())+'</p><blockquote lang="ne">'+escapeHtml(item.line)+'</blockquote><p lang="ne"><b>सरल अर्थ:</b> '+escapeHtml(item.meaning)+'</p><p lang="ne"><b>आजको सानो अभ्यास:</b> '+escapeHtml(item.action)+'</p><p class="gita-muted">Gita '+escapeHtml(item.ref)+' · '+escapeHtml(item.theme)+'<br>Original Nepali reflection inspired by the passage; not a verbatim verse or the book’s Hindi translation.</p><button type="button" class="btn secondary btn-sm" data-gita-source="'+item.page+'">Read the source context →</button></article>';
}
function gitaLibraryHtml(){
  const pos=gitaReadRecord('position'),page=Math.max(1,Math.min(GITA_BOOK.pages,Number(pos?.page)||1));
  return '<div class="gita-library"><article class="card"><img class="gita-book-cover" src="books/gita-cover.jpg" alt="Cover of your supplied Bhagavad Gita" loading="lazy"><p class="yoga-eyebrow">BOOK</p><h3>श्रीमद्भगवद्गीता</h3><p>Learn in English · 18 chapters · 700 verses<br>Original Sadhak-Sanjivani PDF also preserved</p><p class="gita-muted">Read the meaning, understand the context, and choose a practical next step. Your PDF reading place is page '+page+'.</p><button type="button" class="btn" data-yoga-mode="book">Open Book →</button></article>'+gitaDailyHtml()+'</div><details class="card gita-study" id="gitaStudyGuide"><summary>Chapter overview & daily study method</summary>'+gitaStudyHtml()+'</details>';
}
function gitaLoadScript(path,test){
  if(test())return Promise.resolve();
  if(gitaScriptPromises[path])return gitaScriptPromises[path];
  gitaScriptPromises[path]=new Promise((resolve,reject)=>{const s=document.createElement('script');s.src=path;s.onload=()=>{if(test())resolve();else{s.remove();delete gitaScriptPromises[path];reject(Error('Book asset did not initialise'));}};s.onerror=()=>{s.remove();delete gitaScriptPromises[path];reject(Error('Book files are not available. Open online once, or keep the books and vendor folders beside study-hub.html.'));};document.head.append(s);});
  return gitaScriptPromises[path];
}
function gitaLoadPdf(){
  if(gitaPdfPromise)return gitaPdfPromise;
  gitaPdfPromise=Promise.all([
    gitaLoadScript('vendor/pdfjs-6.4.299/pdf.worker.js',()=>Boolean(window.pdfjsWorker)),
    gitaLoadScript('vendor/pdfjs-6.4.299/pdf.js',()=>Boolean(window.StudyHubPdf)),
    gitaLoadScript('books/gita-pdf-v1.js',()=>Boolean(window.STUDY_HUB_GITA_BASE64))
  ]).then(async()=>{const raw=atob(window.STUDY_HUB_GITA_BASE64),data=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)data[i]=raw.charCodeAt(i);
    const doc=await window.StudyHubPdf.getDocument({data:data,isEvalSupported:false,useWasm:false,useWorkerFetch:false,disableAutoFetch:true,disableStream:true,stopAtErrors:false}).promise;
    if(doc.numPages!==GITA_BOOK.pages)throw Error('The book page count differs from the verified original.');return doc;
  }).catch(e=>{gitaPdfPromise=null;throw e;});
  return gitaPdfPromise;
}
function gitaPaperOffset(){
  if(!gitaCurrent?.ready)return 0;const p=document.getElementById('gitaPaper'),wrap=document.getElementById('gitaPageScroll');if(!p||!wrap)return 0;
  return Math.max(0,Math.min(1,wrap.scrollTop/Math.max(p.clientHeight,1)));
}
function gitaStickyTop(){
  let top=0;for(const id of ['topbar','tabnav']){const n=document.getElementById(id);if(!n||!n.getClientRects().length)continue;const r=n.getBoundingClientRect();if(r.top<=top+2)top=Math.max(top,r.bottom);}
  return top;
}
function gitaSaveReading(){
  if(!gitaCurrent?.ready)return;
  const record={page:gitaCurrent.page,offset:gitaPaperOffset()};
  const old=gitaReadRecord('position');
  if(!old||old.page!==record.page||Math.abs((old.offset||0)-record.offset)>.005)gitaWriteRecord('position',record);
}
function gitaBookLeave(){
  if(!gitaCurrent&&!gitaRenderTask)return;
  gitaSaveReading();clearTimeout(gitaReadTimer);gitaReadTimer=null;gitaRenderGeneration++;
  if(gitaRenderTask)gitaRenderTask.cancel();gitaRenderTask=null;gitaCurrent=null;gitaDrawing=false;
}
function gitaDrawMarks(){
  const svg=document.getElementById('gitaInk');if(!svg||!gitaCurrent)return;
  svg.replaceChildren();for(const {value:m} of gitaMarks(gitaCurrent.page)){
    const points=m.points.slice(0,1000).filter(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)).map(p=>p.map(v=>Math.max(0,Math.min(1,v))).join(',')).join(' ');
    if(!points)continue;const n=document.createElementNS('http://www.w3.org/2000/svg','polyline');n.setAttribute('points',points);svg.append(n);
  }
  const undo=document.getElementById('gitaUndo'),redo=document.getElementById('gitaRedo');
  if(undo)undo.disabled=!gitaMarks(gitaCurrent.page).length;
  if(redo)redo.disabled=!gitaMarks(gitaCurrent.page,true).some(m=>m.value.deleted);
}
function gitaWireDrawing(){
  const svg=document.getElementById('gitaInk');let stroke=null,pointer=null,preview=null;
  function point(e){const r=svg.getBoundingClientRect();return [(e.clientX-r.left)/r.width,(e.clientY-r.top)/r.height].map(v=>Math.round(Math.max(0,Math.min(1,v))*10000)/10000);}
  svg.onpointerdown=e=>{if(!gitaDrawing||!gitaCurrent?.ready||e.button!==0)return;e.preventDefault();pointer=e.pointerId;stroke=[point(e)];svg.setPointerCapture(pointer);preview=document.createElementNS('http://www.w3.org/2000/svg','polyline');svg.append(preview);};
  svg.onpointermove=e=>{if(!stroke||e.pointerId!==pointer)return;const p=point(e),last=stroke[stroke.length-1];if(Math.hypot(p[0]-last[0],p[1]-last[1])>.0015&&stroke.length<1000)stroke.push(p);preview.setAttribute('points',stroke.map(p=>p.join(',')).join(' '));};
  function finish(e){if(!stroke||e.pointerId!==pointer)return;const points=stroke;stroke=null;pointer=null;
    if(points.length>1)gitaWriteRecord('mark:'+uid(),{page:gitaCurrent.page,points:points,createdAt:Date.now(),deleted:false});
    gitaDrawMarks();document.getElementById('gitaStatus').textContent=points.length>1?'Underline saved.':'Drag along the text to draw an underline.';
  }
  svg.onpointerup=finish;
  svg.onpointercancel=()=>{stroke=null;pointer=null;gitaDrawMarks();};
}
function gitaSetPencil(on){
  gitaDrawing=Boolean(on);const svg=document.getElementById('gitaInk'),button=document.getElementById('gitaPencil');
  document.querySelector('.gita-pencil-tools')?.classList.toggle('is-drawing',gitaDrawing);
  if(svg)svg.classList.toggle('is-drawing',gitaDrawing);
  if(button){button.setAttribute('aria-pressed',String(gitaDrawing));button.setAttribute('aria-label',gitaDrawing?'Turn pencil off to scroll':'Turn pencil on to underline');}
  const help=document.getElementById('gitaPencilHelp');if(help)help.textContent=gitaDrawing?'Pencil ON · drag across the page to underline. Turn the pencil off to scroll normally.':'Reading mode · scroll normally. Turn on the floating pencil to draw an underline. Marks stay aligned when you zoom.';
}
async function gitaRenderPage(page,offset){
  page=Math.max(1,Math.min(GITA_BOOK.pages,Math.trunc(Number(page)||1)));
  gitaSaveReading();if(gitaRenderTask)gitaRenderTask.cancel();
  const generation=++gitaRenderGeneration;gitaCurrent={page:page,ready:false};gitaSetPencil(false);
  const status=document.getElementById('gitaStatus');if(!status)return;status.textContent='Opening PDF page '+page+'…';
  document.getElementById('gitaPage').value=page;
  document.getElementById('gitaPrevious').disabled=page===1;document.getElementById('gitaNext').disabled=page===GITA_BOOK.pages;
  document.getElementById('gitaPencil').disabled=true;
  try{
    const doc=await gitaLoadPdf();if(generation!==gitaRenderGeneration)return;
    const pdfPage=await doc.getPage(page);if(generation!==gitaRenderGeneration)return;
    const wrap=document.getElementById('gitaPageScroll'),paper=document.getElementById('gitaPaper'),canvas=paper.querySelector('canvas');
    gitaSizeViewport();
    const zoom=document.getElementById('gitaZoom').value,base=pdfPage.getViewport({scale:1});
    const fitWidth=Math.max(100,wrap.clientWidth-20)/base.width,fitPage=Math.min(fitWidth,Math.max(100,wrap.clientHeight-20)/base.height);
    const scale=zoom==='page'?fitPage:zoom==='width'?fitWidth:fitWidth*(Number(zoom)||1);
    const viewport=pdfPage.getViewport({scale}),ratio=Math.min(devicePixelRatio||1,2);
    paper.style.width=viewport.width+'px';paper.style.height=viewport.height+'px';
    canvas.width=Math.round(viewport.width*ratio);canvas.height=Math.round(viewport.height*ratio);
    canvas.setAttribute('aria-label','Original Bhagavad Gita · PDF page '+page+' of '+GITA_BOOK.pages);
    canvas.style.width=viewport.width+'px';canvas.style.height=viewport.height+'px';
    gitaRenderTask=pdfPage.render({canvasContext:canvas.getContext('2d'),viewport:viewport,transform:ratio===1?null:[ratio,0,0,ratio,0,0],background:'#fff'});
    await gitaRenderTask.promise;if(generation!==gitaRenderGeneration)return;gitaRenderTask=null;gitaCurrent.ready=true;
    gitaDrawMarks();document.getElementById('gitaPencil').disabled=false;
    const chapter=GITA_BOOK.chapters.filter(c=>c.page<=page).slice(-1)[0];
    document.getElementById('gitaCurrentPage').textContent='PDF page '+page+' / '+GITA_BOOK.pages+(chapter?' · Chapter '+chapter.chapter:' · Front matter');
    status.textContent='Page ready. Your reading place saves automatically.';
    const notes=document.getElementById('gitaPageNotes');
    notes.innerHTML=renderSections([{t:'h',v:'My notes · PDF page '+page,noteKey:GITA_PREFIX+'page-note:'+page}],GITA_PREFIX+'page:'+page);wireHeadNotes(notes);
    requestAnimationFrame(()=>{if(generation!==gitaRenderGeneration)return;wrap.scrollTop=(Number(offset)||0)*paper.clientHeight;gitaSaveReading();});
    gitaOfflineStatus();
  }catch(e){if(e?.name==='RenderingCancelledException'||generation!==gitaRenderGeneration)return;status.textContent='Could not open the book. '+e.message;document.getElementById('gitaRetry').hidden=false;}
}
async function gitaOfflineStatus(){
  const node=document.getElementById('gitaOfflineStatus');if(!node)return;
  if(location.protocol==='file:'){node.textContent='Local book · available offline with the books and vendor folders.';return;}
  try{const assets=['books/gita-pdf-v1.js','vendor/pdfjs-6.4.299/pdf.js','vendor/pdfjs-6.4.299/pdf.worker.js'];const hits=await Promise.all(assets.map(p=>caches.match(new URL(p,location.href).href)));node.textContent=hits.every(Boolean)?'Book saved for offline reading on this device.':'To save offline, open Book while online once and wait for the page to finish loading.';}catch(e){node.textContent='Offline availability depends on this browser keeping its website data.';}
}
function gitaSourceButtons(root){
  root.querySelectorAll('[data-gita-source]').forEach(b=>b.onclick=()=>{const page=Number(b.dataset.gitaSource);yogaPage.mode='book';gitaBookMode='pdf';renderYoga();gitaRenderPage(page,0);});
}
function renderGitaPdf(el){
  gitaBookLeave();const pos=gitaReadRecord('position')||{page:1,offset:0},bookmark=gitaReadRecord('bookmark');
  const pencil='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m4 16-1 5 5-1L20 8l-4-4L4 16Zm10-10 4 4M3 21l5-1"/></svg>';
  el.innerHTML='<div class="gita-reader gita-pdf-reader">'+gitaWorkspaceHeader('pdf')+'<details class="gita-about"><summary>About this edition · download & saved place</summary><p>Sadhak-Sanjivani Hindi commentary · Swami Ramsukhdas · Gita Press. Your original 1,296-page PDF is unchanged. Notes and pencil marks save separately.</p><div class="gita-book-actions"><button type="button" class="btn secondary" id="gitaResume">Resume PDF</button><button type="button" class="btn secondary" id="gitaBookmarkGo"'+(!bookmark?' disabled':'')+'>'+(bookmark?'Saved place · page '+Number(bookmark.page):'No saved bookmark yet')+'</button><button type="button" class="btn secondary" id="gitaDownload">Download original PDF</button></div><p class="gita-muted" id="gitaOfflineStatus">The reader loads only when opened.</p></details>'+
    '<div class="gita-toolbar" id="gitaToolbar" aria-label="Book page controls"><div class="gita-toolbar-primary"><button type="button" class="btn secondary" id="gitaPrevious" aria-label="Previous book page">←</button><label>Page <input type="number" min="1" max="'+GITA_BOOK.pages+'" id="gitaPage" value="'+Math.max(1,Math.min(GITA_BOOK.pages,Number(pos.page)||1))+'"></label><button type="button" class="btn secondary" id="gitaGo">Go</button><button type="button" class="btn secondary" id="gitaNext" aria-label="Next book page">→</button><button type="button" class="btn secondary" id="gitaControlsToggle" aria-expanded="true" aria-controls="gitaExtraControls">Hide controls</button></div><div class="gita-extra-controls" id="gitaExtraControls"><select id="gitaChapter" class="gita-chapter-select" aria-label="Choose a Gita chapter"><option value="">Choose chapter</option>'+GITA_BOOK.chapters.map(c=>'<option value="'+c.page+'">'+c.chapter+'. '+escapeHtml(c.name)+'</option>').join('')+'</select><select id="gitaZoom" aria-label="Book zoom"><option value="page">Fit page</option><option value="width">Fit width</option><option value="1">100%</option><option value="1.3">130%</option><option value="1.4">140%</option><option value="1.6">160%</option><option value="2">200%</option><option value="custom">Custom</option></select><label class="gita-custom-zoom"><input id="gitaZoomPercent" aria-label="Custom zoom percentage" type="number" min="25" max="300" step="5" value="100">% <button type="button" class="btn secondary" id="gitaApplyZoom">Apply</button></label></div></div>'+
    '<p id="gitaCurrentPage" class="gita-muted"></p><p class="gita-pencil-help" id="gitaPencilHelp">Reading mode · use the floating pencil to underline.</p><p class="gita-status" id="gitaStatus" role="status" aria-live="polite"></p><button type="button" class="btn secondary" id="gitaRetry" hidden>Retry opening</button><div class="gita-page-scroll" id="gitaPageScroll"><div class="gita-paper" id="gitaPaper"><canvas aria-label="Original Bhagavad Gita PDF page"></canvas><svg class="gita-ink" id="gitaInk" viewBox="0 0 1 1" preserveAspectRatio="none" aria-label="Pencil drawing area"></svg></div></div><section class="gita-notes" id="gitaPageNotes"></section>'+
    '<div class="gita-pencil-tools" aria-label="Reading pencil tools"><button type="button" class="btn secondary" id="gitaPencil" aria-label="Turn pencil on to underline" aria-pressed="false" title="Pencil · underline">'+pencil+'</button><button type="button" class="btn secondary" id="gitaUndo" aria-label="Undo last underline on this page" title="Undo underline" disabled>↶</button><button type="button" class="btn secondary" id="gitaRedo" aria-label="Restore last undone underline on this page" title="Redo underline" disabled>↷</button><button type="button" class="btn secondary" id="gitaBookmark" aria-label="Save my reading place" title="Save this reading place">▣</button></div></div>';
  el.querySelector('.gita-reader').style.setProperty('--gita-sticky-top',(gitaStickyTop()+4)+'px');
  gitaWireWorkspace(el);
  document.getElementById('gitaGo').onclick=()=>gitaRenderPage(document.getElementById('gitaPage').value,0);
  document.getElementById('gitaPage').onkeydown=e=>{if(e.key==='Enter')document.getElementById('gitaGo').click();};
  document.getElementById('gitaPrevious').onclick=()=>gitaRenderPage((gitaCurrent?.page||1)-1,0);
  document.getElementById('gitaNext').onclick=()=>gitaRenderPage((gitaCurrent?.page||1)+1,0);
  document.getElementById('gitaChapter').onchange=e=>{if(e.target.value)gitaRenderPage(e.target.value,0);};
  document.getElementById('gitaZoom').onchange=e=>{if(e.target.value==='custom'){const input=document.getElementById('gitaZoomPercent');input.focus();input.select();return;}if(Number(e.target.value))document.getElementById('gitaZoomPercent').value=Math.round(Number(e.target.value)*100);gitaRenderPage(gitaCurrent?.page||pos.page,gitaPaperOffset());};
  document.getElementById('gitaControlsToggle').onclick=e=>{const extra=document.getElementById('gitaExtraControls');extra.hidden=!extra.hidden;e.target.setAttribute('aria-expanded',String(!extra.hidden));e.target.textContent=extra.hidden?'Show controls':'Hide controls';gitaRenderPage(gitaCurrent?.page||pos.page,gitaPaperOffset());};
  function customZoom(){const n=Math.max(25,Math.min(300,Number(document.getElementById('gitaZoomPercent').value)||100));document.getElementById('gitaZoomPercent').value=n;const select=document.getElementById('gitaZoom');let option=select.querySelector('[data-custom]');if(!option){option=document.createElement('option');option.dataset.custom='true';select.add(option);}option.value=String(n/100);option.textContent=n+'%';select.value=option.value;gitaRenderPage(gitaCurrent?.page||pos.page,gitaPaperOffset());}
  document.getElementById('gitaApplyZoom').onclick=customZoom;
  document.getElementById('gitaZoomPercent').onkeydown=e=>{if(e.key==='Enter')customZoom();};
  document.getElementById('gitaPageScroll').onscroll=()=>{clearTimeout(gitaReadTimer);gitaReadTimer=setTimeout(gitaSaveReading,250);};
  document.getElementById('gitaPencil').onclick=()=>gitaSetPencil(!gitaDrawing);
  document.getElementById('gitaUndo').onclick=()=>{const m=gitaMarks(gitaCurrent.page).slice(-1)[0];if(m){gitaWriteRecord(m.key,Object.assign({},m.value,{deleted:true}));gitaDrawMarks();}};
  document.getElementById('gitaRedo').onclick=()=>{const m=gitaMarks(gitaCurrent.page,true).filter(x=>x.value.deleted).sort((a,b)=>b.value.updatedAt-a.value.updatedAt)[0];if(m){gitaWriteRecord(m.key,Object.assign({},m.value,{deleted:false}));gitaDrawMarks();}};
  document.getElementById('gitaBookmark').onclick=()=>{if(!gitaCurrent?.ready)return;gitaWriteRecord('bookmark',{page:gitaCurrent.page,offset:gitaPaperOffset()});const b=document.getElementById('gitaBookmarkGo');b.disabled=false;b.textContent='Saved place · page '+gitaCurrent.page;toast('Reading place saved');};
  document.getElementById('gitaBookmarkGo').onclick=()=>{const b=gitaReadRecord('bookmark');if(b)gitaRenderPage(b.page,b.offset);};
  document.getElementById('gitaResume').onclick=()=>{const p=gitaReadRecord('position')||pos;gitaRenderPage(p.page,p.offset);};
  document.getElementById('gitaRetry').onclick=()=>{document.getElementById('gitaRetry').hidden=true;gitaRenderPage(gitaCurrent?.page||pos.page,0);};
  document.getElementById('gitaDownload').onclick=async()=>{try{await gitaLoadPdf();const raw=atob(window.STUDY_HUB_GITA_BASE64),bytes=Uint8Array.from(raw,c=>c.charCodeAt(0)),url=URL.createObjectURL(new Blob([bytes],{type:'application/pdf'})),a=document.createElement('a');a.href=url;a.download='shrimad-bhagavad-gita.pdf';a.click();setTimeout(()=>URL.revokeObjectURL(url),2000);}catch(e){toast('Open the book successfully before downloading.');}};
  gitaSourceButtons(el);gitaWireDrawing();gitaRenderPage(pos.page,pos.offset);
  if(innerWidth<600){document.getElementById('gitaExtraControls').hidden=true;const b=document.getElementById('gitaControlsToggle');b.textContent='Show controls';b.setAttribute('aria-expanded','false');}
  el.querySelector('.gita-about').ontoggle=()=>{if(gitaCurrent?.ready)gitaRenderPage(gitaCurrent.page,gitaPaperOffset());};
}
function gitaStudyHtml(){
  return '<p lang="ne">यो ग्रन्थ युद्धभूमिमा अर्जुनको नैतिक सङ्कटबाट सुरु भएको कृष्ण–अर्जुन संवाद हो। साधक–सञ्जीवनीको केन्द्र केवल उपलब्धि वा जोस होइन; विवेक, निष्काम कर्म, आत्मबोध र भगवान्प्रतिको भक्ति जोडिएका छन्। तलका सार र जीवनका उदाहरण मौलिक अध्ययन-सहायता हुन्; मूल श्लोक र टीकाको विकल्प होइनन्।</p><h3>Read slowly · reflect · practise</h3><ol lang="ne"><li>पहिले अघिपछिको प्रसङ्ग पढ। आज १–३ श्लोक र तिनको टीका पर्याप्त हुन सक्छ। पृष्ठ सङ्ख्याको हतार नगर।</li><li>वक्ता, समस्या र उत्तर छुट्याऊ। नबुझेका शब्द लेख। एउटा वाक्य अलग गरेर आफ्नै इच्छाको अर्थ नलगाऊ।</li><li>एउटा सरल अर्थ आफ्नै शब्दमा लेख; त्यसपछि जीवनमा गर्ने एउटा सानो काम छान।</li><li>राति व्यवहार जाँच: कहाँ पालन भयो, कहाँ भएन, भोलि के सुधार्ने? आफूलाई गाली नगरी फेरि अभ्यास गर।</li></ol><p class="gita-muted">Chapter buttons use verified PDF page numbers from this file. A verse reference identifies the passage; read the surrounding commentary as well. Chapter 13 numbering can vary across editions; this guide follows the supplied book.</p><div class="gita-chapter-grid">'+GITA_BOOK.chapters.map(c=>'<button type="button" class="btn secondary" data-gita-source="'+c.page+'">'+c.chapter+'. '+escapeHtml(c.name)+'</button>').join('')+'</div>'+GITA_BOOK.chapters.map(c=>'<details><summary>'+c.chapter+'. '+escapeHtml(c.name)+' · PDF '+c.page+'</summary><p lang="ne"><b>प्रसङ्ग:</b> '+escapeHtml(c.context)+'</p><p lang="ne"><b>गहिरो विचार:</b> '+escapeHtml(c.insight)+'</p><p lang="ne"><b>जीवनमा अभ्यास:</b> '+escapeHtml(c.practice)+'</p><p lang="ne"><b>आफैँलाई प्रश्न:</b> '+escapeHtml(c.question)+'</p><button type="button" class="btn secondary" data-gita-source="'+c.page+'">Read Chapter '+c.chapter+' →</button></details>').join('');
}
window.addEventListener('scroll',()=>{if(!gitaCurrent?.ready||yogaPage.mode!=='book')return;clearTimeout(gitaReadTimer);gitaReadTimer=setTimeout(gitaSaveReading,350);},{passive:true});
window.addEventListener('pagehide',gitaSaveReading);
document.addEventListener('visibilitychange',()=>{if(document.hidden)gitaSaveReading();});
function gitaRefreshDaily(){
  if(gitaDailyStamp===new Date().toDateString()||!document.getElementById('view-lessons').classList.contains('active'))return;
  const cards=document.querySelectorAll('#lessonsBody .gita-daily');cards.forEach(c=>{c.outerHTML=gitaDailyHtml();});gitaSourceButtons(document.getElementById('lessonsBody'));
}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)gitaRefreshDaily();});
setInterval(gitaRefreshDaily,60000);
let gitaResizeTimer;
window.addEventListener('resize',()=>{document.querySelector('.gita-reader')?.style.setProperty('--gita-sticky-top',(gitaStickyTop()+4)+'px');if(!gitaCurrent?.ready)return;clearTimeout(gitaResizeTimer);gitaResizeTimer=setTimeout(()=>{if(!gitaCurrent?.ready)return;const page=gitaCurrent.page,offset=gitaPaperOffset();gitaRenderPage(page,offset);},180);});
new MutationObserver(()=>{if(gitaCurrent&&!document.getElementById('view-lessons').classList.contains('active'))gitaBookLeave();}).observe(document.getElementById('view-lessons'),{attributes:true,attributeFilter:['class']});
/* GITA BOOK READER END */
