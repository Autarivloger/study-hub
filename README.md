# Study Hub

An offline-first Python learning platform. One self-contained HTML file holding a
12-month, 364-lesson curriculum, plus notes, a daily journal, flashcards with
spaced repetition, quizzes, a Pomodoro timer, and a Life Lessons journal.

No build step. No dependencies. No server required.

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
  are written; weeks 14–52 currently render from the week skeleton only.
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

## Syncing between your phone and computer

The app is offline-first. Sync is entirely optional and, when it is not set up,
no network code ever runs.

Progress is stored in a **private GitHub Gist** that only you can read.

### One-time setup

1. Go to <https://github.com/settings/tokens> → **Fine-grained tokens** →
   **Generate new token**.
2. Under **Account permissions**, set **Gists** to **Read and write**.
   Grant nothing else.
3. Copy the token.
4. In Study Hub, tap **☁** in the top bar, paste the token, and press **↑ Push**.
   A private Gist is created and its ID appears in the dialog.
5. On your other device, open Study Hub, tap **☁**, paste the **same token** and
   the **Gist ID**, then press **↓ Pull**.

Tick **Push automatically after changes** to have it upload in the background
(debounced, so it will not spam the network while you type).

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

- It is stored under its own key, `studyHubSync`, and is **never** part of `DB`.
  It therefore never appears in an exported backup or in the synced payload.
- It lives only in that browser, on that device.
- It only has permission to read and write your Gists — nothing else in your
  GitHub account.
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
