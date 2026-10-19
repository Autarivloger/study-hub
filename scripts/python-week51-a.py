L(0, '1. Define the result before measuring speed',
  'Write an observable contract and a representative workload before changing code.',
  [('Performance contract', 'A written agreement about inputs, output, order, errors and what a measurement includes. A faster different answer is not an optimization.'),
   ('Baseline', 'The correct starting implementation and its measurements, retained for comparison.'),
   ('bench.slow_unique and fixture', 'Original functions supplied in docs/python-week51/bench.py. slow_unique scans a list; fixture creates synthetic labels, never your study history.')],
  "Week 50 taught you how execution models overlap work. This week asks an earlier question: why does the program take time at all? Adding workers to an inefficient algorithm can multiply cost without fixing its cause. Begin with the required answer, then measure the actual work.\n\nOur running example removes repeated study-topic labels. It must retain the first occurrence, preserve case, accept a one-shot iterable and return a new list. For valid strings, ['SQL', 'Python', 'SQL'] must become ['SQL', 'Python']; sorting it would change the contract. The packaged version additionally rejects non-string items.\n\nThe reference function scans a growing result list for every input item. It is intentionally simple and useful as a correctness oracle for valid inputs. Before timing, cover empty input, all duplicates, all distinct labels and case differences. Also decide whether input creation, validation, disk reads and startup belong inside your timing boundary. The example establishes behavior; it does not yet prove any speed improvement.",
  r'''from bench import slow_unique
values = ["SQL", "Python", "SQL", "python", ""]
original = values.copy()
print(slow_unique(values))
print("Input unchanged:", values == original)
print("Empty:", slow_unique([]))''',
  'Check the first-occurrence result for three representative input shapes.',
  r'''from bench import slow_unique
for values in [[], ["a", "a", "a"], ["c", "b", "a"]]:
    print(values, "->", slow_unique(values))''',
  'Show why a sorted answer is not interchangeable with the required ordered answer.',
  r'''from bench import slow_unique
values = ["b", "a", "b"]
print("Required:", slow_unique(values))
print("Different contract:", sorted(set(values)))
print("Same answer:", slow_unique(values) == sorted(set(values)))''',
  [('Can sorting replace first-seen ordering without a compatibility decision?', 'No', 'Always', 'Only for long lists', 'Output order is part of the contract, independent of speed.'),
   ('What should be established before a speed claim?', 'Equal required results and timing scope', 'A larger thread count', 'A shorter function name', 'A benchmark needs comparable work and a declared measurement boundary.')],
  'Time two functions that produce different ordering and call the faster one an improvement.',
  'Write the contract; verify equality; measure equivalent complete work.',
  'The small fixtures make ordering and input ownership visible before timing adds noise.',
  syntax='contract -> valid reference -> representative input -> measurement -> decision')

L(0, '2. Read cProfile as a map of call costs',
  'Use call counts, own time and cumulative time to locate a bottleneck.',
  [('cProfile.Profile', 'A standard-library deterministic profiler. It observes calls and returns; instrumenting code adds overhead.'),
   ('runcall', 'Run a callable under the profiler while returning its normal result.'),
   ('pstats.Stats', 'Read profiler records. A record identifies a file, line and function; tottime excludes child calls while cumtime includes them.')],
  "Suppose your script takes four seconds. Guessing that the longest-looking function is responsible is unreliable. A profiler shows which functions ran, how often and where their time accumulated. Use that map to choose a small area to investigate.\n\nIn a profile table, ncalls counts calls. tottime is time attributed to the function itself, excluding its callees; cumtime includes work below that function. A top-level wrapper can have a large cumulative time simply because it owns the whole job. Do not optimize the wrapper's spelling when an inner scan owns the repeated work.\n\nBelow we profile the reference once and inspect its named record. The record tuple contains primitive calls, total calls, own seconds, cumulative seconds and caller data. Filtering on the known function keeps the teaching output readable. For a real script, use python -m cProfile -s cumulative your_script.py or save a .prof file and inspect it with pstats. After choosing an improvement, benchmark again without the profiler: instrumented timings answer a different question.",
  r'''import cProfile
import pstats
from bench import fixture, slow_unique
profile = cProfile.Profile()
result = profile.runcall(slow_unique, fixture(40))
stats = pstats.Stats(profile)
for key, record in stats.stats.items():
    if key[2] == "slow_unique":
        print("Function:", key[2], "calls:", record[1])
        print("Own time nonnegative:", record[2] >= 0)
        print("Cumulative >= own:", record[3] >= record[2])
print("Distinct results:", len(result))''',
  'Profile two calls and confirm the total named-function call count.',
  r'''import cProfile
import pstats
from bench import slow_unique
profile = cProfile.Profile()
profile.enable()
slow_unique(["a", "b", "a"])
slow_unique([])
profile.disable()
print(sum(row[1] for key, row in pstats.Stats(profile).stats.items()
          if key[2] == "slow_unique"))''',
  'Explain why optimizing a rarely called helper cannot remove most runtime.',
  r'''total_seconds, helper_seconds = 10, 1
print("Helper share:", helper_seconds / total_seconds)
print("Best possible total if helper became free:", total_seconds - helper_seconds)
print("Maximum whole-program ratio:", round(total_seconds / (total_seconds-helper_seconds), 2))''',
  [('Which profiler column includes time in child functions?', 'Cumulative time', 'Own time only', 'The filename', 'Cumulative time follows the call subtree.'),
   ('Should profiled execution supply your final benchmark comparison?', 'Use a separate unprofiled benchmark', 'Always use the profiler alone', 'Disable correctness checks instead', 'Profiler overhead can affect implementations differently.')],
  'The top-level function has the largest cumulative time, so rewrite that wrapper first.',
  'Inspect its callees and repeated operations; target the measured cost.',
  'Call counts and time ownership guide investigation; they do not automatically prescribe a fix.',
  syntax='profile = cProfile.Profile(); result = profile.runcall(function, argument)',
  shell='python -m cProfile -s cumulative bench.py --size 1000')

