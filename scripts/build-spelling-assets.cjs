// Rebuild from the official typo-js1.4.0 tarball after verifying its registry SHA512.
const fs=require('fs'),path=require('path'),crypto=require('crypto');
const root=path.resolve('tmp/pdfs/spelling-package'),pkg=path.join(root,'package'),out='vendor/spelling';
const integrity='QP5VvwpQKk+xcKCbZmkHHtmdPt53ICuV/A4a1PXJOKeu6HdtBMgweScy7Gw1gxcHv6e2lFTUIM17PUxP7/GABg==';
if(crypto.createHash('sha512').update(fs.readFileSync(path.join(root,'typo-js-1.4.0.tgz'))).digest('base64')!==integrity)throw Error('Package integrity mismatch');
fs.mkdirSync(out,{recursive:true});
const engine=fs.readFileSync(path.join(pkg,'typo.js'),'utf8'),aff=fs.readFileSync(path.join(pkg,'dictionaries/en_US/en_US.aff'),'utf8'),dic=fs.readFileSync(path.join(pkg,'dictionaries/en_US/en_US.dic'),'utf8');
const source=engine+'\n'+fs.readFileSync('scripts/spelling-worker.js','utf8')+'\nstartStudyHubSpelling('+JSON.stringify(aff)+','+JSON.stringify(dic)+');\n';
fs.writeFileSync(out+'/english-v1.js','/* Study Hub offline English spelling. Typo.js1.4.0 BSD-3-Clause; SCOWL en_US2020.12.07. See adjacent notices. */\nwindow.STUDY_HUB_SPELLING_SOURCE='+JSON.stringify(source)+';\n');
fs.copyFileSync(path.join(root,'LICENSE.txt'),out+'/TYPO-LICENSE.txt');
fs.copyFileSync(path.join(pkg,'dictionaries/en_US/README.md'),out+'/DICTIONARY-NOTICES.txt');
fs.writeFileSync(out+'/README.md','# Offline English spelling\n\nGenerated with scripts/build-spelling-assets.cjs from the official npm typo-js1.4.0 package. Registry SHA512: '+integrity+'\n\nEngine: https://github.com/cfinke/Typo.js (BSD-3-Clause). The package includes SCOWL en_US2020.12.07; its complete notices are retained in DICTIONARY-NOTICES.txt. English suggestions run in a local Blob worker. No writing is sent to a service and no automatic replacements are performed. The bundled asset works with file:// and the existing hosted offline cache.\n');
console.log('Built offline English asset:',fs.statSync(out+'/english-v1.js').size,'bytes');
