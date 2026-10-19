"""Build an installable capstone and exercise its wheel outside the checkout."""

import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile
from pathlib import Path

from smoke import running_server


def command(arguments, cwd, env):
    result = subprocess.run(
        arguments,
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=180,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"Command failed: {arguments[:4]}\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def verify(output, wheelhouse=None):
    root = Path(__file__).resolve().parent
    env = {key: value for key, value in os.environ.items() if key != "PYTHONPATH"}
    env.update(PYTHONUTF8="1", PYTHONDONTWRITEBYTECODE="1", PIP_DISABLE_PIP_VERSION_CHECK="1")
    with tempfile.TemporaryDirectory(prefix="studylog52-release-") as temporary:
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
                "data",
                "artifacts",
                ".git",
                "*.sqlite*",
                ".env",
            ),
        )
        command([sys.executable, "-m", "build", "--no-isolation"], source, env)
        wheels = list((source / "dist").glob("*.whl"))
        assert len(wheels) == 1
        wheel = wheels[0]
        with zipfile.ZipFile(wheel) as archive:
            assert "capstone/static/index.html" in archive.namelist()
        if wheelhouse is None:
            wheelhouse = folder / "wheelhouse"
            command(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "download",
                    "--only-binary=:all:",
                    "-r",
                    str(source / "requirements.txt"),
                    "--dest",
                    str(wheelhouse),
                ],
                source,
                env,
            )
        else:
            wheelhouse = Path(wheelhouse).resolve()
        venv.EnvBuilder(with_pip=True).create(folder / "consumer")
        python = folder / "consumer" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        outside = folder / "outside-checkout"
        outside.mkdir()
        command(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                "--find-links",
                str(wheelhouse),
                str(wheel),
            ],
            outside,
            env,
        )
        origin = command(
            [
                str(python),
                "-c",
                'import capstone,sys;from pathlib import Path;assert Path(capstone.__file__).resolve().is_relative_to(Path(sys.prefix).resolve());print("installed origin verified")',
            ],
            outside,
            env,
        )
        with running_server(
            outside / "installed.sqlite", secrets.token_urlsafe(24), python=python, cwd=outside
        ) as client:
            assert "StudyLog" in client.get("/").text
            assert (
                client.post(
                    "/api/sessions",
                    json={"day": "2026-10-19", "subject": "Wheel consumer", "minutes": 25},
                ).status_code
                == 201
            )
            assert client.get("/api/summary").json()["minutes"] == 25
        report = {
            "wheel": wheel.name,
            "sha256": hashlib.sha256(wheel.read_bytes()).hexdigest(),
            "origin": origin,
            "checks": [
                "wheel from sdist",
                "packaged HTML",
                "fresh offline wheelhouse install",
                "outside-checkout import",
                "installed HTTP API and UI",
            ],
            "dependency_preparation": "downloaded wheels"
            if wheelhouse == folder / "wheelhouse"
            else "supplied wheelhouse",
            "public_deployment_verified": False,
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("artifacts/release.json"))
    parser.add_argument("--wheelhouse", type=Path)
    arguments = parser.parse_args()
    print(verify(arguments.output, arguments.wheelhouse))
