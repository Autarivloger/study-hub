L(2, '1. Separate the import package from the distribution',
  'Explain src layout, import names and what a user actually installs.',
  [('Import package', 'A directory such as studyhub_records that Python imports; __init__.py exposes its public functions.'),
   ('Distribution name', 'The installable project identifier in package metadata. Our example is studyhub51-records, which differs from its Python import name.'),
   ('src layout', 'Keep importable source below src/ so running Python from the repository root does not automatically prove the package was installed correctly.')],
  "A useful script becomes a reusable library when callers can install it, import a stable interface and understand its behavior. Copying a folder into another project is not the same as producing an installable distribution with metadata.\n\nOur distribution is named studyhub51-records; users import studyhub_records. The first is a packaging name, the second is a Python identifier. __init__.py re-exports three documented functions while core.py owns their implementation. Development tools such as bench.py stay outside the runtime package. The command-line adapter is a thin wrapper around the library.\n\nThe supplied project uses src/studyhub_records. During development, an editable install makes that package importable while you change its source. An editable success alone does not prove a wheel contains the correct files. Later you will install the built wheel into a fresh environment and run from a directory outside the checkout. The lesson verifier temporarily adds src to its own test path; that convenience is explicitly not evidence of installation.",
  r'''from pathlib import Path
import tomllib
metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
print("Distribution:", metadata["name"])
print("Import folder:", Path("src/studyhub_records").is_dir())
import studyhub_records
print("Public functions:", studyhub_records.__all__)''',
  'Identify runtime source and development-only files in the supplied layout.',
  r'''from pathlib import Path
print("Runtime module:", Path("src/studyhub_records/core.py").exists())
print("Development benchmark:", Path("bench.py").exists())
print("Tests separated:", Path("tests/test_records.py").exists())''',
  'Check that the public namespace produces a usable result without importing the benchmark.',
  r'''from studyhub_records import unique_in_order
print(unique_in_order(["read", "code", "read"]))''',
  [('Must distribution and import names be identical?', 'No', 'Always', 'Only if there is no CLI', 'Packaging identifiers and Python import identifiers are separate concepts.'),
   ('Does importing from a manually added src path prove wheel installation?', 'No', 'Yes', 'Only on Windows', 'The built artifact must be tested independently of the source path.')],
  'Assume pip install studyhub51-records means import studyhub51-records.',
  'Read the documented import name: from studyhub_records import unique_in_order.',
  'A small explicit public interface makes a package easier to learn, review and preserve.',
  syntax='distribution: studyhub51-records\nimport: from studyhub_records import unique_in_order',
  shell='python -m pip install --no-build-isolation --no-deps -e .')

L(2, '2. Read pyproject.toml as a build and API promise',
  'Distinguish backend requirements, runtime dependencies, metadata and command entry points.',
  [('pyproject.toml / tomllib', 'Standard project configuration and Python 3.11+ standard-library TOML reader. Tables group related configuration.'),
   ('Build frontend / backend', 'A frontend such as build requests an artifact; a backend such as setuptools.build_meta produces it.'),
   ('requires-python and dependencies', 'Declare the supported interpreter range and packages needed at runtime. Development tools are a separate installation concern.'),
   ('Console entry point', 'A mapping from an installed command name to a callable, here studyhub-records to studyhub_records.cli:main.')],
  "The build-system table tells a frontend which backend and build tools are needed. The project table describes what users will install: name, version, description, README, license, Python requirement and runtime dependencies. These are different kinds of information even when both use lists named requires or dependencies.\n\nThis library has no runtime dependency because its implementation uses the standard library. pytest, MkDocs, Twine and line-profiler are development tools; putting them in runtime dependencies would make every user install tools they do not need. The pinned development file records direct authoring tools, but it is not a complete transitive lockfile.\n\nOur license expression uses the SPDX string MIT and includes the new original project's LICENSE. Setuptools support for these fields requires a sufficiently recent backend; the build requirement states >=77. Before publishing your own work, choose a license you can grant and review included files. A license string cannot grant rights to material you do not own. Read every metadata field as a promise to the package consumer, then test the built artifact against it.",
  r'''from pathlib import Path
import tomllib
config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print("Backend:", config["build-system"]["build-backend"])
print("Runtime dependencies:", config["project"]["dependencies"])
print("Python:", config["project"]["requires-python"])
print("CLI:", config["project"]["scripts"]["studyhub-records"])''',
  'Extract version and source-package discovery location from real configuration.',
  r'''from pathlib import Path
import tomllib
config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
print("Version:", config["project"]["version"])
print("Source roots:", config["tool"]["setuptools"]["packages"]["find"]["where"])''',
  'Keep runtime needs separate from the development tool list.',
  r'''from pathlib import Path
import tomllib
config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
tools = Path("requirements-dev.txt").read_text(encoding="utf-8")
print("pytest is a development tool:", "pytest==" in tools)
print("Runtime dependency count:", len(config["project"]["dependencies"]))''',
  [('Does build-system.requires describe every runtime dependency?', 'No, it describes build requirements', 'Always', 'Only for wheels', 'Runtime dependencies belong to project metadata.'),
   ('What does the CLI entry point reference?', 'An importable module and callable', 'An HTML lesson', 'A developer password', 'Installers create a command wrapper that calls the configured Python function.')],
  'Add every local tool to project.dependencies because it was used during development.',
  'Declare only runtime needs there and install development tooling separately.',
  'Accurate metadata reduces surprises for the person installing your package.',
  syntax='[build-system]\nrequires = ["setuptools>=77", "wheel"]\nbuild-backend = "setuptools.build_meta"\n\n[project.scripts]\nstudyhub-records = "studyhub_records.cli:main"')

