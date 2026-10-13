# Python reviews and practice

This update improves the existing screens and reads exercises directly from
DAY_TEACH. It does not duplicate or rewrite the curriculum.

## Learning scope

- Spaced repetition uses completed parts and old completed course days.
- Required parts of an old completed day remain eligible; optional supplements
  require their own completion flag.
- Old completed Lessons entries use their existing route to the matching
  course day. Their saved review IDs, dates and histories are retained.
- Partial-day completion enrolls the existing day review ID immediately.
  Completing the rest of a day does not reset its schedule.
- Unmarking the last eligible part stops its active reviews. The stored review
  and history remain intact and resume when the source is completed again.
- Merely opening a later week does not mark previous lessons as studied.

## Review experience

Prompts mix exercises, code prediction, lesson quizzes, mistake correction and
concept recall. Completed parts contribute across their full sections, without
the former first-eight cutoff. Learning-objective metadata is not a question.
Duplicate prompts prefer the real quiz choices when available.

Code, needed reference context, worked solutions, output and explanations use
the existing lesson components. Answers remain hidden until revealed.
Another question changes the prompt without grading it. Original lesson links
open the exact source part. Review drafts survive reveal/option selection
within the current question but are not persisted after leaving the session.

The adaptive date/stage/rating algorithm is unchanged. Python history entries
may additionally record questionId, an optional backwards-compatible reference
that prevents immediate repeats and prioritizes less-reviewed questions.
Question kinds/parts are interleaved; questions with the lowest recorded usage
are selected before more-reviewed questions. Older history without questionId
remains valid. Question selection is separate from the review schedule.

Japanese prompt selection and scheduling remain unchanged. The existing
reminder stays available on the homepage and does not cover an active review
or Python Practice screen.

## Python Practice

Find it in the Python Course header, course homepage or review dashboard.

- Starts with all studied weeks, rather than only Week 1.
- Studied lessons only uses saved completion flags.
- Include current part optionally adds only the exact current part.
- Turn off studied-only for an explicitly labeled exploration of all authored
  exercises; existing unrestricted practice is still available.
- Week/phase filters, set size and only-unsolved filters remain available.
- Shuffle mixes parts and changes the first exercise when alternatives exist.
- Exercise attempts use the existing headNotes map under python-practice|ID.
- Pending attempt edits are saved when leaving or refreshing the page, including
  edits made during the short autosave delay.
- Solved flags retain their original course.practice.solved identities.
- Model solutions, output, reference context and exact source links are available.
- Code must be run in the learner's own editor/terminal; this update does not
  claim to execute Python inside the website.

## Storage and verification

No new localStorage key, database root or migration version is introduced.
Existing course.partsDone now participates in non-destructive import/sync.
The existing legacy attempt counter keeps the larger merged value without
double-counting a reimport; uniquely solved IDs remain the practice metric.
Review history merge includes optional questionId so distinct questions with
the same timestamp/rating are retained.

Static tests compare the entire authored curriculum and storage defaults with
the previous commit, verify all 1,070 exercise identities and test full prompt
extraction. Isolated-browser tests use fictional data to check eligibility,
variety, nonrepeat, code/quiz feedback, partial enrollment, saved attempts,
solutions, exact links, shuffle, history, actual export/import merge and replace,
refresh, mobile themes and JavaScript errors. Existing course, review and habit
regressions also run. No personal profile, credentials or actual progress is read.
