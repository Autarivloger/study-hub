function cyberRoadmapOverviewHtml(){
  return roadmapYearsHtml(CYBERSECURITY_PATH,CYBERSECURITY_ROADMAP,cyberPage.week,'cyber',item=>Boolean(CYBERSECURITY_TEACH[item.week+'.1']));
}
