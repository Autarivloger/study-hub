const fs=require('fs'),assert=require('assert'),cp=require('child_process');
const html=fs.readFileSync('study-hub.html','utf8'),data=JSON.parse(html.match(/const JP_WEEK29_CORE = ([^\r\n]+);/)[1]);
assert.equal(data.length,7);data.forEach((l,i)=>{assert.equal(l.id,'29.'+(i+1));assert(l.explain&&l.model&&l.speak&&l.readingQuestions.length>=4);assert(l.reading.replace(/\s/g,'').length>=300);assert(l.practice.length>=15);assert(l.furigana.length>100);l.quiz.forEach(q=>{assert(q[2]>=0&&q[2]<q[1].length);assert.equal(new Set(q[1]).size,q[1].length);});if(i<6){assert.equal(l.vocab.length,20);assert.equal(new Set(l.vocab.map(v=>v[0])).size,20);assert.equal(l.kanji.length,5);assert.equal(l.grammar.length,3);assert.equal(l.quiz.length,14);l.kanji.forEach(k=>assert(/On: .+ · Kun: .+/.test(k[1])));}});
assert.equal(data[6].reviewPractice.length,4);assert.equal(data[6].practice.length,40);assert.equal(data[6].quiz.length,20);assert(data[6].reviewOnly);
for(const l of data.slice(0,6))for(const type of ['vocab','kanji']){const word=l[type][0][0];assert(data[6].reviewPractice.flatMap(g=>g[1]).some(q=>q.some(x=>x.includes(word))),'Day missing from review: '+l.id+' '+type);}
for(const l of data.slice(0,6))assert(data[6].quiz.some(q=>q[0]===l.quiz[4][0]),'Day grammar missing from checkpoint: '+l.id);
const old=cp.execFileSync('git',['show','1d20474:study-hub.html'],{encoding:'utf8',maxBuffer:32e6}).replace(/\r\n/g,'\n');
for(let w=24;w<=28;w++)assert.equal(html.match(new RegExp('const JP_WEEK'+w+'_CORE = ([^\\r\\n]+);'))[1],old.match(new RegExp('const JP_WEEK'+w+'_CORE = ([^\\r\\n]+);'))[1],'Prior Japanese content changed');
const literal=t=>t.replace(/\r\n/g,'\n').split('const DAY_TEACH = ')[1].split('\nconst REST_DAY')[0];assert.equal(literal(html),literal(old),'Python course changed');
for(const match of html.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/g))new Function(match[1]);
console.log('PASS: Japanese Week 29 seven days, 120 vocabulary slots, 30 daily On/Kun kanji, 84 daily quiz questions, full-week 40 drills and 20-question checkpoint, original curriculum preserved, JavaScript syntax');
