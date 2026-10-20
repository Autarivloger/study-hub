# Study Hub

An offline-first Python learning platform. One self-contained HTML file holding a
12-month, 364-lesson Python curriculum, plus a Japanese learning section, typing,
notes, a daily journal, flashcards with spaced repetition, quizzes, a Pomodoro
timer, and a Life Lessons journal.

No build step. No dependencies. No server required.

## Workspace design

The offline interface uses a calm green palette, grouped navigation, a clear
resume/progress dashboard, readable lesson typography and matching light/dark
themes. Search and the theme switch stay in the header. The **three-dot Workspace
tools** menu contains sync, export/import, device transfer and diagnostics.
All styling and icons are embedded in the HTML; no fonts or UI libraries are
downloaded. Editable presentation sources live in `scripts/premium-theme.css`
and `scripts/premium-shell.js`. Curriculum and learner storage are unchanged.

The bottom sidebar arrow switches between labelled navigation and a narrow icon
rail. Icons keep accessible names and hover titles; the arrow remains available
while the navigation list scrolls. The preference is stored locally under
`studyHubSidebarCompact`, separately from learner data. Python's opening dashboard
and shared page spacing are compact, while lesson/code text keeps its existing
size. Presentation sources are `scripts/compact-workspace.css` and
`scripts/compact-workspace.js`, embedded for offline use.

The refined theme adds softly shaded cards, a glass desktop header, coordinated
study tools and clearer visual hierarchy. All styles remain embedded for offline
use, with no font download or decorative JavaScript. Reading widths, text selection,
touch targets, Furigana navigation clearance, reduced motion and High Contrast
keyboard outlines are covered by the design checks.

The Japanese area has a dedicated study dashboard, a grouped monthly path,
compact day cards and consistent lesson/vocabulary/quiz sizing. Its presentation
source is `scripts/japanese-theme.css`, embedded in the HTML for offline use.
The daily random review stays immediately available; Continue, Meaning Folder,
Hard words and all 36 weeks remain accessible. The Japanese theme is scoped to
that view and preserves the curriculum, existing progress keys and storage logic.

Meaning Folder opens one list at a time; Back returns to its folders. Opposite,
near-synonym and uploaded-word meanings start visible and can be hidden by
clicking the word. Opposite/synonym lists have Add pair and pencil Edit controls.
Personal entries and overrides live in the additive `japanese.meaningPairs` map;
the original 100/30 pairs remain unchanged. Per-pair timestamps merge edits across
the existing backup/sync system. Search, CSV downloads and future flashcard
additions use the edited list; previously studied cards retain their own history.

## Web Development — three-year beginner roadmap

Open **Learn → Web Development → Year → Week → Day**. The 156-week path contains
1,092 day plans with five study days, a project day and a review/catch-up day each
week. Every week has a specific readiness check; repeat a week when needed.

Year 1 begins with files, folders and a first HTML page, then develops semantic
HTML, CSS, JavaScript, accessibility, testing and an independent browser app.
Year 2 introduces TypeScript/React after JavaScript, then a Python bridge,
Django, SQL, APIs, deployment and a full-stack capstone. Year 3 develops deeper
architecture, multilingual/accessibility work, measured performance, offline
data/sync, operations, specialisation and a major product/portfolio project.

This is an original **roadmap only**, with topics, project goals and readiness
criteria. Full teaching lessons have not been added yet. References use official
MDN, web.dev, W3C, TypeScript, React, Django/DRF and PostgreSQL documentation.
The plan works offline; external references require internet. No new learner
storage keys or completion data are created by reading the roadmap.

Authoring sources are `scripts/web-development-plan.txt` and
`scripts/web-development-path.json`; the generated roadmap and view are embedded
in the HTML. `scripts/roadmap-years.js` reuses the existing Cybersecurity year/week
component, preserving its markup, navigation and lessons.

## Exercise log

Open **To-Do → Exercise → Add exercise** to save your own exercise names and
usual units/sets. Use **Log activity** or an exercise's **Log** button to record
the date, amount per set, unit, sets and optional notes. Units include reps,
seconds, minutes, rounds and total sets. Multiple activities can be recorded on
the same day. Pencil menus edit or remove records; removed records can be restored.
Monthly history follows the chosen date. Renaming/removing an exercise preserves
the names and amounts already recorded in history.

