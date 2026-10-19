const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const html=fs.readFileSync('study-hub.html','utf8');
const lessons=JSON.parse(html.match(/const JP_WEEK31_CORE = ([^\r\n]+);/)[1]);
assert.equal(lessons.length,7);
for(const [i,l] of lessons.entries()){
 assert.equal(l.id,'31.'+(i+1));assert(l.studyNav&&l.listening.prompt&&l.readingHelp&&l.model&&l.speak);
 assert(!l.optional&&!l.progressId);assert(l.reading.replace(/\s/g,'').length>=300);
 assert(l.practice.length>=18&&l.readingQuestions.length>=6&&l.summary.length>=4);
 assert(l.enrich.length===3&&l.furigana.length>100);
 if(i<6){
  assert.equal(l.vocab.length,20);assert.equal(new Set(l.vocab.map(v=>v[0])).size,20);assert.equal(l.kanji.length,5);assert.equal(l.quiz.length,14);
  for(const v of l.vocab){assert.equal(v.length,3);assert(/^[ぁ-ゖー]+$/.test(v[1]));assert(v[2].includes('·'));}
 }
 assert.equal(l.grammar.length,3);l.grammar.forEach(g=>assert.equal(g.length,6));
 for(const k of l.kanji){assert(/On: .+ · Kun: .+/.test(k[1]));assert(/（[ぁ-ゖー]+）/.test(k[2]));}
 for(const q of l.quiz){assert.equal(q.length,4);assert(q[3]);assert(q[2]>=0&&q[2]<q[1].length);assert.equal(new Set(q[1]).size,3);}
}
const review=lessons[6];assert(review.reviewOnly);assert.equal(review.quiz.length,24);assert.equal(review.practice.length,48);
assert.equal(review.reviewPractice.length,4);review.reviewPractice.forEach(g=>assert.equal(g[1].length,12));
for(const l of lessons.slice(0,6))for(const kind of ['vocab','kanji'])for(const item of l[kind].slice(0,2))assert(review.reviewPractice.flatMap(g=>g[1]).some(q=>q[0].includes(item[0])));
for(const [word,reading] of Object.entries({'新しい':'あたらしい','配ら':'くばら','来た':'きた','来て':'きて','遅らせ':'おくらせ','曲がっ':'まがっ','二十人分':'にじゅうにんぶん','残り':'のこり','頼ん':'たのん','空いて':'あいて','近道':'ちかみち','構い':'かまい','曜日':'ようび'})){
 for(const l of lessons)if(JSON.stringify({...l,furigana:[]}).includes(word))assert.equal(new Map(l.furigana).get(word),reading,'Contextual reading '+l.id+' '+word);
}
assert.equal(lessons[0].quiz[4][1][lessons[0].quiz[4][2]],'名札の名前を確認する');
assert.equal(lessons[1].quiz[4][1][lessons[1].quiz[4][2]],'十一時までに別館二階');
assert.equal(lessons[3].quiz[4][1][lessons[3].quiz[4][2]],'二袋、一袋五本');
assert.equal(lessons[5].quiz[4][1][lessons[5].quiz[4][2]],'B');
// Restore only the three explicitly edited functions, remove additive blocks,
// and compare every remaining byte (line endings excepted) with the prior commit.
const old=cp.execFileSync('git',['show','c3543b1:study-hub.html'],{encoding:'utf8',maxBuffer:40e6});
const normalize=s=>s.replace(/\r\n/g,'\n');let stripped=normalize(html);
stripped=stripped.replace(/\nconst JP_WEEK31_CORE = [^\n]+;\nJP_WEEK31_CORE.forEach\(function\(l\)\{JP_ENRICH\[l.id\]=l.enrich;\}\);\nJP_LESSONS.push\(\.\.\.JP_WEEK31_CORE\);/,'');
stripped=stripped.replace(/ : week===31 \? '<div class="jp-panel"><h3>Week 31 finish line[^\n]+?<\/button><\/div>'/,'');
stripped=stripped.replace(/\n\/\* JAPANESE LISTENING STYLE START \*\/[\s\S]*?\/\* JAPANESE LISTENING STYLE END \*\/\n/,'');
stripped=stripped.replace(/\/\* JAPANESE LISTENING HELPERS START \*\/[\s\S]*?\/\* JAPANESE LISTENING HELPERS END \*\/\n/,'');
for(const name of ['switchView','jpRenderLesson','renderJapanese']){
 const re=new RegExp('^function '+name+'\\([^\\n]*\\)\\{[\\s\\S]*?^\\}','m');
 const prior=normalize(old).match(re);assert(prior,'Old function '+name);assert(re.test(stripped),'New function '+name);
 stripped=stripped.replace(re,()=>prior[0]);
}
assert.equal(stripped,normalize(old),'Unrelated content, code, styles or storage changed');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
console.log('PASS: 7 complete lessons; 120 vocabulary and 30 On/Kun slots; 108 quizzes; 48 review drills; contextual readings; script syntax; every prior lesson, design and storage function preserved. Only 3 named view/audio functions edited.');
