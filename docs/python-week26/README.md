# Week 26: Automation, scheduling and notifications

Six days with four parts per day, 48 practice/challenge prompts, 58 quiz questions and 72 verified example/solution outputs. Existing notes, quiz scores and part completion controls are reused.

| Day | Focus |
| --- | --- |
| 1 | Argparse, validation/status, subcommands and Click |
| 2 | Execution environment, Windows Task Scheduler, cron and in-process scheduling |
| 3 | Message composition, attachments, mocked SMTP/TLS and notification adapters |
| 4 | GUI context/fail-safe, authored images, matching failures and verified workflows |
| 5 | Subprocess arguments, statuses/timeouts, environment and backup verification |
| 6 | Idempotency, pure dry-run, overlap locks, backup project and failure review |

## Practice environment

Use Python 3.11 or newer. For the optional CLI/scheduler/image exercises:

    python -m pip install click schedule pillow

The backup project itself uses the standard library. Lesson email examples mock SMTP and send nothing. GUI examples use a FakeDesktop test double; Pillow creates authored images without reading personal screenshots.

For a deliberate real scratch-window exercise, install PyAutoGUI separately, verify the intended editor/focus, keep fail-safe enabled, and follow Day 4. Fake test success does not prove real desktop layout/readiness.

## Backup project

Copy this directory into your own practice folder:

    python backup_job.py practice-notes practice-backups --dry-run
    python backup_job.py practice-notes practice-backups --apply
    python backup_job.py practice-notes practice-backups --apply
    python backup_job.py --help

Default mode and explicit dry-run print a plan without creating output folders, logs, locks, archives or alerts. Explicit apply creates a verified ZIP, job.log and outcome.json under the separate destination.

The archive records relative filenames, sizes and SHA-256 content hashes. Repeated identical input reuses only an archive that verifies. Changed input produces another archive; old archives and source files remain intact.

A cooperative exclusive lock blocks overlap. A second run never removes the owner's lock. After a crash inspect active processes and local evidence before manually removing a stale owned lock or staging file.

### Scope and limits

- Ordinary files only: no symlinks, at most 200 files, 1 MB per file, 10 MB total.
- Separate non-nested source and destination folders.
- Byte content verification; not encryption.
- Empty directories, filesystem permissions/ACLs, retention and automatic restore are outside the project contract.
- Re-planning detects many concurrent source changes; it is not an atomic filesystem snapshot. Use a quiet practice directory.
- outcome.json is a local outcome/alert report, not an email/push delivery.
- A verified archive may exist even if its subsequent log/outcome write fails. The job reports nonzero failure; a repeated run verifies and reuses the artifact.
- A stale lock/temporary file causes a visible stop instead of being silently deleted.

Restore practice reads payloads into a separate scratch folder and checks hashes. Do not overwrite the only original.

## Schedule deliberately after manual verification

Day 2 explains how to configure your own Task Scheduler or cron. Start with a daily dry-run using an explicit interpreter, absolute paths, intended account/time zone, logs and an overlap policy. The website and tests do not register OS tasks.

For real email use the provider's documented host/TLS/authentication method, private configuration outside Git, and explicit intended recipients. SMTP acceptance does not prove final inbox delivery. Do not put real credentials in public HTML, JavaScript or example files.

## Primary references

- [Argparse](https://docs.python.org/3/library/argparse.html)
- [Click](https://click.palletsprojects.com/en/stable/)
- [Windows scheduled task configuration](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create)
- [Schedule](https://schedule.readthedocs.io/en/stable/)
- [Python email examples](https://docs.python.org/3/library/email.examples.html)
- [SMTP](https://docs.python.org/3/library/smtplib.html)
- [PyAutoGUI](https://pyautogui.readthedocs.io/en/latest/)
- [Subprocess](https://docs.python.org/3/library/subprocess.html)
- [Logging](https://docs.python.org/3/library/logging.html)

The lesson explanations, exercises, fixtures and project are original teaching material. Primary documentation is used to check API behaviour.
