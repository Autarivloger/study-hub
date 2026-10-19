"""Build and install the actual distribution locally; never upload anything."""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import tomllib
import venv
from pathlib import Path


def run(command, cwd, env):
    result = subprocess.run(
        command,
        check=False,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
    )
    if result.returncode:
        raise RuntimeError(f"Command failed: {command[:4]}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def verify(output):
    root = Path(__file__).resolve().parent
    metadata = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    with tempfile.TemporaryDirectory(prefix="studyhub51-release-") as temporary:
        folder = Path(temporary)
        source = folder / "source"
        shutil.copytree(
            root,
            source,
            ignore=shutil.ignore_patterns(
                ".venv",
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
                "*.egg-info",
                "build",
                "dist",
                "site",
                "artifacts",
                ".git",
                "*.prof",
            ),
        )
        run([sys.executable, "-m", "build", "--no-isolation"], source, env)
        wheels = list((source / "dist").glob("*.whl"))
        archives = list((source / "dist").glob("*.tar.gz"))
        if len(wheels) != 1 or len(archives) != 1:
            raise RuntimeError("Expected one wheel and one source archive")
        run(
            [sys.executable, "-m", "twine", "check", "--strict", str(wheels[0]), str(archives[0])],
            source,
            env,
        )
        run([sys.executable, "-m", "mkdocs", "build", "--strict"], source, env)
        venv.EnvBuilder(with_pip=True).create(folder / "consumer")
        python = folder / "consumer" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        outside = folder / "outside-checkout"
        outside.mkdir()
        run(
            [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheels[0])],
            outside,
            env,
        )
        consumer = r"""
import doctest, importlib.metadata as metadata, json, sys
from pathlib import Path
import studyhub_records
from studyhub_records import core, unique_in_order, running_totals, totals_by_category
from studyhub_records.cli import main
assert Path(studyhub_records.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
assert unique_in_order(["b", "a", "b"]) == ["b", "a"]
assert totals_by_category([("Python", 20), ("Python", 5)]) == {"Python": 25}
assert running_totals(iter([2, 0, 3])) == [2, 2, 5]
assert doctest.testmod(core).failed == 0
Path("sample.csv").write_text("category,minutes\nPython,20\nSQL,5\n", encoding="utf-8")
assert main(["sample.csv", "--output", "report.json"]) == 0
assert json.loads(Path("report.json").read_text(encoding="utf-8"))["totals"] == {"Python": 20, "SQL": 5}
print(metadata.version(sys.argv[1]))
"""
        result = run([str(python), "-c", consumer, metadata["name"]], outside, env)
        if result.splitlines()[-1] != metadata["version"]:
            raise RuntimeError("Installed version differs from source metadata")
        # Exercise the installed console entry point, not merely the Python main().
        executable = python.parent / (
            "studyhub-records.exe" if os.name == "nt" else "studyhub-records"
        )
        run([str(executable), "sample.csv", "--output", "cli-report.json"], outside, env)
        report = {
            "distribution": metadata["name"],
            "version": metadata["version"],
            "wheel": wheels[0].name,
            "sdist": archives[0].name,
            "sha256": hashlib.sha256(wheels[0].read_bytes()).hexdigest(),
            "python": sys.version.split()[0],
            "built_from_sdist": True,
            "checks": [
                "twine metadata",
                "strict MkDocs",
                "fresh wheel install",
                "outside-checkout import",
                "API examples",
                "installed doctests",
                "installed CLI entry point",
            ],
            "published": False,
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/release.json"))
    arguments = parser.parse_args()
    release = verify(arguments.output)
    print("Verified local distribution:", release["distribution"], release["version"])
    print("Checks:", ", ".join(release["checks"]))
    print("Public upload performed:", release["published"])