L(2, '3. Build and inspect a real wheel',
  'Create distribution artifacts and inspect their contents before release.',
  [('Wheel (.whl)', 'A built distribution archive with importable files and installation metadata. A pure-Python wheel is still a real installable artifact.'),
   ('Source distribution (sdist)', 'An archive of source/build inputs from which an installer or builder can produce a wheel.'),
   ('Build isolation', 'A frontend can prepare a separate build environment from declared requirements. --no-isolation instead uses an already-prepared environment and must be stated.'),
   ('zipfile.ZipFile', 'Read the wheel archive to verify package source and .dist-info metadata are present.')],
  "From the practice project folder, python -m build normally prepares a source archive and then builds a wheel from that source archive. That second step helps expose missing build inputs: a checkout-only success is weaker evidence than a successful rebuild from its sdist.\n\nThe executable example below builds one wheel with --no-isolation because the authoring environment already contains the declared backend tools. It then opens the archive and checks source and metadata files. The full release verifier separately performs the sdist-to-wheel route. A wheel is not proved correct merely because a file with the .whl suffix exists.\n\nBuild isolation is usually useful for checking declared build requirements independently. This prepared offline rehearsal deliberately avoids dependency downloads during the build, so it cannot establish that a future resolver chooses exactly the same tools. State that limitation. Keep dist/, build/ and egg-info generated outputs out of your source changes, and inspect metadata before making any public release.",
  r'''from pathlib import Path
import subprocess
import sys
import zipfile
subprocess.run([sys.executable, "-m", "build", "--wheel", "--no-isolation"],
               check=True, capture_output=True, text=True)
wheel = next(Path("dist").glob("*.whl"))
with zipfile.ZipFile(wheel) as archive:
    names = archive.namelist()
print("Wheel:", wheel.name)
print("Contains core:", "studyhub_records/core.py" in names)
print("Contains metadata:", any(name.endswith(".dist-info/METADATA") for name in names))''',
  'Read which source root the backend will package rather than guessing from your current directory.',
  r'''from pathlib import Path
import tomllib
config = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
root = Path(config["tool"]["setuptools"]["packages"]["find"]["where"][0])
print(sorted(path.relative_to(root).as_posix() for path in root.rglob("*.py")))''',
  'Plan a complete artifact check and distinguish each stage.',
  r'''stages = ["build sdist", "build wheel from sdist", "validate metadata", "install exact wheel", "run outside checkout"]
for number, stage in enumerate(stages, 1):
    print(number, stage)''',
  [('Does a successful wheel build prove installation and imports work?', 'No, install and execute the artifact too', 'Always', 'Only for small packages', 'Build, metadata, installation and runtime behavior are separate checks.'),
   ('What does --no-isolation assume?', 'Build dependencies are already prepared', 'No dependencies are needed anywhere', 'The wheel is published', 'It reuses the current build environment instead of preparing a separate one.')],
  'Publish immediately after seeing any wheel filename.',
  'Inspect contents and metadata, rebuild from sdist, then test a fresh installation.',
  'The build step creates evidence that must be followed by consumer-side checks.',
  syntax='python -m build\npython -m twine check --strict dist/*',
  shell='python -m build --no-isolation\npython -m twine check --strict dist/*',
  diagram=('From source tree to a consumer import', ['Source + pyproject + README + license', 'Build source distribution (sdist)', 'Build wheel from the sdist', 'Check metadata and install exact wheel', 'Run API and CLI outside the checkout'], 'The local release verifier performs this route with a prepared build environment; it never uploads.'))

