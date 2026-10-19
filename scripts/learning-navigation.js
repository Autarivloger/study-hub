/* LEARNING NAVIGATION START — device-only presentation; no learner-data changes. */
const learningGroupPreferenceKey='studyHubLearningGroups';
const learningGroupPreferences=Object.create(null);
try{
  const raw=localStorage.getItem(learningGroupPreferenceKey);
  const values=raw&&raw.length<4096?JSON.parse(raw):null;
  if(values&&typeof values==='object'&&!Array.isArray(values)){
    Object.keys(values).forEach(key=>{
      if(/^python-phase-[1-8]$/.test(key)&&typeof values[key]==='boolean')learningGroupPreferences[key]=values[key];
    });
  }
}catch(error){}
function learningGroupOpen(key){return learningGroupPreferences[key]===true;}
function wireLearningGroups(root){
  root.querySelectorAll('details[data-learning-group]').forEach(group=>{
    group.addEventListener('toggle',()=>{
      if(!root.contains(group))return;
      const key=group.dataset.learningGroup;
      if(!/^python-phase-[1-8]$/.test(key)||learningGroupPreferences[key]===group.open)return;
      learningGroupPreferences[key]=group.open;
      try{localStorage.setItem(learningGroupPreferenceKey,JSON.stringify(learningGroupPreferences));}catch(error){}
    });
  });
}
/* LEARNING NAVIGATION END */