L(0, '3. Narrow the investigation with line profiling',
  'Use line-level hit counts and timings after a function-level profile identifies a target.',
  [('line_profiler.LineProfiler', 'An optional development tool that instruments selected Python functions by source line. Install line-profiler from the supplied development requirements.'),
   ('add_function / get_stats', 'Register a function, run it under the profiler, then inspect recorded line hits and timer units.'),
   ('Instrumentation overhead', 'Extra work introduced by measurement. Fine-grained tools can change the runtime they observe.')],
  "A function can contain validation, a loop, a membership test and an append. Function totals tell you which function is expensive; line profiling helps distinguish those operations inside it. Instrument only a small relevant region so the report stays useful.\n\nThe slow deduplication function lives in a real source file, bench.py. That matters: a line profiler associates measurements with source lines. We register that function and call it once with duplicate labels. A high hit count means the line ran often; expensive total time can also arise from one unusually costly operation. Read hits, total time and per-hit time together.\n\nThe example prints the function name and whether useful line records exist, rather than promising identical nanoseconds on every device. To inspect the detailed table yourself, call profiler.print_stats(). Always state the timer unit from get_stats().unit when converting raw timings to seconds. Line profiling is a diagnostic follow-up, not a reason to measure every function or to replace the final uninstrumented benchmark.",
  r'''from line_profiler import LineProfiler
from bench import slow_unique
profiler = LineProfiler()
profiler.add_function(slow_unique)
print(profiler.runcall(slow_unique, ["a", "b", "a"]))
stats = profiler.get_stats()
for key, timings in stats.timings.items():
    print("Function:", key[2])
    print("Recorded source lines:", len(timings) > 0)
    print("Positive timer unit:", stats.unit > 0)''',
  'Record a larger fixture and confirm the loop has repeated line hits.',
  r'''from line_profiler import LineProfiler
from bench import fixture, slow_unique
profiler = LineProfiler()
profiler.add_function(slow_unique)
profiler.runcall(slow_unique, fixture(20))
hits = [hits for rows in profiler.get_stats().timings.values() for line, hits, ticks in rows]
print("Repeated line execution:", max(hits) > 20)''',
  'Convert hypothetical raw ticks to seconds using the stated unit; do not confuse ticks with seconds.',
  r'''ticks, unit = 2500, 1e-9
print("Illustrative seconds:", ticks * unit)
print("Illustrative microseconds:", ticks * unit * 1_000_000)''',
  [('When is line profiling most useful?', 'After finding a relevant expensive function', 'Before defining the program result', 'Instead of tests', 'Narrowing the target makes line-level evidence interpretable.'),
   ('Are raw line-profiler ticks automatically seconds?', 'No, multiply by the reported unit', 'Yes', 'They are always milliseconds', 'Timer units must accompany numeric measurements.')],
  'A line has many hits, therefore it must dominate runtime.',
  'Compare total time, per-hit time and the operation performed on that line.',
  'Repeated execution is evidence of work count; cost per operation still determines the bottleneck.',
  syntax='profiler.add_function(target); profiler.runcall(target, data); profiler.print_stats()')

