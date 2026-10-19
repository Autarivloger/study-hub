// Opt-in listening UI. Existing lessons keep their reading-first presentation.
const fs=require('fs'),assert=require('assert/strict'),path=require('path');
const file=path.join(__dirname,'../study-hub.html');let html=fs.readFileSync(file,'utf8');
if(html.includes('/* JAPANESE LISTENING HELPERS START */')){console.log('Listening UI already installed.');process.exit(0);}
const helpers=`/* JAPANESE LISTENING HELPERS START */
let jpSpeechCurrent=null;
function jpStopSpeech(){
  if(!jpSpeechCurrent)return;
  jpSpeechCurrent.onend=null;jpSpeechCurrent.onerror=null;jpSpeechCurrent=null;
  if("speechSynthesis" in window)speechSynthesis.cancel();
  const status=document.getElementById('jpListeningStatus');
  if(status)status.textContent='Stopped. Replay whenever you are ready.';
}
function jpSpeakReading(lesson,rate){
  jpStopSpeech();
  const status=document.getElementById('jpListeningStatus');
  const message=function(text){if(status)status.textContent=text;else toast(text);};
  if(!lesson)return;
  if(!('speechSynthesis' in window)||!('SpeechSynthesisUtterance' in window)){
    message('Speech is unavailable. You can open the transcript for reading practice.');return;
  }
  const voice=speechSynthesis.getVoices().find(function(v){return /^ja(?:-|$)/i.test(v.lang)&&v.localService;});
  if(!voice){message('No offline Japanese voice is available yet. If one is installed, try Play again after it loads. Otherwise use the transcript for reading practice.');return;}
  const utterance=new SpeechSynthesisUtterance(lesson.reading);
  utterance.voice=voice;utterance.lang='ja-JP';utterance.rate=rate;
  jpSpeechCurrent=utterance;
  utterance.onend=function(){if(jpSpeechCurrent!==utterance)return;jpSpeechCurrent=null;message('Finished. Write your answer before revealing the transcript.');};
  utterance.onerror=function(){if(jpSpeechCurrent!==utterance)return;jpSpeechCurrent=null;message('Playback failed. Try Play again, or use the transcript for reading practice.');};
  message('Playing at '+rate+'×. Keep the transcript closed for your first attempt.');
  try{speechSynthesis.cancel();speechSynthesis.speak(utterance);}catch(e){jpSpeechCurrent=null;message('Playback could not start. Try again or open the transcript.');}
}
function jpListeningPanelHtml(lesson,prefix){
  if(!lesson.listening)return '';
  return '<section class="jp-panel jp-listening" id="'+prefix+'listening" aria-label="Listen before reading">'+
    '<h3>Listen first · सुनेर काम पत्ता लगाऊ</h3><p lang="ja" class="jp-listening-prompt">'+jpFuriganaHtml(lesson.listening.prompt,lesson)+'</p>'+
    '<p>पहिले यो प्रश्न पढ। Script बन्द राखेर एकपटक सुन, उत्तर टिप, अनि फेरि सुन। त्यसपछि मात्र तलको transcript र उत्तर खोल।</p>'+
    '<div class="jp-actions"><button type="button" class="btn" data-jp-listen="1">▶ Play · 1×</button><button type="button" class="btn secondary" data-jp-listen="0.8">▶ Slow · 0.8×</button><button type="button" class="btn secondary" data-jp-stop="1">■ Stop</button><button type="button" class="btn secondary" data-jp-jump="'+prefix+'reading">Transcript ↓</button></div>'+
    '<p id="jpListeningStatus" class="jp-muted" role="status" aria-live="polite">Ready when you are. Nothing plays automatically.</p>'+
    '<p class="jp-muted">Uses an installed local Japanese device voice. 1× is the voice’s default speed, not a human JLPT recording. Without a local voice, use the transcript as reading practice; no online voice is substituted.</p></section>';
}
/* JAPANESE LISTENING HELPERS END */
`;
const replace=(old,next)=>{assert(html.includes(old),'Missing anchor '+old.slice(0,100));html=html.replace(old,next);};
replace('function jpRenderLesson(id){',helpers+'function jpRenderLesson(id){');
replace('function switchView(name){','function switchView(name){\n  if(name!=="japanese")jpStopSpeech();');
replace('function renderJapanese(){','function renderJapanese(){\n  jpStopSpeech();');
replace("    '<div class=\"jp-panel\"><h3>Understand it</h3><p>' + jpFuriganaHtml(lesson.explain,lesson)","    jpListeningPanelHtml(lesson,studyPrefix) + '<div class=\"jp-panel\"><h3>Understand it</h3><p>' + jpFuriganaHtml(lesson.explain,lesson)");
const navStart='      (lesson.teRules ? [["Words","vocab"]';
replace(navStart,'      (lesson.listening ? [["Listen","listening"],["Words","vocab"],["Kanji","kanji"],["Grammar","uses"],["Transcript","reading"],["Practice","practice"],["Quiz","quiz"],["Summary","summary"]] : lesson.teRules ? [["Words","vocab"]');
replace("'<div class=\"jp-panel\"' + (studyPrefix ? ' id=\"' + studyPrefix + 'reading\"' : '') + '><h3>Read first, then reveal meaning</h3>' +", "'<div class=\"jp-panel\"' + (studyPrefix ? ' id=\"' + studyPrefix + 'reading\"' : '') + '><h3>' + (lesson.listening ? 'Transcript · open after listening' : 'Read first, then reveal meaning') + '</h3>' +\n    (lesson.listening ? '<details class=\"jp-listening-transcript\"><summary>Reveal Japanese transcript</summary>' : '') +");
replace("escapeHtml(lesson.readingHelp) + '</p></details>';","escapeHtml(lesson.readingHelp) + '</p></details>' + (lesson.listening ? '</details>' : '');");
replace("html += '<h4>Reading questions · पहिले आफैँ उत्तर देऊ</h4>';","html += '<h4>' + (lesson.listening ? 'Listening checks · पहिले सुनेर उत्तर देऊ' : 'Reading questions · पहिले आफैँ उत्तर देऊ') + '</h4>';");
replace("'> I read this before opening the meaning</label></div>' +","'> ' + (lesson.listening ? 'I checked my answer against the transcript (use notes to record listening or reading practice)' : 'I read this before opening the meaning') + '</label></div>' +");
const start=html.indexOf('      }else if(el.dataset.jpSound){'),end=html.indexOf('      }else return;',start);assert(start>=0&&end>start);
html=html.slice(0,start)+`      }else if(el.dataset.jpSound || el.dataset.jpListen){
        const lesson=JP_LESSONS.find(function(l){return l.id===jpPage.lesson;});
        jpSpeakReading(lesson,el.dataset.jpListen==='0.8' ? .8 : (el.dataset.jpListen ? 1 : .82));
        return;
      }else if(el.dataset.jpStop){
        jpStopSpeech();return;
`+html.slice(end);
const css=`\n/* JAPANESE LISTENING STYLE START */
.jp-listening{border-color:var(--accent);}
.jp-listening .jp-listening-prompt{font-size:18px;line-height:1.8;font-weight:600;}
.jp-listening-transcript{margin:10px 0;}
.jp-listening-transcript>summary{padding:10px 0;cursor:pointer;}
.jp-listening [role="status"]{min-height:1.65em;}
@media(max-width:600px){#view-japanese .jp-listening .jp-actions>.btn{flex:1 1 130px;min-height:44px;}.jp-listening .jp-listening-prompt{font-size:17px;}}
/* JAPANESE LISTENING STYLE END */\n`;
replace('</style>',css+'</style>');
for(const m of html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)){if(/type=["']application\/json["']/.test(m[1]))JSON.parse(m[2]);else if(!/\bsrc=/.test(m[1]))new Function(m[2]);}
fs.writeFileSync(file+'.tmp',html,'utf8');for(let n=0;;n++){try{fs.renameSync(file+'.tmp',file);break;}catch(e){if(n>=12)throw e;Atomics.wait(new Int32Array(new SharedArrayBuffer(4)),0,0,200);}}
console.log('Listening UI installed; shared speech helper, opt-in panel/transcript and no learner-data changes.');
