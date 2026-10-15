'use strict';
// Values from schema/server are rendered as text, never executable HTML.
const operations=document.querySelector('#operations'),status=document.querySelector('#status'),bearer=document.querySelector('#bearer'),authState=document.querySelector('#authState');
function auth(){authState.textContent=bearer.value?'Token loaded for this tab.':'No token loaded.';}
bearer.addEventListener('input',auth);
document.querySelector('#forget').addEventListener('click',()=>{bearer.value='';auth();});
function element(tag,text,parent){const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(parent)parent.append(node);return node;}
function field(parent,label,type,value){const id='field-'+crypto.randomUUID(),caption=element('label',label,parent);caption.htmlFor=id;const input=element(type==='json'?'textarea':'input',undefined,parent);input.id=id;if(type!=='json')input.type=type;input.value=value;input.autocomplete='off';return input;}
async function start(){
 const response=await fetch('/openapi.json');if(!response.ok)throw Error('Schema could not be loaded');const schema=await response.json();let count=0;
 for(const [route,methods] of Object.entries(schema.paths))for(const [method,operation] of Object.entries(methods)){
  if(!['get','post','put','patch','delete'].includes(method))continue;count++;
  const card=element('details',undefined,operations);card.dataset.operation=method+' '+route;
  const summary=element('summary',undefined,card);element('span',method.toUpperCase(),summary);summary.append(document.createTextNode(route));
  element('p',operation.summary||'Try this operation',card);
  const parameters=[];
  for(const parameter of operation.parameters||[]){parameters.push([parameter,field(card,parameter.in+' · '+parameter.name,parameter.schema.type==='integer'?'number':'text',String(parameter.schema.default??(parameter.in==='path'?1:'')))]);}
  let json,username,password;
  if(operation.requestBody){
   if(operation.requestBody.content['application/x-www-form-urlencoded']){username=field(card,'Fictional username','text','asha');password=field(card,'Fictional practice password','password','');}
   else{let example=route==='/v1/users'?{username:'asha',password:'fictional-learning-passphrase'}:method==='patch'?{completed:true}:{title:'My API lesson',body:'Explain the request and response.',completed:false};json=field(card,'JSON request body','json',JSON.stringify(example,null,2));}
  }
  const run=element('button','Send request',card);run.type='button';const output=element('pre','Response will appear here.',card);output.setAttribute('aria-live','polite');
  run.addEventListener('click',async()=>{
   run.disabled=true;
   try{
    let target=route;const query=new URLSearchParams();
    for(const [parameter,input] of parameters){if(parameter.in==='path')target=target.replace('{'+parameter.name+'}',encodeURIComponent(input.value));else if(input.value!=='')query.set(parameter.name,input.value);}
    const headers={};if(bearer.value)headers.Authorization='Bearer '+bearer.value.trim();let body;
    if(json){body=JSON.stringify(JSON.parse(json.value));headers['Content-Type']='application/json';}
    if(username){body=new URLSearchParams({username:username.value,password:password.value});headers['Content-Type']='application/x-www-form-urlencoded';}
    const result=await fetch(target+(query.size?'?'+query:''),{method:method.toUpperCase(),headers,body});
    const text=await result.text();let value=text?JSON.parse(text):null;
    if(value&&value.access_token){bearer.value=value.access_token;value.access_token='[kept in this tab only]';auth();}
    if(password)password.value='';
    if(route==='/v1/users'&&json){try{const v=JSON.parse(json.value);v.password='';json.value=JSON.stringify(v,null,2);}catch{}}
    if(route==='/v1/logout'&&result.ok){bearer.value='';auth();}
    output.textContent=result.status+' '+result.statusText+'\n'+(value===null?'(no response body)':JSON.stringify(value,null,2));
   }catch(error){output.textContent='Request failed: '+error.message;}finally{run.disabled=false;}
  });
 }
 status.textContent=count+' operations loaded from local /openapi.json. No internet required.';
}
start().catch(error=>{status.textContent=error.message;});
