const fs=require('fs'),vm=require('vm'),assert=require('assert');
const source=fs.readFileSync('study-hub.html','utf8');const ctx={};vm.createContext(ctx);
vm.runInContext(source.slice(source.indexOf('const JP_LESSONS ='),source.indexOf('const JP_FURIGANA_AUTO'))+'\nthis.lessons=JP_LESSONS;this.reading=jpKanjiReadingWithOnKun;',ctx);
let total=0,retained=0;
for(const lesson of ctx.lessons)for(const item of lesson.kanji||[]){
  total++;assert(/On:\s*.+ · Kun:\s*.+/.test(item[1]),'Missing On/Kun: '+lesson.id+' '+item[0]);
  assert(item[2],'Context example lost: '+lesson.id+' '+item[0]);
  if(item[1].includes('Lesson reading:'))retained++;
}
assert.equal(ctx.lessons.filter(l=>Number(l.id.split(".")[0])<=27).reduce((n,l)=>n+(l.kanji||[]).length,0),961);assert(total>=961);assert.equal(retained,280);
assert(ctx.lessons.filter(l=>l.id.startsWith('1.')).every(l=>(l.kanji||[]).every(k=>/On:/.test(k[1])&&/Kun:/.test(k[1]))),'Week1 missed');
assert.equal(ctx.reading('食','On: ショク · Kun: た(べる)'),'On: ショク · Kun: た(べる)','Existing readings replaced');
assert(ctx.reading('員','いん').includes('Kun: — (no dictionary Kun reading)'),'Absent Kun fabricated');
assert(ctx.reading('食','たべる').includes('Lesson reading: たべる'),'Original contextual reading lost');
const data=JSON.parse(fs.readFileSync('japanese-kanji-readings.json','utf8'));
assert.equal(Object.keys(data.readings).length,208);assert.equal(data.licence,'CC BY-SA 4.0');
const start=source.indexOf('function jpStudyItemHtml('),end=source.indexOf('\n}',start)+2;
ctx.DB={japanese:{checks:{}}};ctx.jpFuriganaOn=false;ctx.jpHardKey=(t,w)=>t+':'+w;ctx.escapeHtml=x=>String(x);
vm.runInContext(source.slice(start,end)+'\nthis.render=jpStudyItemHtml;',ctx);
const hidden=ctx.render('k',['食','たべる','食べる']);assert(hidden.includes('Show On/Kun &amp; meaning'));assert(hidden.includes('<details')&&!hidden.includes('<details open'),'Answers exposed by default');assert(hidden.includes('On: ショク'));
ctx.jpFuriganaOn=true;assert(ctx.render('k',['食','たべる','食べる']).includes('jp-kanji-readings'),'Reading control does not show kanji readings');
assert(ctx.render('v',['食べる','たべる','eat']).includes('Show reading &amp; meaning'),'Vocabulary disclosure changed');
console.log('PASS: all '+total+' kanji entries, 280 enriched entries, retained examples/readings, no fabricated Kun, hidden answers and Furigana display.');
