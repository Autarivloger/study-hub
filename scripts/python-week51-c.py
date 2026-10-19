L(4, '1. Shape a pull request around one observable change',
  'Write a small reviewable proposal with a concrete trigger, result and evidence.',
  [('Pull request (PR)', 'A proposal to merge a branch into another branch, with a diff, discussion and checks. Creating one does not mean it has been accepted.'),
   ('Review scope', 'The specific behavior being changed and the files necessary to support that change.'),
   ('Diff', 'The before/after source changes a reviewer inspects. Keep unrelated formatting and features out of a focused behavioral fix.')],
  "A reviewer should understand the problem before reading every line. Describe a concrete input that fails, what the old code does and what the corrected code does. Then name the tests or observations supporting the change. This is more useful than a title such as 'many improvements'.\n\nSuppose a proposed optimization replaces first-seen deduplication with sorted(set(values)). It may look compact, but ['b', 'a', 'b'] now returns ['a', 'b'] instead of ['b', 'a']. The appropriate review discusses the ordering contract and a regression test, not merely whether the new line is elegant.\n\nFor your practice PR, include a problem statement, focused patch, tests, documentation impact and any remaining uncertainty. Separate a proposal from its merge or deployment status. The example below is a local rehearsal; it neither opens a GitHub PR nor messages a maintainer.",
  r'''from studyhub_records import unique_in_order
values = ["b", "a", "b"]
proposed = sorted(set(values))
required = unique_in_order(values)
print("Proposed result:", proposed)
print("Required result:", required)
print("Ordering regression:", proposed != required)''',
  'Write a PR description with a reproducible trigger and a checked result.',
  r'''proposal = {"problem": "Sorted deduplication changes first-occurrence order",
            "trigger": "['b', 'a', 'b']",
            "result": "Preserve ['b', 'a'] with a set membership index",
            "evidence": "Order, empty-input and generator tests"}
for key, value in proposal.items():
    print(key + ":", value)''',
  'Produce a small local diff for the core design choice, clearly labeled as a teaching excerpt.',
  r'''from difflib import unified_diff
before = ["# Teaching excerpt\n", "result = sorted(set(values))\n"]
after = ["# Teaching excerpt\n", "result = unique_in_order(values)\n"]
print("".join(unified_diff(before, after, fromfile="before.py", tofile="after.py")), end="")''',
  [('What should a reviewer understand first?', 'The concrete problem and resulting behavior', 'The author typing speed', 'Every unrelated future feature', 'A clear trigger and effect frame the diff.'),
   ('Does opening a PR mean it has been merged?', 'No', 'Always', 'Only if it has tests', 'Proposed, reviewed, accepted and deployed are different states.')],
  'Bundle an ordering change, a new CLI and unrelated reformatting into one unexplained PR.',
  'Keep one observable change focused and explain its trigger, result and tests.',
  'A reviewable change lets another person evaluate the behavior without reconstructing your private reasoning.',
  syntax='PR description: trigger -> before/after behavior -> tests -> compatibility/limits')

L(4, '2. Review correctness and ownership before style',
  'Find failures in validation, ordering, mutation and one-shot input behavior.',
  [('Correctness review', 'Compare the implementation against documented behavior, including empty and invalid input.'),
   ('Mutation/ownership review', 'Check whether a function changes objects owned by its caller and whether that is promised.'),
   ('Iterator exhaustion', 'A generator or iterator can be consumed by validation or a first loop, leaving no values for a second loop.')],
  "A review that concentrates on naming while missing a consumed generator does not protect the user. Begin with the contract. Ask what valid input produces, how errors behave and whether caller-owned values are altered. Then inspect implementation details.\n\nThe deliberately flawed validator below calls all() on an iterator to check types, then tries to sum that same iterator. The first pass exhausted it, so a valid [10, 20] generator returns zero. The packaged running_totals validates while consuming once. To return only a total, a single loop could validate and accumulate without storing the full input.\n\nAlso inspect Python's type relationships: isinstance(True, int) is true. Review domain meaning rather than assuming a broad type check is sufficient. When you identify a real failure, provide the smallest reproducing input and state the expected behavior. Keep optional naming or style comments distinct from correctness concerns so the author knows what blocks acceptance.",
  r'''def flawed_total(values):
    if not all(isinstance(value, int) for value in values):
        raise TypeError("integers required")
    return sum(values)
print("List result:", flawed_total([10, 20]))
print("Iterator result:", flawed_total(iter([10, 20])))
print("bool is int subclass:", isinstance(True, int))''',
  'Replace the two-pass generator bug with one-pass validated accumulation.',
  r'''def checked_total(values):
    total = 0
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("integer minutes required")
        if value < 0:
            raise ValueError("nonnegative minutes required")
        total += value
    return total
print(checked_total(iter([10, 20, 0])))''',
  'Detect an input-mutation regression caused by sorting in place.',
  r'''values = ["b", "a", "b"]
original = values.copy()
values.sort()
print("Caller input changed:", values != original)
print("Non-mutating alternative:", sorted(original))
print("Original retained:", original)''',
  [('Why can validate-then-sum fail for an iterator?', 'Validation may consume it before summing', 'sum cannot add integers', 'all always returns zero', 'One-shot input is an ownership/consumption constraint.'),
   ('Which should normally block review first?', 'A reproducible contract violation', 'A personal preference for a variable name', 'The number of blank lines alone', 'Correctness and safety of the promised behavior precede optional style preferences.')],
  'Validate a generator in one full pass, then assume a second pass starts at the beginning.',
  'Validate and compute in one pass, or explicitly materialize when the contract allows it.',
  'The reproducing input makes the review comment actionable and protects future callers.',
  syntax='review: valid input + empty input + invalid input + order + mutation + generator consumption')

