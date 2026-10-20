// Runs inside a local worker. Receives a single word, never the full note.
function startStudyHubSpelling(aff,dic){
  const dictionary=new Typo('en_US',aff,dic),cache=new Map(),alphabet='abcdefghijklmnopqrstuvwxyz';
  const wordList=Array.from(dictionary.dictionaryTable.keys()).filter(w=>/^[a-z]{3,26}$/.test(w)&&!dictionary.hasFlag(w,'NOSUGGEST'));
  function suggestions(raw){
    const word=raw.toLowerCase(),found=new Set();
    function add(candidate){if(candidate!==word&&!found.has(candidate)&&dictionary.check(candidate)&&!dictionary.hasFlag(candidate,'NOSUGGEST'))found.add(candidate);}
    // Common single-letter mistakes first; avoids expensive edit-two expansion while typing.
    for(let i=0;i<word.length-1;i++)add(word.slice(0,i)+word[i+1]+word[i]+word.slice(i+2));
    for(let i=0;i<word.length;i++)add(word.slice(0,i)+word[i]+word.slice(i));
    for(let i=0;i<word.length;i++)add(word.slice(0,i)+word.slice(i+1));
    for(let i=0;i<=word.length;i++)for(const c of alphabet)add(word.slice(0,i)+c+word.slice(i));
    for(let i=0;i<word.length;i++)for(const c of alphabet)add(word.slice(0,i)+c+word.slice(i+1));
    if(!found.size){
      // A bounded dictionary scan handles two errors without generating millions of candidates.
      for(const candidate of wordList){if(Math.abs(candidate.length-word.length)>2)continue;let previous=Array.from({length:candidate.length+1},(_,i)=>i),before=null;
        for(let i=1;i<=word.length;i++){const row=[i];for(let j=1;j<=candidate.length;j++){row[j]=Math.min(row[j-1]+1,previous[j]+1,previous[j-1]+(word[i-1]===candidate[j-1]?0:1));if(before&&i>1&&j>1&&word[i-1]===candidate[j-2]&&word[i-2]===candidate[j-1])row[j]=Math.min(row[j],before[j-2]+1);}before=previous;previous=row;}
        if(previous[candidate.length]<=2)found.add(candidate);if(found.size>=5)break;
      }
    }
    return Array.from(found).slice(0,5).map(w=>raw===raw.toUpperCase()?w.toUpperCase():/^[A-Z]/.test(raw)?w[0].toUpperCase()+w.slice(1):w);
  }
  self.onmessage=event=>{
    const {id,word}=event.data||{};
    if(typeof word!=='string'||word.length>30||!/^[A-Za-z]+(?:['’][A-Za-z]+)*$/.test(word))return;
    try{
      let result=cache.get(word);
      if(!result){const normalized=word.replace(/’/g,"'");const correct=dictionary.check(normalized);result={correct,suggestions:correct?[]:suggestions(normalized)};if(cache.size>=300)cache.delete(cache.keys().next().value);cache.set(word,result);}
      self.postMessage({id,word,...result});
    }catch(error){self.postMessage({id,word,correct:false,suggestions:[],failed:true});}
  };
  self.postMessage({ready:true,words:Array.from(dictionary.dictionaryTable.keys())});
}
