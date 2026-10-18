# Week 49 — Advanced Python: the language deeply

Open **Course → Week 49**. Six days and 36 parts develop iterators, generators,
resource ownership, decorators, attribute protocols, class creation and memory.
Each part has first-use explanations, syntax, executed examples, mistakes,
two practice prompts/solutions and explained quizzes. Take as long as needed.
There are 72 exercises, 72 quiz questions, 108 executed snippets, five original
protocol diagrams and one measured memory chart, all embedded in the offline HTML.

## Run the project without package installation

Use Python 3.12 or 3.13 in this folder:

```powershell
python lab.py --output artifacts
```

This generates 10,000 synthetic events, streams validated study/review records,
writes selected CSV and a report, and compares **1,000,000 live objects per layout**
in separate owned Python processes. Runtime uses only the standard library, runs
offline, and never reads Study Hub progress, notes, credentials or browser data.

For a smaller quick experiment:

```powershell
python lab.py --output artifacts-small --rows 100 --memory-records 10000
python memory_lab.py --count 1000000
```

To check your own separate CSV, the exact UTF-8 header is
`event_id,category,minutes`. Run:

```powershell
python lab.py --source my-events.csv --output artifacts-custom --memory-records 10000
```

Use a dedicated output folder; successful runs replace the named output artifacts.
An input cannot also be an output artifact. Default demo generation uses only
fictional local events and creates `synthetic-events.csv` in that output folder.

## Optional tests and figure reproduction

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
```

On Linux use `.venv/bin/python`. Installation needs internet once. Tests then run
offline. The final optional plotted example, and rebuilding the website's original
figures, need `requirements-authoring.txt` (Matplotlib/NumPy/Pandas plus test tools).
Those libraries are not runtime dependencies of the actual CSV/memory project.
Imports of `streamkit`, `memory_lab` and `lab` mean these supplied local files.

## Public API and guarantees

| Object/function | Purpose |
| --- | --- |
| `CountIterator(stop)` | Single-use iterator over 0 through stop-1; exhausted stays exhausted. |
| `CountRange(stop)` | Iterable returning independent fresh counters. |
| `count_calls(label=...)` | Metadata-preserving ordinary-function call/failure counter. |
| `NonNegativeInt` | Data descriptor validating every public assignment to minutes. |
| `Event` | Slotted event with readable id/category and validated minutes. |
| `iter_events(handle)` | Lazy strict CSV parsing over a caller-owned open text handle. |
| `select_categories(events, allowed)` | Lazy order-preserving category filter. |
| `as_rows(events)` | Lazy projection to output dictionaries. |
| `open_events(path)` | Context manager owning and closing the input file. |
| `atomic_text(path)` | Context manager replacing one file after successful flush/close. |
| `write_selected(source, destination)` | Complete-consumption pipeline with fixed-category totals. |
| `compare_layouts(count)` | Separate-process tracemalloc comparison with explicit scope. |

CSV input is strict: exact header/order, exact row width, nonempty id up to 64
characters, category study/review/break, and 1–9 ASCII decimal minute digits.
Minutes may be zero. An empty data section is valid. All rows are validated before
filtering; a malformed break row still fails a study-only selection.

Creating the generator does not parse the file. Consume it inside the owning
`with`; escaping it beyond that lifetime is an API error. Partial consumption
cannot establish whole-file totals or absence of a later malformed row.

Strict parsing failures propagate, close resources, remove the owned temporary
output and preserve an existing destination. Successful file replacement is
atomic per file. The CSV and JSON are **not one multi-file transaction**: after an
interruption, compare the CSV SHA-256 with the saved report. A digest checks byte
agreement with a trusted report, not source authenticity.

Pipeline retained state is one event/row, parser buffers and at most three category
totals. It does not retain all input rows. This is bounded state relative to row
count under fixed field/category assumptions, not an unconditional constant-byte
claim: record size, CSV parser limits, counters and buffering still matter. Sorting
everything, list(...), arbitrary per-id grouping or tee buffering can break that
bound. The intentionally eager object-layout experiment is a separate task.

The decorator counts synchronous calls and re-raises their exceptions. A decorated
generator function returns before iteration, so later iteration failures are not
ordinary call failures. Counters are local mutable instrumentation, not thread-safe
service metrics. Wrapping does not automatically preserve coroutine/generator kind.

Descriptors/slots express an API, not a security boundary. Underscore storage can
still be manipulated deliberately. Slots restrict ordinary extra attributes;
they do not make nested values or objects immutable. Custom metaclasses are taught
in isolated examples; this library uses simpler hooks where they are sufficient.

## Memory evidence

`memory_lab.py` compares a normal dictionary-backed two-field class with a slotted
two-field class. Each measurement owns a fresh Python process, keeps the same
number of objects alive, and assigns the same shared zero values. It records the
interpreter/version, live traced bytes and peak traced bytes.

The measurement includes the list of references and traced instance storage.
It does not measure complete process RSS, every native allocation, recursive deep
size or runtime speed. Results depend on interpreter, version, build and workload.
Do not promise a fixed universal number of saved bytes. `sys.getsizeof` in earlier
parts is explicitly shallow and not a substitute for this controlled comparison.

Tests verify independent iteration, sticky exhaustion, laziness and delayed errors,
resource release, strict invalid-row handling, replacement rollback, descriptor
validation, decorator metadata and exception behavior, generator-call scope,
small-layout comparison and report/CSV reconstruction. The documented full command
also exercises the one-million-object comparison.

## Optional primary references

- [Iterator types](https://docs.python.org/3.12/library/stdtypes.html#iterator-types)
- [Yield expressions](https://docs.python.org/3.12/reference/expressions.html#yield-expressions)
- [itertools](https://docs.python.org/3.12/library/itertools.html)
- [Context managers](https://docs.python.org/3.12/library/contextlib.html)
- [Decorators and wraps](https://docs.python.org/3.12/library/functools.html)
- [Descriptor guide](https://docs.python.org/3.12/howto/descriptor.html)
- [Data model and class creation](https://docs.python.org/3.12/reference/datamodel.html)
- [tracemalloc](https://docs.python.org/3.12/library/tracemalloc.html)

Original explanations and diagrams remain readable offline; optional references
supplement the executed examples rather than replacing the lesson.