L(0, '4. Benchmark equal work with timeit',
  'Measure repeated unprofiled calls and state what setup and garbage collection are doing.',
  [('timeit.Timer / repeat', 'Measure a callable repeatedly. number is calls per sample; repeat is the number of samples.'),
   ('Per-call time', 'A sample total divided by its number of complete calls. Comparing different call counts without normalization is misleading.'),
   ('Minimum and median', 'Minimum approximates a low-interference lower bound; median describes a typical measured sample. Retain raw samples and label the summary you choose.')],
  "A single stopwatch observation includes scheduling noise, caches and other work on the machine. Repeating the same complete operation gives more evidence. It does not make a tiny artificial input representative of the real application.\n\nHere the fixture is created before timing, while each function call includes its own result construction. The faster function includes validation and creation of the set index. Both must produce exactly the same ordered result before any time ratio is reported. When comparing multiple implementations, alternate their measurement order and run small, distinct-heavy and duplicate-heavy fixtures.\n\ntimeit normally disables garbage collection while timing. That can be reasonable for a small operation but differs from some production workloads. If collection is relevant, explicitly enable it in setup and explain the choice. For very short operations, increase number to amortize timer overhead, then divide by number. The example records observations; no fixed ratio or pass/fail speed threshold is required.",
  r'''from statistics import median
from timeit import Timer
from bench import fixture, slow_unique
from studyhub_records import unique_in_order
values = fixture(400)
assert slow_unique(values) == unique_in_order(values)
for name, function in [("list scan", slow_unique), ("set index", unique_in_order)]:
    samples = Timer(lambda: function(values)).repeat(repeat=5, number=3)
    per_call = [seconds / 3 for seconds in samples]
    print(name, "median milliseconds:", round(median(per_call) * 1000, 4))
    print("Five positive observations:", len(samples) == 5 and min(samples) > 0)''',
  'Normalize illustrative sample totals when each sample contains 20 calls.',
  r'''from statistics import median
totals = [0.040, 0.044, 0.042]
per_call = [value / 20 for value in totals]
print("Median milliseconds per call:", round(median(per_call) * 1000, 2))''',
  'Use the supplied benchmark and verify its scope and equal-result check.',
  r'''from bench import benchmark
report = benchmark(size=100, repeats=3)
print("Equal results:", report["equal_results"])
print("Samples per method:", [len(x) for x in report["seconds"].values()])
print("Recorded implementation:", bool(report["implementation"]))''',
  [('What does number=20 mean in timeit.repeat?', 'Twenty calls per recorded sample', 'Twenty seconds', 'Twenty CPU cores', 'A sample is a total for number calls and needs per-call normalization.'),
   ('Does timeit normally leave garbage collection enabled?', 'No, its default disables collection during timing', 'Always', 'Only on Linux', 'GC policy is part of the benchmark scope.')],
  'Compare one candidate call with twenty baseline calls and use raw totals.',
  'Use the same workload and normalize totals by complete call count.',
  'Record the samples and scope so another learner can reproduce the comparison.',
  syntax='samples = Timer(callable).repeat(repeat=5, number=3)')

