# Cybersecurity Week 7 — Monitoring, incidents and evidence

Seven English lessons,36 reasoned checks, first-use explanations and a prepared
fictional log case. Existing day notes, answer reveal, navigation and app storage
are reused. The42 earlier cybersecurity lessons and other courses are retained.

## Study sequence

1. Monitoring: event/log/alert/incident units, SOC/SIEM, detection windows,
   accountable review and collection health.
2. Context: behaviour baseline, false positive/negative, login/application/
   endpoint/network sources, source trust, account versus person, correlation
   references and alternative explanations.
3. Chronology: raw and normalised timestamps, UTC/offsets, event versus receipt,
   clock/precision limits, duplicate and late delivery, cutoff and unknown time.
4. Triage: supported facts versus hypotheses, scope/impact/urgency, escalation,
   authorised containment trade-offs, concise communication and Python's role in
   sorting/correlating approved evidence.
5. Recovery/evidence: raw versus working views, provenance/handling records,
   exact-byte digests and their limitations, recovery verification, collection
   health and accountable after-action improvements.
6. Worked case: read12 supplied records, reconcile different cutoffs, derive
   counts/timeline, retain unresolved evidence and write a bounded summary.
7. Closed-notes review: four-part case package and twelve questions/answers
   connecting the whole week to verification and improvement.

Python is described as a supporting tool. No extra Python coding worksheet,
external target test, account access or live incident collection is added.

## Prepared handouts

Week7 Day6 references link to these files. They are optional: essential records,
explanations and worked answers are also embedded in study-hub.html. For offline
handouts, keep this directory with the downloaded project folder.

- sample-events.json: original fictional delivery records and context.
- case-notes.txt: portable raw-record list, assumptions and paper exercises.
- digest-manifest.json: SHA-256 references and byte sizes for the two files.

The dates are explicitly fictional. IPs use documentation ranges; accounts and
correlation label C-7 are made up. C-7 is not a credential. There are no actual
passwords, replayable session values, private note bodies or real device logs.

## Ground truth and limits

-12 collector deliveries describe11 distinct source events.
- Event identity is source + event_id; L04 repeats auth A03 from L03.
- Ten distinct events carry explicit offsets. Their clocks are assumed correct
  for this worksheet only. A real incident needs source-clock verification.
- X01's event timezone is undocumented and stays outside UTC event ordering.
  Its known receipt instant does not recover its event instant.
- Known event order: A01,A02,A04,A03,A10,N01,P01,P02,E01,Z01.
- In [00:00,00:03) UTC, four unique failed logins are A01,A02,A04,A03; the raw
  deliveries contain five failure records because A03 was repeated.
- Z01's00:07 alert saw A01,A02,A03. Late A04 arrived at00:08:30, the final cutoff.
  The alert is not another underlying failed-login event.
- P01 reports a refused N2 edit/no write; P02 reports a persisted N1 edit. Those
  are application log claims. Relevant independent state evidence would
  strengthen a verified write/no-write conclusion.
- An accepted account event and shared reference do not prove a human actor,
  takeover, data exfiltration or a successful unauthorised N2 change.
- A stale class job is a hypothesis, not verified cause. User/job confirmation,
  relevant state/history and logging reliability are not supplied.
- Endpoint heartbeat and network allow data have limited source-specific meaning.
- No containment, credential change, reboot or cleanup actually occurred.

Use raw references in the paper case. A working deduplicated timeline does not
replace preserved deliveries. Proposed actions must be labelled proposed and
assigned to appropriate fictional owners under the response plan.

## Integrity references

The manifest compares exact UTF-8 bytes, including final newline and formatting.
It is a reference for this teaching package, not a signed origin claim, a proof
of event truth, complete coverage, human attribution or legal forensic sufficiency.
Downloading through an altered representation or changing line endings can
produce a different byte digest even if parsed JSON values remain identical.
Preserve the raw representation and analyse a working copy.

## References

- [NIST response guidance, revision3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [OWASP protected logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Microsoft SIEM source/correlation overview](https://learn.microsoft.com/en-us/azure/sentinel/overview)
- [Python aware/naive datetime meaning](https://docs.python.org/3/library/datetime.html)
- [NIST forensic techniques/provenance](https://csrc.nist.gov/pubs/sp/800/86/final)
- [Python exact-byte hashing](https://docs.python.org/3/library/hashlib.html)

Explanations, records and case exercises are original. The simplified classroom
workflow is not presented as a rigid official phase sequence. Real response and
evidence handling follow the applicable authorised process and qualified advice.

## Verification

Static checks compare all earlier cybersecurity lessons and every byte of
application/storage/other-course code outside the teaching map against c1cf3f0.
Prepared-data tests verify offsets, duplicate identity, known/unknown event
order, raw/unique failure counts, collection cutoffs and actual manifest digests.
Isolated browser tests use fictional progress for all seven views,36 answer
show/hide checks, note saving/hiding/refresh, week boundaries, previous quizzes,
375px themes and console errors. Actual backup/import merge-and-replace tests
use a separate fictional profile; real user data/credentials are not accessed.
