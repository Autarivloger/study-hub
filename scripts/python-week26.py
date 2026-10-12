"""Author Week 26 additively; execute each output in an isolated practice folder."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

ROOT = Path(__file__).resolve().parent.parent
DAYS = {f"26.{d}": {"parts": []} for d in range(6)}
EXECUTED = 0


def clean(code):
    return textwrap.dedent(code).strip() + "\n"


def output(code):
    global EXECUTED
    with tempfile.TemporaryDirectory(prefix="studyhub-w26-") as folder:
        run = subprocess.run([sys.executable, "-c", clean(code)], cwd=folder,
                             capture_output=True, encoding="utf-8", timeout=35,
                             env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    if run.returncode:
        raise RuntimeError(run.stderr + "\n" + code)
    EXECUTED += 1
    return run.stdout.replace("\r\n", "\n").rstrip()


def s(t, v=None, **extra):
    return {"t": t, **({"v": v} if v is not None else {}), **extra}


def add(day, title, goal, concepts, explanation, syntax, code, walk, mistake,
        task, solution, challenge, challenge_code, key, quizzes):
    parts = DAYS[f"26.{day}"]["parts"]
    index = len(parts)
    questions = []
    for n, (q, answer, wrong1, wrong2, why) in enumerate(quizzes):
        rotation = (index + n) % 3
        options = [answer, wrong1, wrong2]
        for _ in range(rotation):
            options.insert(0, options.pop())
        questions.append({"q": q, "options": options, "correct": rotation, "why": why})
    parts.append({"title": title, "sections": [
        s("h", title), s("key", "Learning objective: " + goal),
        *[s("new", name, note=note) for name, note in concepts],
        s("p", explanation), s("syn", syntax, note="Pattern first; run the complete example below."),
        s("code", clean(code)), s("out", output(code)), s("p", walk),
        s("mis", wrong=mistake[0], right=mistake[1], why=mistake[2]),
        s("ex", task, practiceId=f"26.{day}.{index}.build"),
        s("sol", code=clean(solution), out=output(solution), why="Build check: " + key),
        s("ex", "Mini challenge: " + challenge, practiceId=f"26.{day}.{index}.challenge"),
        s("sol", code=clean(challenge_code), out=output(challenge_code), why="Challenge check: " + key),
        s("try", q=quizzes[0][0], code="# Predict and explain before revealing.",
          a=quizzes[0][1], why=quizzes[0][4]),
        s("checkpoint", lesson={"id": f"course:26.{day}.{index}", "quiz": questions}), s("key", key),
    ]})

add(0, "1. Argparse: positional inputs, options and flags",
    "Turn a hard-coded script into a predictable command-line interface.",
    [("CLI; argv; Namespace", "A CLI accepts command-line tokens. argparse parses argv into a Namespace whose attributes hold validated option values."),
     ("Positional argument versus option", "A positional argument is chosen by its position; --limit is a named option with a value. --dry-run is an on/off flag using action='store_true'."),
     ("allow_abbrev=False", "Disable automatic long-option abbreviation in scripts used by schedulers so a future option cannot change how an abbreviated command is interpreted.")],
    "Weeks 23–25 used small command-line programs. This week makes their interface deliberate. Start with a required input path, a numeric limit and a dry-run flag. "
    "Pass a list to parse_args in the example so it runs without your terminal arguments; a real main() normally parses the supplied argv or sys.argv. "
    "Parsing converts tokens, but your program still needs domain checks such as positive limits and readable files. "
    "A flag must use store_true: type=bool would treat the nonempty string 'false' as True. Keep the parser separate from the function that performs work.",
    'parser.add_argument("input")\nparser.add_argument("--limit", type=int, default=10)\nparser.add_argument("--dry-run", action="store_true")\nargs = parser.parse_args(argv)',
    '''
    import argparse
    parser = argparse.ArgumentParser(prog="report", allow_abbrev=False)
    parser.add_argument("input")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(["sales.csv", "--limit", "3", "--dry-run"])
    print(args.input, args.limit, args.dry_run)
    print(type(args.limit).__name__)
    ''',
    "sales.csv positional input हो, --limit 3 named value र --dry-run flag। Example ले file पढेको छैन; arguments मात्र parse भएका हुन्। "
    "Input valid format मा आएपछि पनि file/domain validation छुट्टै चाहिन्छ।",
    ('parser.add_argument("--dry-run", type=bool)', 'parser.add_argument("--dry-run", action="store_true")',
     "bool('false') is True because the string is nonempty; flags should have explicit presence semantics."),
    "Add --format with choices csv/json and verify the selected format.",
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["csv", "json"], default="csv")
    print(parser.parse_args(["--format", "json"]).format)
    ''',
    "Verify an absent store_true flag is False rather than an empty string.",
    '''
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    print(parser.parse_args([]).dry_run)
    print(bool("false"))
    ''',
    "Use clear positional inputs, explicit options and presence-based flags. Parsing is one boundary; validating the domain and performing work are separate.",
    [("Does type=bool parse the string false as False?", "No", "Yes", "Only with a default", "Nonempty strings are truthy; use proper flags."),
     ("Does parsing an input filename prove that file exists?", "No", "Yes", "Only if it ends in csv", "File existence/shape requires further validation.")])

add(0, "2. Validation, help and meaningful exit codes",
    "Reject invalid arguments before side effects and return a status schedulers can inspect.",
    [("ArgumentTypeError; parser.error", "A custom converter can raise ArgumentTypeError for invalid CLI values. parser.error reports usage and normally exits with code 2."),
     ("Exit status; sys.exit(main())", "Conventionally 0 indicates success, 1 an operational failure and 2 CLI misuse. A scheduler can inspect these without guessing from printed text."),
     ("__main__ guard", "Only invoke the CLI when the file runs as a script. Importing its functions for tests should not automatically run the job.")],
    "A useful help page describes required input, units and effects. Invalid syntax should fail before any output file, email or GUI action. "
    "The example catches SystemExit only in a test so the lesson can display its status; production should let CLI misuse terminate. "
    "Keep operational failures distinct: 'input file unavailable' is not the same as 'unknown option'. "
    "Write main(argv=None) to return a status, and end the actual script with sys.exit(main()). Printing FAILED while returning 0 can fool Task Scheduler into reporting success.",
    'def positive(value): validate and return int\nparser.add_argument("--count", type=positive)\nif __name__ == "__main__": sys.exit(main())',
    '''
    import argparse, contextlib, io
    def positive(text):
        value = int(text)
        if value < 1:
            raise argparse.ArgumentTypeError("count must be positive")
        return value
    parser = argparse.ArgumentParser(prog="job")
    parser.add_argument("--count", type=positive, default=1)
    print("Help includes count:", "--count" in parser.format_help())
    with contextlib.redirect_stderr(io.StringIO()):
        try:
            parser.parse_args(["--count", "0"])
        except SystemExit as error:
            print("CLI status:", error.code)
    ''',
    "0 count reject हुँदा code 2 आउँछ। stderr capture test को लागि हो, failure लुकाउन होइन। "
    "Scheduler लाई failure थाहा दिन actual script को exit status सही चाहिन्छ।",
    ('print("FAILED"); return 0', 'print failure to stderr; return a nonzero status',
     "Schedulers and calling processes primarily observe the exit code, not the wording of stdout."),
    "Write a main-like function that returns 0 on success and 1 on an operational failure.",
    '''
    def main(available):
        if not available:
            return 1
        return 0
    print(main(True), main(False))
    ''',
    "Verify --help exits successfully without executing a job.",
    '''
    import argparse, contextlib, io
    parser = argparse.ArgumentParser(prog="job")
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            parser.parse_args(["--help"])
        except SystemExit as error:
            print_to_show = error.code
    print("Help status:", print_to_show)
    ''',
    "Help should reveal the interface; validation should precede effects. Expose meaningful nonzero failures and keep imported modules inert.",
    [("What is the normal argparse status for invalid CLI arguments?", "2", "0", "Always 100", "Argparse reports usage and exits with code 2."),
     ("What should a failed scheduled operation return?", "A nonzero status", "Always zero", "Only a success message", "The caller needs a machine-readable failure signal.")])

add(0, "3. Subcommands: plan, run and verify",
    "Use explicit command names to separate inspection, execution and verification.",
    [("add_subparsers; required=True", "A subparser provides a CLI for a named operation. Requiring one prevents silently choosing a state-changing default."),
     ("set_defaults handler", "Attach a callable to a parsed command; dispatch through that handler rather than a long chain of string comparisons."),
     ("Pure planning", "A plan describes intended effects without performing them. Keeping planning functions free of writes makes both CLI use and tests clearer.")],
    "A backup tool needs more than options: plan shows proposed files, run executes and verify checks a saved result. "
    "These are different user intentions, so name them explicitly. The fixture handlers below only return descriptive text; actual work is introduced later. "
    "set_defaults puts the chosen handler on Namespace. Each handler still receives validated inputs and must enforce its own effects. "
    "Subcommands reduce accidental execution only when the implementation respects that boundary. Do not make plan create folders or send a test email.",
    'sub = parser.add_subparsers(dest="command", required=True)\nplan = sub.add_parser("plan")\nplan.set_defaults(handler=plan_job)\nargs.handler(args)',
    '''
    import argparse
    def plan(args):
        return "PLAN " + args.source
    def verify(args):
        return "VERIFY " + args.source
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    for name, handler in [("plan", plan), ("verify", verify)]:
        command = commands.add_parser(name)
        command.add_argument("source")
        command.set_defaults(handler=handler)
    args = parser.parse_args(["plan", "notes"])
    print(args.command, args.handler(args))
    ''',
    "plan र verify अलग operations हुन्। handler parsed Namespace मा जोडियो र त्यो function call भयो। "
    "Output text बनाउनु मात्रै plan demo हो; यसले backup copy गरेको छैन।",
    ('No command supplied -> default to overwriting output', 'Require an explicit command and keep plan free of effects',
     "A missing command should not guess a destructive or external action."),
    "Select verify and route it to the correct handler.",
    '''
    import argparse
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify")
    verify.set_defaults(handler=lambda args: "Verification requested")
    args = parser.parse_args(["verify"])
    print(args.handler(args))
    ''',
    "Demonstrate a pure plan leaves its input list unchanged.",
    '''
    files = ["a.txt", "b.txt"]
    before = list(files)
    def plan(names):
        return [{"source": name, "action": "copy"} for name in sorted(names)]
    print(plan(files))
    print("Input unchanged:", files == before)
    ''',
    "Name operations by intent. Require explicit subcommands, dispatch to small handlers and keep plans pure.",
    [("Should the plan command perform copies?", "No", "Yes", "Only small files", "A plan describes intended work without applying it."),
     ("What does set_defaults(handler=...) provide?", "A callable for command dispatch", "A new Python interpreter", "An SMTP password", "The handler becomes an attribute on the parsed Namespace.")])

add(0, "4. Click: decorators and CLI tests",
    "Compare a small Click interface with argparse and test it without a terminal.",
    [("Click; @command; @option", "Click is a third-party CLI library. Decorators declare commands/options and pass parsed values into a function."),
     ("IntRange; is_flag", "IntRange constrains numeric values; is_flag=True gives a presence-based Boolean option. Do not mix library syntax with argparse's action names."),
     ("CliRunner; result.exit_code; output", "Click's test runner invokes a command with tokens and captures output/status. No terminal or external action is required.")],
    "Argparse needs no package installation and is enough for many tools. Click can make composed commands and decorators convenient; choose one CLI layer per project. "
    "The business function should remain reusable independently of the command library. Test defaults, invalid values and help. "
    "This fixture invokes only an echoing command, so you can see argument handling without writes. "
    "Decorators were introduced in earlier Python lessons; here the new topic is Click's parameter declarations, not a mysterious new language syntax.",
    '@click.command()\n@click.option("--count", type=click.IntRange(1,5), default=1)\n@click.option("--dry-run", is_flag=True)\ndef job(count, dry_run): ...',
    '''
    import click
    from click.testing import CliRunner
    @click.command()
    @click.option("--count", type=click.IntRange(1, 5), default=1)
    @click.option("--dry-run", is_flag=True)
    def job(count, dry_run):
        click.echo(f"count={count} dry={dry_run}")
    result = CliRunner().invoke(job, ["--count", "2", "--dry-run"])
    print(result.output.strip())
    print("Status:", result.exit_code)
    ''',
    "CliRunner test ले shell command चलाएको होइन; Click command function invoke गरेको हो। "
    "count integer range भित्र छ र flag True छ। Business work अलग function मा राख्न सकिन्छ।",
    ('@click.option("--dry-run", action="store_true")', '@click.option("--dry-run", is_flag=True)',
     "Click and argparse use different parameter APIs."),
    "Reject a count above 5 and check the captured status.",
    '''
    import click
    from click.testing import CliRunner
    @click.command()
    @click.option("--count", type=click.IntRange(1, 5))
    def job(count):
        click.echo(count)
    result = CliRunner().invoke(job, ["--count", "8"])
    print("Status:", result.exit_code)
    print("Range mentioned:", "range" in result.output.lower())
    ''',
    "Test that --help succeeds and lists an option.",
    '''
    import click
    from click.testing import CliRunner
    @click.command()
    @click.option("--dry-run", is_flag=True)
    def job(dry_run):
        pass
    result = CliRunner().invoke(job, ["--help"])
    print(result.exit_code, "--dry-run" in result.output)
    ''',
    "Choose a CLI library deliberately and keep work independent. Test successful parsing, rejection and help with captured output/status.",
    [("Is Click part of Python's standard library?", "No", "Yes", "Only on Windows", "It is installed separately."),
     ("What does CliRunner capture?", "Output and exit status", "Your browser passwords", "A real mailbox", "It invokes the command in a test context.")])

add(1, "1. Scheduling: trigger, job and execution environment",
    "Explain why a scheduled job needs explicit paths, account, time zone and failure reporting.",
    [("Trigger versus job", "The trigger decides when a run is due. The job performs one finite unit of work. Keep them separate so the job can also run manually."),
     ("Working directory; absolute paths", "An unattended process may start in a different folder from your terminal. Use absolute input/output paths and an explicit interpreter from the intended environment."),
     ("Missed run; overlap policy", "A sleeping/offline machine can miss a trigger. A long run can overlap the next trigger. Decide whether to catch up, skip or queue instead of assuming the scheduler handles it your way.")],
    "A script that works in your terminal can fail overnight because its environment is different. Record the interpreter, script path, input/output paths, account permissions, time zone and logging destination. "
    "Avoid prompts in unattended jobs: no person is there to type a password or click OK. "
    "A job should run once and exit, while Task Scheduler/cron starts it at the requested time. In-process schedulers are another design and must stay running. "
    "The following fixture describes a job; it registers no task. Later scheduling instructions are for your own practice computer after a successful manual dry-run.",
    'trigger configuration -> launch explicit interpreter/script/arguments\njob -> validate -> work once -> log outcome -> exit',
    '''
    from pathlib import Path
    config = {"time": "08:00", "timezone": "Asia/Tokyo",
              "overlap": "skip", "missed_run": "manual catch-up"}
    paths = [Path("practice") / "input", Path("practice") / "output"]
    print(config["time"], config["timezone"])
    print("Policies:", config["overlap"], "/", config["missed_run"])
    print("Unattended prompts:", False)
    ''',
    "Trigger 08:00 हो; actual file work छुट्टै job हो। Paths demo हुन्, scheduler register भएको छैन। "
    "Computer sleep हुँदा catch-up के गर्ने र overlap के गर्ने भनेर स्पष्ट निर्णय चाहिन्छ।",
    ('Assume the scheduler starts in the folder used by your terminal', 'Configure absolute paths and a known interpreter/environment',
     "Scheduled processes can have different working directories and environment variables."),
    "Build a command argument list from an explicit interpreter and script path; do not run it yet.",
    '''
    from pathlib import Path
    interpreter = Path("venv") / "Scripts" / "python.exe"
    script = Path("practice") / "backup.py"
    command = [str(interpreter), str(script), "--dry-run"]
    print(command[-1], len(command))
    ''',
    "Classify two triggers arriving while a run is still active under a skip-overlap policy.",
    '''
    running = True
    for trigger in ["08:00", "08:05"]:
        print(trigger, "skip overlap" if running else "start")
    ''',
    "Schedule a finite, independently testable job. Specify paths, account, time zone, missed-run behaviour and overlap policy; do not rely on an interactive terminal.",
    [("Does a scheduler necessarily use your terminal's working folder?", "No", "Yes", "Only for Python", "Execution context must be configured explicitly."),
     ("Who decides what happens after a missed trigger?", "Your scheduler/job policy", "A product title", "CSV quoting", "Catch-up, skip and queue behaviour differ.")])

add(1, "2. Windows Task Scheduler: configure an explicit action",
    "Translate a tested Python CLI into a daily Windows task without embedding a password.",
    [("Task Scheduler action fields", "Program/script is the interpreter executable; Add arguments holds script/options; Start in is the working folder. Separate fields handle paths with spaces more clearly."),
     ("Task history; Last Run Result", "Check the task's recorded start/end and result code, then inspect the job's log. A trigger occurring is not proof the work completed."),
     ("Account/session conditions", "The chosen account needs file permissions. GUI tasks normally need the relevant interactive session; file-only jobs do not need a visible desktop.")],
    "On your practice computer open Task Scheduler, create a named task, choose a Daily trigger and check the Windows local time zone. "
    "For this week's project select the Python executable from its environment, enter a quoted full script path plus full source/destination paths in Add arguments, and set Start in to the script folder. "
    "First use --dry-run. Run the task manually, inspect its log/result, then decide power/sleep and missed-run settings. Set 'Do not start a new instance' when using the project's single-run lock. "
    "Do not put account passwords in a BAT file, public HTML or command examples. Configure any required account authentication in the operating system's own task interface. "
    "The fixture below builds fields only; no Windows task is registered by the lesson.",
    'Program/script: full path to python.exe\nAdd arguments: quoted script + quoted input/output + --dry-run\nStart in: script directory\nDaily trigger: chosen local time',
    '''
    action = {
        "program": r"C:\\Practice\\venv\\Scripts\\python.exe",
        "arguments": r'"C:\\Practice\\backup_job.py" "C:\\Practice\\notes" "C:\\Practice\\backups" --dry-run',
        "start_in": r"C:\\Practice",
    }
    print("Python executable:", action["program"].endswith("python.exe"))
    print("Dry-run first:", "--dry-run" in action["arguments"])
    print("Password in action:", "password" in action["arguments"].lower())
    ''',
    "तीन fields छुट्टाछुट्टै भरिन्छन्। Dry-run ले पहिले plan देखाउँछ। Task चलेपछि Last Run Result र आफ्नै log दुबै हेर्नुपर्छ। "
    "यो configuration example मात्र हो, तिम्रो Windows मा task बनाइएको छैन।",
    ('Put Python, script and options all in Program/script', 'Separate interpreter, arguments and Start in',
     "The executable field and argument parsing are different configuration steps."),
    "Recognize status 0 as success and status 1 as an operational failure.",
    '''
    for result in [0, 1]:
        print(result, "success" if result == 0 else "inspect failure log")
    ''',
    "Compare a GUI job with a file-only backup when deciding whether an interactive desktop is needed.",
    '''
    jobs = [("copy local files", False), ("type in an editor", True)]
    for name, needs_desktop in jobs:
        print(name, "interactive desktop needed:", needs_desktop)
    ''',
    "Use separate action fields and a tested CLI. Check result plus logs, choose conditions intentionally and keep account secrets out of source.",
    [("Does a successful trigger prove the backup completed?", "No", "Yes", "Only daily triggers", "The launched job can still fail; inspect status/logs."),
     ("Where should a task account password be configured if needed?", "The operating system's task authentication interface", "Public HTML", "A committed BAT file", "Do not embed secrets in source or example arguments.")])

add(1, "3. Cron: a time expression is not the whole job",
    "Read a basic daily cron expression and account for its limited environment.",
    [("Cron five-field expression", "Classic cron uses minute, hour, day of month, month and day of week, followed by a command. Implementations vary; these examples use basic daily fields."),
     ("PATH; stdout/stderr redirection", "Cron may have a limited PATH and environment. Use explicit executable paths, and send output/error to a known log rather than assuming a terminal."),
     ("Time-zone implementation differences", "Cron generally uses its configured scheduling time zone; per-entry time-zone support differs. Verify the installed scheduler instead of assuming CRON_TZ is universal.")],
    "On a Linux practice machine, 0 8 * * * means minute 0 at hour 8 every day under that cron's configured zone. "
    "Use crontab -e to edit your own schedule after manually testing the finite command. "
    "An example command could use /home/student/venv/bin/python with absolute script/source/destination paths and append both output streams to a log. "
    "Cron starts processes; it does not guarantee the machine was awake, the job succeeded or duplicate runs were prevented. "
    "The fixture parses fields for explanation; it does not install or execute a schedule. Windows users can focus on the preceding Task Scheduler part.",
    '0 8 * * * /absolute/python /absolute/job.py ... >> /absolute/job.log 2>&1',
    '''
    fields = "0 8 * * *".split()
    labels = ["minute", "hour", "day-of-month", "month", "day-of-week"]
    for label, value in zip(labels, fields):
        print(label + ":", value)
    ''',
    "पहिलो field minute हो, दोस्रो hour। 0 8 ले daily08:00 बताउँछ। "
    "Time zone, log path र interpreter अर्को configuration हो; expression मात्रै पूर्ण automation होइन।",
    ('Assume python on PATH and use relative input filenames', 'Use a known interpreter and absolute paths in the scheduled command',
     "A restricted environment can invoke a different interpreter or fail to locate files."),
    "Read a 30 18 daily expression as 18:30.",
    '''
    minute, hour, *_ = "30 18 * * *".split()
    print(f"Daily {int(hour):02d}:{int(minute):02d}")
    ''',
    "Explain redirection of both output streams using a prepared command string without executing it.",
    '''
    command = "/home/student/venv/bin/python /home/student/job.py --dry-run >> /home/student/job.log 2>&1"
    print("Append log:", ">>" in command)
    print("Include stderr:", "2>&1" in command)
    ''',
    "Read cron fields in order, verify the scheduler's time zone/environment and capture failures. A time expression alone does not provide durability or overlap control.",
    [("What is the first field in the basic five-field cron syntax?", "Minute", "Year", "Interpreter name", "The order starts minute, hour, day-of-month, month, day-of-week."),
     ("Is per-entry time-zone support identical in every cron?", "No", "Yes", "Only for Python", "Check the installed implementation.")])

add(1, "4. An in-process scheduler must stay alive",
    "Use schedule for simple recurring functions and understand its persistence limits.",
    [("schedule.Scheduler; every; do", "The third-party schedule library registers functions in a Python process. A Scheduler instance keeps this example's jobs separate from other test state."),
     ("run_pending; run_all; cancel_job", "run_pending runs due jobs while the process polls; run_all forces registered jobs for testing. cancel_job removes a registration."),
     ("No built-in durable job store", "The library does not persist registrations across process restarts or automatically replay every missed interval. Long jobs block its default sequential execution.")],
    "An in-process scheduler is useful for a small script you deliberately keep running. Register the job once, then a real loop calls run_pending and sleeps briefly. "
    "Our runnable example uses run_all to demonstrate the function immediately; it does not pretend that a minute passed. "
    "Closing Python stops this scheduler. Use an operating-system scheduler when you want to start a finite job even after the previous Python process exited. "
    "Do not schedule a blocking GUI task inside a tight loop and expect accurate execution of every other job. Handle exceptions and missed-run behaviour explicitly.",
    'scheduler.every(1).minutes.do(job)\n# Real polling loop: run_pending(); sleep briefly\n# Test only: scheduler.run_all(delay_seconds=0)',
    '''
    import schedule
    events = []
    scheduler = schedule.Scheduler()
    job = scheduler.every(1).minutes.do(lambda: events.append("run"))
    print("Registered:", len(scheduler.jobs))
    scheduler.run_all(delay_seconds=0)
    print(events)
    scheduler.cancel_job(job)
    print("Remaining:", len(scheduler.jobs))
    ''',
    "run_all test भएकाले तुरुन्तै run आयो, scheduled minute कुरेको छैन। "
    "Process बन्द भयो भने registrations हराउँछन्। Task Scheduler जस्तो external trigger र यो processभित्रको scheduler फरक हुन्।",
    ('Register a schedule and exit, expecting it to run tomorrow', 'Keep the process polling or use an external scheduler to launch a finite job',
     "In-process registrations do not run after the process has stopped."),
    "Register two jobs and force both once in a test.",
    '''
    import schedule
    events = []
    scheduler = schedule.Scheduler()
    scheduler.every(1).minutes.do(lambda: events.append("A"))
    scheduler.every(2).minutes.do(lambda: events.append("B"))
    scheduler.run_all(delay_seconds=0)
    print(events)
    ''',
    "Cancel all classroom registrations and verify none remain.",
    '''
    import schedule
    scheduler = schedule.Scheduler()
    scheduler.every(1).hours.do(lambda: None)
    scheduler.clear()
    print(len(scheduler.jobs))
    ''',
    "In-process scheduling needs a live polling process. Separate forced test execution from real time, and understand missed runs, blocking jobs and nonpersistent registrations.",
    [("Will schedule run jobs after the Python process exits?", "No", "Yes", "Only daily jobs", "Its registrations live in the process."),
     ("What does run_all do in this lesson?", "Forces jobs immediately for testing", "Waits one day", "Installs cron entries", "It is a test shortcut, not proof that a trigger elapsed.")])

MESSAGE = '''
from email.message import EmailMessage
message = EmailMessage()
message["From"] = "student@example.org"
message["To"] = "student@example.org"
message["Subject"] = "Practice report"
message.set_content("Completed: 3 tasks\\nFailures: 0\\n")
'''

add(2, "1. Compose an email before sending anything",
    "Build and inspect a structured message offline.",
    [("EmailMessage; headers; set_content", "EmailMessage builds a standards-aware message. Headers describe sender/recipient/subject; set_content sets the body. Creating or serializing a message does not deliver it."),
     ("SMTP envelope versus visible headers", "The SMTP envelope tells a server where to deliver; visible From/To headers are message content. Do not assume headers alone prove sender identity or successful delivery."),
     ("Reserved example addresses", "example.org addresses here are fictional fixtures. Replace them only in your private practice configuration when you deliberately choose to send.")],
    "Automations should first prepare a useful, small report: what ran, which records/files were processed, whether it succeeded and where to inspect details. "
    "Use the email library rather than hand-building header lines. A body can contain Unicode; the library handles message encoding. "
    "A preview is a message, not a delivery. Do not log the entire message when it contains sensitive information. "
    "Every runnable email example in this course either inspects local message data or mocks the transport; studying the lesson sends no email.",
    'message = EmailMessage()\nmessage["Subject"] = "Practice report"\nmessage.set_content(body)\n# Compose/inspect first; transport is separate',
    MESSAGE + '''
print(message["Subject"])
print(message["To"])
print(message.get_content().strip())
''',
    "EmailMessage तयार भयो, mailbox मा गएको छैन। Subject/header र body छुट्टाछुट्टै छन्। "
    "Automation report मा result र inspect गर्ने स्थान स्पष्ट राख, secretdata नहाल।",
    ('Concatenate arbitrary input into raw email header lines', 'Use EmailMessage header/body APIs and validate intended recipients',
     "Structured APIs and a recipient policy are clearer than manual protocol-string assembly."),
    "Compose a Japanese/Nepali body and verify the text remains readable before delivery.",
    '''
    from email.message import EmailMessage
    message = EmailMessage()
    message["Subject"] = "Study report"
    message.set_content("日本語 अभ्यास पूरा भयो।")
    print(message.get_content().strip())
    ''',
    "Keep a preview operation separate from a send operation using an explicit flag.",
    '''
    send_enabled = False
    result = {"message_prepared": True, "sent": send_enabled}
    print(result)
    ''',
    "Compose, inspect and validate first. Message preparation, SMTP acceptance and final delivery are separate states.",
    [("Does EmailMessage.set_content send email?", "No", "Yes", "Only if To exists", "It prepares message data; transport is separate."),
     ("Do visible To headers alone prove delivery?", "No", "Yes", "Only for ASCII", "Delivery uses a transport/envelope and can fail later.")])

add(2, "2. Attach a generated report with an explicit MIME type",
    "Prepare an attachment without reading personal files or relying on a live mailbox.",
    [("add_attachment; MIME maintype/subtype", "Attachment metadata describes the payload type. A CSV can use text/csv, a PDF application/pdf; attach known bytes with an intended filename."),
     ("iter_attachments; get_payload(decode=True)", "Inspect attachment parts and decode payload bytes to verify the prepared content. This is message preparation, not proof of delivery."),
     ("Attachment size and data minimization", "Choose the exact report file, enforce a size policy and avoid attaching directories, credentials or unrelated personal data.")],
    "Week 24 generated reports; now attach one intentionally. The example uses an authored CSV byte string, so no private file is read. "
    "In your practice tool read a known report path, reject oversized payloads and include only the data you intend to share. "
    "The MIME type and filename help the recipient's client display it; they do not validate that the bytes form a correct report. "
    "Inspect the generated message and attachment bytes before choosing live delivery. Never upload a real private report into this public website source.",
    'message.add_attachment(payload, maintype="text", subtype="csv", filename="report.csv")',
    MESSAGE + '''
payload = b"task,status\\nreading,done\\n"
message.add_attachment(payload, maintype="text", subtype="csv", filename="report.csv")
part = next(message.iter_attachments())
print(part.get_filename(), part.get_content_type())
print(part.get_payload(decode=True).decode("utf-8").strip())
''',
    "Authored CSV bytes attachment बने। File name र MIME metadata मिले पनि reportकोcontent ठीक छ कि separately जाँच्नुपर्छ। "
    "Message तयार भएको मात्र हो; SMTP send गरिएको छैन।",
    ('Attach every file in the working folder', 'Attach only a validated chosen report under a size policy',
     "A broad file selection can include unintended data and does not identify the desired report."),
    "Reject a payload exceeding a tiny classroom limit before adding it.",
    '''
    payload, limit = b"123456", 5
    print("Attachment permitted:", len(payload) <= limit)
    ''',
    "Verify the exact attachment bytes round-trip unchanged.",
    MESSAGE + '''
payload = b"task,status\\nreading,done\\n"
message.add_attachment(payload, maintype="text", subtype="csv", filename="report.csv")
print(next(message.iter_attachments()).get_payload(decode=True) == payload)
''',
    "Attach a chosen validated payload, specify its type/name and inspect byte content. Keep size and sharing decisions explicit.",
    [("Does setting MIME type validate the report contents?", "No", "Yes", "Only for CSV", "Metadata describes how to interpret bytes; it does not validate the report."),
     ("What should an attachment operation read?", "The intended validated report", "Every file nearby", "Stored passwords", "Minimize and explicitly choose the data to share.")])

add(2, "3. SMTP with TLS, private configuration and mocked transport",
    "Understand the sending sequence and test it without using real credentials or delivery.",
    [("smtplib.SMTP; STARTTLS; SSL context", "SMTP talks to a mail server. STARTTLS upgrades a supported connection to TLS using a verifying SSL context; some providers instead require SMTP_SSL from the start."),
     ("login; send_message; refused recipients", "Authenticate under the provider's supported policy, then send a prepared message. send_message can return refused-recipient details; acceptance does not prove inbox delivery."),
     ("Private environment/secret storage", "Read secrets from private runtime configuration rather than public HTML or source. Environment variables are not magical encryption; OS access and logs still matter.")],
    "Use your provider's documented host, port and authentication method. Some providers require app credentials or OAuth rather than a normal account password; do not assume one universal setup. "
    "The shown sequence uses STARTTLS, checks for an encrypted connection before login and then sends. It does not disable certificate verification. "
    "Our test replaces SMTP with a mock and uses a visibly fictional credential; there is no real network connection or email. "
    "Production loads private configuration outside Git, checks refused recipients, reports failure and avoids logging secret values. Do not ask someone to paste a token into lesson code.",
    'with SMTP(host, port, timeout=10) as client:\n    client.ehlo()\n    client.starttls(context=ssl.create_default_context())\n    client.ehlo()\n    client.login(private_user, private_secret)\n    refused = client.send_message(message)',
    MESSAGE + '''
import smtplib, ssl
from unittest.mock import patch
with patch("smtplib.SMTP") as smtp:
    client = smtp.return_value.__enter__.return_value
    client.send_message.return_value = {}
    with smtplib.SMTP("mail.example.org", 587, timeout=10) as connection:
        connection.ehlo()
        connection.starttls(context=ssl.create_default_context())
        connection.ehlo()
        connection.login("fixture-user", "FICTIONAL-NOT-A-SECRET")
        refused = connection.send_message(message)
    print("TLS requested:", client.starttls.called)
    print("Accepted by mock server:", not refused)
    print("Real delivery:", False)
''',
    "SMTP patch भएकाले email पठाइएन। Mock server accepted भनेको real inbox delivery होइन। "
    "Actual credentials privateconfiguration बाट आउनुपर्छ, source/code मा राख्नु हुँदैन। Providerकोpolicy पहिला हेर्नुपर्छ।",
    ('Hard-code real account secrets and disable TLS verification', 'Load private configuration and use the provider-supported encrypted authentication path',
     "Secrets belong outside published code; certificate verification protects the connection."),
    "Mock a refused recipient and demonstrate that it is not a successful all-recipient send.",
    MESSAGE + '''
import smtplib
from unittest.mock import patch
with patch("smtplib.SMTP") as smtp:
    client = smtp.return_value.__enter__.return_value
    client.send_message.return_value = {"student@example.org": (550, b"fixture rejection")}
    with smtplib.SMTP("mail.example.org", 587, timeout=10) as connection:
        refused = connection.send_message(message)
    print("All recipients accepted:", not refused)
''',
    "Validate that missing private configuration blocks live sending; do not print secret values.",
    '''
    config = {"host": "", "user": "", "secret": ""}
    ready = all(config[name] for name in ["host", "user", "secret"])
    print("Live transport ready:", ready)
    print("Action:", "stop and configure privately" if not ready else "send deliberately")
    ''',
    "Test with mocked transport first. Real sending requires provider-specific private configuration, verified TLS and recipient/error checks; server acceptance is not inbox proof.",
    [("Does a successful mocked send prove real inbox delivery?", "No", "Yes", "Only for one recipient", "A mock exercises program logic without a real transport."),
     ("Where should real SMTP secrets live?", "Private runtime configuration outside Git", "Public HTML", "A committed JS string", "Published source cannot hide a usable secret.")])

add(2, "4. Notifications and durable failure reports",
    "Separate the work result from notification delivery and preserve a local report.",
    [("Notifier adapter", "Pass a callable that receives a title/body. Tests record calls; a deliberate desktop or push adapter can later use a platform-specific library."),
     ("Outbox", "A local queue/report records pending notifications. Delivery can fail independently of the work, so preserve evidence and avoid pretending the notification succeeded."),
     ("Delivery semantics", "Retrying a notification can produce duplicates after ambiguous acknowledgement. Exactly-once delivery needs additional design; a local recorded event is not that guarantee.")],
    "A popup may disappear while you are away, and a remote push service may be unavailable. Keep a persistent local outcome record even when notifications are enabled. "
    "The fixture notifier appends to a list; it does not display a system popup. A desktop implementation could call a platform library's notification function, but verify OS/session support first. "
    "A backup succeeding while email delivery fails is two outcomes, not a failed backup that should be copied again. "
    "Make the report useful: operation, result, counts and an inspection path. Exclude secrets. Track pending/sent/failed states honestly and avoid unbounded retry spam.",
    'work_result -> persist outcome\nnotify adapter -> separate delivery result\non delivery failure: retain local pending report',
    '''
    events = []
    def notify(title, body):
        events.append({"title": title, "body": body})
    result = {"status": "success", "files": 3}
    notify("Backup completed", f"Files: {result['files']}. Inspect local log.")
    print(events[0])
    ''',
    "List मा notification event capture भयो, popup/push गएको छैन। Work result र delivery result अलग राख। "
    "Alert fail भए backup फेरिcopy गर्नुपर्ने अर्थ हुँदैन; local report बचाउनुपर्छ।",
    ('Notification failed -> rerun all successful work immediately', 'Keep the completed work result and retry only its pending notification deliberately',
     "Coupling delivery retry to the work can duplicate effects."),
    "Preserve an outbox event when the injected notifier fails.",
    '''
    pending = [{"id": "run-1", "status": "pending"}]
    def notify(event):
        raise OSError("fixture unavailable")
    try:
        notify(pending[0])
    except OSError:
        pending[0]["status"] = "pending"
    print(pending)
    ''',
    "Create a short failure summary that references a local log without including credentials.",
    '''
    event = {"operation": "backup", "status": "failed", "log": "job.log"}
    print(f"{event['operation']}: {event['status']}; inspect {event['log']}")
    ''',
    "Persist outcomes and separate work from delivery. A simulated notifier is a test adapter; actual OS/push/email delivery requires explicit configuration.",
    [("If notification delivery fails after a successful copy, must the copy run again?", "No", "Yes", "Only for email", "Delivery and completed work have separate retry boundaries."),
     ("Does an outbox alone guarantee exactly-once delivery?", "No", "Yes", "Only for a file", "Ambiguous acknowledgement and retry can still create duplicates.")])

GUI = '''
class StopAutomation(Exception):
    pass

class FakeDesktop:
    """Test double only: no actual mouse, keyboard or personal screenshot."""
    def __init__(self):
        self.FAILSAFE = True
        self.PAUSE = 0.1
        self.corner = False
        self.calls = []
    def check(self):
        if self.FAILSAFE and self.corner:
            raise StopAutomation("Fixture fail-safe")
    def moveTo(self, x, y, duration=0):
        self.check()
        self.calls.append(("move", x, y))
    def write(self, text, interval=0):
        self.check()
        self.calls.append(("write", text))
    def hotkey(self, *keys):
        self.check()
        self.calls.append(("hotkey",) + keys)
'''

add(3, "1. GUI automation: coordinates, focus and fail-safe",
    "Plan a small owned-window interaction and stop safely when context is wrong.",
    [("PyAutoGUI; moveTo; write; hotkey", "The third-party library operates the real mouse/keyboard. Coordinates refer to a screen, write types supported key characters and hotkey presses a key combination."),
     ("FAILSAFE; PAUSE", "PyAutoGUI's fail-safe can raise FailSafeException when the pointer is in a supported screen corner. PAUSE adds a pause after calls; it is not proof a window is ready."),
     ("Test double", "FakeDesktop below records intended calls and simulates a stop. It is not PyAutoGUI or a real desktop; examples do not move your mouse.")],
    "Prefer a file API or browser locator over clicking coordinates when possible. GUI automation depends on the correct window, focus, resolution and visible state. "
    "For personal practice, use an empty scratch editor, verify its focus manually and choose known safe coordinates. Never aim at an account/payment/delete interface. "
    "Keep FAILSAFE enabled and test how to stop before any longer run. A sleeping/locked session is not a working interactive desktop. "
    "The runnable lesson uses a fake adapter so every call is inspectable. A deliberate real exercise imports pyautogui and passes it to the same small workflow after checking the window.",
    'pyautogui.FAILSAFE = True\npyautogui.PAUSE = 0.2\n# Confirm scratch window focus before moveTo/write/hotkey',
    GUI + '''
desktop = FakeDesktop()
desktop.moveTo(100, 100, duration=0.2)
desktop.write("Python practice", interval=0.05)
print(desktop.calls)
print("Real desktop used:", False)
''',
    "Coordinates fake desktop का हुन्। Real pyautogui मा mouse/keyboard चल्छ, त्यसैले scratchwindow focus verify गरेर मात्र प्रयोग गर। "
    "PAUSE केवलdelayहो, सहीwindow खुल्योभन्नेproof होइन।",
    ('Disable FAILSAFE so the loop never stops', 'Keep FAILSAFE enabled and bound the interaction count',
     "A stop mechanism matters when a GUI action targets the wrong window."),
    "Set the fixture pointer at a corner and prove writing stops.",
    GUI + '''
desktop = FakeDesktop()
desktop.corner = True
try:
    desktop.write("Should not type")
except StopAutomation:
    print("Stopped")
print(desktop.calls)
''',
    "Record Ctrl+A only in the simulated scratch editor and inspect the combination.",
    GUI + '''
desktop = FakeDesktop()
desktop.hotkey("ctrl", "a")
print(desktop.calls)
''',
    "GUI automation needs verified context and a tested stop. Fake adapters verify intentions; they cannot prove a real window's focus or layout.",
    [("Does FakeDesktop move the real mouse?", "No", "Yes", "Only on Windows", "It is a test double that records calls."),
     ("Does PAUSE prove the correct window is ready?", "No", "Yes", "Only after a second", "Time elapsed is not a readiness condition.")])

add(3, "2. Screenshots and regions without exposing personal screens",
    "Understand region coordinates and verify an authored screenshot fixture.",
    [("screenshot(region=(left,top,width,height))", "PyAutoGUI can capture a defined screen region. Limit captures to the intended scratch window; screenshots may contain private information."),
     ("Pillow Image; size; crop", "Pillow manipulates images. This example creates an image from scratch and crops it; it captures no real screen."),
     ("Coordinate spaces", "Screen coordinates, window-relative coordinates and image pixel coordinates are different. A crop box uses left/top/right/bottom rather than region width/height.")],
    "A screenshot is an observation to verify context, not proof that a later click remains safe. Windows can move and focus can change. "
    "Use the smallest relevant region, inspect it locally, and keep private captures out of public Git. "
    "The example creates a 200×100 authored image and crops a 50×30 area. This teaches coordinate arithmetic without reading your screen. "
    "PyAutoGUI's screenshot region expects width/height, while Pillow crop expects endpoint coordinates. Mixing them can crop the wrong place.",
    'screen region: (left, top, width, height)\nPillow crop: (left, top, left+width, top+height)',
    '''
    from PIL import Image
    image = Image.new("RGB", (200, 100), color="white")
    left, top, width, height = 10, 20, 50, 30
    crop = image.crop((left, top, left + width, top + height))
    print(image.size, crop.size)
    print(crop.getpixel((0, 0)))
    ''',
    "Image authoredfixture हो, computer screenshot होइन। crop मा right=left+width चाहिन्छ। "
    "Personal capture लाईpublic repo मा नराख; अभ्यासकासानाscratchregion मात्र हेर्नुपर्छ।",
    ('image.crop((left, top, width, height))', 'image.crop((left, top, left + width, top + height))',
     "Crop's last two values are endpoints, not dimensions."),
    "Calculate a 40×20 crop beginning at x=5,y=6.",
    '''
    from PIL import Image
    image = Image.new("RGB", (100, 100))
    print(image.crop((5, 6, 5 + 40, 6 + 20)).size)
    ''',
    "Validate a region is inside an authored image before using it.",
    '''
    size = (200, 100)
    for left, top, width, height in [(10, 20, 50, 30), (190, 90, 30, 20)]:
        valid = 0 <= left and 0 <= top and width > 0 and height > 0 and left + width <= size[0] and top + height <= size[1]
        print(valid)
    ''',
    "Use an explicit region, correct coordinate space and bounds. Authored images test image logic; a real screenshot requires separate private context verification.",
    [("What are Pillow crop's last two values?", "Right and bottom endpoints", "Width and height", "Screen password", "They define the box's ending coordinates."),
     ("Does this Pillow fixture capture your desktop?", "No", "Yes", "Only in dark mode", "Image.new constructs an authored image.")])

add(3, "3. Image matching: missing or ambiguous is a stop",
    "Handle image-location failure and require a unique intended target.",
    [("locateOnScreen; ImageNotFoundException", "PyAutoGUI can locate a template image on screen. Current documented APIs can raise ImageNotFoundException when no image is found; confirm the installed version's behaviour."),
     ("confidence and OpenCV", "Confidence-based matching requires an optional OpenCV dependency. A match score is not a guarantee of semantic correctness."),
     ("Ambiguous target", "Repeated icons can match in several places. Restrict the search region and require a unique verified target before clicking; matching an image does not authorize the action.")],
    "Template matching is sensitive to scale, theme and layout. Save a small scratch-window template under the same visual conditions you test. "
    "Handle missing results explicitly; do not replace a failed match with a default coordinate and click anyway. "
    "The fixture uses candidate rectangles and selects only one within an intended region. It does not run real screen matching. "
    "For a real scratch test, catch pyautogui.ImageNotFoundException, inspect any returned box, and stop on uncertainty. Consider the intended control label/state as well as the picture.",
    'try: box = pyautogui.locateOnScreen(template, region=known_region)\nexcept ImageNotFoundException: stop\nverify unique intended target before action',
    '''
    def unique_target(matches):
        if len(matches) != 1:
            raise ValueError("Need exactly one verified target")
        x, y, width, height = matches[0]
        return x + width // 2, y + height // 2
    print(unique_target([(10, 20, 40, 30)]))
    for candidates in [[], [(0, 0, 10, 10), (50, 50, 10, 10)]]:
        try:
            unique_target(candidates)
        except ValueError as error:
            print(error)
    ''',
    "एक target भए center calculate भयो। Zero वा दुईtargets हुँदा stop भयो, randomclick गरेन। "
    "Actual imagematching test यहाँ छैन; real scratchwindow मा version/theme/region जाँच्नुपर्छ।",
    ('No match -> click (0,0) and continue', 'Stop and inspect when a match is missing or ambiguous',
     "A fallback coordinate can trigger an unrelated control."),
    "Filter a candidate rectangle to the known scratch region.",
    '''
    candidates = [(10, 20, 20, 10), (300, 200, 20, 10)]
    allowed = [box for box in candidates if 0 <= box[0] and 0 <= box[1] and box[0] + box[2] <= 100 and box[1] + box[3] <= 100]
    print(allowed)
    ''',
    "Inspect that theme changes are a reason to revalidate templates, not a reason to ignore errors.",
    '''
    template_theme, current_theme = "light", "dark"
    print("Revalidate template:", template_theme != current_theme)
    ''',
    "Missing/ambiguous matches should stop. Verify the region, visual conditions and intended control; a confidence score is not an action guarantee.",
    [("What should zero image matches lead to?", "Stop and inspect", "A fallback click", "Unlimited clicking", "The intended target was not verified."),
     ("Does confidence prove the matched control's meaning?", "No", "Yes", "Only with OpenCV", "Visual similarity and semantic intent are different.")])

add(3, "4. A bounded scratch-editor workflow and verification",
    "Compose GUI steps with a context check, stop path and result verification.",
    [("Precondition; postcondition", "A precondition states what must be true before acting; a postcondition verifies the intended result afterward. They make a GUI script more than a blind sequence."),
     ("Supported text versus Unicode typing", "PyAutoGUI's write is key-based and is not a universal Unicode input method. For arbitrary Unicode prefer an application/file API or a carefully controlled platform-specific paste workflow."),
     ("Bounded workflow", "Use a small finite number of steps and stop on failed context/verification. Avoid a loop that keeps typing into an unknown window.")],
    "The workflow below types one ASCII practice line only after the injected context says the scratch editor is active. It verifies the expected text via a supplied read function. "
    "In a real GUI exercise, read-back must use actual application state or a reliable local observation; returning the expected string without observing is not proof. "
    "Our fake adapter provides controlled state for testing the logic. It proves the branch decisions, not actual OS focus. "
    "For Japanese text, avoid assuming write can type every character; generating a UTF-8 file can be a better automation than manipulating a keyboard.",
    'verify scratch context -> perform finite steps -> read actual result -> compare\non fail-safe or mismatch: stop and report',
    GUI + '''
def scratch_job(desktop, context_ok, read_text):
    if not context_ok():
        raise ValueError("Wrong window")
    desktop.write("Python practice")
    if read_text() != "Python practice":
        raise ValueError("Verification failed")
    return "verified in fixture"
desktop = FakeDesktop()
print(scratch_job(desktop, lambda: True, lambda: "Python practice"))
print(desktop.calls)
''',
    "Context र result दुवै fakeobserver हुन्। Logicकोsuccess verified भयो, actualcomputerfocus verifiedभएको होइन। "
    "Realexercise गर्दा actualread-back चाहिन्छ। Japaneseकोलागि UTF8file API सजिलो र भरपर्दो हुनसक्छ।",
    ('Assume typing finished correctly because write returned', 'Read actual result and compare a postcondition',
     "Focus/layout problems can send keys elsewhere without the call knowing."),
    "Reject wrong-window context before any fake keystroke.",
    GUI + '''
desktop = FakeDesktop()
context_ok = False
if not context_ok:
    print("Stop: wrong window")
else:
    desktop.write("Practice")
print(desktop.calls)
''',
    "Generate a Japanese UTF-8 text file in a temporary folder instead of assuming keyboard support.",
    '''
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as name:
        path = Path(name) / "practice.txt"
        path.write_text("日本語の練習", encoding="utf-8")
        print(path.read_text(encoding="utf-8"))
    ''',
    "Prefer APIs for data work. GUI practice requires verified context, finite actions, working stop behaviour and a genuine observed postcondition.",
    [("Does a fake read-back prove real OS focus?", "No", "Yes", "Only with ASCII", "It verifies the program's test logic, not the actual desktop."),
     ("Is write a universal Japanese Unicode input method?", "No", "Yes", "Only with PAUSE", "It is key-based; choose an appropriate text/file/application interface.")])

add(4, "1. Subprocess: an argument list, not a shell string",
    "Run a small child process with explicit arguments and inspect its output.",
    [("subprocess.run; CompletedProcess", "run starts a child process, waits for it and returns its returncode/stdout/stderr when captured."),
     ("shell=False; argument list", "With shell=False and an argument list, the shell does not interpret separators or quoting. This prevents shell interpretation, but you must still validate the chosen program's own options/inputs."),
     ("sys.executable; capture_output; text", "sys.executable selects the current interpreter. capture_output captures both streams; text=True plus encoding defines text decoding.")],
    "Use a library when it already solves your task; subprocess is appropriate for an explicit external program. "
    "Do not build a shell command by joining untrusted strings. Pass each argument as a separate list item and keep shell=False. "
    "The example launches the same Python interpreter and prints one literal argument. Spaces and & belong to that argument rather than a shell instruction. "
    "This still does not make arbitrary executables or arbitrary Python code safe: our '-c' body is fixed authored test code, never user-provided text.",
    'result = subprocess.run([sys.executable, "-c", fixed_code, literal_argument], capture_output=True, text=True, encoding="utf-8", check=True, timeout=5)',
    '''
    import subprocess, sys
    result = subprocess.run([sys.executable, "-c", "import sys; print(sys.argv[1])", "book & notes"],
                            capture_output=True, text=True, encoding="utf-8", check=True, timeout=5)
    print(result.stdout.strip())
    print("Status:", result.returncode)
    ''',
    "book & notes एउटा literalargument हो; &shellseparator भएन। Fixed Pythonbody मात्रै run हुन्छ। "
    "Argumentlist ले shellinterpretation रोक्छ, तर chosenprogramकोallowedoptions/input validation अझैचाहिन्छ।",
    ('subprocess.run("tool " + user_input, shell=True)', 'Pass a validated executable and separate argument list with shell=False',
     "Shell strings can reinterpret input as commands; lists preserve token boundaries."),
    "Pass a filename containing spaces as one literal child argument.",
    '''
    import subprocess, sys
    result = subprocess.run([sys.executable, "-c", "import sys; print(len(sys.argv)-1); print(sys.argv[1])", "my report.csv"],
                            capture_output=True, text=True, check=True, timeout=5)
    print(result.stdout.strip())
    ''',
    "Verify stdout and stderr are captured separately.",
    '''
    import subprocess, sys
    result = subprocess.run([sys.executable, "-c", "import sys; print('result'); print('diagnostic', file=sys.stderr)"],
                            capture_output=True, text=True, check=True, timeout=5)
    print("OUT:", result.stdout.strip())
    print("ERR:", result.stderr.strip())
    ''',
    "Use a known executable and argument list, explicit encoding, timeout and result checks. shell=False removes shell parsing, not every possible program-level risk.",
    [("Does shell=False validate the target program's business options?", "No", "Yes", "Only for Python", "You still control which executable and inputs are allowed."),
     ("What does sys.executable choose?", "The current Python interpreter", "A random shell", "An email server", "It keeps the child in the intended interpreter environment.")])

add(4, "2. Nonzero exits and timeout recovery",
    "Handle process failure distinctly and avoid interpreting partial output as success.",
    [("check=True; CalledProcessError", "check=True raises when the child returns nonzero. The exception carries status and captured streams."),
     ("TimeoutExpired", "A subprocess timeout raises when the wait limit is exceeded. run handles its child cleanup, but an entire tree of grandchildren may need platform-specific management."),
     ("Retry boundary", "A child failure does not prove it had no side effects. Retrying a copy/send/payment-like operation blindly can duplicate partial work.")],
    "A child can print useful-looking output and then fail. Inspect its exit code; do not accept stdout alone as proof. "
    "Set a finite timeout to avoid unattended jobs waiting forever. The timeout covers run's wait behaviour; process creation and complex process trees have platform limitations. "
    "The fixture runs only small authored Python children, including a sleeping child in the challenge. No external system utility or personal process is touched. "
    "After a failure preserve evidence, inspect the work's postconditions and only retry a deliberately idempotent operation.",
    'try: subprocess.run(..., check=True, timeout=5)\nexcept CalledProcessError: inspect status/streams\nexcept TimeoutExpired: mark incomplete and inspect effects',
    '''
    import subprocess, sys
    try:
        subprocess.run([sys.executable, "-c", "import sys; print('partial'); sys.exit(3)"],
                       capture_output=True, text=True, check=True, timeout=5)
    except subprocess.CalledProcessError as error:
        print("Status:", error.returncode)
        print("Partial output:", error.stdout.strip())
    ''',
    "partial output आयो तरstatus3भएकोलेsuccessहोइन। Call failed भएपछि outputसँगैexitstatus बुझ। "
    "Retryपहिले partialsideeffects भएकिनभए हेर्नुपर्छ।",
    ('stdout exists -> success', 'Check returncode or use check=True, then verify the intended result',
     "A process can emit output before failing."),
    "Use check=False deliberately and branch on returncode.",
    '''
    import subprocess, sys
    result = subprocess.run([sys.executable, "-c", "import sys; sys.exit(2)"],
                            capture_output=True, text=True, timeout=5)
    print("Success:", result.returncode == 0)
    ''',
    "Timeout a private fixture child that sleeps; report failure without using its partial data.",
    '''
    import subprocess, sys
    try:
        subprocess.run([sys.executable, "-c", "import time; time.sleep(2)"],
                       capture_output=True, timeout=0.1)
    except subprocess.TimeoutExpired:
        print("Timed out: do not claim completed work")
    ''',
    "Status and timeout are first-class outcomes. Failure can follow partial effects; preserve evidence and verify state before any retry.",
    [("Can a failed child have printed stdout?", "Yes", "No", "Only with shell=True", "Output may be produced before the nonzero exit."),
     ("Does a failed process prove no side effects occurred?", "No", "Yes", "Only for copies", "Partial work may already have happened.")])

add(4, "3. Explicit working directory and environment",
    "Make a subprocess reproducible under a scheduler rather than a personal terminal.",
    [("cwd; env", "cwd chooses the child working folder. env provides its environment; passing one variable alone replaces the rest rather than automatically merging."),
     ("Environment inheritance", "Start from a deliberate environment policy. Copying os.environ preserves inherited values; sanitize or reduce it for a tool if appropriate. Never print the whole environment to diagnose secrets."),
     ("encoding and locale", "Captured output needs a known encoding. For a Python fixture use PYTHONIOENCODING=utf-8 and decode explicitly; other tools have their own output conventions.")],
    "The scheduler's current folder and locale may differ from your terminal. The following example creates an input file in a temporary folder, then starts a child with that explicit cwd. "
    "The child sees input.txt there and a fixture-specific environment option. It does not access your private account settings. "
    "Use distinct names for application variables, and never repurpose HOME or system configuration variables for task data. "
    "A full environment dump can expose credentials. Log only known harmless configuration such as a mode name or a count.",
    'env = {**os.environ, "JOB_MODE": "practice", "PYTHONIOENCODING": "utf-8"}\nsubprocess.run(command, cwd=practice_dir, env=env, encoding="utf-8", ...)',
    '''
    import os, subprocess, sys, tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as name:
        folder = Path(name)
        (folder / "input.txt").write_text("日本語", encoding="utf-8")
        code = "import os; from pathlib import Path; print(os.environ['JOB_MODE']); print(Path('input.txt').read_text(encoding='utf-8'))"
        env = {**os.environ, "JOB_MODE": "practice", "PYTHONIOENCODING": "utf-8"}
        result = subprocess.run([sys.executable, "-c", code], cwd=folder, env=env,
                                capture_output=True, text=True, encoding="utf-8", check=True, timeout=5)
        print(result.stdout.strip())
    ''',
    "cwd temporaryfolder भएकाले input.txt त्यहीबाटपढिन्छ। UTF8text ठीकdecodeभयो। "
    "EnvironmentकोJOB_MODEमात्रprintगरिएकोछ, सम्पूर्णenvironment वाsecret होइन।",
    ('env={"JOB_MODE": "practice"}  # assume all other values remain', 'Choose whether to inherit/merge an environment or provide a complete controlled one',
     "Supplying env replaces the child's environment mapping."),
    "Show that an explicit cwd controls a child relative-file lookup.",
    '''
    import subprocess, sys, tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as name:
        (Path(name) / "marker.txt").write_text("owned fixture", encoding="utf-8")
        result = subprocess.run([sys.executable, "-c", "from pathlib import Path; print(Path('marker.txt').is_file())"],
                                cwd=name, capture_output=True, text=True, check=True, timeout=5)
        print(result.stdout.strip())
    ''',
    "Prepare a narrow harmless environment and list only its keys, not private inherited values.",
    '''
    values = {"JOB_MODE": "practice", "PYTHONIOENCODING": "utf-8"}
    print(sorted(values))
    ''',
    "Define cwd, interpreter and encoding. Treat environment inheritance as a policy and keep private values out of logs.",
    [("Does env automatically merge with the parent when you pass a mapping?", "No", "Yes", "Only on Windows", "The passed mapping supplies the child's environment."),
     ("Should debugging print every environment variable?", "No", "Yes", "Only overnight", "Environment values can include credentials.")])

HASH = '''
import hashlib
from pathlib import Path
import shutil
import tempfile

def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()
'''

add(4, "4. Verify a backup's content, not just command success",
    "Compare source and destination bytes and distinguish copying from a recoverable backup.",
    [("shutil.copy2; SHA-256 digest", "copy2 copies a file and attempts metadata preservation. SHA-256 gives a content digest for comparison; it does not encrypt the backup."),
     ("Restore test", "A backup is useful only if it can be read and restored to an intended separate location. Do not test restoration by overwriting the original."),
     ("Live-source consistency", "Files can change while a backup runs. A consistent snapshot or change detection is needed; a digest taken only before a copy is not proof of the final copied content.")],
    "If Python can copy a file directly, do not invent a shell command just for the sake of subprocess. For a system utility, use the previous parts' status/timeouts and still verify the destination. "
    "The example copies one authored file to a new practice path and compares digests. It then deliberately changes the copy to show corruption detection. "
    "Backups also need metadata/scope/retention/restore policies; this part only proves one file's bytes. "
    "Never claim encryption because the filename contains a hash. Keep backups in a separate intended location and preserve the source during restore tests.",
    'copy selected file to a new destination\ncompare actual source/destination content digests\nrestore to a separate scratch folder and inspect',
    HASH + '''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    source, target = folder / "source.txt", folder / "copy.txt"
    source.write_text("Owned study notes", encoding="utf-8")
    shutil.copy2(source, target)
    print("Verified:", digest(source) == digest(target))
    target.write_text("Changed copy", encoding="utf-8")
    print("Verified after change:", digest(source) == digest(target))
''',
    "पहिलाdigestमेलखायो। Copyबदलेपछिफरकभयो। Copycommandsuccessभएपनि actualcontentजाँचचाहिन्छ। "
    "Restoretest sourceमाथिओभरwriteनगर; अर्कोscratchpathप्रयोगगर।",
    ('Command exit 0 -> backup is proven recoverable', 'Verify bytes and perform a separate restore/read test',
     "A successful command is not a full recovery test."),
    "Copy Japanese UTF-8 bytes and verify both content and digest.",
    HASH + '''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    source, target = folder / "a.txt", folder / "b.txt"
    source.write_text("日本語のノート", encoding="utf-8")
    shutil.copy2(source, target)
    print(target.read_text(encoding="utf-8"))
    print(digest(source) == digest(target))
''',
    "Use a separate restore path and confirm the original file remains unchanged.",
    HASH + '''
with tempfile.TemporaryDirectory() as name:
    folder = Path(name)
    source, backup, restored = [folder / n for n in ["source.txt", "backup.txt", "restored.txt"]]
    source.write_bytes(b"practice")
    shutil.copy2(source, backup)
    shutil.copy2(backup, restored)
    print(source.read_bytes() == restored.read_bytes())
    print(source.read_bytes())
''',
    "Verify actual bytes and practice recovery separately. Hashes detect content differences but do not encrypt data or make a live multi-file source consistent.",
    [("Does SHA-256 encrypt a copied file?", "No", "Yes", "Only in a ZIP", "It is a digest, not encryption."),
     ("Where should a restore test write?", "A separate scratch location", "Over the only original", "A credential file", "Preserve the original while testing recovery.")])

add(5, "1. Idempotency, dry-run and truthful logging",
    "Repeat work safely and make its effects inspectable before execution.",
    [("Idempotency", "Repeating the same valid operation leaves the intended state equivalent instead of duplicating effects. This must be designed; a retry flag alone does not provide it."),
     ("Dry-run boundary", "A dry-run can read and validate inputs, but it should not copy, delete, send or mutate job output/log state. Print the proposed plan instead."),
     ("logging.Logger; StreamHandler; levels", "Python logging records structured severity and context. Use INFO for progress and ERROR for failure; never log secrets or claim completed work before verification.")],
    "Suppose the scheduler starts the same backup twice. A content-addressed archive name plus verification can let the second run reuse the same valid artifact. "
    "Sending an email twice is not idempotent merely because the body matches; delivery is a different effect. "
    "For a dry-run compute the plan but return before output directory creation, lock files, persistent logs or alerts. "
    "Real runs should report planned, started, verified, completed/failed states honestly. This fixture logs to memory so you can inspect exact messages without changing your files.",
    'plan = validate_and_plan()\nif dry_run: print(plan); return 0\nperform -> verify -> record completed\non failure: record failure and return nonzero',
    '''
    import io, logging
    stream = io.StringIO()
    logger = logging.Logger("practice", level=logging.INFO)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.info("planned files=%s", 3)
    logger.error("failed: inspect local outcome report")
    print(stream.getvalue().strip())
    ''',
    "INFOplanहो, completedभएकोclaimहोइन। ERRORfailureअलगछ। Stream memoryमा भएकालेpersistentlogfileलेखिएकोछैन। "
    "Dryrunलेoutputfolder/create/log/alertकोsideeffectनगर्नुपर्छ।",
    ('Dry-run still sends a test notification and creates output files', 'Dry-run returns after validation/printed plan, before all effects',
     "A preview should not perform the very external/file effects it is previewing."),
    "Demonstrate idempotent set insertion versus non-idempotent list appending.",
    '''
    targets, events = set(), []
    for _ in range(2):
        targets.add("archive-A")
        events.append("email-A")
    print(len(targets), len(events))
    ''',
    "Verify a dry-run creates no output folder in a temporary practice directory.",
    '''
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as name:
        output = Path(name) / "output"
        dry_run = True
        if not dry_run:
            output.mkdir()
        print("Output exists:", output.exists())
    ''',
    "Design repeatability per effect. Dry-run is a real side-effect boundary, and logs must distinguish plans from verified completion.",
    [("Is sending the same email twice automatically idempotent?", "No", "Yes", "Only scheduled email", "Recipients can receive duplicate messages."),
     ("Should dry-run create a persistent output log?", "No in this course's contract", "Always", "Only with a flag", "The preview contract avoids output-state mutations.")])

add(5, "2. Prevent overlap with an owned lock and an explicit policy",
    "Reject a second concurrent run and clean up only the lock you acquired.",
    [("Exclusive create mode x", "Opening a file with mode x fails if it already exists. This supports a small cooperative lock among instances using the same local path."),
     ("Lock ownership; finally", "Only the process that successfully acquired the lock should remove it in finally. A second process must not delete another run's lock."),
     ("Stale lock", "A crash can leave a lock file behind. Inspect whether the job is still active before manual recovery; blindly deleting it can allow overlap. This simple local protocol is not a distributed lock.")],
    "Configure the scheduler not to start another instance, but also protect the finite job against accidental manual overlap. "
    "The fixture acquires a local lock with exclusive creation. A second acquisition fails and leaves the first intact. "
    "For this beginner project stale locks cause a visible stop; recover manually only after confirming no active run. "
    "Avoid 'check exists, then write' because two processes can both pass the check. More advanced operating-system locks and distributed coordination belong to later study.",
    'try: open(lock_path, "x")\nexcept FileExistsError: report overlap; stop\ntry: work\nfinally: remove only your acquired lock',
    '''
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as name:
        lock = Path(name) / "job.lock"
        with lock.open("x", encoding="utf-8") as stream:
            stream.write("fixture owner")
        try:
            with lock.open("x"):
                pass
        except FileExistsError:
            print("Second run blocked")
        print("Owner's lock intact:", lock.read_text(encoding="utf-8") == "fixture owner")
        lock.unlink()
        print("Released:", not lock.exists())
    ''',
    "Secondrunलेपहिलोlockहटाएकोछैन। आफ्नोownedlockमात्रfinallyमाreleaseगर। "
    "Crashकोstale lockभएरोकिन्छ; activejobछकिनैजाँचेरmanualrecoveryगर।",
    ('If lock exists: delete it and start anyway', 'Stop on an existing lock and inspect ownership/activity',
     "Deleting an active lock defeats overlap prevention."),
    "Verify finally releases an owned practice lock after a simulated operation failure.",
    '''
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as name:
        lock = Path(name) / "job.lock"
        lock.write_text("owned fixture", encoding="utf-8")
        try:
            raise ValueError("fixture failure")
        except ValueError:
            print("Operation failed")
        finally:
            lock.unlink()
        print(lock.exists())
    ''',
    "Demonstrate an unowned existing lock remains when a new run is refused.",
    '''
    from pathlib import Path
    import tempfile
    with tempfile.TemporaryDirectory() as name:
        lock = Path(name) / "job.lock"
        lock.write_text("other owner", encoding="utf-8")
        acquired = False
        try:
            lock.open("x").close()
            acquired = True
        except FileExistsError:
            pass
        finally:
            if acquired:
                lock.unlink()
        print(lock.read_text(encoding="utf-8"))
    ''',
    "Block overlap atomically, keep ownership explicit and release only owned locks. Treat stale locks as a visible recovery problem, not permission to overlap.",
    [("Should a refused second run delete the first run's lock?", "No", "Yes", "Only if small", "It does not own that lock."),
     ("Is this local file protocol a distributed lock guarantee?", "No", "Yes", "Only with JSON", "It is a small cooperative local design with documented limits.")])

PROJECT = clean(r'''
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
''')

SETUP = '''
import tempfile
def practice_source(root):
    source = root / "notes"
    source.mkdir()
    (source / "a.txt").write_text("Python practice", encoding="utf-8")
    (source / "b.txt").write_text("日本語のノート", encoding="utf-8")
    return source
'''

add(5, "3. Milestone: a verified repeatable backup job",
    "Combine a CLI, pure planning, a lock, verified archive, local logs and an outcome report.",
    [("Content-addressed backup", "The archive name is derived from the validated relative paths/sizes/content hashes. A repeated identical plan reuses only an archive whose contents verify."),
     ("zipfile; manifest; writestr", "zipfile creates/reads archives. A manifest states expected file paths, byte counts and hashes; writestr stores known bytes rather than invoking a shell."),
     ("Staging ownership; atomic publish", "Build a new archive to an exclusively owned temporary file, verify it, then publish. Never delete an unrelated stale temporary file or another process's lock."),
     ("Practice contract and consistency limit", "This project selects at most 200 ordinary files, 1 MB each/10 MB total. It detects many source changes, but it is not an operating-system atomic filesystem snapshot or a production backup suite.")],
    "Read the complete project by layers: read_small bounds input, plan_backup validates scope and computes a manifest, verify_archive reads every archive payload, and main controls effects. "
    "Default mode and --dry-run only print a plan. --apply explicitly creates the destination, acquires the lock and creates/reuses a verified ZIP. "
    "Source files are never deleted or replaced. The destination must be separate and non-nested. A symlink, empty source or oversized scope fails visibly. "
    "The local outcome.json is an alert report, not an email/push delivery. job.log records operation status/count; schedule this finite CLI using Day 2 after a manual test. "
    "The re-plan catches additions/removals/content changes during archive creation, but a live folder can still change between observations; use a quiet practice source or a proper filesystem snapshot for stronger consistency. "
    "Archives are unencrypted and byte-oriented: permissions, ACLs, empty folders, retention and automatic restoration are outside this small project's contract.",
    'validate + pure plan -> optional preview\nexclusive lock -> create/reuse -> verify\nrecord local outcome -> return status -> release owned resources',
    PROJECT + SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source, destination = practice_source(root), root / "backups"
    assert main([str(source), str(destination), "--dry-run"]) == 0
    print("Output before apply:", destination.exists())
    assert main([str(source), str(destination), "--apply"]) == 0
    assert main([str(source), str(destination), "--apply"]) == 0
    print("ZIP count:", len(list(destination.glob("*.zip"))))
    print("Outcome:", json.loads((destination / "outcome.json").read_text())["status"])
''',
    "Dryrunकोबेलadestinationबनएन। पहिलोapplyलेverifiedZIPबनायो, दोस्रोलेsamevalidZIPreuseगर्‍यो। "
    "Hash encryptionहोइन। Localoutcome notification transportहोइन। Realfolderlivechangingभएatomic snapshotजस्तोग्यारेन्टीछैन।",
    ('Archive exists -> silently claim verified success', 'Read and verify existing archive against the current manifest before reuse',
     "An existing path may contain a corrupt or unrelated archive."),
    "Read archived file bytes and verify the digest against the manifest without extracting over the source.",
    PROJECT + SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source, destination = practice_source(root), root / "backups"
    assert main([str(source), str(destination), "--apply"]) == 0
    _, _, manifest, _ = plan_backup(source, destination)
    target = next(destination.glob("*.zip"))
    print("Archive verified:", verify_archive(target, manifest))
    with zipfile.ZipFile(target) as archive:
        print(archive.read("files/b.txt").decode("utf-8"))
''',
    "Change an owned source file and verify the new content produces another verified archive without deleting the old one.",
    PROJECT + SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source, destination = practice_source(root), root / "backups"
    assert main([str(source), str(destination), "--apply"]) == 0
    (source / "a.txt").write_text("Updated practice", encoding="utf-8")
    assert main([str(source), str(destination), "--apply"]) == 0
    print("ZIP count:", len(list(destination.glob("*.zip"))))
''',
    "A trustworthy automation combines explicit effects, verified repeatability and honest outcomes. Understand the project's narrow contract before extending scheduling, delivery or backup scope.",
    [("What is the default project mode?", "Preview with no writes", "Delete source files", "Send an email", "Only explicit --apply performs output effects."),
     ("Is the archive automatically encrypted?", "No", "Yes", "Only with a hash name", "Hashes support integrity/identity, not encryption.")])

add(5, "4. Whole-week review: failed work must stay visible",
    "Prove dry-run, reuse, corruption detection, overlap refusal and source preservation.",
    [("Failure matrix", "Use separate tests for invalid CLI, missing input, nested paths, overlap, changed source and corrupt output. They exercise different contracts."),
     ("Outcome versus notification status", "An artifact may be created even if saving its log/outcome later fails. Return failure honestly, retain the verified artifact, and let a repeat verify/reuse it."),
     ("Recovery policy", "Inspect errors and stale locks/staging files before manual recovery. Do not delete unrelated output just to make the next run green.")],
    "Review by explaining every effect before running it. Why does a dry-run return before destination creation? Why must the second process not delete the lock? "
    "Why can subprocess output exist even when the status is nonzero? Why is mocked SMTP acceptance not proof of real delivery? "
    "The exercise below verifies source bytes remain identical after a backup. The accompanying project test file also checks corrupt archives, overlap and output-preservation failures. "
    "For a restore exercise read an archive payload into a separate scratch folder and compare its hash; never overwrite the only original. "
    "Do not mark the week mastered until you can run the CLI manually, inspect status/log/outcome, explain its limitations and configure a daily dry-run task on your own practice system.",
    'test happy path + no-write preview + repeat + corruption + overlap\nassert source bytes unchanged\nassert nonzero failure and truthful local evidence',
    PROJECT + SETUP + '''
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source, destination = practice_source(root), root / "backups"
    before = {p.name: p.read_bytes() for p in source.iterdir()}
    assert main([str(source), str(destination), "--apply"]) == 0
    after = {p.name: p.read_bytes() for p in source.iterdir()}
    print("Source unchanged:", before == after)
    print("Lock released:", not (destination / "job.lock").exists())
''',
    "Backupपछिsourcebytesसुरक्षित छन्। Ownedlockreleaseभयो। Successमात्रनहेरीfailurecasesपनिverifyगर। "
    "अर्कोstep आफ्नोpracticecomputerमादaily dryrun scheduleगर्नेहो; योwebsiteलेतिम्रोOSमातास्कregisterगरेकोछैन।",
    ('Test only a happy-path printout', 'Test distinct failures and verify original/input/output state',
     "A successful print does not prove dry-run, overlap or recovery contracts."),
    "Verify a nested destination is rejected before it is created.",
    PROJECT + SETUP + '''
import contextlib, io
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source = practice_source(root)
    destination = source / "backups"
    with contextlib.redirect_stderr(io.StringIO()):
        status = main([str(source), str(destination), "--apply"])
    print("Status:", status, "Nested output exists:", destination.exists())
''',
    "Keep another run's lock intact when an apply request is refused.",
    PROJECT + SETUP + '''
import contextlib, io
with tempfile.TemporaryDirectory() as name:
    root = Path(name)
    source, destination = practice_source(root), root / "backups"
    destination.mkdir()
    lock = destination / "job.lock"
    lock.write_text("other-owner", encoding="utf-8")
    with contextlib.redirect_stderr(io.StringIO()):
        status = main([str(source), str(destination), "--apply"])
    print("Status:", status)
    print("Other lock:", lock.read_text(encoding="utf-8"))
''',
    "Week 26 mastery: clear CLIs, explicit scheduled environments, private transport configuration, cautious GUI context, checked child processes and verified repeatable jobs with truthful failure outcomes.",
    [
        ("What should argparse flags use for presence-based True?", "store_true", "type=bool", "A string password", "Nonempty string conversion does not parse false reliably."),
        ("What indicates a failed finite job?", "A nonzero exit status", "Always zero", "Only a smiley", "Schedulers need machine-readable failure."),
        ("Does schedule keep running after Python exits?", "No", "Yes", "Only hourly jobs", "It is an in-process scheduler."),
        ("Does a Task Scheduler trigger prove work completion?", "No", "Yes", "Only daily jobs", "Inspect the job's status and outcome."),
        ("Does composing EmailMessage deliver it?", "No", "Yes", "Only with a subject", "Composition and transport are separate."),
        ("Does SMTP server acceptance guarantee inbox delivery?", "No", "Yes", "Only under TLS", "Further delivery/bounce/filtering outcomes are possible."),
        ("Should a failed image match trigger a fallback click?", "No", "Yes", "Only at zero", "An unverified target is a stop."),
        ("Does shell=False remove every program-level risk?", "No", "Yes", "Only for arguments", "The executable's own options/input still need validation."),
        ("Can a failed child process have partial side effects?", "Yes", "No", "Only on Linux", "Failure does not imply no work occurred."),
        ("Should dry-run mutate persistent output state?", "No under this contract", "Always", "Only output logs", "A pure preview returns before effects."),
        ("Should a blocked second run remove the owner's lock?", "No", "Yes", "Only when small", "Lock ownership is explicit."),
        ("Does the backup hash encrypt its contents?", "No", "Yes", "Only in ZIP", "Integrity/identity and encryption are different."),
    ])

DAYS["26.0"]["parts"][3]["sections"].insert(3, s("sh", "python -m pip install click",
    note="Argparse requires no install. Click is optional for that part's runnable tests. Install once in a practice environment."))
DAYS["26.1"]["parts"][3]["sections"].insert(3, s("sh", "python -m pip install schedule",
    note="Install once. Forced run_all examples do not wait for a real trigger or register an OS task."))
DAYS["26.3"]["parts"][0]["sections"].insert(3, s("sh", "python -m pip install pyautogui pillow",
    note="For a deliberate real scratch-window exercise only. Runnable website examples use FakeDesktop; Pillow image examples create authored images instead of screenshots."))
DAYS["26.5"]["parts"][2]["sections"].append(s("sh",
    'python backup_job.py "practice-notes" "practice-backups" --dry-run\npython backup_job.py "practice-notes" "practice-backups" --apply\npython backup_job.py --help',
    note="Copy the standalone project and sample practice-notes folder into a practice directory. --apply creates only the separate backup destination; source files remain intact."))
DAYS["26.5"]["parts"][-1]["sections"].append(s("p",
    "Primary references: https://docs.python.org/3/library/argparse.html · https://click.palletsprojects.com/en/stable/ · "
    "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks-create · https://schedule.readthedocs.io/en/stable/ · "
    "https://docs.python.org/3/library/email.examples.html · https://docs.python.org/3/library/smtplib.html · "
    "https://pyautogui.readthedocs.io/en/latest/ · https://docs.python.org/3/library/subprocess.html · https://docs.python.org/3/library/logging.html. "
    "All authored explanations, fixtures, worked examples, outputs, questions and solutions are included for offline study."))


def write():
    target = ROOT / "study-hub.html"
    original = target.read_bytes().decode("utf-8")
    start = original.index("const DAY_TEACH = {")
    end = original.index("\n};\n\nconst REST_DAY", start)
    if any(('"' + key + '":') in original[start:end] for key in DAYS):
        raise RuntimeError("Week 26 exists; refusing to overwrite.")
    addition = "\n".join(json.dumps(k) + ": " + json.dumps(v, ensure_ascii=False, indent=2) + "," for k, v in DAYS.items())
    addition = addition.replace("</", "<\\/")
    prefix = original[:end].rstrip()
    if not prefix.endswith(","):
        prefix += ","
    temporary = target.with_suffix(".html.tmp")
    temporary.write_bytes((prefix + "\n" + addition + original[end:]).encode("utf-8"))
    temporary.replace(target)
    project_root = ROOT / "docs" / "python-week26"
    project_root.mkdir(exist_ok=True)
    (project_root / "backup_job.py").write_text(
        '"""Week26 small-file backup practice. Python3.11+. No external services or GUI."""\n'
        + PROJECT + '\nif __name__ == "__main__":\n    sys.exit(main())\n', encoding="utf-8")
    sample = project_root / "practice-notes"
    sample.mkdir(exist_ok=True)
    (sample / "python.txt").write_text("Python automation practice\n", encoding="utf-8")
    (sample / "japanese.txt").write_text("日本語の練習\n", encoding="utf-8")
    parts = [part for day in DAYS.values() for part in day["parts"]]
    quizzes = sum(len(section["lesson"]["quiz"]) for part in parts for section in part["sections"] if section["t"] == "checkpoint")
    print(f"Added Week26: 6 days, {len(parts)} parts, {len(parts)*2} practice prompts, {quizzes} questions, {EXECUTED} verified outputs.")


if __name__ == "__main__":
    write()