L(0, '5. Measure Python allocation peaks with tracemalloc',
  'Distinguish retained allocations, peak allocations, object size and process memory.',
  [('tracemalloc', 'Trace Python memory allocations after tracing starts. It does not represent all native memory or total operating-system process RSS.'),
   ('Current versus peak', 'Current is traced memory still allocated; peak is the highest traced amount since tracing began or its peak was reset.'),
   ('Snapshot comparison', 'Compare traced allocation snapshots to locate retained growth by file/line. Retained growth is not automatically a leak.')],
  "The set index avoids repeated scans by retaining more state. That is a deliberate time/memory tradeoff. A faster function can use a higher temporary peak, and a streaming function can still retain a large result if its API returns a list.\n\nStart tracing before the allocations you want to study. The supplied memory_peak helper receives an already-created input, starts tracing, calls one function and measures while the result is still alive. Consequently its numbers include result construction and temporary Python allocations, but exclude input creation before tracing. That boundary must accompany the output.\n\nA snapshot comparison can help locate growing caches or retained containers. It reports allocation differences, not a diagnosis by itself: a cache intentionally filled for later use can grow once and then stabilize. Also avoid adding shallow sys.getsizeof values as though they included every referenced object. Use an appropriate process-memory tool separately when RSS or native libraries are the actual concern.",
  r'''from bench import fixture, memory_peak, slow_unique
from studyhub_records import unique_in_order
values = fixture(300)
for name, function in [("list scan", slow_unique), ("set index", unique_in_order)]:
    result = memory_peak(function, values)
    print(name, "peak traced bytes:", result["peak_bytes"])
    print("Retained result items:", result["result_items"])''',
  'Trace a retained bytearray and verify peak is at least current traced memory.',
  r'''import tracemalloc
tracemalloc.start()
payload = bytearray(20000)
current, peak = tracemalloc.get_traced_memory()
print("Payload bytes:", len(payload))
print("Peak >= current:", peak >= current)
tracemalloc.stop()''',
  'Use snapshots to detect an intentional retained allocation without claiming a leak.',
  r'''import tracemalloc
tracemalloc.start()
before = tracemalloc.take_snapshot()
kept = [bytearray(5000) for _ in range(4)]
after = tracemalloc.take_snapshot()
growth = sum(stat.size_diff for stat in after.compare_to(before, "lineno"))
print("Retained blocks:", len(kept))
print("Positive traced growth:", growth > 0)
tracemalloc.stop()''',
  [('Does tracemalloc peak equal total process RSS?', 'No', 'Always', 'Only for dictionaries', 'It traces Python allocations within its tracing boundary.'),
   ('Can a faster set-based solution allocate more memory?', 'Yes', 'Never', 'Only if it is incorrect', 'Indexing exchanges retained state for less repeated search work.')],
  'Call a traced Python allocation peak the total RAM used by the application.',
  'Label the tracing interval, retained result and excluded memory categories.',
  'The measurement is useful because its boundary is explicit, not because it claims to measure every byte.',
  syntax='tracemalloc.start(); current, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()')

L(0, '6. Report an improvement without inventing a speedup',
  'Combine equal results, measured timings and whole-program limits into an honest optimization decision.',
  [('Observed speed ratio', 'Baseline seconds divided by candidate seconds for the declared equal-result workload. A value below one means the candidate was slower.'),
   ("Amdahl's law", 'If fraction p of total runtime is improved by factor s, ideal whole-program speedup is 1 / ((1-p) + p/s), assuming the rest is unchanged.'),
   ('Regression budget', 'A stated performance limit measured under controlled conditions. Separate noisy performance observations from deterministic correctness tests.')],
  "The curriculum asks you to seek a dramatic improvement, but a target such as 10x is an experiment goal, not a number to print regardless of the result. Preserve slower observations and explain the input, interpreter, validation and setup boundaries. Correctness tests should pass even when the computer is busy.\n\nThe chart executes both deduplication implementations on three declared distinct-label counts. It compares complete calls after checking equal answers. Input generation is outside timing; candidate set construction is inside. The vertical axis is logarithmic because the scales may differ greatly. These are measurements of synthetic in-memory labels, not of your website or a full CSV pipeline.\n\nFinally estimate the possible whole-program benefit. If duplicate removal owns only 20% of total elapsed time, making it ten times faster yields about 1.22x overall under the simple model. If the profile shows I/O dominates, optimize the relevant stage or accept that this change has a small application effect. Write a short decision including correctness, time, memory, complexity and whether the added code is worth maintaining.",
  r'''import matplotlib.pyplot as plt
from bench import benchmark
sizes = [30, 300, 1800]
reports = [benchmark(size=n, repeats=5) for n in sizes]
fig, ax = plt.subplots(figsize=(6.3, 3.8))
for key, label in [("list_scan", "List membership baseline"), ("set_index", "Set index incl. validation")]:
    ax.plot(sizes, [r["median_seconds"][key] * 1000 for r in reports], marker="o", label=label)
ax.set(xlabel="Distinct labels (input contains each twice)", ylabel="Median milliseconds per complete call", yscale="log")
ax.set_title("Observed local deduplication timing; setup excluded")
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig("chart.png", dpi=110)
print("Every result equal:", all(r["equal_results"] for r in reports))
print("Largest-fixture observed ratio:", round(reports[-1]["observed_ratio"], 2))''',
  'Calculate the ideal whole-program benefit when 20% becomes ten times faster.',
  r'''fraction, local_ratio = 0.2, 10
overall = 1 / ((1 - fraction) + fraction / local_ratio)
print("Ideal whole-program ratio:", round(overall, 2))''',
  'Preserve a slower result instead of renaming it an improvement.',
  r'''baseline_seconds, candidate_seconds = 0.20, 0.25
ratio = baseline_seconds / candidate_seconds
print("Observed ratio:", ratio)
print("Decision:", "candidate faster" if ratio > 1 else "retain baseline or investigate")''',
  [('Should an optimization exercise always print 10x?', 'No, report the actual observation', 'Yes, it is the target', 'Only if a chart is present', 'A target is not a measurement.'),
   ('What constrains whole-program benefit?', 'The runtime fraction actually improved', 'The number of source files', 'Only the candidate microbenchmark', 'Unchanged work remains in total elapsed time.')],
  'A 10x microbenchmark proves the entire application is 10x faster.',
  'Measure the application boundary and account for the fraction improved.',
  'A result is credible when equal work, scope and limitations accompany it.',
  syntax='ratio = baseline_seconds / candidate_seconds',
  figure=('Local benchmark of equal ordered deduplication results', 'Five alternating samples per method and size; medians plotted on a logarithmic time axis. Actual authoring-machine observations, not guaranteed speedups.'))

