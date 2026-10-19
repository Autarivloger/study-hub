// Original English teaching. Python supports a security question in every day.
const s=(t,v,extra={})=>({t,v,...extra});
const h=v=>s('h',v),p=v=>s('p',v),term=(v,note)=>s('new',v,{note});
const check=(q,a,why)=>({q,a,why});
const refs=[
 {title:'Python: JSON input and size limits',url:'https://docs.python.org/3/library/json.html'},
 {title:'Python: aware timestamps',url:'https://docs.python.org/3/library/datetime.html'},
 {title:'OWASP: logging, sensitive data and interpretation',url:'https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html'},
 {title:'Week 9 lab setup and helper explanations',url:'docs/cybersecurity-week9/README.md'}
];
function lesson(objective,sections,checks,reflection){return {objective,sections,checks,reflection,references:refs};}
function example(code){return [s('code',code.trim()),s('out','')];}
function exercise(task,code,why){return [s('ex',task),{t:'sol',code:code.trim(),out:'',why}];}
module.exports={
 '9.1':lesson(
 'Set up a read-only Python evidence lab, state one investigation question and distinguish a delivered record from a verified real-world event.',[
 h('Part 1 · Start with the security question'),
 p('Weeks 1–8 established accounts, networks, controls and evidence. Now Python will help you repeat careful analysis. The question for this week is: how many distinct failed-login events does the prepared source report in a stated interval, and what needs review? Answering that question requires defining the source, identity rule, time interval and collection cutoff. A large number printed by a script is useful only when you can explain what was counted.'),
 term('Evidence pipeline','A sequence of explicit transformations: read original input → validate records → reconcile identities → normalise known times → count a defined behaviour → explain results and limitations. Each stage preserves references back to the source.'),
 p('The supplied case is the same fictional Week 7 dataset. It contains 12 deliveries from authentication, application, network, endpoint, alert and legacy-export sources. Documentation IP addresses are public teaching values, not systems to contact. C-7 is a non-secret correlation label. Nothing here establishes an observation about your computer or your accounts. The script reads the supplied file; it does not discover devices, retrieve account logs or change settings.'),
 h('Part 2 · Prepare a small working folder'),
 term('pathlib.Path and the supplied security_lab module','Path represents filesystem paths. The original helper module security_lab.py sits beside the fixture and defines small analysis functions. SAMPLE is the fixture path relative to that module, so the program does not search your computer for logs.'),
 p('Download the repository and open docs/cybersecurity-week9 in PowerShell. Python 3.12 or later is sufficient; all imports use the standard library. Save each complete lesson snippet into practice.py in this folder, then run python practice.py. Do not overwrite security_lab.py or call your file json.py. The website shows recorded example output; Python runs locally in your own terminal. Reading the lessons remains available offline.'),
 s('sh','python --version\npython -m unittest -v\npython security_lab.py'),
 p('Run these as separate commands. The first checks your interpreter, the second runs the supplied tests, and the third prints the worked report. A test run checks specific expected behaviours; it does not certify a whole computer as secure. There is no package installation step or API credential. Read README.md before changing the lab, and keep the reference fixture unchanged so that later comparisons have a stable starting point.'),
 h('Part 3 · Inspect before interpreting'),
 term('load_fixture() and JSON document shape','load_fixture reads a bounded UTF-8 JSON document and checks its top-level structure. JSON objects become Python dictionaries and arrays become lists. This helper returns events plus context; it does not authenticate the source or prove every row is valid.'),
 ...example(`from security_lab import load_fixture
document = load_fixture()
print('Deliveries:', len(document['events']))
print('First reference:', document['events'][0]['record'])
print('Scope:', document['context']['scope'])`),
 p('Read the expressions from the inside outward. document["events"] retrieves the delivery list; len counts its entries; [0] selects the first delivery; ["record"] retrieves the collector reference. The value L01 lets you return to that row. It is not the same thing as event_id A01, which belongs to the source event. Keeping both references will explain why L03 and L04 can describe one source event without becoming one identical delivery.'),
 h('Part 4 · Keep the originals and state limits'),
 p('Write your question, input filename and assumptions before analysing. The worksheet assumes offset-bearing clocks are correct for this exercise. X01 lacks a documented timezone. A log is a source report with a particular collection history; an accepted-login label does not independently prove which human used an account. Read the context limitations and keep them with your result. A script should make these uncertainties visible rather than replace them with confident guesses.'),
 ...exercise('Practice: count delivered authentication rows before deduplication. Explain the unit in your answer.',`from security_lab import load_fixture
rows = load_fixture()['events']
print('Authentication deliveries:', sum(row['source'] == 'auth' for row in rows))
print('Unit: deliveries, not unique events')`,'Each True contributes one to sum. The source filter is explicit, but a repeated delivery still counts until Day 3 reconciles event identities.'),
 h('Part 5 · A defensible first observation'),
 p('Keep three sentences separate: what the input contains, what your code calculated, and what the result means for the question. At this stage you know the delivered record count and can locate a reference. You have not yet excluded malformed rows, reconciled duplicates or resolved time. Finish this stage before introducing a threshold. You can take several study sessions for one labelled day; understanding each transformation is more important than reaching the next button.'),
 ...exercise('Mini challenge: list the source labels in a stable order without printing full records.',`from security_lab import load_fixture
sources = {row['source'] for row in load_fixture()['events']}
print(', '.join(sorted(sources)))`,'A set removes repeated labels. sorted makes the presentation reproducible. This summarises categories rather than exposing every field.'),
 s('key','Security question first; explicit input, reference and counting unit second; interpretation only after the required checks.')
 ],[
 check('What is Python helping investigate this week?','Distinct reported failed-login events in a stated interval, with evidence references and limitations.','The question determines the filters and counting unit.'),
 check('Does 12 deliveries prove 12 independent events?','No. One source event can be delivered more than once.','Delivery identity and source-event identity are different.'),
 check('Does the website execute these Python snippets?','No. It displays recorded output; run practice.py locally in the supplied folder.','A rendered code block is not an interpreter.'),
 check('Why keep the context object?','It records the fictional scope and interpretation limitations.','Data without provenance can support misleading conclusions.'),
 check('Should the script contact a displayed documentation IP?','No. The analysis only reads prepared local evidence.','An address inside a record is data, not an instruction.'),
 check('Why keep the reference fixture unchanged?','It provides a stable input for checks and later comparisons.','Make changes in a separate practice copy.')
 ],'Write the investigation question, counting unit, reference filename and two limits. Record your own terminal result without copying any real account data.'),
 '9.2':lesson(
 'Reject malformed inputs explicitly, distinguish structural validation from trust, and keep rejected-row references beside accepted records.',[
 h('Part 1 · Parsing is only the first boundary'),
 p('Yesterday you read the prepared file. Today consider a record with status "403" as text, a missing source or a boolean status True. A JSON parser can accept all those values because they are legal JSON types. Your analysis still needs a contract for what each field means. If you count before checking, missing values may crash the script, or a convenient conversion may silently transform a bad observation into an apparently valid one.'),
 term('Schema and validation','A schema is a stated shape/type contract. Validation checks an input against that contract. It can establish that a status is an integer in the expected range; it cannot establish that a real service actually returned that status.'),
 p('The lab requires nonblank strings for record, source, event_id, event_time, received_time and action. It checks their length and control characters. Present status values must be actual integers from 100 to 599; present write_performed values must be booleans. An account label, if present, must be bounded text. Unknown metadata remains present. Dates are handled separately: a nonblank event_time can still be invalid or offset-free and will be reported as unknown on Day 4.'),
 h('Part 2 · Bound the document before analysis'),
 term('Input budget and strict JSON decoding','The loader reads at most 100,001 bytes, rejecting files above 100,000 bytes and more than 1,000 deliveries. It also rejects duplicate JSON object keys and NaN/Infinity. These deliberate limits make this small fixture lab easier to reason about.'),
 p('An ordinary dictionary cannot retain two different values for the same key after the later value replaces the earlier one. The helper therefore uses object_pairs_hook to inspect key/value pairs before building each object. parse_constant rejects Python decoder extensions for non-finite numbers. You do not need to memorise these callbacks today; find their short definitions in security_lab.py and explain why the boundary rejects ambiguity instead of guessing which value the source intended.'),
 p('A byte budget is useful but is not a complete untrusted-document service. Extreme nesting and a hostile collection environment require additional design. This course lab uses a small supplied fixture; it is not a request to load arbitrary downloads into a privileged program. The lesson is to match a boundary to an explicit workload and record what it does not guarantee. Unknown input is not automatically trustworthy just because the file extension is .json.'),
 h('Part 3 · Accept, reject and preserve the reference'),
 term('validate_rows(rows)','This supplied pure helper returns two lists: accepted copies and errors containing a one-based row number plus reason. It does not edit the original records or repair rejected values. Tuple unpacking assigns the two returned lists to two names.'),
 ...example(`from security_lab import load_fixture, validate_rows
accepted, rejected = validate_rows(load_fixture()['events'])
print('Accepted:', len(accepted))
print('Rejected:', len(rejected))`),
 p('The clean reference fixture has no rejected rows. That does not make it a complete incident history. It means the rows passed this contract. For a bad file, keep the input count, accepted count and rejected count visible. Otherwise a report may say only two failures when the missing third observation was discarded by a parser. Never make an error count disappear merely because the remaining records are easier to analyse.'),
 h('Part 4 · Avoid helpful-looking coercion'),
 term('type(value) is int versus isinstance(value, int)','In Python bool is a subclass of int, so isinstance(True, int) is True. The status boundary deliberately requires type(value) is int to reject a boolean masquerading as an HTTP status.'),
 ...exercise('Practice: add a clearly invalid copy in memory and show its rejected-row reason. Leave the fixture file alone.',`from security_lab import load_fixture, validate_rows
row = load_fixture()['events'][0]
bad = {**row, 'record': 'TEST', 'status': True}
accepted, rejected = validate_rows([bad])
print('Accepted:', len(accepted))
print('Rejected row:', rejected[0]['row'])
print('Reason:', rejected[0]['reason'])`,'Dictionary unpacking creates a new top-level object. Strict type checking stops True from being interpreted as status 1 or accepted as a valid integer status.'),
 p('Do not fix an invalid status with int(value) inside the validator. That would accept some strings and lose the difference between a source contract violation and a valid observation. A documented normalisation stage can be appropriate for another source, but it must preserve what changed and why. In this lab rejection is the intentional behaviour, and later results must disclose any rejected observations.'),
 h('Part 5 · Validate failure cases, not only the happy path'),
 ...exercise('Mini challenge: demonstrate a missing required field and verify that the original delivery still has it.',`from security_lab import load_fixture, validate_rows
original = load_fixture()['events'][0]
copy = {key: value for key, value in original.items() if key != 'source'}
accepted, rejected = validate_rows([copy])
print('Rejected:', len(rejected))
print('Original source:', original['source'])`,'The comprehension creates a separate object. A meaningful rejection test also checks that analysis did not damage its reference input.'),
 p('Use the supplied unit tests to inspect malformed objects, repeated delivery labels, unexpected types and loader limits. A good test names an expected failure, not merely that the program ran. Keep your day note focused on the contract and observed behaviour. If you cannot explain why an input was accepted or rejected, pause before using its count as evidence for a security finding.'),
 s('key','Valid shape is not verified truth. Keep rejection evidence visible and preserve the unmodified input.')
 ],[
 check('Does successful JSON parsing establish valid record types?','No. Parsing and application validation are separate boundaries.','Legal JSON can violate the analysis contract.'),
 check('Why reject status True?','A boolean is not an HTTP status even though bool subclasses int in Python.','The contract requires an actual integer from 100 to 599.'),
 check('Should invalid rows vanish from the report?','No. Retain their row references and reasons.','Missing evidence can change how a count should be interpreted.'),
 check('Does a valid event_time string establish a known UTC time?','No. It can still lack an offset or contain an invalid date.','Time semantics are checked separately.'),
 check('Why reject duplicate JSON object keys?','They make the intended value ambiguous and ordinary decoding can overwrite a value.','Detect ambiguity before building the dictionary.'),
 check('Does the small input budget make this a general hostile-file sandbox?','No. It is a bounded teaching loader with stated limits.','Match guarantees to the workload actually implemented.')
 ],'Describe one accepted row, one rejected row and why validation cannot prove authenticity. Explain how you checked that the reference data stayed unchanged.'),
 '9.3':lesson(
 'Count source events once using their documented identity and quarantine conflicting copies instead of choosing a convenient version.',[
 h('Part 1 · Separate three different quantities'),
 p('A collector receives deliveries. A source produces events. An alert describes a rule result over some events. Those three quantities are not interchangeable. The reference case has 12 deliveries and 11 source events. L03 and L04 both carry authentication event A03. Alert Z01 describes an earlier threshold calculation; counting that alert as another failed login would count an analytical conclusion as if it were another underlying occurrence.'),
 term('Composite event identity','In this worksheet the pair (source, event_id) identifies a source event. A tuple can be a dictionary key because its text elements are hashable. event_id alone is insufficient when different sources can reuse the same label.'),
 p('Identity is a contract, not something to invent from whichever fields happen to match. Some systems identify events using an extra tenant or device key, or reuse IDs after a restart. Learn the source contract before extending the method. In this prepared fixture the source-plus-ID rule is explicitly documented, and it permits authentication A03 to stay separate from an unrelated source that happens to use A03 too.'),
 h('Part 2 · Compare the event payload'),
 term('Delivery metadata versus event payload','record, received_time and annotation describe the delivery in this fixture. The remaining fields describe its event payload. Equal payload copies with the same event identity count once. A different payload under the same identity is a conflict requiring review.'),
 p('L03 and L04 have different collector labels and receipt times. Their event payload agrees, so the retained source event can point to L03 while a duplicate note points from L04 to L03. We do not delete either original. Do not generalise the exclusion of annotation to every system: here it is a collector note. If another source uses that field as event evidence, excluding it would hide a relevant difference.'),
 h('Part 3 · Reconcile the prepared evidence'),
 term('deduplicate(rows)','This supplied helper groups validated rows by composite identity, compares payloads and returns unique rows, duplicate-delivery references and conflict groups. Validate first. Deduplication does not parse or authenticate a record.'),
 ...example(`from security_lab import load_fixture, validate_rows, deduplicate
accepted, rejected = validate_rows(load_fixture()['events'])
unique, duplicates, conflicts = deduplicate(accepted)
print('Unique events:', len(unique))
print('Repeated deliveries:', duplicates)
print('Conflicting groups:', len(conflicts))`),
 p('The chosen representative is the first delivered equal copy. If you reverse delivery order, the representative reference can change even though the unique-event count is the same. That is why a reproducible report records both its input and reconciliation policy. Never claim that the retained delivery arrived first in real-world event time simply because it appeared first in the collector file.'),
 h('Part 4 · Do not overwrite a conflict'),
 p('Imagine another delivery for auth A01 whose result changes from rejected to accepted. A dictionary assignment seen[key] = row would quietly keep the later version and hide the disagreement. The supplied helper excludes that entire conflicting group from normal counts and reports its references. The resulting count is incomplete with an explicit quality flag; it is not a confident corrected total. Resolving the conflict needs authorised source evidence beyond this worksheet.'),
 ...exercise('Practice: introduce one conflicting payload in memory and inspect the references kept for review.',`from security_lab import load_fixture, deduplicate
first = load_fixture()['events'][0]
changed = {**first, 'record': 'TEST', 'result': 'accepted'}
unique, duplicates, conflicts = deduplicate([first, changed])
print('Countable events:', len(unique))
print('Conflicting references:', conflicts[0]['records'])`,'The helper preserves the disagreement instead of deciding which result is true. This example isolates deduplication using two already well-shaped rows.'),
 h('Part 5 · Check the invariants and count honestly'),
 p('For the clean fixture, accepted deliveries equal unique events plus repeated equal deliveries because there are no conflicts. With conflicts, add the number of deliveries inside quarantined groups as a separate term. Do not add the number of conflict groups to the number of events and call that an exact reconciliation. A group can contain several deliveries. Write which unit each total uses, and test the clean and conflict cases separately.'),
 ...exercise('Mini challenge: prove that equal event IDs from different sources are separate under this contract.',`from security_lab import load_fixture, deduplicate
first = load_fixture()['events'][0]
other = {**first, 'record': 'OTHER', 'source': 'training-copy'}
unique, duplicates, conflicts = deduplicate([first, other])
print('Distinct composite identities:', len(unique))`,'Changing the source changes the documented identity. This does not assert that a real source is trustworthy; it exercises the grouping contract.'),
 p('Stop before applying a threshold. At this point you have defensible source-event units and references to duplicate or disputed evidence. You still need time semantics and a stated interval. A clear intermediate result is valuable: it allows a reviewer to challenge one assumption without having to reverse-engineer an entire script.'),
 s('key','Deduplicate by a documented source-event identity. Preserve duplicate references and surface conflicts before counting behaviour.')
 ],[
 check('Why is event_id alone not the key?','Different sources can reuse the same event_id.','The documented identity is source plus event_id.'),
 check('Is L04 another failed-login event?','No. It repeats auth A03 under this fixture contract.','It is another delivery of the same source event.'),
 check('Is alert Z01 an additional login failure?','No. It is a separate alert event about earlier failures.','Counting evidence and conclusions together inflates the behaviour count.'),
 check('What happens to conflicting copies?','The group is quarantined from ordinary event counts and its references are reported.','Do not overwrite evidence or invent which version is correct.'),
 check('Can representative delivery references change after reordering?','Yes. Equal copies retain the first supplied representative.','Record input order/policy; the unique count should still agree.'),
 check('Can every source ignore annotation during comparison?','No. That exclusion belongs to this fixture contract.','Field meaning must come from the source specification.')
 ],'Reconcile 12 deliveries to 11 unique events. Explain L03/L04, Z01 and how a conflict changes the confidence of a count.'),
 '9.4':lesson(
 'Convert explicit offsets to UTC, preserve unknown times and distinguish event-time order from collection-time availability.',[
 h('Part 1 · Two clocks answer different questions'),
 p('Event time says when the source reports something happened. Received time says when the collector reports obtaining the delivery. A04 happened at 00:01:30 UTC but arrived at 00:08:30 UTC. Sorting receipt times can therefore put an earlier event at the end. Neither field alone proves a source clock was accurate. The fixture assumes its offset-bearing source clocks are correct only so that we can practise reconciliation with a known contract.'),
 term('Aware datetime and UTC normalisation','A datetime with a usable UTC offset describes an instant relative to UTC. astimezone(timezone.utc) changes its representation while preserving that instant. An offset-free time does not establish which instant it means.'),
 p('09:00:00+09:00 and 00:00:00Z represent the same instant on the stated date. Python datetime.fromisoformat parses the forms used here. The supplied utc_time helper returns None for invalid or offset-free values. It never guesses your computer timezone, never replaces missing data with the current time and never treats received_time as an undocumented substitute for event_time.'),
 h('Part 2 · Show one conversion clearly'),
 ...example(`from security_lab import utc_time
print(utc_time('2026-10-01T09:00:00+09:00').isoformat())
print(utc_time('2026-10-01 09:01:30'))`),
 p('The first output has +00:00, indicating UTC. The second is None, meaning that this helper cannot place the value on the UTC event timeline. None does not mean midnight, zero events or that the event never happened. The input remains in a separate unknown-time list. Keeping unknowns is necessary because leaving them out of an interval count can otherwise look like evidence of absence.'),
 h('Part 3 · Build a known-time view without losing unknowns'),
 term('timeline(rows)','This helper returns known-time records ordered by UTC instant plus deterministic source/ID tie-breakers, and a separate list of unknown-time records. Sorting changes the view, not the source file or the credibility of its clocks.'),
 ...exercise('Practice: build the unique-event timeline and name the unknown delivery reference.',`from security_lab import load_fixture, validate_rows, deduplicate, timeline
accepted, _ = validate_rows(load_fixture()['events'])
unique, _, _ = deduplicate(accepted)
ordered, unknown = timeline(unique)
print('Known-time events:', len(ordered))
print('Order:', ','.join(row['event_id'] for row in ordered))
print('Unknown references:', [row['record'] for row in unknown])`,'Validation and reconciliation happen before ordering. L11 stays available for review rather than receiving an invented offset.'),
 p('Notice where A04 appears relative to A02 and A03. It belongs between them by reported event time, even though the collector delivered it last. Deterministic tie-breaking makes repeated output stable when timestamps tie; it does not establish causal order between simultaneous observations. A timeline should state what its ordering rule can and cannot resolve.'),
 h('Part 4 · Define the interval before filtering'),
 term('Half-open interval [start, end)','The start instant is included and the end instant is excluded. Adjacent intervals can share a boundary without counting that boundary event twice. The helper requires increasing offset-bearing endpoints.'),
 p('Our question uses [00:00,00:03) UTC on 2026-10-01. A failure exactly at 00:00 belongs to it; one exactly at 00:03 does not. This boundary rule is deliberate and must appear in the report. An inclusive end may be suitable for a different query, but silently changing it between runs makes counts incomparable. Always compare compatible aware instants rather than sorting raw mixed-offset strings.'),
 h('Part 5 · Separate what happened from what was available'),
 ...exercise('Mini challenge: compare known failures available by 00:07 with the complete fixture at its later cutoff.',`from security_lab import load_fixture, validate_rows, deduplicate, utc_time, login_window
accepted, _ = validate_rows(load_fixture()['events'])
unique, _, _ = deduplicate(accepted)
cutoff = utc_time('2026-10-01T00:07:00Z')
early = [row for row in unique if utc_time(row['received_time']) <= cutoff]
start, end = '2026-10-01T00:00:00Z', '2026-10-01T00:03:00Z'
print('Available early:', len(login_window(early, start, end)[0]))
print('Available later:', len(login_window(unique, start, end)[0]))`,'This clean fixture has valid receipt offsets. In a general collector, unknown receipt times would need their own visible handling rather than this simplified comprehension.'),
 p('The earlier alert seeing three failures and the final worksheet seeing four are consistent with late arrival. They use different collection cutoffs. Neither total alone demonstrates tampering or a broken alert. In your note include interval, cutoff and clock assumption together. If a source timezone is undocumented, the next task is obtaining that documentation or another trusted time reference, not selecting whichever offset makes the timeline look neat.'),
 s('key','Normalise known offsets, retain unknowns and disclose event interval plus collection cutoff. Time order is not proof of causation.')
 ],[
 check('Do 09:00+09:00 and 00:00Z describe different instants here?','No. They describe the same instant on the stated date.','Offsets must be normalised before comparison.'),
 check('What should happen to L11?','Keep it in the unknown-time list.','Its source timezone is undocumented.'),
 check('Can received_time silently replace missing event_time?','No. They answer different questions.','A substitute would change the timeline semantics.'),
 check('Is an event exactly at the interval end included?','No, the stated interval is half-open.','[start,end) includes start and excludes end.'),
 check('Why do early and later counts differ?','A04 arrived after the earlier collection cutoff.','Availability time and event time differ.'),
 check('Does UTC sorting verify clock accuracy or causation?','No. It orders reported instants under stated assumptions.','Accurate clocks and causal links need separate evidence.')
 ],'Explain A04’s two times, L11’s unknown timezone and the interval boundary using your own examples. Record both counts and their collection contexts.'),
 '9.5':lesson(
 'Apply a small explicit review rule to unique timed events and write a finding that separates observations, quality flags, interpretation and next checks.',[
 h('Part 1 · Translate the question into a rule'),
 p('The question now has the pieces it needs: a prepared source, validated records, documented event identity and known-time interval. Our teaching rule requests review when an account label has at least three unique authentication failure events in the fixed three-minute interval. This is a toy rule for reasoning, not a threshold to copy into every real service. Normal retry patterns, source coverage and operational context change what a useful threshold would be.'),
 term('Detection rule and review threshold','A rule describes observable conditions. Crossing a threshold produces a review candidate. It does not by itself prove malicious intent, identity takeover, malware or harm.'),
 p('The rule filters source auth and action login.failed. It does not count every record containing the word failed, every HTTP refusal or the alert itself. It groups source-event observations by a reported account label, which is not independent proof of who acted. Keep that distinction in the title and conclusion: reported failures for maya under this dataset, not attacker identified.'),
 h('Part 2 · Follow a small complete pipeline'),
 term('analyse(document)','This supplied helper combines validation, deduplication, timing, interval filtering and a review summary. The report keeps rejected rows, duplicates, conflicts and unknown-time references alongside counts. Its interval and threshold are deliberately fixed for the supplied case.'),
 ...example(`from security_lab import load_fixture, analyse
report = analyse(load_fixture())
print('Unique events:', report['unique_events'])
print('Window failures:', report['failure_count'])
print('Review labels:', report['review_accounts'])
print(report['conclusion'])`),
 p('Read the helper rather than treating it as magic. Counter accumulates counts for each account label in selected events. The comparison count >= 3 produces the candidate list. sorted gives deterministic output. The report never blocks an account, resets a credential or deletes a file. It provides a bounded observation for a person to assess with the correct authority and additional context.'),
 h('Part 3 · Link the finding to evidence'),
 ...exercise('Practice: identify the delivery references supporting the four counted failures and show quality flags beside them.',`from security_lab import load_fixture, analyse
report = analyse(load_fixture())
print('Evidence:', ','.join(report['failure_records']))
print('Rejected:', len(report['rejected']))
print('Conflicts:', len(report['conflicts']))
print('Unknown event-time references:', report['unknown_time_records'])`,'A count with traceable references can be reviewed. Unknowns and rejected inputs are part of the result, even when they do not change this particular failure count.'),
 p('The retained references appear in input grouping order, not sorted event-time order. This is acceptable because they identify evidence rather than claiming chronology. If you need a chronological display, use the separately explained timeline view and label it. Avoid making the same array mean both collection order and event order in different paragraphs of a report.'),
 h('Part 4 · Test an alternative explanation'),
 p('Four failed logins could result from stale credentials in an approved job, ordinary user mistakes, or misuse. The prepared records do not select among those explanations. Ask for the permitted job schedule and credential-change history, appropriate user confirmation and additional account/session evidence. A later accepted-login event is relevant context, but it is not proof that the failures caused a successful intrusion. Shared IPs do not identify a unique person.'),
 term('False positive, false negative and coverage','A false positive flags benign activity under an intended detection goal. A false negative misses concerning activity under that goal. You need suitable labelled context to measure them; no alert and no observed event are not equivalent to no harm.'),
 p('A legitimate job repeatedly failing might be a correct detection of failures but an unhelpful signal for a rule advertised as confirmed account compromise. Define the intended goal before naming an error. You cannot estimate a production false-positive rate from one prepared case, and tuning the threshold until this worksheet looks quiet is not evidence of improvement. Later weeks will build explicitly labelled test sets and evaluate rule changes against the same data.'),
 h('Part 5 · Write an actionable, limited finding'),
 ...exercise('Mini challenge: print a three-line finding with an observation, an unknown and the next evidence question.',`from security_lab import load_fixture, analyse
report = analyse(load_fixture())
print(f"Observed: {report['failure_count']} distinct failures in {report['failure_window']}")
print('Unknown: whether these failures were ordinary mistakes, a stale job or misuse')
print('Next: check authorised job history and account context before response decisions')`,'Separate observation from hypothesis and action. A defensible next question is more useful than invented attribution.'),
 p('Finish by stating the full fixture cutoff, 00:08:30 UTC, and the known clock assumption. Mention that the alert at 00:07 had only three failures available. If conflicts or rejected rows appear in a modified copy, explain how they limit the total rather than reporting a clean verdict. Save the reasoning in your day notes; do not paste raw real logs or credential values into a public learning report.'),
 s('key','A threshold is a reason to review. A finding needs the interval, cutoff, evidence references, quality flags and a justified next question.')
 ],[
 check('Does four failures prove takeover?','No. It establishes reported failures under the stated counting rule.','Intent, identity and account impact need more evidence.'),
 check('Why filter source and action explicitly?','To count the intended behaviour rather than unrelated errors or alerts.','A word match is not the same as an event contract.'),
 check('Can one prepared case establish a production false-positive rate?','No. Suitable labelled context and representative evaluation are missing.','Do not generalise a demonstration into an operational metric.'),
 check('Should the script automatically block maya?','No. It generates a review candidate, not an authorised response decision.','A threshold alone is insufficient for impact-bearing action.'),
 check('What makes the finding traceable?','Its source references, interval, collection cutoff and processing policy.','A reviewer must be able to inspect the basis of the count.'),
 check('Name a useful next evidence question.','Was an authorised job using stale credentials at the relevant time?','A discriminating question can help distinguish plausible explanations.')
 ],'Write a short finding with evidence references, interval/cutoff, quality flags, two plausible explanations and one next authorised check.'),
 '9.6':lesson(
 'Check original file bytes, distinguish repeatability from correctness and run failure-case tests without changing the evidence fixture.',[
 h('Part 1 · Know which input you analysed'),
 p('A report should identify the input version. Two files can have the same name and different bytes. A SHA-256 digest helps compare a file with a retained reference, while the filename and collection notes explain where the bytes came from. Hash the original file bytes, not a pretty-printed dictionary, when your question concerns whether the exact file changed. JSON whitespace can change bytes without changing the parsed observations.'),
 term('hashlib.sha256 and a byte digest','hashlib is Python’s standard hashing module. sha256 accumulates bytes and produces a fixed-length hexadecimal digest. digest(path) is the supplied chunk-reading helper; it does not encrypt the file, prove who created it or establish trust in a reference stored beside it.'),
 p('The helper reads fixed-size chunks rather than loading an arbitrarily large file at once. In this lab the loader already limits input size, but streaming is still a useful habit for hashing. The same digest comparison is meaningful only when the earlier reference and its provenance are protected appropriately. An adversary able to replace both a file and its local digest can make that local pair agree.'),
 h('Part 2 · Observe byte change without inventing semantic change'),
 ...example(`import hashlib
from security_lab import SAMPLE, digest
raw = SAMPLE.read_bytes()
print('Digest agrees:', digest() == hashlib.sha256(raw).hexdigest())
print('SHA-256 hex characters:', len(digest()))
print('Extra newline changes bytes:', hashlib.sha256(raw + b'\\n').hexdigest() != digest())`),
 p('The changed-byte demonstration stays in memory; it does not overwrite the fixture. A different digest tells you that the bytes differ. It does not tell you whether the change was malicious, whether the previous version was correct, or which field changed. For meaning, parse the separately controlled version and compare the relevant records under their schema. Keep byte integrity and semantic analysis as two related but distinct questions.'),
 h('Part 3 · Make the analysis repeatable'),
 term('Determinism and reproducibility','Deterministic analysis gives the same result for the same input and policy. Reproducibility also needs enough input, environment and method information for someone else to repeat it. A deterministic mistake is still a mistake.'),
 ...exercise('Practice: run the pipeline twice and verify the original bytes are unchanged.',`from security_lab import SAMPLE, load_fixture, analyse
before = SAMPLE.read_bytes()
one = analyse(load_fixture())
two = analyse(load_fixture())
print('Repeated reports agree:', one == two)
print('Reference unchanged:', SAMPLE.read_bytes() == before)`,'Repeated equality checks consistency. Independent expected outcomes and failure cases are needed to check correctness.'),
 p('Avoid inserting the current time or an absolute machine path into the analytical result when those values are not part of the question. They make repeated output differ for irrelevant reasons. A separate execution record can retain environment and run time when needed. In this example the fixed interval and fixture facts make exact comparison easy. When the source grows or collection changes, record the new cutoff instead of pretending the old result still describes it.'),
 h('Part 4 · Test what could make the finding wrong'),
 term('unittest and regression cases','unittest runs named checks with expected outcomes. A regression case preserves behaviour after a fix. The supplied suite tests the clean count, duplicate/conflict handling, unknown times, interval endpoints, loader errors, unchanged inputs and byte/semantic differences.'),
 s('sh','python -m unittest -v'),
 p('Use independently reasoned expectations: an event exactly at the end is excluded; a repeated source event does not add another failure; different sources may reuse an ID; a conflicting group is reported rather than overwritten. These cases test the investigation semantics. A test that merely repeats the implementation’s calculation as its expected value may reproduce the same bug and provide little additional confidence.'),
 h('Part 5 · Share the smallest useful result'),
 p('Real authentication logs can contain identifiers, IPs, user agents and sensitive data. OWASP’s logging guidance stresses excluding secrets and controlling access to log data. This fixture is fictional and public, but that does not grant permission to publish a real export. A minimal summary should include only the fields needed for its reader and keep detailed evidence in its approved location. Python can help apply a field allowlist, but the sharing decision still needs review.'),
 ...exercise('Mini challenge: select a small summary from the fictional report without copying the complete event list.',`import json
from security_lab import load_fixture, analyse
report = analyse(load_fixture())
summary = {name: report[name] for name in ('scope', 'failure_count', 'conclusion')}
print(json.dumps(summary, sort_keys=True))`,'An allowlist states which fields are included. It is a useful starting point for minimisation, not automatic approval to share real sensitive findings.'),
 s('key','Digest agreement, repeated output and passing tests answer different questions. Keep the evidence and the claim for each check explicit.')
 ],[
 check('Does a hash encrypt a log file?','No. It summarises bytes for comparison.','Hashing does not hide the source data.'),
 check('Does a digest beside a file establish an independently trusted baseline?','No. Both may have been replaced together.','Reference provenance and protection matter.'),
 check('Can a newline change the digest while parsed observations stay equal?','Yes. Byte identity and JSON meaning are different comparisons.','Hash the intended representation.'),
 check('Do two equal reports prove the analysis is correct?','No. A deterministic bug can repeat exactly.','Use independent expected results and boundary cases.'),
 check('Why test an event exactly at the interval end?','It verifies the documented half-open boundary.','A small off-by-one boundary error changes a security count.'),
 check('May the same public sharing policy be used for real logs?','No. Review readers and minimise fields under the actual data policy.','Public synthetic evidence does not imply public real evidence.')
 ],'Record the test outcomes you actually ran. Explain byte identity, repeatability and correctness separately, then write a minimal fictional summary.'),
 '9.7':lesson(
 'Independently explain and reconstruct the evidence pipeline, test changed observations and produce a referenced investigation summary without overclaiming.',[
 h('Part 1 · Retrieve the model before rereading'),
 p('Close the earlier explanations and draw seven boxes: question, bounded input, row validation, identity reconciliation, time, rule and finding. For each arrow name what can go wrong and which reference survives. Explain why parsing is not validation, validation is not authenticity, a delivery is not always another event, and a rule match is not a confirmed incident. If a distinction feels uncertain, return to the matching day and demonstrate it using a small example.'),
 term('Independent demonstration','You can explain the contract, predict a changed result, implement or adapt the relevant step, and verify it against an independently reasoned expectation. Merely reproducing a supplied terminal output is a useful earlier milestone, not the same demonstration.'),
 p('The current module is short enough to inspect in stages. You do not need to memorise its spelling. Use the official module documentation when a function signature is unfamiliar, but write down your expected result before pressing Run. Take extra sessions for any stage you cannot explain; a Day 7 label is not a deadline that justifies skipping the reasoning.'),
 h('Part 2 · Reconcile the reference case'),
 ...example(`from security_lab import load_fixture, analyse
report = analyse(load_fixture())
print('Deliveries / unique / timed:', report['deliveries'], report['unique_events'], len(report['ordered_event_ids']))
print('Failure count:', report['failure_count'])
print('Unknown references:', report['unknown_time_records'])`),
 p('The clean case has 12 deliveries, 11 unique source events and ten events placed on the known-time timeline. Four unique authentication failures belong to [00:00,00:03) UTC. L04 repeats L03. L12 delivers A04 late. L11 remains unknown-time. Z01 is an alert event and not a fifth failure. The final collector cutoff is 00:08:30 UTC; the earlier alert had only three counted failures available. Explain each number without relying on the output block.'),
 h('Part 3 · Predict one change at a time'),
 p('Make separate practice copies, or change an independent in-memory document. Add an equal copy of A01 with a new record label: delivered rows increase by one while the unique failure count stays four. Next create a conflicting payload under A01: the group becomes a quality issue and is excluded, so the remaining count is incomplete. Then remove a failure’s offset: it remains a source event but cannot enter a known UTC interval. Finally add a new unique failure exactly at 00:03:00Z: it is outside the half-open interval.'),
 ...exercise('Practice: add an equal delivery copy in memory and confirm the predicted delivery/event/failure counts.',`from security_lab import load_fixture, analyse
document = load_fixture()
document['events'].append({**document['events'][0], 'record': 'EXTRA'})
report = analyse(document)
print('Deliveries:', report['deliveries'])
print('Unique:', report['unique_events'])
print('Failures:', report['failure_count'])`,'The new delivery label is distinct, but its source-event identity and payload agree with A01. The input file itself remains untouched.'),
 h('Part 4 · Challenge an edge and keep the unknown'),
 ...exercise('Mini challenge: remove the offset from A01 in memory. Explain why this reduces the known-window count without proving fewer real failures.',`from security_lab import load_fixture, analyse
document = load_fixture()
document['events'][0]['event_time'] = '2026-10-01 00:00:00'
report = analyse(document)
print('Known-window failures:', report['failure_count'])
print('Unknown failure-time references:', report['unknown_failure_times'])`,'The source event is not erased. Its time cannot be safely compared with the stated UTC interval; the quality flag explains the smaller count.'),
 p('For every variant compare the expected result and all quality flags, not only the headline number. A lower count can result from worse data quality. A greater count can result from another delivery or a later cutoff rather than more underlying behaviour. This is where security reasoning and Python meet: the code must preserve enough context for the explanation to remain honest after the data changes.'),
 h('Part 5 · Write and defend a small case summary'),
 p('Your deliverable is one page: scope and question; input/version and identity contract; interval/cutoff and clock assumption; observations with source references; rejected/conflicting/unknown evidence; interpretation and alternatives; next authorised evidence question. Include the tests you personally ran and one limitation of the helper. Do not claim confirmed takeover, exfiltration or a clean account. The provided observations do not establish those conclusions.'),
 p('Use the questions below as an oral or written review. Answer before revealing, and revise answers that omit the counting unit or the evidence boundary. When ready, Week 10’s roadmap continues with file integrity and recovery automation: still a cybersecurity task supported by Python. Weeks 10–16 currently contain daily plans, not completed teaching lessons. Return for each full week when you are ready rather than mistaking a roadmap title for mastered material.'),
 s('key','A good security script preserves the distinction between source observations, data-quality limits and conclusions. Demonstrate your reasoning on a changed case.')
 ],[
 check('What exact question does the reference pipeline answer?','How many unique reported auth failures fall in the stated fixed interval, with quality/context limits.','It is not a universal compromise detector.'),
 check('How many deliveries, unique events and known-time events are in the clean fixture?','12 deliveries, 11 unique events and 10 known-time events.','Duplicate delivery L04 and unknown-time L11 affect different counts.'),
 check('Why is L04 not another failure?','It repeats auth A03 with an equal event payload.','The composite source-event identity is unchanged.'),
 check('Why is Z01 not a fifth failure?','Its action is an alert rule result, not login.failed.','A derived alert and its supporting observations are different units.'),
 check('What is the counted interval?','[2026-10-01T00:00:00Z, 2026-10-01T00:03:00Z).','State the timezone and end-exclusion rule.'),
 check('What is the final collection cutoff?','00:08:30 UTC on 2026-10-01 in the prepared case.','The later collection includes A04, which the earlier alert had not received.'),
 check('Why preserve L11 separately?','Its source time lacks a documented timezone.','Do not turn an unknown instant into a guessed known instant.'),
 check('How should conflicting same-identity payloads be handled?','Report the references and quarantine the group from normal counting.','Silent overwrite hides disagreement.'),
 check('What happens when an equal A01 delivery gets a new record label?','13 deliveries, still 11 unique events and four counted failures.','New delivery identity does not necessarily mean a new source event.'),
 check('What happens to a new event exactly at 00:03Z?','It is excluded from this fixed interval.','The end is not included.'),
 check('Can fewer counted failures mean poorer evidence?','Yes, for example when a relevant event loses its timezone.','Read the unknown/error flags beside the count.'),
 check('Does a valid JSON object prove a trustworthy source?','No. Format, contract and provenance are separate questions.','Syntactic correctness is not authenticity.'),
 check('Does same-IP evidence identify one person?','No. Addresses may be shared or translated, and attribution needs additional evidence.','Do not promote a field label into identity proof.'),
 check('What does a changed SHA-256 establish?','The compared byte sequences differ, under the comparison assumptions.','It does not by itself establish cause or malicious intent.'),
 check('Name one competing explanation for the failures.','Ordinary mistakes or stale credentials in an authorised job, alongside possible misuse.','Ask for discriminating authorised evidence rather than choosing by drama.'),
 check('What establishes readiness for the next stage?','Explain and reproduce the clean and changed cases with justified outputs and limitations.','Independent demonstration is stronger evidence than a completion checkbox.')
 ],'Create the one-page investigation summary and record which variants you predicted correctly. List any concepts that need another session before Week 10.')
};
