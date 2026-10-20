/* STUDY HUB SPELLING START — suggestions only; no learner-data schema or automatic edits. */
function initSpellingAssistance(){
  const selector='textarea,input,[contenteditable="true"],[contenteditable="plaintext-only"]';
  const excluded='#tyProxy,#tyCustomText,#reviewAttempt,[data-practice-attempt],#searchInput,#syTok,#syGist,#tfPaste,[data-spelling="off"],[spellcheck="false"]';
  const technical=/^(?:syTok|syGist|chessFen|chessPgn|chFen|chPgn|tfPaste)$|(?:password|token|secret|credential|apiKey)/i;
  const glossary=new Set(('python javascript typescript html css json csv sql sqlite github git numpy pandas pytest django flask cyber cybersecurity sudoku sokoban kanji hiragana katakana furigana romaji onyomi kunyomi gita bhagavad bhagavadgita dharma karma atman brahman sattva rajas tamas prakriti purusha krishna arjuna dhritarashtra sanjaya pandavas kauravas yoga yogi pranayama samadhi sadhana sadhak sanjivani ramsukhdas surya namaskar shloka vedas upanishads hunspell scowl').split(' '));
  const ignored=new Set(),cache=new Map();let field=null,worker=null,loadPromise=null,words=null,sequence=0,timer=0,current=null,composing=false,closedWord='',popup=null;
  for(const word of 'practise practised practising colour colours colourful favourite favourites behaviour behaviours organise organised organising organisation organisations realise realised realising centre centres travelling travelled traveller travellers learnt cancelled defence offence licence licences metre metres theatre theatres neighbour neighbours'.split(' '))glossary.add(word);
  const button=document.createElement('button');button.type='button';button.id='spellingButton';button.className='spelling-button';button.hidden=true;button.textContent='ABC';button.title='English spelling · suggestions only. Right-click a word, or click here.';button.setAttribute('aria-label','English spelling suggestions');button.setAttribute('aria-haspopup','menu');document.body.append(button);
  function sensitive(node){return technical.test((node.id||'')+' '+(node.name||''))||Boolean(node.closest('[data-sensitive]'));}
  function editable(node){
    if(!(node instanceof HTMLElement)||!node.matches(selector)||node.matches(excluded)||sensitive(node)||node.disabled||node.readOnly)return false;
    if(node instanceof HTMLInputElement&&(!['text','search'].includes(node.type)||/^(numeric|decimal|tel|url|email)$/.test(node.inputMode)))return false;
    return node instanceof HTMLInputElement||node instanceof HTMLTextAreaElement||node.isContentEditable;
  }
  function configure(node){
    if(!editable(node)){if(node.matches?.(selector)&&(sensitive(node)||node.matches(excluded))){node.setAttribute('spellcheck','false');node.setAttribute('autocorrect','off');node.setAttribute('autocapitalize','off');}return;}
    node.setAttribute('spellcheck','true');node.setAttribute('autocorrect','off');node.setAttribute('autocapitalize','off');
  }
  function scan(root){if(root.nodeType!==1)return;if(root.matches(selector))configure(root);root.querySelectorAll(selector).forEach(configure);}
  function eligible(node){return editable(node)&&typeof node.value==='string'&&!/^ja(?:-|$)|^ne(?:-|$)|^sa(?:-|$)/i.test(node.closest('[lang]')?.lang||'')&&!/^mpField[0134]$/.test(node.id);}
  function getWord(node,start,end){
    const value=node.value,caret=start===undefined?node.selectionStart:start,finish=end===undefined?node.selectionEnd:end;if(caret===null)return null;
    let a=caret,b=finish;if(a!==b){if(!/^[A-Za-z]+(?:['’][A-Za-z]+)*$/.test(value.slice(a,b)))return null;}
    else{if(a>0&&!/[A-Za-z’']/.test(value[a]||''))a--;b=a;while(a>0&&/[A-Za-z’']/.test(value[a-1]))a--;while(b<value.length&&/[A-Za-z’']/.test(value[b]))b++;}
    while(a<b&&/['’]/.test(value[a]))a++;while(b>a&&/['’]/.test(value[b-1]))b--;
    const word=value.slice(a,b);if(word.length<3||word.length>24||!/^[A-Za-z]+(?:['’][A-Za-z]+)*$/.test(word)||/[\p{L}\p{N}_@/\\]/u.test(value[a-1]||'')||/[\p{L}\p{N}_@/\\]/u.test(value[b]||''))return null;
    if(glossary.has(word.toLowerCase())||ignored.has(word.toLowerCase())||/^[A-Z]{2,}$|[a-z][A-Z]/.test(word))return null;
    const line=value.slice(value.lastIndexOf('\n',a-1)+1,(value.indexOf('\n',b)+1||value.length+1)-1);
    if(/https?:\/\/|www\.|\b(?:def|class|import|return|print)\b.*[:=(]|```|=>|\w+\([^)]*\)/.test(line)||value.slice(0,a).split('```').length%2===0)return null;
    return {field:node,start:a,end:b,word};
  }
  function known(word){return words&&(words.has(word)||words.has(word.toLowerCase())||words.has(word.charAt(0).toUpperCase()+word.slice(1).toLowerCase()));}
  function dismiss(){sequence++;current=null;if(popup)popup.hidden=true;button.dataset.state='';}
  function keepHidden(){if(current)closedWord=current.word;dismiss();}
  function viewport(){const v=window.visualViewport;return {left:v?.offsetLeft||0,top:v?.offsetTop||0,width:v?.width||innerWidth,height:v?.height||innerHeight};}
  function place(){
    if(!field?.isConnected||!eligible(field)){button.hidden=true;dismiss();return;}
    const r=field.getBoundingClientRect(),v=viewport(),bottom=v.top+v.height;
    if(r.bottom<v.top||r.top>bottom||!field.getClientRects().length){button.hidden=true;if(popup)popup.hidden=true;return;}
    button.hidden=false;button.style.left=Math.max(v.left+8,Math.min(r.right-48,v.left+v.width-48))+'px';
    const y=r.bottom+4+30<bottom?r.bottom+4:Math.max(v.top+8,Math.min(r.top-32,bottom-38));button.style.top=y+'px';
    if(popup&&!popup.hidden){const w=Math.min(330,v.width-16);popup.style.width=w+'px';popup.style.left=Math.max(v.left+8,Math.min(r.left,v.left+v.width-w-8))+'px';
      const h=popup.getBoundingClientRect().height,below=r.bottom+6;popup.style.top=Math.max(v.top+8,Math.min(below+h<bottom?below:r.top-h-6,bottom-h-8))+'px';}
  }
  function show(info,result,manual){
    if(!field?.isConnected||field!==info.field||field.value.slice(info.start,info.end)!==info.word||(!manual&&document.activeElement!==field))return;
    if(result.correct&&!manual){dismiss();return;}
    current={...info,manual};button.dataset.state=result.correct?'':'mistake';
    if(!popup){popup=document.createElement('section');popup.id='spellingSuggestions';popup.className='spelling-suggestions';popup.setAttribute('role','menu');popup.setAttribute('aria-label','English spelling suggestions');document.body.append(popup);}
    popup.replaceChildren();const head=document.createElement('div');head.className='spelling-head';const title=document.createElement('b');title.textContent=result.correct?'Spelling looks correct':result.loading?'Checking spelling…':'Did you mean…';
    const close=document.createElement('button');close.type='button';close.textContent='×';close.setAttribute('aria-label','Close spelling suggestions');close.onclick=()=>{keepHidden();field?.focus({preventScroll:true});};head.append(title,close);popup.append(head);
    const original=document.createElement('p');original.className='spelling-original';original.textContent=info.word;popup.append(original);
    const list=document.createElement('div');list.className='spelling-options';
    for(const suggestion of result.suggestions||[]){const item=document.createElement('button');item.type='button';item.setAttribute('role','menuitem');item.dataset.spellingSuggestion=suggestion;item.textContent=suggestion;item.onclick=()=>replace(info,suggestion);list.append(item);}
    popup.append(list);
    if(!result.correct&&!result.loading&&!(result.suggestions||[]).length){const empty=document.createElement('p');empty.textContent=result.failed?'Browser spelling is still available.':'No close English match found.';popup.append(empty);}
    const foot=document.createElement('div');foot.className='spelling-foot';const note=document.createElement('small');note.textContent='English · Nothing changes until you choose.';foot.append(note);
    if(!result.correct&&!result.loading){const ignore=document.createElement('button');ignore.type='button';ignore.textContent='Ignore word';ignore.title='Ignore this word for this visit';ignore.onclick=()=>{ignored.add(info.word.toLowerCase());dismiss();field?.focus({preventScroll:true});};foot.append(ignore);}
    popup.append(foot);popup.hidden=false;place();
  }
  function replace(info,suggestion){
    const target=info.field;if(!target.isConnected||!eligible(target)||target.value.slice(info.start,info.end)!==info.word){dismiss();return;}
    target.focus({preventScroll:true});target.setSelectionRange(info.start,info.end);
    // Native insertText keeps the browser's undo history. The fallback fires the same input event used by autosave.
    let inserted=false;try{inserted=document.execCommand('insertText',false,suggestion);}catch(error){}
    if(!inserted){target.setRangeText(suggestion,info.start,info.end,'end');target.dispatchEvent(new InputEvent('input',{bubbles:true,inputType:'insertReplacementText',data:suggestion}));}
    closedWord='';dismiss();place();
  }
  function load(){
    if(loadPromise)return loadPromise;
    loadPromise=new Promise((resolve,reject)=>{
      const script=document.createElement('script');script.src='vendor/spelling/english-v1.js';script.onload=()=>{let url;
        try{url=URL.createObjectURL(new Blob([window.STUDY_HUB_SPELLING_SOURCE],{type:'application/javascript'}));worker=new Worker(url);worker.onmessage=e=>{
          if(e.data.ready){words=new Set(e.data.words);resolve();return;}
          cache.set(e.data.word,e.data);if(cache.size>300)cache.delete(cache.keys().next().value);
          if(e.data.id===sequence&&current)show(current,e.data,current.manual);
        };worker.onerror=e=>{e.preventDefault();reject(Error('Offline spelling unavailable'));};}catch(error){reject(error);}finally{if(url)URL.revokeObjectURL(url);}
      };script.onerror=()=>{script.remove();loadPromise=null;reject(Error('Dictionary not available'));};document.head.append(script);
    });return loadPromise;
  }
  async function check(manual=false,info=getWord(field||{value:'',selectionStart:null})){
    if(!info||!field||!eligible(field)||composing){dismiss();return;}
    if(!manual&&info.word===closedWord)return;current={...info,manual};const id=++sequence;
    if(manual)show(info,{loading:true,suggestions:[]},true);
    try{await load();if(id!==sequence||field!==info.field||!field.isConnected)return;
      if(known(info.word)){show(info,{correct:true,suggestions:[]},manual);return;}
      const stored=cache.get(info.word);if(stored){show(info,stored,manual);return;}
      current={...info,manual};worker.postMessage({id,word:info.word});
    }catch(error){if(id===sequence){if(manual)show(info,{failed:true,suggestions:[]},true);else dismiss();}}
  }
  // Resolve the actual word under a right-click, including in a scrolled textarea.
  function wordAtPoint(node,x,y){
    const r=node.getBoundingClientRect();if(x<r.left||x>r.right||y<r.top||y>r.bottom)return null;
    const mirror=document.createElement('div'),style=getComputedStyle(node);
    const props=['fontFamily','fontSize','fontWeight','fontStyle','fontVariant','lineHeight','letterSpacing','textTransform','textAlign','textIndent','direction','wordSpacing','tabSize','paddingTop','paddingRight','paddingBottom','paddingLeft','borderTopWidth','borderRightWidth','borderBottomWidth','borderLeftWidth','borderStyle','boxSizing','wordBreak','overflowWrap'];
    for(const p of props)mirror.style[p]=style[p];Object.assign(mirror.style,{position:'fixed',left:r.left+'px',top:r.top+'px',width:r.width+'px',height:r.height+'px',overflow:'hidden',whiteSpace:node.tagName==='TEXTAREA'?'pre-wrap':'pre',visibility:'hidden',pointerEvents:'none'});
    const text=document.createTextNode(node.value);mirror.append(text);document.body.append(mirror);mirror.scrollTop=node.scrollTop;mirror.scrollLeft=node.scrollLeft;
    let found=null;const range=document.createRange();
    try{for(const m of node.value.matchAll(/[A-Za-z]+(?:['’][A-Za-z]+)*/g)){range.setStart(text,m.index);range.setEnd(text,m.index+m[0].length);for(const box of range.getClientRects()){if(x>=box.left-2&&x<=box.right+2&&y>=box.top&&y<=box.bottom){found=getWord(node,m.index,m.index+m[0].length);break;}}if(found)break;}}
    finally{mirror.remove();}return found;
  }
  scan(document.body);
  new MutationObserver(records=>{for(const record of records)for(const node of record.addedNodes)scan(node);if(field&&!field.isConnected){field=null;button.hidden=true;dismiss();}}).observe(document.body,{subtree:true,childList:true});
  document.addEventListener('focusin',event=>{const node=event.target;if(node===button||popup?.contains(node))return;configure(node);if(eligible(node)){if(field!==node)closedWord='';field=node;place();clearTimeout(timer);timer=setTimeout(()=>check(false),600);}else{field=null;button.hidden=true;dismiss();}});
  document.addEventListener('focusout',()=>setTimeout(()=>{if(document.activeElement!==field&&document.activeElement!==button&&!popup?.contains(document.activeElement)){field=null;button.hidden=true;dismiss();}},0));
  document.addEventListener('input',event=>{if(event.target!==field)return;closedWord='';dismiss();clearTimeout(timer);if(!composing)timer=setTimeout(()=>check(false),650);});
  document.addEventListener('compositionstart',event=>{if(event.target===field){composing=true;dismiss();clearTimeout(timer);}});
  document.addEventListener('compositionend',event=>{if(event.target===field){composing=false;clearTimeout(timer);timer=setTimeout(()=>check(false),650);}});
  document.addEventListener('pointerdown',event=>{if(event.target===button||popup?.contains(event.target))return;dismiss();if(event.target!==field){field=null;button.hidden=true;}});
  document.addEventListener('contextmenu',event=>{if(event.shiftKey||!eligible(event.target))return;
    const selected=event.target.value.slice(event.target.selectionStart,event.target.selectionEnd);if(selected&&!/^[A-Za-z]+(?:['’][A-Za-z]+)*$/.test(selected))return;
    const info=wordAtPoint(event.target,event.clientX,event.clientY);if(!info)return;
    field=event.target;place();if(words&&!known(info.word)){event.preventDefault();check(true,info);}else if(cache.get(info.word)?.correct===false){event.preventDefault();check(true,info);}
  });
  document.addEventListener('keydown',event=>{if(event.key==='Escape'&&popup&&!popup.hidden){keepHidden();return;}if(event.altKey&&event.key==='ArrowDown'&&event.target===field){event.preventDefault();check(true);return;}if(popup?.contains(event.target)&&['ArrowDown','ArrowUp'].includes(event.key)){const items=Array.from(popup.querySelectorAll('button'));const at=items.indexOf(document.activeElement);items[(at+(event.key==='ArrowDown'?1:-1)+items.length)%items.length].focus();event.preventDefault();}});
  button.addEventListener('pointerdown',event=>event.preventDefault());button.onclick=()=>check(true);
  document.addEventListener('scroll',place,{capture:true,passive:true});window.addEventListener('resize',place,{passive:true});window.visualViewport?.addEventListener('resize',place,{passive:true});
}
initSpellingAssistance();
/* STUDY HUB SPELLING END */