L(1, '1. Count work before choosing a data structure',
  'Read Big-O as input-growth behavior and distinguish expected, worst-case and output costs.',
  [('Big-O', 'An upper-bound growth description under a stated cost model, not a time in seconds or a guarantee for small inputs.'),
   ('n, u and k', 'Name input size n, distinct values u and groups k separately; retained state and output can depend on different quantities.'),
   ('Expected versus worst-case', 'Hash-table lookup is usually constant average/expected work under ordinary hashing; collisions and large keys can change the cost.')],
  "An O(n²) loop can be perfectly adequate for five items and painful for fifty thousand. An O(n) algorithm can have overhead that loses on tiny inputs. Use growth analysis to identify scaling problems, then measure realistic sizes for the actual decision.\n\nFor distinct labels, the list baseline checks 0 + 1 + ... + (n-1) prior result items: n(n-1)/2 comparisons in a simplified model. Replacing that membership scan with a set changes expected lookup work, but retains an index. Python string hashing and comparisons also depend on string length, so the standard O(n) discussion assumes ordinary bounded-size labels.\n\nSome tasks cannot run faster than their output size: returning n prefix totals already requires n result entries. Distinguish auxiliary working memory from returned output. The diagram is a decision sequence, not a rule that one data structure always wins.",
  r'''for n in [10, 20, 40]:
    scan_comparisons = n * (n - 1) // 2
    indexed_checks = n
    print(n, "distinct inputs:", scan_comparisons, "prior-item comparisons;", indexed_checks, "indexed checks")''',
  'Compare a linear and quadratic operation model when input size doubles.',
  r'''n = 100
print("Linear multiplier:", (2*n) / n)
print("Quadratic multiplier:", (2*n)**2 / n**2)''',
  'Identify the unavoidable output cost of returning all prefix sums.',
  r'''from studyhub_records import running_totals
values = [1] * 12
result = running_totals(values)
print("Input entries:", len(values))
print("Required output entries:", len(result))''',
  [('Does O(n) guarantee the fastest function for every small input?', 'No', 'Always', 'Only on Windows', 'Growth class omits constants, workload shape and implementation details.'),
   ('Is a returned list of n totals O(1) output space?', 'No, the output occupies O(n)', 'Yes', 'Only if a generator was used as input', 'A one-pass input does not remove the required retained result.')],
  'Describe a hash-based algorithm as guaranteed worst-case O(n) without assumptions.',
  'State expected dictionary/set behavior, key costs and result size.',
  'Naming the cost model prevents a useful simplification from becoming a misleading absolute claim.',
  syntax='list membership: O(n) scan; hash membership: expected O(1); sorting: O(n log n) comparisons',
  diagram=('Choose by contract, growth and measurements', ['Define input, ordering and error behavior', 'Count repeated work and required output', 'Choose an index, sort, stream or simple scan', 'Verify equality across edge cases', 'Measure time and memory on relevant sizes'], 'A structure earns its place by satisfying the contract and improving relevant measured work.'))