L(4, '3. Review performance claims against the real boundary',
  'Check equality, preparation cost, amortization and memory before accepting an optimization.',
  [('Amortization', 'Spread a one-time preparation cost across repeated uses. Whether preparation pays off depends on the actual number of queries.'),
   ('Benchmark fairness', 'Compare the same required work and include the costs that belong to the use case.'),
   ('Cache validity', 'Cached answers are useful only while they remain correct for their key, data version and invalidation policy.')],
  "A PR claims that membership became instant after building a set. Ask where the set construction is timed and how often it is reused. If a set is rebuilt for every single query, moving it outside the measured block can conceal the main cost. If a prepared index is intentionally reused across thousands of queries, show that usage pattern instead.\n\nA cached result can also be fast because it is stale. Review cache keys, invalidation, maximum retained state and whether cached exceptions or partial results are appropriate. This is another form of contract review. Do not accept speed numbers without knowing the answer remains valid.\n\nThe arithmetic below is an illustrative cost model, not measured milliseconds. It shows how a setup cost can lose for one query and win for many. For the real package, bench.py includes candidate set construction and validation inside each complete call. The appropriate final choice follows the real workload and evidence, not an isolated favorable number.",
  r'''setup_cost, indexed_query, scan_query = 100, 1, 20
for queries in [1, 10, 100]:
    indexed_total = setup_cost + queries * indexed_query
    scanning_total = queries * scan_query
    print("queries:", queries, "illustrative indexed units:", indexed_total,
          "scan units:", scanning_total)''',
  'Identify an invalid cached answer after source data changes.',
  r'''values = [10, 20]
cached_total = sum(values)
values.append(5)
print("Cached:", cached_total, "current:", sum(values))
print("Cache still valid:", cached_total == sum(values))''',
  'Inspect the actual benchmark scope before citing its ratio.',
  r'''from bench import benchmark
report = benchmark(size=80, repeats=3)
print("Equal results:", report["equal_results"])
print("Scope:", report["scope"])
print("Raw samples retained:", all(len(values) == 3 for values in report["seconds"].values()))''',
  [('May set preparation be excluded from every benchmark?', 'Only when the stated use case intentionally excludes or separately accounts for it', 'Always', 'Never, even for a reused prepared index', 'The measurement boundary must match the claimed usage.'),
   ('Is a stale cached result a valid speedup?', 'No', 'Always', 'Only if it is ten times faster', 'Correctness remains a prerequisite for performance comparison.')],
  'Accept a favorable ratio while ignoring preparation and stale-cache behavior.',
  'Review equivalent work, setup/reuse assumptions, memory and invalidation.',
  'A performance review checks why the number applies to the user, not merely that a number exists.',
  syntax='total indexed cost = preparation + query_count * per_query_cost')