L(2, '4. Test the consumer boundary, not your checkout',
  'Detect source-path contamination and distinguish editable development from wheel consumption.',
  [('Editable install', 'A development installation that points imports at changing source. Helpful for editing, insufficient as the final distribution test.'),
   ('Fresh environment', 'A new virtual environment without the development checkout on its import path.'),
   ('Import origin', 'The actual module file used by Python, visible through module.__file__. Check it belongs to the intended installed environment.')],
  "It is easy to test the wrong thing. Running from the repository root, leaving PYTHONPATH set, or using an editable install can make imports succeed even when your wheel is missing files. Treat the consumer test as a boundary crossing.\n\nThe project release verifier builds in a temporary source copy, creates a new virtual environment, installs the exact wheel with --no-index --no-deps and runs from another temporary directory. It removes inherited PYTHONPATH and checks that the imported module file belongs under sys.prefix in that fresh environment. It also checks installed distribution metadata and runs the actual console entry point.\n\nBelow, the lesson test harness is intentionally using the supplied source path. It labels that condition rather than pretending it is an installed-wheel result. Run verify_release.py later for the complete artifact rehearsal. An environment can still contain platform differences not covered by a single machine; CI adds a second operating-system/interpreter context but also has a declared matrix rather than universal coverage.",
  r'''from pathlib import Path
import sys
import studyhub_records
origin = Path(studyhub_records.__file__).resolve()
print("Module file:", origin.name)
print("Lesson uses supplied source:", "src" in origin.parts)
print("Inside this interpreter environment:", origin.is_relative_to(Path(sys.prefix).resolve()))''',
  'Use an origin check to distinguish a hypothetical source file from an installed environment file.',
  r'''from pathlib import PurePosixPath
environment = PurePosixPath("/tmp/consumer")
for origin in [PurePosixPath("/repo/src/studyhub_records/core.py"), PurePosixPath("/tmp/consumer/lib/site-packages/studyhub_records/core.py")]:
    print(origin.is_relative_to(environment))''',
  'List contamination sources the fresh-consumer check removes.',
  r'''conditions = {"PYTHONPATH removed": True, "cwd outside checkout": True,
              "exact wheel installed": True, "editable-only test": False}
print("Required conditions satisfied:", all(value for key, value in conditions.items() if key != "editable-only test"))
print("Editable alone proves distribution:", conditions["editable-only test"])''',
  [('Why run outside the source checkout?', 'To avoid accidentally importing uninstalled source', 'To make the code shorter', 'To hide failing tests', 'The consumer must use the built installed files.'),
   ('Which check identifies the module actually imported?', 'Inspect its resolved __file__ path', 'Read the latest commit message', 'Count README headings', 'The import origin reveals source-path contamination.')],
  'A successful editable install is the final release test.',
  'Install the exact wheel into a fresh environment and test from outside the source tree.',
  'The consuming environment must prove the artifact works without checkout conveniences.',
  syntax='origin = Path(package.__file__).resolve()\nassert origin.is_relative_to(Path(sys.prefix).resolve())')