L(1, '2. Rewrite stable deduplication with a set index',
  'Preserve first-occurrence order while replacing repeated output-list searches.',
  [('seen set', 'Auxiliary membership index. It answers whether a string was encountered; the separate list preserves output order.'),
   ('Hashability', 'Set/dict keys must have a stable hash and equality behavior. Our public API accepts strings, not arbitrary nested mutable values.'),
   ('Single-pass iterable', 'An input that can be consumed once. Do not repeatedly loop over a generator expecting it to rewind.')],
  "A set alone removes duplicates, but returning it changes type and does not express the required first-seen list order. Keep two jobs separate: the set answers membership; the list owns output order. Append only when a valid string is new.\n\nFor each input, validate its type, ask seen, then add to both structures when absent. This performs expected O(n) hash-table operations and retains O(u) auxiliary set entries plus the output list. For a single string argument, the iterable consists of its characters; callers wanting one whole label should pass [label].\n\nValidation is observable behavior. The original baseline is our oracle for valid strings, while the packaged function deliberately rejects mixed-type labels. Test valid equivalence separately from new validation. Avoid silently calling str(value): converting 1 to '1' would merge meanings that the caller may distinguish.",
  r'''from studyhub_records import unique_in_order
values = ["b", "a", "b", "A", ""]
print(unique_in_order(iter(values)))
print("Original input:", values)
try:
    unique_in_order(["Python", 1])
except TypeError as error:
    print(type(error).__name__, str(error))''',
  'Write the indexing pattern yourself for valid string inputs.',
  r'''def deduplicate(values):
    seen, result = set(), []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result
print(deduplicate(["SQL", "Python", "SQL", "SQL"]))''',
  'Demonstrate why a list containing one label differs from passing a bare string.',
  r'''from studyhub_records import unique_in_order
print("One label:", unique_in_order(["banana"]))
print("Character iterable:", unique_in_order("banana"))''',
  [('Which structure preserves the required output order here?', 'The result list', 'A sorted replacement', 'A numeric counter', 'The set is only the membership index.'),
   ('Should non-string values be silently stringified?', 'No, follow the documented validation contract', 'Always', 'Only inside generators', 'Silent conversion can merge distinct caller meanings.')],
  'return list(set(values)) for a first-seen ordered-list API.',
  'Use a membership set plus an append-only ordered result list.',
  'The data structure improves membership work while the public answer stays explicit.',
  syntax='if value not in seen:\n    seen.add(value)\n    result.append(value)')

L(1, '3. Aggregate each category in one pass',
  'Replace a scan per category with a dictionary accumulator and preserve validation.',
  [('Accumulator dictionary', 'A mapping whose value grows as each input record is visited.'),
   ('dict.get(key, default)', 'Read the prior total, or zero when the category is new, without a separate membership branch.'),
   ('First-insertion ordering', 'Python dictionaries retain insertion order. Updating an existing key does not move it to the end.')],
  "A slow report first collects all categories, then scans every row again for each one. When almost every row has its own category, that repeated work approaches quadratic growth. A dictionary lets each row update only its own total.\n\nOur API consumes (category, minutes) tuples once. It rejects blank labels, negative minutes, floats and bool. Boolean rejection is deliberate: isinstance(True, int) is true, but a yes/no flag should not quietly become one minute. Nonblank surrounding whitespace is preserved; normalization would be a separate stated feature.\n\nKeep validation when comparing implementations. A benchmark that removes checks from the candidate changes what the caller receives for bad inputs. Tests should check total values, category order, empty input, generator consumption and that caller-owned rows remain unchanged.",
  r'''from studyhub_records import totals_by_category
rows = [("Python", 20), ("SQL", 10), ("Python", 5), ("SQL", 0)]
totals = totals_by_category(iter(rows))
print(totals)
print("First-category order:", list(totals))
try:
    totals_by_category([("Python", True)])
except TypeError as error:
    print(type(error).__name__)''',
  'Implement the accumulation step for already-valid records.',
  r'''rows = [("read", 5), ("code", 20), ("read", 10)]
totals = {}
for category, minutes in rows:
    totals[category] = totals.get(category, 0) + minutes
print(totals)''',
  'Check that an empty group input returns an empty mapping and invalid minutes fail.',
  r'''from studyhub_records import totals_by_category
print(totals_by_category([]))
for bad in [-1, 2.5, True]:
    try:
        totals_by_category([("practice", bad)])
    except (TypeError, ValueError) as error:
        print(repr(bad), type(error).__name__)''',
  [('What removes the repeated per-category scans?', 'Updating one dictionary total per row', 'Sorting category names after every row', 'Adding a thread per row', 'The accumulator performs the relevant update once.'),
   ('Why reject True as minutes explicitly?', 'bool subclasses int but has a different domain meaning', 'True is a float', 'Dictionaries cannot store booleans', 'Domain validation is stricter than Python type inheritance alone.')],
  'Find each category, then scan all input rows again to calculate its total.',
  'Validate each record and add its minutes to totals.get(category, 0).',
  'One pass improves expected work while the documented ordering and error behavior remain visible.',
  syntax='totals[category] = totals.get(category, 0) + minutes')

