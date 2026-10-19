const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const previous=cp.execFileSync('git',['show','5d8cc7e:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const js=fs.readFileSync('scripts/exercise-tracker.js','utf8'),css=fs.readFileSync('scripts/exercise-tracker.css','utf8');
let restored=html;assert(restored.includes(js));assert(restored.includes(css));restored=restored.replace(js+'\n','').replace(css+'\n','');
const changes=[
 ['data-todo-mode="tasks" aria-pressed="false">Tasks</button><button type="button" class="btn secondary btn-sm" data-todo-mode="exercise" aria-pressed="false">Exercise</button></div>','data-todo-mode="tasks" aria-pressed="false">Tasks</button></div>'],
 ['\n      <div id="exercisePane" hidden></div>',''],
 ['  d.exerciseTracker = exerciseDefaults(d.exerciseTracker);\n',''],
 ['  exerciseMerge(incoming.exerciseTracker);\n',''],
 ['\n  if(todoMode==="exercise")renderExerciseTracker();\n  document.getElementById("exercisePane").hidden=todoMode!=="exercise";','']
];
for(const [from,to] of changes){assert.equal(restored.split(from).length,2,from);restored=restored.replace(from,to);}
assert.equal(restored,previous,'Unexpected changes to habits/tasks, learning material, progress or backup routines');
for(const script of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/.test(script[1])&&!/\bsrc=/.test(script[1]))new Function(script[2]);
const api=new Function(js+';return {exerciseDefaults,exerciseValidDate,exerciseValidRecord,exerciseNewer,exerciseCopyRecord};\nfunction habitValidMonth(v){return typeof v==="string"&&/^(?!0000)\\d{4}-(0[1-9]|1[0-2])$/.test(v)}\nfunction habitDays(v){const[y,m]=v.split("-").map(Number);return m===2?(y%4===0&&(y%100!==0||y%400===0)?29:28):[4,6,9,11].includes(m)?30:31}')();
for(const date of ['2026-10-19','2028-02-29','2000-02-29','0001-01-01','9999-12-31'])assert(api.exerciseValidDate(date),date);
for(const date of ['2026-02-29','2100-02-29','2026-04-31','2026-00-01','0000-01-01','2026-10-00','2026-10-019','not-date'])assert(!api.exerciseValidDate(date),date);
const at='2026-10-19T12:00:00.000Z';
const entry={id:'entry1',exerciseId:'exercise1',exerciseName:'Plank',date:'2026-10-19',quantity:40,unit:'sec',sets:2,notes:'Keep my note',createdAt:at,updatedAt:at,deleted:false};
assert(api.exerciseValidRecord('entries',entry.id,entry));
for(const bad of [{quantity:0},{quantity:-1},{quantity:Infinity},{unit:'reps',quantity:1.5},{sets:0},{sets:1.5},{unit:'sets',sets:2},{date:'2026-04-31'},{notes:'x'.repeat(2001)},{exerciseId:'__proto__'},{unit:{toString:null}},{updatedAt:'not-time'}])assert(!api.exerciseValidRecord('entries',entry.id,{...entry,...bad}),JSON.stringify(bad));
assert(api.exerciseValidRecord('entries',entry.id,{...entry,unit:'min',quantity:2.5}));
const malformed=JSON.parse('{"entries":{"__proto__":{"id":"__proto__"}},"exercises":[],"selectedDate":{"value":"2026-04-31"}}');
assert.deepEqual(api.exerciseDefaults(malformed),{exercises:{},entries:{},selectedDate:null});
const canonical=api.exerciseCopyRecord('entries',entry);
const reverse=Object.fromEntries(Object.entries(entry).reverse());
assert.deepEqual(api.exerciseCopyRecord('entries',reverse),canonical,'Canonical tie comparison');
assert(api.exerciseNewer({...canonical,deleted:true},canonical),'Deletion wins an equal-timestamp conflict');
assert(!api.exerciseNewer(canonical,{...canonical,deleted:true}),'Old live record must not resurrect deletion');
console.log('PASS: additive tab/store only; all existing code and study content preserved; date/leap-year/record validation, invalid import handling and deterministic deletion-aware conflicts; JavaScript valid.');
