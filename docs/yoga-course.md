# Yoga & Meditation

The former empty Lessons tab now opens an original Hindi/Nepali intermediate practice module. Its internal `lessons` view identifier remains for legacy Python links, which still route to the corresponding Course days.

## Initial module

Seven repeatable sessions start from the learner's reported 10 minutes of familiar Sun Salutation and 5 minutes of running. They add controlled movement, supported balance, recovery and attention practice. The suggested 20/30-minute schedules are adaptable; there is no daily streak or compulsory hold duration. This is a gradual intermediate path, not an assumption of advanced pose competence.

Ten pose guides cover entry, breathing, alternatives, common mistakes and exit. Five breath/meditation guides include natural breath awareness, alternate-nostril breathing without retention, optional mantra, observation and walking attention. Sessions contain 21 understanding questions in total.

## Sources and teaching boundaries

The supplied Gita Press *श्रीमद्भगवद्गीता* PDF has 1296 pages and a legacy font encoding that prevents reliable plain text extraction. The cover, contents and relevant Chapter 6 pages were inspected visually. References are 6.12–14 (printed pages 434–436), 6.16–17 (438–439), 6.26 (456), and 6.35 (467–468). The website uses original paraphrases and distinguishes spiritual context from modern practice adaptations. The full PDF and its modern translation are not bundled with the site.

Safety references: [NCCIH Yoga](https://www.nccih.nih.gov/health/yoga-effectiveness-and-safety) and [NCCIH Meditation](https://www.nccih.nih.gov/health/meditation-and-mindfulness-effectiveness-and-safety). No cure, detox, or guaranteed spiritual outcome is claimed. Text guidance cannot assess individual alignment. The self-guided module excludes extreme inversions, forced lotus, breath retention and forceful breathing.

## Compatibility

- Completion: existing `lessonsDone`, keys `yoga:intermediate:1.N`.
- Quiz scores: existing `lessonQuizScores`, keys `yoga:quiz:1.N`.
- Reflection notes: existing `headNotes`, keys `yoga:intermediate:1.N|reflection`.
- Existing backup, merge/import and Gist payload mechanisms handle these maps without a new schema or token handling.
- Python review migration now filters actual legacy Python lesson IDs, so Yoga completion does not repeatedly trigger a nonexistent Python review.
- Yoga's continue button uses the first incomplete session. It does not replace the saved Python Course Resume position.

`scripts/yoga-course.cjs` contains the authored data, `scripts/yoga-view.txt` the view implementation, and `scripts/add-yoga.cjs` the one-time additive installer. It refuses duplicate installation. Later content edits should update the corresponding authored data and inline literal together, preserving IDs.

## Verification

`tests/yoga-course.cjs` checks course references, quiz choices, unchanged Python/Japanese teaching and unchanged storage defaults. `tests/yoga-smoke.cjs` uses an isolated Chrome profile to test all sessions, times, quizzes, notes, completion/undo, next/previous, continue, reload, actual backup export/file import merge and replace, three screen sizes, both themes, screenshots and JavaScript errors. Existing Python and Japanese tests cover the retained platform features.
