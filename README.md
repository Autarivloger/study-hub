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

The refined theme adds softly shaded cards, a glass desktop header, coordinated
study tools and clearer visual hierarchy. All styles remain embedded for offline
use, with no font download or decorative JavaScript. Reading widths, text selection,
touch targets, Furigana navigation clearance, reduced motion and High Contrast
keyboard outlines are covered by the design checks.

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