L(2, '5. Version the public contract deliberately',
  'Classify compatible fixes, compatible additions and breaking public changes.',
  [('Semantic versioning', 'A chosen policy for a declared public API. In stable 1.x+, MAJOR breaks compatibility, MINOR adds compatible features and PATCH makes compatible fixes.'),
   ('0.x policy', 'Initial development has weaker stability expectations; explicitly describe your own compatibility and migration policy instead of implying 1.x guarantees.'),
   ('Changelog / migration note', 'Tell users what changed, why it matters and how they adapt affected code.')],
  "A version number helps users decide whether an update fits their expectations. It is useful only when you describe the public API and honor the chosen compatibility policy. A tool can increment numbers, but it cannot decide whether sorting previously ordered results breaks a caller.\n\nOur teaching package starts at 0.1.0 and documents its current behavior. For a stable 1.x API, preserving the ordered output while fixing an internal validation bug may be a patch; adding an optional backward-compatible helper may be a minor release; changing return type or first-seen ordering is a breaking major change. Actual classification depends on the promised behavior, including errors.\n\nReleasing new contents under a previously used artifact filename/version is not a safe replacement strategy. Prepare a new version, rebuild and retain a clear changelog. Development requirements also need maintenance, but changing a development tool alone does not automatically require a runtime API major release. Think about the consumer's observable contract rather than the number of lines changed.",
  r'''changes = {"preserve output; fix documented behavior": "PATCH",
           "add optional compatible helper": "MINOR",
           "change ordered list return to set": "MAJOR"}
for change, level in changes.items():
    print(level, "-", change)
print("Example assumes a stable 1.x public API")''',
  'Compute the next illustrative stable versions for three change classes.',
  r'''major, minor, patch = 1, 4, 2
print("Fix:", (major, minor, patch + 1))
print("Addition:", (major, minor + 1, 0))
print("Breaking:", (major + 1, 0, 0))''',
  'Read the actual project version and its release-history heading.',
  r'''from pathlib import Path
import tomllib
version = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
print("Project version:", version)
print("Changelog records version:", "## " + version in Path("CHANGELOG.md").read_text(encoding="utf-8"))''',
  [('Can a one-line order change be a breaking API change?', 'Yes', 'Never', 'Only if dependencies change', 'Compatibility depends on the observed contract, not diff size.'),
   ('Does 0.1.0 automatically promise stable 1.x compatibility?', 'No', 'Always', 'Only with a README', 'Initial-development stability and migration policies must be stated.')],
  'Decide version changes only by counting edited lines.',
  'Classify the effect on documented callers and write a migration note when needed.',
  'Versioning communicates a maintenance decision; it does not substitute for that decision.',
  syntax='stable policy: MAJOR.MINOR.PATCH\n0.x: state your stability and migration policy')

L(2, '6. Rehearse TestPyPI publication safely and honestly',
  'Prepare a manual test-index release and identify the evidence needed to call it published.',
  [('TestPyPI', 'A separate online test package index with its own account. It is for rehearsal and may be periodically cleared.'),
   ('Twine', 'A distribution upload and metadata-check tool. Upload is a separate action from creating a wheel.'),
   ('Single-index verification', 'For this dependency-free project, install the exact version from TestPyPI with --no-deps; no extra package index is needed.'),
   ('Publication evidence', 'An actual TestPyPI project/version page and an install verified against that index. A local build report alone is not publication.')],
  "First complete the local wheel rehearsal. Then, in your own practice copy, choose a unique distribution name you control, review metadata and license, update the version if needed, rebuild and run twine check. The shared teaching name may already be unavailable.\n\nCreate your own TestPyPI account and complete its current account requirements. If using an API token, enter it yourself at Twine's hidden prompt. Never put it into HTML, a source file, a shell argument, a screenshot or Study Hub notes. The lesson needs no token and no automated upload. A trusted-publishing setup is another option when you are ready to configure its repository/environment rules.\n\nThe terminal block is a manual online exercise. Replace YOUR-UNIQUE-NAME before running the install command. Check the actual version page and test the downloaded package in a fresh environment. If you have only done the local checks, record 'local distribution verified; publication pending'. That is an accurate completed local milestone, and it avoids confusing a terminal plan with a real upstream action.",
  r'''from pathlib import Path
import tomllib
metadata = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]
print("Local distribution:", metadata["name"], metadata["version"])
print("Local metadata alone proves upload:", False)
print("Next manual evidence: TestPyPI version page and fresh index install")''',
  'Separate completed local checks from an upload that has not happened.',
  r'''evidence = {"wheel built": True, "fresh local install": True, "TestPyPI version page": False}
print("Local rehearsal complete:", evidence["wheel built"] and evidence["fresh local install"])
print("Publication verified:", evidence["TestPyPI version page"])''',
  'Construct a public project URL from a non-secret practice name; do not upload anything.',
  r'''name, version = "my-unique-study-records", "0.1.0"
print(f"https://test.pypi.org/project/{name}/{version}/")''',
  [('Does a local wheel on disk mean the package is on TestPyPI?', 'No', 'Always', 'Only when it has a version', 'Publication requires a successful upload and independent index verification.'),
   ('Where should your token go for the manual Twine exercise?', 'Only into its hidden credential prompt or an intentionally configured trusted flow', 'Inside the website HTML', 'Inside a public command example', 'Keep secrets out of source and displayed shell arguments.')],
  'Paste a token into a tracked script and call a local build a public release.',
  'Complete local checks; perform your own manual upload; verify the actual index artifact.',
  'Local verification and online publication are distinct observable states.',
  syntax='build -> metadata check -> manual authenticated upload -> verify exact index version',
  shell='python -m twine check --strict dist/*\n# Manual online exercise; you enter your own credentials at the hidden prompt.\npython -m twine upload --repository testpypi dist/*\n# In a fresh environment; replace the unique name.\npython -m pip install --no-deps --index-url https://test.pypi.org/simple/ YOUR-UNIQUE-NAME==0.1.0')

