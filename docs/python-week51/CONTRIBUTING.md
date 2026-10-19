# Contributing and review rehearsal

1. Read the API contract and open issues; ask before starting a large change.
2. Create a branch such as `fix-empty-category-message` in your own practice copy.
3. Reproduce one defect with minimal synthetic input and a failing test.
4. Make the smallest correction; run tests, doctests, lint and the wheel rehearsal.
5. Describe the problem, changed behavior, evidence and compatibility impact.
6. Review correctness, errors, input ownership, scope and performance claims first.
7. Explain the impact of a comment and suggest an actionable fix. Mark optional style
   suggestions clearly; acknowledge useful feedback and answer unresolved concerns.
8. A draft PR, a submitted PR and an accepted/merged contribution are different states.

For a real upstream contribution, read that project's CONTRIBUTING and license,
check whether the issue is already being solved, reproduce it on the supported
version, and follow the maintainer's test and communication requirements. A useful
documentation correction can be a meaningful contribution. Keep discussion factual.

Example constructive review: "For an empty input the new branch returns None,
but the documented API returns []. Could we preserve [] and add an empty-generator
regression test? This also keeps callers' iteration behavior compatible."
