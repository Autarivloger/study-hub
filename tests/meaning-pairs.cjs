const fs=require('fs'),cp=require('child_process'),assert=require('assert/strict');
const old=cp.execFileSync('git',['show','89d109a:study-hub.html'],{encoding:'utf8',maxBuffer:50e6});
const html=fs.readFileSync('study-hub.html','utf8');let restored=html;
function part(s,start,end){const a=s.indexOf(start),b=s.indexOf(end,a+start.length);assert(a>=0&&b>a,start);return s.slice(a,b);}
const cssStart='/* JAPANESE STUDY DESIGN START',cssEnd='/* JAPANESE STUDY DESIGN END */';
const css=fs.readFileSync('scripts/japanese-theme.css','utf8').trimEnd();assert(html.includes(css));
restored=restored.replace(part(restored,cssStart,cssEnd),part(old,cssStart,cssEnd));
const addition='  if(!d.japanese.meaningPairs || typeof d.japanese.meaningPairs!=="object" || Array.isArray(d.japanese.meaningPairs)) d.japanese.meaningPairs={};\n';
assert(restored.includes(addition));restored=restored.replace(addition,'');
const merge=part(restored,'  // Pair edits/additions share','  /* Review sync');restored=restored.replace(merge,'');
const helpers=part(restored,'function jpMeaningPairValid(','function jpMeaningCards(');restored=restored.replace(helpers,'');
for(const name of ['jpStudyItemHtml','jpMeaningCards','jpMeaningAddCards','jpMeaningListHtml','jpRenderMeanings','renderJapanese']){
 const prefix='function '+name+'(';
 restored=restored.replace(part(restored,prefix,'\nfunction '),part(old,prefix,'\nfunction '));
}
assert.equal(restored,old,'Unexpected curriculum/storage/other feature changes');
const valid=new Function(part(html,'function jpMeaningPairValid(','function jpMeaningPairs(')+';return jpMeaningPairValid;')();
const good={type:'opposites',baseIndex:0,pair:['大きい','おおきい','big','小さい','ちいさい','small','Size'],updatedAt:'2026-10-19T00:00:00Z'};
assert(valid('opposites:b:0',good));assert(valid('opposites:u:test',{...good,baseIndex:null}));
for(const [key,record] of [['__proto__',good],['opposites:b:1',good],['synonyms:b:0',good],['opposites:u:test',good],['opposites:b:0',{...good,updatedAt:'invalid'}],['opposites:b:0',{...good,pair:['','','','','','','']}],['opposites:b:0',{...good,pair:[...good.pair.slice(0,6),'x'.repeat(2001)]}],['opposites:b:0',{...good,pair:[{},...good.pair.slice(1)]}]])assert(!valid(key,record),'Invalid pair accepted '+key);
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g))if(!/type=["']application\/json/.test(m[1])&&!/\bsrc=/.test(m[1]))new Function(m[2]);
console.log('PASS: only authorised pair UI, one additive map/default and per-pair merge changed; all original content and unrelated code byte-identical; record validation and JavaScript valid.');
