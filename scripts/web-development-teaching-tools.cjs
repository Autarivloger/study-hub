// Authoring helpers only. The website continues to use its existing renderers.
const h=v=>({t:'h',v}),p=v=>({t:'p',v}),key=v=>({t:'key',v}),tip=v=>({t:'tip',v}),warn=v=>({t:'warn',v});
const term=(v,note)=>({t:'new',v,note});
const code=(v,lang='text')=>({t:'code',v,lang});
const out=v=>({t:'out',v});
const mistake=(wrong,right,why,lang='html')=>({t:'mis',wrong,right,why,lang});
const exercise=(q,input,a,why,lang='text')=>({t:'try',q,code:input,a,why,lang});
const page=(title,body,language='en')=>`<!doctype html>
<html lang="${language}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${title}</title>
  </head>
  <body>
${body}
  </body>
</html>`;
function lesson(week,day,d){
 const sections=d.parts.flatMap((part,i)=>[h('Part '+(i+1)+' · '+part[0]),...part[1]]);
 sections.push(h(day===7?'Retrieval and repair workshop':'Practice · Try before revealing'),...d.practice.map(args=>exercise(...args)));
 sections.push(h('Mini challenge · '+d.challenge[0]),p(d.challenge[1]),{t:'sol',code:d.challenge[2],why:d.challenge[3],lang:d.challenge[4]||'text',...(d.challenge[5]?{out:d.challenge[5]}:{})});
 sections.push(h('Ready to continue?'),p(d.ready));
 return{id:'webdev:'+week+'.'+day,title:d.title,objective:d.objective,sections,quiz:d.quiz.map(([q,answer,a,b,why],i)=>{
  const options=[answer,a,b],n=i%3;return{q,options:options.slice(n).concat(options.slice(0,n)),correct:(3-n)%3,why};
 }),reflection:d.reflection};
}
module.exports={h,p,key,tip,warn,term,code,out,mistake,exercise,page,lesson};