L(4, '4. Make CI test the consumer artifact too',
  'Read an automated check as evidence with a stated environment and artifact boundary.',
  [('Workflow/job/step', 'A GitHub Actions workflow contains jobs; each job runs ordered steps on a runner. Matrix settings repeat a job across declared environments.'),
   ('Read-only repository permission', 'The teaching workflow needs contents: read for checkout and runs no publishing or credential-writing operation.'),
   ('Artifact-consumer check', 'Install and execute the built distribution, rather than relying only on tests importing a source tree.')],
  "The supplied workflow runs when this practice project changes and can also be started manually. Its matrix declares Python 3.12 and 3.13 on an Ubuntu runner. It installs development tools, runs behavior tests and formatting checks, records a benchmark and invokes the local release rehearsal.\n\nThe example below executes the actual project tests in a child Python process. It captures the test report and shows success, while a nonzero return code would fail the lesson verification. This is a real test run, not a dictionary of imaginary green checkmarks. The suite includes bounded exhaustive comparisons, invalid inputs, generator behavior and output preservation.\n\nA green source test alone is insufficient when distribution files may be missing. verify_release.py adds the sdist/wheel and fresh-consumer boundary. CI still covers only the declared matrix: Windows authoring verification and Linux CI together are useful evidence, not proof of every Python, architecture or operating system. A failed required check should be investigated rather than marked continue-on-error to make the badge green.",
  r'''import os
import subprocess
import sys
result = subprocess.run([sys.executable, "-m", "pytest", "-q"],
                        env={**os.environ, "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
                        capture_output=True, text=True, check=True)
print("Actual project tests passed:", result.returncode == 0)
print("Report contains passed tests:", "passed" in result.stdout)''',
  'Separate test properties from the checks that provide evidence for them.',
  r'''checks = {"algorithm behavior": "pytest + reference comparisons",
          "doc examples": "doctest", "distribution": "fresh wheel install",
          "docs navigation": "MkDocs strict build"}
for property_name, check in checks.items():
    print(property_name + " -> " + check)''',
  'Identify what a declared Python matrix covers without extending its claim.',
  r'''matrix = ["3.12", "3.13"]
for version in ["3.12", "3.13", "3.14"]:
    print(version, "declared in this matrix:", version in matrix)''',
  [('Why test a built wheel in CI?', 'Source-tree imports can hide missing distribution files', 'It replaces all unit tests', 'It publishes automatically', 'Consumers use the distribution artifact, not your editable checkout.'),
   ('Should failed required checks be hidden with continue-on-error?', 'No, investigate the failure', 'Always', 'Only if the README looks correct', 'A green badge is useful only when it represents meaningful passing gates.')],
  'Run only editable-source imports and assume package consumers are covered.',
  'Run behavior checks and install the exact built wheel outside the checkout.',
  'The workflow is credible when the checked boundary matches the claim made to consumers.',
  syntax='tests -> lint/format -> benchmark evidence -> build -> metadata -> fresh consumer',
  shell='python -m pytest -q\npython -m ruff check .\npython -m ruff format --check .\npython verify_release.py --output artifacts/release.json')

L(4, '5. Give and receive review as a technical conversation',
  'Write actionable comments and answer feedback with evidence and clear resolution.',
  [('Blocking comment', 'A concern that must be resolved for correctness, compatibility or another agreed requirement.'),
   ('Optional suggestion', 'A possible improvement that does not block acceptance; label it so its importance is clear.'),
   ('Review resolution', 'A response describing the correction or evidence-backed reason for retaining a choice, with unresolved concerns still visible.')],
  "A useful review comment names the observation, explains its consequence and suggests a next step. 'This is bad' gives the author no reproducing input or path to a better result. 'This iterator is consumed during validation; could we validate and add in one pass and test iter([10, 20])?' is concrete.\n\nWhen receiving feedback, reproduce the concern before defending the code. If it is valid, fix the behavior and add a targeted regression case. If the reviewer misunderstood a documented requirement, explain it with the contract and an example. Technical disagreement is normal; keep it about behavior, evidence and maintenance cost.\n\nAvoid resolving a conversation merely because new commits exist. State which change addresses it and which test supports the correction. Separate optional stylistic preferences from required behavior. Thank a reviewer for identifying a useful issue without pretending that every suggestion must be accepted. The exercise writes a local response; no message is sent to another person.",
  r'''review = {"observation": "Type validation exhausts a generator",
          "impact": "Valid [10, 20] input can incorrectly total zero",
          "request": "Validate and accumulate once; add an iterator regression test"}
for name, value in review.items():
    print(name + ":", value)''',
  'Respond to a valid review concern with the concrete fix and its evidence.',
  r'''response = {"change": "Replaced validation pass plus sum with one validated loop",
            "evidence": "Iterator input [10, 20] now returns 30",
            "remaining": "No known unresolved concern for this case"}
for name, value in response.items():
    print(name + ":", value)''',
  'Classify a correctness regression separately from an optional naming preference.',
  r'''comments = [("Empty input returns None instead of []", "blocking correctness"),
            ("Consider the name minutes instead of value", "optional clarity")]
for comment, category in comments:
    print(category + ":", comment)''',
  [('What makes feedback actionable?', 'Observation, impact and a concrete next step', 'A negative adjective alone', 'Only the reviewer seniority', 'The author needs a reproducible concern and a feasible correction.'),
   ('What is a useful response to a valid concern?', 'Explain the correction and supporting regression test', 'Mark resolved without checking', 'Change unrelated formatting', 'Resolution should connect the feedback to observable evidence.')],
  'Make personal judgments or silently dismiss a reproducible bug report.',
  'Discuss behavior, reproduce the issue and answer with a fix or clear evidence.',
  'Review improves code when both people can trace a concern to an observable outcome.',
  syntax='comment: observation -> impact -> request\nresponse: correction/reason -> evidence -> unresolved points')

