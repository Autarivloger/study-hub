/* EXERCISE TRACKER START — additive records; existing tasks and habits stay independent. */
function exerciseUnits(){return {reps:'reps',sec:'seconds',min:'minutes',rounds:'rounds',sets:'sets'};}
function exerciseValidDate(value){
  return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&habitValidMonth(value.slice(0,7))&&Number(value.slice(8))>=1&&Number(value.slice(8))<=habitDays(value.slice(0,7));
}
function exerciseValidId(value){return typeof value==='string'&&/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,99}$/.test(value)&&!['constructor','prototype'].includes(value);}
function exerciseValidTime(value){return typeof value==='string'&&value.length<=40&&Number.isFinite(Date.parse(value));}
function exerciseValidAmount(quantity,unit){return Number.isFinite(quantity)&&quantity>0&&quantity<=1000000&&(['sec','min'].includes(unit)||Number.isInteger(quantity));}
function exerciseValidRecord(kind,key,item){
  if(!item||typeof item!=='object'||Array.isArray(item)||!exerciseValidId(key)||item.id!==key||
    !exerciseValidTime(item.createdAt)||!exerciseValidTime(item.updatedAt)||typeof item.deleted!=='boolean'||
    typeof item.unit!=='string'||!Object.hasOwn(exerciseUnits(),item.unit))return false;
  const name=kind==='exercises'?item.name:item.exerciseName;
  if(typeof name!=='string'||!name.trim()||name.length>120)return false;
  const sets=kind==='exercises'?item.defaultSets:item.sets;
  if(!Number.isInteger(sets)||sets<1||sets>1000||(item.unit==='sets'&&sets!==1))return false;
  return kind==='exercises'||(exerciseValidId(item.exerciseId)&&exerciseValidDate(item.date)&&exerciseValidAmount(item.quantity,item.unit)&&typeof item.notes==='string'&&item.notes.length<=2000);
}
function exerciseCopyRecord(kind,item){
  const common={id:item.id,unit:item.unit,createdAt:item.createdAt,updatedAt:item.updatedAt,deleted:item.deleted};
  return kind==='exercises'?{...common,name:item.name,defaultSets:item.defaultSets}:
    {...common,exerciseId:item.exerciseId,exerciseName:item.exerciseName,date:item.date,quantity:item.quantity,sets:item.sets,notes:item.notes};
}
function exerciseDefaults(value){
  const source=value&&typeof value==='object'&&!Array.isArray(value)?value:{};
  const result={exercises:{},entries:{},selectedDate:null};
  for(const kind of ['exercises','entries']){
    const map=source[kind];if(!map||typeof map!=='object'||Array.isArray(map))continue;
    for(const [key,item] of Object.entries(map))if(exerciseValidRecord(kind,key,item))result[kind][key]=exerciseCopyRecord(kind,item);
  }
  const date=source.selectedDate;
  if(date&&exerciseValidDate(date.value)&&exerciseValidTime(date.updatedAt))result.selectedDate={value:date.value,updatedAt:date.updatedAt};
  return result;
}
function exerciseNewer(theirs,mine){
  if(!mine)return true;
  const difference=Date.parse(theirs.updatedAt)-Date.parse(mine.updatedAt);
  if(difference)return difference>0;
  if(theirs.deleted!==mine.deleted)return theirs.deleted===true;
  return JSON.stringify(theirs)>JSON.stringify(mine);
}
function exerciseMerge(value){
  const incoming=exerciseDefaults(value),target=DB.exerciseTracker;
  for(const kind of ['exercises','entries'])for(const [key,item] of Object.entries(incoming[kind])){
    if(!Object.hasOwn(target[kind],key)||exerciseNewer(item,target[kind][key]))target[kind][key]=item;
  }
  if(incoming.selectedDate&&exerciseNewer(incoming.selectedDate,target.selectedDate))target.selectedDate=incoming.selectedDate;
}
function exerciseStamp(previous){return new Date(Math.max(Date.now(),(Date.parse(previous?.updatedAt)||0)+1)).toISOString();}
function exerciseDate(){return DB.exerciseTracker.selectedDate?.value||todayStr();}
function exerciseSelectDate(value){
  if(!exerciseValidDate(value))return;
  DB.exerciseTracker.selectedDate={value,updatedAt:exerciseStamp(DB.exerciseTracker.selectedDate)};save();renderTodos();
}
function exerciseMoveDate(amount){
  const value=new Date(exerciseDate()+'T12:00:00Z');value.setUTCDate(value.getUTCDate()+amount);
  const next=value.toISOString().slice(0,10);if(exerciseValidDate(next))exerciseSelectDate(next);
}
function exerciseTemplates(removed=false){
  return Object.values(DB.exerciseTracker.exercises).filter(item=>item.deleted===removed).sort((a,b)=>a.name.localeCompare(b.name)||a.id.localeCompare(b.id));
}
function exerciseEntries(date,removed=false){
  return Object.values(DB.exerciseTracker.entries).filter(item=>item.date===date&&item.deleted===removed).sort((a,b)=>a.createdAt.localeCompare(b.createdAt)||a.id.localeCompare(b.id));
}
function exerciseAmount(item){
  const labels=exerciseUnits(),unit=item.unit==='sec'?'sec':item.unit==='min'?'min':labels[item.unit];
  return item.quantity+' '+unit+(item.sets>1?' × '+item.sets+' sets':'');
}
function exercisePencil(label,kind,id){
  return '<details class="exercise-menu"><summary aria-label="'+escapeAttr(label)+'" title="'+escapeAttr(label)+'">'+
    '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 5 4 4M4 20l4-1L20 7a2.8 2.8 0 0 0-4-4L4 15z" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></summary>'+
    '<div><button type="button" data-exercise-edit="'+escapeAttr(id)+'" data-exercise-kind="'+kind+'">Edit</button>'+
    '<button type="button" data-exercise-remove="'+escapeAttr(id)+'" data-exercise-kind="'+kind+'">Remove</button></div></details>';
}
function exerciseRemovedHtml(kind,items){
  if(!items.length)return '';
  return '<details class="exercise-removed"><summary>Removed '+(kind==='exercises'?'exercises':'activities')+' · '+items.length+'</summary>'+items.map(item=>
    '<div class="exercise-restore-row"><span>'+escapeHtml(kind==='exercises'?item.name:item.exerciseName+' · '+exerciseAmount(item))+'</span><button type="button" class="btn secondary btn-sm" data-exercise-restore="'+escapeAttr(item.id)+'" data-exercise-kind="'+kind+'">Restore</button></div>').join('')+'</details>';
}
function renderExerciseTracker(){
  const pane=document.getElementById('exercisePane'),date=exerciseDate(),month=date.slice(0,7),entries=exerciseEntries(date),templates=exerciseTemplates();
  const monthEntries=Object.values(DB.exerciseTracker.entries).filter(item=>!item.deleted&&item.date.startsWith(month)),dates=[...new Set(monthEntries.map(item=>item.date))].sort().reverse();
  pane.innerHTML='<div class="exercise-toolbar"><div><h2>Exercise</h2><p>Reps, time, sets and a record for every day.</p></div><div class="exercise-actions"><button type="button" class="btn secondary" id="exerciseAdd">+ Add exercise</button><button type="button" class="btn" id="exerciseLog">+ Log activity</button></div></div>'+
    '<div class="exercise-date-bar"><label for="exerciseDate">Date</label><button type="button" class="icon-btn" id="exercisePrev" aria-label="Previous day"'+(date==='0001-01-01'?' disabled':'')+'>←</button><input type="date" id="exerciseDate" min="0001-01-01" max="9999-12-31" value="'+date+'"><button type="button" class="icon-btn" id="exerciseNext" aria-label="Next day"'+(date==='9999-12-31'?' disabled':'')+'>→</button><button type="button" class="btn secondary btn-sm" id="exerciseToday">Today</button></div>'+
    '<div class="exercise-layout"><section class="exercise-panel" aria-labelledby="exerciseDailyHeading"><div class="exercise-section-heading"><h3 id="exerciseDailyHeading">Daily activity</h3><span>'+entries.length+' '+(entries.length===1?'entry':'entries')+'</span></div>'+
    (entries.length?'<div class="exercise-daily-list">'+entries.map(item=>'<article class="exercise-log-row"><div class="exercise-log-copy"><h4>'+escapeHtml(item.exerciseName)+'</h4><div class="exercise-dose">'+escapeHtml(exerciseAmount(item))+'</div>'+(item.notes?'<p class="exercise-note">'+escapeHtml(item.notes)+'</p>':'')+'</div>'+exercisePencil('Edit or remove '+item.exerciseName,'entries',item.id)+'</article>').join('')+'</div>':
      '<div class="exercise-empty"><strong>No activity recorded for this date.</strong><p>Choose an exercise, then enter what you completed.</p></div>')+exerciseRemovedHtml('entries',exerciseEntries(date,true))+'</section>'+
    '<section class="exercise-panel exercise-library" aria-labelledby="exerciseLibraryHeading"><div class="exercise-section-heading"><h3 id="exerciseLibraryHeading">My exercises</h3><span>'+templates.length+'</span></div>'+
    (templates.length?templates.map(item=>'<div class="exercise-template-row"><div><strong>'+escapeHtml(item.name)+'</strong><small>'+escapeHtml(exerciseUnits()[item.unit])+(item.defaultSets>1?' · '+item.defaultSets+' sets':'')+'</small></div><button type="button" class="btn secondary btn-sm" data-exercise-log="'+escapeAttr(item.id)+'">Log</button>'+exercisePencil('Edit or remove '+item.name,'exercises',item.id)+'</div>').join(''):
      '<div class="exercise-empty"><strong>Add your own exercise names.</strong><p>For example: Push-up, Squat, Plank, Pull-up, Meditation or Surya Namaskar.</p><button type="button" class="btn secondary btn-sm" id="exerciseFirst">+ Add exercise</button></div>')+
    exerciseRemovedHtml('exercises',exerciseTemplates(true))+'</section></div>'+
    '<details class="exercise-history exercise-panel"><summary>'+escapeHtml(habitMonthName(month))+' history · '+dates.length+' recorded '+(dates.length===1?'day':'days')+'</summary>'+
    (dates.length?dates.map(day=>'<section class="exercise-history-day"><button type="button" class="exercise-history-date" data-exercise-date="'+day+'">'+day+'</button><ul>'+monthEntries.filter(item=>item.date===day).sort((a,b)=>a.createdAt.localeCompare(b.createdAt)).map(item=>'<li><span>'+escapeHtml(item.exerciseName)+'</span><strong>'+escapeHtml(exerciseAmount(item))+'</strong></li>').join('')+'</ul></section>').join(''):'<p class="exercise-muted">Your saved activities for this month will appear here. Choose another date to view a different month.</p>')+'</details>';
  pane.querySelector('#exerciseAdd').onclick=()=>exerciseEditTemplate();
  pane.querySelector('#exerciseFirst')?.addEventListener('click',()=>exerciseEditTemplate());
  pane.querySelector('#exerciseLog').onclick=()=>templates.length?exerciseEditEntry():exerciseEditTemplate();
  pane.querySelector('#exerciseDate').onchange=event=>exerciseSelectDate(event.target.value);
  pane.querySelector('#exercisePrev').onclick=()=>exerciseMoveDate(-1);
  pane.querySelector('#exerciseNext').onclick=()=>exerciseMoveDate(1);
  pane.querySelector('#exerciseToday').onclick=()=>exerciseSelectDate(todayStr());
  pane.querySelectorAll('[data-exercise-date]').forEach(button=>button.onclick=()=>exerciseSelectDate(button.dataset.exerciseDate));
  pane.querySelectorAll('[data-exercise-log]').forEach(button=>button.onclick=()=>exerciseEditEntry(null,button.dataset.exerciseLog));
  pane.querySelectorAll('[data-exercise-edit]').forEach(button=>button.onclick=()=>{
    pane.querySelectorAll('.exercise-menu').forEach(menu=>menu.open=false);
    if(button.dataset.exerciseKind==='exercises')exerciseEditTemplate(button.dataset.exerciseEdit);else exerciseEditEntry(button.dataset.exerciseEdit);
  });
  pane.querySelectorAll('[data-exercise-remove]').forEach(button=>button.onclick=()=>{
    const kind=button.dataset.exerciseKind,item=DB.exerciseTracker[kind][button.dataset.exerciseRemove];
    pane.querySelectorAll('.exercise-menu').forEach(menu=>menu.open=false);
    confirmDialog('Remove <b>'+escapeHtml(kind==='exercises'?item.name:item.exerciseName)+'</b>? '+(kind==='exercises'?'Saved activities will stay in your history. ':'')+'You can restore it from Removed '+(kind==='exercises'?'exercises.':'activities.'),()=>{
      item.deleted=true;item.updatedAt=exerciseStamp(item);save();renderTodos();
    });
  });
  pane.querySelectorAll('[data-exercise-restore]').forEach(button=>button.onclick=()=>{
    const item=DB.exerciseTracker[button.dataset.exerciseKind][button.dataset.exerciseRestore];item.deleted=false;item.updatedAt=exerciseStamp(item);save();renderTodos();
  });
  pane.querySelectorAll('.exercise-menu').forEach(menu=>menu.addEventListener('toggle',()=>{
    if(menu.open)pane.querySelectorAll('.exercise-menu').forEach(other=>{if(other!==menu)other.open=false;});
  }));
  pane.onkeydown=event=>{if(event.key==='Escape'){const menu=event.target.closest('.exercise-menu');if(menu?.open){menu.open=false;menu.querySelector('summary').focus();event.preventDefault();}}};
}
function exerciseUnitOptions(unit){return Object.entries(exerciseUnits()).map(([value,label])=>'<option value="'+value+'"'+(value===unit?' selected':'')+'>'+label+'</option>').join('');}
function exerciseWireUnits(unit,sets,amount){
  function update(){
    sets.disabled=unit.value==='sets';if(sets.disabled)sets.value='1';
    if(amount){
      amount.step=['sec','min'].includes(unit.value)?'any':'1';
      document.querySelector('label[for="exerciseQuantity"]').textContent=unit.value==='sets'?'Total sets':unit.value==='reps'?'Reps per set':unit.value==='rounds'?'Rounds per set':'Time per set';
    }
  }
  unit.addEventListener('change',update);update();
}
function exerciseEditTemplate(id){
  const existing=DB.exerciseTracker.exercises[id];
  openModal('<h2>'+(existing?'Edit exercise':'Add exercise')+'</h2><form id="exerciseTemplateForm"><div class="form-row"><label for="exerciseName">Exercise name</label><input id="exerciseName" required maxlength="120" placeholder="e.g. Push-up or Meditation" value="'+escapeAttr(existing?.name||'')+'"></div><div class="exercise-form-grid"><div class="form-row"><label for="exerciseUnit">Measure in</label><select id="exerciseUnit">'+exerciseUnitOptions(existing?.unit||'reps')+'</select></div><div class="form-row"><label for="exerciseSets">Usual sets</label><input id="exerciseSets" type="number" min="1" max="1000" step="1" required value="'+(existing?.defaultSets||1)+'"></div></div><p class="exercise-muted">Examples: reps for push-ups, seconds for a plank, minutes for meditation, or sets/rounds for Surya Namaskar. You can change the amount and sets when logging.</p><p id="exerciseFormError" role="alert" class="exercise-error"></p><div class="modal-actions"><button type="button" class="btn secondary" id="exerciseCancel">Cancel</button><button type="submit" class="btn">'+(existing?'Save changes':'Add exercise')+'</button></div></form>');
  const name=document.getElementById('exerciseName'),unit=document.getElementById('exerciseUnit'),sets=document.getElementById('exerciseSets');
  exerciseWireUnits(unit,sets);document.getElementById('exerciseCancel').onclick=closeModal;name.focus();
  document.getElementById('exerciseTemplateForm').onsubmit=event=>{
    event.preventDefault();const at=exerciseStamp(existing),item={id:existing?.id||uid(),name:name.value.trim(),unit:unit.value,defaultSets:Number(sets.value),deleted:false,createdAt:existing?.createdAt||at,updatedAt:at};
    if(!exerciseValidRecord('exercises',item.id,item)){document.getElementById('exerciseFormError').textContent='Enter a name, a measure and a whole number of sets from 1 to 1,000.';return;}
    DB.exerciseTracker.exercises[item.id]=exerciseCopyRecord('exercises',item);save();closeModal();renderTodos();
  };
}
function exerciseEditEntry(id,templateId){
  const existing=DB.exerciseTracker.entries[id],templates=exerciseTemplates(),selected=existing?.exerciseId||templateId||templates[0]?.id;
  if(!selected){exerciseEditTemplate();return;}
  // Removed/renamed exercises keep the name and measure recorded on that day.
  const available=templates.slice();
  if(existing&&!available.some(item=>item.id===existing.exerciseId))available.push({id:existing.exerciseId,name:existing.exerciseName,unit:existing.unit,defaultSets:existing.sets});
  const template=available.find(item=>item.id===selected);if(!template)return;
  openModal('<h2>'+(existing?'Edit activity':'Log activity')+'</h2><form id="exerciseEntryForm"><div class="form-row"><label for="exerciseChoice">Exercise</label><select id="exerciseChoice">'+available.map(item=>'<option value="'+escapeAttr(item.id)+'"'+(item.id===selected?' selected':'')+'>'+escapeHtml(existing&&item.id===existing.exerciseId?existing.exerciseName:item.name)+'</option>').join('')+'</select></div><div class="form-row"><label for="exerciseLogDate">Date</label><input id="exerciseLogDate" type="date" min="0001-01-01" max="9999-12-31" required value="'+(existing?.date||exerciseDate())+'"></div><div class="exercise-form-grid"><div class="form-row"><label for="exerciseQuantity">Amount per set</label><input id="exerciseQuantity" type="number" min="0" max="1000000" required placeholder="e.g. 20" value="'+(existing?.quantity||'')+'"></div><div class="form-row"><label for="exerciseUnit">Measure in</label><select id="exerciseUnit">'+exerciseUnitOptions(existing?.unit||template.unit)+'</select></div><div class="form-row"><label for="exerciseSets">Sets</label><input id="exerciseSets" type="number" min="1" max="1000" step="1" required value="'+(existing?.sets||template.defaultSets)+'"></div></div><p class="exercise-muted">20 reps × 2 sets · 40 seconds × 2 sets · 20 minutes. When measuring in sets, enter the total number of sets in Amount.</p><div class="form-row"><label for="exerciseLogNotes">Notes (optional)</label><textarea id="exerciseLogNotes" maxlength="2000" rows="3" placeholder="e.g. First set 20, second set 18">'+escapeHtml(existing?.notes||'')+'</textarea></div><p id="exerciseFormError" role="alert" class="exercise-error"></p><div class="modal-actions"><button type="button" class="btn secondary" id="exerciseCancel">Cancel</button><button type="submit" class="btn">'+(existing?'Save changes':'Save activity')+'</button></div></form>');
  const choice=document.getElementById('exerciseChoice'),unit=document.getElementById('exerciseUnit'),sets=document.getElementById('exerciseSets'),quantity=document.getElementById('exerciseQuantity');
  exerciseWireUnits(unit,sets,quantity);document.getElementById('exerciseCancel').onclick=closeModal;
  choice.onchange=()=>{const item=available.find(item=>item.id===choice.value);unit.value=item.unit;sets.value=item.defaultSets;unit.dispatchEvent(new Event('change'));};
  quantity.focus();
  document.getElementById('exerciseEntryForm').onsubmit=event=>{
    event.preventDefault();const at=exerciseStamp(existing),chosen=available.find(item=>item.id===choice.value);
    const item={id:existing?.id||uid(),exerciseId:choice.value,exerciseName:existing&&choice.value===existing.exerciseId?existing.exerciseName:chosen.name,date:document.getElementById('exerciseLogDate').value,quantity:Number(quantity.value),unit:unit.value,sets:Number(sets.value),notes:document.getElementById('exerciseLogNotes').value.trim(),deleted:false,createdAt:existing?.createdAt||at,updatedAt:at};
    if(!exerciseValidRecord('entries',item.id,item)){document.getElementById('exerciseFormError').textContent='Choose a valid date and positive amount. Reps, rounds and sets use whole numbers; sets must be from 1 to 1,000.';return;}
    DB.exerciseTracker.entries[item.id]=exerciseCopyRecord('entries',item);
    DB.exerciseTracker.selectedDate={value:item.date,updatedAt:exerciseStamp(DB.exerciseTracker.selectedDate)};
    save();closeModal();renderTodos();
  };
}
/* EXERCISE TRACKER END */
