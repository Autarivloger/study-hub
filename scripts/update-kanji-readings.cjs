// Refresh the selected KANJIDIC2 extract; lesson IDs, examples and saved data stay intact.
const fs=require('fs'),path=require('path'),zlib=require('zlib');
async function main(){
  const root=path.resolve(__dirname,'..'),dataPath=path.join(root,'japanese-kanji-readings.json'),htmlPath=path.join(root,'study-hub.html');
  const data=JSON.parse(fs.readFileSync(dataPath,'utf8')),wanted=new Set(Object.keys(data.readings));
  const response=await fetch('https://www.edrdg.org/kanjidic/kanjidic2.xml.gz',{signal:AbortSignal.timeout(30000)});
  if(!response.ok)throw Error('Dictionary download failed: '+response.status);
  const bytes=Buffer.from(await response.arrayBuffer());
  const xml=(bytes[0]===31&&bytes[1]===139?zlib.gunzipSync(bytes):bytes).toString('utf8'),readings={};
  const format=x=>x.replace(/\.([^.-]+)/g,'($1)');
  for(const m of xml.matchAll(/<character>([\s\S]*?)<\/character>/g)){
    const k=m[1].match(/<literal>(.*?)<\/literal>/)[1];if(!wanted.has(k))continue;
    const on=[],kun=[];
    for(const r of m[1].matchAll(/<reading\s+([^>]+)>([^<]+)<\/reading>/g)){
      if(/r_type="ja_on"/.test(r[1]))on.push(format(r[2]));
      if(/r_type="ja_kun"/.test(r[1]))kun.push(format(r[2]));
    }
    readings[k]='On: '+(on.join('・')||'— (no dictionary On reading)')+' · Kun: '+(kun.join('・')||'— (no dictionary Kun reading)');
  }
  if(Object.keys(readings).length!==wanted.size)throw Error('Incomplete dictionary; files not updated');
  const source=fs.readFileSync(htmlPath,'utf8');
  const marker=/const JP_KANJI_READING_ADDITIONS = [^\r\n]+;/;
  if(!marker.test(source))throw Error('Embedded readings marker missing; files not updated');
  const result=source.replace(marker,'const JP_KANJI_READING_ADDITIONS = '+JSON.stringify(readings)+';');
  const vm=require('vm');for(const m of result.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script>/gi))new vm.Script(m[1]);
  data.readings=readings;data.checkedOn=new Date().toISOString().slice(0,10);
  fs.writeFileSync(htmlPath+'.tmp',result);fs.writeFileSync(dataPath+'.tmp',JSON.stringify(data,null,2)+'\n');
  fs.renameSync(htmlPath+'.tmp',htmlPath);fs.renameSync(dataPath+'.tmp',dataPath);
  console.log('Refreshed '+wanted.size+' selected kanji readings. Run the kanji and Japanese browser tests before publishing.');
}
main().catch(e=>{console.error(e.message);process.exitCode=1;});
