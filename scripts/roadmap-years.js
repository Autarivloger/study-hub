/* SHARED ROADMAP YEARS START — presentation only, used by Cybersecurity and Web Development. */
function roadmapYearsHtml(path,weeks,selectedWeek,prefix,isReady){
  const selected=Math.ceil((selectedWeek||1)/52);
  return path.years.map(function(year){
    return '<details class="cyber-year" data-'+prefix+'-year="'+year.year+'"'+(year.year===selected?' open':'')+'>'+
      '<summary><span class="cyber-year-label">Year '+year.year+'</span><span class="cyber-year-heading">'+escapeHtml(year.title)+
      '<small>Weeks '+year.start+'–'+year.end+' · 52 weeks</small><small>'+escapeHtml(year.focus)+'</small></span></summary>'+
      '<div class="cyber-year-content">'+path.phases.filter(function(phase){return phase.start>=year.start&&phase.end<=year.end;}).map(function(phase){
        return '<section class="cyber-phase" aria-labelledby="'+prefix+'Phase'+phase.start+'"><h3 id="'+prefix+'Phase'+phase.start+'">'+escapeHtml(phase.title)+
          '</h3><p class="cyber-phase-range">Weeks '+phase.start+'–'+phase.end+'</p><div class="week-grid">'+
          weeks.filter(function(item){return item.week>=phase.start&&item.week<=phase.end;}).map(function(item){
            return '<button type="button" class="week-chip" data-'+prefix+'-week="'+item.week+'">'+
              '<span class="wc-num">Week '+item.week+'</span><span class="wc-title">'+escapeHtml(item.title)+'</span>'+
              '<span class="wc-prog">Day 1–Day 7 · '+(isReady&&isReady(item)?'Lessons ready':'Roadmap')+'</span></button>';
          }).join('')+'</div></section>';
      }).join('')+'</div></details>';
  }).join('');
}
/* SHARED ROADMAP YEARS END */