The additive `exerciseTracker` store participates in existing backup/import and
Gist sync. Per-record timestamps merge changes; deletion records prevent stale
backups from resurrecting removed entries. Habits and Tasks keep their own stores.
The entire feature is embedded in the HTML and works offline.

## Cybersecurity — foundations to defensive Python

Open **Cybersecurity → Week 9** for seven complete English lessons: a scoped
local lab, JSON validation, event deduplication, UTC/unknown timestamps,
traceable findings, byte integrity and a full weekly review. It includes 21
executed Python examples/solutions, 14 practices/challenges and 52 explained
self-checks. [The standard-library lab](docs/cybersecurity-week9/README.md) reuses
the exact fictional Week 7 records, keeps originals unchanged and makes no
network/account requests. Read lessons offline; run Python in the supplied local
folder. Existing day notes use the same storage keys and backup/import paths.

The complete **three-year roadmap covers Weeks 1–156**, with seven day plans per
week (1,092 study/project/review days). Open **Cybersecurity → Year 1 / Year 2 /
Year 3 → Week → Day**. Four-week topic groups keep the list manageable. Year 1
builds systems, network, identity and secure-development foundations; Year 2
covers operations, application/cloud security and investigations; Year 3 adds
engineering, specialisation and integrated capstones. The sequence is an original
study plan informed by NIST CSF/NICE, OWASP, MITRE ATT&CK and incident-response
guidance, with reference links inside the app. It is not an official certification
syllabus or a guarantee of professional proficiency.

**Weeks 1–9 retain their complete teaching; Weeks 10–156 are roadmaps only.**
The original first 16 week plans, all existing lessons/notes/progress and Online
Safety remain. New plans list topics and project/review goals, with Python as a
supporting tool for evidence, testing and reporting. No new teaching explanations
or executable labs were added. The complete path works offline; external
references need internet. The schedule can be repeated or paced flexibly.

## Python Week 52 — Capstone & what comes next

Open **Course → Week 52** for six days with 36 teaching parts, 72 exercises,
72 explained quiz questions, 108 executed examples/solutions and six embedded
visuals. Work from specification and scope through architecture, core behavior,
error cases, measured queries, deployment evidence and a final retrospective.
The [original StudyLog capstone](docs/python-week52/README.md) includes SQLite,
a validated FastAPI service, a responsive offline-assets interface, revision-aware
edits/deletes, summaries, tests and verified snapshots. Actual localhost HTTP,
process restart, restored service, browser workflows and a fresh installed wheel
are checked separately. Docker and remote/second-device instructions are manual
exercises and are not represented as executed public deployment. Day labels are
milestones: use additional sessions for independent reconstruction and practice.

## Python Week 51 — Performance, packaging & professional practice

Open **Course → Week 51** for six days with 36 teaching parts, 72 exercises,
72 explained quiz questions, 108 executed Python examples/solutions and six
embedded visuals. Study call/line profiling, fair timing and allocation measures,
three algorithm rewrites, package metadata, wheels, documentation, code review
and focused contribution habits. Take additional sessions whenever needed.
The [original records library](docs/python-week51/README.md) includes behavior
tests, a measured benchmark, executable docstrings, a real MkDocs build and a
release verifier that builds a wheel from its source archive, installs it into
a fresh environment and runs the installed API and CLI outside the checkout.
TestPyPI publication and an actual upstream submission are separate manual online
exercises; local builds never upload packages or handle learner credentials.

## Python Week 50 — Concurrency & parallelism

Open **Course → Week 50** for six days, 36 parts, 72 exercises, 72 explained
quiz questions and 108 executed examples/solutions. Learn threads, locks, queues,
spawn processes, futures, asyncio, bounded HTTP collection and cancellation.
Five original diagrams and a measured collector timing chart are embedded offline.
The [local concurrency lab](docs/python-week50/README.md) combines actual loopback
HTTP requests with CPU workers, explicit errors, progress and bounded queues.
Its measurements require equal complete results and retain startup/cleanup costs;
observed speedups are workload-specific, and slower results remain in the report.

## Python Week 49 — Advanced Python: the language deeply

