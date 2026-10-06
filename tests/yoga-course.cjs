const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const current=fs.readFileSync('study-hub.html','utf8').replace(/\r\n/g,'\n'),baseline=cp.execFileSync('git',['show','464186e:study-hub.html'],{encoding:'utf8',maxBuffer:40e6}).replace(/\r\n/g,'\n');
function teaching(s){const a=s.indexOf('const DAY_TEACH = ')+18,b=s.indexOf('\n};\n\nconst REST_DAY',a);return Function('return ('+s.slice(a,b+2)+')')();}
assert.deepEqual(teaching(current),teaching(baseline),'Python teaching changed');
for(const m of baseline.matchAll(/const JP_WEEK\d+_CORE = [\s\S]*?;\n/g))assert(current.includes(m[0]),'Japanese lesson literal changed: '+m[0].slice(0,30));
function defaults(s){return s.slice(s.indexOf('function applyDefaults('),s.indexOf('const ARRAY_KEYS'));}
assert.equal(defaults(current),defaults(baseline),'Storage defaults/schema changed');
for(const name of ['ARRAY_KEYS','MAP_KEYS']){const re=new RegExp('const '+name+'[^;]+;');assert.equal(current.match(re)[0],baseline.match(re)[0]);}
const a=current.indexOf('const YOGA_COURSE = ')+20,b=current.indexOf(';\n\n/* ================= YOGA',a),course=JSON.parse(current.slice(a,b));
assert.deepEqual(course,require('../scripts/yoga-course.cjs'));
assert.equal(course.sessions.length,7);assert.equal(course.poses.length,10);assert.equal(course.meditations.length,5);assert.equal(course.gita.length,4);
const ids=new Set();for(const s of course.sessions){assert(s.id.startsWith('yoga:'));assert(!ids.has(s.id));ids.add(s.id);for(const id of s.poses)assert(course.poses.some(p=>p.id===id));assert(course.meditations.some(p=>p.id===s.meditation));assert(course.gita.some(p=>p.id===s.gita));assert.equal(s.quiz.quiz.length,3);for(const q of s.quiz.quiz)assert(q.options[q.correct]);}
assert.equal((current.match(/data-view="lessons"[^>]*><span class="ic">🧘<\/span>Yoga &amp; Meditation/g)||[]).length,2,'Navigation rename missing');
for(const m of current.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(m[1]);
console.log('PASS: Yoga content/references,21 quiz questions; Python/Japanese curriculum and storage schema retained');
