# Week 25: Web scraping

Six days, four parts per day, 48 practice prompts, 58 quiz questions and 72 verified example/solution outputs.

| Day | Focus |
| --- | --- |
| 1 | HTTP, requests, statuses, decoding, timeouts and an owned local server |
| 2 | HTML trees, scoped selectors, table contracts and exact money |
| 3 | Relative URLs, pagination, identity, duplicate conflicts and CSV/JSON export |
| 4 | Source versus rendered DOM, Playwright, readiness and bounded Load more |
| 5 | Allowed sources, robots, redirects, pacing and Retry-After |
| 6 | Finite retries, cache provenance, a complete local tracker and failure review |

Study the objective, predict the example output, trace each line, write the build task without looking, then attempt the challenge and quiz. Use existing course notes and part completion controls.

## Practice setup

Use Python 3.11 or newer in your practice environment:

    python -m pip install requests beautifulsoup4 playwright
    python -m playwright install chromium

Installation initially needs internet. The examples afterward use prepared/mocked responses, supplied HTML, a loopback server, or an isolated browser loading local HTML. Study Hub works offline; fetching a remote website would require internet.

## Price tracker project

The project parses owned saved HTML fixture sets and does not fetch remote websites. Copy this folder into a practice directory and run:

    python price_tracker.py sample-run1 snapshot.json
    python price_tracker.py sample-run2 snapshot.json
    python price_tracker.py sample-run2 snapshot.json

Run 1 adds A and B. Run 2 changes A, observes B missing and adds C. Repeating Run 2 produces no changes.

Each sample directory includes its manifest and every page. The manifest carries a fixed fixture acquisition time; re-reading a fixture does not count as fresh acquisition. Page markers and explicit empty states belong to this authored practice contract, not to all websites.

The parser validates IDs, title, USD amount, duplicate observations and page coverage. It rejects missing fields, unknown price formats, conflicting IDs and incomplete manifests. The previous snapshot is validated before a new state is committed. A failed run returns status 1 and preserves the prior snapshot. Use a separate JSON state filename; an existing temporary file causes a visible failure instead of being overwritten.

The complete project and self-contained generated fixtures are also inside Day 6 Part 3. The website examples do not depend on downloading this folder.

### Extend after understanding the local version

A real acquisition adapter would verify permitted use, origin/path boundaries, robots policy, timeouts, redirects, retries, origin pacing and server Retry-After before producing a complete snapshot. A browser may request many subresources. Prefer an allowed documented API/export.

Day 6's injected waiter must integrate real pacing/server policy before live use. Its teaching helper does not automatically retry 429. Missing observations are not proof of permanent business deletion. Scheduling and notifications belong to Week 26.

## Primary references

- [Requests quickstart](https://requests.readthedocs.io/en/latest/user/quickstart/)
- [Requests advanced usage](https://requests.readthedocs.io/en/latest/user/advanced/#timeouts)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Python URL parsing](https://docs.python.org/3/library/urllib.parse.html)
- [Python robots parser](https://docs.python.org/3/library/urllib.robotparser.html)
- [Playwright library](https://playwright.dev/python/docs/library)
- [Playwright locators](https://playwright.dev/python/docs/locators)
- [HTTP 429](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/429)

The explanations, fixtures, examples and project are original teaching material; documentation verifies library behaviour.
