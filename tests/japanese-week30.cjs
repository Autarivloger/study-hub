const fs=require('fs'),assert=require('assert/strict'),cp=require('child_process');
const html=fs.readFileSync('study-hub.html','utf8');
const lessons=JSON.parse(html.match(/const JP_WEEK30_CORE = ([^\r\n]+);/)[1]);
assert.equal(lessons.length,7);
for(const [i,l] of lessons.entries()){
 assert.equal(l.id,'30.'+(i+1));assert.equal(l.studyNav,true);
 assert(l.explain&&l.model&&l.speak&&l.readingHelp&&l.enrich.length===3);
 assert(l.reading.replace(/\s/g,'').length>=300);
 assert(l.readingQuestions.length>=6&&l.practice.length>=18&&l.furigana.length>100);
 assert(l.summary.length>=4);
 assert(!l.progressId&&!l.optional,'Stable independent new lesson IDs');
 for(const q of l.quiz){assert.equal(q.length,4);assert(q[3]);assert(Number.isInteger(q[2])&&q[2]>=0&&q[2]<q[1].length);assert.equal(new Set(q[1]).size,q[1].length);}
 if(i<6){
  assert.equal(l.vocab.length,20);assert.equal(new Set(l.vocab.map(v=>v[0])).size,20);
  assert.equal(l.kanji.length,5);assert.equal(l.grammar.length,3);assert.equal(l.quiz.length,14);
  l.vocab.forEach(v=>{assert.equal(v.length,3);assert(/^[ぁ-ゖー]+$/.test(v[1]));assert(v[2].includes('·'));});
  l.kanji.forEach(k=>{assert(/On: .+ · Kun: .+/.test(k[1]));assert(/（[ぁ-ゖー]+）/.test(k[2]));});
  l.grammar.forEach(g=>assert.equal(g.length,6));
 }
}
const review=lessons[6];assert(review.reviewOnly);assert.equal(review.reviewPractice.length,4);
const readings={'回数':'かいすう','日時':'にちじ','休館日':'きゅうかんび','工事中':'こうじちゅう','その分':'そのぶん','日本語':'にほんご','合わせ':'あわせ','待つ間':'まつあいだ','二十人中':'にじゅうにんちゅう','一回':'いっかい','何を':'なにを'};
for(const lesson of lessons)for(const [word,reading] of Object.entries(readings))if(lesson.reading.includes(word))assert.equal(new Map(lesson.furigana).get(word),reading,'Contextual reading '+lesson.id+' '+word);
review.reviewPractice.forEach(g=>assert.equal(g[1].length,12));
assert.equal(review.practice.length,48);assert.equal(review.quiz.length,24);
for(const l of lessons.slice(0,6)){
 for(const kind of ['vocab','kanji'])for(const item of l[kind].slice(0,2))assert(review.reviewPractice.flatMap(g=>g[1]).some(q=>q[0].includes(item[0])),'Review missing '+l.id+' '+item[0]);
 for(const index of [4,8])assert(review.quiz.some(q=>q[0]===l.quiz[index][0]),'Review must sample every day');
}
// Audit the entire old file, including Python, Japanese 1–29, UI, storage and import.
const old=cp.execFileSync('git',['show','5ac54ea:study-hub.html'],{encoding:'utf8',maxBuffer:40e6});
const normalize=s=>s.replace(/\r\n/g,'\n');
let stripped=html.replace(/\nconst JP_WEEK30_CORE = [^\r\n]+;\nJP_WEEK30_CORE.forEach\(function\(l\)\{JP_ENRICH\[l.id\]=l.enrich;\}\);\nJP_LESSONS.push\(\.\.\.JP_WEEK30_CORE\);/,'');
stripped=stripped.replace(/ : week===30 \? '<div class="jp-panel"><h3>Week 30 finish line[^\r\n]+?<\/button><\/div>'/,'');
assert.equal(normalize(stripped),normalize(old),'Unrelated code/content changed');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){
 if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);
}
console.log('PASS: 7 days; 120 vocabulary slots; 30 On/Kun kanji; 108 quiz questions; 48 review drills covering all 6 days; all previous HTML content/UI/storage preserved exactly; executable scripts and JSON valid.');
