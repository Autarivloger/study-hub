# Python course learning order

The Python Course remains the original 52-week, 364-day programme. Written teaching currently reaches Week 19. Lessons is intentionally empty: its eight former lessons are now distributed across Course days, with advanced examples placed after their prerequisites.

| Former lesson | Main course location |
| --- | --- |
| Foundations | Week 1; input and precise formatting in Week 2 |
| Strings | Week 2, especially Day 4 |
| Conditionals | Week 3 |
| Loops | Week 4 |
| Lists | Week 5 |
| Sets and tuples | Week 6 |
| Dictionaries | Week 7 |
| Functions | Week 9 |

Sorting callbacks/lambda appear from Week 10; comprehensions/generators from Week 11; general imports from Week 12; error handling from Week 14. Limited earlier introductions to `collections` and `copy` retain explicit explanations. Every moved course section has a link at its former location that opens its exact destination part. Search also opens the matching part.

Weeks 1–9 now have a beginner introduction each day: objective, new concept explanation, example, verified output, writing task, explained solution, output prediction and quiz. Original day material, worked examples, challenges and quizzes remain available. Original planning prompts/projects are retained as additional practice at suitable locations. The original anagram exercise now explains why set equality alone is insufficient.

## Saved data compatibility

- Existing day IDs and original mandatory part positions are retained.
- Every original Course exercise retains its original `week.day.ordinal` ID, even after moving to another week. There are 391 such IDs.
- Heading note keys retain their original course or legacy lesson context.
- Original lesson completion and quiz score keys remain in storage. Legacy lesson Resume/review links redirect to Course.
- Appended further-study parts have separate progress controls. Toggling them cannot remove an existing day completion.
- New quiz scores use the existing `lessonQuizScores` map. New practice questions have distinct `starter:`, `legacy:` and `plan:` IDs in the existing solved map.
- Practice defaults to Week 1 and “Up to my current lesson.” Learners can choose another week and disable that filter to explore.
- No localStorage schema, backup format or Gist payload format changes.

`LEGACY_PYTHON_LESSONS` is a compatibility source for old review records, rather than a second displayed curriculum. Keep it until a separately tested migration makes it unnecessary.

## Verification

`tests/python-course-migration.cjs` compares the course against Git baseline `5c88139`, checks content retention and identities, audits syntax prerequisites, runs 108 new Python examples/solutions and parses inline JavaScript. `tests/python-course-smoke.cjs` runs Chrome checks for all authored parts, quizzes, moved practice, saved progress/notes, Resume, search, prerequisite links, practice filtering, reload, mobile layout and theme.

Existing Japanese, spaced review, meanings and kanji tests cover the unaffected features, including backup/import and mocked Gist sync. Browser test fixtures use isolated profiles; real user storage and credentials are not read.

The one-time generator `scripts/reorganize-python-course.cjs` writes atomically and refuses to run on an already migrated file. `--baseline` explicitly rebuilds from the pinned audit baseline and is only for reproducing this migration; do not run it after adding newer content.
