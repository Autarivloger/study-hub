"""Exercise real backup files in owned temporary folders; no email, tasks or GUI."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("backup_job", ROOT / "docs/python-week26/backup_job.py")
job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(job)


def run(source, destination, *flags):
    output, errors = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
        code = job.main([str(source), str(destination), *flags])
    return code, output.getvalue(), errors.getvalue()


with tempfile.TemporaryDirectory(prefix="studyhub-w26-project-") as name:
    root = Path(name)
    source, destination = root / "notes", root / "backups"
    source.mkdir()
    (source / "a.txt").write_text("Python practice", encoding="utf-8")
    (source / "b.txt").write_text("日本語", encoding="utf-8")
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    assert run(source, destination, "--dry-run")[0] == 0
    assert run(source, destination)[0] == 0
    assert not destination.exists(), "Preview created output/log/lock"
    assert before == {p.name: p.read_bytes() for p in source.iterdir()}
    assert run(source, destination, "--apply")[0] == 0
    target = next(destination.glob("*.zip"))
    original = target.read_bytes()
    _, _, manifest, identity = job.plan_backup(source, destination)
    assert job.verify_archive(target, manifest)
    assert run(source, destination, "--apply")[0] == 0
    assert len(list(destination.glob("*.zip"))) == 1
    assert target.read_bytes() == original, "Repeat rewrote verified artifact"
    assert json.loads((destination / "outcome.json").read_text())["status"] == "reused"
    assert not (destination / "job.lock").exists()
    # Restore to an owned separate location, preserving originals.
    restore = root / "restored"
    restore.mkdir()
    with zipfile.ZipFile(target) as archive:
        for row in manifest["records"]:
            (restore / row["path"]).write_bytes(archive.read("files/" + row["path"]))
    assert before == {p.name: p.read_bytes() for p in restore.iterdir()}
    assert before == {p.name: p.read_bytes() for p in source.iterdir()}
    # A corrupt existing archive is reported, never silently overwritten/reused.
    target.write_bytes(b"corrupt fixture")
    status, _, errors = run(source, destination, "--apply")
    assert status == 1 and errors.startswith("FAILED:")
    assert target.read_bytes() == b"corrupt fixture"
    assert json.loads((destination / "outcome.json").read_text())["status"] == "failed"
    assert not (destination / "job.lock").exists()
    target.write_bytes(original)
    # Other-owner lock and reports remain untouched when another run is refused.
    lock = destination / "job.lock"
    lock.write_text("other-owner", encoding="utf-8")
    old_report, old_log = (destination / "outcome.json").read_bytes(), (destination / "job.log").read_bytes()
    assert run(source, destination, "--apply")[0] == 1
    assert lock.read_text() == "other-owner"
    assert (destination / "outcome.json").read_bytes() == old_report
    assert (destination / "job.log").read_bytes() == old_log
    lock.unlink()
    # Nested paths and empty/missing sources fail before output effects.
    nested = source / "output"
    assert run(source, nested, "--apply")[0] == 1 and not nested.exists()
    assert run(root / "missing", root / "missing-output", "--apply")[0] == 1
    empty = root / "empty"
    empty.mkdir()
    assert run(empty, root / "empty-output", "--apply")[0] == 1
    # New content produces another archive and leaves the older artifact intact.
    (source / "a.txt").write_text("New practice notes", encoding="utf-8")
    assert run(source, destination, "--apply")[0] == 0
    assert len(list(destination.glob("*.zip"))) == 2
    assert target.read_bytes() == original
    # A pre-existing temporary file is not owned and must survive failure.
    (source / "a.txt").write_text("Third version", encoding="utf-8")
    _, _, _, third = job.plan_backup(source, destination)
    staging = destination / ("backup-" + third + ".tmp")
    staging.write_bytes(b"other temporary owner")
    assert run(source, destination, "--apply")[0] == 1
    assert staging.read_bytes() == b"other temporary owner"
    assert not (destination / "job.lock").exists()
    staging.unlink()
    # Source bytes changing between the plan and archive write cause a clean failure.
    change_output = root / "change-output"
    calls = [0]
    original_read = job.read_small
    def changed_read(path):
        calls[0] += 1
        data = original_read(path)
        return b"changed during copy" if calls[0] == 3 else data
    with patch.object(job, "read_small", side_effect=changed_read):
        assert run(source, change_output, "--apply")[0] == 1
    assert not list(change_output.glob("*.zip"))
    assert not list(change_output.glob("backup-*.tmp"))
    assert not (change_output / "job.lock").exists()
    assert json.loads((change_output / "outcome.json").read_text())["status"] == "failed"
    # An alert/log failure is visible even if the archive itself was verified.
    outcome_output = root / "outcome-output"
    with patch.object(job, "write_outcome", side_effect=OSError("fixture report failure")):
        assert run(source, outcome_output, "--apply")[0] == 1
    archive = next(outcome_output.glob("*.zip"))
    _, _, expected, _ = job.plan_backup(source, outcome_output)
    assert job.verify_archive(archive, expected)
    assert run(source, outcome_output, "--apply")[0] == 0
    assert len(list(outcome_output.glob("*.zip"))) == 1
    # CLI misuse and help produce conventional statuses.
    for flags, expected_status in [(["--apply", "--dry-run"], 2), (["--help"], 0)]:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            try:
                job.main([str(source), str(destination), *flags])
            except SystemExit as error:
                assert error.code == expected_status

print("PASS: zero-write default/dry-run, verified ZIP/restore, unchanged reuse, corrupt artifact preservation, overlap ownership, nested/missing/empty input, source-change cleanup, unrelated staging preservation, failed outcome/recovery, CLI statuses; no real mail/GUI/schedules.")
