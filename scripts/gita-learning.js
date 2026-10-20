/* GITA ENGLISH LEARNING START */
let gitaBookMode='learn',gitaStudyPage={chapter:0,verse:0};
function gitaSizeViewport(){
  const wrap=document.getElementById('gitaPageScroll');if(!wrap)return;
  const top=wrap.getBoundingClientRect().top;
  wrap.style.height=Math.max(120,window.innerHeight-Math.max(gitaStickyTop()+65,top)-20)+'px';
}
function gitaWorkspaceHeader(mode){
  return '<header class="gita-workspace-head"><button type="button" class="back-link" id="gitaBookBack">← Yoga & Meditation</button><div class="gita-workspace-title"><span>BOOK</span><h2>Bhagavad Gita</h2></div><nav class="gita-mode-tabs" aria-label="Book reading mode"><button type="button" class="btn '+(mode==='learn'?'':'secondary')+'" data-gita-mode="learn" aria-pressed="'+(mode==='learn')+'">Learn in English</button><button type="button" class="btn '+(mode==='pdf'?'':'secondary')+'" data-gita-mode="pdf" aria-pressed="'+(mode==='pdf')+'">Original PDF</button></nav></header>';
}
function gitaWireWorkspace(el){
  el.querySelector('#gitaBookBack').onclick=()=>{gitaBookLeave();yogaPage.mode='home';renderYoga();window.scrollTo(0,0);};
  el.querySelectorAll('[data-gita-mode]').forEach(b=>b.onclick=()=>{gitaBookLeave();gitaBookMode=b.dataset.gitaMode;renderGitaBook(el);window.scrollTo(0,0);});
}
function renderGitaBook(el){
  if(gitaBookMode==='pdf')return renderGitaPdf(el);
  gitaBookLeave();renderGitaLearning(el);
}
function gitaOpenVerse(chapter,verse){
  chapter=Math.max(1,Math.min(18,Math.trunc(Number(chapter)||1)));
  const ch=GITA_LEARNING[chapter-1];verse=Math.max(1,Math.min(ch.verses.length,Math.trunc(Number(verse)||1)));
  gitaStudyPage={chapter,verse};gitaWriteRecord('study-position',{chapter,verse});gitaBookMode='learn';
  renderGitaLearning(document.getElementById('lessonsBody'));window.scrollTo(0,0);
}
function gitaVerseId(c,v){return 'gita:verse:'+c+'.'+v;}
function gitaChapterDone(ch){return ch.verses.filter(v=>lessonDone(gitaVerseId(ch.chapter,v.verse))).length;}
function renderGitaLearning(el){
  const p=gitaStudyPage,pos=gitaReadRecord('study-position'),total=GITA_LEARNING.reduce((n,c)=>n+gitaChapterDone(c),0);
  let html='<div class="gita-reader gita-learning">'+gitaWorkspaceHeader('learn');
  if(!p.chapter){
    html+='<section class="gita-learn-intro card"><p class="yoga-eyebrow">18 CHAPTERS · 700 VERSES · ENGLISH STUDY</p><h3>Understand one verse. Practise one change.</h3><p>Read the Sanskrit, understand the simple English meaning, then connect the passage to a thoughtful action. Start with Chapter 1: it presents Arjuna’s crisis before Krishna’s teaching begins.</p><div class="gita-book-actions"><button class="btn" type="button" id="gitaContinue">'+(pos?'Continue · '+Number(pos.chapter)+'.'+Number(pos.verse):'Begin · Chapter 1, Verse 1')+' →</button><span class="gita-muted">'+total+' / 700 studied</span></div>'+progressBar(total,700)+'</section><div class="gita-learning-chapters">'+GITA_LEARNING.map(c=>'<button type="button" class="card gita-chapter-card" data-gita-chapter="'+c.chapter+'"><span class="yoga-eyebrow">CHAPTER '+c.chapter+' · '+c.verses.length+' VERSES</span><h3>'+escapeHtml(c.title)+'</h3><p>'+escapeHtml(c.intro)+'</p><span class="gita-muted">'+gitaChapterDone(c)+' / '+c.verses.length+' studied →</span>'+progressBar(gitaChapterDone(c),c.verses.length)+'</button>').join('')+'</div>';
  }else{
    const ch=GITA_LEARNING[p.chapter-1],v=ch.verses[p.verse-1],group=ch.groups.find(g=>p.verse>=g.from&&p.verse<=g.to),done=lessonDone(gitaVerseId(p.chapter,p.verse));
    html+='<div class="gita-lesson-nav"><button type="button" class="btn secondary" id="gitaAllChapters">← Chapters</button><label>Chapter<select id="gitaStudyChapter" aria-label="Study chapter">'+GITA_LEARNING.map(c=>'<option value="'+c.chapter+'"'+(c.chapter===p.chapter?' selected':'')+'>'+c.chapter+'. '+escapeHtml(c.title)+'</option>').join('')+'</select></label><label>Verse<select id="gitaStudyVerse" aria-label="Study verse">'+ch.verses.map(x=>'<option value="'+x.verse+'"'+(x.verse===p.verse?' selected':'')+'>'+x.verse+(lessonDone(gitaVerseId(ch.chapter,x.verse))?' ✓':'')+'</option>').join('')+'</select></label></div>';
    html+='<p class="gita-muted">CHAPTER '+p.chapter+' · VERSE '+p.verse+' OF '+ch.verses.length+' · '+gitaChapterDone(ch)+' studied</p>'+progressBar(gitaChapterDone(ch),ch.verses.length)+'<article class="card gita-verse-card"><p class="yoga-eyebrow">'+escapeHtml(ch.title)+' · '+p.chapter+'.'+p.verse+'</p><h3>'+escapeHtml(group.title)+'</h3><div class="gita-sanskrit" lang="sa">'+escapeHtml(v.sanskrit).replace(/\n/g,'<br>')+'</div><section><h4>In simple English</h4><p>'+escapeHtml(v.meaning)+'</p></section><section class="gita-context"><h4>Understand the passage · '+group.from+(group.to===group.from?'':'–'+group.to)+'</h4><p>'+escapeHtml(group.context)+'</p></section>'+(group.caution?'<section class="gita-reading-care"><h4>Read carefully</h4><p>'+escapeHtml(group.caution)+'</p></section>':'')+'<section class="gita-application"><h4>Bring it into your life</h4><p>'+escapeHtml(v.practice)+'</p></section><section id="gitaVerseNotes">'+renderSections([{t:'h',v:'My reflection & next step',noteKey:GITA_PREFIX+'verse-note:'+p.chapter+'.'+p.verse},{t:'p',v:'In your own words: what does this verse mean in its passage? Write one realistic action, then return later to record what happened.'}],gitaVerseId(p.chapter,p.verse))+'</section><div class="gita-book-actions"><button type="button" class="btn" id="gitaVerseDone">'+(done?'✓ Studied · undo':'Mark verse studied')+'</button><button type="button" class="btn secondary" id="gitaVersePdf">Read original Chapter '+p.chapter+' →</button></div></article><footer class="gita-verse-footer"><button type="button" class="btn secondary" id="gitaVersePrevious"'+(p.chapter===1&&p.verse===1?' disabled':'')+'>← Previous verse</button><span>'+p.chapter+'.'+p.verse+'</span><button type="button" class="btn" id="gitaVerseNext"'+(p.chapter===18&&p.verse===78?' disabled':'')+'>Next verse →</button></footer>';
  }
  html+='<details class="gita-about"><summary>About these English lessons & sources</summary><p>The English meanings and practical reflections are original Study Hub learning notes, not a line-by-line translation of Swami Ramsukhdas’s Hindi commentary. Read the unchanged supplied PDF for that commentary. Practical examples are applications, not hidden commands inside every verse. Chapter 1 records a crisis; later chapters answer it.</p><p>The Sanskrit follows the 700-verse numbering used by your book: Chapter 1 has 47 verses; Chapter 13 has 34. Some other editions count an opening question in Chapter 13 and number the following verses one higher.</p><p>Ancient Sanskrit: <a href="https://github.com/AdiyogiArts/gita-json" target="_blank" rel="noopener noreferrer">Adiyogi Arts corpus (Sanskrit only, MIT)</a>, checked and corrected against <a href="https://sanskritdocuments.org/doc_giitaa/bhagvadnew.html" target="_blank" rel="noopener noreferrer">Sanskrit Documents</a> and normalised to this edition. Reference: your supplied Sadhak-Sanjivani; historical English comparison: <a href="https://en.wikisource.org/wiki/Sacred_Books_of_the_East/Volume_8/1882" target="_blank" rel="noopener noreferrer">K. T. Telang, 1882</a>. Spiritual interpretations differ between traditions; these notes retain the Gita’s teachings on self, duty, devotion and liberation.</p></details></div>';
  el.innerHTML=html;el.querySelector('.gita-reader').style.setProperty('--gita-sticky-top',(gitaStickyTop()+4)+'px');gitaWireWorkspace(el);wireHeadNotes(el);
  if(!p.chapter){
    document.getElementById('gitaContinue').onclick=()=>gitaOpenVerse(pos?.chapter||1,pos?.verse||1);
    el.querySelectorAll('[data-gita-chapter]').forEach(b=>b.onclick=()=>gitaOpenVerse(b.dataset.gitaChapter,1));
  }else{
    const ch=GITA_LEARNING[p.chapter-1];
    document.getElementById('gitaAllChapters').onclick=()=>{gitaStudyPage={chapter:0,verse:0};renderGitaLearning(el);window.scrollTo(0,0);};
    document.getElementById('gitaStudyChapter').onchange=e=>gitaOpenVerse(e.target.value,1);
    document.getElementById('gitaStudyVerse').onchange=e=>gitaOpenVerse(p.chapter,e.target.value);
    document.getElementById('gitaVerseDone').onclick=()=>{const y=window.scrollY;toggleLessonDone(gitaVerseId(p.chapter,p.verse));renderGitaLearning(el);renderSideStats();window.scrollTo(0,y);};
    document.getElementById('gitaVersePrevious').onclick=()=>p.verse>1?gitaOpenVerse(p.chapter,p.verse-1):p.chapter>1?gitaOpenVerse(p.chapter-1,GITA_LEARNING[p.chapter-2].verses.length):null;
    document.getElementById('gitaVerseNext').onclick=()=>p.verse<ch.verses.length?gitaOpenVerse(p.chapter,p.verse+1):p.chapter<18?gitaOpenVerse(p.chapter+1,1):null;
    document.getElementById('gitaVersePdf').onclick=()=>{gitaBookMode='pdf';renderGitaPdf(el);gitaRenderPage(GITA_BOOK.chapters[p.chapter-1].page,0);window.scrollTo(0,0);};
  }
}
/* GITA ENGLISH LEARNING END */
