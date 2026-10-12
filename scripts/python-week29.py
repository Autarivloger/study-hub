"""Author Week 29 additively; execute each output in an isolated practice folder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
DAYS = {f"29.{d}": {"parts": []} for d in range(6)}
EXECUTED = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global EXECUTED
    with tempfile.TemporaryDirectory(prefix="studyhub-w29-") as folder:
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
    parts = DAYS[f"29.{day}"]["parts"]
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
        s("ex", task, practiceId=f"29.{day}.{index}.build"),
        s("sol", code=clean(solution), out=output(solution), why="Build check: " + key),
        s("ex", "Mini challenge: " + challenge, practiceId=f"29.{day}.{index}.challenge"),
        s("sol", code=clean(challenge_code), out=output(challenge_code), why="Challenge check: " + key),
        s("try", q=quizzes[0][0], code="# Predict and explain before revealing.",
          a=quizzes[0][1], why=quizzes[0][4]),
        s("checkpoint", lesson={"id": f"course:29.{day}.{index}", "quiz": questions}), s("key", key),
    ]})


def lesson(day, title, goal, concepts, explanation, syntax, example, walk,
           wrong, right, reason, task, solution, challenge, challenge_code,
           takeaway, questions):
    """Keep the existing section renderer and durable practice/quiz identifiers."""
    add(day, title, goal, concepts, explanation, syntax, example, walk,
        (wrong, right, reason), task, solution, challenge, challenge_code,
        takeaway, questions)


lesson(0, "1. Missing is a fact, not a value to guess",
    "Distinguish missing markers, empty text, zero and invalid data before choosing a strategy.",
    [("Missingness versus validity", "isna detects pandas missing markers. Empty/whitespace strings, impossible numbers and infinity are not necessarily missing; they require separate domain checks."),
     ("NaN; NaT; pd.NA", "NaN commonly marks missing floating values, NaT marks missing dates, and pd.NA is used by nullable dtypes. Use isna/notna, not equality with a missing marker.")],
    "Week28 showed how to inspect data without changing it. Week29 asks which changes are justified. First define what a field means: zero minutes is a real observation, an empty response may mean unknown, and a negative duration may be invalid. "
    "Do not merge all three meanings under 'dirty'. In this explicitly nullable text column, None is missing but empty text and spaces are still text. "
    "Only convert blank text to missing when your data contract says blanks represent no answer. Keep a copy of the source and record that interpretation. "
    "Missingness can depend on who answered or which system failed, so removing or filling it can change the population being summarized.",
    'missing = series.isna()\nblank = series.str.strip().eq("").fillna(False)\n# Define whether blanks mean missing before replacing them',
    '''
    import pandas as pd
    labels = pd.Series(["yes", "", "   ", None, "0"], dtype="string")
    print("Missing:", labels.isna().tolist())
    blank = labels.str.strip().eq("").fillna(False)
    print("Blank text:", blank.tolist())
    normalized = labels.mask(blank, pd.NA)
    print("After declared blank policy:", normalized.isna().tolist())
    ''',
    "0 text पनि एउटा value हो। None मात्रै सुरुमा missing थियो। Blank लाई missing बनाउने policy लागू गरेपछि मात्र खाली text हरू missing भए।",
    'Replace every falsy-looking value with zero', 'Separate known zero, blank, missing and invalid cases',
    "Unknown and known zero carry different information.",
    "For nullable scores [0,missing,80], print missing flags, observed count and observed mean.",
    '''
    import pandas as pd
    scores = pd.Series([0, pd.NA, 80], dtype="Float64")
    print(scores.isna().tolist(), scores.count(), float(scores.mean()))
    ''',
    "Declare whitespace-only names missing while retaining literal NA as a legitimate text token.",
    '''
    import pandas as pd
    names = pd.Series([" NA ", "   ", None], dtype="string")
    stripped = names.str.strip()
    cleaned = stripped.mask(stripped.eq("").fillna(False), pd.NA)
    print(cleaned.isna().tolist(), cleaned.loc[0])
    ''',
    "Define missingness using the field's meaning. Preserve raw data and explain every conversion.",
    [("Is numeric zero automatically missing?", "No", "Always", "Only in pandas", "Zero can be a valid observed value."),
     ("Does isna always detect whitespace-only text?", "No", "Always", "Only with string dtype", "Blank-text rules are a separate policy.")])

lesson(0, "2. Dropping observations with a stated denominator",
    "Use subset/how/thresh deliberately and compare retained rows with the original population.",
    [("dropna; subset; how", "dropna removes rows by default. subset chooses fields that matter; how='any' removes rows missing any checked field and how='all' removes rows missing every checked field."),
     ("thresh; axis", "thresh requires at least that many nonmissing checked values; do not combine it with how. axis=1 drops columns instead of rows."),
     ("Retention report", "Report original and retained counts plus the exact rule. A smaller cleaner-looking table may have excluded a meaningful group.")],
    "Dropping rows is a policy, not a universal repair. If a report requires a known score, dropna(subset=['score']) makes that requirement explicit. "
    "Dropping on every column could unnecessarily exclude someone just because an optional comment is absent. how='all' and thresh answer different questions: remove entirely missing observations, or require enough known fields. "
    "Keep the discarded IDs accessible in the raw data and report the retention denominator. Never present the surviving mean as though it describes the original full population. "
    "A missing value is not proof that a person or event should be erased.",
    'known_scores = df.dropna(subset=["score"])\nnonempty = df.dropna(subset=["score","minutes"], how="all")\nenough = df.dropna(subset=["score","minutes"], thresh=1)',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C"], "score": [80, None, 90], "comment": [None, "ok", "ok"]})
    required = df.dropna(subset=["score"])
    every_column = df.dropna()
    print("Original:", len(df))
    print("Score required:", required["id"].tolist())
    print("Every column required:", every_column["id"].tolist())
    ''',
    "Optional comment नभएको A लाई score report बाट हटाउन आवश्यक थिएन। subset ले कुन field चाहिएको हो स्पष्ट बनायो।",
    'df.dropna() for every report without checking optional fields',
    'Specify required columns and report exclusions',
    "A global rule can discard valid observations for irrelevant missing fields.",
    "Retain rows with at least one of score/minutes known, then print original and retained IDs.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "C"], "score": [80, None, None], "minutes": [None, 30, None]})
    retained = df.dropna(subset=["score", "minutes"], thresh=1)
    print(df["id"].tolist(), retained["id"].tolist())
    ''',
    "Drop only rows missing both checked measurements using how='all'.",
    '''
    import pandas as pd
    df = pd.DataFrame({"a": [1, None, None], "b": [None, 2, None]}, index=["A", "B", "C"])
    print(df.dropna(how="all").index.tolist())
    print("Raw rows:", len(df))
    ''',
    "Drop by a declared requirement and report retention; preserve the raw population for later review.",
    [("Which limits dropping to score missingness?", "subset=['score']", "axis=1 alone", "sort_index", "subset defines the checked fields."),
     ("What does thresh=1 require?", "At least one known checked value", "Exactly one missing value", "All columns missing", "thresh counts nonmissing values.")])

lesson(0, "3. Filling with provenance, not pretending to observe",
    "Compare constant and median filling while preserving an imputation flag.",
    [("fillna; median", "fillna returns values with missing entries filled under your policy. median is the middle observed value; an even count averages the two middle values and may produce a fraction."),
     ("Imputation flag", "A Boolean flag records which values were estimated rather than observed. Compute it before filling; otherwise provenance is lost."),
     ("All-missing and leakage policy", "No observed values means no data-derived median. In predictive work, learn fills from training data only and reuse them for validation/test data; otherwise information can leak.")],
    "A fill is an estimate or explicit default, not a recovered observation. Filling a missing score with zero claims a different result from median filling. "
    "Use a domain rule and keep a score_was_missing flag so downstream readers can distinguish known scores from estimates. "
    "Integer storage can reject a fractional median; use an appropriate nullable float dtype when fractional estimates are allowed. "
    "An all-missing column cannot supply its own median. Require another justified source or stop. The following comparison is a descriptive exercise, not an instruction to median-fill every future dataset.",
    'was_missing = scores.isna()\nmedian = scores.median()\nif pd.isna(median): raise ValueError("No observed median")\nfilled = scores.fillna(median)',
    '''
    import pandas as pd
    scores = pd.Series([40, pd.NA, 90], dtype="Float64")
    flag = scores.isna()
    zero = scores.fillna(0)
    median = scores.fillna(scores.median())
    print("Observed mean:", float(scores.mean()))
    print("Zero-fill mean:", round(float(zero.mean()), 2))
    print("Median-fill:", median.tolist())
    print("Estimated flags:", flag.tolist())
    ''',
    "Zero fill गर्दा mean बदलियो। Median fill पनि assumption हो। Flag राखेकाले कुन value अनुमान गरिएको हो छुट्याउन सकिन्छ।",
    'Fill first, then call isna to discover estimated values',
    'Save the missing mask before filling',
    "After filling, isna cannot tell which values were originally missing.",
    "Fill [10,missing,21] with its observed median using Float64 and preserve the flag.",
    '''
    import pandas as pd
    scores = pd.Series([10, pd.NA, 21], dtype="Float64")
    flag = scores.isna()
    print(scores.fillna(scores.median()).tolist(), flag.tolist())
    ''',
    "Reject data-derived median filling for an all-missing column.",
    '''
    import pandas as pd
    scores = pd.Series([pd.NA, pd.NA], dtype="Float64")
    if pd.isna(scores.median()):
        print("Stop: no observed values for a median")
    ''',
    "Treat fills as estimates, preserve flags, choose a compatible dtype and handle the no-observation case.",
    [("Is a filled value a known recovered observation?", "No", "Always", "Only median fills", "Imputation supplies an assumption."),
     ("Can an all-missing column estimate its own median?", "No", "Always zero", "Only with Int64", "There are no observed values to order.")])

lesson(0, "4. Interpolation and three-strategy comparison",
    "Use interpolation only with a meaningful order and compare drop/fill/interpolate effects.",
    [("interpolate; method; limit_area", "Default linear interpolation uses equally spaced positions, not arbitrary labels. limit_area='inside' fills gaps bounded by known values and leaves unbounded edges missing."),
     ("ffill; bfill; limit", "ffill carries earlier observations forward, bfill carries later ones backward, and limit bounds runs of filled entries. These methods assume carrying a value is meaningful; bfill can leak future information."),
     ("Time-aware interpolation preview", "method='time' uses elapsed time on a suitable DatetimeIndex. Day3 introduces explicit date parsing; Week30 expands time-indexed analysis.")],
    "Interpolation estimates between known points. It makes sense for some ordered measurements, not for random student IDs or arbitrary category codes. "
    "Linear interpolation assumes equal position spacing unless you choose a different method. Use inside-only filling when you do not justify extrapolating beyond observed endpoints. "
    "Forward filling is another assumption: it treats the last known value as still applicable, possibly with a maximum gap. "
    "Compare strategies on one small fictional sequence and report how many values each uses. A smoother line or complete table is not proof that the missing truth was recovered.",
    's.interpolate(method="linear", limit_area="inside")\ns.ffill(limit=1)\n# Compare retained counts, estimated positions and remaining gaps',
    '''
    import pandas as pd
    s = pd.Series([None, 10.0, None, 30.0, None])
    print("Drop:", s.dropna().tolist())
    print("Median fill:", s.fillna(s.median()).tolist())
    interpolated = s.interpolate(limit_area="inside")
    print("Known/interpolated:", interpolated.loc[interpolated.notna()].tolist())
    print("Remaining gaps:", interpolated.isna().tolist())
    ''',
    "बीचको gap मात्रै estimate भयो। सुरु/अन्त्यमा observations ले नघेरेका gaps अझै missing छन्। क्रमको अर्थ नभएको data मा interpolation नगर्नु।",
    'Interpolate scores merely because student IDs are sorted',
    'Interpolate only when order/spacing and measurement meaning justify it',
    "Student identity order is not a continuous measurement axis.",
    "Interpolate [0,missing,20] and compare estimated flags with the original observed flags.",
    '''
    import pandas as pd
    s = pd.Series([0.0, None, 20.0])
    result = s.interpolate(limit_area="inside")
    print(result.tolist())
    print((s.isna() & result.notna()).tolist())
    ''',
    "Forward-fill at most one consecutive missing value, leaving later gaps missing.",
    '''
    import pandas as pd
    s = pd.Series([5.0, None, None, 8.0])
    result = s.ffill(limit=1)
    print(result.isna().tolist())
    print(result.loc[result.notna()].tolist())
    ''',
    "Drop, fill and interpolate change assumptions and populations differently. Record the strategy and estimated positions.",
    [("What does inside-only interpolation avoid filling?", "Unbounded edge gaps", "All internal gaps", "Known zeros", "Both bounding observations must exist."),
     ("Does default linear interpolation understand arbitrary ID spacing?", "No", "Always", "Only numeric IDs", "It treats positions as equally spaced.")])

lesson(1, "1. Exact duplicates versus repeated entities",
    "Distinguish duplicate full rows from repeated identity keys and choose keep semantics.",
    [("duplicated(subset, keep)", "duplicated marks repeats under chosen fields. keep='first' keeps the first unmarked, keep='last' keeps the last, and keep=False marks every member of a repeated group."),
     ("drop_duplicates", "drop_duplicates removes repeated rows under the chosen key policy; it does not decide which observation is business-correct. Row indexes are not used to identify duplicates.")],
    "Two identical rows might be an accidental reimport, or two legitimate events that happen to look the same. You need an identity contract to decide. "
    "A repeated student ID is not necessarily an exact duplicate: it could be a later update. Check complete rows and entity keys separately. "
    "keep specifies which row survives in the current order; it does not automatically understand timestamps. "
    "Always retain the original dataset and report the removed record references. Use keep=False to inspect all members before choosing a rule, not simply to delete them all.",
    'df.duplicated()\ndf.duplicated(subset=["id"], keep=False)\ndf.drop_duplicates(subset=["id"], keep="last")',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "001", "002", "001"], "score": [80, 90, 70, 80]})
    print("Exact after first:", df.duplicated().tolist())
    print("Repeated IDs all members:", df.duplicated(subset=["id"], keep=False).tolist())
    print("Exact rows retained:", len(df.drop_duplicates()))
    ''',
    "001 का सबै rows एउटै होइनन्; score90 update हुन सक्छ। Exact duplicate check र ID duplicate check फरक प्रश्न हुन्।",
    'Delete every repeated ID without examining updates',
    'Define identity and retention policy before drop_duplicates',
    "A repeated key can represent a valid update or a repeated event.",
    "Keep the last occurrence by current input order for repeated IDs, explicitly stating that this is not timestamp order.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B", "A"], "score": [80, 70, 90]})
    print(df.drop_duplicates(subset=["id"], keep="last").to_dict(orient="records"))
    ''',
    "Show that differing row indexes do not prevent full-row duplicate detection.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "001"], "score": [80, 80]}, index=[10, 99])
    print(df.duplicated().tolist())
    ''',
    "A duplicate policy needs a key and a meaningful survival rule; indexes alone are not identity.",
    [("Does duplicated compare the row index by default?", "No", "Always", "Only for strings", "It compares the selected data fields."),
     ("Does keep='last' automatically mean newest timestamp?", "No", "Always", "Only with IDs", "It means last in the current row order.")])

lesson(1, "2. Keep the newest valid update deterministically",
    "Sort parsed timestamps and a tie-break field before deduplicating entity keys.",
    [("to_datetime format preview", "to_datetime converts text to dates/timestamps. An explicit format avoids guessing; errors='coerce' creates NaT for unparseable values, which must be audited. Day3 teaches this fully."),
     ("Source-record tie-break", "A preserved source-record number defines input order explicitly. Here newer date wins; equal-date ties choose the later input record. That is a declared example policy, not a universal rule.")],
    "To keep the latest update, first establish that the timestamp is valid and represents the same time convention. Then sort the chosen key by descending time. "
    "A stable or explicit secondary tie-break makes equal timestamps reproducible. In this daily-date fixture, the larger source-record number wins a same-day tie. "
    "Invalid dates must be separated before choosing a winner; otherwise a missing timestamp could accidentally retain or discard a record. "
    "The selected rows remain traceable to their input records. For real event histories you may need all updates rather than one latest snapshot.",
    'valid = df.loc[df["updated"].notna()]\nordered = valid.sort_values(["id","updated","source"], ascending=[True,False,False])\nlatest = ordered.drop_duplicates("id", keep="first")',
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001", "001", "002", "001"], "score": [80, 90, 70, 95],
                       "updated": ["2026-01-01", "2026-01-03", "2026-01-02", "2026-01-03"],
                       "source": [1, 2, 3, 4]})
    df["updated"] = pd.to_datetime(df["updated"], format="%Y-%m-%d", errors="coerce")
    valid = df.loc[df["updated"].notna()]
    latest = valid.sort_values(["id", "updated", "source"], ascending=[True, False, False]).drop_duplicates("id")
    print(latest[["id", "score", "source"]].to_dict(orient="records"))
    ''',
    "001 को newer date छानियो। उही date का दुई updates हुँदा source4 जित्यो, किनकि policy मा later input record भनिएको छ।",
    'drop_duplicates("id", keep="last") on unsorted file and call it latest',
    'Validate dates, sort chronologically and define ties before deduplicating',
    "File order and timestamp order may differ.",
    "Given out-of-order updates, retain the newest valid record for each ID.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "A", "B"], "score": [95, 80, 70],
                       "updated": ["2026-02-03", "2026-02-01", "2026-02-02"]})
    df["updated"] = pd.to_datetime(df["updated"], format="%Y-%m-%d")
    latest = df.sort_values(["id", "updated"], ascending=[True, False]).drop_duplicates("id")
    print(latest[["id", "score"]].to_dict(orient="records"))
    ''',
    "Identify an invalid timestamp before it can participate in newest-record selection.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "A"], "updated": ["bad", "2026-02-01"]})
    parsed = pd.to_datetime(df["updated"], format="%Y-%m-%d", errors="coerce")
    print("Invalid records:", (parsed.isna()).tolist())
    print("Eligible IDs:", df.loc[parsed.notna(), "id"].tolist())
    ''',
    "Newest means newest valid time under a declared tie policy, not simply the final row of a file.",
    [("What must happen before chronological deduplication?", "Parse and validate timestamps", "Delete the raw CSV", "Fill invalid dates with today", "Sorting bad text does not establish valid chronological order."),
     ("How should equal-timestamp ties be resolved?", "With an explicit rule", "Always randomly", "By silently dropping all rows", "Reproducible choices need a stated tie-break.")])

lesson(1, "3. Normalize categories without inventing recognition",
    "Map known aliases to canonical categories and expose unknown values.",
    [("casefold; strip", "strip removes surrounding whitespace. casefold supports caseless matching more fully than lower for some scripts; do not apply it to case-sensitive IDs/passwords."),
     ("Alias map; unknown mask", "An alias dictionary translates known variants to canonical categories. A nonmissing cleaned token with no mapping is unknown, not automatically missing or a recognized default.")],
    "Nepal, NP and a spaced lowercase spelling may refer to one category under your declared mapping. Clean formatting, then map only known aliases. "
    "A typo or an unexpected country is not proof that it means Nepal. Preserve the source token and put unknown values in a review list. "
    "Before collapsing categories, check whether the distinctions matter: case-sensitive product IDs and account names may not permit casefolding. "
    "A clean category column should have a known vocabulary and a separate unknown policy. Normalization can also expose duplicates that were hidden by spelling differences, so decide operation order deliberately.",
    'tokens = series.str.strip().str.casefold()\ncanonical = tokens.map({"np":"NP","nepal":"NP","jp":"JP","japan":"JP"})\nunknown = tokens.notna() & canonical.isna()',
    '''
    import pandas as pd
    raw = pd.Series([" NP ", "Nepal", "JAPAN", "Npeal", None], dtype="string")
    tokens = raw.str.strip().str.casefold()
    canonical = tokens.map({"np": "NP", "nepal": "NP", "jp": "JP", "japan": "JP"})
    unknown = tokens.notna() & canonical.isna()
    print("Known:", canonical.loc[canonical.notna()].tolist())
    print("Unknown raw:", raw.loc[unknown].tolist())
    print("Original missing:", raw.isna().tolist())
    ''',
    "Npeal typo जस्तो देखिए पनि स्वतः Nepal बनाइएन। Known alias मात्रै map भयो। Unknown र original missing छुट्टै हुन्।",
    'Fill every unmapped category with "NP"', 'Flag unmapped nonmissing tokens for review',
    "Unknown text is not evidence of membership in the default category.",
    "Normalize beginner aliases B/basic/beginner and expose an unknown advanced label.",
    '''
    import pandas as pd
    raw = pd.Series([" B ", "basic", "BEGINNER", "advanced"], dtype="string")
    token = raw.str.strip().str.casefold()
    mapped = token.map({"b": "Beginner", "basic": "Beginner", "beginner": "Beginner"})
    print(mapped.loc[mapped.notna()].tolist())
    print(raw.loc[token.notna() & mapped.isna()].tolist())
    ''',
    "Show why normalizing an ID is different from casting it to a number.",
    '''
    import pandas as pd
    raw = pd.Series([" 001 ", "002"], dtype="string")
    cleaned = raw.str.strip()
    print(cleaned.tolist())
    print(raw.tolist())
    ''',
    "Normalize only permitted differences, preserve IDs as text and review unknown categories explicitly.",
    [("Does dictionary mapping prove an unknown typo's intended category?", "No", "Always", "Only with casefold", "The dictionary only recognizes supplied aliases."),
     ("Should casefold be applied to every identity field?", "No", "Always", "Only before deduplication", "Some identities distinguish case.")])

lesson(1, "4. Audit changes and test repeatability",
    "Record before/after values and distinguish deterministic cleaning from unsupported assumptions.",
    [("Cell-change audit", "An audit records source-record identity, field, old value, new value and rule. Missing-to-missing should not be counted as a change; missing comparisons need explicit handling."),
     ("Idempotence", "A cleaning transformation is idempotent when applying it again gives the same result. This is useful for formatting rules, but does not prove their business assumptions are correct."),
     ("pipe", "pipe passes a DataFrame into a function, supporting an explicit sequence of stages. Each stage should return a result and keep mutation behavior understandable.")],
    "A clean table without a report is difficult to trust. Count and identify replacements, removals, imputed cells and unrecognized values. "
    "Use stable source references rather than whichever index happens to remain after filtering. Normalize comparisons so two missing markers do not count as a new edit. "
    "Test repeatability: stripping already-stripped text should change nothing on the second run. This does not prove the rule was appropriate for that field; it only detects some implementation drift. "
    "pipe can make stages readable, but readability still depends on small functions with clear input/output contracts.",
    'cleaned = raw.pipe(normalize_text)\nagain = cleaned.pipe(normalize_text)\nassert cleaned.equals(again)\n# Log changed fields with source references',
    '''
    import pandas as pd
    def normalize(df):
        out = df.copy()
        out["name"] = out["name"].str.strip()
        return out
    raw = pd.DataFrame({"name": pd.Series([" Asha ", "Bina"], dtype="string")})
    clean = raw.pipe(normalize)
    changes = [{"record": i + 1, "old": raw.loc[i, "name"], "new": clean.loc[i, "name"]}
               for i in raw.index if raw.loc[i, "name"] != clean.loc[i, "name"]]
    print(changes)
    print("Repeatable:", clean.equals(clean.pipe(normalize)))
    print("Raw:", raw["name"].tolist())
    ''',
    "Record1 को नाम मात्रै बदलियो। फेरि normalize गर्दा उही result आयो। Raw नाम बचेकाले rule गलत भए फर्काएर अर्को निर्णय गर्न सकिन्छ।",
    'Claim a rule is correct solely because it is idempotent',
    'Check both repeatability and field-specific business meaning',
    "A consistently wrong mapping can also be idempotent.",
    "Write a pure strip/casefold function and check repeatability on nullable category text.",
    '''
    import pandas as pd
    def canonical_text(s):
        return s.str.strip().str.casefold()
    raw = pd.Series([" NP ", "Japan", pd.NA], dtype="string")
    cleaned = canonical_text(raw)
    print(cleaned.loc[cleaned.notna()].tolist())
    print(cleaned.equals(canonical_text(cleaned)))
    ''',
    "Count a missing-to-missing result as unchanged using a null-safe comparison.",
    '''
    import pandas as pd
    before = pd.Series([" A ", pd.NA], dtype="string")
    after = before.str.strip()
    same = before.eq(after).fillna(False) | (before.isna() & after.isna())
    print("Changed:", (~same).tolist())
    ''',
    "Log changes with source identities, keep functions explicit and test repeatability plus semantic correctness.",
    [("What does idempotence mean?", "A second application gives the same result", "All values become zero", "Every rule is business-correct", "Repeat application should not keep changing the output."),
     ("Should missing-to-missing count as an edit?", "No", "Always", "Only for dates", "No new value was supplied.")])

lesson(2, "1. Numeric conversion with a failure mask",
    "Convert declared quantities, preserve identifiers and audit failed/nonfinite values.",
    [("to_numeric; errors='raise'/'coerce'", "raise stops on invalid text; coerce produces a missing conversion result. Detect nonmissing source tokens that became missing so errors do not disappear silently."),
     ("np.isfinite; nullable Float64", "isfinite identifies finite numerical values separately from parsing success. Float64 supports nullable decimal quantities. Infinity may parse successfully but is not a valid finite score."),
     ("astype is not a cleaning policy", "astype requests a dtype conversion; it does not decide how to interpret currency signs, commas, IDs or bad text. Specify text conventions and validate before narrowing types.")],
    "Convert only fields declared numerical by the schema. An ID made of digits remains text. A score containing 'oops' should not become an ordinary missing response without an error record. "
    "Build a failure mask from known source values and missing conversion results. Check finiteness separately: 'inf' can parse even though it is not a finite observation. "
    "Only remove commas or symbols under a known locale/format rule; a decimal comma and a thousands comma have different meanings. "
    "Do not use errors='coerce' as permission to ignore failures. It is a mechanism for isolating them so the pipeline can reject or quarantine them deliberately.",
    'numeric = pd.to_numeric(tokens, errors="coerce").astype("Float64")\nfailed = tokens.notna() & numeric.isna()\nfinite = np.isfinite(numeric.to_numpy(dtype=float, na_value=np.nan))',
    '''
    import numpy as np
    import pandas as pd
    raw = pd.Series(["80", "oops", None, "inf"], dtype="string")
    numeric = pd.to_numeric(raw, errors="coerce").astype("Float64")
    failed = raw.notna() & numeric.isna()
    finite = np.isfinite(numeric.to_numpy(dtype=float, na_value=np.nan))
    print("Failed text:", raw.loc[failed].tolist())
    print("Finite decisions:", finite.tolist())
    print("Originally missing:", raw.isna().tolist())
    ''',
    "oops parse भएन, inf parse भए पनि finite भएन। Source missing र conversion failure एउटै घटना होइनन्; छुट्टै report चाहिन्छ।",
    'Coerce bad text, fill it with zero and report no errors',
    'Audit failed conversions and validate finite/domain constraints',
    "A data error is not a genuine score of zero.",
    "Convert quantities ['10','20','bad']; show only valid quantities and failed source tokens.",
    '''
    import pandas as pd
    raw = pd.Series(["10", "20", "bad"], dtype="string")
    values = pd.to_numeric(raw, errors="coerce")
    print(values.loc[values.notna()].tolist())
    print(raw.loc[raw.notna() & values.isna()].tolist())
    ''',
    "Reject a fractional score before storing in nullable Int64; do not truncate it.",
    '''
    import pandas as pd
    raw = pd.Series(["10", "10.5"], dtype="string")
    numbers = pd.to_numeric(raw, errors="raise")
    whole = numbers.mod(1).eq(0)
    print("Whole-number decisions:", whole.tolist())
    print(numbers.loc[whole].astype("Int64").tolist())
    ''',
    "Conversion success, finiteness and domain validity are separate checks; identifiers remain text.",
    [("Can infinity parse as a numeric value?", "Yes", "Never", "Only with IDs", "Parsing does not ensure a finite domain."),
     ("What should follow errors='coerce'?", "Audit conversion failures", "Assume all values were valid", "Delete the source", "Compare known source tokens with missing converted results.")])

lesson(2, "2. Dates: format, failures and timezone meaning",
    "Parse explicit date conventions and normalize actual offset timestamps to UTC.",
    [("to_datetime; format; NaT", "format states the expected pattern; errors='coerce' maps unparseable dates to NaT. Audit failed nonmissing tokens and calendar validity."),
     ("utc=True", "For timestamps with supplied timezone offsets, utc=True normalizes instants to UTC. For naive timestamps it assumes UTC; do not use that assumption unless the source contract says it is correct."),
     ("dt.strftime; dt accessor", "The dt accessor provides datetime operations; strftime formats valid dates/timestamps. Day30 develops date components and time series in depth.")],
    "01/02/2026 could mean January2 or February1. Guessing a convention can create a valid but wrong date. State the source format and test an impossible date like February30. "
    "Calendar dates, local wall-clock times and timezone-aware instants are different types of information. "
    "If offsets are included, UTC normalization lets you compare the same instant across regions. If a naive timestamp means local Tokyo time, setting utc=True directly would reinterpret it as UTC incorrectly; establish/localize the source timezone first. "
    "For this week's cleaning project, updated is a simple YYYY-MM-DD calendar date. It does not claim within-day ordering.",
    'dates = pd.to_datetime(tokens, format="%Y-%m-%d", errors="coerce")\ninstants = pd.to_datetime(offset_tokens, utc=True)\ndates.dt.strftime("%Y-%m-%d")',
    '''
    import pandas as pd
    raw = pd.Series(["2026-02-01", "2026-02-30", None], dtype="string")
    dates = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
    print("Failed dates:", raw.loc[raw.notna() & dates.isna()].tolist())
    print("Valid:", dates.loc[dates.notna()].dt.strftime("%Y-%m-%d").tolist())
    offsets = pd.Series(["2026-01-01T09:00:00+09:00", "2026-01-01T00:00:00+00:00"])
    utc = pd.to_datetime(offsets, utc=True)
    print("Same instant:", utc.iloc[0] == utc.iloc[1])
    ''',
    "February30 invalid भयो। Tokyo offset सहितको 09:00 र UTC00:00 एउटै instant हुन्। Naive time लाई timezone थाहा नपाई UTC नमान्नु।",
    'Let pandas guess ambiguous date conventions for every source',
    'Declare the date format and timezone contract explicitly',
    "A successful parse can still mean the wrong calendar date or instant.",
    "Parse 01/02/2026 using day/month/year and print its unambiguous ISO date.",
    '''
    import pandas as pd
    dates = pd.to_datetime(pd.Series(["01/02/2026"]), format="%d/%m/%Y")
    print(dates.dt.strftime("%Y-%m-%d").tolist())
    ''',
    "Separate originally missing dates from invalid nonmissing date text.",
    '''
    import pandas as pd
    raw = pd.Series([None, "not-a-date", "2026-01-01"], dtype="string")
    dates = pd.to_datetime(raw, format="%Y-%m-%d", errors="coerce")
    print("Originally missing:", raw.isna().tolist())
    print("Failed known:", (raw.notna() & dates.isna()).tolist())
    ''',
    "Dates need a format and time meaning. Preserve failures and never assume a naive time's timezone without evidence.",
    [("Can 01/02/2026 be ambiguous?", "Yes", "No", "Only when missing", "Different conventions assign different dates."),
     ("Does utc=True correctly infer every naive source timezone?", "No", "Always", "Only for Japanese text", "It treats naive values as UTC rather than discovering a local timezone.")])

lesson(2, "3. Nullable integers and categorical vocabularies",
    "Choose types after validation and expose unknown category values before casting.",
    [("CategoricalDtype; ordered", "CategoricalDtype defines allowed categories and optional ordering. ordered=True uses the declared category order for comparisons/sorting, not alphabetical order."),
     ("Unknown category conversion", "Casting a token outside a declared categorical vocabulary can turn it into missing. Detect unknown tokens first so this does not silently erase the source error."),
     ("convert_dtypes preview", "convert_dtypes attempts convenient nullable type choices, but cannot establish business meaning. A declared ID/quantity/date schema remains necessary.")],
    "Types should express the intended domain. Whole-number counts can use Int64 when missing is possible; decimal measurements require a float or another suitable representation. "
    "Categorical types express a fixed vocabulary such as beginner/intermediate/advanced, optionally with a meaningful order. "
    "Validate aliases and unknown values before casting. An unexpected category becoming missing during conversion is not the same as a person leaving the field blank. "
    "Automatic dtype helpers are useful after inspection, but they do not know that 001 is an identifier or that advanced should rank above intermediate. Store those decisions in the schema.",
    'kind = pd.CategoricalDtype(["beginner","intermediate","advanced"], ordered=True)\nunknown = raw.notna() & ~raw.isin(kind.categories)\nvalid = raw.loc[~unknown].astype(kind)',
    '''
    import pandas as pd
    raw = pd.Series(["advanced", "beginner", "expert", None], dtype="string")
    kind = pd.CategoricalDtype(["beginner", "intermediate", "advanced"], ordered=True)
    unknown = raw.notna() & ~raw.isin(kind.categories)
    print("Unknown:", raw.loc[unknown].tolist())
    valid = raw.loc[~unknown].astype(kind)
    print("Sorted known:", valid.loc[valid.notna()].sort_values().tolist())
    print("Originally missing:", raw.isna().tolist())
    ''',
    "expert allowed category थिएन, cast गर्नुअघि छुट्टै देखायौँ। Beginner र advanced को order हाम्रो vocabulary ले तय गर्‍यो।",
    'Cast unknown labels to category, then call them ordinary missing responses',
    'Report unknown source labels before categorical conversion',
    "Casting may erase the distinction between invalid text and no response.",
    "Define low/medium/high as ordered categories and sort high/low/medium accordingly.",
    '''
    import pandas as pd
    kind = pd.CategoricalDtype(["low", "medium", "high"], ordered=True)
    s = pd.Series(["high", "low", "medium"], dtype=kind)
    print(s.sort_values().tolist())
    ''',
    "Store missing whole counts without turning identifiers into numbers.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": pd.Series(["001", "002"], dtype="string"),
                       "count": pd.Series([10, pd.NA], dtype="Int64")})
    print(df["id"].tolist(), str(df["count"].dtype), df["count"].isna().tolist())
    ''',
    "Validate first, then choose types that encode your declared domain and missing policy.",
    [("Does an ordered category use its declared order?", "Yes", "Always alphabetical", "Only numeric IDs", "The vocabulary order defines ranking."),
     ("Should unknown categories be detected before casting?", "Yes", "Never", "Only with uppercase names", "Casting can turn unknown tokens into missing.")])

lesson(2, "4. Staged schema validation",
    "Validate required columns, conversion failures and ranges before declaring a dataset clean.",
    [("Schema validation", "A schema describes required columns, identity rules, storage types, allowed categories, numerical bounds and date conventions."),
     ("Quarantine", "Quarantine separates invalid records for review while preserving their source references and reasons. It does not invent a repair or delete the raw file."),
     ("Validation order", "Normalize permitted text differences, convert types, audit failures, check domains, then apply identity/fill rules. Later stages must not hide earlier invalidity.")],
    "Do not call a table clean solely because numeric columns no longer contain text. A parsed score of150 is outside the declared0..100 domain; a parsed date may still belong to the wrong time convention. "
    "Make each rule understandable and testable. Required names cannot be blank, IDs have an expected format, regions must be recognized, and scores must be finite and within bounds. "
    "Separate a genuine blank score from a failed score conversion. Only the former is eligible for a later fill policy. "
    "Keep bad records reviewable with reasons. If the source schema is missing or changes unexpectedly, stop rather than guessing which columns to use.",
    'check required columns\nnormalize declared text differences\nparse values and audit failures\nvalidate finite/range/category/identity rules\nquarantine invalid rows before fills/deduplication',
    '''
    import numpy as np
    import pandas as pd
    raw = pd.DataFrame({"id": ["001", "002", "003"], "score": ["80", "150", "oops"]})
    numeric = pd.to_numeric(raw["score"], errors="coerce")
    finite = pd.Series(np.isfinite(numeric), index=raw.index)
    valid = finite & numeric.between(0, 100).fillna(False)
    print("Accepted:", raw.loc[valid, "id"].tolist())
    print("Review:", raw.loc[~valid, "id"].tolist())
    print("Source scores:", raw["score"].tolist())
    ''',
    "150 parse भएको भए पनि score domain बाहिर थियो। oops parse भएन। दुवैलाई fill गरेर valid बनाएको छैन।",
    'Fill every failed score conversion with the median before validation',
    'Distinguish blank source fields from invalid nonblank tokens',
    "Filling errors hides evidence and makes invalid data appear acceptable.",
    "Reject a missing required column before accessing values.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["001"]})
    required = {"id", "score"}
    missing_columns = sorted(required - set(df.columns))
    print("Missing schema fields:", missing_columns)
    ''',
    "Validate exact three-ASCII-digit IDs while keeping their leading zeros.",
    '''
    import pandas as pd
    ids = pd.Series(["001", "12", "A03", None], dtype="string")
    valid = ids.str.fullmatch(r"[0-9]{3}").fillna(False)
    print(valid.tolist())
    print(ids.loc[valid].tolist())
    ''',
    "A clean dataset satisfies an explicit schema; parse failures and domain failures stay reviewable.",
    [("Does parsing 150 make it a valid score under0..100?", "No", "Always", "Only as Float64", "Successful conversion does not satisfy the domain rule."),
     ("What is quarantine for?", "Reviewing invalid records with reasons", "Guessing replacement values", "Deleting the original file", "It keeps invalid observations traceable.")])

lesson(3, "1. Whitespace, case and Unicode boundaries",
    "Normalize permitted name/category formatting without deleting meaningful text.",
    [("str.replace; regex=True/False", "replace performs literal replacement with regex=False or regular-expression substitution with regex=True. State the mode explicitly."),
     ("Unicode normalization", "str.normalize('NFC') can combine equivalent Unicode sequences without changing their intended text. NFKC is stronger compatibility normalization and may change meaningful distinctions."),
     ("Internal whitespace policy", "Collapsing repeated whitespace can suit display names but may be wrong for source code, addresses or exact IDs. Formatting rules are field-specific.")],
    "strip removes whitespace only at the edges. A display name can also contain repeated internal spaces; collapse them only if your contract permits it. "
    "Normalize case for recognized category matching, not for every user name or password. Unicode text can have equivalent spellings encoded with different code-point sequences; NFC is useful when that distinction should not create separate categories. "
    "Do not strip accents or remove every non-ASCII character from multilingual names. "
    "A clean field should preserve meaning and retain the raw version. Document which formatting distinctions are intentionally collapsed.",
    'names.str.normalize("NFC").str.strip().str.replace(r"\\s+", " ", regex=True)\ncategories.str.strip().str.casefold()',
    '''
    import pandas as pd
    raw = pd.Series(["  Asha   Rai ", "Bina\\tShah", "Cafe\\u0301"], dtype="string")
    clean = raw.str.normalize("NFC").str.strip().str.replace(r"\\s+", " ", regex=True)
    print(clean.tolist())
    print("Raw first:", raw.iloc[0])
    ''',
    "Name भित्रको repeated whitespace single space बन्यो। Café को accent हटाइएको छैन। Exact text चाहिने field मा यही rule स्वतः लागू नगर्नु।",
    'Remove every character outside A-Z from names',
    'Use permitted whitespace/Unicode normalization and preserve multilingual letters',
    "Deleting non-ASCII text damages valid names.",
    "Normalize spaced category text with strip/casefold while preserving missing entries.",
    '''
    import pandas as pd
    raw = pd.Series([" Nepal ", "JAPAN", pd.NA], dtype="string")
    clean = raw.str.strip().str.casefold()
    print(clean.loc[clean.notna()].tolist(), clean.isna().tolist())
    ''',
    "Show that strip alone does not collapse internal spaces.",
    '''
    import pandas as pd
    s = pd.Series([" Asha   Rai "], dtype="string")
    print(s.str.strip().tolist())
    print(s.str.strip().str.replace(r"\\s+", " ", regex=True).tolist())
    ''',
    "Normalize only meaningful equivalences and preserve multilingual text plus the raw source.",
    [("Does strip collapse internal repeated spaces?", "No", "Always", "Only tabs", "It removes leading/trailing whitespace."),
     ("Should names lose all non-ASCII letters?", "No", "Always", "Only for matching", "Those letters can be essential to valid names.")])

lesson(3, "2. Literal replacements versus regex rules",
    "Replace only declared syntax and test characters with special regex meaning.",
    [("Regular expression metacharacter", "Characters such as . have special regex meaning. regex=False matches their literal text; escape special characters when a regex is genuinely intended."),
     ("Anchors ^ and $", "^ anchors the start and $ the end of a pattern. Anchors help avoid matching a valid-looking substring inside invalid surrounding text."),
     ("Exact source format", "A US-style thousands comma and a decimal comma require different interpretations. Use explicit source conventions before removing punctuation.")],
    "Replacement can quietly corrupt data when its matching mode is wrong. A dot in regex means almost any character, so replacing '.' with regex=True is not the same as removing literal dots. "
    "Use literal mode for fixed tokens and regex mode for a stated pattern such as runs of whitespace. "
    "When cleaning numbers, know the locale first: 1,234 may mean1234, while 1,23 may mean1.23 under another convention. "
    "The exercise accepts only a declared whole-number comma-grouping format before removing commas. Invalid grouping remains visible for review instead of being silently converted.",
    's.str.replace(".", "", regex=False)\nvalid = s.str.fullmatch(r"[0-9]{1,3}(,[0-9]{3})+")\n# Only permitted comma-grouped integer tokens may be normalized',
    '''
    import pandas as pd
    s = pd.Series(["v1.2", "abc"], dtype="string")
    print("Literal:", s.str.replace(".", "", regex=False).tolist())
    print("Regex dot:", s.str.replace(".", "", regex=True).tolist())
    ''',
    "Literal dot हटाउँदा v12 भयो। Regex dot ले अक्षरहरू समेत match गर्‍यो। replace मा mode सधैँ स्पष्ट लेख्नु।",
    's.str.replace(".", "", regex=True) to remove only punctuation dots',
    's.str.replace(".", "", regex=False)',
    "Regex dot matches characters beyond a literal dot.",
    "Recognize valid comma-grouped whole numbers ['1,234','12,345','1,23']; convert only the recognized tokens.",
    '''
    import pandas as pd
    raw = pd.Series(["1,234", "12,345", "1,23"], dtype="string")
    valid = raw.str.fullmatch(r"[0-9]{1,3}(,[0-9]{3})+").fillna(False)
    tokens = raw.loc[valid].str.replace(",", "", regex=False)
    print(pd.to_numeric(tokens).tolist())
    print("Review:", raw.loc[~valid].tolist())
    ''',
    "Remove a literal currency prefix only after recognizing the declared complete token format.",
    '''
    import pandas as pd
    raw = pd.Series(["NPR 100", "NPR 200", "USD 300"], dtype="string")
    valid = raw.str.fullmatch(r"NPR [0-9]+").fillna(False)
    clean = raw.loc[valid].str.replace("NPR ", "", regex=False)
    print(pd.to_numeric(clean).tolist(), raw.loc[~valid].tolist())
    ''',
    "Choose literal or regex replacement explicitly, validate the source format and keep unrecognized tokens.",
    [("What does regex dot normally match?", "A character other than newline", "Only a literal dot", "Only numbers", "Dot is a regex metacharacter."),
     ("Should every comma in numeric text simply be deleted?", "No", "Always", "Only before astype", "Its meaning depends on the source format/locale.")])

lesson(3, "3. contains, fullmatch and extract",
    "Separate finding a substring from validating a whole field and extracting structured parts.",
    [("str.contains; na", "contains finds a substring/pattern. regex=False uses literal text; na=False explicitly treats missing fields as not matching."),
     ("str.fullmatch", "fullmatch requires the entire string to match a pattern, useful for validating IDs. contains can find a valid fragment inside invalid surrounding text."),
     ("str.extract; capture group", "extract returns captured regex groups from a match. A capture group in parentheses identifies the desired part. Missing matches become missing results.")],
    "Searching and validating answer different questions. contains('NP',regex=False) can find NP anywhere, including inside a longer invalid code. "
    "fullmatch checks the whole field. extract retrieves a part of a matched structure, but extraction success alone does not establish the rest of the field's meaning. "
    "Use anchors or fullmatch when validating complete tokens. Handle missing text through an explicit na policy. "
    "These examples validate fictional order references; they do not claim that a small regex validates every real email, address or Unicode name.",
    's.str.contains("NP", regex=False, na=False)\nvalid = s.str.fullmatch(r"ORD-[0-9]{3}").fillna(False)\nnumber = s.loc[valid].str.extract(r"ORD-([0-9]{3})", expand=False)',
    '''
    import pandas as pd
    raw = pd.Series(["ORD-001", "xORD-002x", "ORD-ABC", None], dtype="string")
    contains = raw.str.contains("ORD-", regex=False, na=False)
    valid = raw.str.fullmatch(r"ORD-[0-9]{3}").fillna(False)
    number = raw.loc[valid].str.extract(r"ORD-([0-9]{3})", expand=False)
    print("Contains prefix:", contains.tolist())
    print("Full valid:", valid.tolist())
    print("Text number:", number.tolist())
    ''',
    "xORD-002x मा prefix भेटियो तर पूरा ID valid भएन। Extract गरेको001 लाई text नै राख्दा leading zero बच्यो।",
    'Use contains to prove a whole ID is valid',
    'Use fullmatch for the complete ID contract',
    "A valid substring can appear inside an invalid full field.",
    "Find literal dots in a nullable text Series without treating dot as a regex wildcard.",
    '''
    import pandas as pd
    s = pd.Series(["a.b", "ab", None], dtype="string")
    print(s.str.contains(".", regex=False, na=False).tolist())
    ''',
    "Extract a known LEVEL:beginner/intermediate/advanced token only after validating the whole pattern.",
    '''
    import pandas as pd
    s = pd.Series(["LEVEL:beginner", "LEVEL:advanced", "LEVEL:expert"], dtype="string")
    valid = s.str.fullmatch(r"LEVEL:(beginner|intermediate|advanced)").fillna(False)
    print(s.loc[valid].str.extract(r"LEVEL:(beginner|intermediate|advanced)", expand=False).tolist())
    print("Unknown:", s.loc[~valid].tolist())
    ''',
    "contains searches, fullmatch validates the whole token and extract retrieves stated components.",
    [("Does contains prove the whole field matches a schema?", "No", "Always", "Only with na=False", "It searches for matching parts."),
     ("What does a regex capture group identify?", "A part to extract", "An automatic database key", "A missing column", "Parentheses capture a specified portion of a match.")])

lesson(3, "4. Splitting structured fields and validating parts",
    "Split an explicitly delimited field without assuming every name/address has that structure.",
    [("str.split; n; expand", "split divides a string at a delimiter. n limits the number of splits; expand=True produces separate columns. Missing/absent parts still require checks."),
     ("Compound-field schema", "A compound field needs a known delimiter rule and component domains. Real person names or arbitrary addresses cannot safely be parsed by always splitting on the first space.")],
    "A declared region|level field is a reasonable splitting exercise because the delimiter and allowed values are specified. "
    "Do not transfer this assumption to names: many valid names have different numbers of parts and spaces. n=1 preserves any remaining delimiter in the second component, making an extra delimiter visible to validation. "
    "After splitting, strip permitted whitespace and validate each component against its vocabulary. Missing parts, unknown values and extra delimiters belong in a review list. "
    "The original compound token stays available for explaining every rejection.",
    'parts = s.str.split("|", n=1, expand=True, regex=False)\nregion = parts[0].str.strip()\nlevel = parts[1].str.strip()\nvalid = region.isin(...) & level.isin(...)',
    '''
    import pandas as pd
    raw = pd.Series(["NP|beginner", " JP | advanced ", "NP", "NP|beginner|extra"], dtype="string")
    parts = raw.str.split("|", n=1, expand=True, regex=False)
    region, level = parts[0].str.strip(), parts[1].str.strip()
    valid = region.isin(["NP", "JP"]) & level.isin(["beginner", "advanced"])
    print("Valid:", raw.loc[valid].tolist())
    print("Review:", raw.loc[~valid].tolist())
    ''',
    "Extra delimiter भएको token को दोस्रो part beginner|extra रह्यो र validation ले reject गर्‍यो। Split भएको भन्दैमा field valid भएको होइन।",
    'Split every person name into exactly first and last at one space',
    'Use a declared compound-field schema; preserve full names when no such schema exists',
    "Real names do not share one universal two-part structure.",
    "Split 'book:100' and 'pen:20' at a literal colon and parse the declared integer quantity part.",
    '''
    import pandas as pd
    s = pd.Series(["book:100", "pen:20"], dtype="string")
    parts = s.str.split(":", n=1, expand=True, regex=False)
    quantity = pd.to_numeric(parts[1], errors="raise")
    print(parts[0].tolist(), quantity.tolist())
    ''',
    "Reject a missing component in a declared region|level field.",
    '''
    import pandas as pd
    s = pd.Series(["NP|beginner", "JP|", "|advanced"], dtype="string")
    parts = s.str.split("|", n=1, expand=True, regex=False)
    valid = parts[0].isin(["NP", "JP"]) & parts[1].isin(["beginner", "advanced"])
    print(valid.tolist())
    ''',
    "A split is only structural parsing. Validate every part and avoid imposing arbitrary structures on real names.",
    [("Does successful splitting guarantee valid components?", "No", "Always", "Only with expand=True", "Vocabulary and missingness rules still need checking."),
     ("What does n=1 limit?", "The number of splits", "The number of input rows", "The allowed categories", "Only the first delimiter splits the field.")])

lesson(4, "1. Domain errors versus statistical surprises",
    "Validate finite values and known bounds before applying statistical outlier rules.",
    [("Domain constraint", "A domain constraint comes from field meaning: a score here is finite and between0 and100. A statistical rarity is a different kind of check."),
     ("clip", "clip caps values at chosen bounds. It changes observations; use it only under an explicit adjustment policy, not to make invalid source values appear valid."),
     ("Inspection versus correction", "A flag requests investigation. Correct only with trustworthy source evidence, quarantine invalid records, or retain legitimate rare values with documentation.")],
    "A score150 violates our declared score domain regardless of the rest of the dataset. A valid score0 might be statistically unusual but still true. "
    "Validate source constraints before fitting statistical thresholds; invalid infinities and impossible values can corrupt mean and spread estimates. "
    "Do not clip input scores to0..100 merely so validation passes. Clipping can be a documented derived adjustment, but it must not erase evidence of bad source data. "
    "Keep flags and reasons separate from decisions. A high salary, large sale or low grade can be important precisely because it is unusual.",
    'finite = np.isfinite(values.to_numpy(dtype=float, na_value=np.nan))\nvalid = finite & values.between(0,100).fillna(False)\n# Preserve invalid values in raw data for review',
    '''
    import numpy as np
    import pandas as pd
    scores = pd.Series([0, 80, 150, np.inf, pd.NA], dtype="Float64")
    finite = np.isfinite(scores.to_numpy(dtype=float, na_value=np.nan))
    valid = finite & scores.between(0, 100).fillna(False)
    print("Valid:", valid.tolist())
    print("Valid scores:", scores.loc[valid].tolist())
    print("Missing:", scores.isna().tolist())
    ''',
    "0 valid score हो।150 domain बाहिर, infinity finite होइन, र missing अर्को अवस्था हो। Statistical rule ले यी अर्थ छुट्याउँदैन।",
    'Clip invalid score150 to100 and call the source correct',
    'Flag/quarantine the invalid source; adjust only with a documented separate policy',
    "Clipping removes evidence of the original violation.",
    "Flag negative durations independently from missing durations.",
    '''
    import pandas as pd
    duration = pd.Series([0, -5, 30, pd.NA], dtype="Float64")
    invalid = (duration < 0).fillna(False)
    print("Negative:", invalid.tolist(), "Missing:", duration.isna().tolist())
    ''',
    "Create a separately named capped display column and keep the original large values.",
    '''
    import pandas as pd
    df = pd.DataFrame({"raw_value": [10, 20, 1000]})
    df["display_capped"] = df["raw_value"].clip(upper=100)
    print(df.to_dict(orient="records"))
    ''',
    "Validate domain rules first. A rare valid observation and an impossible value need different decisions.",
    [("Is every statistically unusual value an error?", "No", "Always", "Only negative numbers", "Rare events can be genuine and important."),
     ("Does clipping prove an invalid source value was correct?", "No", "Always", "Only with upper=100", "It changes the value without proving its truth.")])

lesson(4, "2. IQR fences with explicit edge cases",
    "Calculate quartiles and fences while treating outlier flags as inspection signals.",
    [("quantile; Q1/Q3; IQR", "Q1 is the25th percentile, Q3 the75th and IQR=Q3-Q1. pandas quantile interpolates by default; state the method for reproducibility."),
     ("Tukey-style fences", "The example flags values below Q1-1.5*IQR or above Q3+1.5*IQR. Boundaries themselves are not flagged; this is a descriptive convention, not a universal probability guarantee."),
     ("Zero IQR; small samples", "Repeated values can make IQR zero and small samples make thresholds unstable. Here zero IQR returns no automatic fence decision and requests manual domain review.")],
    "IQR uses the middle half of the observed distribution, which can resist some extremes better than mean-based spread. "
    "Compute thresholds from valid known values only and retain the threshold policy in the report. Quantile conventions can differ across tools, especially on small datasets. "
    "Use fences to select records for inspection, not as a command to delete them. A skewed distribution may legitimately have many high values. "
    "When IQR is zero, this lesson avoids mechanically treating every different value as a bad record. Report the degenerate spread and use domain knowledge. An all-missing column cannot provide meaningful quartiles.",
    'q1,q3 = known.quantile([0.25,0.75], interpolation="linear")\niqr = q3-q1\nlower,upper = q1-1.5*iqr, q3+1.5*iqr\nflags = (known < lower) | (known > upper)',
    '''
    import pandas as pd
    values = pd.Series([10, 11, 12, 13, 100], dtype="Float64")
    q1, q3 = values.quantile([0.25, 0.75], interpolation="linear")
    iqr = q3 - q1
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    print("Q1,Q3,IQR:", float(q1), float(q3), float(iqr))
    print("Fences:", float(lower), float(upper))
    print("Inspect:", values.loc[(values < lower) | (values > upper)].tolist())
    ''',
    "100 fence बाहिर पर्‍यो, त्यसैले inspect list मा आयो। यो स्वतः गलत भन्न मिल्दैन; source र measurement को अर्थ जाँच्नु।",
    'Drop every row outside an IQR fence without a report',
    'Record thresholds and flags, then decide using domain/source evidence',
    "A descriptive fence does not establish an error.",
    "Calculate IQR fences for [1,2,3,4,20] and list flagged values.",
    '''
    import pandas as pd
    s = pd.Series([1, 2, 3, 4, 20], dtype="Float64")
    q1, q3 = s.quantile([0.25, 0.75])
    lower, upper = q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1)
    print(float(lower), float(upper), s.loc[(s < lower) | (s > upper)].tolist())
    ''',
    "Handle zero IQR explicitly rather than inventing a robust statistical decision.",
    '''
    import pandas as pd
    s = pd.Series([10, 10, 10, 10, 10, 11], dtype="Float64")
    q1, q3 = s.quantile([0.25, 0.75])
    if q3 == q1:
        print("Zero IQR: domain review; no automatic fence decision")
    ''',
    "IQR flags depend on valid data, quantile convention and spread; flags request inspection.",
    [("Is IQR Q3 minus Q1?", "Yes", "No; mean minus median", "Only maximum minus minimum", "It measures the middle-half spread."),
     ("Do IQR flags prove source errors?", "No", "Always", "Only on small samples", "Thresholds are descriptive screening rules.")])

lesson(4, "3. Z-scores, spread conventions and constant columns",
    "Compute an explicitly defined z-score and handle zero/absent spread.",
    [("z-score; abs", "z=(value-mean)/standard_deviation measures signed distance in spread units. abs gives its magnitude for two-sided threshold checks."),
     ("std(ddof=0/1)", "ddof=0 uses population-style spread for this complete descriptive fixture; pandas defaults to ddof=1. Record the convention rather than relying on defaults."),
     ("Zero spread; contaminated statistics", "A constant column has zero spread, so ordinary z division is undefined. Extreme values can also pull mean/std and mask themselves; z flags are not universal robust decisions.")],
    "Z-scores are useful when the mean/spread representation is appropriate. They are not interchangeable with IQR fences or proof of a particular probability distribution. "
    "Record whether the threshold comparison is > or >= and which ddof you use. The fixture flags magnitudes at least2 using ddof=0. "
    "Constant or absent observations cannot support the ordinary division. Report no spread-based decision instead of silently dividing by zero. "
    "Skew, small sample sizes and influential extremes can make mean-based screening misleading. Choose a method for the data's meaning and preserve raw values for follow-up.",
    'spread = known.std(ddof=0)\nif spread > 0:\n    z = (known-known.mean())/spread\n    inspect = z.abs() >= 2\nelse: report no spread-based decision',
    '''
    import pandas as pd
    values = pd.Series([10] * 9 + [100], dtype="Float64")
    spread = values.std(ddof=0)
    z = (values - values.mean()) / spread
    print("Mean/std:", float(values.mean()), float(spread))
    print("Last z:", round(float(z.iloc[-1]), 3))
    print("Inspect:", values.loc[z.abs() >= 2].tolist())
    ''',
    "Mean19 र std27 बाट100 को z3 आयो। ddof=0 र threshold>=2 स्पष्ट छन्। यो screening हो, delete गर्ने आदेश होइन।",
    'Divide by std without checking zero or missing spread',
    'Check observed count and finite positive spread before division',
    "A constant/all-missing column makes ordinary z division undefined.",
    "Compare population/sample spread for [10,20,30] using explicit ddof.",
    '''
    import pandas as pd
    s = pd.Series([10, 20, 30], dtype="Float64")
    print(round(float(s.std(ddof=0)), 3), round(float(s.std(ddof=1)), 3))
    ''',
    "Handle a constant column with no automatic z-score decision.",
    '''
    import pandas as pd
    s = pd.Series([20, 20, 20], dtype="Float64")
    spread = s.std(ddof=0)
    if pd.isna(spread) or spread == 0:
        print("No positive spread: review domain, no automatic z decision")
    ''',
    "Z-score screening needs valid observations, a defined spread convention, a threshold and edge-case handling.",
    [("Which ddof does pandas std use by default?", "1", "0", "The threshold", "Specify your convention explicitly."),
     ("Is ordinary z division defined for zero spread?", "No", "Always", "Only for integers", "Its denominator would be zero.")])

lesson(4, "4. Decisions, reasons and validation after changes",
    "Document keep/quarantine/fill choices and prove final invariants after a transformation.",
    [("Decision ledger", "A ledger records what was observed, which rule applied, what changed and why. Keep statistical inspection flags separate from verified invalidity."),
     ("Postconditions", "Postconditions are required properties of a returned result: valid ranges, known identity, permitted vocabulary and preserved raw input."),
     ("Fit/transform separation preview", "Data-derived parameters such as medians should be learned once from the intended reference/training population and reused where appropriate. Recomputing from future data can change meaning or leak information.")],
    "Cleaning is a chain of decisions, not a collection of convenient method calls. Validate first, quarantine invalid records, apply any justified fill only to genuinely missing values, and validate the result again. "
    "For this fictional score exercise, the chosen policy fills an unknown score with the median of valid observed scores; it does not fill a score outside0..100. "
    "Report both dropped records and estimated cells. Keep the input table unchanged so decisions remain reversible. "
    "In predictive work, learn parameters from the permitted training/reference population rather than the combined dataset. Our examples are descriptive local exercises and do not claim a universal imputation model.",
    'validate known scores\nseparate invalid rows\nsave missing flags\nfill genuinely missing values under stated policy\nvalidate final invariants and preserve raw input',
    '''
    import pandas as pd
    raw = pd.DataFrame({"id": ["A", "B", "C", "D"],
                       "score": pd.Series([80, pd.NA, 90, 150], dtype="Float64")})
    invalid = raw["score"].notna() & ~raw["score"].between(0, 100).fillna(False)
    clean = raw.loc[~invalid].copy()
    clean["was_missing"] = clean["score"].isna()
    median = clean["score"].median()
    if pd.isna(median):
        raise ValueError("No observed median")
    clean["score"] = clean["score"].fillna(median)
    assert clean["score"].between(0, 100).all()
    print(clean.to_dict(orient="records"))
    print("Quarantine:", raw.loc[invalid, "id"].tolist())
    print("Raw missing:", raw["score"].isna().tolist())
    ''',
    "D को150 quarantine भयो। B को missing score मात्रै85 estimate भयो र was_missing=True रह्यो। Raw score अझै missing छ।",
    'Treat all invalid and missing scores as the same median-fill group',
    'Quarantine invalid known scores before estimating genuine missing values',
    "The pipeline must not hide domain violations behind imputation.",
    "Record an explicit decision to retain a valid rare score rather than deleting it.",
    '''
    import pandas as pd
    df = pd.DataFrame({"id": ["A", "B"], "score": [0, 90]})
    ledger = [{"id": "A", "signal": "unusually low", "decision": "retain",
               "reason": "source verified; score is within declared bounds"}]
    print(df["score"].tolist())
    print(ledger)
    ''',
    "Use a previously chosen fill parameter85 on a new missing score, not a recomputed median from that new table.",
    '''
    import pandas as pd
    reference_median = 85.0
    new_scores = pd.Series([pd.NA, 10], dtype="Float64")
    print(new_scores.fillna(reference_median).tolist())
    ''',
    "Every change needs a reason, source reference and final validity check; keep raw data and estimation provenance.",
    [("Should an invalid known score be hidden by median filling?", "No", "Always", "Only if rare", "Invalidity and missingness need different actions."),
     ("Why validate after changes?", "To prove the result still meets the schema", "To delete the source", "To guarantee all assumptions are true", "Implementation changes can introduce violations.")])

lesson(5, "1. Tidy data and melt: wide to long",
    "Identify observation units and convert subject columns into a long table without losing IDs.",
    [("Tidy-data principle", "For a chosen observation unit, each variable is a column and each observation a row. Long form often suits repeated measurements, but a wide presentation can still be useful."),
     ("melt; id_vars; value_vars", "melt keeps identifier columns and turns selected measurement columns into variable/value rows. var_name and value_name name the new columns."),
     ("Observation key", "In this example, id+subject identifies one student-subject observation. Validate that compound key rather than assuming id alone is unique after reshaping.")],
    "A wide table can store one student per row and separate subject columns. A long table stores one student-subject observation per row, with subject and score as columns. "
    "The best layout depends on what constitutes an observation and the operation you need. Preserve IDs as explicit columns during reshape; do not use positional row counters as identity. "
    "melt repeats identifier values for each selected measurement. Two students and two subjects produce four long rows. "
    "Missing scores remain missing observations unless you deliberately drop them. Reshaping must not silently replace unknown scores with zero.",
    'long = wide.melt(id_vars=["id"], value_vars=["math","english"],\n                 var_name="subject", value_name="score")',
    '''
    import pandas as pd
    wide = pd.DataFrame({"id": ["001", "002"], "math": [80, 90], "english": [70, 85]})
    long = wide.melt(id_vars=["id"], value_vars=["math", "english"],
                     var_name="subject", value_name="score")
    print(long.to_dict(orient="records"))
    print("Shape:", long.shape)
    print("Repeated observation keys:", int(long.duplicated(["id", "subject"]).sum()))
    ''',
    "Long table मा001 दुई पटक आउँछ, किनकि दुई subjects छन्। त्यसैले id मात्रको repeat duplicate error होइन; id+subject observation key हो।",
    'Treat repeated id after melt as duplicated students to delete',
    'Use the declared student-subject observation key',
    "melt intentionally creates one row per measurement.",
    "Melt January/February minutes for two students while retaining text IDs.",
    '''
    import pandas as pd
    wide = pd.DataFrame({"id": ["001", "002"], "Jan": [30, 40], "Feb": [50, 60]})
    long = wide.melt(id_vars="id", value_vars=["Jan", "Feb"], var_name="month", value_name="minutes")
    print(long.to_dict(orient="records"))
    ''',
    "Retain a missing measurement through melt and report how many long observations remain unknown.",
    '''
    import pandas as pd
    wide = pd.DataFrame({"id": ["001"], "math": [80.0], "english": [None]})
    long = wide.melt(id_vars="id", value_vars=["math", "english"], var_name="subject", value_name="score")
    print(long.shape, int(long["score"].isna().sum()))
    ''',
    "Define the observation unit and key; melt changes layout, not missing-data truth.",
    [("How many long rows come from2 students×2 subjects?", "4", "2", "8", "Each student-subject measurement becomes a row."),
     ("Does a repeated id after melt always mean an error?", "No", "Always", "Only if numerical", "The observation key may include the measurement label.")])

lesson(5, "2. pivot is reshape; pivot_table is aggregation",
    "Rebuild wide data only when keys are unique, and aggregate duplicates only deliberately.",
    [("pivot", "pivot reshapes unique index/column combinations without aggregation. Duplicate combinations raise an error because one output cell has multiple candidate values."),
     ("pivot_table; aggfunc; observed", "pivot_table combines repeated combinations with an explicit aggregate such as mean or sum. observed=True limits categorical grouping to observed categories; choose this parameter explicitly."),
     ("reset_index; rename_axis", "reset_index moves index labels into columns; rename_axis changes axis metadata. These help reconstruct a conventional table after pivot without changing cell values.")],
    "Round-trip a unique long table with pivot when each student-subject pair has one score. If that key repeats, pandas cannot decide which value belongs in the cell. "
    "Investigate duplicates rather than hiding them with an accidental default mean. pivot_table intentionally aggregates: mean for repeated measurements and sum for additive transactions answer different questions. "
    "State the aggregation and preserve counts or source rows when they matter. Aggregation cannot generally be reversed into the original observations. "
    "After a pivot, make IDs ordinary columns again when exporting a flat table. Column order and axis names may differ even when the measurements are correctly reconstructed.",
    'wide = long.pivot(index="id", columns="subject", values="score")\nsummary = long.pivot_table(index="id", columns="subject", values="score", aggfunc="mean", observed=True)',
    '''
    import pandas as pd
    long = pd.DataFrame({"id": ["001", "001", "002", "002"], "subject": ["math", "english", "math", "english"],
                         "score": [80, 70, 90, 85]})
    wide = long.pivot(index="id", columns="subject", values="score")
    flat = wide.reset_index().rename_axis(None, axis=1)
    print(flat[["id", "math", "english"]].to_dict(orient="records"))
    ''',
    "Unique pair भएकाले pivot ले कुनै mean/sum नगरी values फर्कायो। Flat export का लागि id index बाट column मा ल्याइयो।",
    'Use pivot_table merely to hide unexplained duplicate keys',
    'Investigate duplicates; choose aggregation only when it answers the intended question',
    "Aggregation changes observation meaning and can destroy source distinctions.",
    "Demonstrate pivot's duplicate-key error, then explicitly summarize repeated scores using mean.",
    '''
    import pandas as pd
    long = pd.DataFrame({"id": ["001", "001"], "subject": ["math", "math"], "score": [80, 90]})
    try:
        long.pivot(index="id", columns="subject", values="score")
    except ValueError:
        print("Duplicate observation key: pivot rejected")
    mean = long.pivot_table(index="id", columns="subject", values="score", aggfunc="mean", observed=True)
    print(float(mean.loc["001", "math"]))
    ''',
    "Show that mean and sum aggregate the same two transactions differently.",
    '''
    import pandas as pd
    rows = pd.DataFrame({"id": ["A", "A"], "item": ["book", "book"], "amount": [10, 20]})
    mean = rows.pivot_table(index="id", columns="item", values="amount", aggfunc="mean", observed=True)
    total = rows.pivot_table(index="id", columns="item", values="amount", aggfunc="sum", observed=True)
    print(float(mean.loc["A", "book"]), float(total.loc["A", "book"]))
    ''',
    "pivot requires a unique observation key; pivot_table performs a declared, generally irreversible aggregation.",
    [("What does pivot do with duplicate output-cell keys?", "Raises an error", "Always sums", "Always keeps the last", "One output cell cannot represent two candidates without a policy."),
     ("Can mean aggregation recover every original repeated observation?", "No", "Always", "Only for text IDs", "Aggregation loses individual values.")])

lesson(5, "3. stack/unstack and named index levels",
    "Move a named measurement axis into a MultiIndex and reverse it explicitly.",
    [("MultiIndex", "A MultiIndex stores multiple label levels for one axis. Here a tuple (id,subject) identifies each stacked value."),
     ("stack; unstack", "stack moves a column level into index levels; unstack moves an index level into columns. Name the levels so the chosen axis is understandable."),
     ("pandas3 stack behavior", "These examples use pandas3's default stack implementation. Do not paste legacy dropna/sort arguments blindly; choose an explicit later missing filter if your policy requires it.")],
    "melt produces regular columns, while stack commonly creates a Series with a multi-level index. Both can represent student-subject measurements, but the result interface differs. "
    "Name the index and column axes before stacking so a tuple label has an understandable meaning. unstack('subject') moves that named level back to columns. "
    "A round-trip should preserve measurement values under an explicit row/column ordering. Sparse combinations and missing values may need additional policies; absence of an observation is not necessarily a measured zero. "
    "Use the pandas3 stack interface shown here; older tutorials may assume different sorting or missing-value defaults.",
    'wide = wide.rename_axis("id", axis=0).rename_axis("subject", axis=1)\nstacked = wide.stack()\nrestored = stacked.unstack("subject")',
    '''
    import pandas as pd
    wide = pd.DataFrame({"math": [80, 90], "english": [70, 85]}, index=["001", "002"])
    wide = wide.rename_axis("id", axis=0).rename_axis("subject", axis=1)
    stacked = wide.stack()
    restored = stacked.unstack("subject")
    print("Levels:", stacked.index.names)
    print("One value:", stacked.loc[("001", "math")])
    print("Round trip:", restored.equals(wide))
    ''',
    "Tuple('001','math') ले एउटा measurement चिनायो। Named subject level unstack गर्दा wide table फेरि आयो। MultiIndex positions भन्दा labels को structure हो।",
    'Treat a MultiIndex tuple as two unrelated row positions',
    'Interpret tuple components as the named index levels',
    "The components identify one labeled observation.",
    "Stack two item columns for one student and read the item-specific value by tuple label.",
    '''
    import pandas as pd
    wide = pd.DataFrame({"pen": [2], "book": [3]}, index=["001"])
    wide = wide.rename_axis("id").rename_axis("item", axis=1)
    stacked = wide.stack()
    print(stacked.loc[("001", "book")], stacked.index.names)
    ''',
    "Complete a melt/pivot round-trip and restore explicit column order before testing equality.",
    '''
    import pandas as pd
    wide = pd.DataFrame({"id": ["001", "002"], "math": [80, 90], "english": [70, 85]})
    long = wide.melt(id_vars="id", var_name="subject", value_name="score")
    restored = long.pivot(index="id", columns="subject", values="score").reset_index().rename_axis(None, axis=1)
    restored = restored[wide.columns.tolist()]
    print(restored.equals(wide))
    ''',
    "Named index levels make stack/unstack predictable. Check ordering, keys and missing policies in round trips.",
    [("What does stack move into index levels?", "A column level", "The Python interpreter", "Only missing cells", "It reshapes a column axis into row-index structure."),
     ("Why name MultiIndex levels?", "To identify their meaning and select them explicitly", "To convert every value to text", "To remove missing rows", "Named levels clarify tuple labels and unstack choices.")])

PROJECT = clean(r'''
import argparse
import csv
from io import StringIO
import json
import os
from pathlib import Path
import sys
import tempfile
import numpy as np
import pandas as pd

COLUMNS = ["id", "name", "region", "score", "updated"]
MAX_BYTES, MAX_ROWS = 5 * 1024 * 1024, 10_000
ALIASES = {"np": "NP", "nepal": "NP", "jp": "JP", "japan": "JP"}

def load_raw(path):
    with Path(path).open("rb") as handle:
        data = handle.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Input exceeds 5 MiB")
    try:
        text = data.decode("utf-8-sig")
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        header = next(reader, None)
        if header is None or len(header) != len(set(header)) or set(header) != set(COLUMNS):
            raise ValueError("Require exactly id,name,region,score,updated with unique headers")
        rows = 0
        for record in reader:
            if not record:
                continue
            rows += 1
            if len(record) != len(COLUMNS) or rows > MAX_ROWS:
                raise ValueError("Ragged or oversized CSV")
    except (UnicodeDecodeError, csv.Error) as error:
        raise ValueError("Expected well-formed UTF-8 comma CSV") from error
    raw = pd.read_csv(StringIO(text), dtype="string", keep_default_na=False,
                      na_values=[""], skip_blank_lines=True)
    if raw.shape != (rows, len(COLUMNS)) or raw.columns.tolist() != header:
        raise ValueError("Parser/header mismatch")
    return raw[COLUMNS]

def normalize_text(raw):
    if not raw.columns.is_unique or set(raw.columns) != set(COLUMNS):
        raise ValueError("Unexpected source schema")
    if len(raw) > MAX_ROWS or not all(isinstance(dtype, pd.StringDtype) for dtype in raw.dtypes):
        raise ValueError("Require bounded raw string columns")
    out = raw[COLUMNS].reset_index(drop=True).copy()
    out["_source_record"] = range(1, len(out) + 1)
    for column in COLUMNS:
        out[column] = out[column].str.strip()
    out["name"] = out["name"].str.normalize("NFC").str.replace(r"\s+", " ", regex=True)
    tokens = out["region"].str.casefold()
    out["region"] = tokens.map(ALIASES).fillna(tokens).astype("string")
    out["score"] = out["score"].mask(out["score"].eq("").fillna(False), pd.NA)
    return out

def convert_types(normalized):
    out = normalized.copy()
    out["score"] = pd.to_numeric(out["score"], errors="coerce").astype("Float64")
    out["updated"] = pd.to_datetime(out["updated"], format="%Y-%m-%d", errors="coerce")
    return out

def rejection_reasons(normalized, typed):
    finite = pd.Series(np.isfinite(typed["score"].to_numpy(dtype=float, na_value=np.nan)), index=typed.index)
    rules = {
        "id_requires_three_ASCII_digits": ~normalized["id"].str.fullmatch(r"[0-9]{3}").fillna(False),
        "name_required": normalized["name"].isna() | normalized["name"].eq("").fillna(False),
        "unknown_region": ~normalized["region"].isin(["NP", "JP"]),
        "invalid_or_missing_updated_date": typed["updated"].isna() | ~normalized["updated"].str.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}").fillna(False),
        "score_not_numeric": normalized["score"].notna() & typed["score"].isna(),
        "score_nonfinite": typed["score"].notna() & ~finite,
        "score_outside_0_100": finite & ~typed["score"].between(0, 100).fillna(False),
    }
    reasons = {i: [] for i in typed.index}
    for reason, mask in rules.items():
        for i in typed.index[mask]:
            reasons[i].append(reason)
    return reasons

def validate_clean(clean):
    if clean.empty or clean.columns.tolist() != COLUMNS:
        raise ValueError("Require a nonempty canonical result")
    if not clean["id"].is_unique or not clean["id"].str.fullmatch(r"[0-9]{3}").fillna(False).all():
        raise ValueError("Invalid or repeated result ID")
    if not clean["name"].notna().all() or not clean["name"].str.strip().ne("").fillna(False).all():
        raise ValueError("Invalid result name")
    if not clean["region"].isin(["NP", "JP"]).all() or clean["updated"].isna().any():
        raise ValueError("Invalid result region/date")
    finite = np.isfinite(clean["score"].to_numpy(dtype=float, na_value=np.nan))
    if not finite.all() or not clean["score"].between(0, 100).fillna(False).all():
        raise ValueError("Invalid result score")

def cleaning_pipeline(raw):
    normalized = normalize_text(raw)
    typed = convert_types(normalized)
    reasons = rejection_reasons(normalized, typed)
    rejected = [i for i in typed.index if reasons[i]]
    accepted = typed.loc[[i for i in typed.index if not reasons[i]]].copy()
    ordered = accepted.sort_values(["id", "updated", "_source_record"], ascending=[True, False, False])
    repeated = ordered.duplicated("id", keep="first")
    removed = ordered.loc[repeated]
    latest = ordered.loc[~repeated].copy()
    if latest.empty:
        raise ValueError("No valid records remain")
    missing = latest["score"].isna()
    fill_value = None
    if missing.any():
        median = latest["score"].median()
        if pd.isna(median):
            raise ValueError("No observed retained scores to estimate a median")
        fill_value = float(median)
        latest["score"] = latest["score"].fillna(fill_value)
    estimated_records = latest.loc[missing, "_source_record"].astype(int).tolist()
    typed.loc[latest.index, "score"] = latest["score"]
    staged = typed[COLUMNS].copy()
    staged["updated"] = typed["updated"].dt.strftime("%Y-%m-%d").astype("string")
    staged["score"] = typed["score"].astype("string")
    source = raw[COLUMNS].reset_index(drop=True)
    changes = []
    for i in staged.index:
        for column in COLUMNS:
            old = None if pd.isna(source.at[i, column]) else str(source.at[i, column])
            new = None if pd.isna(staged.at[i, column]) else str(staged.at[i, column])
            if old != new:
                rule = "normalize_text"
                if column in ("score", "updated"):
                    rule = "convert_type"
                if column == "score" and int(typed.at[i, "_source_record"]) in estimated_records:
                    rule = "median_fill"
                changes.append({"record": i + 1, "column": column, "before": old, "after": new, "rule": rule})
    clean = latest[COLUMNS].reset_index(drop=True)
    clean["region"] = clean["region"].astype(pd.CategoricalDtype(["NP", "JP"]))
    validate_clean(clean)
    q1, q3 = clean["score"].quantile([0.25, 0.75], interpolation="linear")
    iqr = float(q3 - q1)
    lower, upper = float(q1 - 1.5 * iqr), float(q3 + 1.5 * iqr)
    flags = [] if iqr == 0 else clean.loc[(clean["score"] < lower) | (clean["score"] > upper), "id"].tolist()
    report = {
        "input_rows": len(raw), "kept_rows": len(clean),
        "quarantined": [{"record": i + 1, "reasons": reasons[i]} for i in rejected],
        "removed_duplicate_records": removed["_source_record"].astype(int).tolist(),
        "imputed_score_records": estimated_records, "score_fill_value": fill_value,
        "cell_changes": changes,
        "iqr_inspection": {"computed_on": "final scores, including disclosed estimates",
                           "iqr": iqr, "lower": lower, "upper": upper, "ids": flags,
                           "decision": "inspect only" if iqr > 0 else "zero IQR; no automatic decision"},
        "policy": {"schema": "three-digit text id; required name; region NP/JP; score finite0..100; updated YYYY-MM-DD",
                   "missing": "empty/whitespace-only scores only; invalid known tokens quarantined",
                   "latest": "newest valid date, then later input record for same-day ties",
                   "fill": "median of known retained scores; stop if estimation has no observations",
                   "audit": "source-to-final-staged cell changes include quarantined and superseded records",
                   "record": "one-based parsed observation position, not physical CSV line number",
                   "limits": {"bytes": MAX_BYTES, "rows": MAX_ROWS}},
    }
    assert len(raw) == len(clean) + len(rejected) + len(removed)
    return clean, report

def publish_bundle(clean, report, destination):
    """Publish one new directory; never overwrite an existing output bundle."""
    destination = Path(destination)
    if destination.exists():
        raise ValueError("Output already exists; choose a new bundle directory")
    validate_clean(clean)
    payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    csv_text = clean.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\n")
    with tempfile.TemporaryDirectory(prefix=".cleaning-", dir=destination.parent) as folder:
        stage = Path(folder)
        (stage / "clean.csv").write_text(csv_text, encoding="utf-8", newline="\n")
        (stage / "report.json").write_text(payload, encoding="utf-8", newline="\n")
        os.rename(stage, destination)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Clean the supplied student schema into a new output bundle")
    parser.add_argument("raw_csv")
    parser.add_argument("new_bundle")
    args = parser.parse_args(argv)
    try:
        raw = load_raw(args.raw_csv)
        clean, report = cleaning_pipeline(raw)
        report["input_name"] = Path(args.raw_csv).name
        publish_bundle(clean, report, args.new_bundle)
    except (OSError, ValueError, pd.errors.ParserError) as error:
        print("No new bundle:", error, file=sys.stderr)
        return 1
    print("Published new bundle; raw CSV unchanged")
    return 0
''')

FIXTURE = 'id,name,region,score,updated\n 001 , Asha   Rai ,nepal,80,2026-01-01\n001,Asha Rai,NP,90,2026-01-03\n002,Bina, Japan ,,2026-01-02\n003,Chandra,JP,70,2026-01-02\n004,Dipa,NP,150,2026-01-01\n005,Eka,Npeal,oops,bad\n003,Chandra,JP,75,2026-01-02\n'
SETUP = "\nPath('messy.csv').write_text(" + repr(FIXTURE) + ", encoding='utf-8', newline='\\n')\n"

lesson(5, "4. Complete audited cleaning pipeline and week review",
    "Combine small cleaning stages into a validated result and a documented new output bundle.",
    [("Cleaning pipeline contract", "This project cleans one supplied student schema, not arbitrary CSVs: id,name,region,score,updated. It reads bounded local UTF-8 comma CSV, preserves raw input and never guesses unknown categories."),
     ("Function stages", "load_raw parses a bounded snapshot; normalize_text applies declared formatting; convert_types parses quantities/dates; rejection_reasons separates invalid records; cleaning_pipeline chooses latest records, estimates genuine missing scores and audits changes."),
     ("at; index-aligned assignment; source records", "at reads one scalar by row/column labels. Internal source records retain one-based parsed observation identity across sorting/filtering. typed.loc[latest.index,'score'] aligns retained score updates by those stable row labels."),
     ("Postconditions and row accounting", "validate_clean proves final schema/domain constraints. Input rows must equal kept + quarantined + superseded records. The audit records raw-to-final-staged cells, including attempted transformations of rejected rows."),
     ("New output bundle", "publish_bundle writes clean.csv and report.json in one owned temporary directory, then renames it to a new destination. Existing bundles are refused, so reruns cannot overwrite previous outputs."),
     ("Canonical export and idempotence", "The clean CSV exports IDs as text, scores as numerical text and dates as YYYY-MM-DD. Reloading through the explicit string schema and cleaning again should reproduce the same CSV values; source/provenance reports necessarily refer to the new input.")],
    "Read the schema before running this project. A valid ID is exactly three ASCII digits, a name is required, region must map to NP/JP, a known score must be finite0..100 and updated is a calendar date. "
    "Only a genuinely blank score can be estimated. Invalid text, unknown categories, impossible scores and invalid dates are quarantined with record references and reasons. "
    "For each valid ID, the newest valid date wins; same-day ties choose the later input record. Then the median of known retained scores fills any genuinely missing retained scores. "
    "All-missing retained scores stop the run if an estimate is required. Every source-to-staged cell change is logged; estimated records are separately listed. "
    "IQR flags on the final table include disclosed estimates and request inspection only. Raw data is unchanged, and an existing output bundle is never overwritten. "
    "The sample is fictional; actual personal datasets and their audit reports belong in private storage. This teaching policy is specific to this schema, not a universal cleaning recipe.",
    'python cleaning_pipeline.py messy_students.csv run-01\n# run-01/clean.csv + run-01/report.json; destination must not exist\nraw = load_raw(path)\nclean, report = cleaning_pipeline(raw)\npublish_bundle(clean, report, new_directory)',
    PROJECT + SETUP + '''
raw = load_raw("messy.csv")
before = raw.copy()
clean, report = cleaning_pipeline(raw)
print(clean[["id", "name", "region", "score"]].to_dict(orient="records"))
print("Rows:", report["input_rows"], report["kept_rows"])
print("Quarantine:", [row["record"] for row in report["quarantined"]])
print("Superseded:", report["removed_duplicate_records"])
print("Estimated:", report["imputed_score_records"], report["score_fill_value"])
print("Raw unchanged:", raw.equals(before))
''',
    "001 को newer90 र003 को same-day later75 बच्यो। त्यसैले002 को blank score median82.5 भयो। Invalid records5/6 estimate भएनन्; report मा review reasons छन्।",
    'Publish clean.csv first and discover a report-writing error afterward',
    'Validate and serialize first, then publish both files in a new bundle',
    "A new bundle keeps dataset/report together and refuses overwriting an earlier run.",
    "Run the full pipeline, publish the bundle and inspect the retained score, audit count and unchanged CSV bytes.",
    PROJECT + SETUP + '''
source = Path("messy.csv")
before = source.read_bytes()
raw = load_raw(source)
clean, report = cleaning_pipeline(raw)
publish_bundle(clean, report, "run-01")
stored = json.loads(Path("run-01/report.json").read_text(encoding="utf-8"))
print("Bundle files:", sorted(path.name for path in Path("run-01").iterdir()))
print("Cell changes:", len(stored["cell_changes"]))
print("Input unchanged:", source.read_bytes() == before)
print("Saved IDs:", load_raw("run-01/clean.csv")["id"].tolist())
''',
    "Reload the clean CSV, run cleaning again and prove canonical values are unchanged; also reject overwriting run-01.",
    PROJECT + SETUP + '''
clean, report = cleaning_pipeline(load_raw("messy.csv"))
publish_bundle(clean, report, "run-01")
again, second_report = cleaning_pipeline(load_raw("run-01/clean.csv"))
def canonical_csv(frame):
    return frame.to_csv(index=False, date_format="%Y-%m-%d", lineterminator="\\n")
print("Repeatable CSV:", canonical_csv(clean) == canonical_csv(again))
print("Second imputation:", second_report["imputed_score_records"])
try:
    publish_bundle(clean, report, "run-01")
except ValueError:
    print("Existing bundle preserved")
''',
    "Week29 mastery: deliberate missing policies, identity-aware deduplication, audited conversion, meaningful text rules, domain/outlier distinctions, valid reshaping and a repeatable documented pipeline.",
    [
        ("Is unknown data the same as observed zero?", "No", "Always", "Only for scores", "Unknown does not establish a zero value."),
        ("What must an imputation report preserve?", "Which cells were estimated", "Only the final mean", "No source references", "Estimated values must stay distinguishable from observations."),
        ("Is linear interpolation appropriate for random student-ID order?", "No", "Always", "Only with numeric IDs", "The ordering needs a continuous measurement meaning."),
        ("Does keep='last' mean newest timestamp automatically?", "No", "Always", "Only after loading CSV", "It follows current row order."),
        ("What follows numeric coercion?", "Audit failures and validate domain", "Fill every error with zero", "Delete the raw file", "Coercion can hide source errors if not audited."),
        ("Can naive timestamps' timezone be guessed by utc=True?", "No", "Always", "Only with dates", "The source time convention must be declared."),
        ("Does categorical casting preserve every unknown token?", "No", "Always", "Only with ordered=True", "Unknown values may become missing."),
        ("Which validates a whole token?", "fullmatch", "contains alone", "head", "Substring matching does not validate surrounding text."),
        ("Do outlier flags prove errors?", "No", "Always", "Only IQR flags", "Flags request domain/source investigation."),
        ("Can ordinary z division use zero spread?", "No", "Always", "Only with ddof=0", "The denominator would be zero."),
        ("Which reshapes without aggregating unique keys?", "pivot", "pivot_table with mean", "fillna", "pivot requires unique output-cell keys."),
        ("Should an existing project output bundle be overwritten?", "No; choose a new directory", "Always silently", "Only when CSV parsed", "Previous output remains available for comparison."),
    ])

# Explain small first-use helpers before they appear in executable examples.
DAYS["29.0"]["parts"][0]["sections"].insert(3, s("new", "Nullable Float64; pd.isna",
    note="Capital-F Float64 is pandas' nullable floating dtype, suitable for decimal measurements with pd.NA. pd.isna(value) also checks one scalar such as a missing median; it is not equality with a missing marker."))
DAYS["29.0"]["parts"][0]["sections"].insert(3, s("new", "eq; mask",
    note="eq compares values element-wise (like ==). mask replaces values where a Boolean condition is True; here it deliberately turns declared blank fields into pd.NA while retaining raw text."))
DAYS["29.2"]["parts"][0]["sections"].insert(3, s("new", "mod(1); to_numpy(na_value=...)",
    note="mod(1) gives the fractional remainder, so eq(0) checks whole-number values before integer casting. to_numpy requests an array representation and explicitly supplies np.nan for nullable missing values."))
DAYS["29.2"]["parts"][3]["sections"].insert(3, s("new", "str.fullmatch preview",
    note="fullmatch requires the entire string to satisfy a regex. [0-9]{3} means exactly three ASCII digits; Day4 expands searching/extraction and explains why contains is not whole-field validation."))
DAYS["29.5"]["parts"][3]["sections"].insert(3, s("new", "items; ne; to_csv; date_format",
    note="items iterates named dictionary/Series entries; ne is element-wise !=. to_csv exports a table; index=False omits row labels, date_format specifies date text and lineterminator='\\n' makes output newline choice explicit."))
DAYS["29.0"]["parts"][0]["sections"].insert(3, s("sh", 'python -m pip install "pandas>=3,<4"',
    note="Continue using the Week28 Python practice environment. Initial package installation needs internet; this course and all supplied local fixtures remain usable offline afterward. Verified with pandas3.0.6."))
DAYS["29.5"]["parts"][3]["sections"].insert(6, s("p",
    "Project walkthrough 1 — loading and normalization: load_raw reads one bounded byte snapshot, checks unique required headers and record widths, then loads every field as string. "
    "normalize_text keeps IDs textual, assigns parsed record references, permits name whitespace/NFC normalization and maps only declared region aliases. Unknown tokens survive for validation."))
DAYS["29.5"]["parts"][3]["sections"].insert(7, s("p",
    "Project walkthrough 2 — conversion and selection: convert_types creates nullable numerical scores and parsed dates. rejection_reasons retains all applicable errors per record. "
    "Only valid records enter newest-date/same-day-source-order selection. Missing-score estimation uses known scores from the retained population, not invalid or superseded observations."))
DAYS["29.5"]["parts"][3]["sections"].insert(8, s("p",
    "Project walkthrough 3 — audit and publication: cell_changes compares every raw field with its final staged representation, with conversion/normalization/fill rule labels. "
    "validate_clean checks the final result and row accounting proves where every source record went. publish_bundle validates and serializes before writing two files to an owned temporary folder; only a new destination is published."))
DAYS["29.5"]["parts"][3]["sections"].append(s("sh",
    "python cleaning_pipeline.py messy_students.csv run-01\npython cleaning_pipeline.py --help",
    note="Complete standalone project and fictional sample: docs/python-week29. Choose run-02 for another run; existing bundles and raw CSVs remain intact."))
DAYS["29.5"]["parts"][3]["sections"].append(s("p",
    "Primary references: https://pandas.pydata.org/docs/user_guide/missing_data.html · "
    "https://pandas.pydata.org/docs/user_guide/text.html · https://pandas.pydata.org/docs/reference/api/pandas.to_datetime.html · "
    "https://pandas.pydata.org/docs/user_guide/reshaping.html · https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.stack.html. "
    "Original explanations, fictional fixtures, examples/outputs, exercises and complete solutions are included for offline study."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week29 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in DAYS.items())
    addition = addition.replace("</", "<\\/")
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix + "\n" + addition + original[end:]).encode("utf-8"))
    temporary.replace(target)
    project_root = ROOT / "docs" / "python-week29"
    project_root.mkdir(exist_ok=True)
    (project_root / "cleaning_pipeline.py").write_text(
        '"""Week29 schema-specific audited cleaning practice. Python3.11+, pandas3.x."""\n'
        + PROJECT + '\nif __name__ == "__main__":\n    sys.exit(main())\n', encoding="utf-8")
    (project_root / "messy_students.csv").write_text(FIXTURE, encoding="utf-8", newline="\n")
    parts = [part for day in DAYS.values() for part in day["parts"]]
    quizzes = sum(len(section["lesson"]["quiz"]) for part in parts for section in part["sections"] if section["t"] == "checkpoint")
    print(f"Added Week29: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {EXECUTED} verified outputs.")


if __name__ == "__main__":
    write()