L(4, '6. Rehearse a complete review of one bug fix',
  'Connect reproduction, a focused patch, regression evidence and a clear review response.',
  [('Review packet', 'A small collection of the problem, minimal input, diff, tests and compatibility note needed to evaluate a change.'),
   ('Before/after evidence', 'The same trigger run against the flawed behavior and corrected implementation.'),
   ('Acceptance decision', 'A review outcome based on the agreed requirements; local rehearsal is not an upstream approval.')],
  "Take a complete local example. A hypothetical helper returns None when there are no labels. Its documented return type is always list[str], so callers expecting to iterate fail. The patch should preserve [] for empty input and avoid changing ordering for other inputs.\n\nFirst show the failure, then run the same case against the correct public helper. Include an iterator case because empty generators are easy to miss. Keep any broader refactor out of this small fix. A review response can then say what changed and which tests cover it.\n\nThe exercise closes the loop without claiming an actual maintainer has reviewed it. For your own project, have another person inspect the packet if available, or return to it after a break and review against the written contract. The diagram shows the process you can reuse for the real contribution exercise tomorrow.",
  r'''from studyhub_records import unique_in_order
def flawed_empty(values):
    result = list(dict.fromkeys(values))
    return result or None
print("Before:", flawed_empty(iter([])))
print("Required:", [])
print("After:", unique_in_order(iter([])))
print("Nonempty order retained:", unique_in_order(["b", "a", "b"]) == ["b", "a"])''',
  'Write regression assertions for the empty-list and empty-generator contract.',
  r'''from studyhub_records import unique_in_order
for values in [[], iter([])]:
    result = unique_in_order(values)
    assert result == [] and isinstance(result, list)
print("Both empty-input forms return a list")''',
  'Prepare a review response that distinguishes local evidence from upstream acceptance.',
  r'''print("Fixed: empty input consistently returns []")
print("Evidence: empty-list, empty-generator and order regression checks pass")
print("Status: local review rehearsal; no upstream acceptance claimed")''',
  [('What does this local rehearsal establish?', 'A reproduced behavior and checked correction', 'A merged upstream PR', 'A guaranteed job offer', 'Only actual external review can establish upstream acceptance.'),
   ('Should an empty-input fix also preserve nonempty ordering?', 'Yes', 'No', 'Only if sorting is slower', 'A focused fix should retain unaffected parts of the contract.')],
  'Fix the empty case while silently changing every nonempty result order.',
  'Test the bug trigger and preserve the neighboring documented behaviors.',
  'A focused review packet connects the problem, correction and evidence in one inspectable unit.',
  syntax='reproduce -> focused fix -> regression -> review explanation -> explicit status',
  diagram=('A review loop that reaches a concrete result', ['Reproduce one contract failure', 'Write a focused failing regression', 'Make the smallest sufficient fix', 'Review tests, docs and compatibility', 'Answer feedback and record the actual status'], 'This is a local rehearsal. Submitting or merging an external PR is a separate action.'))

