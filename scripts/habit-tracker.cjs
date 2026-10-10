const fs=require('fs'),path=require('path');
const root=path.join(__dirname,'..'),target=path.join(root,'study-hub.html');
let html=fs.readFileSync(target,'utf8');
if(html.includes('function renderHabitTracker(')){
 if(!process.argv.includes('--update')) throw Error('Habit tracker exists; use --update to refresh its marked source regions.');
 const cssStart=html.indexOf('/* Monthly tracker uses Study Hub'),cssEnd=html.indexOf('/* Todo */',cssStart);
 const viewStart=html.indexOf('/* Monthly habit tracker: one additive store'),viewEnd=html.indexOf('function renderTaskList(){',viewStart);
 if(cssStart<0 || cssEnd<0 || viewStart<0 || viewEnd<0)throw Error('Habit source boundaries missing');
 html=html.slice(0,viewStart)+fs.readFileSync(path.join(__dirname,'habit-tracker-view.txt'),'utf8')+'\n'+html.slice(viewEnd);
 html=html.slice(0,cssStart)+fs.readFileSync(path.join(__dirname,'habit-tracker.css'),'utf8')+'\n'+html.slice(cssEnd);
 for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(match[1]);
 fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
 console.log('Updated habit view/styles within the existing source boundaries.');
 process.exit(0);
}
function replace(old,next){if(!html.includes(old))throw Error('Missing expected source: '+old.slice(0,80));html=html.replace(old,next);}
replace('  d.todos = d.todos||[]; d.quizzes = d.quizzes||[];',[
 '  d.todos = d.todos||[]; d.quizzes = d.quizzes||[];',
 '  // Additive monthly habits; existing tasks and course stores retain their structure.',
 '  if(!d.habitTracker || typeof d.habitTracker!=="object" || Array.isArray(d.habitTracker)) d.habitTracker={};',
 '  ["months","items","checks"].forEach(function(key){',
 '    if(!d.habitTracker[key] || typeof d.habitTracker[key]!=="object" || Array.isArray(d.habitTracker[key])) d.habitTracker[key]={};',
 '  });',
 '  if(!d.habitTracker.selectedMonth || !habitValidMonth(d.habitTracker.selectedMonth.value)) d.habitTracker.selectedMonth=null;'
].join('\n'));
replace('  DB.reviews.migrationVersion=Math.max(DB.reviews.migrationVersion||0,incoming.reviews.migrationVersion||0);',
 '  DB.reviews.migrationVersion=Math.max(DB.reviews.migrationVersion||0,incoming.reviews.migrationVersion||0);\n\n  habitMerge(incoming.habitTracker);');
replace('      <div id="todoList"></div>',
 '      <div class="ht-tabs" role="group" aria-label="To-do sections"><button type="button" class="btn secondary btn-sm" data-todo-mode="habits" aria-pressed="true">Habits</button><button type="button" class="btn secondary btn-sm" data-todo-mode="tasks" aria-pressed="false">Tasks</button></div>\n      <div id="habitPane"></div>\n      <div id="taskPane" hidden><div id="todoList"></div></div>');
replace('/* ================= TODO ================= */\nfunction renderTodos(){',
 '/* ================= TODO ================= */\n'+fs.readFileSync(path.join(__dirname,'habit-tracker-view.txt'),'utf8')+'\nfunction renderTaskList(){');
replace('/* Todo */',fs.readFileSync(path.join(__dirname,'habit-tracker.css'),'utf8')+'\n/* Todo */');
for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(match[1]);
fs.writeFileSync(target+'.tmp',html,'utf8');fs.renameSync(target+'.tmp',target);
console.log('Added monthly habit tracker, goals, charts, recoverable removal, month history and per-record backup/sync merge.');
