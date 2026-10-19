# Week 1 · Your computer, browser and first web page

Open **Study Hub → Web Development → Week 1 → Day 1**.

These original lessons start with files and folders. They assume no HTML, CSS,
JavaScript, terminal or framework knowledge. Repeat or split a day as needed.

| Day | Learn and demonstrate |
| --- | --- |
| 1 | Create and find a separate practice folder; identify filenames, extensions and full paths. |
| 2 | Distinguish file manager, plain-text editor and browser; save, close and reopen a text file. |
| 3 | Explain HTML/CSS/JavaScript roles; read matching h1 and p elements. |
| 4 | Create index.html; explain the document shell, attributes, encoding, viewport, tab title and body. |
| 5 | Practise edit–save–refresh; reproduce and diagnose unsaved edits and wrong-file mistakes. |
| 6 | Build a learning journal with h1, two h2 sections and paragraphs; verify explicit requirements. |
| 7 | Rebuild from an empty folder; complete 12 retrieval tasks, four repairs and a 12-question review quiz. |

There are **43 explained quiz questions** across the seven days. Each day includes
practice, a solution to compare after an attempt, readiness checks, heading notes
and day notes. Completion is manual and can be undone. Scores retain the best
attempt. Later weeks retain their existing roadmap status.

## Practice files

Create your own `Documents/web-projects/first-page` folder (or another location
you can reliably find). **Keep it separate from the existing Study Hub project.**
The learner's `index.html` must not replace Study Hub's existing redirect file.

The `examples/` files are complete, self-contained reference pages:

- `first.html`: Day 4's first complete document.
- `revised.html`: Day 5's verified edit/save/refresh result.
- `project.html`: Day 6's learning journal solution.
- `rebuild.html`: Day 7's rebuild reference.

Open a reference with a browser to see its result, or with a text editor to read
its source. Attempt the tasks before consulting the references. No external
styles, scripts, images or server are required. The practice names and sentences
are examples; use your own wording.

## Implementation and saved data

- `scripts/web-development-week1-content.cjs`: original lesson source.
- `scripts/web-development-week1.cjs`: guarded atomic integration and example generation.
- `scripts/web-development-view.js`: existing view, with authored-lesson support.
- `study-hub.html`: embedded content and styles for offline use.

Existing functions render the sections, answer/solution controls, quiz and
heading notes. An optional `lang` field labels HTML/text/file examples and escapes
their code; Python sections without this field keep their existing output.

Storage reuses existing maps with independent namespaced IDs:

| Purpose | Existing map / key |
| --- | --- |
| Completion | `lessonsDone["webdev:1.1"]` through `webdev:1.7` |
| Best quiz score | `lessonQuizScores["webdev:1.1"]` through `webdev:1.7` |
| Day notes | `headNotes["webdev:1.1|day-notes"]` through Day 7 |
| Heading notes | `headNotes["webdev:1.1|<existing heading slug>"]` |

No storage schema, import/export, sync, review enrolment or Python/Japanese/
Cybersecurity content was changed. These records travel through the existing
backup/import and configured sync maps. Opening a lesson does not mark it done.

Run `node scripts/web-development-week1.cjs --update` to regenerate these lessons
from their source. Run `node tests/web-development-week1.cjs` for preservation,
language rendering and syntax checks, then
`node tests/web-development-week1-browser.cjs` for isolated Chrome checks.
The browser test uses synthetic progress, exercises real save/quiz/import
controls and opens the four example pages with networking disabled. It never
opens the learner's browser profile. `tests/web-development-browser.cjs` also
checks all 1,092 existing roadmap days.

## References checked during authoring

- [MDN · Dealing with files](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Environment_setup/Dealing_with_files)
- [MDN · HTML: Creating the content](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started/Your_first_website/Creating_the_content)
- [MDN · Getting started](https://developer.mozilla.org/en-US/docs/Learn_web_development/Getting_started)

The course explanations, practice tasks and example text were written for Study
Hub. Reference websites are optional and need internet; the lessons do not.