L(1, '4. Replace repeated prefix sums with a running total',
  'Remove quadratic re-summing and avoid hidden slice copies.',
  [('Prefix sum', 'The sum from the beginning through a particular position. A result with n inputs has n prefix totals.'),
   ('Repeated slicing cost', 'values[:i] creates a new slice for a list. Repeating it inside a loop can add copying as well as arithmetic.'),
   ('Auxiliary state', 'Working data beyond the required output. A running numeric total is constant auxiliary state under a bounded-integer cost model.')],
  "The expression [sum(values[:i+1]) for i in range(len(values))] looks compact. It re-adds earlier numbers over and over and copies growing list slices. For n items, the total number of values revisited grows like 1 + 2 + ... + n.\n\nCarry forward what you already know. After consuming one value, update total and append that new total. The packaged function accepts a generator, validates nonnegative integer minutes and produces the same prefix list for valid input. Zero still deserves an output entry: a zero-minute day is not a missing day.\n\nThe algorithm uses n additions and one running accumulator; its output still has n integers. For unusually large integers, addition cost depends on bit length, so describe O(n) as an operation-count model rather than a universal machine-time guarantee. The optimized function does not rewind a generator if a later invalid item raises.",
  r'''from studyhub_records import running_totals
values = [10, 0, 5, 20]
reference = [sum(values[:i+1]) for i in range(len(values))]
actual = running_totals(iter(values))
print(actual)
print("Same required answer:", actual == reference)
print("Empty:", running_totals([]))''',
  'Write an explicit running accumulator for [3, 2, 0, 4].',
  r'''total, result = 0, []
for minutes in [3, 2, 0, 4]:
    total += minutes
    result.append(total)
print(result)''',
  'Count the arithmetic visits in the repeated-sum model and the single-pass model.',
  r'''n = 1000
print("Repeated prefix visits:", n * (n + 1) // 2)
print("Running additions:", n)''',
  [('Does a short list comprehension guarantee linear work?', 'No, inspect the operations inside it', 'Always', 'Only if it calls sum', 'Repeated slicing and summing can hide quadratic work.'),
   ('Should a zero value be omitted from prefix output?', 'No', 'Always', 'Only at the start', 'There must be one cumulative total for each input position.')],
  'Recompute every earlier sum for each new position.',
  'Carry a total forward and append it exactly once per input.',
  'The optimized operation reuses previous work instead of repeating it.',
  syntax='total += value\nresult.append(total)')

L(1, '5. Use sorting when ordered structure matches the problem',
  'Improve a duplicate-existence check from pair comparisons to sort-and-scan without changing its boolean result.',
  [('O(n log n)', 'A common comparison-sorting growth bound; it can improve quadratic pairwise checks while using a different time/memory tradeoff from hashing.'),
   ('Adjacent-equal scan', 'After sorting, any duplicate values must appear next to one another.'),
   ('bisect_left', 'Find an insertion boundary in a sorted sequence in logarithmic comparison count; inserting into a Python list still shifts items.')],
  "Not every optimization must use a set. When you need a sorted structure for other work, sorting once can make later comparisons or binary searches useful. For a function returning only 'any duplicate?', changing internal order is allowed if the caller's original list is not mutated.\n\nThe reference compares each pair: O(n²) comparisons. The replacement sorts a copy and scans neighbors: O(n log n) comparisons overall, with extra memory for the copy. That meets the curriculum's quadratic-to-n-log-n exercise. It is different from stable deduplication, whose output order must be preserved.\n\nBinary search is another tool for sorted data. bisect_left finds a possible location; you must still check the boundary and equality to determine existence. O(log n) search does not make list insertion O(log n), because moving later entries can cost O(n). Include the sort/preparation cost when the use case performs only one query.",
  r'''from bisect import bisect_left
values = [5, 2, 9, 2]
ordered = sorted(values)
has_duplicate = any(a == b for a, b in zip(ordered, ordered[1:]))
print("Duplicate:", has_duplicate)
print("Original:", values)
position = bisect_left(ordered, 5)
print("Found five:", position < len(ordered) and ordered[position] == 5)''',
  'Compare pairwise and sort-and-scan duplicate detection on three fixtures.',
  r'''def pairwise(values):
    return any(values[i] == values[j] for i in range(len(values)) for j in range(i+1, len(values)))
def sorted_check(values):
    ordered = sorted(values)
    return any(a == b for a, b in zip(ordered, ordered[1:]))
for values in [[], [3, 1, 2], [3, 1, 3]]:
    print(pairwise(values), sorted_check(values))''',
  'Search for a missing large value without indexing past the end.',
  r'''from bisect import bisect_left
ordered = [10, 20, 30]
position = bisect_left(ordered, 99)
found = position < len(ordered) and ordered[position] == 99
print("Position:", position, "found:", found)''',
  [('Why is sorting a copy allowed for the boolean duplicate check?', 'The public output is a boolean and the original input stays unchanged', 'Sorting never changes order', 'All APIs ignore order', 'Internal changes are valid when the observable contract is preserved.'),
   ('Is insertion into a Python list O(log n) because bisect found its position?', 'No, shifting list items can be O(n)', 'Yes', 'Only for strings', 'Search and insertion are different operations.')],
  'Use bisect on unsorted data or index its returned end boundary directly.',
  'Prepare sorted data, check bounds, then check equality.',
  'Match the algorithm to the complete operation and its input assumptions.',
  syntax='position = bisect_left(ordered, value)\nfound = position < len(ordered) and ordered[position] == value')

