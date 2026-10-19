let webDevPage={mode:'overview',week:1,day:1};
function webDevLessonHtml(lesson){
  const context=lesson.id;
  return '<article class="webdev-teaching"><div class="ls-obj"><div class="ls-obj-lab">What you will be able to do</div><div class="ls-obj-text">'+escapeHtml(lesson.objective)+'</div></div>'+
    '<button type="button" class="btn secondary btn-sm" data-webdev-notes>My day notes ↓</button>'+renderSections(lesson.sections,context)+
    renderLessonQuiz(lesson)+'</article><section id="webdevDayNotes" class="cyber-day-notes" aria-label="Day notes">'+
    renderSections([{t:'h',v:'Day Notes',noteKey:context+'|day-notes'},{t:'p',v:lesson.reflection}],context)+'</section>'+
    '<div class="webdev-completion"><button type="button" class="btn'+(lessonDone(context)?' secondary':'')+'" data-webdev-done="'+escapeAttr(context)+'" aria-pressed="'+lessonDone(context)+'">'+(lessonDone(context)?'✓ Completed · tap to undo':'Mark lesson complete')+'</button><span>Your progress and notes are saved in this browser. Backup/import and configured sync include them.</span></div>';
}
function renderWebDevelopment(){
  const body=document.getElementById('webDevelopmentBody');
  const week=WEBDEV_ROADMAP.find(item=>item.week===webDevPage.week)||WEBDEV_ROADMAP[0];
  webDevPage.week=week.week;
  let content='';
  if(webDevPage.mode==='overview'){
    content='<div class="cyber-heading"><h1>Web Development</h1><p class="cyber-subtitle">Beginner path · 3 years · 156 weeks</p></div>'+
      '<section class="webdev-start"><div><span class="webdev-kicker">START FROM ZERO</span><h2>Your first page, then useful applications.</h2><p>No previous HTML, CSS or JavaScript knowledge is assumed. Start with files, folders and your browser. Learn the foundations before adding frameworks.</p></div><button type="button" class="btn" data-webdev-week="1">Start with Week 1 →</button></section>'+
      '<p class="webdev-rhythm">Each week: 5 study days · 1 project day · 1 review/catch-up day. Repeat a week whenever a topic needs more practice.</p>'+
      '<div class="section-label">Choose a year, then a week</div>'+roadmapYearsHtml(WEBDEV_PATH,WEBDEV_ROADMAP,webDevPage.week,'webdev',item=>Boolean(WEBDEV_TEACH[item.week+'.1']));
  }else if(webDevPage.mode==='week'){
    content='<button type="button" class="back-link" data-webdev-all>← All years and weeks</button><div class="week-header"><div class="wh-eyebrow">Year '+Math.ceil(week.week/52)+' · Week '+week.week+' · Web Development</div><h2>'+escapeHtml(week.title)+'</h2></div>'+
      '<section class="webdev-checkpoint"><h3>This week’s readiness check</h3><p>'+escapeHtml(week.checkpoint)+'</p>'+(WEBDEV_TEACH[week.week+'.1']?'<p class="webdev-week-progress">'+week.days.filter(d=>lessonDone('webdev:'+week.week+'.'+d.day)).length+' / 7 days complete</p>':'')+'</section><div class="section-label">'+(WEBDEV_TEACH[week.week+'.1']?'Daily lessons':'Daily roadmap')+'</div><div class="day-list lesson-day-grid" aria-label="Choose a daily lesson">'+week.days.map(function(day){
        return '<div class="day-row"><button type="button" class="day-open" data-webdev-day="'+day.day+'" title="'+escapeAttr("Day "+day.day+": "+day.focus)+'"><div class="dr-title day-card-number">Day '+day.day+'</div><div class="dr-meta">'+escapeHtml(day.focus)+(lessonDone('webdev:'+week.week+'.'+day.day)?' · ✓ Completed':'')+'</div></button></div>';
      }).join('')+'</div>';
  }else{
    const day=week.days.find(item=>item.day===webDevPage.day)||week.days[0];webDevPage.day=day.day;
    const position=(week.week-1)*7+day.day-1;
    const lesson=WEBDEV_TEACH[week.week+'.'+day.day];
    content='<button type="button" class="back-link" data-webdev-week="'+week.week+'">← Week '+week.week+'</button><div class="week-header"><div class="wh-eyebrow">Year '+Math.ceil(week.week/52)+' · Week '+week.week+' · Day '+day.day+' of 7</div><h2>Day '+day.day+'</h2><p class="wh-goal">'+escapeHtml(day.focus)+'</p></div>'+
      '<section class="cyber-day-topics"><h3>'+(day.day===6?'Project goals':day.day===7?'Review and catch up':'What to study')+'</h3><ul class="ex-list">'+day.topics.map(topic=>'<li>'+escapeHtml(topic)+'</li>').join('')+'</ul></section>'+
      (lesson?webDevLessonHtml(lesson):'<p class="webdev-roadmap-label">Roadmap only · This page lists learning and practice goals.</p>')+
      '<div class="cyber-day-navigation"><button type="button" class="btn secondary" data-webdev-step="-1"'+(position===0?' disabled':'')+'>← Previous day</button><button type="button" class="btn" data-webdev-step="1"'+(position===WEBDEV_ROADMAP.length*7-1?' disabled':'')+'>Next day →</button></div>';
  }
  body.innerHTML=content+'<footer class="webdev-references"><p>Lessons and roadmap available offline. External references need internet.</p><div>References: '+WEBDEV_PATH.references.map(item=>'<a href="'+escapeAttr(item.url)+'" target="_blank" rel="noopener noreferrer">'+escapeHtml(item.title)+'</a>').join(' · ')+'</div></footer>';
  wireRevealButtons(body);wireHeadNotes(body);
  const lesson=webDevPage.mode==='day'?WEBDEV_TEACH[week.week+'.'+webDevPage.day]:null;
  if(lesson){
    wireLessonQuiz(body,lesson);
    const notes=body.querySelector('#webdevDayNotes'),box=notes.querySelector('.hn-box'),button=notes.querySelector('[data-hn]'),input=notes.querySelector('textarea');
    box.hidden=false;button.classList.add('open');input.setAttribute('aria-label','Notes for Web Development Week '+week.week+' Day '+webDevPage.day);
    input.placeholder='Write what you understood, your file path, experiments and questions.';
    body.querySelector('[data-webdev-notes]').onclick=()=>{box.hidden=false;button.classList.add('open');notes.scrollIntoView({block:'center'});input.focus({preventScroll:true});};
    body.querySelector('[data-webdev-done]').onclick=()=>{
      if(DB.lessonsDone[lesson.id])delete DB.lessonsDone[lesson.id];else DB.lessonsDone[lesson.id]=nowISO();
      save();const button=body.querySelector('[data-webdev-done]'),done=lessonDone(lesson.id);button.setAttribute('aria-pressed',String(done));button.classList.toggle('secondary',done);button.textContent=done?'✓ Completed · tap to undo':'Mark lesson complete';
    };
  }
  function update(){renderWebDevelopment();window.scrollTo(0,0);}
  body.querySelectorAll('[data-webdev-all]').forEach(button=>button.onclick=()=>{webDevPage.mode='overview';update();});
  body.querySelectorAll('[data-webdev-week]').forEach(button=>button.onclick=()=>{webDevPage={mode:'week',week:Number(button.dataset.webdevWeek),day:1};update();});
  body.querySelectorAll('[data-webdev-day]').forEach(button=>button.onclick=()=>{webDevPage.mode='day';webDevPage.day=Number(button.dataset.webdevDay);update();});
  body.querySelectorAll('[data-webdev-step]').forEach(button=>button.onclick=()=>{
    const position=(webDevPage.week-1)*7+webDevPage.day-1+Number(button.dataset.webdevStep);
    if(position<0||position>=WEBDEV_ROADMAP.length*7)return;
    webDevPage={mode:'day',week:Math.floor(position/7)+1,day:position%7+1};update();
  });
}