Open **Course → Week 49** for six days, 36 parts, 72 exercises, 72 explained
quiz questions and 108 executed examples/solutions. Study iteration protocols,
lazy generators, context ownership, parameterized decorators, descriptors,
class-creation hooks/metaclasses and Python memory behavior. Five original
protocol diagrams and a measured one-million-object layout chart are embedded.
The [standard-library streaming project](docs/python-week49/README.md) combines
strict incremental CSV parsing, validated slotted records, preserved metadata,
resource cleanup, per-file output replacement and reconstructable reports.

## Python Week 48 — Unsupervised learning & deep learning intro

Open **Course → Week 48** for six days, 36 parts, 72 exercises, 72 explained
quiz questions, 108 executed examples/solutions and eight embedded charts.
Study K-means, hierarchical clustering, DBSCAN, PCA, actual t-SNE/UMAP,
calibrated anomaly screening, a gradient-checked NumPy network and CPU PyTorch.
The [offline segmentation and neural lab](docs/python-week48/README.md) preserves
fitting/development/audit boundaries, original-unit profiles, paired predictions
and explicit evidence limits. The neural exercise includes a simple logistic
baseline, validation-selected checkpoints and tested saved inference.

## Python Week 47 — Model evaluation, tuning & pipelines

Open **Course → Week 47** for six days with 36 teaching parts, 72 exercises,
72 explained quiz questions, 108 executed examples/solutions and six embedded
charts. Study task-appropriate cross-validation, grid/random/TPE search, complete
pipelines, actual SHAP explanations, learning curves and error diagnosis.
The [offline evaluation and inference lab](docs/python-week47/README.md) evaluates
the complete parameter-and-threshold procedure, exports a validated numeric model
and verifies a local FastAPI service over real loopback HTTP. Simulation results
and local serving are explicitly distinguished from real customer performance
and public deployment. Existing course content and progress storage are preserved.

## Python Week 46 — Classification

Open **Course → Week 46** for six days with 36 teaching parts, 72 exercises,
72 explained quiz questions, 108 executed examples/solutions and six embedded
charts. Study logistic coefficients, confusion counts, precision/recall/F1,
ROC/PR curves, thresholds, class imbalance and tree ensembles including CPU
XGBoost. The [offline classification lab](docs/python-week46/README.md) separates
training, validation selection and final reporting, with traceable JSON/CSV
artifacts. Simulated cancellation outcomes are clearly identified; the observed
failure to improve final decision cost is preserved and explained.

## Python Week 45 — Regression & prediction

Open **Course → Week 45** for six days with 36 teaching parts, 72 exercises,
72 explained quiz questions, 108 executed examples/solutions and six embedded
charts. Study linear coefficients, MAE/MSE/RMSE/R-squared, polynomial complexity,
Ridge/Lasso, feature ablation, tree ensembles and training-only cross-validation.
The separate [offline demand lab](docs/python-week45/README.md) compares four
predeclared pipelines with a median baseline and exports traceable JSON/CSV
results. Its independent events are explicitly simulated; scores are educational
evidence, not measurements of real customer forecasting performance.

## Python Week 44 — Machine learning foundations

Open **Course → Week 44** for six days with 36 teaching parts, 72 exercises,
72 explained quiz questions, 108 executed Python examples/solutions and three
embedded charts. Learn problem framing, the estimator interface, honest splits,
overfitting, leakage, missing values, scaling, encoding and pipelines.
The independent [offline Iris lab](docs/python-week44/README.md) includes a fixed
train/validation/test workflow, a majority baseline, checked prediction inputs,
inspectable JSON/CSV reports and tests. Installation needs internet once; bundled
data and the installed lab run offline. No learner progress is used as model data.

## Python Week 43 — Full-stack project sprint

Open **Course → Week 43** for six days and 36 parts taking a scoped product from
requirements through backend, authentication, frontend, testing and release.
The [Study Notes practice app](docs/python-week43/README.md) supplies a real
dashboard and Python API with private notes, tags, search, completion filters and
pages, plus reproducible browser/container checks. Its data is separate from
Study Hub progress. Public API hosting is a documented manual exercise.

## Python Week 42 — Docker & deployment

Open **Course → Week 42** for six days with 36 teaching parts, 72 practice
prompts, 72 explained quiz questions and 108 executed Python examples/solutions.
The separate [Week 42 practice project](docs/python-week42/README.md) includes
Docker packaging, PostgreSQL/Compose, restricted database roles, persistence
and backup/restore checks. Public hosting is an ordered manual staging exercise;
the learning website itself remains self-contained and readable offline.

