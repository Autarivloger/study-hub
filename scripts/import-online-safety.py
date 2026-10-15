"""Extract the supplied lesson transcript; repeated scheduling prompts are not app commands."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path(sys.argv[1]).read_text(encoding="utf-8-sig")


def sections(text):
    text = re.sub(r"^Progress:.*(?:\n|$)", "", text, flags=re.M)
    headings = {"Small variations are predictable.", "What a normal password change looks like",
        "Common mistakes, explained simply", "Protect the vault’s entrance", "Understand what unlocking means",
        "Let the manager help you check the website", "Plan recovery before you need it",
        "Use a careful save-and-confirm routine", "Recognize the common methods", "A code is a temporary key",
        "Unexpected approval requests deserve a pause", "Prepare for a lost phone",
        "Why passkeys help against fake websites", "Where your passkey lives matters",
        "What happens if you lose your phone?", "Only create passkeys on devices you control",
        "Look at the requested action", "Use a route the message didn’t supply",
        "Appearance provides clues, not proof", "If you already clicked, respond to what happened",
        "“It works fine” doesn’t mean it’s secure", "Several parts of your device need updates",
        "Treat unexpected update prompts like other unexpected requests", "Make updates manageable",
        "Support eventually ends"}
    result = []
    for paragraph in re.split(r"\n\s*\n", text.strip()):
        if "\t" in paragraph:
            for line in paragraph.splitlines():
                cells = line.split("\t")
                result.append({"t": "p", "v": " — ".join(cells)})
        else:
            result.append({"t": "h" if paragraph in headings else "p", "v": paragraph})
    return result


lessons = [{
    "number": 1, "title": "Email and account safety: protect your reset hub", "origin": "Added introduction",
    "objective": "Explain why your main email matters and choose a trusted route to an account’s security settings.",
    "sections": [
        {"t": "h", "v": "Review · 2 minutes"},
        {"t": "p", "v": "This is the starting lesson. Your supplied transcript begins at Lesson 2 and refers back to email safety, so this introduction fills that gap. There is no earlier exercise to report. Read the goal and think about the accounts you use, without listing passwords or private account details here."},
        {"t": "h", "v": "Learn · 10 minutes"},
        {"t": "p", "v": "An account is your identity inside a service: email, shopping, social media or a learning platform. Signing in proves that you may use that account. Account security means reducing unwanted access and knowing how to regain control when something goes wrong."},
        {"t": "h", "v": "Why your inbox is a useful starting point"},
        {"t": "p", "v": "Many services send password-reset links or security notices to your email. Someone who controls that inbox may be able to reset connected accounts, although recovery rules differ by service. Think of your main inbox as a hub with several paths leading to it. Protecting the hub helps protect the connected accounts."},
        {"t": "p", "v": "For example, Mira uses an email address for shopping and a photo service. The photo service sends a reset link to that inbox. Mira should protect both accounts, but her inbox deserves early attention because it receives recovery messages. This does not mean every account can always be recovered through email."},
        {"t": "h", "v": "Use a route you opened yourself"},
        {"t": "p", "v": "If an unexpected message says your account is at risk, pause before using its button, QR code or phone number. Open the usual app or a known website address independently and find account security there. A familiar logo or urgent deadline is not proof of who sent the message."},
        {"t": "h", "v": "Build layers gradually"},
        {"t": "p", "v": "A unique password limits damage from reuse. A password manager can help store independent passwords. Additional sign-in checks and passkeys provide other protections where supported. Recovery planning helps when a device or credential becomes unavailable. The next lessons explain these one at a time; you do not need to change settings today."},
        {"t": "h", "v": "Common mistakes, explained simply"},
        {"t": "p", "v": "“I never send important messages, so my email does not matter.” Your inbox may still receive reset messages for important services.\n“A security message must be genuine because it knows my name.” Names and logos can be copied. Reach the service independently.\n“I must share a code to prove I am learning.” Never put passwords, one-time codes, recovery keys or sensitive account details in lesson notes or chat."},
    ],
    "exerciseTitle": "One exercise: map a fictional reset hub · 5 minutes",
    "exercise": [{"t": "p", "v": "Mira’s shopping account and photo account both send password-reset emails to her main inbox. A text message now claims the inbox will be closed unless she follows its sign-in link. Write a short answer explaining which account deserves early protection, why the other accounts depend on it, and how she could check the warning safely. Use only this fictional situation; no real sign-in, settings change or account information is needed."}],
    "selfCheck": [{"t": "p", "v": "A successful answer identifies the main inbox as an early priority because it receives recovery messages, explains the connection to the shopping/photo accounts, and says Mira should open her usual email app or a known website independently rather than use the text’s link. If you chose to trust the message because it sounded urgent, revise that step: urgency is a reason to pause, not proof of identity."}],
    "recap": [{"t": "p", "v": "Your main inbox can connect to recovery for other accounts.\nReach security settings through an app or website you opened independently.\nBuild protections step by step and keep credentials out of learning notes."}],
    "next": "Next lesson: Unique passwords—protect one account at a time."
}]

for match in re.finditer(r"^Lesson (\d+) — (.+)$", SOURCE, re.M):
    number = int(match[1]); start = match.end()
    ending = re.search(r"^Next lesson:.*$", SOURCE[start:], re.M)
    if ending is None:
        raise ValueError("Missing lesson ending")
    block = SOURCE[start:start+ending.end()].strip()
    goal = re.search(r"^Today’s goal: (.+)$", block, re.M)
    review = block.index("Review · 2 minutes")
    learn = block.index("Learn · 10 minutes")
    exercise = block.index("One exercise:")
    answer = block.index("Self-check and feedback · 3 minutes")
    recap = block.index("Recap — Lesson ")
    next_pos = block.index("Next lesson:")
    ex_title, ex_body = block[exercise:answer].split("\n", 1)
    recap_body = block[recap:next_pos].split("\n", 1)[1]
    lessons.append({"number": number, "title": match[2].strip(), "origin": "From your supplied transcript",
        "objective": goal[1].strip(),
        "sections": [{"t":"h","v":"Review · 2 minutes"}, *sections(block[review+len('Review · 2 minutes'):learn]),
                     {"t":"h","v":"Learn · 10 minutes"}, *sections(block[learn+len('Learn · 10 minutes'):exercise])],
        "exerciseTitle":ex_title.strip(), "exercise":sections(ex_body),
        "selfCheck":sections(block[answer+len('Self-check and feedback · 3 minutes'):recap]),
        "recap":sections(recap_body), "next":block[next_pos:].strip()})

assert [l["number"] for l in lessons] == list(range(1,8))
(ROOT/"scripts"/"cybersecurity-online-safety-content.json").write_text(json.dumps(lessons,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("Prepared seven lessons: added introduction 1; supplied lessons 2–7 preserved. Scheduling/chat wrapper excluded.")
