"""Week26 small-file backup practice. Python3.11+. No external services or GUI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import zipfile

MAX_FILE = 1_000_000
MAX_TOTAL = 10_000_000
MAX_FILES = 200

def read_small(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError("Source must contain ordinary files, not symlinks")
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE + 1)
    if len(data) > MAX_FILE:
        raise ValueError("Practice file size limit exceeded")
    return data

def plan_backup(source, destination):
    if source.is_symlink():
        raise ValueError("Choose a real practice source directory")
    source, destination = source.resolve(), destination.resolve()
    if not source.is_dir():
        raise ValueError("Source directory missing")
    if source == destination or source in destination.parents or destination in source.parents:
        raise ValueError("Use separate non-nested source and destination folders")
    records, total = [], 0
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlinks are outside this practice contract")
        if not path.is_file():
            continue
        data = read_small(path)
        total += len(data)
        relative = path.relative_to(source).as_posix()
        records.append({"path": relative, "size": len(data),
                        "sha256": hashlib.sha256(data).hexdigest()})
        if len(records) > MAX_FILES or total > MAX_TOTAL:
            raise ValueError("Practice backup scope limit exceeded")
    if not records:
        raise ValueError("No files selected")
    manifest = {"schema": 1, "records": records}
    encoded = json.dumps(manifest, sort_keys=True, ensure_ascii=False).encode("utf-8")
    identity = hashlib.sha256(encoded).hexdigest()
    return source, destination, manifest, identity

def verify_archive(path, expected):
    with zipfile.ZipFile(path) as archive:
        expected_names = {"manifest.json"} | {"files/" + row["path"] for row in expected["records"]}
        names = archive.namelist()
        if len(names) != len(set(names)) or set(names) != expected_names:
            raise ValueError("Archive entry set differs")
        info = archive.getinfo("manifest.json")
        if info.file_size > MAX_FILE:
            raise ValueError("Invalid manifest size")
        manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
        if manifest != expected:
            raise ValueError("Archive manifest differs")
        for row in expected["records"]:
            info = archive.getinfo("files/" + row["path"])
            if info.file_size != row["size"] or info.file_size > MAX_FILE:
                raise ValueError("Archive size differs")
            data = archive.read(info)
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                raise ValueError("Archive hash differs")
    return True

def write_outcome(destination, status, count):
    # Local alert/report only: no email, push or desktop transport.
    with (destination / "job.log").open("a", encoding="utf-8") as stream:
        stream.write(f"{status} files={count}\n")
    report = destination / "outcome.json"
    temporary = destination / "outcome.tmp"
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump({"status": status, "files": count,
                   "notification": "local report only"}, stream)
    temporary.replace(report)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Verified small-file practice backup; default preview.", allow_abbrev=False)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        source, destination, manifest, identity = plan_backup(args.source, args.destination)
    except (OSError, ValueError) as error:
        print("FAILED:", error, file=sys.stderr)
        return 1
    count = len(manifest["records"])
    if not args.apply:
        print("PLAN files:", count)
        print("Writes:", False)
        return 0
    acquired, staging_owned = False, False
    lock = destination / "job.lock"
    staging = destination / ("backup-" + identity + ".tmp")
    target = destination / ("backup-" + identity + ".zip")
    owner = str(os.getpid())
    try:
        destination.mkdir(parents=True, exist_ok=True)
        with lock.open("x", encoding="utf-8") as stream:
            acquired = True
            stream.write(owner)
        if target.exists():
            verify_archive(target, manifest)
            status = "reused"
        else:
            # The archive is built to an exclusively owned staging file.
            with staging.open("xb") as handle:
                staging_owned = True
                with zipfile.ZipFile(handle, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                    archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False))
                    for row in manifest["records"]:
                        data = read_small(source / row["path"])
                        if len(data) != row["size"] or hashlib.sha256(data).hexdigest() != row["sha256"]:
                            raise ValueError("Source changed after planning")
                        archive.writestr("files/" + row["path"], data)
            # Re-plan to detect additions/removals/content changes during creation.
            _, _, after, _ = plan_backup(source, destination)
            if after != manifest:
                raise ValueError("Source changed during backup")
            verify_archive(staging, manifest)
            staging.replace(target)
            staging_owned = False
            status = "created"
        write_outcome(destination, status, count)
        print("BACKUP:", status, "files:", count)
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError) as error:
        print("FAILED:", error, file=sys.stderr)
        if acquired:
            try:
                write_outcome(destination, "failed", count)
            except (OSError, ValueError):
                print("Also failed to save outcome; inspect stderr/job.log", file=sys.stderr)
        return 1
    finally:
        if staging_owned:
            staging.unlink(missing_ok=True)
        if acquired and lock.exists() and lock.read_text(encoding="utf-8") == owner:
            lock.unlink()

if __name__ == "__main__":
    sys.exit(main())