L(3, '1. Write documentation around a reader task',
  'Give a new user one successful result before expanding into reference details.',
  [('Quickstart', 'The shortest complete path from installation to a checked useful result, including expected output.'),
   ('How-to versus reference', 'A how-to solves a specific task; reference documents precise callable behavior and parameters.'),
   ('Documentation audience', 'Name the reader and prerequisites instead of assuming they have your checkout, environment or background knowledge.')],
  "A long README is not automatically useful documentation. A new user first needs to know what the package does, which Python version it supports, how to install it and what a successful first result looks like. Put a small working example near the beginning.\n\nThe quickstart below imports the public API and returns ordered topics, group totals and prefix sums. It is complete: no unexplained variable is assumed to exist from an earlier notebook cell. The project manual then links to the API contract for errors and complexity, a performance page for measurement limits and a release page for packaging steps.\n\nKeep a task guide focused. 'Summarize a CSV' should show the required columns, a command, output shape and likely failure messages. Reference can explain accepted types and generator behavior in greater detail. A tutorial should build understanding step by step. Combining all three indiscriminately makes each harder to use.",
  r'''from studyhub_records import unique_in_order, totals_by_category, running_totals
print(unique_in_order(["Python", "SQL", "Python"]))
print(totals_by_category([("Python", 20), ("Python", 10)]))
print(running_totals([20, 0, 10]))''',
  'Define a quickstart completeness checklist rather than measuring documentation by word count.',
  r'''quickstart = {"supported Python": True, "installation": True, "complete example": True, "expected output": True}
print("Complete first-result path:", all(quickstart.values()))''',
  'Locate the manual pages readers can follow after the first example.',
  r'''from pathlib import Path
for name in ["index.md", "api.md", "performance.md", "release.md"]:
    print(name, (Path("manual") / name).is_file())''',
  [('What should a quickstart establish?', 'A small complete path to a verified result', 'Every implementation detail', 'Only a screenshot of a terminal', 'A reader needs prerequisites, actions and a recognizable success result.'),
   ('Where do exact accepted types and errors belong?', 'API reference', 'Only the project logo', 'Only the commit title', 'Reference is the place to retrieve precise callable contracts.')],
  'Start the README with pages of internals before showing a usable example.',
  'Show one complete successful task, then link to deeper guides and reference.',
  'Good documentation reduces the assumptions a reader must guess.',
  syntax='purpose -> prerequisites -> install -> complete example -> expected output -> next link')

L(3, '2. Make docstrings describe contracts',
  'Document return values, ordering, errors, side effects and examples without restating the function name.',
  [('Docstring', 'The first string in a module, class or function body, available through help() and inspect.getdoc().'),
   ('inspect.getdoc', 'Retrieve a cleaned documentation string for an object.'),
   ('Public error contract', 'Document the failures callers can intentionally handle, including type and value distinctions.')],
  "A docstring saying 'does unique in order' adds little. A useful docstring says which inputs are valid, what result is returned, how order and case behave, whether input is changed and what errors can occur. Keep that public behavior independent of internal variable names.\n\nOur functions accept iterables and consume them once. That detail matters when a generator fails partway through: no result is returned, but already-consumed input cannot be rewound. For minute totals, bool is rejected even though it subclasses int. These are meaningful caller decisions worth documenting.\n\nUse one consistent convention, such as a concise summary followed by behavior and executable examples. A generated API site can display docstrings but cannot invent missing promises. If you later change validation, update the docstring, tests and relevant migration note together. Avoid guaranteeing universal byte sizes or worst-case hash timings that the implementation does not establish.",
  r'''import inspect
from studyhub_records import unique_in_order, totals_by_category
for function in [unique_in_order, totals_by_category]:
    documentation = inspect.getdoc(function)
    print(function.__name__, "->", documentation.splitlines()[0])
print("Callable example documented:", ">>>" in inspect.getdoc(unique_in_order))''',
  'Write a small docstring that names its behavior and validate that it is retrievable.',
  r'''import inspect
def double_minutes(minutes):
    """Return twice an already-validated nonnegative integer minute count."""
    return minutes * 2
print(inspect.getdoc(double_minutes))
print(double_minutes(5))''',
  'Check that the real group helper documents its boolean rejection.',
  r'''import inspect
from studyhub_records import totals_by_category
documentation = inspect.getdoc(totals_by_category)
print("Boolean behavior described:", "bool" in documentation)
print("Mutation described:", "mutate" in documentation)''',
  [('Can generated documentation replace a missing behavior contract?', 'No', 'Always', 'Only if it uses a theme', 'A generator can present information but cannot infer your intended public promises.'),
   ('Should generator-consumption behavior be documented?', 'Yes, callers can observe it', 'Never', 'Only if the function is async', 'Input ownership and consumption affect callers after both success and failure.')],
  'Describe only internal variable assignments and omit caller-visible errors.',
  'Document valid input, returned value, ordering, ownership and intentional failures.',
  'A docstring is a compact API promise that tests and implementation must support.',
  syntax='def function(argument):\n    """Summary, contract, errors and a small complete example."""\n    ...')

