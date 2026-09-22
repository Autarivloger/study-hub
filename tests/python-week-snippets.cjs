const fs = require('fs');
const os = require('os');
const path = require('path');
const {spawnSync} = require('child_process');

const week = Number(process.argv[2]);
if (!Number.isInteger(week)) throw new Error('Usage: node tests/python-week-snippets.cjs WEEK');

const html = fs.readFileSync(path.join(__dirname, '..', 'study-hub.html'), 'utf8');
const start = html.indexOf('const DAY_TEACH = {');
const end = html.indexOf('\n};\n\nconst REST_DAY', start);
if (start < 0 || end < 0) throw new Error('DAY_TEACH block not found');
const body = html.slice(start + 'const DAY_TEACH = '.length, end + 2);
const days = new Function('return (' + body + ')')();

const bundled = 'C:\\Users\\vlogerautari\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe';
const python = process.env.STUDY_HUB_PYTHON || (fs.existsSync(bundled) ? bundled : 'python');
const cases = [];

for (let day = 0; day < 6; day++) {
  const lesson = days[week + '.' + day];
  if (!lesson) throw new Error(`Missing Week ${week} Day ${day + 1}`);
  const sections = lesson.parts.flatMap(p => p.sections || []);
  for (let i = 0; i < sections.length; i++) {
    const s = sections[i];
    if (s.t === 'sol' && s.code && Object.hasOwn(s, 'out')) cases.push({day, code:s.code, out:s.out});
    if (s.t === 'code' && s.v && sections[i+1] && sections[i+1].t === 'out') cases.push({day, code:s.v, out:sections[i+1].v});
  }
}

let passed = 0;
for (const c of cases) {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), `study-hub-w${week}-`));
  const file = path.join(dir, 'snippet.py');
  fs.writeFileSync(file, c.code, 'utf8');
  const run = spawnSync(python, [file], {cwd:dir, encoding:'utf8'});
  fs.rmSync(dir, {recursive:true, force:true});
  if (run.status !== 0) throw new Error(`Week ${week} Day ${c.day+1} failed:\n${run.stderr}\n${c.code}`);
  const actual = run.stdout.replace(/\r\n/g, '\n').trimEnd();
  const expected = c.out.replace(/\r\n/g, '\n').trimEnd();
  if (actual !== expected) throw new Error(`Week ${week} Day ${c.day+1} output mismatch\nEXPECTED:\n${expected}\nACTUAL:\n${actual}\nCODE:\n${c.code}`);
  passed++;
}

console.log(`PASS: Week ${week}, 6 days, ${passed} executable examples matched`);
