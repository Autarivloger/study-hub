// Reproduce the offline assets from the supplied PDF and pinned npm packages.
const fs=require('fs'),path=require('path'),crypto=require('crypto'),assert=require('assert/strict');
const [source,modules]=process.argv.slice(2);assert(source&&modules,'Usage: node scripts/build-gita-assets.cjs <PDF> <build node_modules>');
const base=path.resolve(modules),pdf=path.join(base,'pdfjs-dist'),esbuild=require(path.join(base,'esbuild'));
assert.equal(require(path.join(pdf,'package.json')).version,'6.4.299');
const dir='vendor/pdfjs-6.4.299';fs.mkdirSync(dir,{recursive:true});
for(const [input,name] of [['pdf.mjs','pdf.js'],['pdf.worker.mjs','pdf.worker.js']]){
 esbuild.buildSync({entryPoints:[path.join(pdf,'build',input)],outfile:path.join(dir,name),bundle:false,format:'iife',globalName:name==='pdf.js'?'StudyHubPdf':'pdfjsWorker',minify:true,target:'es2022',legalComments:'eof'});
}
fs.copyFileSync(path.join(pdf,'LICENSE'),path.join(dir,'LICENSE'));
const bytes=fs.readFileSync(source),sha=crypto.createHash('sha256').update(bytes).digest('hex');
fs.mkdirSync('books',{recursive:true});
fs.writeFileSync('books/gita-pdf-v1.js','// The supplied original PDF, unchanged; base64 permits offline file:// loading.\nwindow.STUDY_HUB_GITA_BASE64='+JSON.stringify(bytes.toString('base64'))+';\n');
console.log(JSON.stringify({bytes:bytes.length,sha256:sha,pdfjs:'6.4.299'}));