## Games: Chess, Sudoku and Sokoban

Choose **Games** at the top of the site, then **Chess**. Play two players on the same device,
play an offline computer opponent, or practise **10,000 checkmate puzzles**:
4,000 mate in one, 4,000 mate in two, and 2,000 mate in three. The board supports
legal move highlights, castling, en passant, all four promotions, undo, flipping,
automatic game saving and PGN download. Puzzles have rating filters, hints,
solutions and separate independent/assisted completion tracking.

Chess works inside the same self-contained HTML, including when opened directly
from disk. Its saved game and puzzle progress use the existing backup/import and
optional sync. [Data provenance, licenses and authoring notes](data/chess/README.md).

**Sudoku** offers Easy, Medium, Hard and Expert puzzles with pencil notes,
auto notes, undo, hints, answer checking and automatic saving. Its 200 original
layouts create fresh offline variations. Both boards fit the available screen
height; **Focus view** gives them more room. [Sudoku authoring notes](data/sudoku/README.md).

Sudoku also has **Save puzzle**, a **Saved puzzles** library and **Play again**.
Starting another puzzle keeps the previous board, entered numbers and pencil
notes. **Continue** restores that progress; **Play again** resets the exact same
clues for a fresh attempt while retaining completion records. Earlier completed
puzzles can be reconstructed from their saved layout/seed. The additive
`sudoku.saved` map is included in the existing backup/import and optional sync.

**Sokoban** adds 40 original warehouse levels, keyboard/touch/swipe controls,
undo after reopening, restart, offline hints, and saved completion/best results.
Its Focus view keeps the board and large movement buttons together, including
on landscape phones. [Sokoban authoring notes](data/sokoban/README.md).

**Focus view** requests browser fullscreen for all three games. The board fills
the available area, with the original Back/Undo/Hint and other controls arranged
beside it on larger screens or below it on portrait phones. Action labels use
15px text and movement/number controls use 20px text. Exit focus, Escape or Back
returns to the normal layout. If a browser blocks fullscreen, the same Focus
layout remains available with an on-screen explanation.

---

## Running it

**On your computer** — double-click `study-hub.html`. That is the whole setup.