L(3, '3. Run documentation examples and build a real site',
  'Use doctest for examples and MkDocs strict mode for generated navigation/content checks.',
  [('doctest.testmod', 'Execute interactive examples embedded in module docstrings and compare their displayed outputs.'),
   ('MkDocs', 'A development tool that converts Markdown pages and mkdocs.yml navigation into a local HTML documentation site.'),
   ('Strict documentation build', 'Treat documentation warnings as failures. It helps catch broken references/configuration but does not prove semantic accuracy.')],
  "Examples can go stale even while the application tests remain green. doctest checks small >>> examples against the implementation. It is particularly helpful for deterministic input/output contracts; machine-dependent timing numbers should not be hard-coded as doctest expectations.\n\nThe example runs the actual packaged docstrings and builds the supplied four-page MkDocs site. It checks that generated index and API pages exist. This is real output from the documentation tool, not a hand-written mock page. The site uses flat page links so you can open its pages from disk after generation.\n\nA strict build catches warnings and many reference/configuration problems, but a grammatically valid page can still teach a false API behavior. Review the text and run its examples. Conversely, doctest is not a substitute for tests of malformed CSV, write failure or generator consumption. Use each tool for the boundary it actually checks.",
  r'''from pathlib import Path
import doctest
import subprocess
import sys
from studyhub_records import core
result = doctest.testmod(core)
print("Docstring examples passed:", result.failed == 0, "attempted:", result.attempted)
subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict"],
               check=True, capture_output=True, text=True)
print("Generated home:", Path("site/index.html").is_file())
print("Generated API:", Path("site/api.html").is_file())''',
  'Run a standalone deterministic doctest block.',
  r'''import doctest
text = ">>> sum([2, 3])\n5\n"
test = doctest.DocTestParser().get_doctest(text, {}, "sum_example", None, 0)
runner = doctest.DocTestRunner()
runner.run(test)
print("Failed:", runner.failures, "attempted:", runner.tries)''',
  'Detect a stale expected output without hiding the failure count.',
  r'''import doctest
import io
text = ">>> sum([2, 3])\n6\n"
test = doctest.DocTestParser().get_doctest(text, {}, "stale_example", None, 0)
runner = doctest.DocTestRunner()
diagnostic = io.StringIO()
runner.run(test, out=diagnostic.write)
print("Detected stale example:", runner.failures == 1)
print("Failure includes expected output:", "Expected" in diagnostic.getvalue())''',
  [('Does a strict docs build prove every explanation is true?', 'No, review behavior and run examples too', 'Always', 'Only when it has four pages', 'Build validity and instructional accuracy are different properties.'),
   ('Should doctests require the exact benchmark milliseconds from your laptop?', 'No', 'Always', 'Only if timeit was used', 'Timing observations vary and are unsuitable fixed output contracts.')],
  'Assume generated HTML and passing spelling checks prove the examples still work.',
  'Execute deterministic examples and build the linked documentation in strict mode.',
  'The documentation stays useful when both its navigation and its executable contracts are checked.',
  syntax='python -m doctest src/studyhub_records/core.py\npython -m mkdocs build --strict',
  shell='python -m doctest src/studyhub_records/core.py\npython -m mkdocs build --strict',
  diagram=('Keep documentation connected to behavior', ['Start with a reader task and API contract', 'Write complete deterministic examples', 'Execute examples with doctest/tests', 'Build linked pages with MkDocs strict mode', 'Review meaning and update docs with code'], 'Generated documentation presents your promises; executable examples help keep them accurate.'))

