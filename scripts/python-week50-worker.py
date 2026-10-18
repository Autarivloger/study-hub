"""Execute authored concurrency snippets as guarded, spawn-importable scripts."""

import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap


def main():
    source, destination = map(Path, sys.argv[1:])
    results = []
    for index, code in enumerate(json.loads(source.read_text(encoding="utf-8")), 1):
        with tempfile.TemporaryDirectory(prefix="studyhub-w50-example-") as folder:
            folder = Path(folder)
            script = folder / "example.py"
            script.write_text('if __name__ == "__main__":\n' + textwrap.indent(code, "    "), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(script)], cwd=folder, capture_output=True,
                text=True, encoding="utf-8", timeout=120,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "MPLBACKEND": "Agg"},
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if process.returncode or process.stderr.strip():
                raise RuntimeError(f"Authored concurrency example {index} failed:\n{process.stderr}")
            image = folder / "chart.png"
            results.append({
                "out": process.stdout.replace("\r\n", "\n").rstrip(),
                "png": base64.b64encode(image.read_bytes()).decode("ascii") if image.exists() else None,
            })
        if index % 12 == 0:
            print(f"Verified {index} guarded concurrency examples", flush=True)
    destination.write_text(json.dumps(results), encoding="utf-8")


if __name__ == "__main__":
    main()