L(5, '1. Choose a contribution you can reproduce',
  'Select a small useful upstream task and learn its project rules before changing code.',
  [('Upstream', 'The original project to which your fork or branch proposes a contribution.'),
   ('CONTRIBUTING guide', 'The project-specific instructions for setup, tests, communication and contribution scope.'),
   ('Minimal reproduction', 'The smallest supported input and environment that demonstrate a reported problem.')],
  "A first contribution does not have to be a large feature. A reproducible bug, a broken example or an unclear supported-version instruction can be useful when corrected carefully. Choose a project you actually use or can run locally, then read its contribution guide and license.\n\nCheck whether the issue is still present on a supported version and whether someone is already working on it. For a large change, discuss the intended scope before investing heavily. Do not assume an old issue description is still current, and do not send speculative fixes without reproducing the behavior.\n\nThe local exercise reads this project's contribution guide and creates a small issue packet from known synthetic evidence. For a real upstream exercise, replace that packet with observed environment details and the project's required test command. Read-only investigation and local rehearsal can be completed offline after fetching the source; submitting a real contribution needs the project's online workflow and your own deliberate action.",
  r'''from pathlib import Path
guide = Path("CONTRIBUTING.md").read_text(encoding="utf-8")
print("Contribution guide present:", bool(guide.strip()))
print("Regression guidance:", "regression" in guide)
print("License file present:", Path("LICENSE").is_file())''',
  'Create a minimal issue packet for the already-reproduced empty-input bug.',
  r'''issue = {"environment": "Declared supported Python version",
         "input": "iter([])", "expected": "[]", "observed": "None in flawed teaching helper",
         "scope": "Local synthetic reproduction"}
for name, value in issue.items():
    print(name + ":", value)''',
  'Reject an attractive task that you cannot currently reproduce.',
  r'''candidates = [{"name": "Broken empty example", "reproduced": True, "small_scope": True},
              {"name": "Large speculative rewrite", "reproduced": False, "small_scope": False}]
print([task["name"] for task in candidates if task["reproduced"] and task["small_scope"]])''',
  [('What makes a good first contribution target?', 'A useful, reproducible and manageable task', 'The largest possible rewrite', 'An issue already fixed upstream', 'A clear small scope makes the contribution testable and reviewable.'),
   ('Which setup/test rules apply to an upstream project?', 'Its own contribution guide and supported environment', 'Only your personal preferences', 'Only this teaching package rules', 'Each project defines the requirements a contribution must satisfy.')],
  'Start a broad upstream rewrite before checking current behavior or project instructions.',
  'Read the guide, reproduce a supported case and choose a focused useful change.',
  'A contribution begins with understanding the project and its users.',
  syntax='project guide -> supported setup -> reproduce -> check existing work -> scope the contribution')

L(5, '2. Turn a reproduction into a regression test',
  'Make a bug report executable and show that the intended correction changes the outcome.',
  [('Regression-first workflow', 'Write a test for the failure before changing behavior, so the test demonstrates why the patch is needed.'),
   ('Expected versus observed', 'State the contractual answer separately from the current flawed result.'),
   ('Patch scope', 'The smallest change sufficient to restore the promised behavior, with neighboring cases retained.')],
  "A reproducible report becomes stronger when it includes an executable assertion. First run the failure against the flawed implementation and confirm the assertion would fail for the intended reason. A test that already passes may still be useful coverage, but it does not by itself demonstrate the reported regression.\n\nThen apply the focused correction and run the same case again. For the empty-result bug, [] must remain a list rather than becoming None. Include a nonempty order case so a sweeping 'fix' does not quietly replace the API with sorted output.\n\nIn an upstream project, use its existing testing style and fixtures. Avoid introducing a new framework for one small case. Keep the test deterministic and based on synthetic input; it should not require credentials, live services or the current clock unless those are the actual tested boundary. The example catches the intended assertion locally so you can inspect both before and after results in one complete teaching snippet.",
  r'''from studyhub_records import unique_in_order
def flawed(values):
    return list(dict.fromkeys(values)) or None
try:
    assert flawed([]) == []
except AssertionError:
    print("Before: regression assertion fails")
assert unique_in_order([]) == []
assert unique_in_order(["b", "a", "b"]) == ["b", "a"]
print("After: empty and neighboring order assertions pass")''',
  'Add an invalid-type test to prevent a broad fix from silently coercing labels.',
  r'''from studyhub_records import unique_in_order
try:
    unique_in_order(["a", 1])
except TypeError:
    print("Invalid-type contract preserved")
else:
    raise AssertionError("Expected TypeError")''',
  'Write a one-shot generator regression with the expected first-seen result.',
  r'''from studyhub_records import unique_in_order
values = (item for item in ["read", "code", "read"])
assert unique_in_order(values) == ["read", "code"]
print("One-shot input works; remaining input:", list(values))''',
  [('What should the regression test demonstrate before the patch?', 'The reported failure for the intended reason', 'Only a formatting difference', 'A network outage unrelated to the bug', 'A targeted failing assertion connects the report to the fix.'),
   ('Should a small contribution introduce a new test framework automatically?', 'Usually follow the project existing test style', 'Always', 'Only for empty inputs', 'A focused contribution minimizes unrelated maintenance work.')],
  'Change the expected answer to match the bug and call the test fixed.',
  'Keep the documented expected answer and correct the implementation.',
  'A regression test is evidence of a repaired contract, not a way to redefine a failure out of existence.',
  syntax='same contractual assertion: fails before -> passes after; neighboring cases still pass')