L(1, '6. Prove the three rewrites preserve behavior',
  'Use edge cases and exhaustive small valid inputs before relying on performance results.',
  [('Differential test', 'Run a simple trusted reference and a candidate on the same inputs, then compare their required results.'),
   ('itertools.product', 'Generate all small combinations from a declared alphabet; this is exhaustive only over that bounded test space.'),
   ('Regression case', 'A focused example that would fail if a previously fixed behavior returned.')],
  "Our three rewrites cover stable deduplication, grouping and prefix sums. Each removes repeated work, but a wrong result can still be very fast. Retain a simple valid-input reference and add explicit tests for errors and input ownership.\n\nExhaustively checking every list of length zero through four over two small labels is inexpensive and catches many ordering mistakes. It does not prove every Unicode string, object implementation or large input. State that bound and supplement it with targeted cases: mixed case, empty strings, invalid minutes, generators and large integers.\n\nThe supplied project tests run these checks and exercise CSV failure behavior. An invalid report input must leave an older output intact, and a failure during replacement must clean its temporary file. These tests establish behavior, while the benchmark records observations separately. A busy machine should not turn a correct implementation into a failed correctness test merely because it missed an arbitrary 10x threshold.",
  r'''from itertools import product
from bench import slow_unique
from studyhub_records import unique_in_order, totals_by_category, running_totals
checked = 0
for length in range(5):
    for values in product(["a", "b"], repeat=length):
        assert unique_in_order(iter(values)) == slow_unique(values)
        checked += 1
print("Bounded differential cases:", checked)
print(totals_by_category([("a", 2), ("b", 3), ("a", 4)]))
print(running_totals([2, 3, 4]))''',
  'Test the group contract without silently normalizing distinct labels.',
  r'''from studyhub_records import totals_by_category
result = totals_by_category([("Python", 5), (" Python ", 7), ("Python", 1)])
print(result)
assert len(result) == 2''',
  'Show that an input generator is consumed when an error occurs partway through.',
  r'''from studyhub_records import running_totals
values = iter([1, -2, 3])
try:
    running_totals(values)
except ValueError:
    print("Rejected invalid input")
print("Generator still contains:", list(values))''',
  [('Do exhaustive length-four tests prove all possible inputs?', 'No, only the stated bounded input space', 'Yes', 'Only if pytest runs them', 'Small exhaustive tests are strong local evidence with explicit limits.'),
   ('Should correctness tests demand a fixed speed ratio?', 'Usually keep timing evidence separate', 'Always demand 10x', 'Only when tests run on GitHub', 'Noisy timing is not the same property as deterministic functional correctness.')],
  'Delete reference and edge-case tests after one promising timing run.',
  'Keep behavior tests; record separate, scoped performance observations.',
  'The package earns its optimization claim by preserving behavior and exposing measurement assumptions.',
  syntax='assert candidate(valid_input) == reference(valid_input)',
  shell='python -m pytest -q\npython bench.py --output artifacts/benchmark.json')
