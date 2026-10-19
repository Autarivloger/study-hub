let webDevPage={mode:'overview',week:1,day:1};
function renderWebDevelopment(){
  const body=document.getElementById('webDevelopmentBody');
  const week=WEBDEV_ROADMAP.find(item=>item.week===webDevPage.week)||WEBDEV_ROADMAP[0];
  webDevPage.week=week.week;
  let content='';
  if(webDevPage.mode==='overview'){
    content='<div class="cyber-heading"><h1>Web Development</h1><p class="cyber-subtitle">Beginner path · 3 years · 156 weeks</p></div>'+
      '<section class="webdev-start"><div><span class="webdev-kicker">START FROM ZERO</span><h2>Your first page, then useful applications.</h2><p>No previous HTML, CSS or JavaScript knowledge is assumed. Start with files, folders and your browser. Learn the foundations before adding frameworks.</p></div><button type="button" class="btn" data-webdev-week="1">Start with Week 1 →</button></section>'+
      '<p class="webdev-rhythm">Each week: 5 study days · 1 project day · 1 review/catch-up day. Repeat a week whenever a topic needs more practice.</p>'+
      '<div class="section-label">Choose a year, then a week</div>'+roadmapYearsHtml(WEBDEV_PATH,WEBDEV_ROADMAP,webDevPage.week,'webdev');
  }else if(webDevPage.mode==='week'){
    content='<button type="button" class="back-link" data-webdev-all>← All years and weeks</button><div class="week-header"><div class="wh-eyebrow">Year '+Math.ceil(week.week/52)+' · Week '+week.week+' · Web Development</div><h2>'+escapeHtml(week.title)+'</h2></div>'+
      '<section class="webdev-checkpoint"><h3>This week’s readiness check</h3><p>'+escapeHtml(week.checkpoint)+'</p></section><div class="section-label">Daily roadmap</div><div class="day-list">'+week.days.map(function(day){
        return '<div class="day-row"><button type="button" class="day-open" data-webdev-day="'+day.day+'"><div class="dr-title">Day '+day.day+'</div><div class="dr-meta">'+escapeHtml(day.focus)+'</div></button></div>';
      }).join('')+'</div>';
  }else{
    const day=week.days.find(item=>item.day===webDevPage.day)||week.days[0];webDevPage.day=day.day;
    const position=(week.week-1)*7+day.day-1;
    content='<button type="button" class="back-link" data-webdev-week="'+week.week+'">← Week '+week.week+'</button><div class="week-header"><div class="wh-eyebrow">Year '+Math.ceil(week.week/52)+' · Week '+week.week+' · Day '+day.day+' of 7</div><h2>Day '+day.day+'</h2><p class="wh-goal">'+escapeHtml(day.focus)+'</p></div>'+
      '<section class="cyber-day-topics"><h3>'+(day.day===6?'Project goals':day.day===7?'Review and catch up':'What to study')+'</h3><ul class="ex-list">'+day.topics.map(topic=>'<li>'+escapeHtml(topic)+'</li>').join('')+'</ul></section>'+
      '<p class="webdev-roadmap-label">Roadmap only · This page lists learning and practice goals.</p>'+
      '<div class="cyber-day-navigation"><button type="button" class="btn secondary" data-webdev-step="-1"'+(position===0?' disabled':'')+'>← Previous day</button><button type="button" class="btn" data-webdev-step="1"'+(position===WEBDEV_ROADMAP.length*7-1?' disabled':'')+'>Next day →</button></div>';
  }
  body.innerHTML=content+'<footer class="webdev-references"><p>Roadmap available offline. External references need internet.</p><div>References: '+WEBDEV_PATH.references.map(item=>'<a href="'+escapeAttr(item.url)+'" target="_blank" rel="noopener noreferrer">'+escapeHtml(item.title)+'</a>').join(' · ')+'</div></footer>';
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
