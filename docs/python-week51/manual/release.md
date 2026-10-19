# Release rehearsal

Complete the local checks in the repository README. A passing release rehearsal
means wheel/sdist creation, metadata validation, strict documentation generation,
and import/API/CLI execution in a fresh environment outside the source checkout.
The verification script records which artifact was installed and its SHA-256.

TestPyPI publication is a separate, manual online exercise. Rename the distribution
to a unique name you control, choose a license, rebuild, and use your own TestPyPI
account. Enter credentials only at Twine's hidden prompt. Never put a token into
Python, HTML, Git, a command argument, a screenshot or a lesson note. No upload
occurs in the test suite, build script or GitHub workflow.

For a dependency-free package, install from the single test index using
`python -m pip install --no-deps --index-url https://test.pypi.org/simple/ YOUR-NAME==0.1.0`.
Do not add a second package index for this exercise. Verify in a fresh environment
and preserve the actual project link and installed version as publication evidence.

Semantic versioning is a chosen compatibility policy, not automatic enforcement.
For 1.0 and later, MAJOR breaks public compatibility, MINOR adds compatible
functionality, PATCH makes compatible fixes. In 0.x, explicitly document your
stability policy. Published filenames/version artifacts should not be replaced;
prepare a new version for changed contents.