L(5, '3. Prepare a contribution without overstating its status',
  'Distinguish a local patch, a submitted proposal, review and acceptance.',
  [('Fork/branch', 'A fork is your repository copy; a branch is a line of work. Choose the mechanism allowed by the target project.'),
   ('Draft proposal', 'A reviewable work-in-progress state, useful for early feedback without implying final readiness.'),
   ('Contribution status', 'Local preparation, submitted, reviewed and merged are different states and need distinct evidence.')],
  "A completed local patch is valuable practice, but it is not an upstream contribution until you actually submit it through the project's process. A submitted PR is still a proposal; a merged PR has separate acceptance evidence. Record the actual state in your notes and portfolio.\n\nBefore submission, run the project's required checks, inspect the diff for unrelated files, and write a concise explanation with reproduction and test results. If your branch needs updating, follow that project's instructions and avoid rewriting shared history casually. Answer review feedback with evidence and preserve unresolved concerns.\n\nThis lesson deliberately prepares a local contribution packet. It does not open an issue, send a review or message any maintainer. For the real exercise, you perform the chosen upstream submission and save the actual URL. If the change is declined, a clear explanation of what you learned remains useful evidence; acceptance depends on the project's needs as well as code correctness.",
  r'''packet = {"reproduction": True, "focused diff": True, "regression": True,
          "required checks": True, "submitted upstream": False, "merged upstream": False}
local_ready = all(packet[name] for name in ["reproduction", "focused diff", "regression", "required checks"])
print("Local packet ready:", local_ready)
print("Submitted:", packet["submitted upstream"])
print("Merged:", packet["merged upstream"])''',
  'Create a local Markdown contribution packet that another reviewer can inspect.',
  r'''from pathlib import Path
packet = "# Local review packet\n\nProblem: empty input returns None.\nExpected: [].\nEvidence: empty-list and generator regressions.\nStatus: prepared locally, not submitted.\n"
Path("review-packet.md").write_text(packet, encoding="utf-8")
print("Local packet written:", Path("review-packet.md").is_file())''',
  'Choose an honest status statement from explicit evidence.',
  r'''evidence = {"patch": True, "tests": True, "upstream_url": None}
status = "submitted" if evidence["upstream_url"] else "local patch tested; submission pending"
print(status)''',
  [('Does a tested local patch prove upstream acceptance?', 'No', 'Always', 'Only if it has a README', 'Acceptance requires actual project review/merge evidence.'),
   ('What should a portfolio record about a PR?', 'Its actual state and a real link when submitted', 'Merged status regardless of outcome', 'A fabricated issue number', 'Traceable status helps readers judge the work accurately.')],
  'Describe a prepared patch as a merged contribution without an upstream record.',
  'Record local, submitted, reviewed and merged states using actual evidence.',
  'An honest contribution history explains both your work and its real outcome.',
  syntax='local patch -> checks -> actual submission -> review -> accepted/declined status')