**On the web** — see [Hosting on GitHub Pages](#hosting-on-github-pages) below.

Everything you do is saved in your browser's local storage under the key
`studyHubData_v1`. Nothing is sent anywhere unless you deliberately turn on sync.

---

## The lesson structure

Each lesson in the Lessons tab follows the same shape, so you always know where
you are:

| # | Part | Where it comes from |
|---|------|---------------------|
| 1 | Title | `title` |
| 2 | Learning objective | `objective` |
| 3 | Simple explanation | `p` sections |
| 4 | Syntax | `syn` sections |
| 5 | Example | `code` sections |
| 6 | Output | `out` sections |
| 7 | Key points | `key` sections |
| 8 | Common mistakes | `mistakes[]` |
| 9 | Practice questions | `ex` + `sol` section pairs |
| 10 | Mini challenge | `challenge` |
| 11 | Quiz | `quiz[]` |
| 12 | Mark as complete | `lessonsDone` |
| 13 | Previous lesson | curriculum order |
| 14 | Next lesson | curriculum order |
| 15 | Progress indicator | lesson position + completion |

Every field is optional. A lesson that has no `challenge` simply does not show
that block, so partial lessons degrade gracefully instead of breaking.

### Adding content

Teaching content lives in two places in `study-hub.html`:

- **`DAY_TEACH`** — the body of a single course day, keyed `"week.dayIndex"`
  where the day index is **0-based**, so Day 1 of Week 1 is `"1.0"`. Weeks 1–13
  are written, as are weeks 14-18; weeks 19-52 currently render from the week
  skeleton only.
- **`LESSONS`** — the long-form lessons in the Lessons tab.

Both are rendered by the same function, `renderSections()`, which understands
these section types:

```
h     heading                out   expected output
p     paragraph              key   key-idea callout
code  Python code            tip   green tip box
syn   syntax pattern         warn  red warning box
ex    practice exercise      mis   common mistake (wrong / right / why)
sol   hidden solution        try   predict-the-output
```

A `sol` must come **immediately after** its `ex` — that adjacency is what the
practice-set builders look for.

---

## Japanese Language

Open Japanese in the sidebar or mobile tab bar. The section has a 36-week,
nine-month roadmap from an N5 review to N3 reading and conversation practice.
Weeks 1 and 2 currently contain 12 complete lessons, each with a goal,
explanation, examples, vocabulary, reading, speaking prompt, quiz and personal
note. Later weeks are clearly marked as roadmap topics until full teaching
content is written. Each lesson can add its vocabulary to the existing
spaced-repetition Flashcards deck without creating duplicate cards.

Completions, best quiz scores, notes and reading/speaking checks are saved in
the existing Study Hub backup under the japanese key and merge with device
sync. The page and lessons work offline. Listening playback is only offered
when the device has an offline Japanese voice installed.

Run the browser smoke test on Windows with Chrome installed:
node tests/japanese-smoke.cjs

---

## Syncing between your phone and computer

The app is offline-first. Sync is entirely optional and, when it is not set up,
no network code ever runs.

Progress is stored in an **unlisted GitHub Gist**. Anyone who learns its Gist
ID/link may be able to read it, so keep that ID private and do not put
passwords or other secrets in Study Hub notes.

### One-time setup

1. Go to <https://github.com/settings/tokens> → **Fine-grained tokens** →
   **Generate new token**.
2. Under **Account permissions**, set **Gists** to **Read and write**.
   Grant nothing else.
3. Copy the token.
4. In Study Hub, tap **☁** in the top bar, paste the token, and press **↑ Push**.
   An unlisted Gist is created and its ID appears in the dialog.
5. On your other device, open Study Hub, tap **☁**, paste the **same token** and
   the **Gist ID**, then press **↓ Pull**.

Tick **Push automatically after changes** to have it upload in the background
(debounced, so it will not spam the network while you type).
GitHub repository pushes only publish website code; personal writing needs
Study Hub's own Push/Pull. If a sync fails, the dialog keeps the last error
visible so you can check it later.

### How merging works

A pull **never deletes anything**. It is a union merge:

- Completed days, lessons, journal entries and Life Lessons are added if the
  device does not already have them.
- Quiz scores keep whichever attempt was **higher**.
- Notes, decks, cards, to-dos and quizzes are matched by `id`, so nothing is
  duplicated.

Where both devices have edited the *same* entry, the copy on the device you are
using wins. Move one direction at a time if you want to be certain.

### About the token

- New tokens stay in browser session storage by default. Closing the browser
  may require you to paste the token again. You can opt into **Remember token
  on this device** for convenience. Tokens saved by older versions remain
  remembered until you uncheck that option.
- The token is **never** part of `DB`, so it never appears in an exported
  backup or the synced Gist payload. It still exists in that browser while
  sync is available and can be read by code running in the same browser
  origin; do not treat a public static site as a password vault.
- **Forget token on this device** removes the saved/session token while
  keeping your notes, progress and Gist ID.
- Give the token only the Gists permission. A token with broader permissions
  can access more of your GitHub account; do not use one here.
- If you ever lose the device, revoke the token on GitHub and it is dead.

If you would rather not use a token at all, the **⇄ Transfer** button does the
same job by hand: copy your data on one device, paste it on the other.

---

## Backups

- **⇩ Export** writes `study-hub-backup-YYYY-MM-DD.json`.
- **⇧ Import** offers **Merge** or **Replace all**.
- **⇄ Transfer** copies your data as text for moving between devices.

All three restore paths go through a single function, `applyDefaults()`, so a
backup written by an older version of the app is always safe to load — missing
keys get their defaults rather than being dropped.

Export regularly. Browser storage is not permanent: clearing site data erases it.

---

## Hosting on GitHub Pages

The repository already contains everything Pages needs:

| File | Purpose |
|------|---------|
| `index.html` | Redirects the site root to `study-hub.html` |
| `manifest.webmanifest` | Lets you install it to your phone's home screen |
| `sw.js` | Service worker — keeps the site working offline once loaded |
| `icon.svg` | App icon |
| `.nojekyll` | Stops GitHub from running Jekyll over the files |

### Publishing

Create an empty repository on GitHub named `study-hub`, then:

```bash
git remote add origin https://github.com/YOUR-USERNAME/study-hub.git
git branch -M main
git push -u origin main
```

Then in the repository: **Settings → Pages → Source: Deploy from a branch →
Branch: `main` / `root` → Save**.

After a minute your site is live at:

```
https://YOUR-USERNAME.github.io/study-hub/
```

Open that on your phone and use **Add to Home Screen** to install it.

> **Note:** GitHub Pages on the free tier only serves **public** repositories.
> Your curriculum and notes will be publicly readable. Your progress is not — it
> lives in your browser and, if you enable sync, in a private Gist.

### Updating the site

```bash
git add -A
git commit -m "Describe what changed"
git push
```

The service worker serves the cached copy first and refreshes in the background,
so a change usually appears on the second visit after you publish it.

---

## Project layout

```
study-hub.html          the entire application
index.html              redirect for the hosted site root
sw.js                   offline caching (hosted only)
manifest.webmanifest    installable-app metadata
icon.svg                app icon
.nojekyll               disables Jekyll on GitHub Pages
```

## Editing safely

`study-hub.html` is a single large file with the content inlined, so:

- Commit before a large content edit — `git` is the undo button.
- After editing, check for syntax errors before trusting the file:
  ```bash
  node --check <(sed -n '/^<script>$/,/^<\/script>$/p' study-hub.html)
  ```
  or simply open it and confirm the browser console is clean.
- Add one week of lessons at a time and verify, rather than many at once.

## Kanji reading reference

Selected On’yomi/Kun’yomi additions use KANJIDIC2, © James William BREEN and
the Electronic Dictionary Research and Development Group, under CC BY-SA 4.0.
The licensed extract is `japanese-kanji-readings.json`; it is embedded in the HTML
for offline use. Existing lesson examples/readings and saved user data are preserved.
Dictionary readings can include uncommon forms. Learn the contextual example first;
parentheses mark okurigana and a dash with an explanatory note means no reading in
that dictionary category. This is not a complete Japanese dictionary.

- Documentation: https://www.edrdg.org/wiki/KANJIDIC_Project.html
- Licence: https://www.edrdg.org/edrdg/licence.html
- Refresh selected data monthly or before the next published curriculum update:
  `node scripts/update-kanji-readings.cjs` (requires network access).
- Check the result with `node tests/kanji-readings.cjs` and
  `node tests/japanese-smoke.cjs`, inspect the diff, then publish.

## Japanese Week 30

Open **Japanese Language → Week 30 → Day 1**. Days 1–6 progress from notices,
deadlines and changes to comparing two notices, following references in an essay,
separating opinion from evidence, and giving a three-minute spoken summary.
Each study day has 20 vocabulary slots (including intentional review), five
contextual Kanji with selected On/Kun readings, three grammar patterns, an original
reading with a Nepali explanation, six open reading questions and 14 quiz questions.
Day 7 has a fresh integrated reading, 48 retrieval drills covering every study day,
and a 24-question checkpoint. Practice timings are optional learning targets.

These are original lessons, not an official JLPT paper. Reading task design was
checked against the [JLPT section descriptions](https://www.jlpt.jp/e/guideline/testsections.html)
and the Japan Foundation's [Irodori reading guidance](https://www.irodori.jpf.go.jp/assets/data/elementary02/pdf/Z_howto_en.pdf).
The uncommon On reading for [届](https://www.kanjipedia.jp/kanji/0005337600)
is marked as rare; learners should prioritize 届く and 届ける.

Regenerate only this week's content with `node scripts/japanese-week30.cjs --update`.
Check content preservation with `node tests/japanese-week30.cjs` and run the isolated
browser test with `node tests/japanese-week30-browser.cjs` (Chrome required).

## Compact course navigation

The Python, Japanese, Cybersecurity and Web Development week pages show their
existing daily lessons in a responsive card grid: four columns on desktop, three
on tablets with a sidebar, and two on phones. Full titles/goals remain available
in the cards' hover text and in the original lessons. Python completion buttons
remain separate from the buttons that open a lesson.

On the Python overview, click a phase heading or its +/− control to show/hide its
weeks. All eight phases start closed. The browser remembers your choices under
the separate `studyHubLearningGroups` layout preference; it is outside learner
data and does not change the progress, backup/import or sync format.

Styles and preference handling are in `scripts/learning-navigation.css` and
`scripts/learning-navigation.js`, embedded for offline use. Reapply with
`python scripts/apply-learning-navigation.py`. Validate with
`node tests/learning-navigation.cjs` and
`node tests/learning-navigation-browser.cjs` (Chrome required).

## Shared visual polish

`scripts/premium-polish.css` defines a common heading scale, aligned page frames,
consistent card corners, quieter shadows and compact exercise/quiz spacing across
the workspace. Japanese practice prompts and their closed answer controls share a
row on wider screens; opening an answer gives it the full width. Phone layouts
wrap naturally and retain 44px answer targets. Reading, Kanji and code keep their
learning sizes. No lesson text, app JavaScript or stored data is changed.

The stylesheet is also embedded in `study-hub.html` for offline use. Reapply it with
`python scripts/apply-premium-polish.py`; validate preservation with
`node tests/premium-polish.cjs`. The browser comparison uses
`node tests/premium-polish-browser.cjs --before`, then
`node tests/premium-polish-browser.cjs` (Chrome required).

## Japanese Week 31 · listening for actions and key points

Open **Japanese Language → Week 31 → Day 1–7**. Six study days cover the next
action, corrected times/venues, directions, quantities/counters, telephone
messages and selecting an option against required conditions. Each includes 20
vocabulary entries (new and deliberate review), five kanji with selected On/Kun
readings and compounds, three explained grammar reviews, an original listening
script, six evidence questions, 18 practice prompts and a 14-question quiz.
Day 7 adds a fresh transfer script, 48 retrieval drills spanning all six days and
a 24-question review. Uncommon dictionary readings are labelled; practical word
readings take priority. No official JLPT vocabulary/kanji syllabus is claimed.

For these seven lessons, the question and **Play / Slow / Stop** controls appear
before the explanation. The transcript and its translation stay closed until
the learner reveals them. Playback uses a Japanese voice explicitly reported as
local by the device; it never substitutes an online voice. The 1× button uses
the installed voice's default rate, not a recording of natural human speech or
an official JLPT recording. If voices have not loaded, try Play again; if no
local Japanese voice is installed, the transcript remains usable for reading.
Listening practice is self-assessed, with no autoplay or automatic completion.
Switching lessons or leaving Japanese stops playback. Older lessons retain their
visible reading and existing 0.82× listening button through the shared helper.

Original scripts and explanations were authored for Study Hub. Skill selection
follows the [official N3 listening item purposes](https://www.jlpt.jp/e/guideline/pdf/n3_e.pdf):
extracting a required action and identifying details relevant to a question.
Official practice remains available separately through the
[JLPT sample/workbook page](https://www.jlpt.jp/e/samples/sampleindex.html).
Rare Kun readings were checked against 漢字ペディア entries for
[訂](https://www.kanjipedia.jp/kanji/0004956900),
[階](https://www.kanjipedia.jp/kanji/0000811200),
[号](https://www.kanjipedia.jp/search?k=%E5%8F%B7&kt=1&sk=leftHand),
[条](https://www.kanjipedia.jp/search?k=%E6%9D%A1&kt=1&sk=leftHand) and
[件](https://www.kanjipedia.jp/search?k=%E4%BB%B6&kt=1&sk=leftHand).
No external audio/content dependency was added to the offline app.

Content source: `scripts/japanese-week31.cjs`; apply once with
`node scripts/japanese-week31.cjs`, or revise just these lessons with `--update`.
The optional listening renderer/control patch is maintained in
`scripts/japanese-listening-ui.cjs` and is already embedded in the HTML.
No learner-data key, backup/import, sync or progress format changed.

Run `node tests/japanese-week31.cjs` for source/content preservation and
`node tests/japanese-week31-browser.cjs` for isolated Chrome checks of all seven
days, Furigana, quizzes, notes, Hard, separate weekly decks, navigation, responsive
themes, reload and actual backup/import controls. Speech checks use a controlled
adapter to verify local-only selection, rates, Stop/end/error and no-voice
fallback; physical sound still depends on the device and was not verified by
the headless test.

## Web Development Week 1 · complete beginner lessons

**Web Development → Week 1 → Day 1–7** now contains full teaching, not only
roadmap goals. Study files/folders, editor/browser roles, the three web languages,
your first complete HTML document and edit–save–refresh before building a small
learning journal. Every new construct is explained before the complete example.
Day 7 includes 16 retrieval/repair exercises and a rebuild checkpoint. There are
43 explained quiz questions across the week, with daily/heading notes, best quiz
scores, manual completion/undo and a seven-day progress count.

The existing section, quiz and note components are reused. HTML examples display
as escaped source with an HTML label; existing Python code rendering remains
unchanged. Saved work uses the existing `lessonsDone`, `lessonQuizScores` and
`headNotes` maps with `webdev:1.N` keys, preserving backup/import and configured
sync. The 156-week roadmap is unchanged; Week 2 onward still show roadmap goals.

See [Week 1 guide and reference files](docs/web-development-week1/README.md).
Validate with `node tests/web-development-week1.cjs` and
`node tests/web-development-week1-browser.cjs` (Chrome required). The latter uses
synthetic storage and also opens all four reference pages with networking off.

## GitHub Pages publication

The site is published at its existing `autarivloger.github.io/study-hub/` address
using `.github/workflows/publish-pages.yml`. Pages **Source** is **GitHub Actions**.
The workflow runs on pushes to `main` and can also be started manually. It uses
an explicit Ubuntu 24.04 image, one publishing job and official GitHub actions
pinned to verified release commits. It replaces the built-in branch publishing
workflow that stalled while publishing Web Development Week 1.

`scripts/package-pages.py` copies tracked public files into a new staging
directory, including all course/game/reference files. Hidden development files
are excluded; `.nojekyll` is kept. It does not package Git metadata, ignored local
files or browser storage. The HTML, service worker, manifest and icons are copied
without transforming their contents. No learner-data format changes are needed.

The generated `build-info.json` contains the deployed commit and HTML checksum.
Check this file and the **Publish Study Hub** run before reporting an update as
live. A successful push alone is not proof of a successful publication.

Test packaging with
`python -m unittest discover -s tests -p test_package_pages.py -v`.
The previous publishing setting was **Deploy from a branch → main → / (root)**;
it remains a configuration rollback option. The domain and HTTPS setting stay
the same. No password, personal token or additional repository secret is used.

## Gita book and English study

Open **Yoga & Meditation → Book → Learn in English** for all 18 chapters and
700 verse lessons, with Sanskrit, original plain-English meanings, 93 passage
guides, individual practical reflections, notes and saved study progress.
Chapter 1 has 47 verses; Chapter 13 follows the supplied book's 34-verse numbering.
These are original study notes, not a translation of the complete Hindi commentary.

**Original PDF** preserves the supplied 1,296-page book. It supports Fit page,
Fit width, custom zoom, collapsible controls, pencil overlays and bookmarks.
PDF overlays and the separate English study position reuse the existing
`headNotes` map; studied verses reuse `lessonsDone`. Backup/import retains both.

Authoring sources are `scripts/gita-lessons/`, `scripts/gita-learning.js` and
`scripts/gita-book.js`. Sanskrit provenance is in `books/GITA-SOURCES.txt`.
Rebuild with `node scripts/add-gita-book.cjs`. Check with
`node tests/gita-book.cjs` and `node tests/gita-book-browser.cjs`; the latter uses
a disposable browser profile. Add `--hosted` to verify actual service-worker
caching and offline reload. The original PDF and English lessons use local assets.

## Spelling suggestions

Writing fields offer English spelling suggestions after a short pause. Right-click
an unfamiliar English word or click the small **ABC** button, then choose a
replacement. Nothing is replaced automatically; normal typing, Space and Enter
do not accept suggestions. The browser's Undo command works after a replacement.
Common British variants and course terms are recognised too. Suggestions are
spelling assistance, not grammar checking or a Nepali/Japanese dictionary.

Multiword text selections and Shift + right-click keep the browser's normal menu.
Typing practice, code-answer fields, credentials and technical identifiers are
excluded. The helper uses existing input/autosave handlers and adds no learner
storage keys. **Ignore word** lasts for the current visit.

The bundled Typo.js/SCOWL dictionary runs in a local worker; the spelling helper
does not send text to a remote spelling service. Browser-native spelling settings
remain controlled by the browser. The existing service worker also precaches the
local dictionary without replacing its cache or removing old offline assets.
Run `node scripts/add-spelling.cjs` to embed the helper and styles, then
`node tests/spelling.cjs` and `node tests/spelling-browser.cjs` to verify.
Use `--hosted` on the browser test for actual offline cache/reload verification.
