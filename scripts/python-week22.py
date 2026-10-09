"""Add Week 22 only; run all examples before the atomic content write."""
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

ROOT = Path(__file__).resolve().parent.parent
days = {f"22.{d}": {"parts": []} for d in range(6)}
executed = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global executed
    run = subprocess.run(
        [sys.executable, "-c", clean(code)], capture_output=True,
        encoding="utf-8", timeout=8,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    executed += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def section(kind, value=None, **extra):
    result = {"t": kind, **extra}
    if value is not None:
        result["v"] = value
    return result


def question(prompt, answer, wrong1, wrong2, why, rotation):
    options = [answer, wrong1, wrong2]
    for _ in range(rotation % 3):
        options.insert(0, options.pop())
    return {"q": prompt, "options": options, "correct": rotation % 3, "why": why}


def add(day, title, goal, concepts, explanation, syntax, code, walkthrough,
        mistake, task, solution, challenge, challenge_code, key, quizzes):
    parts = days[f"22.{day}"]["parts"]
    index = len(parts)
    qs = [question(*q, index + n) for n, q in enumerate(quizzes)]
    sections = [
        section("h", title),
        section("key", "Learning objective: " + goal),
        *[section("new", name, note=note) for name, note in concepts],
        section("p", explanation),
        section("syn", syntax.replace(r"\n", "\n"), note="Read the pattern, then trace the complete example below."),
        section("code", clean(code)),
        section("out", output(code)),
        section("p", walkthrough),
        section("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        section("ex", task, practiceId=f"22.{day}.{index}.build"),
        section("sol", code=clean(solution), out=output(solution),
                why="Build walkthrough: " + key),
        section("ex", "Mini challenge: " + challenge,
                practiceId=f"22.{day}.{index}.challenge"),
        section("sol", code=clean(challenge_code), out=output(challenge_code),
                why="Challenge check: " + key),
        section("try", q=quizzes[0][0], code="# Explain your prediction before revealing.",
                a=quizzes[0][1], why=quizzes[0][4]),
        section("checkpoint", lesson={"id": f"course:22.{day}.{index}", "quiz": qs}),
        section("key", key),
    ]
    parts.append({"title": title, "sections": sections})


add(0, "1. What a regex does: first match, or no match",
    "Find a literal piece of text and safely inspect its match.",
    [
        ("Regular expression; re module",
         "Regex is a small pattern language for text. Python's standard-library re module runs these patterns; no package installation is needed."),
        ("re.search; Match; None",
         "search looks anywhere in a string and returns the first Match object, or None when nothing matches. A Match stores the matched text and its location."),
        ("group(0); span()",
         "group(0) returns the entire matched substring. span() returns (start, end), using the same end-exclusive indexes as Python slicing."),
    ],
    "Week 21 finished object-oriented design; this week returns to text processing. "
    "Start with a literal pattern, not a complicated formula. For a plain yes/no substring test, 'Python' in text is often simpler. "
    "Regex becomes useful when the wanted text has a changing shape: several digits, a date, or a structured log line. "
    "Use Python 3.10 or newer. Every example here works offline with the standard library.",
    'import re\nmatch = re.search("wanted", text)\nif match is not None:\n    print(match.group(0), match.span())',
    r'''
    import re
    text = "I study Python today"
    found = re.search("Python", text)
    if found is not None:
        print(found.group(0))
        print(found.span())
        start, end = found.span()
        print(text[start:end])
    print(re.search("Java", text) is None)
    ''',
    "पहिलो import ले re उपलब्ध बनाउँछ। 'Python' index 8 बाट सुरु हुन्छ; end 14 भनेको index 14 सम्मको अक्षर समावेश हुँदैन। "
    "त्यसैले text[8:14] र group(0) एउटै हुन्छन्। Java नभएकाले अन्तिम output True आउँछ। "
    "Match लाई string नसम्झ: पहिले None जाँच, त्यसपछि त्यसको method प्रयोग गर।",
    ("re.search('Java', text).group(0)",
     "found = re.search('Java', text)\nif found is not None:\n    print(found.group(0))",
     "An absent match is None, which has no group method. Check absence before accessing match information."),
    "Search for ERROR in two messages. Print its text and indexes when present; otherwise print 'no error marker'.",
    r'''
    import re
    for text in ("INFO ready", "ERROR disk full"):
        found = re.search("ERROR", text)
        if found is None:
            print("no error marker")
        else:
            print(found.group(0), found.span())
    ''',
    "Search 'cat cat'. Which occurrence is returned? Show its slice and compare it with group(0).",
    r'''
    import re
    text = "cat cat"
    found = re.search("cat", text)
    if found is not None:
        start, end = found.span()
        print(found.group(0), found.span())
        print(text[start:end] == found.group(0))
    ''',
    "search returns the first occurrence, not all occurrences. Check None, then use group(0) and end-exclusive span indexes. Prefer ordinary string methods when a literal test already solves the task.",
    [
        ("What does search return when the pattern is absent?", "None", "An empty Match", "False as a boolean", "The absence result is None; it has no match methods."),
        ("A match span is (8, 14). Which slice reproduces it?", "text[8:14]", "text[8:15]", "text[9:14]", "Python's slice stop index is excluded."),
    ])

add(0, "2. Raw strings: Python reads first, regex reads second",
    "Explain the two interpretation layers and write backslash patterns correctly.",
    [
        ("Raw string prefix r",
         "A raw string preserves backslashes at Python's string-literal layer. The regex engine still interprets those backslashes as pattern instructions."),
        (r"\d; +",
         r"\d matches one Unicode decimal digit; + repeats the preceding token one or more times. Day 2 explores classes and repetition fully."),
        ("repr() for a pattern",
         "repr shows a debugging representation with escapes visible. The extra escaping in its display is not extra text in the original string."),
    ],
    r"Python must create a string before re can read it. In an ordinary Python string, '\b' is a single backspace character. "
    r"In r'\b', Python preserves two characters, backslash and b; regex later interprets them as a word-boundary instruction. "
    r"Do not try to memorise displayed backslashes alone: inspect repr and length, then ask which layer is interpreting them.",
    r'pattern = r"\d+"\nfound = re.search(pattern, text)',
    r'''
    import re
    pattern = r"\d+"
    print(repr(pattern))
    found = re.search(pattern, "Order 42 costs 150")
    if found is not None:
        print(found.group(0))
    print(len(r"\b"), len("\b"))
    ''',
    r"r'\d+' मा \d एउटा digit र + लगातार digits हुन्। पहिलो समूह 42 हो, 150 होइन। "
    r"Raw \b को length 2 हुन्छ; ordinary \b को length 1 हुन्छ। Raw ले regex बन्द गरेको होइन—Python को escape conversion मात्र रोक्छ।",
    (r'pattern = "\bcat\b"', r'pattern = r"\bcat\b"',
     r"Ordinary \b becomes backspace before regex sees it. Raw strings express the intended regex boundary. A raw string cannot end with an odd number of backslashes."),
    "Extract the first number from 'Invoice 2087 is ready' using a raw pattern, then print its integer value.",
    r'''
    import re
    found = re.search(r"\d+", "Invoice 2087 is ready")
    if found is not None:
        print(found.group(0))
        print(int(found.group(0)))
    ''',
    r"Compare ordinary '\n' and raw r'\n': print each length and repr. Explain why a raw string can still be used to match a newline in regex.",
    r'''
    import re
    ordinary = "\n"
    raw = r"\n"
    print(len(ordinary), len(raw))
    print(repr(ordinary), repr(raw))
    print(re.fullmatch(raw, ordinary) is not None)
    ''',
    r"Python string escapes and regex escapes are separate layers. Raw strings make patterns readable; re still gives \d, \b and \n their regex meanings. Use repr while debugging.",
    [
        ("Does r make a regex treat every character literally?", "No; it only changes Python string-literal processing.", "Yes; regex is disabled.", "It changes the result into bytes.", "The resulting string is still parsed by the regex engine."),
        (r"How many characters are in r'\b'?", "2", "1", "0", "It contains a backslash and b; ordinary '\\b' contains one backspace."),
    ])

add(0, "3. Choose search, match, fullmatch or findall",
    "Choose the operation according to the question, rather than adding accidental anchors.",
    [
        ("re.match", "match checks only at the beginning; it may match a prefix without consuming the whole string."),
        ("re.fullmatch", "fullmatch requires the pattern to consume the complete string. Use it for a whole-input format check."),
        ("re.findall", "findall collects non-overlapping matches. Without capture groups it returns a list of matched strings; Day 3 explains how captures change this shape."),
    ],
    "Ask four different questions: Is the pattern anywhere? Does it start here? Does the whole value obey the format? "
    "What are all its occurrences? These are search, match, fullmatch and findall respectively. A prefix match is not a complete validation. "
    "Extracting a number produces text: call int only when you actually need arithmetic.",
    're.search(pattern, text)\nre.match(pattern, text)\nre.fullmatch(pattern, text)\nre.findall(pattern, text)',
    r'''
    import re
    text = "abc 12 and 34"
    print(re.search(r"\d+", text).group(0))
    print(re.match(r"\d+", text) is None)
    print(re.findall(r"\d+", text))
    print(re.match(r"\d+", "123abc").group(0))
    print(re.fullmatch(r"\d+", "123abc") is None)
    ''',
    "abc बाट सुरु हुने text मा match ले number पाउँदैन, search ले 12 पाउँछ। findall ले 12 र 34 दुवै text रूपमा दिन्छ। "
    "123abc को सुरुमा 123 भए पनि पूरा value digits मात्र होइन; त्यसैले fullmatch असफल हुन्छ। "
    "यहाँ group(0) सीधै बोलाइएको ठाउँमा literal input मा match निश्चित छ; अनिश्चित input मा None जाँच्नै पर्छ।",
    ("bool(re.match(r'\\d+', user_input))",
     "re.fullmatch(r'\\d+', user_input) is not None",
     "match can accept the numeric prefix of '42junk'; fullmatch rejects trailing junk."),
    "Validate '42', '42x' and an empty string as one-or-more digits. Print the input with repr and its validity.",
    r'''
    import re
    for value in ("42", "42x", ""):
        print(repr(value), re.fullmatch(r"\d+", value) is not None)
    ''',
    "Extract 5 and 12 from '5 apples, 12 pears', convert each string to int, and print the sum.",
    r'''
    import re
    pieces = re.findall(r"\d+", "5 apples, 12 pears")
    numbers = [int(piece) for piece in pieces]
    print(pieces)
    print(sum(numbers))
    ''',
    "Operation choice expresses intent: anywhere, beginning, entire input, or all matches. findall gives strings here; numeric conversion is a separate step.",
    [
        ("Which operation validates a whole numeric field?", "fullmatch", "search", "match", "A complete field must have no unmatched prefix or suffix."),
        ("What is findall(r'\\d+', '5 and 12') here?", "['5', '12']", "[5, 12]", "A single Match", "No capture groups are present, so each occurrence is a matched string."),
    ])

add(0, "4. Compile a pattern and iterate over match locations",
    "Reuse a named pattern and process each match with its position.",
    [
        ("re.compile; compiled pattern methods", "compile returns a reusable pattern object. Give it a meaningful variable name; its search/finditer/fullmatch methods use that pattern."),
        ("finditer", "finditer yields Match objects one at a time, retaining matched text and spans. It avoids creating a list of all matches when iteration is enough."),
    ],
    "A pattern such as number_pattern communicates its role more clearly than a repeated anonymous string. "
    "Python already caches recent patterns, so compiling is not a promise of dramatic speed improvement. "
    "Use finditer when you need locations, or when you can process matches incrementally. Converting that iterator to a list still uses memory for all its matches.",
    'pattern = re.compile(r"\\d+")\nfor found in pattern.finditer(text):\n    print(found.group(0), found.span())',
    r'''
    import re
    number_pattern = re.compile(r"\d+")
    for found in number_pattern.finditer("a12 b345"):
        print(found.group(0), found.span())
    print(number_pattern.fullmatch("99") is not None)
    ''',
    "Pattern एक पटक नाम दिएर बनायौँ। loop को पहिलो Match 12 र दोस्रो 345 हो। प्रत्येक Match को span फरक हुन्छ। "
    "findall को string list बाट यस्तो location सीधै आउँदैन; finditer को Match बाट आउँछ।",
    ("for number in re.findall(r'\\d+', text):\n    print(number.span())",
     "for found in re.finditer(r'\\d+', text):\n    print(found.span())",
     "findall returns strings in this case, not Match objects; strings have no span method."),
    "Compile a digit pattern and reuse it for 'Room 7' and 'Floor 12'. Print each line's matches.",
    r'''
    import re
    number_pattern = re.compile(r"\d+")
    for line in ("Room 7", "Floor 12"):
        print(number_pattern.findall(line))
    ''',
    "For each match in 'x4 y55', prove that the recorded slice equals the matched text.",
    r'''
    import re
    text = "x4 y55"
    for found in re.finditer(r"\d+", text):
        start, end = found.span()
        print(text[start:end], text[start:end] == found.group(0))
    ''',
    "compile names and reuses a pattern; finditer retains locations. End-exclusive slices reproduce matches. Iterator use is incremental only if you do not collect all results.",
    [
        ("Which operation keeps a Match object for every occurrence?", "finditer", "findall without groups", "str.split", "finditer yields match objects; their group and span methods remain available."),
        ("Does compile always make repeated matching dramatically faster?", "No; clarity and reuse are benefits, and re already caches patterns.", "Yes, in every program.", "It turns regex into native machine code.", "Performance depends on workload; avoid unmeasured blanket claims."),
    ])

add(1, "1. Character classes: a set means one character",
    "Read ranges, negated sets, and Unicode-aware shorthand classes.",
    [
        ("[abc]; [a-z]; [^...]", "A bracket class matches one character from a set or range; a leading ^ inside brackets negates the set. It is not a whole word."),
        (r"\w; \s; \D", r"\w matches Unicode alphanumeric characters plus underscore; \s matches Unicode whitespace; \D is the complement of decimal-digit class \d."),
        ("re.ASCII", r"On a str pattern, ASCII narrows \d, \w, \s and related classes/boundaries to ASCII definitions."),
    ],
    r"Read [A-C] as one character A, B or C. Add + to match a run. [^,]+ means one or more non-comma characters. "
    r"\w is a programming character class, not a complete language-aware definition of a word. It includes underscores and many non-English characters; "
    r"combining marks are not all covered. \d includes Nepali decimal digits; use [0-9] if the required format explicitly permits only ASCII digits.",
    r'[A-Z]+     [0-9]+     [^,]+\n\w+        \s+         \D+',
    r'''
    import re
    print(re.findall(r"[A-C]", "A x C D"))
    print(re.findall(r"\w+", "cat_2 東京"))
    value = "१२"
    print(re.fullmatch(r"\d+", value) is not None)
    print(re.fullmatch(r"[0-9]+", value) is not None)
    print(re.fullmatch(r"\d+", value, flags=re.ASCII) is not None)
    ''',
    "Brackets ले एक पटकमा एउटा character छान्छन्। \u005cw+ ले cat_2 लाई एउटै token मान्छ र 東京 पनि भेट्छ। "
    "१२ decimal digits भएकाले Unicode digit pattern सफल हुन्छ; ASCII-only विकल्प असफल हुन्छन्। "
    "आफ्नो data policy हेरेर class छान; English मात्र हो भन्ने अनुमान नगर।",
    ("[cat] means the complete word cat", "cat means the sequence; [cat] means one of c, a or t",
     "Square brackets choose one character. Character-set membership and a sequence are different operations."),
    "Extract ASCII alphabetic runs from 'room12 floor3'; then extract its digits separately.",
    r'''
    import re
    text = "room12 floor3"
    print(re.findall(r"[A-Za-z]+", text))
    print(re.findall(r"[0-9]+", text))
    ''',
    "Extract non-comma runs from 'one,two,,three'. Explain why the empty field disappears; compare str.split(',').",
    r'''
    import re
    text = "one,two,,three"
    print(re.findall(r"[^,]+", text))
    print(text.split(","))
    ''',
    "A class chooses a character; repetition chooses its count. Unicode and ASCII policies differ. Nonempty-run extraction may discard empty fields, which can change data meaning.",
    [
        ("What does [cat] match?", "One character: c, a or t", "Only the word cat", "All English words", "A bracket class describes alternatives at one character position."),
        ("Does default \\d match Nepali decimal digits?", "Yes", "No, only 0-9", "Only with IGNORECASE", "Default str patterns use Unicode decimal-digit semantics."),
    ])

add(1, "2. Quantifiers: how many repetitions?",
    "Choose required, optional, and bounded repetition without accepting empty input accidentally.",
    [
        ("*; +; ?", "* means zero or more; + means one or more; ? means zero or one occurrence of the preceding token."),
        ("{n}; {m,n}; {m,}", "Brace quantifiers specify an exact count, an inclusive minimum/maximum, or a minimum with no stated maximum."),
    ],
    "A quantifier modifies the token immediately before it: [0-9]{2} requires two digits; A{2} requires AA. "
    "It does not apply to the whole preceding sentence. To repeat a sequence, put it in a group (Day 3). "
    "Zero is permitted by * and ?, so fullmatch can accept the empty string for some patterns. "
    "Build validators by writing accepted and rejected examples before writing the regex.",
    r'A[0-9]{2}     colou?r     [0-9]{2,4}\n[0-9]*        [0-9]+',
    r'''
    import re
    for value in ("A12", "A1", "A123"):
        print(value, re.fullmatch(r"A[0-9]{2}", value) is not None)
    for value in ("color", "colour"):
        print(value, re.fullmatch(r"colou?r", value) is not None)
    print(re.fullmatch(r"[0-9]*", "") is not None)
    print(re.fullmatch(r"[0-9]+", "") is not None)
    ''',
    "A12 मा A पछि ठीक दुई digits छन्। colou?r मा u मात्र optional हो, पूरै colour होइन। "
    "Empty value मा * सफल र + असफल हुन्छ। त्यसैले required input का लागि + वा उचित minimum राख।",
    ("re.fullmatch(r'[0-9]*', '') accepts required numeric input",
     "Use [0-9]+ when at least one digit is required",
     "* explicitly permits zero occurrences, including an empty complete match."),
    "Validate digit strings with length 2 through 4. Test 1, 12, 1234 and 12345.",
    r'''
    import re
    for value in ("1", "12", "1234", "12345"):
        print(value, re.fullmatch(r"[0-9]{2,4}", value) is not None)
    ''',
    "Accept both gray and grey with one bracket class, but reject graay.",
    r'''
    import re
    for value in ("gray", "grey", "graay"):
        print(value, re.fullmatch(r"gr[ae]y", value) is not None)
    ''',
    "Quantifiers apply to the preceding token. Test minimum, maximum, empty, and too-long inputs. Optional spelling characters and optional whole sequences are different.",
    [
        ("Which quantifier means one or more?", "+", "*", "?", "+ has minimum one; * permits zero, ? permits zero or one."),
        ("What does A[0-9]{2} require?", "A followed by exactly two ASCII digits", "Two copies of the complete A-number", "An optional A", "The brace quantifier applies to the digit class immediately before it."),
    ])

add(1, "3. Four phone formats: define the rule first",
    "Validate a deliberately limited format policy with complete-string checks.",
    [
        (r"\( and \): literal parentheses", "Regex parentheses normally form a group. Escaping them matches the actual punctuation characters."),
        ("Format policy vs real-world validity", "A regex can check your chosen text shape. It does not prove that a number exists, belongs to someone, or obeys every country's numbering system."),
    ],
    "Our learning policy accepts exactly four 10-digit layouts: 1234567890, 123-456-7890, 123 456 7890, and (123) 456-7890. "
    "This is not a universal Nepal or Japan phone-number rule. Reject mixed separators, incorrect lengths, and trailing junk. "
    "Use four simple patterns and any(...) now; Day 3 introduces alternation to combine choices. The digits here must be ASCII.",
    r'patterns = [r"[0-9]{10}", r"[0-9]{3}-[0-9]{3}-[0-9]{4}", ...]\nany(re.fullmatch(p, value) is not None for p in patterns)',
    r'''
    import re
    patterns = [
        r"[0-9]{10}",
        r"[0-9]{3}-[0-9]{3}-[0-9]{4}",
        r"[0-9]{3} [0-9]{3} [0-9]{4}",
        r"\([0-9]{3}\) [0-9]{3}-[0-9]{4}",
    ]
    for value in ("1234567890", "123-456-7890", "123 456 7890",
                  "(123) 456-7890", "123-456 7890"):
        valid = any(re.fullmatch(p, value) is not None for p in patterns)
        print(value, valid)
    ''',
    "हरेक pattern एउटा allowed layout हो। any ले कम्तीमा एक layout मिल्यो कि भनेर हेर्छ। "
    "सबैमा fullmatch भएकाले अगाडि वा पछाडि extra text स्वीकारिँदैन। Parentheses देखाउन regex मा escape चाहिन्छ। "
    "देशअनुसार number rules फरक हुन्छन्; production policy छुट्टै तय गर्नुपर्छ।",
    ("Use search to validate a phone field", "Use fullmatch with an explicit allowed-format policy",
     "search can find a valid-looking substring inside an otherwise invalid field."),
    "Check the hyphen layout against a valid value, a short value, and a valid prefix followed by junk.",
    r'''
    import re
    pattern = r"[0-9]{3}-[0-9]{3}-[0-9]{4}"
    for value in ("123-456-7890", "12-456-7890", "123-456-7890junk"):
        print(value, re.fullmatch(pattern, value) is not None)
    ''',
    "Find the literal text '(2026)' in a sentence, including its parentheses.",
    r'''
    import re
    found = re.search(r"\([0-9]{4}\)", "Year (2026) is here")
    if found is not None:
        print(found.group(0))
    ''',
    "Write the accepted format policy before its regex. Escape literal punctuation, reject trailing junk with fullmatch, and separate shape validation from ownership or real-world validity.",
    [
        ("Does a matching phone format prove the number exists?", "No", "Yes", "Only if it has parentheses", "Shape is not reachability, ownership, or every country's numbering policy."),
        ("How do you match a literal opening parenthesis?", r"\(", "(", "[0-9]", "Unescaped parentheses have grouping meaning; escaping makes this punctuation literal."),
    ])

add(1, "4. Flags and the dot: case, lines and newlines",
    "Distinguish IGNORECASE, MULTILINE and DOTALL.",
    [
        (".; escaped dot", "An unescaped dot matches one character except newline by default. Backslash-dot matches an actual dot."),
        ("re.IGNORECASE; re.MULTILINE; re.DOTALL", "IGNORECASE relaxes case matching; MULTILINE changes ^/$ line anchors; DOTALL allows dot to include newline."),
        ("Flag combination with |", "Bitwise OR combines integer flag values: re.IGNORECASE | re.MULTILINE. This is separate from alternation inside a pattern string."),
    ],
    "Change one flag at a time and observe its effect. MULTILINE does not make dot cross newlines; DOTALL does. "
    "^ marks the beginning and $ the end (Day 3 explains the edge cases). With MULTILINE, anchors also operate at line boundaries. "
    "For ordinary Unicode case-insensitive matching, do not assume this performs every language-specific comparison you might need.",
    're.findall(pattern, text, flags=re.IGNORECASE)\nre.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)',
    r'''
    import re
    print(re.findall(r"python", "Python PYTHON python", flags=re.IGNORECASE))
    text = "a\nb"
    print(re.fullmatch(r"a.b", text) is not None)
    print(re.fullmatch(r"a.b", text, flags=re.DOTALL) is not None)
    print(re.search(r"^ERROR", "INFO ready\nERROR disk", flags=re.MULTILINE).group(0))
    ''',
    "पहिलो output मा case फरक भए पनि तीन matches आउँछन्। a र b बीच newline हुँदा default dot असफल हुन्छ; "
    "DOTALL ले सफल बनाउँछ। MULTILINE ले दोस्रो line को सुरुमा ERROR भेट्न मद्दत गर्छ।",
    ("MULTILINE makes . match a newline", "DOTALL changes dot; MULTILINE changes line-anchor behaviour",
     "These flags alter different regex instructions."),
    "Find ERROR at the start of a line, ignoring case, in a two-line message.",
    r'''
    import re
    found = re.search(r"^error", "INFO ready\nError disk",
                      flags=re.IGNORECASE | re.MULTILINE)
    if found is not None:
        print(found.group(0), found.span())
    ''',
    "Require the literal version '1.2'; show why 1.2 without escaping would also match '1x2'.",
    r'''
    import re
    for value in ("1.2", "1x2"):
        print(value, re.fullmatch(r"1.2", value) is not None,
              re.fullmatch(r"1\.2", value) is not None)
    ''',
    "Flags have distinct jobs. Dot is a wildcard, not punctuation, unless escaped. Combine flag constants outside the pattern; Day 3's | inside a pattern means alternatives.",
    [
        ("Which flag makes dot include a newline?", "DOTALL", "MULTILINE", "ASCII", "DOTALL changes the dot; MULTILINE changes ^ and $."),
        ("Which pattern matches a literal 1.2 only?", r"1\.2", "1.2", "1[0-9]2", "An escaped dot is literal, while an unescaped dot is a wildcard."),
    ])

add(2, "1. Anchors and word boundaries: position, not characters",
    "Use start/end positions and explain why a boundary is not a space.",
    [
        ("^; $", "These assert start/end positions. MULTILINE also allows line boundaries. Without MULTILINE, $ can still match just before a final newline."),
        (r"\A; \Z", r"\A asserts the beginning of the entire string; \Z its absolute end. These examples use syntax supported by Python 3.10+, not version-specific newer anchors."),
        (r"\b; zero-width assertion", r"\b asserts a boundary between a \w and a non-\w character, or an appropriate string edge. It consumes no character; it is not a literal space."),
    ],
    "An anchor tests where matching is happening. It does not add a character to group(0). "
    "catfish contains cat but has no boundary after its t. cat_name also has no boundary there because underscore belongs to \\w. "
    "A boundary is based on the regex word class, not a dictionary of real words. For a complete field, fullmatch is usually clearer than assembling anchors.",
    r're.search(r"\bcat\b", text)\nre.fullmatch(r"cat", value)\nre.search(r"\Acat\Z", value)',
    r'''
    import re
    print(re.findall(r"\bcat\b", "cat catfish cat_name (cat)"))
    value = "cat\n"
    print(re.search(r"^cat$", value) is not None)
    print(re.fullmatch(r"cat", value) is not None)
    print(re.search(r"\Acat\Z", value) is not None)
    ''',
    "दुई छुट्टै cat भेटिन्छन्; catfish र cat_name भेटिँदैनन्। 'cat\\n' मा $ ले अन्तिम newline भन्दा अगाडि end position स्वीकार्छ। "
    "fullmatch र absolute end \\Z ले newline बाँकी भएकाले reject गर्छन्। यो सानो फरक validation मा महत्त्वपूर्ण हुन्छ।",
    ("^cat$ always means the exact complete input is cat",
     "Use fullmatch('cat', value) for exact whole-input matching",
     "$ has a final-newline exception; fullmatch must consume the entire string."),
    "Extract standalone ASCII numbers from '12 x12 34 56x' using boundaries; explain excluded values.",
    r'''
    import re
    print(re.findall(r"\b[0-9]+\b", "12 x12 34 56x"))
    ''',
    "Use MULTILINE to find lines beginning INFO, then contrast it with \\A which still requires the string's beginning.",
    r'''
    import re
    text = "WARN first\nINFO second"
    print(re.search(r"^INFO", text, flags=re.MULTILINE) is not None)
    print(re.search(r"\AINFO", text, flags=re.MULTILINE) is not None)
    ''',
    "Anchors and boundaries consume no text. Underscore is a word character. $ permits a position before a final newline; use fullmatch for exact field validation.",
    [
        ("Will \\bcat\\b match cat_name?", "No; underscore is a word character.", "Yes; underscore is always a boundary.", "Only with DOTALL", "No word-to-nonword transition exists after cat here."),
        ("Does $ always mean the absolute string end?", "No; it can match before a final newline.", "Yes, without exceptions.", "It consumes a dollar sign.", "For a strict complete input, prefer fullmatch."),
    ])

add(2, "2. Captures: turn a match into named fields",
    "Capture related pieces, convert values deliberately, and understand findall's result shape.",
    [
        ("(pattern); group(1); groups()", "Parentheses capture a submatch. Numbering starts at 1, group(0) is the whole match, and groups() returns the captured subgroups as a tuple."),
        ("(?P<name>pattern); groupdict()", "A named group labels a field. groupdict returns name-to-captured-text mappings; the field values are still strings."),
        ("findall and capture count", "No capture groups: full-match strings. One group: that group's strings. Multiple groups: tuples of captured strings."),
    ],
    "Parse the structure into fields rather than repeatedly splitting an uncertain format. "
    "books=12 has a label and a quantity. Capture each; then convert quantity to int. "
    "A successful digit capture does not establish a domain rule such as quantity <= stock. A date-shaped capture likewise does not prove the date exists.",
    r'pattern = r"(?P<name>[A-Za-z]+)=(?P<count>[0-9]+)"\nfound.group("count")\nfound.groupdict()',
    r'''
    import re
    pattern = r"(?P<name>[A-Za-z]+)=(?P<count>[0-9]+)"
    found = re.fullmatch(pattern, "books=12")
    if found is not None:
        print(found.group(0))
        print(found.groups())
        print(found.groupdict())
        print(int(found.group("count")) + 1)
    text = "a1 b22"
    print(re.findall(r"[a-z][0-9]+", text))
    print(re.findall(r"[a-z]([0-9]+)", text))
    print(re.findall(r"([a-z])([0-9]+)", text))
    ''',
    "पूरा match books=12 हो; captures books र 12 हुन्। groupdict ले field names दिन्छ, int ले संख्या बनाउँछ। "
    "तलका तीन findall का patterns मिल्दोजुल्दो भए पनि capture count फरक भएकाले result shape फरक छ। "
    "आफ्नो loop ले string चाहन्छ कि tuple भन्ने कुरा पहिले बुझ।",
    ("Treat found.group('count') as an integer automatically",
     "count = int(found.group('count'))",
     "Regex returns captured text. Conversion and range validation are separate steps."),
    "Capture name and score from 'Sita:90', print the named dictionary, then check that score is between 0 and 100.",
    r'''
    import re
    found = re.fullmatch(r"(?P<name>[A-Za-z]+):(?P<score>[0-9]+)", "Sita:90")
    if found is not None:
        fields = found.groupdict()
        score = int(fields["score"])
        print(fields)
        print(0 <= score <= 100)
    ''',
    "Capture year, month and day from '2026-02-31'. Show that this format matches, then explain why calendar checking is still needed (Day 6).",
    r'''
    import re
    found = re.fullmatch(
        r"(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})",
        "2026-02-31")
    if found is not None:
        print(found.groupdict())
        print("shape matches; calendar not checked")
    ''',
    "Capture names make field intent explicit. group(0) remains the whole match. Convert numeric fields and validate domain rules separately. Capture count changes findall's return shape.",
    [
        ("What type is a captured numeric group on a str pattern?", "str", "int", "float", "Matching does not perform numeric conversion."),
        ("What does findall return when the pattern has two capture groups?", "A list of tuples of captured strings", "Only the entire match strings", "A dictionary automatically", "Multiple captures produce one tuple per occurrence."),
    ])

add(2, "3. Alternation and noncapturing groups",
    "Group alternative sequences without creating unwanted captured fields.",
    [
        ("| inside a pattern", "Alternation chooses among branches. Python tries branches left to right; a successful earlier branch need not be the longest possible one."),
        ("(?:...)", "A noncapturing group organises a sequence or alternatives without adding a numbered capture or changing findall's capture shape."),
        ("Alternation precedence", "Anchors on separate ungrouped branches do not automatically apply to every alternative. Group the alternatives or use fullmatch."),
    ],
    "cat|dog means cat or dog. ^cat|dog$ instead means 'cat at the beginning' OR 'dog at the end', "
    "not necessarily the complete value cat or dog. fullmatch with a grouped choice expresses complete-input intent clearly. "
    "Use capture groups for fields you want back, and noncapturing groups for structure only.",
    r're.fullmatch(r"(?:cat|dog)", value)\nr"(?P<method>GET|POST) /[A-Za-z]+"',
    r'''
    import re
    for value in ("cat", "dog", "catfish"):
        print(value, re.fullmatch(r"(?:cat|dog)", value) is not None)
    print(re.search(r"cat|caterpillar", "caterpillar").group(0))
    print(re.search(r"caterpillar|cat", "caterpillar").group(0))
    print(re.search(r"^cat|dog$", "catfish") is not None)
    ''',
    "पहिलो loop पूरा value जाँच्छ। search मा cat पहिला लेख्दा caterpillar भित्रको cat नै पहिलो सफल branch हुन्छ। "
    "यो 'सबैभन्दा लामो branch खोज्ने' नियम होइन। अन्तिम example मा ungrouped anchors ले catfish स्वीकारेको कारण बुझेर मात्र pattern बदल।",
    ("^cat|dog$ for exact cat-or-dog validation",
     "re.fullmatch(r'(?:cat|dog)', value)",
     "The alternation splits the anchors across branches. Grouping plus fullmatch avoids the accidental prefix/suffix acceptance."),
    "Parse 'GET /books' and 'POST /items' into named method and path fields; reject 'DELETE /books'.",
    r'''
    import re
    pattern = r"(?P<method>GET|POST) (?P<path>/[A-Za-z]+)"
    for line in ("GET /books", "POST /items", "DELETE /books"):
        found = re.fullmatch(pattern, line)
        print(found.groupdict() if found is not None else "rejected")
    ''',
    "Find A12 and B34, but return only their numeric fields; use a noncapturing A/B choice.",
    r'''
    import re
    print(re.findall(r"(?:A|B)([0-9]+)", "A12 B34 C56"))
    ''',
    "Alternation tries branches left to right. Use noncapturing groups for structure, named captures for data, and fullmatch for complete-field validation.",
    [
        ("Which group does not create a captured result?", "(?:...)", "(...)", "(?P<name>...)", "The ?: prefix groups structurally without capturing."),
        ("What does search('cat|caterpillar', 'caterpillar') select?", "cat", "caterpillar always", "No match", "The first branch already succeeds at the same starting position."),
    ])

add(2, "4. Literal input and backreferences",
    "Escape dynamic literal text and compare a capture with later text.",
    [
        ("re.escape", "escape turns a literal string into a pattern fragment that matches its regex-special characters literally. It is for patterns, not replacement templates."),
        (r"\1; (?P=name)", "A backreference requires the same text as an earlier captured group. Numbered and named forms refer to the group; they do not rerun its pattern."),
        ("re.error", "The regex exception used here for invalid pattern syntax. Catch a compile error without running a malformed pattern."),
    ],
    "A search term supplied as ordinary text may contain +, ., [, or other regex punctuation. "
    "If the intent is literal matching, escape it before adding it to a pattern; for a plain substring search, string methods remain simpler. "
    "A backreference can detect adjacent duplicate words because the second word must equal the first capture. "
    "This exercise uses ASCII letters and case-sensitive comparison; it is not a universal language tokenizer.",
    r're.search(re.escape(literal), text)\nr"(?P<word>[A-Za-z]+)\s+(?P=word)"',
    r'''
    import re
    literal = "a+b"
    print(re.search(literal, "aaab").group(0))
    print(re.search(re.escape(literal), "aaab") is None)
    print(re.search(re.escape(literal), "use a+b here").group(0))
    pattern = r"\b(?P<word>[A-Za-z]+)\s+(?P=word)\b"
    for found in re.finditer(pattern, "go go then move move"):
        print(found.group(0), found.group("word"))
    ''',
    "Unescaped a+b को अर्थ धेरै a अनि b हो; literal plus होइन। escape गरेपछि a+b नै चाहिन्छ। "
    "Duplicate-word pattern मा पहिलो word capture हुन्छ र दोस्रोले त्यही text दोहोर्‍याउनुपर्छ। "
    "Same shape भएका go र do ले match गर्दैनन्—same text हुनुपर्छ।",
    ("Use re.escape to fix a replacement template", "Use re.escape only for literal pattern fragments",
     "Replacement strings have their own syntax. Day 4 uses a callback to insert replacement text literally."),
    "Search for the literal '[draft]' in a message and show its complete matched punctuation.",
    r'''
    import re
    found = re.search(re.escape("[draft]"), "file [draft] ready")
    if found is not None:
        print(found.group(0))
    ''',
    "Use a numbered backreference to find 'yes yes', then catch the compile error for an unclosed bracket pattern.",
    r'''
    import re
    found = re.search(r"\b([A-Za-z]+)\s+\1\b", "yes yes no")
    if found is not None:
        print(found.group(0))
    try:
        re.compile("[")
    except re.error:
        print("invalid pattern rejected")
    ''',
    "Dynamic literal text is not a regex program: escape it or use literal string operations. Backreferences compare captured text, not just its shape. Handle invalid pattern syntax without running it.",
    [
        ("What is re.escape intended to prepare?", "A literal pattern fragment", "A replacement template", "An encrypted password", "It escapes regex punctuation for use on the pattern side."),
        ("What does a backreference require?", "The text captured by the referenced group", "Any text with the same character count", "A new match with the same pattern", "A backreference reuses the captured value."),
    ])

add(3, "1. Substitution: produce new text and count changes",
    "Replace matches deliberately, preserve line breaks when needed, and retain the returned value.",
    [
        ("re.sub; re.subn", "sub returns a new string with replacements. subn returns (new_string, replacement_count). Neither changes the original string in place."),
        ("count argument", "count limits the number of replacements when positive; its default 0 means replace all occurrences."),
        ("Whitespace policy", r"\s+ includes line breaks. [ \t]+ collapses only space/tab runs, preserving line separators."),
    ],
    "Text cleaning changes information. Decide whether paragraph boundaries should survive before choosing a whitespace pattern. "
    "Replacing all \\s+ with one space flattens lines; that may be good for a one-line field but bad for paragraphs or logs. "
    "Assign the returned string. strip removes outer whitespace separately. Count replacements when you want an audit of the transformation.",
    'cleaned = re.sub(pattern, replacement, text)\ncleaned, count = re.subn(pattern, replacement, text)',
    r'''
    import re
    text = "A   B\nC\t D"
    flattened = re.sub(r"\s+", " ", text)
    kept_lines = re.sub(r"[ \t]+", " ", text)
    print(repr(text))
    print(repr(flattened))
    print(repr(kept_lines))
    print(re.subn(r"[0-9]+", "#", "id12 id34"))
    print(re.sub(r"[0-9]+", "#", "id12 id34", count=1))
    ''',
    "Original string उस्तै रहन्छ। flattened मा newline पनि space भयो; kept_lines मा newline बच्यो। "
    "subn ले cleaned text सँग दुई replacements भएको count दिन्छ। count=1 ले पहिलो numeric run मात्र बदल्छ।",
    ("re.sub(pattern, replacement, text)\nprint(text)",
     "text = re.sub(pattern, replacement, text)\nprint(text)",
     "Python strings are immutable; ignoring the returned result leaves your variable unchanged."),
    "Normalise '  hello\\t\\tworld\\nagain  ' into one stripped line, and print the original with repr too.",
    r'''
    import re
    text = "  hello\t\tworld\nagain  "
    cleaned = re.sub(r"\s+", " ", text).strip()
    print(repr(text))
    print(cleaned)
    ''',
    "Collapse spaces/tabs but preserve the newline in 'a   b\\nc\\t d'. Use subn to show how many runs changed.",
    r'''
    import re
    cleaned, count = re.subn(r"[ \t]+", " ", "a   b\nc\t d")
    print(repr(cleaned))
    print(count)
    ''',
    "Replacement returns a new string. Whitespace policy is a data decision; \\s includes newlines. subn counts replacements, not characters changed.",
    [
        ("Does re.sub modify its input string in place?", "No; it returns a new string.", "Yes", "Only when count=0", "Strings are immutable, and sub returns its transformed result."),
        ("Which pattern collapses spaces/tabs while preserving newlines?", r"[ \t]+", r"\s+", ".", r"\s includes newline; the explicit space/tab class does not."),
    ])

add(3, "2. Replacement templates and callback functions",
    "Reorder captured fields and compute replacement text with a function.",
    [
        (r"\g<name>; \g<1> replacement template", "In a replacement string these insert a captured group. The angle-bracket form makes the group reference unambiguous."),
        ("Replacement callback", "Pass a function as the replacement. For every Match, re calls the function, which must return the replacement string."),
        ("Literal callback result", "A callback's returned string is inserted literally; it is not parsed as a backreference template."),
    ],
    "A replacement template can rearrange a date's fields; that only changes its text shape, not its calendar validity. "
    "A callback can convert captured digits to int, compute a result, then return str(result). "
    "Returning an integer is an error: text replacement needs text. If replacement data contains backslashes intended literally, "
    "a callback avoids accidental interpretation as group references. Do not apply re.escape to replacement data.",
    r're.sub(pattern, r"\g<year>-\g<month>-\g<day>", text)\nre.sub(pattern, replacement_function, text)',
    r'''
    import re
    pattern = r"(?P<day>[0-9]{2})/(?P<month>[0-9]{2})/(?P<year>[0-9]{4})"
    print(re.sub(pattern, r"\g<year>-\g<month>-\g<day>", "on 10/10/2026"))
    def double(found):
        return str(int(found.group(0)) * 2)
    print(re.sub(r"[0-9]+", double, "5 apples, 12 pears"))
    literal = r"\g<1>"
    print(re.sub(r"X", lambda found: literal, "X X"))
    ''',
    "Date template ले captured year/month/day नयाँ क्रमले राख्छ। double function हरेक numeric Match मा बोलिन्छ। "
    "अन्तिम callback ले backslash सहितको text जस्ताको तस्तै राख्छ; group reference झैँ चलाउँदैन। "
    "lambda Week 10 मा पढेको सानो function हो; चाहिँदा सामान्य def प्रयोग गर्न सकिन्छ।",
    ("def replacement(found): return int(found.group(0)) * 2",
     "def replacement(found): return str(int(found.group(0)) * 2)",
     "A callback must return a string when replacing within a str input."),
    "Turn 'Sita=90 Hari=80' into '90:Sita 80:Hari' with named captures and a replacement template.",
    r'''
    import re
    pattern = r"(?P<name>[A-Za-z]+)=(?P<score>[0-9]+)"
    print(re.sub(pattern, r"\g<score>:\g<name>", "Sita=90 Hari=80"))
    ''',
    "Replace each price in 'price=100 price=250' with a price increased by 10, preserving the prefix. Write a named callback.",
    r'''
    import re
    def increase(found):
        amount = int(found.group("amount"))
        return "price=" + str(amount + 10)
    print(re.sub(r"price=(?P<amount>[0-9]+)", increase, "price=100 price=250"))
    ''',
    "Templates rearrange captured text; callbacks compute new text. Callback return values must be strings and are inserted literally. Date shape and calendar validity remain separate.",
    [
        ("What must a replacement callback return for str input?", "str", "int", "A list of Match objects", "Text substitution requires a string for each replacement."),
        ("Is callback output parsed again as a replacement template?", "No; it is inserted literally.", "Yes, always.", "Only if it has a digit", "A callback can safely insert literal backslash text without template interpretation."),
    ])

add(3, "3. Splitting and a small cleaning pipeline",
    "Split on explicit delimiters and separate transformations into testable steps.",
    [
        ("re.split; maxsplit", "split divides text at pattern matches. maxsplit limits splits, leaving the remaining suffix intact."),
        ("Capturing separators in split", "A capturing group in the separator pattern causes separator text to appear in the result too."),
        ("Pipeline; idempotence", "A pipeline performs named steps in order. An idempotent cleaner produces the same result when applied again; test this where your policy expects it."),
    ],
    "For a deliberately simple list format, split on comma or semicolon, strip each field, and decide explicitly whether empty fields matter. "
    "Do not drop an empty field in a table merely because it looks inconvenient. Our word-list exercise discards empty items by policy. "
    "A real CSV parser must handle quoting and embedded delimiters; Day 6 uses csv.reader instead. "
    "Whitespace, case and dates each need their own rule: upper/lower casing can destroy case-sensitive identifiers, "
    "and a date reorder needs calendar validation if correctness matters.",
    r'parts = re.split(r"[,;]", text)\ncleaned = [part.strip() for part in parts]\nkept = [part for part in cleaned if part]',
    r'''
    import re
    text = "one,two;three"
    print(re.split(r"[,;]", text))
    print(re.split(r"([,;])", text))
    print(re.split(r"[,;]", text, maxsplit=1))
    def clean_words(value):
        parts = re.split(r"[,;]", value.strip())
        return [re.sub(r"\s+", " ", part).strip().lower()
                for part in parts if part.strip()]
    print(clean_words("  RED  APPLE; BLUE\tBERRY,, "))
    ''',
    "पहिलो split ले delimiters हटाउँछ; parentheses भएको अर्को pattern ले ती पनि result मा राख्छ। "
    "maxsplit=1 पछि बाँकी suffix उस्तै रहन्छ। Function ले क्रमैसँग split, whitespace cleanup, outer trim र lowercase गर्छ। "
    "यो simple word list को policy हो, quoted CSV को होइन।",
    ("Use re.split(',') to parse every possible CSV row",
     "Use csv.reader for CSV; use regex splitting only for your explicitly simple delimiter format",
     "A quoted field may contain a comma that is not a separator."),
    "Clean '  Python ; REGEX,, text  ' into lowercase nonempty words with comma/semicolon separators.",
    r'''
    import re
    text = "  Python ; REGEX,, text  "
    words = [part.strip().lower() for part in re.split(r"[,;]", text)
             if part.strip()]
    print(words)
    ''',
    "Write a one-line cleaner that strips edges, collapses whitespace and lowercases a label. Assert that cleaning twice gives the same result.",
    r'''
    import re
    def clean_label(value):
        return re.sub(r"\s+", " ", value).strip().lower()
    once = clean_label("  MY\t Study  ")
    assert clean_label(once) == once
    print(once)
    print("idempotence passed")
    ''',
    "Keep each cleaning policy explicit and testable. Captured separators change split output. Empty-field removal and lowercasing are decisions, not universally safe defaults.",
    [
        ("Why are commas included in re.split(r'(,)', text)?", "The separator is captured.", "split always retains separators.", "DOTALL is enabled.", "Capturing groups insert matched separator text into the result."),
        ("What does maxsplit=1 mean?", "Split at most once; keep the remaining suffix.", "Keep only one output field.", "Remove one character.", "One split usually creates two pieces, with the second containing unsplit remainder."),
    ])

add(4, "1. Greedy and lazy: where should a match stop?",
    "Trace consumption and choose a clear delimiter-aware pattern for simple flat text.",
    [
        ("Greedy repetition", "Quantifiers such as * and + initially consume as much as possible while allowing the remainder of the pattern to succeed."),
        ("Lazy repetition: *?; +?", "Adding ? to a quantifier makes it try the smallest consumption first, expanding as necessary. This differs from ? used alone as optionality."),
        ("Negated delimiter class", "For a simple flat delimiter format, a class such as [^>] explicitly refuses the closing delimiter rather than relying on wildcard preference."),
    ],
    "On '<one> <two>', <.*> can span from the first opening angle bracket to the final closing one. "
    "<.*?> instead tries a shorter body first and finds each flat token. <[^>]*> states that the body cannot contain >. "
    "None of these is a complete HTML parser: quoted attributes, nesting, comments and malformed documents require a parser and a defined policy. "
    "The examples intentionally use flat, unescaped toy delimiters.",
    r'<.*>     <.*?>     <[^>]*>',
    r'''
    import re
    text = "<one> <two>"
    print(re.findall(r"<.*>", text))
    print(re.findall(r"<.*?>", text))
    print(re.findall(r"<[^>]*>", text))
    print(re.findall(r"<([^<>]*)>", text))
    ''',
    "Greedy body ले अन्तिम > सम्म जान सक्छ; lazy ले पहिलो सफल > मा रोकिने प्रयास गर्छ। "
    "Negated class ले > लाई body मा अनुमति दिँदैन। अन्तिम pattern मा capture भएका कारण tokens होइन, भित्रको content आउँछ। "
    "यो नियम flat अभ्यासका लागि हो; वास्तविक HTML मा blindly चलाउने होइन।",
    ("<.*> extracts each independent tag reliably",
     "For flat toy delimiters compare <.*?> and <[^>]*>; for actual HTML use a parser",
     "Greedy wildcard can overmatch, and HTML has structure beyond a flat delimiter regex."),
    "Extract 'red' and 'blue' from '[red] [blue]' without including square brackets; reject nested brackets in the body by your class.",
    r'''
    import re
    print(re.findall(r"\[([^\[\]]*)\]", "[red] [blue]"))
    ''',
    "Compare greedy and lazy quoted-string extraction on '\"one\" and \"two\"'. State that this toy format does not support escaped quotes.",
    r'''
    import re
    text = '"one" and "two"'
    print(re.findall(r'".*"', text))
    print(re.findall(r'".*?"', text))
    print("toy quotes only; escapes not supported")
    ''',
    "Greedy and lazy are search preferences, not universal correctness or speed guarantees. State delimiter assumptions. Use a parser for real nested or quoted formats.",
    [
        ("What does <.*> find in '<one> <two>'?", "<one> <two>", "Only <one>", "Only the word one", "The greedy dot-star can consume up to the last closing delimiter."),
        ("Does lazy matching turn a regex into a full HTML parser?", "No", "Yes", "Only with MULTILINE", "Preference for shorter matches does not implement HTML grammar."),
    ])

add(4, "2. Lookahead: inspect what follows without consuming it",
    "Add a following-context condition while returning only the wanted text.",
    [
        ("(?=...): positive lookahead", "At the current position, the following pattern must match. A lookahead consumes no characters in the outer match."),
        ("(?!...): negative lookahead", "The following pattern must not match. A negative condition excludes only what it states; it does not imply a word boundary."),
    ],
    "In [0-9]+(?= USD), the digits belong to the result and the following space/USD is a condition. "
    "The currency text is not part of group(0). cat(?!fish) prevents an immediate fish suffix, but catnap still matches its cat prefix. "
    "If you need a whole word, say so with appropriate boundaries. Combine restrictions carefully and test longer words as well as happy paths.",
    r'[0-9]+(?= USD)\n\bcat\b(?!:)',
    r'''
    import re
    text = "10 USD, 20 EUR, 30 USD"
    for found in re.finditer(r"[0-9]+(?= USD)", text):
        print(found.group(0), found.span())
    print(re.findall(r"cat(?!fish)", "catfish catnap cat"))
    print(re.findall(r"\bcat\b(?!:)", "cat: cat catfish"))
    ''',
    "Lookahead को USD text output मा समावेश हुँदैन। Negative lookahead ले fish मात्र निषेध गर्छ; "
    "catnap मा nap भएकाले अझै cat भेटिन्छ। Whole-word आवश्यकता छ भने boundary चाहिन्छ। "
    "cat: मा colon तत्काल पछाडि भएकाले अन्तिम pattern ले त्यो word हटाउँछ।",
    ("cat(?!fish) means only the whole word cat",
     r"Use \bcat\b when a whole regex-word occurrence is required",
     "Negative lookahead rejects the stated suffix, not every other possible suffix."),
    "Extract integer quantities immediately followed by ' kg' from '3 kg, 7 m, 12 kg'. Do not consume the unit.",
    r'''
    import re
    print(re.findall(r"[0-9]+(?= kg)", "3 kg, 7 m, 12 kg"))
    ''',
    "Find whole ASCII-letter words that are not immediately followed by a colon in 'name: ready status: good'.",
    r'''
    import re
    print(re.findall(r"\b[A-Za-z]+\b(?!:)", "name: ready status: good"))
    ''',
    "Lookahead is a zero-width following-context condition. It does not consume the condition's text. Negative conditions are narrow; boundaries and format policies remain your responsibility.",
    [
        ("Does [0-9]+(?= USD) include USD in group(0)?", "No", "Yes", "Only if USD is uppercase", "Only the digit portion is consumed by the outer match."),
        ("Does cat(?!fish) match a prefix of catnap?", "Yes", "No", "Only when escaped", "The immediate suffix is nap, not fish; no whole-word boundary was requested."),
    ])

add(4, "3. Lookbehind: fixed-width context on the left",
    "Use a fixed-width preceding condition and replace variable-width lookbehind with captures.",
    [
        ("(?<=...); (?<!...)", "Positive/negative lookbehind test text immediately before the current position without consuming it."),
        ("Fixed-width restriction", "Python re requires the inside of a lookbehind to have a fixed length. A variable-length + repetition inside it is rejected."),
        ("Capture the prefix instead", "When preceding context has variable length, match the context normally and capture just the field you want back."),
    ],
    "USD plus one space is four characters, so (?<=USD ) has a fixed width. "
    "USD followed by one-or-more whitespace characters has variable width and is not accepted as a Python re lookbehind. "
    "You do not need a new package to solve that exercise: match the variable prefix normally, then return a named amount capture. "
    "Do not disguise the prefix as fixed width if your actual input permits multiple spaces.",
    r'(?<=USD )[0-9]+\nUSD\s+(?P<amount>[0-9]+)',
    r'''
    import re
    print(re.findall(r"(?<=USD )[0-9]+", "USD 10 EUR 20 USD 30"))
    try:
        re.compile(r"(?<=USD\s+)[0-9]+")
    except re.error:
        print("variable-width lookbehind rejected")
    pattern = r"USD\s+(?P<amount>[0-9]+)"
    for found in re.finditer(pattern, "USD  10 and USD\t30"):
        print(found.group("amount"))
    ''',
    "Fixed-width lookbehind ले amount मात्र निकाल्छ। Compile भएको बेला variable-width pattern reject हुन्छ; "
    "यसलाई matching failure भनेर नबुझ। वैकल्पिक pattern मा पूरा prefix match हुन्छ तर हामी amount group मात्र लिन्छौँ।",
    (r"(?<=USD\s+)[0-9]+", r"USD\s+(?P<amount>[0-9]+)",
     "Standard re rejects variable-width lookbehind; consuming the prefix and selecting a capture expresses the same extraction goal."),
    "Extract amounts after literal 'NPR ' using fixed-width positive lookbehind.",
    r'''
    import re
    print(re.findall(r"(?<=NPR )[0-9]+", "NPR 500 USD 20 NPR 750"))
    ''',
    "Support one or more spaces or tabs after NPR without lookbehind. Return only the named amount.",
    r'''
    import re
    pattern = r"NPR[ \t]+(?P<amount>[0-9]+)"
    for found in re.finditer(pattern, "NPR  500; NPR\t750"):
        print(found.group("amount"))
    ''',
    "Lookbehind inspects preceding context without consuming it, but Python re requires fixed width. A normal prefix match plus a named capture is often simpler for variable-length context.",
    [
        ("Can Python re compile (?<=USD\\s+)[0-9]+?", "No; the lookbehind has variable width.", "Yes, always.", "Only with DOTALL", "+ allows different lengths in the lookbehind."),
        ("How can you extract after a variable-length prefix?", "Match the prefix and select a named captured field.", "Ignore all compile errors.", "Use a greedy dot for every field.", "Capturing the desired field avoids the fixed-width lookbehind restriction."),
    ])

add(4, "4. Backtracking, bounded inputs and simpler patterns",
    "Recognise ambiguous repetition and define limits without running a pathological example.",
    [
        ("Backtracking", "A regex engine may retry earlier choices when a later part fails. Overlapping nested repetitions can create a very large number of alternatives."),
        ("Catastrophic backtracking", "Certain ambiguous patterns can take excessive time on crafted failing input. Pattern shape and input size both matter."),
        ("Input bound; no built-in per-match timeout", "Standard re does not accept a per-match timeout argument. Limit input lengths and prefer simple bounded patterns; a hard timeout needs isolation or other deliberate tooling."),
    ],
    "Consider (a+)+$ conceptually: the same run of a characters can be divided among inner repetitions in many ways. "
    "A failing suffix can force extensive retrying. We intentionally do not run a large dangerous example. "
    "Making a quantifier lazy is not proof of linear time. For a small identifier, say exactly what is permitted and limit its length. "
    "Validate with explicit exceptions, not assertions that may disappear under python -O. A length cap is one defence, not a proof that arbitrary untrusted regex is safe.",
    'if len(value) > limit:\n    raise ValueError("input too long")\nvalid = re.fullmatch(r"[A-Z]{1,3}[0-9]{1,4}", value) is not None',
    r'''
    import re
    def valid_code(value):
        if len(value) > 7:
            return False
        return re.fullmatch(r"[A-Z]{1,3}[0-9]{1,4}", value) is not None
    for value in ("A1", "ABC1234", "ABCD1", "A", "A" * 100):
        print(repr(value[:12]), valid_code(value))
    print("nested ambiguous repetition discussed, not executed")
    ''',
    "Allowed code मा 1–3 uppercase letters र 1–4 digits हुन्छन्, त्यसैले maximum 7 हो। "
    "लामो input regex चलाउनुअघि reject हुन्छ। Ambiguous nested example पढेर यसको समस्या बुझ; "
    "त्यसलाई लामो failing input मा चलाउन आवश्यक छैन।",
    ("Changing (a+)+$ to a lazy version guarantees safe runtime",
     "Remove ambiguous nesting, constrain the format, and limit input",
     "Lazy preference alone does not eliminate costly backtracking. Standard re has no per-match timeout parameter."),
    "Validate a lowercase ASCII username of length 3 through 12, rejecting shorter, longer and uppercase examples.",
    r'''
    import re
    def valid_user(value):
        return len(value) <= 12 and re.fullmatch(r"[a-z]{3,12}", value) is not None
    for value in ("sita", "ab", "Sita", "a" * 13):
        print(value, valid_user(value))
    ''',
    "Check an ASCII 4-digit PIN with a direct length/character test, then compare it with a bounded regex.",
    r'''
    import re
    for value in ("1234", "12", "१२३४", "12x4"):
        direct = len(value) == 4 and all("0" <= ch <= "9" for ch in value)
        regex = re.fullmatch(r"[0-9]{4}", value) is not None
        assert direct == regex
        print(value, direct)
    ''',
    "Simple bounded patterns and ordinary string checks are often best. Avoid overlapping nested repetition and unbounded untrusted inputs. Do not promise a timeout that standard re does not provide.",
    [
        ("Does making a pattern lazy guarantee linear runtime?", "No", "Yes", "Only on Windows", "Matching preference does not prove computational complexity."),
        ("Does standard re.search accept timeout=1?", "No", "Yes", "Only for compiled patterns", "A hard deadline needs a different explicitly designed mechanism, such as process isolation."),
    ])

add(5, "1. Email shapes and URL candidates: honest limits",
    "Separate candidate extraction, simple shape checks, and real-world validity.",
    [
        ("urllib.parse.urlsplit", "The standard-library URL parser separates scheme, network location, path, query and fragment. Parsing a URL does not prove it is safe or reachable."),
        ("Candidate extraction", "A regex can locate possible values for a later parser. A candidate is not automatically valid."),
        ("rstrip(character_set)", "rstrip removes any run of characters from the supplied set at the right edge; it does not remove one fixed suffix."),
    ],
    "For practice, accept a simple email shape with non-whitespace text on both sides of one @ and a later dot. "
    "This deliberately limited rule is not a complete internet email-address validator, and cannot establish mailbox ownership. "
    "For links, extract http/https candidates and inspect urlsplit fields. Our trailing-punctuation trimming is only a prose heuristic: "
    "a real URL can legitimately end in a dot, comma or parenthesis, so trimming may alter it. These examples make no network requests.",
    r're.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value)\nurlsplit(candidate)',
    r'''
    import re
    from urllib.parse import urlsplit
    email_shape = r"[^\s@]+@[^\s@]+\.[^\s@]+"
    for value in ("sita@example.com", "bad@@example.com", "no-at.example"):
        print(value, re.fullmatch(email_shape, value) is not None)
    text = "Read https://example.com/a, then http://example.org/b."
    for candidate in re.findall(r"https?://[^\s]+", text):
        candidate = candidate.rstrip(".,)")
        parsed = urlsplit(candidate)
        print(parsed.scheme, parsed.hostname, parsed.path)
    ''',
    "Regex ले candidate text निकाल्छ; urlsplit ले त्यसको भाग छुट्याउँछ। Hostname देखियो भन्दैमा link सुरक्षित वा चल्ने हो भन्ने प्रमाण होइन। "
    "Email format मिल्यो भन्दैमा account अस्तित्वमा छ भन्ने पनि होइन। यहाँ real addresses मा message वा request पठाइँदैन।",
    ("A short regex proves every matching email/URL is real and safe",
     "State the shape policy, parse candidates, and keep ownership/reachability/safety checks separate",
     "Text matching and parsing do not perform real-world verification."),
    "Test the limited email shape against a valid-looking address, missing dot, double @ and an embedded space.",
    r'''
    import re
    pattern = r"[^\s@]+@[^\s@]+\.[^\s@]+"
    for value in ("a@b.co", "a@b", "a@@b.co", "a b@c.co"):
        print(repr(value), re.fullmatch(pattern, value) is not None)
    ''',
    "Extract two HTTP(S) candidates and print each query separately. Preserve the exact candidates rather than automatically trimming punctuation.",
    r'''
    import re
    from urllib.parse import urlsplit
    text = "https://example.com/search?q=python http://example.org/page?id=2"
    for candidate in re.findall(r"https?://[^\s]+", text):
        print(candidate, urlsplit(candidate).query)
    ''',
    "Be honest about deliberately limited email checks and prose URL heuristics. Parsing is not validation, safety or ownership. Preserve raw candidates when cleaning would lose information.",
    [
        ("Does matching the simple email shape prove a mailbox exists?", "No", "Yes", "Only if it ends in .com", "Existence and ownership are outside this text-format check."),
        ("What does rstrip('.,)') remove?", "Any trailing run of those characters", "Only the exact suffix '.,)'", "All punctuation anywhere", "rstrip uses a character set, and can alter legitimate URL endings."),
    ])

add(5, "2. Dates: format first, calendar second",
    "Normalise three chosen date layouts while rejecting impossible calendar dates.",
    [
        ("datetime.date", "date(year, month, day) represents a calendar date and raises ValueError for an impossible combination."),
        ("date.isoformat()", "isoformat produces a consistent YYYY-MM-DD representation of a validated date."),
        ("A declared date-order policy", "Here slashes/dots mean DD/MM/YYYY and DD.MM.YYYY. These are not guessed from locale or interpreted as month-first."),
    ],
    "A digit-count regex happily captures 2026-02-31; the calendar must reject it. "
    "Accept exactly ISO YYYY-MM-DD, day-first DD/MM/YYYY, and day-first DD.MM.YYYY in this exercise. "
    "Compile three patterns with the same named fields, convert those strings to int, and construct date. "
    "Catch the intended ValueError at the caller. Do not silently swap day and month when a date is ambiguous.",
    'fields = found.groupdict()\nchecked = date(int(fields["year"]), int(fields["month"]), int(fields["day"]))\nchecked.isoformat()',
    r'''
    import re
    from datetime import date
    patterns = [
        r"(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})",
        r"(?P<day>[0-9]{2})/(?P<month>[0-9]{2})/(?P<year>[0-9]{4})",
        r"(?P<day>[0-9]{2})\.(?P<month>[0-9]{2})\.(?P<year>[0-9]{4})",
    ]
    def normalise(value):
        for pattern in patterns:
            found = re.fullmatch(pattern, value)
            if found is not None:
                fields = found.groupdict()
                checked = date(int(fields["year"]), int(fields["month"]), int(fields["day"]))
                return checked.isoformat()
        raise ValueError("unsupported date format")
    for value in ("2026-10-09", "09/10/2026", "09.10.2026", "2026-02-31"):
        try:
            print(value, normalise(value))
        except ValueError:
            print(value, "rejected")
    ''',
    "तीन layouts बाट एउटै field names पाइन्छन्, त्यसैले एउटै date constructor प्रयोग हुन्छ। "
    "09/10/2026 को हाम्रो policy October 9 हो। date ले February 31 reject गर्छ; "
    "regex ले shape जाँच्यो भन्दैमा असम्भव date बच्दैन। isoformat ले valid results एउटै क्रममा देखाउँछ।",
    ("Regex digits alone prove a date is valid", "Construct datetime.date after capturing numeric fields",
     "Calendar rules, including leap years, require semantic validation."),
    "Compare February 29 in leap year 2024 and non-leap year 2025 using date, catching invalid input.",
    r'''
    from datetime import date
    for year in (2024, 2025):
        try:
            print(date(year, 2, 29).isoformat())
        except ValueError:
            print(year, "invalid leap day")
    ''',
    "Create a cleaning pipeline for '  On\\t09/10/2026  '. Collapse whitespace, lowercase the prose, capture the date and replace it through a calendar-validating callback.",
    r'''
    import re
    from datetime import date
    def replace_date(found):
        checked = date(int(found.group("year")), int(found.group("month")),
                       int(found.group("day")))
        return checked.isoformat()
    text = "  On\t09/10/2026  "
    text = re.sub(r"\s+", " ", text).strip().lower()
    pattern = r"\b(?P<day>[0-9]{2})/(?P<month>[0-9]{2})/(?P<year>[0-9]{4})\b"
    print(re.sub(pattern, replace_date, text))
    ''',
    "Separate text shape, numeric conversion and calendar validation. Declare date order; never guess ambiguous layouts. Keep original text available when reporting a rejected transformation.",
    [
        ("Which step rejects February 31?", "datetime.date construction", "A two-digit day capture", "lower()", "The date constructor applies the calendar rules."),
        ("Under our stated policy, what is 09/10/2026?", "October 9, 2026", "September 10, 2026", "The parser guesses", "The declared slash format is day/month/year."),
    ])

add(5, "3. CSV and HTML: choose a parser for structured text",
    "Recognise quoted/nested formats and use standard-library parsers appropriately.",
    [
        ("csv.reader; io.StringIO", "csv.reader understands CSV delimiter and quoting rules. StringIO presents a string as an in-memory text file for that reader."),
        ("html.parser.HTMLParser; handle_data", "HTMLParser is a standard-library event parser. A subclass overrides handle_data to receive text pieces; it does not create a browser-rendered page."),
        ("convert_charrefs=True", "Character references such as &amp; are converted in ordinary text when this parser option is enabled. It is not an HTML sanitizer."),
    ],
    "The row Book,\"red, blue\",12 has three CSV fields, not four: the comma inside quotes is data. "
    "Use csv.reader and, for a real file, with open(path, newline='', encoding='utf-8') as handle. "
    "For simple HTML text collection, a subclass can accumulate data callbacks. This reuses Week 18 classes and Week 19 method overriding. "
    "Our toy collector also receives some text you might not want, such as script content; it is not a general visible-text extractor or sanitizer.",
    'list(csv.reader(io.StringIO(text)))\nclass TextCollector(HTMLParser):\n    def handle_data(self, data):\n        self.parts.append(data)',
    r'''
    import csv
    import io
    from html.parser import HTMLParser
    text = 'Book,"red, blue",12\nPen,"say ""hello""",3\n'
    for row in csv.reader(io.StringIO(text)):
        print(row)
    class TextCollector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
    collector = TextCollector()
    collector.feed("<p>Hello <b>world</b> &amp; all.</p>")
    collector.close()
    print("".join(collector.parts))
    ''',
    "StringIO ले memory को text लाई file-जस्तो reader मा दिन्छ। CSV parser ले quoted comma र doubled quote नियम बुझ्छ। "
    "HTML subclass मा super().__init__ ले parent setup गर्छ; प्रत्येक text callback list मा राख्छ। "
    "Empty-string join ले original text chunks जोड्छ। Word spacing, hidden text र malformed HTML को policy छुट्टै चाहिन्छ।",
    ("Split every CSV line at each comma; strip HTML with <.*?>",
     "Use csv.reader for CSV and a parser for actual HTML",
     "Quoted delimiters and structured markup exceed the assumptions of these flat regex recipes."),
    "Parse 'Sita,\"Kathmandu, Nepal\",90' into three fields, then convert the final score to int.",
    r'''
    import csv
    import io
    row = next(csv.reader(io.StringIO('Sita,"Kathmandu, Nepal",90')))
    print(row)
    print(int(row[2]) + 1)
    ''',
    "Collect text from '<p>One &amp; <b>two</b>.</p>' with HTMLParser. Compare with the original markup and explain that this is not sanitization.",
    r'''
    from html.parser import HTMLParser
    class TextCollector(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []
        def handle_data(self, data):
            self.parts.append(data)
    original = "<p>One &amp; <b>two</b>.</p>"
    collector = TextCollector()
    collector.feed(original)
    collector.close()
    print(original)
    print("".join(collector.parts))
    ''',
    "Regex is useful for local patterns, not every text grammar. csv.reader handles quoting; HTMLParser handles markup events. Parsing, text collection and sanitizing are distinct jobs.",
    [
        ("Why not split CSV at every comma?", "A quoted field can contain a comma.", "Commas are never delimiters.", "CSV has no fields.", "Quoted commas belong inside a field; a CSV parser interprets that grammar."),
        ("Does our HTML text collector sanitize HTML for display?", "No", "Yes", "Only if it calls close()", "Collecting data events is not a security or complete visible-text policy."),
    ])

PROJECT = clean(r'''
import re
from collections import Counter
from datetime import datetime
from ipaddress import ip_address

LOG_PATTERN = re.compile(
    r"(?P<time>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}) "
    r"(?P<level>INFO|WARN|ERROR) "
    r"ip=(?P<ip>[0-9.]+) "
    r"status=(?P<status>[0-9]{3}) "
    r"type=(?P<type>[A-Za-z_]+) "
    r"message=(?P<message>.*)"
)

def parse_line(line):
    if len(line) > 4096:
        raise ValueError("line too long")
    found = LOG_PATTERN.fullmatch(line)
    if found is None:
        raise ValueError("bad log format")
    row = found.groupdict()
    stamp = datetime.fromisoformat(row["time"])
    address = ip_address(row["ip"])
    if address.version != 4:
        raise ValueError("IPv4 required")
    status = int(row["status"])
    if not 100 <= status <= 599:
        raise ValueError("invalid status")
    row["ip"] = str(address)
    row["status"] = status
    row["hour"] = stamp.strftime("%Y-%m-%dT%H")
    return row

def analyse(lines):
    rows, rejected = [], []
    for number, line in enumerate(lines, 1):
        try:
            rows.append(parse_line(line.rstrip("\r\n")))
        except ValueError as error:
            rejected.append((number, str(error)))
    errors = Counter(row["type"] for row in rows if row["level"] == "ERROR")
    hours = Counter(row["hour"] for row in rows)
    offending = Counter(row["ip"] for row in rows if row["status"] >= 400)
    top_ips = sorted(offending.items(), key=lambda item: (-item[1], item[0]))
    return rows, rejected, errors, hours, top_ips
''')

SAMPLE = clean(r'''
sample = [
    "2026-10-10T09:00:00 INFO ip=192.0.2.1 status=200 type=ok message=ready",
    "2026-10-10T09:10:00 ERROR ip=192.0.2.2 status=500 type=disk message=disk full",
    "2026-10-10T10:00:00 WARN ip=192.0.2.1 status=404 type=missing message=not found",
    "2026-10-10T10:05:00 ERROR ip=192.0.2.2 status=503 type=disk message=retry later",
    "2026-02-31T10:00:00 INFO ip=192.0.2.3 status=200 type=ok message=bad date",
    "malformed line",
]
''')

DEMO = clean(r'''
rows, rejected, errors, hours, top_ips = analyse(sample)
print("valid:", len(rows), "rejected:", len(rejected))
print("errors by type:", sorted(errors.items()))
print("requests by hour:", sorted(hours.items()))
print("IPs with status >= 400:", top_ips)
print("rejected line numbers:", [number for number, reason in rejected])
''')

BOUNDARY_CHECKS = clean(r'''
good = "2026-10-10T09:00:00 INFO ip=192.0.2.1 status=200 type=ok message=ready"
bad_values = [
    good.replace("192.0.2.1", "999.0.0.1"),
    good.replace("status=200", "status=999"),
    good.replace("2026-10-10", "2026-02-31"),
    "malformed line",
    "x" * 4097,
]
for value in bad_values:
    try:
        parse_line(value)
    except ValueError:
        continue
    raise AssertionError("bad input was accepted")
assert parse_line(good)["status"] == 200
print("five rejection checks and one valid record passed")
''')

REPORT_CHECKS = clean(r'''
rows, rejected, errors, hours, top_ips = analyse(sample)
assert len(rows) == 4 and len(rejected) == 2
assert errors == {"disk": 2}
assert hours == {"2026-10-10T09": 2, "2026-10-10T10": 2}
assert top_ips == [("192.0.2.2", 2), ("192.0.2.1", 1)]
assert [number for number, reason in rejected] == [5, 6]
print("all report expectations passed")
''')

add(5, "4. Complete project: parse and analyse a server log",
    "Build a checked parser, keep rejected line numbers, and compute three clearly defined reports.",
    [
        ("collections.Counter", "Counter counts occurrences from an iterable. Here it counts error types, request hours, and IPs of records whose status is at least 400."),
        ("datetime.fromisoformat; strftime", "fromisoformat validates our captured ISO timestamp. strftime formats it into an hour bucket; %Y/%m/%d/%H mean year/month/day/hour."),
        ("ipaddress.ip_address; version", "ip_address validates an IP address instead of trusting a digits-and-dots shape. version identifies IPv4 vs IPv6; this declared log format permits IPv4 only."),
        ("Adjacent string literals; named-group log schema", "Python joins adjacent string literals inside parentheses. This lets the compiled pattern show one named field per line without changing its required spaces."),
        ("Deterministic report ordering", "The sort key (-count, ip) puts larger counts first and uses IP text as a consistent tie-breaker. This is lexical tie-breaking, not numeric IP order."),
    ],
    "Use the exact log grammar shown below: naive ISO timestamp, one space, INFO/WARN/ERROR, IPv4 field, "
    "three-digit HTTP status, ASCII-letter/underscore error type, and a message. Each physical line is one record. "
    "fullmatch checks shape; datetime, ip_address and the status range check semantics. Only line-ending CR/LF is stripped, "
    "so meaningful message spaces remain. Reject malformed lines with their 1-based line numbers and continue. "
    "Reports have explicit meanings: errors by type count level ERROR; requests by hour count all valid records; "
    "top 'offending' IPs count status >= 400, which does not establish malicious intent. Timestamps have no timezone here. "
    "The 4096-character cap bounds regex input after the line is read; this teaching implementation retains valid rows "
    "and rejects in lists, so it is not a constant-memory analyser for arbitrarily large files.",
    'match = LOG_PATTERN.fullmatch(line)\nfields = match.groupdict()\n# validate date/IP/status, then count selected fields',
    PROJECT + SAMPLE + DEMO,
    "पहिले pattern लाई field अनुसार पढ: time → level → ip → status → type → message। parse_line ले format नमिले तुरुन्त error उठाउँछ। "
    "मिल्यो भने captures अझै strings हुन्; datetime/IP validation र int conversion पछि record बनाउँछ। "
    "analyse को enumerate(..., 1) ले original line number राख्छ। try/except ले एउटा bad line का कारण बाँकी file रोकिँदैन। "
    "Counters मा कुन records गनिने भन्ने filter छुट्टै छ। sorted ले report को क्रम स्थिर बनाउँछ। "
    "चार valid records र दुई rejected छन्; disk errors दुई, प्रत्येक hour मा दुई requests, "
    "192.0.2.2 का दुई र 192.0.2.1 को एक status>=400 record छ।",
    ("Capture a timestamp and IP, then assume both are valid",
     "Validate with datetime.fromisoformat and ip_address; enforce status range explicitly",
     "2026-02-31 and 999.0.0.1 fit simple shapes but are not valid values. Keep shape checks and semantic checks separate."),
    "Test invalid IP, status 999, impossible date, malformed layout and overlong line; each must raise ValueError. Also prove one valid record is accepted.",
    PROJECT + BOUNDARY_CHECKS,
    "Assert every report result from the six sample lines, including rejected original line numbers and deterministic IP ranking.",
    PROJECT + SAMPLE + REPORT_CHECKS,
    "A useful parser has a declared grammar, semantic validation, an explicit rejection policy and reproducible report counts. Test failing boundaries as well as happy paths. The offline project uses only the standard library.",
    [
        ("What does requests-by-hour count in this project?", "All valid parsed records", "Only ERROR records", "Only rejected lines", "The hour Counter is built from every valid row; the error-type report has its own filter."),
        ("Does a status>=400 record prove its IP is malicious?", "No; this is only a chosen report metric.", "Yes", "Only with status 500", "Client/server errors do not establish an actor's intent."),
    ])

add(5, "5. Whole-week review: rebuild, explain, then test",
    "Recall the week's rules without copying and verify success and failure cases.",
    [
        ("Review by retrieval", "Try to write the pattern and explain each token before opening a solution. If stuck, revisit the smallest earlier part that supplies the missing concept."),
        ("Assertions in tests", "assert expresses a test expectation; optimised Python can remove it. Production validation above uses explicit ValueError, not assertions."),
    ],
    "Day 6 is large: study its parts over several sessions if needed. Day 7 remains your existing review/rest day. "
    "First redraw the operation table (search/match/fullmatch/findall/finditer). Then practise classes, counts, captures, "
    "replacement and context assertions. Finally rebuild parse_line and analyse without a template. "
    "For each validator, test empty, valid, too short, too long, trailing junk and a semantic boundary. "
    "Explain why csv.reader/date/ip_address are needed, rather than making a regex increasingly complicated. "
    "All answers remain inside the site so you can study offline.",
    'write a candidate pattern → list accepted/rejected inputs → run checks → explain every token',
    r'''
    import re
    pattern = re.compile(r"[A-Z]{2}[0-9]{3}")
    expected = {"AB123": True, "A123": False, "AB123x": False, "": False}
    for value, wanted in expected.items():
        actual = pattern.fullmatch(value) is not None
        assert actual == wanted
        print(repr(value), actual)
    ''',
    "दुई letters र तीन digits भएको ID को नियम पढेर accepted/rejected test बनायौँ। "
    "खाली value र extra suffix पनि जाँचिएका छन्। आफ्नै pattern लेखेपछि यस्तो सानो test matrix बनाउने बानी बसाल। "
    "Answers खुलाउनुअघि result र कारण मुखले वा नोटमा लेख।",
    ("Only test one valid example", "Test boundaries and rejected inputs as well as the happy path",
     "A pattern may accept your valid example yet also accept trailing junk, empty input, or invalid semantics."),
    "Without copying, rebuild an exact two-uppercase-letter/three-digit ID validator. Test valid, short, trailing-junk and empty inputs.",
    r'''
    import re
    def valid_id(value):
        return re.fullmatch(r"[A-Z]{2}[0-9]{3}", value) is not None
    assert valid_id("AB123")
    assert not valid_id("A123")
    assert not valid_id("AB123x")
    assert not valid_id("")
    print("ID success and failure checks passed")
    ''',
    "Add a separate errors-by-hour report to the project. Keep the original all-requests-by-hour report and show that each hour has one ERROR but two total requests.",
    PROJECT + SAMPLE + clean(r'''
    rows, rejected, errors, hours, top_ips = analyse(sample)
    error_hours = Counter(row["hour"] for row in rows if row["level"] == "ERROR")
    assert error_hours == {"2026-10-10T09": 1, "2026-10-10T10": 1}
    assert hours == {"2026-10-10T09": 2, "2026-10-10T10": 2}
    print("all requests:", sorted(hours.items()))
    print("errors only:", sorted(error_hours.items()))
    '''),
    "Week 22 mastery: explain every regex token, choose the correct operation, preserve important text, validate semantics with the right parser, and test both accepted and rejected inputs. Revisit weak parts before the next week.",
    [
        ("Which operation checks the complete string?", "fullmatch", "search", "match", "Complete-input matching rejects unmatched suffixes and prefixes."),
        ("Does a raw string disable regex syntax?", "No", "Yes", "Only on Windows", "Raw strings change Python's literal processing, not the regex engine."),
        ("Which repetition requires at least one occurrence?", "+", "*", "?", "+ has minimum one; the others can permit zero."),
        ("Are captured numbers automatically integers?", "No; convert explicitly.", "Yes", "Only in named groups", "Capture values on str input are text."),
        ("What does (?:...) provide?", "Grouping without a capture", "A named captured field", "A literal question mark", "Use it for structural choices without adding result fields."),
        ("Which flag makes dot match newline?", "DOTALL", "MULTILINE", "IGNORECASE", "DOTALL affects dot, while MULTILINE affects anchors."),
        ("What does a lookahead consume in the outer match?", "No characters", "Its entire condition", "One character always", "It tests context at a position without moving the outer match past that condition."),
        ("How should a variable-width preceding context be handled here?", "Match the prefix and capture the wanted field.", "Ignore the compile error.", "Make Python guess.", "Python re lookbehind requires fixed width."),
        ("Which tool handles a quoted comma in CSV?", "csv.reader", "split(',') in every case", "re.findall(r'\\w+')", "The CSV reader understands quoting and separators."),
        ("Is a date-shaped regex enough to reject February 31?", "No; validate with date or datetime.", "Yes", "Only with ASCII", "Calendar validity is a semantic rule beyond digit counts."),
    ])

last = days["22.5"]["parts"][-2]["sections"]
last.extend([
    section("p", "Save the project's definitions as log_analyser.py. To use your own UTF-8 log file, add the following code after the definitions. Keep a copy of rejected line numbers for correction. The definitions and demo are also saved in docs/python-week22-log-analyser.py."),
    section("syn", 'with open("server.log", encoding="utf-8") as handle:\n    rows, rejected, errors, hours, top_ips = analyse(handle)\nprint(sorted(errors.items()))',
            note="Week 9 file handling: change the filename to your practice log. The with block closes it automatically. This analyser still retains parsed records; a streaming aggregation is a later extension."),
])
days["22.5"]["parts"][-1]["sections"].append(section(
    "p", "Optional official references: https://docs.python.org/3.12/library/re.html · https://docs.python.org/3.12/howto/regex.html · https://docs.python.org/3.12/library/csv.html · https://docs.python.org/3.12/library/datetime.html. These are extra references; the complete teaching and solutions above need no connection."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in days):
        raise RuntimeError("Week 22 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in days.items())
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    result = prefix + "\n" + addition + original[end:]
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes(result.encode("utf-8"))
    temporary.replace(target)
    artifact = ROOT / "docs" / "python-week22-log-analyser.py"
    artifact.write_text(
        '"""Week 22 teaching project. Python 3.10+. No external dependencies.\n'
        'Run normally (not python -O) to execute the assertion checks.\n'
        'Format: naive timestamps, IPv4, status 100..599, one record per line.\n'
        'This teaching implementation retains valid/rejected rows in memory.\n'
        '"""\n' + PROJECT + "\n" + SAMPLE +
        '\nif __name__ == "__main__":\n' +
        textwrap.indent(DEMO + BOUNDARY_CHECKS + REPORT_CHECKS, "    "),
        encoding="utf-8",
    )
    parts = [p for day in days.values() for p in day["parts"]]
    quizzes = sum(len(s["lesson"]["quiz"]) for p in parts for s in p["sections"] if s["t"] == "checkpoint")
    print(f"Added Week 22: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {executed} verified examples.")


if __name__ == "__main__":
    write()
