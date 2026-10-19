# Performance evidence

Run `python bench.py --size 2000 --output artifacts/benchmark.json` after installing
the package. The baseline scans a growing output list; the implementation adds a
set index while preserving the same ordered string result.

The fixture is 2000 unique labels followed by those same labels, not actual user
data. Input creation is excluded; complete function calls, validation and set
construction are included. Five repetitions alternate execution order. The report
keeps raw seconds, medians, interpreter and observed ratio. `timeit` disables
garbage collection by default. Try unique, repeated and small inputs separately.

No test requires a 10x result. A measured 10x gain for this fixture would not prove
a 10x gain for reading CSV, startup, networking or your full application. Amdahl's
law bounds total benefit by the fraction of time actually improved.

`cProfile` helps locate call costs; profiler-instrumented times are not the final
benchmark. `tracemalloc` reports Python allocations during a call, including the
retained result. It excludes already-created input and is not process RSS. The
set-based solution can be faster while allocating more memory. Measure honestly.