L(5, '4. Build a portfolio entry around demonstrated skill',
  'Explain a project through its problem, decisions, evidence and limitations.',
  [('Portfolio evidence', 'Inspectable code, tests, artifacts and explanations that show what you can actually do.'),
   ('Decision record', 'A short account of a choice, alternatives considered, evidence and consequences.'),
   ('Deliberate practice', 'Choose a specific weak skill, attempt it independently, get feedback and repeat with a harder case.')],
  "A package name and a technology list tell a reader little about your judgment. Describe the problem, the public contract, one difficult decision and the evidence supporting it. In this project, the interesting decision is preserving ordered behavior while exchanging memory for faster expected membership work.\n\nInclude an example of a rejected alternative: sorting changed order, an editable-only test missed the consumer boundary, or a benchmark omitted setup. Explain why it was rejected and which test or observation supported the decision. That demonstrates reasoning a future collaborator can discuss with you.\n\nState limits plainly. This is a synthetic educational library, not a production analytics service. A locally verified wheel is not a published TestPyPI release. No timing ratio is a promise for all user data. Finish by naming a skill you will practice independently before the capstone: perhaps writing an API contract, profiling an unfamiliar program or reproducing a packaging failure.",
  r'''entry = {"problem": "Summarize validated synthetic study records",
         "decision": "Set index preserves first-seen order while reducing repeated scans",
         "evidence": "Differential tests, benchmark samples and fresh wheel installation",
         "limit": "Measured synthetic workload; public publication not implied",
         "next practice": "Profile a different script before choosing an optimization"}
for name, value in entry.items():
    print(name + ":", value)''',
  'Write a decision record for retaining the correct order instead of sorting.',
  r'''from studyhub_records import unique_in_order
values = ["SQL", "Python", "SQL"]
print("Chosen result:", unique_in_order(values))
print("Rejected sorted alternative:", sorted(set(values)))
print("Reason: required first-occurrence order is observable")''',
  'Choose a targeted next exercise from a self-assessed weak area.',
  r'''skills = {"API contract": 4, "profiling unfamiliar code": 2, "reading a wheel": 3}
target = min(skills, key=skills.get)
print("Next focused practice:", target)
print("Evidence to produce: a profile, a hypothesis and a checked before/after experiment")''',
  [('What makes a project entry convincing?', 'Decisions and inspectable evidence with limits', 'Only a list of library names', 'An unverified speed promise', 'The reader should be able to examine and discuss the demonstrated work.'),
   ('What is deliberate practice here?', 'A focused weak skill with an attempt and feedback', 'Repeating copied code without checking it', 'Adding every possible tool', 'The activity targets learning rather than appearance.')],
  'Claim production scale and upstream acceptance from a small local exercise.',
  'Describe the actual task, decisions, evidence and next learning target.',
  'A portfolio is strongest when another person can verify what each claim means.',
  syntax='problem -> contract -> decision -> evidence -> limitation -> next learning target')

L(5, '5. Decide release readiness with consumer evidence',
  'Use a concrete release checklist while distinguishing local verification from online publication.',
  [('Release gate', 'A required check tied to a failure that would matter to a consumer.'),
   ('Artifact identity', 'The exact filename, version and digest of the wheel that was installed and tested.'),
   ('SHA-256 digest', 'A content fingerprint useful for identifying exact bytes. It is not by itself proof of authorship or trust.')],
  "A release checklist should protect the consumer from specific failures: missing package files, unusable entry points, incorrect metadata, stale examples or undocumented breaking changes. Keep each gate connected to what it establishes instead of collecting badges without purpose.\n\nThe supplied verifier records the built wheel filename, version and SHA-256. It installs that exact artifact into a fresh environment, checks import origin, runs API examples and packaged doctests, and executes the installed command. A digest identifies the tested bytes; it does not say who created them or whether you should trust their source.\n\nBefore an actual upload, choose a unique name, review license and metadata, update release notes and run the checks against the final version. Do not upload one wheel and cite tests of a different build as though they were the same artifact. After TestPyPI upload, verify the exact index version independently and record that additional evidence. Today's local build can finish even while that online exercise remains pending.",
  r'''import hashlib
first = b"example wheel bytes, revision one"
second = b"example wheel bytes, revision two"
print("Same bytes, same digest:", hashlib.sha256(first).hexdigest() == hashlib.sha256(first).hexdigest())
print("Changed bytes, changed digest:", hashlib.sha256(first).hexdigest() != hashlib.sha256(second).hexdigest())
print("A digest alone proves authorship:", False)''',
  'Name the consumer failure each local release check addresses.',
  r'''gates = {"wheel content inspection": "missing package files",
         "fresh outside-checkout import": "accidental source imports",
         "installed CLI run": "broken entry point",
         "doctest": "stale deterministic examples"}
for gate, failure in gates.items():
    print(gate + " -> " + failure)''',
  'Keep local readiness separate from the missing publication record.',
  r'''local_checks = [True, True, True, True]
published_version_page = None
print("Locally ready:", all(local_checks))
print("Online publication verified:", published_version_page is not None)''',
  [('What does a SHA-256 digest identify here?', 'The exact artifact bytes', 'Guaranteed trusted authorship', 'All future builds automatically', 'A content hash is an identity check, not a complete trust decision.'),
   ('Should tests of one wheel be cited for a different uploaded wheel?', 'No, verify the final artifact', 'Always', 'Only when filenames look similar', 'The tested and released artifact identities must match.')],
  'Change package contents after testing, then upload without rebuilding and checking.',
  'Verify the final version and record the exact tested artifact identity.',
  'Release evidence should let a consumer trace the installed behavior to the artifact actually checked.',
  syntax='final version -> build -> metadata -> fresh install -> artifact digest -> optional manual upload')

