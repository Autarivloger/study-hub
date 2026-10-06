// Run with STUDY_HUB_MYPY_PYTHON pointing to an environment containing mypy.
const fs=require('fs'),os=require('os'),path=require('path'),cp=require('child_process'),assert=require('assert/strict');
const python=process.env.STUDY_HUB_MYPY_PYTHON;
if(!python)throw Error('Set STUDY_HUB_MYPY_PYTHON to a Python interpreter with mypy installed');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'studyhub-week21-types-'));
try{
 const html=fs.readFileSync('study-hub.html','utf8'),a=html.indexOf('const DAY_TEACH = ')+18,b=html.indexOf('\n};\n\nconst REST_DAY',a),days=Function('return ('+html.slice(a,b+2)+')')();
 const receipt=days['21.1'].parts[0].sections.find(s=>s.t==='sol'&&s.code).code;
 fs.writeFileSync(path.join(dir,'typed_receipt.py'),receipt,'utf8');
 fs.copyFileSync('docs/python-week21-inventory.py',path.join(dir,'inventory.py'));
 const run=cp.spawnSync(python,['-m','mypy','--strict','--cache-dir',path.join(dir,'cache'),'typed_receipt.py','inventory.py'],{cwd:dir,encoding:'utf8',timeout:60000});
 assert.equal(run.status,0,run.stdout+'\n'+run.stderr);
 fs.writeFileSync(path.join(dir,'bad_call.py'),receipt+'\nprint(total(["wrong"], 20))\n','utf8');
 const bad=cp.spawnSync(python,['-m','mypy','--strict','--cache-dir',path.join(dir,'cache'),'bad_call.py'],{cwd:dir,encoding:'utf8',timeout:60000});
 assert.notEqual(bad.status,0);assert.match(bad.stdout,/incompatible type|list-item/);
 console.log('PASS: five-function receipt and Inventory pass mypy --strict; deliberate wrong input is detected');
}finally{fs.rmSync(dir,{recursive:true,force:true});}