L(3, '4. Teach errors and recovery as part of the API',
  'Give readers a way to recognize and correct invalid input while preserving prior output.',
  [('Actionable error', 'A message that identifies a failed condition and gives enough context to correct it.'),
   ('Exit status', 'A process-level result for automation: our command returns 0 on success and 2 for input/output errors.'),
   ('Per-file atomic replacement', 'Write a temporary file beside the destination, then replace the destination after success. It does not make multiple files a transaction or guarantee power-loss durability.')],
  "A CSV guide that shows only valid input leaves the reader stranded when a spreadsheet exports an extra column or a decimal minute value. State the accepted header and number representation, then show a realistic failure and how to fix it.\n\nOur command accepts exactly category,minutes, with nonblank labels and ASCII decimal digits for minutes. A leading minus sign, missing value or extra field is rejected. It validates the input before replacing an existing report. Errors go to stderr and return status 2; successful summaries return 0.\n\nPreserving old output is useful, but be precise about the guarantee. One completed JSON file is replaced after validation; this is not a transaction involving several reports, cloud storage or Study Hub backups. If operating-system replacement fails, the exception path cleans the temporary file and leaves the existing destination untouched in the tested scenario. Document the scope and give the user a recovery step such as correcting input or choosing a writable destination.",
  r'''from contextlib import redirect_stderr
import io
from pathlib import Path
from studyhub_records.cli import main
Path("bad.csv").write_text("category,minutes\\nPython,-2\\n".replace("\\n", "\n"), encoding="utf-8")
Path("report.json").write_text("previous report", encoding="utf-8")
errors = io.StringIO()
with redirect_stderr(errors):
    status = main(["bad.csv", "--output", "report.json"])
print("Status:", status)
print("Previous output preserved:", Path("report.json").read_text() == "previous report")
print("Error explains minutes:", "minutes" in errors.getvalue())''',
  'Make a valid synthetic CSV and inspect its generated JSON totals.',
  r'''import json
from pathlib import Path
from studyhub_records.cli import main
Path("sample.csv").write_text("category,minutes\nPython,20\nPython,5\nSQL,10\n", encoding="utf-8")
status = main(["sample.csv", "--output", "report.json"])
print("Status:", status)
print(json.loads(Path("report.json").read_text(encoding="utf-8"))["totals"])''',
  'Reject an input/output path collision without modifying the source CSV.',
  r'''from contextlib import redirect_stderr
import io
from pathlib import Path
from studyhub_records.cli import main
text = "category,minutes\nPython,1\n"
Path("sample.csv").write_text(text, encoding="utf-8")
with redirect_stderr(io.StringIO()):
    status = main(["sample.csv", "--output", "sample.csv"])
print("Rejected:", status == 2)
print("Source preserved:", Path("sample.csv").read_text(encoding="utf-8") == text)''',
  [('Where does this CLI send input errors?', 'stderr with a nonzero exit status', 'Only into the success JSON', 'Only into a comment', 'Automation needs an unambiguous failure signal.'),
   ('Does per-file replacement make several files transactional?', 'No', 'Always', 'Only with JSON', 'The guarantee applies to the one replaced destination, within its stated filesystem assumptions.')],
  'Catch all errors, print success and overwrite an old report with partial output.',
  'Validate first, report an actionable failure and preserve the prior report.',
  'Error documentation is useful when it explains observable behavior and a practical next step.',
  syntax='status 0 = success\nstatus 2 = input/output error; read stderr; correct the condition')

