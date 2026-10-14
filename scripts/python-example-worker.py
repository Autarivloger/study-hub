"""Run authored local snippets with fresh globals/folders and reused imports.

This is an authoring verifier, not a sandbox for untrusted Python. Its input
must be the repository author's own examples. The deployed site never runs it.
"""
import base64
from contextlib import redirect_stdout, redirect_stderr
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

os.environ.setdefault("MPLBACKEND", "Agg")
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def main():
    source, destination = map(Path, sys.argv[1:])
    codes = json.loads(source.read_text(encoding="utf-8"))
    results = []
    original_cwd = Path.cwd()
    for index, code in enumerate(codes):
        stdout, stderr = io.StringIO(), io.StringIO()
        with tempfile.TemporaryDirectory(prefix="studyhub-authored-example-") as folder:
            try:
                os.chdir(folder)
                filename = Path(folder)/"snippet.py"
                filename.write_text(code, encoding="utf-8")
                namespace = {"__name__": "__main__", "__file__": str(filename)}
                # Explicitly reset shared plotting/random defaults between runs;
                # each example still has its own globals and filesystem.
                np.random.seed(0)
                with matplotlib.rc_context(), redirect_stdout(stdout), redirect_stderr(stderr):
                    exec(compile(code, str(filename), "exec"), namespace)
                if stderr.getvalue().strip():
                    raise RuntimeError("Unexpected warning: "+stderr.getvalue())
                picture = Path(folder)/"chart.png"
                results.append({"out": stdout.getvalue().replace("\r\n", "\n").rstrip(),
                    "png": base64.b64encode(picture.read_bytes()).decode("ascii") if picture.exists() else None})
            except BaseException:
                print(f"Failed authored example {index+1}", file=sys.stderr)
                traceback.print_exc()
                return 1
            finally:
                plt.close("all")
                os.chdir(original_cwd)
        if (index+1)%12 == 0 or index+1 == len(codes):
            print(f"Verified {index+1}/{len(codes)} local outputs", flush=True)
    destination.write_text(json.dumps(results), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
