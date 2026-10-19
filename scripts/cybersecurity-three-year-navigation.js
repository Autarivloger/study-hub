function cyberRoadmapOverviewHtml(){
  const selected=Math.ceil((cyberPage.week||1)/52);
  return CYBERSECURITY_PATH.years.map(function(year){
    return '<details class="cyber-year" data-cyber-year="'+year.year+'"'+(year.year===selected?' open':'')+'>'+
      '<summary><span class="cyber-year-label">Year '+year.year+'</span><span class="cyber-year-heading">'+escapeHtml(year.title)+
      '<small>Weeks '+year.start+'–'+year.end+' · 52 weeks</small><small>'+escapeHtml(year.focus)+'</small></span></summary>'+
      '<div class="cyber-year-content">'+CYBERSECURITY_PATH.phases.filter(function(phase){return phase.start>=year.start&&phase.end<=year.end;}).map(function(phase){
        return '<section class="cyber-phase" aria-labelledby="cyberPhase'+phase.start+'"><h3 id="cyberPhase'+phase.start+'">'+escapeHtml(phase.title)+
          '</h3><p class="cyber-phase-range">Weeks '+phase.start+'–'+phase.end+'</p><div class="week-grid">'+
          CYBERSECURITY_ROADMAP.filter(function(item){return item.week>=phase.start&&item.week<=phase.end;}).map(function(item){
            return '<button type="button" class="week-chip" data-cyber-week="'+item.week+'">'+
              '<span class="wc-num">Week '+item.week+'</span><span class="wc-title">'+escapeHtml(item.title)+'</span>'+
              '<span class="wc-prog">Day 1–Day 7 · '+(CYBERSECURITY_TEACH[item.week+'.1']?'Lessons ready':'Roadmap')+'</span></button>';
          }).join('')+'</div></section>';
      }).join('')+'</div></details>';
  }).join('');
}