L(3, '5. Write useful changelogs and migration examples',
  'Describe the effect on callers and show how to adapt a changed behavior.',
  [('Release note', 'A reader-facing account of changed behavior, compatibility and known limitations.'),
   ('Migration example', 'A concrete old/new calling pattern for users affected by an intentional change.'),
   ('Deprecation policy', 'Tell users what will change and when, with an alternative, rather than surprising them with a silent removal.')],
  "A changelog entry saying 'changed files' makes the reader inspect the whole diff. Explain the result instead: which input now works, which failure is clearer, what behavior changed and whether callers need to act. Link to the issue or regression evidence when one exists.\n\nConsider a hypothetical package that previously returned sorted unique labels and now wants first-seen ordering. That is not just a faster implementation: the caller-visible order changes. A migration guide should show both results and a deliberate way to retain sorted output, or keep the old public function while introducing a new explicitly named one.\n\nDo not invent a deprecation history for the teaching package: the current release is its first 0.1.0 contract. The example is a review exercise for a future change. Record real completed changes, tested environments and open limitations. Keep raw benchmark observations separate from broad product promises.",
  r'''values = ["SQL", "Python", "SQL"]
from studyhub_records import unique_in_order
print("First-seen API:", unique_in_order(values))
print("Caller intentionally requests sorted display:", sorted(unique_in_order(values)))
print("Different order is a documented choice")''',
  'Read the project changelog and verify its initial release is recorded.',
  r'''from pathlib import Path
text = Path("CHANGELOG.md").read_text(encoding="utf-8")
print("Initial release heading:", "## 0.1.0" in text)
print("Ordering mentioned:", "order" in text)''',
  'Create a concise hypothetical compatible-fix release entry with evidence.',
  r'''entry = {"change": "Preserve [] for empty generator input",
         "impact": "Existing callers can continue iterating the returned list",
         "evidence": "Empty-generator regression test",
         "migration": "No caller change required under the documented contract"}
for key, value in entry.items():
    print(key + ":", value)''',
  [('What makes a release note useful to callers?', 'Changed behavior and compatibility impact', 'Only edited filenames', 'Only author excitement', 'Readers need to know how their own usage is affected.'),
   ('Should an unperformed deprecation be described as completed history?', 'No', 'Yes', 'Only in 0.x', 'Release history must record actual changes and distinguish hypothetical exercises.')],
  'Hide an output-order change under a note saying performance improved.',
  'Name the behavioral change and provide a migration example or compatible alternative.',
  'Documentation should make update decisions easier, not transfer the investigation to the user.',
  syntax='change -> affected callers -> compatibility -> migration -> tested evidence')

L(3, '6. Maintain docs in the same change as the code',
  'Review documentation, tests and implementation as one public interface.',
  [('Documentation drift', 'A mismatch between what the docs promise and what the implementation does.'),
   ('Continuous integration (CI)', 'Automated checks run for proposed changes and pushes, giving repeatable evidence in a declared environment.'),
   ('Reproducible setup instructions', 'State interpreter, tools, folder and commands. A successful personal shell session alone does not establish a repeatable setup.')],
  "A package can pass unit tests while its quickstart imports a removed name. A strict documentation build can pass while a paragraph promises sorted output that the code does not return. Review the public interface across its different representations.\n\nThe project keeps docstrings, manual pages, tests, version and release notes in the same source tree. The CI workflow checks behavior, formatting and distribution installation on its declared Python matrix. The release verifier also builds the docs and executes installed examples. These are useful gates; they do not remove the need to review the meaning of new prose.\n\nWhen editing an API, ask which pages, examples, type hints and migration notes are affected. Run setup instructions in a fresh environment before calling them verified. Initial tool installation may require internet or a prepared wheelhouse; reading the generated lesson and using the already-installed standard-library package remain offline activities.",
  r'''import doctest
from pathlib import Path
from studyhub_records import core
result = doctest.testmod(core)
pages = [Path("manual") / name for name in ["index.md", "api.md", "performance.md", "release.md"]]
print("Docstring checks pass:", result.failed == 0)
print("Manual sources present:", all(page.is_file() for page in pages))
print("Configuration present:", Path("mkdocs.yml").is_file())''',
  'Model an interface change checklist with one missed documentation item.',
  r'''checks = {"implementation": True, "behavior tests": True, "API page": False, "quickstart": True}
print("Unfinished:", [name for name, done in checks.items() if not done])''',
  'Add the missing task and decide whether the change is ready for review.',
  r'''checks = {"implementation": True, "behavior tests": True, "API page": True, "quickstart": True}
print("Ready for human review:", all(checks.values()))
print("Automated checks replace human meaning review:", False)''',
  [('When should affected documentation change?', 'In the same change as the API behavior', 'Only months later', 'Only if a user complains', 'Keeping them together makes the promised interface reviewable.'),
   ('Does a green CI matrix prove all platforms work?', 'No, it covers the declared checks and environments', 'Always', 'Only for pure Python', 'Evidence has a defined coverage boundary.')],
  'Merge an API change and leave the old examples for someone else to fix.',
  'Review implementation, tests, docs and migration notes together.',
  'Documentation remains trustworthy when it shares the maintenance lifecycle of the code.',
  syntax='API change -> tests + docstrings + manual + release note + consumer check')
