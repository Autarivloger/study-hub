# Week 27: NumPy and numerical Python

Six days with four parts each, 48 practice/challenge prompts, 58 quiz questions and 72 verified example/solution outputs.

| Day | Focus |
| --- | --- |
| 1 | Lists versus arrays, shapes, vectorization, fair timing and buffer memory |
| 2 | Constructors, ranges, local random generators and dtype/casting |
| 3 | Index shapes, views/copies, Boolean masks and advanced indexing |
| 4 | Ufuncs/matrix multiplication, broadcasting, normalization and z-scores |
| 5 | Axis reductions, indexes/ties, missing data and weights |
| 6 | Reshape/transpose, joining/splitting, grade project and full review |

Use Python 3.11+ with NumPy 2.x:

    python -m pip install numpy

Installation initially needs internet. The supplied examples and course work offline afterward.

## How to study

Before running each example, write its input and output shapes and name the axis meanings. Predict whether a selected result shares data. Trace the shown output, then write the build and challenge without copying. Explain quiz reasons and use existing course notes/part completion.

The benchmark actually measures both implementations on a million entries, but does not freeze machine-dependent seconds or a speed ratio into the expected output. Inspect its timing variables on your own computer. Array nbytes describes its element buffer, not total process memory.

## Grade-analysis project

Copy this folder to a practice directory:

    python grade_analysis.py scores.csv report.json
    python grade_analysis.py scores.csv curved-report.json --curve 5 --z-threshold 2 --pass-score 60
    python grade_analysis.py --help

The input is a plain rectangular numeric CSV with no header, names, comments, quoted fields or missing cells. Rows represent student input order; columns represent assignments. This is a narrow numeric-text contract, not an arbitrary CSV importer.

The project validates a nonempty 2-D real numeric table and finite scores in 0–100. Boolean/text/object/complex inputs are rejected before conversion. Single-row and single-column files retain their 2-D orientation. Limits are 2 MB input, 10,000 students and 200 assignments.

Numeric work has no Python for/while/comprehension loops. NumPy performs row/column statistics, bounded grade adjustment, column normalization and z-score flags. Standard library file/CLI/JSON code and NumPy internals still perform work.

### Explicit policies

- Standard deviation uses ddof=0 for descriptive population statistics of the supplied input.
- Default curve adds five points per cell, clipped to 0–100. This is a practice rule, not an actual grading recommendation.
- Constant columns normalize to zero.
- Identical student means receive zero z-scores.
- Outlier flags use absolute raw-student-mean z-scores at/above a positive threshold, default 2. Flags request inspection; they do not delete data or establish wrongdoing.
- Missing, nonfinite and out-of-range scores are rejected rather than silently filled.
- Report indexes are zero-based input positions, not stable student identities.

The source file remains unchanged. Every input/policy validation finishes before a separate JSON report is atomically replaced. Failed validation or an unrelated pre-existing temporary file preserves the prior report.

## Primary references

- [NumPy beginner guide](https://numpy.org/doc/stable/user/absolute_beginners.html)
- [Broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html)
- [Copies and views](https://numpy.org/doc/stable/user/basics.copies.html)
- [Data types](https://numpy.org/doc/stable/user/basics.types.html)
- [Random generators](https://numpy.org/doc/stable/reference/random/generator.html)
- [Standard deviation](https://numpy.org/doc/stable/reference/generated/numpy.std.html)
- [Masked division](https://numpy.org/doc/stable/reference/generated/numpy.divide.html)
- [Numeric text loading](https://numpy.org/doc/stable/reference/generated/numpy.loadtxt.html)

The explanations, examples, fictional scores, exercises and project are original teaching material. Documentation verifies API behaviour.
