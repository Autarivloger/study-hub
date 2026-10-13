"""Improve existing Python review/practice without changing curriculum or storage keys."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
target = ROOT / "study-hub.html"
text = target.read_bytes().decode("utf-8")
if "function pythonStudiedParts(" in text:
    raise RuntimeError("Learning patch already applied")

def replace(old, new):
    global text
    if text.count(old) != 1:
        raise RuntimeError("Expected one replacement: " + old[:100])
    text = text.replace(old, new)

def block(start, end, new):
    global text
    a, b = text.index(start), text.index(end, text.index(start))
    text = text[:a] + new.strip() + "\n" + text[b:]

replace('["done","notes"].forEach(function(k){', '["done","notes","partsDone"].forEach(function(k){')
replace('  if(!DB.course.startDate && incoming.course.startDate) DB.course.startDate = incoming.course.startDate;',
        '  if(!DB.course.startDate && incoming.course.startDate) DB.course.startDate = incoming.course.startDate;\n  DB.course.practice.attempts=Math.max(Number(DB.course.practice.attempts)||0,Number(incoming.course.practice.attempts)||0);')
replace('const sig=(h.at || h.date || "")+"|"+(h.rating || "")+"|"+(h.nextReview || "");',
        'const sig=(h.at || h.date || "")+"|"+(h.rating || "")+"|"+(h.nextReview || "")+"|"+(h.questionId||"");')
replace('id="coursePracticeBtn">🏋️ Practice</button>', 'id="coursePracticeBtn">🏋️ Python Practice</button>')
replace('function reviewItems(){return Object.values(DB.reviews.items||{}).filter(function(x){return x&&x.id;});}',
        'function reviewItems(){return Object.values(DB.reviews.items||{}).filter(function(x){return x&&x.id&&(x.subject!=="python"||pythonReviewSourceEligible(x));});}')

block("function pythonSectionsPrompts(", "function reviewEnrollJapanese(", r'''
/* Saved completion defines scope; opening a week never proves it was studied.
   Old completed days include required parts; supplements need their own tick. */
function pythonStudiedParts(w,d,includeCurrent){
  const parts=dayParts(w+"."+d)||[],spot=DB.lastSeen;
  const legacy=Object.keys(DB.lessonsDone||{}).some(function(id){
    const r=PYTHON_LESSON_ROUTES[id];return r&&r.week===w&&r.day===d;
  });
  return parts.map(function(part,i){return {week:w,dayIdx:d,part:i,title:part.title||dayTitleFor(w,d),sections:part.sections||[]};})
    .filter(function(p){
      return isPartDone(w,d,p.part)||(!parts[p.part].optional&&(isDone(w,d)||legacy))||
        (!!includeCurrent&&spot&&spot.kind==="day"&&spot.week===w&&spot.dayIdx===d&&(spot.part||0)===p.part);
    });
}
const pythonPartPromptCache=new Map();
function pythonSectionsPrompts(sections,title){
  const out=[],seen=new Map();let context="";
  function push(p){
    if(!p.q||(!p.a&&!p.answerCode))return;
    const sig=String(p.q).trim()+"|"+String(p.code||"").trim();
    if(seen.has(sig)){const i=seen.get(sig);if(p.options&&!out[i].options)out[i]=p;return;}
    seen.set(sig,out.length);out.push(p);
  }
  (sections||[]).forEach(function(s,i){
    if(s.t==="code")context=s.v||"";
    if(s.t==="ex"){
      const sol=sections[i+1]&&sections[i+1].t==="sol"?sections[i+1]:null;
      if(sol)push({key:"ex:"+i,level:1,kind:"exercise",type:"Write code · Exercise",
        q:s.v,a:sol.why||"Compare your approach with the worked solution.",answerCode:sol.code||"",
        answerOut:sol.out,context:context});
    }else if(s.t==="try"){
      const code=String(s.code||"").trim(),usable=code&&!code.split("\n").every(function(line){return !line.trim()||line.trim().startsWith("#");});
      push({key:"try:"+i,level:1,kind:usable?"predict":"quiz",type:usable?"Predict / explain the code":"Recall question",
        q:s.q||s.v,code:usable?code:"",a:s.a||s.out||s.why,why:s.why||"",
        context:!usable&&/above|following|snippet|example|output/i.test(s.q||s.v||"")?context:""});
    }else if(s.t==="checkpoint"&&s.lesson&&Array.isArray(s.lesson.quiz)){
      s.lesson.quiz.forEach(function(q,n){
        if(!Array.isArray(q.options)||q.options[q.correct]==null)return;
        push({key:"quiz:"+i+":"+n,level:0,kind:"quiz",type:"Lesson quiz",q:q.q,
          options:q.options,correct:q.correct,a:q.options[q.correct],why:q.why||"",
          code:/above|following|snippet|example|output/i.test(q.q||"")?context:""});
      });
    }else if(s.t==="mis"&&s.wrong&&s.right){
      push({key:"mis:"+i,level:1,kind:"debug",type:"Spot and fix the mistake",
        q:"Find the mistake. Explain what is wrong and write the correction.",code:s.wrong,
        answerCode:s.right,a:s.why||"Compare the incorrect and corrected forms."});
    }else if(s.t==="new"&&s.note){
      push({key:"new:"+i,level:0,kind:"concept",type:"Concept recall",
        q:"Explain "+s.v+" in your own words. What is it used for?",a:s.note});
    }
  });
  return out;
}
function pythonPartPrompts(p){
  const id=p.week+"."+p.dayIdx+"."+p.part;
  if(!pythonPartPromptCache.has(id)){
    pythonPartPromptCache.set(id,pythonSectionsPrompts(p.sections,p.title).map(function(q){
      return Object.assign({},q,{key:id+":"+q.key,week:p.week,dayIdx:p.dayIdx,part:p.part,partTitle:p.title});
    }));
  }
  return pythonPartPromptCache.get(id);
}
/* Mix question kinds and completed parts; do not stop at introductory metadata. */
function pythonBalancedPrompts(prompts){
  const kinds=["exercise","predict","quiz","debug","concept"],buckets={};
  kinds.forEach(function(kind){
    const groups=new Map();prompts.filter(function(p){return p.kind===kind;}).forEach(function(p){
      const key=p.week+"."+p.dayIdx+"."+p.part;
      if(!groups.has(key))groups.set(key,[]);groups.get(key).push(p);
    });
    const queue=[];while(Array.from(groups.values()).some(function(g){return g.length;})){
      groups.forEach(function(g){if(g.length)queue.push(g.shift());});
    }buckets[kind]=queue;
  });
  const result=[];while(kinds.some(function(k){return buckets[k].length;})){
    kinds.forEach(function(k){if(buckets[k].length)result.push(buckets[k].shift());});
  }return result;
}
function pythonReviewPrompts(item){
  if(item.sourceType==="python-day"){
    const pos=String(item.sourceId).split(".").map(Number);
    return pythonBalancedPrompts(pythonStudiedParts(pos[0],pos[1],false).flatMap(pythonPartPrompts));
  }
  if(item.sourceType==="python-lesson"&&DB.lessonsDone[item.sourceId]){
    const route=PYTHON_LESSON_ROUTES[item.sourceId];
    if(route)return pythonBalancedPrompts(pythonStudiedParts(route.week,route.day,false).flatMap(pythonPartPrompts));
    const lesson=LEGACY_PYTHON_LESSONS.find(function(l){return l.id===item.sourceId;});
    return lesson?pythonBalancedPrompts(pythonSectionsPrompts(lesson.sections,lesson.title)):[];
  }
  return [];
}
function pythonReviewSourceEligible(item){return pythonReviewPrompts(item).length>0;}
''')

block("function reviewEnrollPythonDay(", "function reviewEnrollPythonLesson(", r'''
function reviewEnrollPythonDay(w,d,completedAt){
  const wk=weekByNum(w),day=d===6?REST_DAY:(wk&&wk[4]&&wk[4][d]);
  const studied=pythonStudiedParts(w,d,false),prompts=pythonBalancedPrompts(studied.flatMap(pythonPartPrompts));
  if(!day||!prompts.length){reviewMarkSourceIncomplete(reviewId("python","day",w+"."+d));return null;}
  const snapshot=prompts.slice(0,12).map(function(p){
    return {level:p.level,type:p.type,q:p.q,a:compactText(p.a||p.answerCode,420)};
  });
  return reviewUpsert({id:reviewId("python","day",w+"."+d),subject:"python",sourceType:"python-day",
    sourceId:w+"."+d,courseName:"Python · 12-month curriculum",lessonName:"Week "+w+" · Day "+(d+1),
    topic:day[0],completedAt:completedAt,summary:compactText(studied.map(function(p){return p.title;}).join(" · "),420),
    concepts:studied.flatMap(function(p){return p.sections;}).filter(function(s){return s.t==="new";})
      .slice(0,6).map(function(s){return compactText(s.v+": "+s.note,220);}),prompts:snapshot});
}
''')
replace('pythonSectionsPrompts(L.sections||[],L.title).forEach(function(p){prompts.push(p);});',
        'pythonSectionsPrompts(L.sections||[],L.title).forEach(function(p){prompts.push({level:p.level,type:p.type,q:p.q,a:compactText(p.a||p.answerCode,420)});});')
replace('  Object.keys(DB.lessonsDone||{}).forEach(function(k){if(!LEGACY_PYTHON_LESSONS.some',
        '''  const partialDays={};
  Object.keys(DB.course.partsDone||{}).forEach(function(k){
    const p=k.split(".").map(Number);
    if(p.length!==3||!dayParts(p[0]+"."+p[1])||!dayParts(p[0]+"."+p[1])[p[2]])return;
    const day=p[0]+"."+p[1],at=DB.course.partsDone[k];
    if(!partialDays[day]||at<partialDays[day])partialDays[day]=at;
  });
  Object.keys(partialDays).forEach(function(k){
    const p=k.split(".").map(Number),id=reviewId("python","day",k);
    if(!DB.reviews.items[id]&&reviewEnrollPythonDay(p[0],p[1],partialDays[k]))changed=true;
  });
  Object.keys(DB.lessonsDone||{}).forEach(function(k){if(!LEGACY_PYTHON_LESSONS.some''')
replace('function reviewPickPrompt(item){\n  const prompts=', '''function reviewPickPrompt(item){
  if(item.subject==="python"){
    const prompts=pythonReviewPrompts(item);
    if(!prompts.length)return null;
    const history=item.history||[],counts=new Map(),last=history.length&&history[history.length-1].questionId;
    history.forEach(function(h){if(h.questionId)counts.set(h.questionId,(counts.get(h.questionId)||0)+1);});
    const available=prompts.filter(function(p){return prompts.length===1||p.key!==last;});
    const least=Math.min.apply(null,available.map(function(p){return counts.get(p.key)||0;}));
    const pool=available.filter(function(p){return (counts.get(p.key)||0)===least;});
    const offset=(reviewView.pythonOffsets||{})[item.id]||0;
    return pool[(history.length+offset)%pool.length];
  }
  const prompts=''')

replace('  item.stage=stage;item.difficulty=rating;', '  if(item.subject==="python"){const prompt=reviewPickPrompt(item);if(prompt)entry.questionId=prompt.key;}\n  item.stage=stage;item.difficulty=rating;')
block("function reviewOpenSource(", "function reviewHomeCardHtml(", r'''
function reviewOpenSource(item){
  if(item.sourceType==="japanese"){jpPage={mode:"lesson",week:Number(item.sourceId.split(".")[0]),lesson:item.sourceId};switchView("japanese");renderJapanese();}
  else if(item.subject==="python"){
    const p=reviewPickPrompt(item),route=PYTHON_LESSON_ROUTES[item.sourceId];
    if(p&&p.week){courseView={mode:"day",week:p.week,dayIdx:p.dayIdx,part:p.part};switchView("course");renderCourse();}
    else if(route){courseView={mode:"day",week:route.week,dayIdx:route.day,part:0};switchView("course");renderCourse();}
  }
  window.scrollTo(0,0);
}
function reviewStart(items){
  if(document.getElementById("reviewLater"))closeModal();
  const source=items===undefined?reviewDueItems(reviewView.subject):items;
  const q=mixedReviews((source||[]).filter(function(x){return x&&(x.subject!=="python"||pythonReviewSourceEligible(x));}));
  if(!q.length){toast("No studied lessons are due in this view");return;}
  reviewView.mode="session";reviewView.queue=q.map(function(x){return x.id;});reviewView.index=0;
  reviewView.revealed=false;reviewView.pythonOffsets={};reviewView.answerChoice=null;reviewView.draft="";
  renderReviews();window.scrollTo(0,0);
}
function openPythonPractice(){
  if(document.getElementById("reviewLater"))closeModal();
  courseView={mode:"practice",week:null,dayIdx:null};practiceView.order=null;
  switchView("course");window.scrollTo(0,0);renderCourse();
}
''')

block("function renderReviewSession(", "function renderReviews(", r'''
function renderReviewSession(){
  const id=reviewView.queue[reviewView.index],item=DB.reviews.items[id];
  const p=item&&reviewPickPrompt(item);
  if(!item||!p){reviewView.mode="dashboard";return renderReviewDashboard();}
  const total=reviewView.queue.length,n=reviewView.index+1,isPython=item.subject==="python";
  const code=function(value){return '<div class="ls-code"><div class="ls-code-tag">python / correction</div><pre><code>'+highlightPy(value)+'</code></pre></div>';};
  const options=p.options?'<div class="ls-quiz">'+p.options.map(function(o,i){
    const mark=reviewView.revealed?(i===p.correct?" correct":i===reviewView.answerChoice?" wrong":""):(i===reviewView.answerChoice?" selected":"");
    return '<button type="button" class="ls-quiz-opt'+mark+'" data-review-option="'+i+'" '+(reviewView.revealed?'disabled':'')+'>'+escapeHtml(o)+'</button>';
  }).join("")+'</div>':"";
  let answer="";
  if(reviewView.revealed){
    answer='<div class="recall-answer"><b>Correct answer / worked model</b>'+
      (p.answerCode?code(p.answerCode):"")+
      (p.answerOut!=null?'<div class="ls-out"><div class="ls-out-tag">output</div><pre><code>'+escapeHtml(p.answerOut)+'</code></pre></div>':"")+
      '<p>'+escapeHtml(p.a||"").replace(/\n/g,"<br>")+'</p>'+
      (p.why&&p.why!==p.a?'<p>'+escapeHtml(p.why).replace(/\n/g,"<br>")+'</p>':"")+'</div>'+
      '<h3>How well did you remember this?</h3><div class="recall-grade"><button type="button" data-grade="forgot">🟥 Forgot</button><button type="button" data-grade="hard">🟨 Hard</button><button type="button" data-grade="good">🟩 Good</button><button type="button" data-grade="easy">🟦 Easy</button></div>';
  }
  return '<div class="review-wrap review-session"><button type="button" class="back-link" data-review-exit="1">← Review dashboard</button><div class="recall-card">'+
    '<div class="recall-progress">'+n+' of '+total+' · '+reviewSubjectLabel(item.subject)+' · '+escapeHtml(item.lessonName)+(isPython&&p.part!=null?' · Part '+(p.part+1):'')+'</div>'+
    (isPython&&p.partTitle?'<p class="jp-muted">'+escapeHtml(p.partTitle)+'</p>':"")+
    '<span class="recall-type">'+escapeHtml(p.type)+'</span><div class="recall-q">'+escapeHtml(p.q).replace(/\n/g,"<br>")+'</div>'+
    (p.code?code(p.code):"")+
    (p.context?'<details class="python-context"><summary>Lesson context / reference example</summary>'+code(p.context)+'</details>':"")+options+
    (isPython?'<label class="python-attempt">Your answer / code (optional)<textarea id="reviewAttempt" spellcheck="false" placeholder="Try it yourself before showing the answer.">'+escapeHtml(reviewView.draft||"")+'</textarea></label>':"")+
    (reviewView.revealed?answer:'<p class="jp-muted">Answer aloud, on paper, or run your code in your Python editor before revealing.</p><button type="button" class="btn" data-review-reveal="1">Show answer</button>')+
    '<div class="jp-actions" style="margin-top:18px">'+
    (isPython?'<button type="button" class="btn secondary btn-sm" data-review-another="1">🔀 Another question</button>':"")+
    '<button type="button" class="btn secondary btn-sm" data-review-source="'+escapeHtml(item.id)+'">Open original lesson</button></div></div></div>';
}
''')
replace('  body.innerHTML=reviewView.mode==="session"?', '  if(migrateCompletedToReviews())save();\n  body.innerHTML=reviewView.mode==="session"?')
replace('    if(b.dataset.reviewStart){reviewStart();return;}', '''    if(b.dataset.pythonPractice){openPythonPractice();return;}
    if(b.dataset.reviewOption!=null){reviewView.answerChoice=Number(b.dataset.reviewOption);renderReviews();return;}
    if(b.dataset.reviewAnother){
      const id=reviewView.queue[reviewView.index];reviewView.pythonOffsets=reviewView.pythonOffsets||{};
      reviewView.pythonOffsets[id]=(reviewView.pythonOffsets[id]||0)+1;
      reviewView.revealed=false;reviewView.answerChoice=null;reviewView.draft="";renderReviews();return;
    }
    if(b.dataset.reviewStart){reviewStart();return;}''')
replace('if(b.dataset.grade){const item=', 'if(b.dataset.grade&&reviewView.revealed){const item=')
replace('reviewView.index++;reviewView.revealed=false;if(reviewView.index>=',
        'reviewView.index++;reviewView.revealed=false;reviewView.answerChoice=null;reviewView.draft="";if(reviewView.index>=')
replace('body.addEventListener("input",function(ev){if(ev.target.id==="reviewSearch")',
        'body.addEventListener("input",function(ev){if(ev.target.id==="reviewAttempt"){reviewView.draft=ev.target.value;return;}if(ev.target.id==="reviewSearch")')
replace("    '<div class=\"review-stats\"><div", '''    (reviewView.subject!=="japanese"?'<section class="review-panel python-practice-link"><h3>🐍 Python Practice</h3><p>Exercises from completed lesson parts, with an optional current-part filter. Choose a week or mix everything you have studied.</p><button type="button" class="btn secondary" data-python-practice="1">Open Python Practice →</button></section>':'')+
    '<div class="review-stats"><div''')

replace('function showReviewNotice(){', 'function showReviewNotice(){\n  if(document.getElementById("view-reviews").classList.contains("active")||\n     (document.getElementById("view-course").classList.contains("active")&&courseView.mode==="practice"))return;')
replace('    reviewMarkSourceIncomplete(reviewId("python","day",k));',
        '    reviewEnrollPythonDay(weekNum, dayIdx, nowISO());')
replace('  if(parts[i] && parts[i].optional){ save(); return; }',
        '  if(parts[i] && parts[i].optional){ reviewEnrollPythonDay(w,d,DB.course.partsDone[k]||nowISO()); save(); return; }')
replace('    reviewEnrollPythonDay(w, d, DB.course.done[dk]);\n', '')
replace('    reviewMarkSourceIncomplete(reviewId("python","day",dk));\n  }\n  save();',
        '  }\n  reviewEnrollPythonDay(w,d,DB.course.done[dk]||DB.course.partsDone[k]||nowISO());\n  save();')

block("function corePool(){", "/* Practice filters,", r'''
function corePool(){
  if(corePoolCache)return corePoolCache;
  const out=[];
  taughtWeeks().forEach(function(w){
    for(let d=0;d<7;d++){
      let n=0;
      (dayParts(w+"."+d)||[]).forEach(function(part,pi){
        let context="";
        (part.sections||[]).forEach(function(s,i){
          if(s.t==="code")context=s.v||"";
          if(s.t!=="ex")return;
          const next=part.sections[i+1],sol=next&&next.t==="sol"?next:null;
          out.push({id:s.practiceId||w+"."+d+"."+n,week:w,day:d+1,part:pi,
            partTitle:part.title||dayTitleFor(w,d),topic:dayTitleFor(w,d),ex:s,sol:sol,context:context});
          n++;
        });
      });
    }
  });
  corePoolCache=out;return out;
}
''')
replace('  block: "w1",', '  block: "all",')
replace('  readyOnly: true,\n  order:', '  readyOnly: true,\n  includeCurrent: true,\n  order:')

replace('function practiceSolved(){', 'let pythonPracticeDraftDirty=false;\nwindow.addEventListener("pagehide",function(){if(pythonPracticeDraftDirty)save();});\nfunction practiceSolved(){')

block("function practiceStats(){", "function renderCorePractice(){", r'''
function pythonPracticePool(){
  return corePool().filter(function(p){
    return !practiceView.readyOnly||pythonStudiedParts(p.week,p.day-1,practiceView.includeCurrent).some(function(s){return s.part===p.part;});
  });
}
function practiceStats(){
  const pool=pythonPracticePool(),solved=practiceSolved(),byWeek={};
  pool.forEach(function(p){byWeek[p.week]=byWeek[p.week]||{total:0,done:0};byWeek[p.week].total++;if(solved[p.id])byWeek[p.week].done++;});
  return {total:pool.length,done:pool.filter(function(p){return solved[p.id];}).length,byWeek:byWeek};
}
function buildPracticeSet(){
  const blocks=coreBlocks(),block=blocks.find(function(b){return b.key===practiceView.block;})||blocks[0],solved=practiceSolved();
  const pool=pythonPracticePool().filter(function(p){return block.weeks.includes(p.week)&&(!practiceView.unsolvedOnly||!solved[p.id]);});
  const groups=new Map();
  shuffled(pool).forEach(function(p){const k=p.week+"."+p.day+"."+p.part;if(!groups.has(k))groups.set(k,[]);groups.get(k).push(p);});
  const mixed=[];while(Array.from(groups.values()).some(function(g){return g.length;})){
    groups.forEach(function(g){if(g.length)mixed.push(g.shift());});
  }
  if(mixed.length>1&&mixed[0].id===practiceView.avoidFirst){const j=mixed.findIndex(function(p){return p.id!==practiceView.avoidFirst;});[mixed[0],mixed[j]]=[mixed[j],mixed[0]];}
  return practiceView.size===0?mixed:mixed.slice(0,practiceView.size);
}
''')

block("function renderCorePractice(){", "/* Fisher-Yates:", r'''
function renderCorePractice(){
  const el=document.getElementById("courseBody"),stats=practiceStats(),solved=practiceSolved(),eligible=new Set(pythonPracticePool().map(function(p){return p.id;}));
  if(!practiceView.order)practiceView.order=buildPracticeSet();
  practiceView.order=practiceView.order.filter(function(p){return eligible.has(p.id);});
  const set=practiceView.order;tryCount=0;solCount=0;
  const items=set.map(function(p,n){
    const secs=[p.ex];if(p.sol)secs.push(p.sol);
    const key="python-practice|"+p.id;
    return '<div class="prac-item"><div class="prac-num">Exercise '+(n+1)+' of '+set.length+' · Week '+p.week+' Day '+p.day+' · Part '+(p.part+1)+'</div>'+
      '<h3 class="ls-h">'+escapeHtml(p.partTitle)+'</h3>'+renderSections(secs)+
      (p.context?'<details class="python-context"><summary>Lesson context / reference example</summary><div class="ls-code"><pre><code>'+highlightPy(p.context)+'</code></pre></div></details>':"")+
      '<label class="python-attempt">Your attempt / notes <span class="jp-muted">(saved)</span><textarea data-practice-attempt="'+escapeHtml(key)+'" spellcheck="false" placeholder="Write your approach or code. Run it in your own Python editor.">'+escapeHtml(DB.headNotes[key]||"")+'</textarea></label>'+
      '<div class="jp-actions"><button type="button" class="btn '+(solved[p.id]?'secondary':'')+' btn-sm" data-solveid="'+escapeHtml(p.id)+'">'+(solved[p.id]?'✓ Solved':'Mark solved')+'</button>'+
      '<button type="button" class="btn secondary btn-sm" data-practice-source="'+p.week+'.'+(p.day-1)+'.'+p.part+'">Open this lesson</button></div></div>';
  }).join("");
  el.innerHTML='<button type="button" class="back-link" id="backFromPractice">← Course</button>'+
    '<div class="day-header"><div class="dh-eyebrow">Exercises from your lessons</div><h2>🏋️ Python Practice</h2></div>'+
    '<div class="course-hero"><div class="ch-label">'+(practiceView.readyOnly?'Your studied exercises':'All authored exercises')+'</div>'+
    '<div class="ch-big"><b>'+stats.done+'</b> <span>/ '+stats.total+' practised</span></div>'+progressBar(stats.done,stats.total)+
    '<div class="ch-sub">Completion is measured by lesson parts, not the date or the highest week you opened.</div></div>'+
    '<div class="section-label">Build a practice set</div><div class="prac-controls">'+
    '<label>Week / topic<select id="pracBlock">'+coreBlocks().map(function(b){return '<option value="'+b.key+'" '+(practiceView.block===b.key?'selected':'')+'>'+escapeHtml(b.key==="all"?"All studied weeks":b.label)+'</option>';}).join("")+'</select></label>'+
    '<label>Exercises<select id="pracSize">'+[5,10,20,50,0].map(function(n){return '<option value="'+n+'" '+(practiceView.size===n?'selected':'')+'>'+(n||"All")+'</option>';}).join("")+'</select></label>'+
    '<label class="prac-check"><input type="checkbox" id="pracReady" '+(practiceView.readyOnly?'checked':'')+'> Studied lessons only</label>'+
    '<label class="prac-check"><input type="checkbox" id="pracCurrent" '+(practiceView.includeCurrent?'checked':'')+' '+(!practiceView.readyOnly?'disabled':'')+'> Include current part</label>'+
    '<label class="prac-check"><input type="checkbox" id="pracUnsolved" '+(practiceView.unsolvedOnly?'checked':'')+'> Only unsolved</label>'+
    '<button type="button" class="btn btn-sm" id="pracNew">🔀 Shuffle / New set</button></div>'+
    '<p class="hint">'+(practiceView.readyOnly?'Uses completed parts and, when enabled, only your exact current part. Later parts and unopened days are excluded.':'Exploration mode: exercises from all authored lessons, including topics you may not have studied.')+
    ' Mark lesson parts complete to keep them in your practice pool. Your old solved records remain saved.</p>'+
    '<div class="section-label">'+set.length+' exercises, shuffled across lesson parts</div><div class="day-teach">'+
    (set.length?items:'<div class="empty-state"><div class="big">📖</div><p>No studied exercises match these filters.</p><p>Complete a lesson part, include your current part, choose another week, or turn off Only unsolved.</p><button type="button" class="btn secondary" id="practiceResume">Continue learning →</button></div>')+'</div>';
  function reset(){practiceView.order=null;renderCorePractice();}
  document.getElementById("pracReady").onchange=function(e){practiceView.readyOnly=e.target.checked;reset();};
  document.getElementById("pracCurrent").onchange=function(e){practiceView.includeCurrent=e.target.checked;reset();};
  document.getElementById("pracBlock").onchange=function(e){practiceView.block=e.target.value;reset();};
  document.getElementById("pracSize").onchange=function(e){practiceView.size=Number(e.target.value);reset();};
  document.getElementById("pracUnsolved").onchange=function(e){practiceView.unsolvedOnly=e.target.checked;reset();};
  document.getElementById("pracNew").onclick=function(){practiceView.avoidFirst=set[0]&&set[0].id;practiceView.order=null;window.scrollTo(0,0);renderCorePractice();};
  document.getElementById("backFromPractice").onclick=function(){courseView={mode:"overview",week:null,dayIdx:null};window.scrollTo(0,0);renderCourse();};
  const resume=document.getElementById("practiceResume");if(resume)resume.onclick=function(){document.getElementById("courseTodayBtn").click();};
  wireRevealButtons(el);
  el.querySelectorAll("[data-practice-source]").forEach(function(b){b.onclick=function(){
    const pos=b.dataset.practiceSource.split(".").map(Number);courseView={mode:"day",week:pos[0],dayIdx:pos[1],part:pos[2]};renderCourse();window.scrollTo(0,0);
  };});
  el.querySelectorAll("[data-practice-attempt]").forEach(function(input){
    let timer;input.oninput=function(){const key=input.dataset.practiceAttempt,value=input.value;DB.headNotes[key]=value;pythonPracticeDraftDirty=true;clearTimeout(timer);timer=setTimeout(function(){save();pythonPracticeDraftDirty=false;},400);};
    input.onblur=function(){clearTimeout(timer);save();pythonPracticeDraftDirty=false;};
  });
  el.querySelectorAll("[data-solveid]").forEach(function(b){b.onclick=function(){
    const id=b.dataset.solveid;if(DB.course.practice.solved[id])delete DB.course.practice.solved[id];
    else{DB.course.practice.solved[id]=true;DB.course.practice.attempts=(DB.course.practice.attempts||0)+1;}
    save();renderCorePractice();renderSideStats();
  };});
}
''')

block('document.getElementById("coursePracticeBtn").addEventListener(', '/* Resume, not Today:', r'''
document.getElementById("coursePracticeBtn").addEventListener("click",openPythonPractice);
''')
replace('    ${resumeCard()}\n', '''    ${resumeCard()}
    <div class="review-panel python-practice-link"><h3>🐍 Python Practice</h3><p>Revisit exercises from the lesson parts you have studied. Mix weeks or choose one topic, then shuffle a new set.</p><button type="button" class="btn secondary" id="pythonPracticeHome">Open Python Practice →</button></div>
''')
replace('  wireResumeCard();\n  el.querySelectorAll("[data-week]")',
        '  wireResumeCard();\n  document.getElementById("pythonPracticeHome").onclick=openPythonPractice;\n  el.querySelectorAll("[data-week]")')
replace('/* Notes */\n#noteTitle{', '''/* Python review and practice use the established lesson components. */
.python-practice-link{margin-bottom:16px}.python-practice-link p{line-height:1.6;color:var(--text-dim)}
.python-attempt{display:block;font-size:13px;font-weight:700;margin:14px 0}
.python-attempt textarea{display:block;width:100%;min-height:150px;padding:12px;margin-top:7px;resize:vertical;background:var(--bg-soft);color:var(--text);border:1px solid var(--border);border-radius:9px;font:14px/1.6 Consolas,monospace}
.python-context{margin:12px 0;padding:10px;border:1px solid var(--border);border-radius:9px;min-width:0}
.python-context summary{cursor:pointer;font-size:13px;font-weight:700}
.recall-card{min-width:0}.recall-q,.recall-answer,.python-practice-link p{overflow-wrap:anywhere}
.recall-card .ls-quiz-opt.selected{border-color:var(--accent);background:var(--accent-soft)}
.recall-card pre{white-space:pre;overflow-x:auto;max-width:100%}
@media(max-width:600px){.recall-card{padding:16px}.recall-q{font-size:18px}.prac-controls select{max-width:100%}.prac-controls label{max-width:100%}}

/* Notes */
#noteTitle{''')

temporary = target.with_suffix(".html.tmp")
temporary.write_bytes(text.encode("utf-8"))
temporary.replace(target)
print("Updated Python review/practice using existing progress, review history and note storage.")
