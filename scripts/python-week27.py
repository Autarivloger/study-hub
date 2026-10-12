"""Author Week 27 additively; execute each output in an isolated practice folder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
DAYS = {f"27.{d}": {"parts": []} for d in range(6)}
EXECUTED = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global EXECUTED
    with tempfile.TemporaryDirectory(prefix="studyhub-w27-") as folder:
        run = subprocess.run([sys.executable, "-c", clean(code)], cwd=folder,
                             capture_output=True, encoding="utf-8", timeout=35,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    EXECUTED += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def s(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def add(day, title, goal, concepts, explanation, syntax, code, walk, mistake,
        task, solution, challenge, challenge_code, key, quizzes):
    parts = DAYS[f"27.{day}"]["parts"]
    index = len(parts)
    questions = []
    for n, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        rotation = (index + n) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(rotation):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": rotation, "why": why})
    parts.append({"title": title, "sections": [
        s("h", title), s("key", "Learning objective: " + goal),
        *[s("new", name, note=note) for name, note in concepts],
        s("p", explanation), s("syn", syntax, note="Pattern first; run the complete example below."),
        s("code", clean(code)), s("out", output(code)), s("p", walk),
        s("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        s("ex", task, practiceId=f"27.{day}.{index}.build"),
        s("sol", code=clean(solution), out=output(solution), why="Build check: " + key),
        s("ex", "Mini challenge: " + challenge, practiceId=f"27.{day}.{index}.challenge"),
        s("sol", code=clean(challenge_code), out=output(challenge_code), why="Challenge check: " + key),
        s("try", q=quizzes[0][0], code="# Predict and explain before revealing.",
          a=quizzes[0][1], why=quizzes[0][4]),
        s("checkpoint", lesson={"id": f"course:27.{day}.{index}", "quiz": questions}), s("key", key),
    ]})

add(0, "1. Lists and arrays solve different problems",
    "Create a numerical array and distinguish list repetition from element-wise arithmetic.",
    [("NumPy; import numpy as np", "NumPy is an installed numerical-computing library. np is the conventional alias, not a Python keyword."),
     ("ndarray; np.array; homogeneous dtype", "An ndarray stores an N-dimensional array with a common dtype. np.array constructs one from supplied data; a Python list remains a general-purpose container."),
     ("tolist", "tolist converts array data to nested ordinary Python lists/scalars. We use it to make lesson output easy to read; conversion is not needed for numerical computation.")],
    "Week 26 automated jobs; Week 27 starts numerical work. Python lists are excellent for general collections, but multiplying a list by 2 repeats it. "
    "Multiplying a numerical array by 2 applies arithmetic to each element. That change in meaning is the first thing to understand, not just memorize. "
    "Use Python 3.11+ and NumPy 2.x in a practice environment; installation initially needs internet, while this course and its supplied examples work offline afterward. "
    "Arrays are not always a better replacement for lists. Choose them for structured numerical data and operations that benefit from array semantics.",
    'import numpy as np\nvalues = np.array([10, 20, 30], dtype=np.int64)\nresult = values * 2',
    '''
    import numpy as np
    values = [10, 20, 30]
    array = np.array(values, dtype=np.int64)
    print("List:", values * 2)
    print("Array:", (array * 2).tolist())
    print("Original:", array.tolist())
    ''',
    "List दोहोरियो, array का प्रत्येक संख्या double भए। array * 2 ले नयाँ result बनायो; original array बदलिएको छैन। "
    "np Python keyword होइन, import को छोटो नाम हो।",
    ('[10, 20, 30] * 2  # assume numeric doubling', 'np.array([10, 20, 30], dtype=np.int64) * 2',
     "List multiplication repeats the sequence; numerical ndarray multiplication is element-wise."),
    "Convert [5,10,15] to an array and add 3 to every entry.",
    '''
    import numpy as np
    values = np.array([5, 10, 15], dtype=np.int64)
    print((values + 3).tolist())
    ''',
    "Show that two array references differ from a newly computed result.",
    '''
    import numpy as np
    a = np.array([1, 2], dtype=np.int64)
    same = a
    result = a + 1
    print(same is a, result is a)
    print(a.tolist(), result.tolist())
    ''',
    "Choose the right container. A numerical array changes arithmetic semantics; aliasing and mutation still matter.",
    [("What does [1,2] * 2 do?", "Repeats the list", "Doubles each number", "Changes its dtype", "List multiplication repeats the sequence."),
     ("Is np a Python keyword?", "No", "Yes", "Only after pip install", "It is an import alias chosen by convention.")])

add(0, "2. Shape, dimensions, size and axes",
    "Read a numerical table's shape before indexing or reducing it.",
    [("shape; ndim; size", "shape is a tuple of axis lengths, ndim is the number of axes and size is the total number of elements. len(array) describes its first axis, not its total size."),
     ("Axis and semantic meaning", "An axis is a dimension in the array. For our score tables axis 0 indexes students and axis 1 indexes assignments; NumPy itself does not know those names."),
     ("Rectangular numeric data", "A normal two-dimensional numeric array needs consistent row lengths. Ragged nested lists do not become a sensible rectangular score table automatically.")],
    "A 3-by-2 score table means three students and two assignments only because we define those meanings. "
    "Read shape=(3,2) from left to right: axis 0 length 3, axis 1 length 2. It contains six numbers and has two dimensions. "
    "A shape of (6,) means one axis, not six rows and one column. (6,1) is a different two-dimensional arrangement. "
    "Check shape at boundaries, especially when reading a single CSV row or column. Do not infer semantics from element count alone.",
    'scores.shape -> (students, assignments)\nscores.ndim -> number of axes\nscores.size -> total entries',
    '''
    import numpy as np
    scores = np.array([[60, 70], [80, 90], [40, 50]], dtype=np.int64)
    print("Shape:", scores.shape)
    print("Dimensions:", scores.ndim)
    print("Elements:", scores.size)
    print("len:", len(scores))
    ''',
    "तीन students × दुई assignments = छ elements। len(scores) चाहिँ first axis को length 3 हो। "
    "Axis लाई student/assignment भन्ने अर्थ हामीले दिएका हौँ; NumPy ले नाम आफैँ थाहा पाउँदैन।",
    ('len(scores)  # assume total cell count', 'scores.size  # total elements; read shape for each axis length',
     "len returns the first dimension for a non-scalar array."),
    "Inspect the difference between shape (3,) and shape (3,1).",
    '''
    import numpy as np
    flat = np.array([1, 2, 3], dtype=np.int64)
    column = np.array([[1], [2], [3]], dtype=np.int64)
    print(flat.shape, flat.ndim)
    print(column.shape, column.ndim)
    ''',
    "Reject ragged numeric rows instead of constructing a misleading table.",
    '''
    import numpy as np
    try:
        np.array([[1, 2], [3]], dtype=np.float64)
    except ValueError:
        print("Reject ragged rows")
    ''',
    "Write down axis meaning and inspect shape/ndim/size. One-dimensional and two-dimensional shapes are not interchangeable.",
    [("What is size for shape (3,2)?", "6", "3", "2", "Total elements are the product of the axis lengths."),
     ("Does NumPy know axis 0 represents students?", "No", "Yes", "Only for floats", "Meaning comes from your data contract.")])

add(0, "3. Vectorization: express the operation on a whole array",
    "Replace a simple Python loop with an equivalent numerical array operation.",
    [("Vectorization", "Express a bulk operation through NumPy array functions/operators so their compiled implementations process the data. It does not mean computation performs no loops internally."),
     ("Element-wise comparison", "A comparison such as scores >= 60 returns a Boolean array with the same compatible shape, not one overall truth value."),
     ("np.array_equal", "array_equal compares entire arrays for exact element/shape equality. Approximate floating-point comparisons use a different policy later.")],
    "Start by writing the rule for one value: adjusted = score + 5. The array expression scores + 5 applies that rule throughout. "
    "To validate a rewrite, compare its result with the original loop on a small known input before measuring performance. "
    "Vectorization improves clarity when the rule naturally applies to arrays. It can also allocate temporary arrays, so understand memory and dtype. "
    "np.vectorize is not the compiled-speed transformation implied by its name; do not use it as a shortcut for understanding array operations.",
    'adjusted = scores + 5\npasses = adjusted >= 60\n# Validate a numerical rewrite against known results',
    '''
    import numpy as np
    values = [40, 55, 80]
    loop_result = [value + 5 for value in values]
    array = np.array(values, dtype=np.int64)
    adjusted = array + 5
    print(adjusted.tolist())
    print((adjusted >= 60).tolist())
    print("Same result:", np.array_equal(adjusted, loop_result))
    ''',
    "प्रत्येक value मा +5 लागू भयो। >=60 को result Boolean array हो। "
    "Small input मा loop र array result मिलेपछि मात्र numerical rewrite सही छ भन्ने आधार मिल्छ।",
    ('np.vectorize(my_python_function)  # assume compiled numerical speed', 'Use actual array operations where their semantics fit',
     "np.vectorize generally provides convenience around Python calls rather than the performance of a compiled ufunc."),
    "Calculate price times quantity element-wise for three records.",
    '''
    import numpy as np
    prices = np.array([10, 20, 30], dtype=np.int64)
    quantities = np.array([2, 1, 3], dtype=np.int64)
    print((prices * quantities).tolist())
    ''',
    "Verify a square-and-add operation against known expected values.",
    '''
    import numpy as np
    values = np.array([1, 2, 3], dtype=np.int64)
    result = values ** 2 + 1
    print(result.tolist())
    print(np.array_equal(result, [2, 5, 10]))
    ''',
    "Express the rule clearly and verify equivalence. Vectorized array computation still performs work and can allocate memory; its speed is not a universal guarantee.",
    [("Does vectorization mean no loops run inside NumPy?", "No", "Yes", "Only for comparisons", "Compiled implementations still iterate over data."),
     ("What does scores >= 60 return?", "A Boolean array", "Always one bool", "An SMTP message", "The comparison applies element-wise.")])

add(0, "4. Measure fairly: timing and numeric buffer memory",
    "Benchmark equivalent work without promising a machine-independent speed ratio.",
    [("timeit; setup versus measured work", "timeit measures repeated execution. Keep data preparation consistently outside or inside both measurements and compare equivalent operations."),
     ("itemsize; nbytes", "itemsize is bytes per array element; nbytes is the numeric element-buffer size. It excludes some object overhead and is not a complete process-memory measurement."),
     ("Benchmark limits", "Hardware, dtype, input size, allocations and library version affect timing. A tiny scalar task can favour plain Python; do not publish invented speed ratios.")],
    "The curriculum asks you to compare a million values. The example creates equivalent input for a list comprehension and a NumPy operation, checks correctness, then times each three times. "
    "Timing values are deliberately not frozen into expected output; they vary by computer. In your own practice inspect list_seconds/array_seconds and repeat the experiment. "
    "The example's array uses int64, eight bytes per element, so its element buffer is eight million bytes. That is not the total memory used by Python and the list together. "
    "Do not include conversion in one benchmark while excluding setup from the other unless conversion is part of the real workload being compared.",
    'prepare equivalent data\nassert equal results\nlist_seconds = timeit.timeit(list_work, number=3)\narray_seconds = timeit.timeit(array_work, number=3)',
    '''
    import numpy as np
    import timeit
    values = list(range(1_000_000))
    array = np.array(values, dtype=np.int64)
    assert np.array_equal([value * 2 for value in values], array * 2)
    list_seconds = timeit.timeit(lambda: [value * 2 for value in values], number=3)
    array_seconds = timeit.timeit(lambda: array * 2, number=3)
    print("Values:", array.size)
    print("Buffer bytes:", array.nbytes)
    print("Measured both:", list_seconds >= 0 and array_seconds >= 0)
    ''',
    "दुवैमा समान doubling काम छ। Timing मापन भयो तर exact seconds output मा fixed छैन। "
    "Practice गर्दा variables हेरेर आफ्नै measurement लेख। nbytes numeric buffer मात्र हो, total process memory होइन।",
    ('Claim NumPy is always exactly 100 times faster', 'Measure equivalent representative workloads and report environment/variability',
     "Performance depends on workload and environment; no universal ratio follows from the library name."),
    "Inspect how int32 versus int64 changes buffer bytes for four values.",
    '''
    import numpy as np
    small = np.array([1, 2, 3, 4], dtype=np.int32)
    wide = small.astype(np.int64)
    print(small.itemsize, small.nbytes)
    print(wide.itemsize, wide.nbytes)
    ''',
    "Check that creating a new calculation result needs a separate array buffer.",
    '''
    import numpy as np
    values = np.arange(5, dtype=np.int64)
    result = values * 2
    print("Shared data:", np.shares_memory(values, result))
    print(result.nbytes)
    ''',
    "Verify correctness before speed. Keep timing setup fair, inspect memory scope honestly and report measurements rather than fixed performance promises.",
    [("Does nbytes include the whole Python process?", "No", "Yes", "Only on Windows", "It describes the array's element buffer."),
     ("Should a published speed ratio be assumed universal?", "No", "Yes", "Only for a million entries", "Measurements depend on environment/workload.")])

add(1, "1. Create arrays deliberately: zeros, ones, full and empty",
    "Choose a construction method that expresses the intended initial values.",
    [("zeros; ones; full", "These construct arrays with specified shape and filled values. Specify dtype when its range/precision matters."),
     ("empty", "empty allocates an array without initializing its elements to a chosen value. Read it only after assigning every element; it is not a zero-filled array."),
     ("astype", "astype converts values into a requested dtype and normally returns a new array. Conversion may truncate/overflow; conversion is not domain validation.")],
    "Use zeros for an initialized count table, ones for known unit values and full for another constant. "
    "Passing shape=(2,3) creates two rows and three columns; passing 3 creates one axis of length three. "
    "empty is useful only when you will fill the entire buffer before using it. Uninitialized values are not deterministic data or valid examples. "
    "For score calculations float64 is often a practical default. An integer dtype is appropriate for exact bounded counts, not automatic conversion of arbitrary decimal scores.",
    'np.zeros((2,3), dtype=np.int64)\nnp.full((2,2), 7, dtype=np.int64)\nraw = np.empty(3); raw[:] = known_values',
    '''
    import numpy as np
    print(np.zeros((2, 3), dtype=np.int64).tolist())
    print(np.ones(3, dtype=np.float64).tolist())
    print(np.full((2, 2), 7, dtype=np.int64).tolist())
    raw = np.empty(3, dtype=np.float64)
    raw[:] = [1.0, 2.0, 3.0]
    print(raw.tolist())
    ''',
    "empty को values पढ्नुअघि सबै elements assign गरिएका छन्। zeros/ones/full को shape र dtype स्पष्ट छन्। "
    "Uninitialized memory लाई sample data मानेर पढ्नु हुँदैन।",
    ('np.empty(3)  # expect zeros', 'np.zeros(3)  # use empty only if every element is filled first',
     "empty does not promise any specific initial value."),
    "Create a 2×2 float table filled with 2.5.",
    '''
    import numpy as np
    values = np.full((2, 2), 2.5, dtype=np.float64)
    print(values.tolist(), values.shape)
    ''',
    "Convert an integer array to float without changing the original dtype.",
    '''
    import numpy as np
    original = np.array([1, 2], dtype=np.int64)
    converted = original.astype(np.float64)
    print(original.dtype, converted.dtype)
    print(converted.tolist())
    ''',
    "Specify shape/initial values/dtype. Never read empty before filling it; treat numeric conversion and validation as separate decisions.",
    [("Does empty guarantee zeros?", "No", "Yes", "Only for floats", "It does not initialize the buffer to a chosen value."),
     ("Which constructor expresses one repeated value?", "full", "argmax", "std", "full fills the specified shape with a chosen value.")])

add(1, "2. Ranges: arange versus linspace",
    "Choose a step-based sequence or a sample-count-based interval.",
    [("arange", "arange produces values using a start/stop/step contract with stop normally excluded. Floating-point steps can accumulate representation problems."),
     ("linspace; endpoint", "linspace chooses a number of evenly spaced samples; by default it includes both interval endpoints. endpoint=False changes that contract."),
     ("Floating-point representation", "Many decimal fractions are approximate in binary. Do not count exact decimal steps by equality when a sample-count contract would express your intent better.")],
    "For integer positions, arange is natural: start at 2, stop before 10, step by 2. "
    "For five samples from 0 through 1 inclusive, linspace expresses the count and endpoints directly. "
    "The two functions answer different questions. Do not translate 'five evenly spaced values' into an invented float step and hope its last value behaves exactly. "
    "Use shapes and tolerant comparisons for numerical results where appropriate; keep exact integer indexes as integers.",
    'np.arange(start, stop, step)\nnp.linspace(start, stop, num=count, endpoint=True)',
    '''
    import numpy as np
    print(np.arange(2, 10, 2, dtype=np.int64).tolist())
    print(np.linspace(0, 1, num=5).tolist())
    print(np.linspace(0, 1, num=4, endpoint=False).tolist())
    ''',
    "arange मा 10 समावेश छैन। linspace को default endpoint=True हुँदा 0 र1 दुवै छन्। "
    "Count चाहिएको हो कि step चाहिएको हो भन्ने पहिले छुट्याऊ।",
    ('Use a float arange step to guarantee exactly five samples', 'Use linspace(..., num=5) for a fixed sample count',
     "Floating-step construction is not a robust fixed-count/endpoints contract."),
    "Generate integer positions 0 through 4 and three samples from 10 to 20.",
    '''
    import numpy as np
    print(np.arange(5, dtype=np.int64).tolist())
    print(np.linspace(10, 20, num=3).tolist())
    ''',
    "Verify endpoint=False leaves the final endpoint outside the returned samples.",
    '''
    import numpy as np
    values = np.linspace(0, 8, num=4, endpoint=False)
    print(values.tolist(), values.size)
    ''',
    "arange expresses steps and an excluded stop; linspace expresses count and endpoint policy. Choose from the intended sequence.",
    [("Does arange(2,10,2) normally include 10?", "No", "Yes", "Only for int64", "The stop is excluded."),
     ("Which is clearer for five samples including 0 and 1?", "linspace(0,1,num=5)", "A guessed float step", "empty(5)", "linspace directly specifies sample count and endpoints.")])

add(1, "3. Reproducible randomness with a local Generator",
    "Generate classroom samples without depending on hidden global random state.",
    [("default_rng; Generator", "default_rng creates a local random Generator. A seed allows controlled experiments without mutating an unrelated global generator."),
     ("integers; high excluded; size", "integers(low,high,size) samples integers with high excluded by default. size specifies the returned shape."),
     ("Reproducibility limits", "A seed controls a particular generator/algorithm/version and call sequence; do not promise identical output from every future NumPy release or call order.")],
    "Random examples should not change expected output on every run. Create a local generator and show reproducibility by constructing another one with the same seed and same calls. "
    "This is simulation data, not a secure token generator. The course does not use random student records as real evidence. "
    "integers(0,10) can return 0 through9. A size of (2,3) creates a 2×3 sample. "
    "Repeated calls advance the generator state. Store seed, algorithm/version and call procedure when an experiment needs reproducibility.",
    'rng = np.random.default_rng(seed)\nvalues = rng.integers(low, high, size=(rows,columns))',
    '''
    import numpy as np
    a = np.random.default_rng(7).integers(0, 10, size=(2, 3))
    b = np.random.default_rng(7).integers(0, 10, size=(2, 3))
    print("Same procedure:", np.array_equal(a, b))
    print("Shape:", a.shape)
    print("Bounds:", bool(((a >= 0) & (a < 10)).all()))
    ''',
    "दुई generator मा same seed/calls भएकाले यस environment मा result मिल्यो। Shape(2,3) र0–9 bounds जाँचिए। "
    "Exact randomnumbersलाई सबै futureversionsकोguarantee मानेका छैनौँ।",
    ('Seed once and assume every later call returns the same sample', 'Use a local Generator and record the call sequence/environment',
     "Each call advances its state; reproducibility needs more than one seed number."),
    "Generate five integers in [1,7) and verify the upper endpoint is excluded.",
    '''
    import numpy as np
    values = np.random.default_rng(9).integers(1, 7, size=5)
    print(values.shape, bool(((values >= 1) & (values < 7)).all()))
    ''',
    "Show that same seed but different requested shapes describes a different experiment.",
    '''
    import numpy as np
    a = np.random.default_rng(2).integers(0, 10, size=3)
    b = np.random.default_rng(2).integers(0, 10, size=(1, 3))
    print(a.shape, b.shape)
    print("Shape-aware equality:", np.array_equal(a, b))
    ''',
    "Use local seeded generators for controlled examples, verify shape/range and record procedure. Numerical RNG is not a security token source.",
    [("Is integers' high endpoint included by default?", "No", "Yes", "Only for seeded calls", "The default interval excludes high."),
     ("Does a seed guarantee every future NumPy version and call sequence matches?", "No", "Yes", "Only for arrays", "Algorithm/version/procedure also matter.")])

add(1, "4. Dtype, fixed-width overflow and lossy casts",
    "Choose numeric range/precision intentionally and validate before conversion.",
    [("int8/int64; float32/float64", "These are fixed-width numerical types. Integers have bounded ranges; floats have finite precision. Python's ordinary integers do not share the same fixed-width limit."),
     ("iinfo; finfo", "iinfo reports integer type bounds; finfo describes floating-point limits. Use them to reason about acceptable values."),
     ("Casting and truncation", "Casting float data to integer truncates fractional values. Narrowing integer casts can overflow; dtype conversion is not validation.")],
    "A smaller dtype saves buffer memory but changes what values can be represented. int8 holds -128 through127; adding two arrays containing120 does not magically become unbounded Python arithmetic. "
    "Choose a wider type before arithmetic if its expected range requires it. For decimal score inputs, keep a floating dtype instead of silently truncating them. "
    "Different versions can change scalar-promotion rules, so the example uses two explicitly int8 arrays rather than relying on a Python scalar being promoted. "
    "Floating precision is separate: converting float32 values to float64 later cannot recover information already rounded away.",
    'bounds = np.iinfo(np.int8)\nwide = narrow.astype(np.int64)\n# Validate range/integrality before lossy conversion',
    '''
    import numpy as np
    narrow = np.array([120], dtype=np.int8)
    print("int8 bounds:", np.iinfo(np.int8).min, np.iinfo(np.int8).max)
    print("Narrow sum:", (narrow + narrow).tolist())
    wide = narrow.astype(np.int64)
    print("Wide sum:", (wide + wide).tolist())
    print(np.array([1.9, -1.9]).astype(np.int64).tolist())
    ''',
    "int8 sum wrap भएर -16 आयो; पहिलेint64माconvert गर्दा240ठीकआयो। Float-to-int castले1.9लाई1बनायो, nearestroundहोइन। "
    "dtype छनोट range/precisionकोनिर्णयहो।",
    ('Cast decimals to int to validate them', 'Check the accepted numeric domain/integrality first; cast only under an explicit policy',
     "A cast can destroy invalid fractions or wrap a narrow integer instead of rejecting the input."),
    "Validate values fit int8 before choosing that type.",
    '''
    import numpy as np
    values = np.array([100, 200], dtype=np.int64)
    bounds = np.iinfo(np.int8)
    print(((values >= bounds.min) & (values <= bounds.max)).tolist())
    ''',
    "Compare the buffer sizes of two float precisions without claiming identical numerical accuracy.",
    '''
    import numpy as np
    a = np.ones(4, dtype=np.float32)
    b = np.ones(4, dtype=np.float64)
    print(a.nbytes, b.nbytes)
    print(np.finfo(np.float32).eps > np.finfo(np.float64).eps)
    ''',
    "Dtype is part of correctness, not just speed. Validate bounds/precision and widen before overflow-prone work; casts are not validation.",
    [("Does casting 1.9 to an integer validate that it was originally integral?", "No", "Yes", "Only with int64", "The fractional information is discarded."),
     ("Can a fixed-width array overflow?", "Yes", "No", "Only Python lists", "Fixed-width types have limited ranges.")])

add(2, "1. Indexing: scalar, row, column and slice",
    "Select the intended axis and predict the result shape.",
    [("array[row,column]", "Comma-separated indexes choose positions on different axes. indexes start at zero; negative indexes count from an axis's end."),
     ("Slice stop excluded; dimension dropping", "A scalar index normally removes its axis from the result. A slice such as 1:2 retains that axis with length one."),
     ("ellipsis", "The ... index represents any needed full-axis slices. For this week's 2-D table, values[...,0] selects its first column.")],
    "For shape (3,2), scores[1,0] is one number; scores[1] is a row of shape(2,), and scores[:,0] is a column represented as shape(3,). "
    "If you need a 2-D column for broadcasting, scores[:,0:1] has shape(3,1). The selected values can be similar while their shapes differ. "
    "Never guess from how an array prints: inspect shape. "
    "The first index chooses axis0 and the second axis1 in this example. Later higher-dimensional arrays retain the same axis-based idea.",
    'value = scores[row,column]\nrow = scores[row,:]\ncolumn = scores[:,column]\ncolumn_2d = scores[:,column:column+1]',
    '''
    import numpy as np
    scores = np.array([[10, 20], [30, 40], [50, 60]], dtype=np.int64)
    print("Scalar:", int(scores[1, 0]))
    print("Row:", scores[1].tolist(), scores[1].shape)
    print("Column:", scores[:, 0].tolist(), scores[:, 0].shape)
    print("2-D column:", scores[:, 0:1].tolist(), scores[:, 0:1].shape)
    ''',
    "Scalar indexलेaxis हटायो; sliceलेlength-oneaxisजोगायो। यहीफरकbroadcastingमामहत्त्वपूर्णहुन्छ। "
    "Columnकोshape(3,)र(3,1)एउटैहोइन।",
    ('scores[:,0]  # assume shape (3,1)', 'scores[:,0:1]  # retain a length-one column axis',
     "A scalar column index drops that axis, while a slice retains it."),
    "Read the last row and last column using negative indexes.",
    '''
    import numpy as np
    a = np.array([[1, 2], [3, 4]], dtype=np.int64)
    print(a[-1].tolist())
    print(a[:, -1].tolist())
    ''',
    "Select the first column with an ellipsis and verify its shape.",
    '''
    import numpy as np
    a = np.array([[1, 2], [3, 4]], dtype=np.int64)
    print(a[..., 0].tolist(), a[..., 0].shape)
    ''',
    "Predict the selected values and shape together. Scalar indexes drop axes; slices can preserve them.",
    [("What is the shape of a[:,0] for a shape (3,2)?", "(3,)", "(3,1)", "(2,3)", "The scalar column index drops axis1."),
     ("Which keeps a 2-D first-column result?", "a[:,0:1]", "a[:,0]", "a[0,0]", "A slice keeps the length-one axis.")])

add(2, "2. Basic slices are views; copy explicitly for independence",
    "Understand when editing a selected array can change its source.",
    [("View; shared data buffer", "A view has its own array metadata but references existing data. Basic slices usually produce views; modifying them can modify the source."),
     ("copy; shares_memory", "copy makes independent element storage. shares_memory tests whether arrays overlap in memory; identity is not the same as data independence."),
     ("Aliasing policy", "Document whether a function returns a view or an independent result. A new Python ndarray object may still share its underlying bytes.")],
    "Python list slicing makes a new list container. NumPy basic slicing usually makes a view instead. "
    "If selected = values[1:3], setting selected[0]=99 changes values[1]. The objects are not identical, yet their data overlaps. "
    "Use .copy() when a practice edit must not alter the original dataset. "
    "Avoid memorizing 'new variable means copy': assignment, views and copies have different ownership meanings. Advanced indexing in a later part normally returns copied selection data.",
    'view = original[1:3]\nindependent = original[1:3].copy()\nnp.shares_memory(original, view)',
    '''
    import numpy as np
    original = np.array([10, 20, 30, 40], dtype=np.int64)
    view = original[1:3]
    independent = original[1:3].copy()
    view[0] = 99
    independent[1] = 77
    print("Original:", original.tolist())
    print("Copy:", independent.tolist())
    print("Shared:", np.shares_memory(original, view), np.shares_memory(original, independent))
    ''',
    "Viewकोeditoriginalमापुग्यो; copyकोeditपुगेन। Pythonobjectअलगभएपनिunderlyingdata साझा हुनसक्छ। "
    "Originalजोगाउनस्पष्टcopyगर।",
    ('selected = values[1:3]; assume independent', 'selected = values[1:3].copy() when independent edits are needed',
     "Basic slicing normally shares storage."),
    "Edit an independent row copy without changing the table.",
    '''
    import numpy as np
    a = np.array([[1, 2], [3, 4]], dtype=np.int64)
    row = a[0].copy()
    row[0] = 50
    print(a.tolist(), row.tolist())
    ''',
    "Demonstrate that distinct ndarray identity does not imply distinct storage.",
    '''
    import numpy as np
    a = np.arange(4, dtype=np.int64)
    b = a[:]
    print(b is a, np.shares_memory(a, b))
    ''',
    "Know your ownership contract. Basic slices can share data; copy for independent mutations and do not equate identity with storage.",
    [("Can editing a basic slice change its original?", "Yes", "No", "Only for lists", "The slice normally references the same element buffer."),
     ("Does b is not a prove b has independent bytes?", "No", "Yes", "Only with int64", "Distinct array objects can share storage.")])

add(2, "3. Boolean masks, row filtering and deliberate assignment",
    "Build element-wise conditions and choose whether to select values or whole rows.",
    [("Boolean mask; & | ~", "A Boolean array can select corresponding elements/rows. Use parenthesized comparisons with &, | and ~ for element-wise Boolean combinations, not Python and/or."),
     ("any/all with axis", "any tests whether at least one Boolean is True; all requires every one. With axis=1 on a 2-D table they reduce each row to one decision."),
     ("Selection copy versus direct assignment", "a[mask] returns a copied selection for reading. a[mask]=value deliberately changes matching positions in the original array.")],
    "An element mask has the same shape as its score table and selecting with it produces a flat collection of matching values. "
    "For whole-row filtering, reduce a condition across assignments: (scores>=60).all(axis=1) says which students passed every assignment. "
    "Python 'and' tries to decide one overall truth of an array and is not the right operator here. Parentheses are required around each comparison when using &. "
    "State whether you intend a returned selection or a mutation. Both use similar brackets but have different effects.",
    'mask = (values >= low) & (values <= high)\nselected = values[mask]\nrow_mask = (scores >= 60).all(axis=1)\nrows = scores[row_mask]',
    '''
    import numpy as np
    scores = np.array([[60, 70], [40, 90], [80, 85]], dtype=np.int64)
    mask = (scores >= 60) & (scores <= 80)
    print("Matching cells:", scores[mask].tolist())
    row_mask = (scores >= 60).all(axis=1)
    print("Row decisions:", row_mask.tolist())
    print("Passing rows:", scores[row_mask].tolist())
    ''',
    "Cellmaskबाटmatchingcells आए। all(axis=1)लेहरेकstudentकाassignmentsमाथिconditioncombineगरेरrowdecisionबनायो। "
    "Whole rows चाहिएको हो भनेcellselectionसँगनझुक्किऊ।",
    ('(scores >= 60) and (scores <= 80)', '(scores >= 60) & (scores <= 80)',
     "Python and requires scalar truth; & combines Boolean arrays element-wise."),
    "Replace negative entries with zero using direct mask assignment.",
    '''
    import numpy as np
    values = np.array([-2, 4, -1, 7], dtype=np.int64)
    values[values < 0] = 0
    print(values.tolist())
    ''',
    "Edit a Boolean-selected copy and prove its source is unchanged.",
    '''
    import numpy as np
    values = np.array([10, 20, 30], dtype=np.int64)
    selected = values[values >= 20]
    selected[:] = 0
    print(values.tolist(), selected.tolist())
    print(np.shares_memory(values, selected))
    ''',
    "Separate cell masks from row masks. Use element-wise Boolean operators and distinguish reading a copied selection from assigning into the source.",
    [("Which combines two array comparisons element-wise?", "& with each comparison parenthesized", "Python and", "A string join", "Boolean array logic uses element-wise operators."),
     ("What does all(axis=1) do here?", "One decision per row", "One decision per column", "Always sorts rows", "It reduces the assignment axis for each student.")])

add(2, "4. Advanced indexing: selected pairs versus a rectangle",
    "Use integer index arrays intentionally and understand their copy behaviour.",
    [("Advanced integer indexing", "An integer index list/array selects particular positions. It normally returns a copy; assigning directly through indexes still changes the source."),
     ("Paired indexes", "a[[0,2],[0,1]] selects the coordinate pairs (0,0) and (2,1), not every combination of those rows/columns."),
     ("np.ix_", "ix_ constructs an index combination for the Cartesian rectangle of selected rows and columns. The result can differ from paired advanced indexing.")],
    "Want rows0 and2? Use a[[0,2]]. Want cells(0,0) and(2,1)? Supply paired row/column lists. "
    "Want the full subtable using rows0/2 and columns0/1? Use np.ix_ to combine them. "
    "The number of arrays and their shapes controls advanced-indexing semantics. Start with explicit small coordinates instead of guessing from a complicated expression. "
    "As with Boolean selection, editing a separately returned advanced selection does not normally edit the original; direct indexed assignment does.",
    'pairs = a[[0,2],[0,1]]\nrectangle = a[np.ix_([0,2],[0,1])]',
    '''
    import numpy as np
    a = np.array([[10, 11], [20, 21], [30, 31]], dtype=np.int64)
    pairs = a[[0, 2], [0, 1]]
    rectangle = a[np.ix_([0, 2], [0, 1])]
    print("Pairs:", pairs.tolist(), pairs.shape)
    print("Rectangle:", rectangle.tolist(), rectangle.shape)
    ''',
    "Pairsमा2cells छन्, rectangleमा2×2cells छन्। एउटै row/columnnumbers भएपनि indexingruleअलगछ। "
    "Coordinates कागजमा लेखेर कुनcellsछानियोtraceगर।",
    ('a[[0,2],[0,1]]  # assume a 2x2 table', 'a[np.ix_([0,2],[0,1])]  # all requested combinations',
     "Paired lists select coordinate pairs; ix_ constructs the rectangular combination."),
    "Select rows in reverse chosen order and verify they are copied.",
    '''
    import numpy as np
    a = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.int64)
    chosen = a[[2, 0]]
    print(chosen.tolist())
    print(np.shares_memory(a, chosen))
    ''',
    "Assign directly to two specified cells and inspect the source.",
    '''
    import numpy as np
    a = np.array([[1, 2], [3, 4]], dtype=np.int64)
    a[[0, 1], [1, 0]] = 99
    print(a.tolist())
    ''',
    "Know whether indexes specify pairs or combinations. Advanced reading selections are copies; direct indexed assignment intentionally mutates the source.",
    [("Does a[[0,2],[0,1]] return all four combinations?", "No", "Yes", "Only on Windows", "It selects paired coordinates."),
     ("Which helper makes the selected rectangular combination?", "np.ix_", "np.std", "np.empty", "ix_ builds broadcastable coordinate combinations.")])

add(3, "1. Element-wise operations, ufuncs and matrix multiplication",
    "Distinguish per-cell arithmetic from row/column multiplication.",
    [("Ufunc; sqrt; absolute", "A universal function performs an operation over compatible array inputs through compiled array logic. sqrt and absolute are common examples; each has a mathematical domain."),
     ("* versus @", "* multiplies compatible elements; @ performs matrix multiplication with its own shape rules. A two-dimensional ndarray is not automatically a special matrix type."),
     ("isclose; allclose", "These compare floating-point values using tolerances. Select tolerances appropriate to your scale rather than assuming binary decimals are always exact.")],
    "For two 2×2 arrays, * multiplies cells at corresponding positions. @ combines rows from the left operand with columns from the right. "
    "These can give entirely different numbers; choose from the mathematical job, not from which symbol happens to run. "
    "sqrt is defined for nonnegative real inputs in this lesson; do not silently accept negative scores then hide its warning. "
    "Floating arithmetic may need approximate checks. Exact identity, equal shape and close numeric values are different comparisons.",
    'cell_products = a * b\nmatrix_product = a @ b\nroots = np.sqrt(nonnegative_values)',
    '''
    import numpy as np
    a = np.array([[1, 2], [3, 4]], dtype=np.int64)
    b = np.array([[2, 0], [1, 2]], dtype=np.int64)
    print("Element-wise:", (a * b).tolist())
    print("Matrix:", (a @ b).tolist())
    print("Roots:", np.sqrt([0.0, 4.0, 9.0]).tolist())
    print("Decimal close:", bool(np.isclose(0.1 + 0.2, 0.3)))
    ''',
    "*कोresultकोहरेकcellअलगmultiplyभयो। @माrow/columnproductsकोsumछ। "
    "sqrtकोdomainपहिलेvalidateगर; decimalresultका लागि उचितtoleranceलेcompareगर।",
    ('a * b  # assume matrix multiplication', 'a @ b when the intended operation is matrix multiplication',
     "ndarray * is element-wise, while @ has matrix-product semantics."),
    "Apply absolute value and squares element-wise.",
    '''
    import numpy as np
    values = np.array([-3, -2, 4], dtype=np.int64)
    print(np.absolute(values).tolist())
    print((values ** 2).tolist())
    ''',
    "Reject negative real square-root inputs before computation.",
    '''
    import numpy as np
    values = np.array([4.0, -1.0])
    print("Real sqrt inputs valid:", bool((values >= 0).all()))
    ''',
    "Pick mathematical semantics deliberately. Ufuncs have domains; * and @ are different, and numeric comparisons need an explicit tolerance policy.",
    [("What does ndarray * do?", "Element-wise multiplication", "Always matrix multiplication", "Repeats rows like a list", "It applies multiplication to compatible element positions."),
     ("Which operator performs matrix multiplication?", "@", "*", "and", "@ uses matrix-product shape rules.")])

add(3, "2. Broadcasting: align shapes from the right",
    "Predict compatible shapes and apply column or row adjustments correctly.",
    [("Broadcast compatibility", "Compare dimensions from the right. Each aligned pair must be equal or one of them must be1. Missing leading dimensions behave as1."),
     ("np.newaxis", "newaxis inserts a length-one axis through indexing. An adjustment of shape(3,) becomes a column shape(3,1) with values[:,np.newaxis]."),
     ("Broadcasted computation versus duplication", "Broadcasting generally avoids explicitly materializing repeated input data, but the output and later operations can still require large allocations.")],
    "A score table of shape(3,2) can add a per-assignment vector of shape(2,): the trailing dimension2 matches. "
    "It cannot add a shape(3,) per-student vector directly because trailing dimensions2 and3 conflict. Insert a column axis to make that vector shape(3,1). "
    "The classroom rule is about shape, not meaning: a shape-compatible adjustment can still be semantically wrong if the axes were labelled incorrectly. "
    "Trace each requested output row before relying on a broadcasting expression.",
    'column_adjustment: scores + shape(assignments,)\nrow_adjustment: scores + row_values[:,np.newaxis]\ncompare trailing axes: equal or1',
    '''
    import numpy as np
    scores = np.array([[10, 20], [30, 40], [50, 60]], dtype=np.int64)
    by_assignment = np.array([1, 2], dtype=np.int64)
    by_student = np.array([1, 2, 3], dtype=np.int64)
    print((scores + by_assignment).tolist())
    print((scores + by_student[:, np.newaxis]).tolist())
    print("Student adjustment shape:", by_student[:, np.newaxis].shape)
    ''',
    "Assignmentvector(2,)हरेकrowमालाग्यो। Studentvectorलाई(3,1)बनाएपछिहरेकstudentकोadjustmentआफ्नाcolumnsमालाग्यो। "
    "Rightबाटshapecompareगर, valueकोनामबाटguessनगर।",
    ('scores + student_adjustment  # shape (3,) versus table(3,2)', 'scores + student_adjustment[:,np.newaxis]',
     "Trailing lengths2 and3 conflict; a length-one column axis expresses per-row broadcasting."),
    "Reject incompatible shape(2,3) and shape(2,) using a real operation.",
    '''
    import numpy as np
    a = np.zeros((2, 3))
    try:
        a + np.ones(2)
    except ValueError:
        print("Incompatible trailing dimensions")
    ''',
    "Compute an outer sum from a column of two values and a row of three.",
    '''
    import numpy as np
    column = np.array([10, 20])[:, np.newaxis]
    row = np.array([1, 2, 3])
    result = column + row
    print(result.tolist(), result.shape)
    ''',
    "Align trailing dimensions and verify axis meaning. Insert length-one axes deliberately; shape compatibility does not guarantee semantic correctness.",
    [("How are broadcasting dimensions compared?", "From the right", "By variable name", "Only by total size", "Trailing dimensions must be equal or length1."),
     ("What shape does a length3 vector gain with [:,newaxis]?", "(3,1)", "(1,3)", "(3,3)", "A new trailing length-one axis makes it a column.")])

add(3, "3. Column normalization and constant-column division",
    "Normalize each column independently and define what happens to a constant column.",
    [("min/max axis=0; keepdims", "Reducing axis0 leaves one value per column. keepdims=True retains the reduced axis as length1 so shape and broadcasting remain explicit."),
     ("np.divide out/where", "A ufunc can write into an initialized output only where a condition is true. Initialize out because excluded locations are otherwise not filled by the operation."),
     ("np.where evaluation", "np.where chooses between already-evaluated expressions. It does not prevent a division expression from being evaluated at zero denominators.")],
    "Min-max normalization computes (value-column_min)/(column_max-column_min). A constant column has range0, so the formula alone is undefined. "
    "Here the explicit policy is to return zero for a constant column. Initialize a float output of zeros, then divide only where the column range is nonzero. "
    "Do not write np.where(range!=0, difference/range,0) expecting the invalid division never to happen; the division is computed before where selects. "
    "For real data validate nonfinite values and document whether zero is the desired constant-column representation.",
    'low = values.min(axis=0, keepdims=True)\nspan = values.max(axis=0,keepdims=True)-low\nresult = np.zeros(values.shape, dtype=np.float64)\nnp.divide(values-low,span,out=result,where=span!=0)',
    '''
    import numpy as np
    values = np.array([[10, 5], [20, 5], [30, 5]], dtype=np.float64)
    low = values.min(axis=0, keepdims=True)
    span = values.max(axis=0, keepdims=True) - low
    result = np.zeros(values.shape, dtype=np.float64)
    np.divide(values - low, span, out=result, where=span != 0)
    print("Minimum shape:", low.shape)
    print("Ranges:", span.tolist())
    print("Normalized:", result.tolist())
    ''',
    "पहिलोcolumn0–1 भयो। दोस्रोcolumnconstantभएकालेयसpolicyअनुसार0रह्यो। out पहिलेzerosलेinitializedछ। "
    "Excludeddivisionलाईwhereलेछान्छ; np.whereकोbranchexpressionपहिलेcomputeहुनेफरकबुझ।",
    ('np.where(span != 0, (values-low)/span, 0)', 'Initialize out; np.divide(values-low,span,out=out,where=span!=0)',
     "np.where does not lazily skip evaluating its division expression."),
    "Normalize a single column [2,4,6] to [0,0.5,1].",
    '''
    import numpy as np
    values = np.array([[2.0], [4.0], [6.0]])
    low = values.min(axis=0, keepdims=True)
    span = values.max(axis=0, keepdims=True) - low
    out = np.zeros(values.shape)
    np.divide(values-low, span, out=out, where=span != 0)
    print(out.tolist())
    ''',
    "Use an all-constant table and verify a finite zero result under this contract.",
    '''
    import numpy as np
    values = np.full((2, 3), 7.0)
    span = values.max(axis=0, keepdims=True)-values.min(axis=0, keepdims=True)
    out = np.zeros(values.shape)
    np.divide(values-values.min(axis=0,keepdims=True), span, out=out, where=span!=0)
    print(out.tolist(), bool(np.isfinite(out).all()))
    ''',
    "Normalize with an explicit constant-column policy. Retain shapes, initialize masked outputs and distinguish np.divide's where from np.where's eager inputs.",
    [("Does np.where prevent evaluation of a division branch?", "No", "Yes", "Only for float64", "Its input expressions are evaluated first."),
     ("Why initialize out before masked division?", "Excluded cells must have defined values", "To change the source", "To send mail", "where=False locations are not assigned by that division.")])

add(3, "4. Z-scores and a zero-spread policy",
    "Standardize a numeric sequence while distinguishing a descriptive flag from a judgment.",
    [("mean; standard deviation; z-score", "Mean describes the average; standard deviation describes spread. A z-score is (value-mean)/std for a chosen population/sample convention."),
     ("ddof=0", "NumPy std uses denominator N by default (ddof=0). Other purposes can require a different denominator; Day5 expands this distinction."),
     ("Zero spread; descriptive outlier flag", "All-identical values have std0. This lesson returns z=0 by explicit policy; a threshold flag is a prompt to inspect data, not proof a person/data point is wrong.")],
    "For [10,10,10,10,0], the low value is far below this small group's mean. Compute its distance in standard-deviation units and optionally flag abs(z)>=2. "
    "This is a descriptive classroom rule, not a universal grading decision or automatic reason to remove an observation. "
    "Initialize zeros and divide only when std is positive, so an identical-value sample does not generate an invalid result. "
    "Document ddof, the group being compared and the threshold. A different group/denominator can change the interpretation.",
    'center = values.mean()\nspread = values.std(ddof=0)\nz = zeros_like_float(values)\nnp.divide(values-center,spread,out=z,where=spread>0)',
    '''
    import numpy as np
    values = np.array([10, 10, 10, 10, 0], dtype=np.float64)
    z = np.zeros(values.shape)
    np.divide(values-values.mean(), values.std(ddof=0), out=z, where=values.std(ddof=0)>0)
    print("Mean/std:", float(values.mean()), float(values.std(ddof=0)))
    print("Z:", z.tolist())
    print("Inspect flags:", (np.absolute(z) >= 2).tolist())
    ''',
    "Mean8रstd4बाटz[0.5,...,-2]आयो। abs(z)>=2लेinspectflagदियो, studentगलतभन्नेjudgmentहोइन। "
    "Group, threshold रddof स्पष्टलेख।",
    ('Remove every record flagged by a z-score rule', 'Inspect flagged records and explain the rule before any data decision',
     "A descriptive threshold is not proof of an invalid observation."),
    "Handle an identical-value sequence under the zero-z policy.",
    '''
    import numpy as np
    values = np.array([5.0, 5.0, 5.0])
    out = np.zeros(values.shape)
    np.divide(values-values.mean(), values.std(ddof=0), out=out, where=values.std(ddof=0)>0)
    print(out.tolist())
    ''',
    "Distinguish signs of z-scores for below-mean and above-mean values.",
    '''
    import numpy as np
    values = np.array([0.0, 10.0])
    z = (values-values.mean())/values.std(ddof=0)
    print(z.tolist())
    ''',
    "State your group, spread convention, threshold and zero-spread policy. Z-scores describe relative distance; flags require interpretation.",
    [("What is NumPy std's default ddof?", "0", "1", "Always the column count", "Default standard deviation uses denominator N."),
     ("Does an outlier flag prove a record must be deleted?", "No", "Yes", "Only for grades", "It is an inspection signal under a stated rule.")])

add(4, "1. Reductions: which axis disappears?",
    "Compute per-assignment and per-student statistics without reversing the axes.",
    [("sum/mean/min/max with axis", "A reduction combines entries along the specified axis and removes it by default. axis=0 on a student-by-assignment table leaves one result per assignment."),
     ("keepdims", "keepdims retains reduced dimensions with length1. A per-row mean then has shape(students,1), useful for subtracting row means."),
     ("Global reduction", "Without an axis, a reduction generally combines all elements. This global statistic is different from a row/column report.")],
    "Draw a 3×2 table and label rows students, columns assignments. axis=0 collapses the student dimension, so its result has two assignment values. "
    "axis=1 collapses assignments, leaving three student values. Think 'which dimension is being reduced?' rather than 'axis0 means a row result'. "
    "No-axis mean answers a different question: all cells pooled together. "
    "Use keepdims when you need the result to broadcast back against the original orientation.",
    'per_assignment = scores.mean(axis=0)\nper_student = scores.mean(axis=1)\nrow_centres = scores.mean(axis=1, keepdims=True)',
    '''
    import numpy as np
    scores = np.array([[10, 20], [30, 40], [50, 60]], dtype=np.float64)
    print("Assignment means:", scores.mean(axis=0).tolist())
    print("Student means:", scores.mean(axis=1).tolist())
    print("Global mean:", float(scores.mean()))
    row_centres = scores.mean(axis=1, keepdims=True)
    print("Centres shape:", row_centres.shape)
    print("Centred rows:", (scores-row_centres).tolist())
    ''',
    "axis0लेstudentsaxisघटाएरदुईassignmentmeansछोड्यो। axis1लेassignmentsघटाएरतीनstudentmeansछोड्यो। "
    "keepdimsको(3,1)result मूलtableमा सहीbroadcastहुन्छ।",
    ('axis=0  # assume one result per row', 'Track the removed axis: axis0 reduction leaves the column/assignment axis',
     "Axis identifies the dimension being combined, not the label of output records."),
    "Compute row sums and column maxima for a 2×3 table.",
    '''
    import numpy as np
    values = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.int64)
    print(values.sum(axis=1).tolist())
    print(values.max(axis=0).tolist())
    ''',
    "Compare output shapes with and without keepdims for axis0.",
    '''
    import numpy as np
    values = np.ones((3, 2))
    print(values.mean(axis=0).shape)
    print(values.mean(axis=0, keepdims=True).shape)
    ''',
    "Name the reduced axis and the surviving semantic dimension. Global, row and column statistics answer different questions.",
    [("For shape(3,2), what shape results from mean(axis=0)?", "(2,)", "(3,)", "(3,2)", "The length3 student axis is reduced."),
     ("What does keepdims preserve?", "Reduced axes as length1", "Every original value", "File passwords", "The result retains dimensional alignment for broadcasting.")])

add(4, "2. Argmin/argmax, ties and spread conventions",
    "Distinguish extreme values from their positions and choose a standard-deviation convention.",
    [("argmin; argmax; first tie", "These return positions of extreme values, not the values themselves. With an axis, positions refer to that axis; the first tied occurrence is selected."),
     ("Flat argmax; unravel_index", "Without axis, argmax returns an index in the flattened order. unravel_index converts it into coordinates for a known shape."),
     ("std ddof; denominator N-ddof", "ddof=0 computes population-style spread for the observed values; ddof=1 uses a sample-style denominator. Choose based on the question and require enough observations.")],
    "A largest score and a student's index are not interchangeable. For each assignment, argmax(axis=0) reports a row position; use that position with the column to retrieve the value. "
    "Ties are not all winners: argmax returns one first position under its ordering. If you need every tie, build an equality mask. "
    "For [2,4], population std is1 while sample std is about1.414. Neither should be chosen only because it appears in a familiar formula. "
    "The project later reports descriptive population statistics for its complete input rather than making sampling claims.",
    'positions = scores.argmax(axis=0)\nvalues = scores.max(axis=0)\ncoordinates = np.unravel_index(scores.argmax(), scores.shape)',
    '''
    import numpy as np
    scores = np.array([[80, 90], [80, 70], [60, 95]], dtype=np.float64)
    print("Best row indexes:", scores.argmax(axis=0).tolist())
    print("Best values:", scores.max(axis=0).tolist())
    row, column = np.unravel_index(scores.argmax(), scores.shape)
    print("Global best coordinates:", int(row), int(column))
    values = np.array([2.0, 4.0])
    print("Std ddof0/1:", round(float(values.std(ddof=0)), 3), round(float(values.std(ddof=1)), 3))
    ''',
    "पहिलोassignment80माtieछ;argmaxलेfirstrowindex0दियो। Value80रindex0अलगचिजहुन्। "
    "ddofबदल्दाspreadबदलिन्छ, त्यसैलेpolicyस्पष्टगर।",
    ('Treat argmax as the maximum value', 'Use max for values and argmax for their positions',
     "One describes magnitude, the other location."),
    "Find every tie for the largest value using a Boolean mask.",
    '''
    import numpy as np
    values = np.array([9, 7, 9], dtype=np.int64)
    print((values == values.max()).tolist())
    print(int(values.argmax()))
    ''',
    "Check sample spread's observation-count requirement before requesting ddof1.",
    '''
    import numpy as np
    values = np.array([5.0])
    print("Can compute ddof1 with N>1:", values.size > 1)
    print("Population spread:", float(values.std(ddof=0)))
    ''',
    "Separate values, indexes and all-tie masks. State the spread denominator and check observation counts before sample-style statistics.",
    [("Does argmax return the maximum score itself?", "No", "Yes", "Only for a tie", "It returns the position."),
     ("For a tied maximum, what does argmax normally select?", "The first occurrence", "Every tied position", "A random one", "Use an equality mask for all ties.")])

add(4, "3. Missing and nonfinite values need a policy",
    "Reject or explicitly handle NaN/inf rather than silently calling every result valid.",
    [("NaN; inf; isfinite; isnan", "NaN represents an invalid/missing numeric result under many workflows; infinity is nonfinite too. isfinite excludes both; isnan identifies NaN specifically."),
     ("NaN equality", "NaN is not equal to itself. Use isnan, not value == np.nan, to detect it."),
     ("nanmean and missing-value policy", "nanmean ignores NaN but not arbitrary bad data; all-NaN slices need handling and can warn. Rejecting, imputing and excluding missing values answer different questions.")],
    "A table with one missing assignment does not automatically mean score0. Ignoring NaN changes which assignments contribute to a mean. "
    "For this week's final grade project, require every score to be finite and in0–100; missing input is an error to fix, not a guessed score. "
    "For another task you may deliberately compute an observed-only mean, but report the count and reject all-missing groups. "
    "Infinity is not fixed by nanmean. Check the accepted domain before aggregation and preserve diagnostics.",
    'if not np.isfinite(scores).all(): reject\nmissing = np.isnan(scores)\n# Optional observed-only statistics require counts and a stated policy',
    '''
    import numpy as np
    values = np.array([10.0, np.nan, np.inf])
    print("Finite:", np.isfinite(values).tolist())
    print("NaN:", np.isnan(values).tolist())
    print("NaN == NaN:", bool(np.nan == np.nan))
    observed = np.array([10.0, np.nan, 20.0])
    print("Observed-only mean:", float(np.nanmean(observed)))
    print("Observed count:", int(np.isfinite(observed).sum()))
    ''',
    "NaNmissingहुनसक्छ, तर0भन्नेअर्थहोइन। nanmeanको15दुईobservedvaluesकोmeanहो। "
    "Inffiniteहोइन, नतnanmeanलेसबैinvalidvalueठीकबनाउँछ।",
    ('values == np.nan', 'np.isnan(values)',
     "NaN is not equal to itself; equality is not its detection rule."),
    "Validate finite 0–100 scores and report invalid positions.",
    '''
    import numpy as np
    scores = np.array([50.0, np.nan, 120.0, -1.0])
    valid = np.isfinite(scores) & (scores >= 0) & (scores <= 100)
    print(valid.tolist())
    print("Invalid indexes:", np.flatnonzero(~valid).tolist())
    ''',
    "Avoid calculating an observed mean for an all-missing group.",
    '''
    import numpy as np
    values = np.array([np.nan, np.nan])
    count = int(np.isfinite(values).sum())
    print("Observed:", count)
    print("Action:", "reject all-missing group" if count == 0 else "apply documented policy")
    ''',
    "Missing, zero and infinity are different. Choose and document a policy, report observed counts and validate numeric domains before reductions.",
    [("Is a missing score automatically zero?", "No", "Yes", "Only in a CSV", "Zero is a real value, while missing needs an explicit policy."),
     ("Does isfinite reject both NaN and infinity?", "Yes", "No", "Only int8", "It identifies finite values under numerical rules.")])

add(4, "4. Weighted scores and transparent threshold reports",
    "Compute one weighted result per student using validated column weights.",
    [("Weights and axis alignment", "A shape(assignments,) weight vector aligns with table columns. Multiplying then summing axis1 gives one weighted score per student."),
     ("Weight contract", "Weights should be finite, nonnegative, match the assignment count and sum to1 under an explicit tolerance. An arbitrary vector should not silently become an accepted grading rule."),
     ("Pass mask; count_nonzero", "A comparison makes a Boolean pass mask. count_nonzero counts True values; it does not automatically justify the chosen pass threshold.")],
    "A score table can describe assignments with different importance. For weights[0.25,0.75], the second assignment contributes three times as much as the first. "
    "Validate the weight vector and keep raw scores so an adjusted report can be traced back. "
    "A passing threshold is a policy you state, not something NumPy discovers. Our classroom example uses60 and reports a count only. "
    "Do not mix weights for rows with weights for assignments because two lengths happen to match. Axis names matter even when broadcasting succeeds.",
    'require valid weights with shape(assignments,)\nweighted = (scores * weights).sum(axis=1)\npass_count = np.count_nonzero(weighted >= threshold)',
    '''
    import numpy as np
    scores = np.array([[40, 80], [80, 40], [90, 90]], dtype=np.float64)
    weights = np.array([0.25, 0.75], dtype=np.float64)
    if weights.shape != (scores.shape[1],) or not np.isfinite(weights).all() or (weights < 0).any() or not np.isclose(weights.sum(), 1.0):
        raise ValueError("Invalid weights")
    weighted = (scores * weights).sum(axis=1)
    print("Weighted:", weighted.tolist())
    print("Pass flags:", (weighted >= 60).tolist())
    print("Pass count:", int(np.count_nonzero(weighted >= 60)))
    ''',
    "पहिलोstudent70, दोस्रो50भयो; assignmentsकोimportanceफरकभएकोलेsimplemeanसँगफरकछ। "
    "Weightsरthreshold policyकोभागहुन्; NumPyलेgradepolicyनिर्णयगर्दैन।",
    ('Apply unvalidated weights because the multiplication works', 'Validate length, nonnegative finite values and sum policy',
     "Shape compatibility alone does not make a weighting scheme meaningful."),
    "Use equal two-assignment weights and compare with an ordinary row mean.",
    '''
    import numpy as np
    scores = np.array([[40.0, 80.0], [60.0, 90.0]])
    weights = np.array([0.5, 0.5])
    print((scores*weights).sum(axis=1).tolist())
    print(np.allclose((scores*weights).sum(axis=1), scores.mean(axis=1)))
    ''',
    "Reject a negative weight even if the sum happens to be1.",
    '''
    import numpy as np
    weights = np.array([-0.5, 1.5])
    print("Sum:", float(weights.sum()))
    print("Nonnegative policy:", bool((weights >= 0).all()))
    ''',
    "Align weights with named axes, validate their domain and report threshold decisions transparently. Raw data and policy should remain inspectable.",
    [("Which axis is reduced for a weighted result per student?", "axis1", "axis0", "The file extension", "Weights apply to assignment columns; assignments are combined."),
     ("Is sum1 alone enough to validate weights?", "No", "Yes", "Only for float64", "Negative, nonfinite or wrong-length values still violate the contract.")])

add(5, "1. Reshape, transpose and diagonal extraction",
    "Rearrange a known number of elements without changing their meaning accidentally.",
    [("reshape; inferred -1", "reshape changes the arrangement while preserving element count. One dimension may be -1 to infer its length; incompatible counts fail."),
     ("transpose; .T", "For a 2-D table .T swaps axes. A 1-D vector's .T remains 1-D; it does not create a column axis."),
     ("np.diag; ravel", "diag extracts a 2-D diagonal (or constructs a diagonal from1-D input). ravel returns a flattened array, using a view when possible.")],
    "An array of six entries can become shape(2,3) or(3,2). It cannot become(4,2) because that requires eight entries. "
    "Reshaping a score table is not automatically a valid way to change students/assignments: element count can match while semantic labels become wrong. "
    "A transpose deliberately swaps the meanings of its two axes. Use it only with a new explicit orientation. "
    "reshape/ravel may share storage depending on layout; do not assume independence. The example also fulfils the curriculum's5×5 diagonal exercise.",
    'arr.reshape(rows,columns)\narr.reshape(-1,columns)\narr.T\nnp.diag(square_table)',
    '''
    import numpy as np
    flat = np.arange(6, dtype=np.int64)
    table = flat.reshape(2, 3)
    print(table.tolist(), table.shape)
    print(table.T.tolist(), table.T.shape)
    print("Vector transpose shape:", flat.T.shape)
    square = np.arange(25, dtype=np.int64).reshape(5, 5)
    print("Diagonal:", np.diag(square).tolist())
    ''',
    "reshapeकोcountसमानछ; transposeलेaxisस्वापगर्‍यो। 1-D.Tकोshapeअझै(6,)छ, columnबनेन। "
    "5×5diagonalindexes[0,0],[1,1]...बाटआए।",
    ('vector.T  # assume shape(n,1)', 'vector[:,np.newaxis] to create a column',
     "A one-dimensional transpose does not insert an axis."),
    "Infer the row count for12 elements and3 columns.",
    '''
    import numpy as np
    values = np.arange(12, dtype=np.int64).reshape(-1, 3)
    print(values.shape)
    ''',
    "Verify an incompatible reshape fails instead of creating missing elements.",
    '''
    import numpy as np
    try:
        np.arange(6).reshape(4, 2)
    except ValueError:
        print("Element count mismatch")
    ''',
    "Shape changes preserve counts, not necessarily meanings. Track orientation and storage ownership; 1-D transpose is not column creation.",
    [("Can six elements reshape to(4,2)?", "No", "Yes", "Only with int64", "The requested element count is8."),
     ("Does a 1-D vector .T become a 2-D column?", "No", "Yes", "Only when nonempty", "Transpose does not add a missing axis.")])

add(5, "2. Concatenate, stack, split and flatten",
    "Distinguish combining along an existing axis from creating a new axis.",
    [("concatenate; stack", "concatenate joins along an existing axis; other dimensions must match. stack adds a new axis and requires matching input shapes."),
     ("split; array_split", "split requires equal division when given a section count; array_split allows unequal chunks. Explicit boundary indexes describe another split contract."),
     ("flatten versus ravel", "flatten always copies; ravel uses a view when possible. Layout matters, especially for a transposed array, so verify sharing when mutation ownership matters.")],
    "Joining two row vectors end to end gives one longer vector. Stacking them on axis0 gives a two-row table instead. "
    "Two student-by-assignment batches concatenate on axis0 when they share assignment columns. Adding a new batch axis with stack is a different structure. "
    "For unequal chunks use array_split intentionally, not split and hope it drops a remainder. "
    "Flattening is useful for certain operations but can erase student/assignment orientation; keep the original shape in the data contract.",
    'np.concatenate((a,b), axis=0)  # existing axis\nnp.stack((a,b), axis=0)        # new axis\nnp.array_split(values,3)\nvalues.flatten()  # independent copy',
    '''
    import numpy as np
    a, b = np.array([1, 2]), np.array([3, 4])
    joined, stacked = np.concatenate((a, b)), np.stack((a, b))
    print("Joined:", joined.tolist(), joined.shape)
    print("Stacked:", stacked.tolist(), stacked.shape)
    chunks = np.array_split(np.arange(5), 3)
    print("Chunks:", [chunk.tolist() for chunk in chunks])
    table = np.arange(6).reshape(2, 3)
    print("Share ravel/flatten:", np.shares_memory(table, table.ravel()), np.shares_memory(table, table.flatten()))
    ''',
    "Joinedकोshape(4,)छ, stackedको(2,2)छ। array_splitलेunequalchunksदियो। "
    "योcontiguoustableमाravelsharesdataछ, flattencopyछ; सबैlayoutमारavelsharesहुन्छभन्नेguaranteeहोइन।",
    ('stack and concatenate always return the same shape', 'Decide whether you are extending an axis or introducing one',
     "The operations represent different arrangements."),
    "Join two one-row score batches along the student axis.",
    '''
    import numpy as np
    a = np.array([[60, 70]])
    b = np.array([[80, 90]])
    result = np.concatenate((a, b), axis=0)
    print(result.tolist(), result.shape)
    ''',
    "Verify split rejects dividing five entries into three equal chunks.",
    '''
    import numpy as np
    try:
        np.split(np.arange(5), 3)
    except ValueError:
        print("Not equally divisible; choose array_split intentionally")
    ''',
    "Join existing axes with concatenate, add axes with stack and choose split contracts explicitly. Flattening/storage choices should preserve intended ownership and labels.",
    [("Which operation adds a new axis?", "stack", "concatenate", "argmin", "stack groups matching arrays under a new dimension."),
     ("Does flatten normally share the source buffer?", "No", "Yes", "Only for int64", "flatten always makes a copy.")])

PROJECT = clean(r'''
import argparse
import io
import json
from pathlib import Path
import sys
import numpy as np

def validate_scores(scores):
    values = np.asarray(scores)
    if values.ndim != 2 or not 1 <= values.shape[0] <= 10_000 or not 1 <= values.shape[1] <= 200:
        raise ValueError("Need a nonempty student-by-assignment table within practice limits")
    if values.dtype.kind not in "iuf":
        raise ValueError("Need real numeric scores, not booleans/objects/text")
    values = values.astype(np.float64, copy=True)
    if not np.isfinite(values).all() or ((values < 0) | (values > 100)).any():
        raise ValueError("Every score must be finite and in 0..100")
    return values

def analyse(scores, curve=5.0, threshold=2.0, pass_score=60.0):
    values = validate_scores(scores)
    if not np.isfinite(curve) or not -100 <= curve <= 100:
        raise ValueError("Curve must be finite and in -100..100")
    if not np.isfinite(threshold) or threshold <= 0:
        raise ValueError("Z threshold must be finite and positive")
    if not np.isfinite(pass_score) or not 0 <= pass_score <= 100:
        raise ValueError("Pass score must be finite and in 0..100")
    student_means = values.mean(axis=1)
    assignment_means = values.mean(axis=0)
    spread = student_means.std(ddof=0)
    z = np.zeros(student_means.shape, dtype=np.float64)
    np.divide(student_means-student_means.mean(), spread, out=z, where=spread>0)
    flags = np.absolute(z) >= threshold
    curved = np.clip(values + curve, 0, 100)
    low = values.min(axis=0, keepdims=True)
    ranges = values.max(axis=0, keepdims=True)-low
    normalized = np.zeros(values.shape, dtype=np.float64)
    np.divide(values-low, ranges, out=normalized, where=ranges!=0)
    return {
        "schema": 1,
        "orientation": "rows=students; columns=assignments; indexes are zero-based",
        "shape": list(values.shape),
        "policy": {"curve_points": float(curve), "clip_range": [0, 100],
                   "pass_score": float(pass_score), "z_threshold": float(threshold),
                   "std_ddof": 0, "constant_column_normalized_value": 0.0,
                   "zero_spread_z_value": 0.0, "missing_scores": "reject",
                   "outlier_basis": "raw student means; inspect only"},
        "student_means": student_means.tolist(),
        "student_min": values.min(axis=1).tolist(),
        "student_max": values.max(axis=1).tolist(),
        "student_std": values.std(axis=1, ddof=0).tolist(),
        "assignment_means": assignment_means.tolist(),
        "assignment_min": values.min(axis=0).tolist(),
        "assignment_max": values.max(axis=0).tolist(),
        "assignment_std": values.std(axis=0, ddof=0).tolist(),
        "class_mean": float(values.mean()),
        "student_z": z.tolist(),
        "inspect_student_indexes": np.flatnonzero(flags).tolist(),
        "raw_pass_flags": (student_means >= pass_score).tolist(),
        "curved_scores": curved.tolist(),
        "curved_student_means": curved.mean(axis=1).tolist(),
        "normalized_columns": normalized.tolist(),
    }

def load_scores(path):
    with path.open("rb") as stream:
        raw = stream.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Practice input exceeds 2 MB")
    text = raw.decode("utf-8-sig")
    if not text.strip():
        raise ValueError("Empty score file")
    # Contract: plain rectangular numeric CSV; no headers, quotes, labels or comments.
    values = np.loadtxt(io.StringIO(text), delimiter=",", comments=None,
                        dtype=np.float64, ndmin=2)
    return validate_scores(values)

def save_report(path, report):
    encoded = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
    temporary = path.with_name(path.name + ".tmp")
    owned = False
    try:
        with temporary.open("x", encoding="utf-8") as stream:
            owned = True
            stream.write(encoded)
        temporary.replace(path)
        owned = False
    finally:
        if owned:
            temporary.unlink(missing_ok=True)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Vectorized grade analysis of plain numeric CSV", allow_abbrev=False)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--curve", type=float, default=5.0)
    parser.add_argument("--z-threshold", type=float, default=2.0)
    parser.add_argument("--pass-score", type=float, default=60.0)
    args = parser.parse_args(argv)
    try:
        if args.input.resolve() == args.output.resolve() or args.output.suffix.lower() != ".json":
            raise ValueError("Choose a separate .json output path")
        scores = load_scores(args.input)
        report = analyse(scores, args.curve, args.z_threshold, args.pass_score)
        report["input_name"] = args.input.name
        save_report(args.output, report)
    except (OSError, UnicodeError, ValueError, TypeError, ArithmeticError) as error:
        print("FAILED:", error, file=sys.stderr)
        return 1
    print("Students:", report["shape"][0], "Assignments:", report["shape"][1])
    print("Raw class mean:", round(report["class_mean"], 2))
    print("Inspect indexes:", report["inspect_student_indexes"])
    print("Report saved")
    return 0
''')

SETUP = '''
import tempfile
def sample_scores(root):
    path = root / "scores.csv"
    path.write_text("80,90,100\\n60,70,80\\n40,50,60\\n", encoding="utf-8")
    return path
'''

add(5, "3. Complete project: a vectorized grade-analysis tool",
    "Load a validated score matrix and generate transparent raw/curved statistics without Python numeric loops.",
    [("np.loadtxt; ndmin=2", "loadtxt reads a simple numeric text format. ndmin=2 retains a matrix for a single row or column. This project does not accept arbitrary CSV quoting/header/label conventions."),
     ("np.asarray; dtype.kind", "asarray obtains array-like input as an array. dtype.kind helps reject Boolean/object/text domains before casting; a numeric cast is not accepted as validation."),
     ("np.clip; raw versus curved", "clip bounds values to a chosen interval. The project's adjustment is a stated classroom policy; raw statistics and outlier flags stay based on the original scores."),
     ("np.flatnonzero; JSON conversion", "flatnonzero returns matching flattened indexes for the1-D student flag vector. tolist/float turn numerical results into JSON-compatible Python values without writing numerical loops.")],
    "Read the project in layers: validate_scores defines a nonempty finite0–100 matrix, analyse performs vectorized reductions/broadcasting, load_scores accepts a narrow numeric CSV contract, and main saves a report. "
    "There are no Python for/while/comprehension loops in the project: numeric work uses NumPy. Standard-library CLI/file/JSON operations still do their own work internally. "
    "Rows represent student input order and columns assignments; the input has no student names or header. indexes in the report are zero-based positions, not stable student identities. "
    "The default curve adds5 points to each cell and clips to0–100. This is an exercise policy, not a recommendation for actual grading. "
    "Flags use raw student means, population spread(ddof0) and an explicit threshold; flagged rows should be inspected rather than deleted. "
    "The input is preserved. Validation completes before a separate JSON report is atomically replaced, and malformed input leaves any prior report untouched.",
    'plain numeric CSV -> validated(student,assignment) matrix\nraw reductions + explicit curve + zero-safe normalization/z\nconvert numerical results -> JSON -> atomic separate report',
    PROJECT + SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source = sample_scores(root)
    output = root / "report.json"
    assert main([str(source), str(output)]) == 0
    report = json.loads(output.read_text(encoding="utf-8"))
    print("Student means:", report["student_means"])
    print("Assignment means:", report["assignment_means"])
    print("Curved means:", report["curved_student_means"])
''',
    "Sampleमाrawstudentmeans90,70,50छन्। Assignmentmeans60,70,80छन्। 100मा5थप्दाclip100 भएकालेपहिलोcurvedmean95भन्दाकमछ। "
    "Reportकोindexstudentidentityहोइन; rawdataरpolicyदुवैजोगाऊ।",
    ('Cast unknown data then assume valid scores', 'Validate numeric kind, shape, finite values and domain before computing',
     "A conversion can hide invalid text, Boolean data or wrong matrix orientation."),
    "Use a constant score matrix and verify zero-safe normalization/z plus upper-bound clipping.",
    PROJECT + '''
scores = np.full((3, 2), 98.0)
report = analyse(scores, curve=5)
print(report["student_z"])
print(report["normalized_columns"])
print(report["curved_scores"])
''',
    "Use four high means and one low mean; verify the descriptive flag refers to its zero-based student index.",
    PROJECT + '''
scores = np.array([[90, 90], [90, 90], [90, 90], [90, 90], [0, 0]], dtype=np.float64)
report = analyse(scores, threshold=2)
print(report["student_z"])
print(report["inspect_student_indexes"])
''',
    "Vectorize after validating orientation/domain. Keep raw observations, explicit numerical policies and source order; save a new report only after every check succeeds.",
    [("Why does loadtxt use ndmin=2?", "To retain a matrix for one row/column", "To create two students automatically", "To replace missing scores", "A singleton input still needs the student-by-assignment orientation."),
     ("Are inspect indexes stable student identities?", "No", "Yes", "Only when numeric", "They are positions in the supplied input order.")])

add(5, "4. Whole-week retrieval and numerical failure tests",
    "Verify shapes, ownership, axes, finite results and preserved input/report state.",
    [("Numerical invariant", "An invariant is a property expected to hold: input unchanged, known output shapes, finite values, and explicit bounds/policies. Test these alongside worked numeric results."),
     ("assert_allclose versus exact assertions", "NumPy's testing.assert_allclose checks numerical arrays under selected tolerances. Use exact shape/dtype/identity checks separately; approximate equality alone may allow unintended broadcasting."),
     ("Rejection tests", "Tests for NaN, infinity, out-of-range values, empty/ragged input and corrupt output paths exercise different boundaries. They should preserve the prior valid report.")],
    "Do not stop at 'it printed an array'. Explain which axis was reduced and prove the intended shapes. "
    "The same numbers in a vector and a column can lead to different broadcasting, and a correct-looking result can still have mutated its source through a view. "
    "Test constant-column and identical-student groups explicitly: they expose zero denominators that random examples might miss. "
    "The accompanying project tests check malformed CSV, out-of-range/nonfinite data, one row/column, output preservation and the absence of Python numerical loops. "
    "For a floating result, choose tolerances for the scale and also assert its shape. Finish the week by explaining a broadcasting example and writing a validated analysis function without copying.",
    'assert actual.shape == expected.shape\nnp.testing.assert_allclose(actual,expected,rtol=...,atol=...)\nassert input unchanged; assert finite policies\nassert malformed input fails before report replacement',
    PROJECT + '''
scores = np.array([[10.0, 20.0], [30.0, 40.0]])
before = scores.copy()
report = analyse(scores)
actual = np.array(report["student_means"])
expected = np.array([15.0, 35.0])
assert actual.shape == expected.shape
np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)
print("Means verified")
print("Input unchanged:", np.array_equal(scores, before))
''',
    "Valuesका साथshapeपनिcheckedछ। Originalscorescopyसँगमेलखायो, mutateभएकोछैन। "
    "Approximateassertionमा unintendedbroadcastingलुक्नसक्नेभएकालेshapeछुट्टैजाँच।",
    ('Approximate numeric equality alone proves every semantic dimension is correct', 'Assert expected shape/axis meaning separately from tolerance-based value checks',
     "A value comparison can broadcast arrays and does not encode student/assignment labels."),
    "Reject NaN, infinity and score101 using the same validation contract.",
    PROJECT + '''
for scores in [np.array([[np.nan]]), np.array([[np.inf]]), np.array([[101.0]])]:
    try:
        validate_scores(scores)
    except ValueError:
        print("Rejected invalid scores")
''',
    "Verify a one-student, one-assignment table keeps the2-D shape and zero-spread policies.",
    PROJECT + '''
report = analyse(np.array([[75.0]]))
print(report["shape"], report["student_means"])
print(report["student_z"], report["normalized_columns"])
''',
    "Week27 mastery: read shapes/axes, control ownership/dtype, predict broadcasting, validate numerical domains, handle zero/missing cases and verify a complete vectorized report.",
    [
        ("Does list *2 double its numbers?", "No; it repeats the list", "Yes", "Only for int64", "List and ndarray arithmetic differ."),
        ("What is size for shape(2,3)?", "6", "2", "3", "Size is the product of axis lengths."),
        ("Does empty guarantee zeros?", "No", "Yes", "Only float64", "Fill its buffer before reading."),
        ("Does arange normally include stop?", "No", "Yes", "Only with seed", "Stop is excluded under its usual contract."),
        ("Can a basic-slice edit mutate its source?", "Yes", "No", "Only lists", "Basic slices normally share storage."),
        ("Which combines Boolean array comparisons?", "& with parentheses", "Python and", "A CSV delimiter", "Use element-wise logic."),
        ("What does ndarray * mean?", "Element-wise multiplication", "Always matrix multiplication", "Transpose", "Matrix multiplication uses @."),
        ("How are broadcasting axes aligned?", "From the right", "By variable title", "Only total size", "Aligned lengths must match or be1."),
        ("For students×assignments, what does mean(axis0) leave?", "One value per assignment", "One per student", "A ZIP", "Axis0 students are reduced."),
        ("Does argmax return the maximum value?", "No; its index", "Yes", "Only tied scores", "Positions and values differ."),
        ("Does a one-dimensional transpose add an axis?", "No", "Yes", "Only under100", "Use newaxis for a column."),
        ("Must a z-score flag be deleted automatically?", "No", "Yes", "Only for grades", "It is a descriptive inspection signal under stated policy."),
    ])

# Explicit first-use explanations for helpers appearing before their later full lessons.
DAYS["27.3"]["parts"][2]["sections"].insert(3, s("new", "np.isfinite",
    note="isfinite produces a Boolean array marking values that are neither NaN nor infinity. .all() combines those checks into one decision; Day5 explains missing/nonfinite policies fully."))
DAYS["27.4"]["parts"][2]["sections"].insert(3, s("new", "np.flatnonzero",
    note="flatnonzero returns positions where a flattened Boolean/numeric input is nonzero. For the1-D invalid-score mask it returns zero-based invalid indexes, not the invalid score values themselves."))
DAYS["27.0"]["parts"][3]["sections"].insert(3, s("new", "arange; astype; shares_memory",
    note="This memory experiment uses arange for integer positions, astype to convert to an explicitly wider dtype, and shares_memory to check overlapping array data. Day2 teaches creation/conversion fully; Day3 expands views/copies."))
DAYS["27.1"]["parts"][2]["sections"].insert(3, s("new", "Parenthesized & and .all()",
    note="& combines Boolean comparisons element-wise; .all() reduces a Boolean array to one all-True decision. Parenthesize each comparison. Day3 teaches masks/axis reductions in detail."))
DAYS["27.0"]["parts"][0]["sections"].insert(3, s("sh", "python -m pip install numpy",
    note="One-time setup in your practice Python environment. The site and authored examples remain offline afterward; use NumPy2.x for these verified examples."))
DAYS["27.0"]["parts"][0]["sections"].insert(3, s("new", "dtype=np.int64",
    note="dtype selects the array's stored numerical type. np.int64 is a signed 64-bit integer type; these small whole-number examples use it explicitly for predictable storage. Day2 explains range, overflow and floating alternatives."))
DAYS["27.5"]["parts"][2]["sections"].append(s("sh",
    "python grade_analysis.py scores.csv report.json\npython grade_analysis.py scores.csv curved-report.json --curve 5 --z-threshold 2 --pass-score 60\npython grade_analysis.py --help",
    note="Use the supplied plain numeric scores.csv and complete project. Choose a separate JSON output; keep the source file unchanged."))
DAYS["27.5"]["parts"][-1]["sections"].append(s("p",
    "Primary references: https://numpy.org/doc/stable/user/absolute_beginners.html · https://numpy.org/doc/stable/user/basics.broadcasting.html · "
    "https://numpy.org/doc/stable/user/basics.copies.html · https://numpy.org/doc/stable/user/basics.types.html · "
    "https://numpy.org/doc/stable/reference/random/generator.html · https://numpy.org/doc/stable/reference/generated/numpy.std.html · "
    "https://numpy.org/doc/stable/reference/generated/numpy.divide.html · https://numpy.org/doc/stable/reference/generated/numpy.loadtxt.html. "
    "The original explanations, fixtures, complete examples/outputs, practice and solutions are included for offline study."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week27 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in DAYS.items())
    addition = addition.replace("</", "<\\/")
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix + "\n" + addition + original[end:]).encode("utf-8"))
    temporary.replace(target)
    project_root = ROOT / "docs" / "python-week27"
    project_root.mkdir(exist_ok=True)
    (project_root / "grade_analysis.py").write_text(
        '"""Week27 vectorized grade-analysis practice. Python3.11+/NumPy2.x; plain numeric CSV."""\n'
        + PROJECT + '\nif __name__ == "__main__":\n    sys.exit(main())\n', encoding="utf-8")
    (project_root / "scores.csv").write_text("80,90,100\n60,70,80\n40,50,60\n", encoding="utf-8")
    parts = [part for day in DAYS.values() for part in day["parts"]]
    quizzes = sum(len(section["lesson"]["quiz"]) for part in parts for section in part["sections"] if section["t"] == "checkpoint")
    print(f"Added Week27: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {EXECUTED} verified outputs.")


if __name__ == "__main__":
    write()