L(5, '6. Milestone: a measured and installable library',
  'Finish a documented package with measured performance and a verified consumer installation.',
  [('verify_release.verify', 'The supplied local verifier in verify_release.py: copy source, build sdist/wheel, validate metadata/docs, install a wheel into a fresh environment and execute consumer checks.'),
   ('Temporary consumer', 'An isolated environment created for the release test and cleaned after the report is written.'),
   ('Capstone handoff', 'The contracts, measurements, package checks and collaboration habits you will reuse in Week 52.')],
  "This milestone connects the week rather than introducing another disconnected script. The library has three validated public functions, a thin CSV command, tests, a benchmark, docstrings, a generated manual, versioned metadata and a local release verifier. The final example actually runs that verifier.\n\nIt builds a source distribution and a wheel from the sdist with the prepared backend tools, checks metadata, builds documentation in strict mode and creates a fresh consumer environment. It installs the exact wheel without consulting a package index, removes source-path conveniences and runs installed API, doctest and CLI checks. The report records artifact identity and states published: false. This can take longer than earlier snippets because real environments and builds are involved.\n\nFor your own milestone, reproduce these steps without copying commands you cannot explain. Write a performance decision, inspect a built wheel, correct a deliberate documentation error and review a small bug fix. If you want the TestPyPI and upstream goals, complete the manual online exercises and preserve their actual links. Take additional sessions as needed. Week 52 uses this evidence and these habits in a capstone you can explain, maintain and demonstrate.",
  r'''from pathlib import Path
from verify_release import verify
report = verify(Path("release-evidence.json"))
print("Verified distribution:", report["distribution"], report["version"])
print("Wheel built from source archive:", report["built_from_sdist"])
print("Consumer checks:", len(report["checks"]))
print("Wheel digest characters:", len(report["sha256"]))
print("Public upload performed:", report["published"])''',
  'Exercise all three public functions with one coherent synthetic study example.',
  r'''from studyhub_records import unique_in_order, totals_by_category, running_totals
rows = [("Python", 20), ("SQL", 10), ("Python", 15)]
print("Topics:", unique_in_order(category for category, minutes in rows))
print("Minutes by topic:", totals_by_category(iter(rows)))
print("Cumulative minutes:", running_totals(minutes for category, minutes in rows))''',
  'Prepare an honest capstone handoff stating completed evidence and pending external actions.',
  r'''handoff = {"contract": "Ordering, input and errors documented",
           "performance": "Equal-result scoped measurements retained",
           "distribution": "Fresh wheel consumer verified locally",
           "collaboration": "Review regression and response rehearsed",
           "pending if desired": "Manual TestPyPI upload and real upstream submission"}
for name, value in handoff.items():
    print(name + ":", value)''',
  [('Which result does the supplied verifier actually establish?', 'A checked local build and fresh consumer installation', 'Automatic public TestPyPI publication', 'An upstream merged PR', 'The report explicitly distinguishes local verification from external actions.'),
   ('What should you carry into Week 52?', 'Explainable contracts, tests, measurements and maintenance habits', 'Only a package name', 'An assumed universal 10x gain', 'The capstone needs transferable judgment and inspectable evidence.')],
  'Finish with an untested folder of scripts and call it a published professional package.',
  'Build, install and exercise the documented artifact; record the actual completion state.',
  'The milestone is useful because a separate consumer environment can run the package and its documented interface.',
  syntax='python verify_release.py --output artifacts/release.json',
  shell='python -m pytest -q\npython -m mkdocs build --strict\npython bench.py --output artifacts/benchmark.json\npython verify_release.py --output artifacts/release.json',
  diagram=('A release milestone supported by evidence', ['Correct public functions and explicit contracts', 'Measured time/memory tradeoffs and regression tests', 'Versioned metadata, source archive and wheel', 'Documentation and fresh installed API/CLI checks', 'Report exact artifact; perform external actions separately'], 'The supplied project completes local verification. TestPyPI publication and upstream acceptance require their own actual evidence.'))
