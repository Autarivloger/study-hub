/* Original Week43 frontend. Credentials live in this closure, never web storage. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const state = {token:"", user:"", editing:null, deleting:null, busy:false, notes:[], total:0, offset:0, limit:5, query:"", completed:"", readVersion:0};
  const el = (tag, text, cls) => {const node=document.createElement(tag);if(text!==undefined)node.textContent=text;if(cls)node.className=cls;return node;};
  function message(text,error=false){$("message").textContent=text;$("message").dataset.error=String(error);}
  function controls(){
    for(const id of ["authFields","editorFields","filterFields"])$(id).disabled=state.busy;
    document.querySelectorAll("#notes button,#logout,#newNote,#retry").forEach(b=>b.disabled=state.busy);
    $("previous").disabled=state.busy||state.offset===0;
    $("next").disabled=state.busy||state.offset+state.limit>=state.total;
  }
  function resetEditor(){state.editing=null;$("noteForm").reset();$("editorTitle").textContent="A new thought";$("saveNote").textContent="Save note";}
  function forget(){
    state.token="";state.user="";state.notes=[];state.total=0;state.offset=0;state.query="";state.completed="";state.deleting=null;state.readVersion++;
    $("auth").hidden=false;$("workspace").hidden=true;$("notes").replaceChildren();$("password").value="";$("searchForm").reset();resetEditor();
    if($("deleteDialog").open)$("deleteDialog").close();
  }
  async function api(path,{method="GET",body,form=false,authenticated=true}={}){
    const usedToken=state.token,headers={};if(authenticated&&usedToken)headers.Authorization="Bearer "+usedToken;
    if(body!==undefined)headers["Content-Type"]=form?"application/x-www-form-urlencoded":"application/json";
    let response;
    try{response=await fetch(path,{method,headers,body:body===undefined?undefined:form?new URLSearchParams(body):JSON.stringify(body),signal:AbortSignal.timeout(8000),cache:"no-store"});}
    catch{throw Error("Connection failed or timed out. Check the server and retry. Your editor has been kept.");}
    if(!response.ok){
      if(response.status===401&&authenticated){if(usedToken===state.token)forget();throw Error("Your session ended. Sign in again; saved notes remain in the database.");}
      const messages={401:"Username or password was not accepted.",404:"That note is no longer available. Refresh your list.",409:"That username is unavailable. Choose another.",422:"Check the field lengths and values. Nothing invalid was saved.",429:"Too many requests. Wait before trying again."};
      throw Error(messages[response.status]||"The server could not finish that request. Please retry.");
    }
    return response.status===204?null:response.json();
  }
  async function mutation(work){if(state.busy)return;state.busy=true;controls();try{await work();}catch(e){message(e.message,true);}finally{state.busy=false;controls();}}
  function render(){
    const list=$("notes");list.replaceChildren();
    if(!state.notes.length){const empty=el("div",undefined,"empty");empty.append(el("strong",state.query||state.completed!==""?"No matching notes":"A little space to begin"),el("span","Write a thought in the editor or adjust your search."));list.append(empty);}
    for(const note of state.notes){
      const card=el("article",undefined,"note"+(note.completed?" done":""));card.dataset.noteId=String(note.id);
      const meta=el("div",undefined,"note-meta");meta.append(el("span",note.completed?"COMPLETED":"TO REVISIT","badge"),el("span","NOTE "+note.id));
      const buttons=el("div",undefined,"button-row");
      for(const [action,label] of [["edit","Edit & tags"],["toggle",note.completed?"Revisit":"Mark complete"],["delete","Delete"]]){
        const button=el("button",label,action==="delete"?"danger":undefined);button.type="button";button.dataset.action=action;
        button.setAttribute("aria-label",label+": "+note.title);button.onclick=()=>act(action,note);buttons.append(button);
      }
      card.append(meta,el("h3",note.title),el("p",note.body),buttons);list.append(card);
    }
    $("resultCount").textContent=state.total+" matching "+(state.total===1?"note":"notes");
    $("pageLabel").textContent=state.total?"Page "+(Math.floor(state.offset/state.limit)+1)+" of "+Math.ceil(state.total/state.limit):"No pages";
    controls();
  }
  async function load(){
    const ticket=++state.readVersion,token=state.token;
    const params=new URLSearchParams({q:state.query,limit:state.limit,offset:state.offset});if(state.completed!=="")params.set("completed",state.completed);
    $("notes").setAttribute("aria-busy","true");
    try{
      const page=await api("/v1/notes?"+params);if(ticket!==state.readVersion||token!==state.token)return;
      const last=Math.max(0,Math.floor((page.total-1)/state.limit)*state.limit);
      if(state.offset>last){state.offset=last;return await load();}
      state.total=page.total;state.notes=page.items;render();
    }finally{if(ticket===state.readVersion)$("notes").setAttribute("aria-busy","false");}
  }
  async function act(action,note){
    if(state.busy)return;
    if(action==="delete"){state.deleting=note.id;$("deleteName").textContent=note.title;$("deleteDialog").showModal();$("cancelDelete").focus();return;}
    await mutation(async()=>{
      if(action==="toggle"){await api("/v1/notes/"+note.id,{method:"PATCH",body:{completed:!note.completed}});await load();message("Completion updated.");return;}
      const tags=await api("/v1/notes/"+note.id+"/tags");
      state.editing=note.id;$("noteTitle").value=note.title;$("noteBody").value=note.body;$("noteComplete").checked=note.completed;
      for(const option of $("noteTags").options)option.selected=tags.includes(option.value);
      $("editorTitle").textContent="Edit your thought";$("saveNote").textContent="Save changes";message("Editing note "+note.id+". Changes stay in the editor until saved.");
    });
    if(action==="edit"&&state.editing===note.id)$("noteTitle").focus();
  }
  async function authenticate(register=false){
    if(!$("authForm").reportValidity())return;
    await mutation(async()=>{
      const username=$("username").value.trim(),password=$("password").value;
      if(register){await api("/v1/users",{method:"POST",body:{username,password},authenticated:false});message("Account created. Signing in…");}
      const result=await api("/v1/token",{method:"POST",body:{username,password},form:true,authenticated:false});
      state.token=result.access_token;$("password").value="";
      const user=await api("/v1/me");state.user=user.username;$("greeting").textContent="WELCOME, "+user.username;
      $("auth").hidden=true;$("workspace").hidden=false;state.offset=0;await load();message("Your workspace is ready. Notes save to the server; this tab holds the login.");
    });
  }
  $("authForm").onsubmit=e=>{e.preventDefault();authenticate();};$("register").onclick=()=>authenticate(true);
  $("noteForm").onsubmit=e=>{
    e.preventDefault();if(!$("noteForm").reportValidity())return;
    mutation(async()=>{
      const title=$("noteTitle").value.trim(),body=$("noteBody").value.trim();if(!title||!body)throw Error("Write a title and a thought; spaces alone are not enough.");
      const payload={title,body,completed:$("noteComplete").checked};
      const note=await api(state.editing?"/v1/notes/"+state.editing:"/v1/notes",{method:state.editing?"PATCH":"POST",body:payload});
      state.editing=note.id;$("editorTitle").textContent="Edit your saved thought";$("saveNote").textContent="Retry save";
      try{await api("/v1/notes/"+note.id+"/tags",{method:"PUT",body:{names:[...$("noteTags").selectedOptions].map(o=>o.value)}});}
      catch(error){await load().catch(()=>{});throw Error("The note was saved, but tags were not confirmed. Retry updates this note. "+error.message);}
      resetEditor();await load();message("Note and tags saved.");
    });
  };
  $("newNote").onclick=$("cancelEdit").onclick=()=>{if(!state.busy){resetEditor();$("noteTitle").focus();}};
  $("searchForm").onsubmit=e=>{e.preventDefault();if(state.busy)return;state.query=$("query").value;state.completed=$("completion").value;state.offset=0;load().then(()=>message("Search updated.")).catch(e=>message(e.message,true));};
  $("retry").onclick=()=>load().then(()=>message("List refreshed.")).catch(e=>message(e.message,true));
  for(const [id,direction] of [["previous",-1],["next",1]])$(id).onclick=()=>{if(state.busy)return;state.offset+=direction*state.limit;load().catch(e=>message(e.message,true));};
  $("logout").onclick=()=>mutation(async()=>{let warning="";try{await api("/v1/logout",{method:"POST"});}catch(e){warning=e.message;}finally{forget();}message(warning?"Signed out of this tab. Server revocation was not confirmed; the token may remain valid until expiry.":"Signed out. Your saved notes remain in the database.",Boolean(warning));});
  $("cancelDelete").onclick=()=>$("deleteDialog").close();
  $("confirmDelete").onclick=()=>{const id=state.deleting;if(id===null)return;$("deleteDialog").close();mutation(async()=>{await api("/v1/notes/"+id,{method:"DELETE"});if(state.editing===id)resetEditor();state.deleting=null;await load();message("Note deleted.");$("newNote").focus();});};
  $("theme").onclick=()=>{const dark=document.documentElement.dataset.theme?document.documentElement.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;document.documentElement.dataset.theme=dark?"light":"dark";};
  controls();
})();
