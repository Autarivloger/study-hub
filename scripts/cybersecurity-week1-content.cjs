// Original beginner lessons. Keep these separate from the Python curriculum.
const h=v=>({t:'h',v}),p=v=>({t:'p',v}),key=v=>({t:'key',v}),tip=v=>({t:'tip',v});
const term=(v,note)=>({t:'new',v,note});
const check=(q,a,why)=>({q,a,why});
module.exports={
 '1.1':{
  objective:'Explain what cybersecurity protects, identify the main parts of a digital system, and describe how your study notes travel between a device and a website.',
  sections:[
   h('1. Start with something you care about'),
   p('Imagine that you have studied for three months. Your notes, lesson progress and account access help you continue learning. Now imagine someone reads your private notes, changes your saved progress, or makes your account unavailable. Each situation harms something you value. Cybersecurity begins by understanding that value and protecting it.'),
   term('Cybersecurity','The work of protecting digital systems, services and information against unauthorised access, unwanted changes and disruption. It includes people, decisions and everyday habits as well as technical tools.'),
   p('A digital system is a collection of parts that work together: a phone, its operating system, an app, your account, stored information and sometimes a service on the internet. Protecting only one part can leave another part exposed. A locked phone cannot stop someone using a stolen password on a different phone.'),
   p('Security problems can also start with accidents. Deleting your only copy of a document is not an attack, but you still need a way to recover. Good security asks what could go wrong and how to reduce the harm, rather than assuming every problem is caused by a hacker.'),
   key('Start with three questions: What matters? What could harm it? What would help protect it?'),
   h('2. Understand the parts before the tools'),
   term('Hardware and software','Hardware is the physical equipment: a phone, keyboard, processor or storage drive. Software is the instructions that equipment runs: an operating system, browser or other application.'),
   term('Operating system and application','An operating system, such as Windows or Android, manages the device and provides services to programs. An application is software for a particular task, such as browsing, messaging or editing a document.'),
   p('Think of a classroom. Hardware is the building and equipment. The operating system coordinates access to the rooms and equipment. Applications are the activities happening inside. This comparison is only a memory aid; the important point is that several layers cooperate.'),
   term('Data and file','Data is information represented so a computer can store or process it: text, photos, settings or a saved score. A file is one way of organising stored data, usually with a name. Some data lives in an app or database rather than a document you can open directly.'),
   p('When you type a note, the keyboard is hardware, the browser is an application, and your words are data. Saving a backup creates a file containing a copy of that data. A security decision can concern any layer: who can use the device, what the app may access, or who can read the backup.'),
   h('3. Follow one ordinary action'),
   term('Browser, client and server','A browser displays web pages. A client requests a service; a server provides a service. When your browser requests a hosted page, it acts as a client and a remote server returns the page.'),
   p('Opening Study Hub online: your browser requests the page; the hosting service returns its HTML, styles and JavaScript; the browser runs the page on your device. Offline: a locally available copy can run without asking the hosting service again. A page being online does not mean every note you write is automatically sent to its host.'),
   term('Local storage and sync','Local storage is browser storage associated with a website on one browser profile. Sync transfers selected information between devices through a service. They are different locations, with different access and recovery questions.'),
   p('In this Study Hub, notes are saved in browser storage. Export makes a backup file. The optional configured sync sends saved data to its sync service. Clearing browser data can remove a local copy. Publishing the website code is a different action from publishing your private notes. Always distinguish the app, the stored data and a backup of that data.'),
   tip('Draw four boxes: device → browser → website service → optional sync service. Mark where the page comes from and where your notes are stored. We will study the network journey more closely in Week 2.'),
   h('4. Check your understanding'),
   p('Explain an everyday action in plain English before learning security tools. If a term is unclear, revisit its definition and give your own example. Today you need to understand the parts, not memorise a list of attacks.')
  ],
  checks:[
   check('Your phone screen breaks, your browser needs an update, and your backup contains lesson notes. Which is hardware, which is software, and which is data?','The screen is hardware. The browser is software. The lesson notes are data.','The backup file is a container for the data. These categories help you describe exactly what needs protection.'),
   check('A website loads on a second phone, but your locally saved notes are missing. Does that alone prove someone stole your notes?','No. The second phone may simply have a separate browser storage area and no configured sync.','Separate observation from explanation. Missing data on another device can be a storage or sync issue; it is not evidence of theft by itself.'),
   check('Explain cybersecurity without using the word hacking.','It means protecting digital information and services so authorised people can use them safely and reliably.','Mention access, unwanted changes and disruption. Your explanation can use different words if those ideas are clear.')
  ],
  reflection:'Describe one device, one application and one piece of information you value. Where is that information stored? What would happen if you lost access?'
 },
 '1.2':{
  objective:'Identify valuable assets and explain confidentiality, integrity and availability using concrete examples.',
  sections:[
   h('1. List what you are protecting'),
   term('Asset','Something valuable to a person or organisation. In cybersecurity, this can be a device, account, information, software or an important service. Its value comes from what people depend on it for.'),
   p('Your phone is an asset, but so are your email account, study notes and ability to open your course. A small text file can be more valuable than an expensive device if it contains work you cannot recreate. Value is not just the purchase price.'),
   term('Dependency','Something an asset relies on. For example, access to a learning account might depend on your email account because password recovery messages go there.'),
   p('Imagine Maya uses her email to recover three other accounts. Her email is therefore important beyond its messages. If she loses control of it, several services may be affected. Identify these connections before deciding where to spend your effort.'),
   p('A simple inventory answers: What is it? Who uses or manages it? Where does its information live? What depends on it? What would losing it interrupt? Use labels such as personal email or study backup. You do not need to record real passwords or recovery codes in a learning inventory.'),
   h('2. Confidentiality: the right people can read it'),
   term('Confidentiality','Information is available only to people or systems authorised to access it. The central question is: who is allowed to see this?'),
   p('A private journal being read by a stranger is a confidentiality failure. A course timetable intentionally shared with students is not a failure just because several people can read it. The expected audience matters.'),
   p('For your study backup, ask whether it contains only public lesson material or also private notes and account details. Two files can look similar but require different handling. A public link can make a file easier to share while also expanding who can access it.'),
   h('3. Integrity: the information stays trustworthy'),
   term('Integrity','Information and system behaviour remain accurate and are changed only in authorised ways. The question is: can I trust that this is what it should be?'),
   p('If you correctly mark a lesson complete, that authorised change supports integrity. If a saved score becomes 100 instead of 40 because of an unauthorised change or an application bug, integrity has failed. Integrity does not mean nothing may ever change; it means changes should be appropriate and trustworthy.'),
   p('Suppose a practice document is readable but its instructions have been altered. Availability is fine because you can open it. Confidentiality may also be fine because only the intended student sees it. The immediate problem is that its content cannot be trusted.'),
   h('4. Availability: you can use it when needed'),
   term('Availability','Authorised users can access needed information or services in a useful way at the time they need them. The question is: can the right person use this now?'),
   p('A service outage, broken device or lost local data can stop you studying. These are availability problems even when no information was stolen. An offline course copy helps with some internet outages, but cannot replace a missing backup of your personal work.'),
   term('CIA triad','A memory tool combining Confidentiality, Integrity and Availability. Here CIA refers to these three security goals, not an organisation.'),
   p('One event can affect several goals. Someone who steals a backup, edits its contents and deletes the original harms confidentiality, integrity and availability. State each effect separately; forcing every event into exactly one category hides useful information.'),
   key('Confidentiality = appropriate access. Integrity = trustworthy content and changes. Availability = usable access when needed.'),
   h('5. Set priorities and connect Python'),
   p('Compare losing a replaceable wallpaper with losing your only copy of a months-long project. Both matter, but the consequences are different. Start with accounts and information whose loss would interrupt important work, reveal private information or affect other people.'),
   p('Python can help produce an inventory: collect permitted file names, group them by location and create a report for you to review. The value is a more complete picture. Python cannot decide which files are private or important without rules and human judgement. For now, understand this role; there is no coding exercise.'),
   tip('An inventory should tell you where protection is needed. Avoid turning it into a new collection of secrets. Keep sensitive account details out of your course notes.')
  ],
  checks:[
   check('A stranger reads a private backup; a progress record changes incorrectly; your course cannot open during an outage. Match each to a CIA goal.','Reading the private backup: confidentiality. Incorrect progress: integrity. Unavailable course: availability.','More than one goal may be affected in a real incident. These examples highlight the main concern in each situation.'),
   check('You intentionally correct an incorrect note. Have you broken integrity because the note changed?','No. An authorised correction can improve integrity.','Trustworthy changes are expected. Integrity is concerned with accuracy and appropriate control over changes.'),
   check('Why might your recovery email deserve protection before a less important account?','It may allow recovery of several other accounts, so it has important dependencies.','Look beyond the inbox itself. Its role in regaining account access can increase the impact of losing it.')
  ],
  reflection:'List three assets. For each, write its main CIA concern and one dependency. Explain which you would protect first and why.'
 },
 '1.3':{
  objective:'Distinguish a threat, vulnerability, risk and control, then analyse a simple security situation without guessing.',
  sections:[
   h('1. Separate four ideas that sound similar'),
   p('You already know what you want to protect. Now ask how it could be harmed. The words threat, vulnerability, risk and control describe different parts of that question. Learn them through one continuing example: a student uses the same password for email and a small discussion website.'),
   term('Threat','A potential cause of harm to an asset. It can involve a person, a malicious action, an accident or an environmental event. A threat is a possibility; it does not mean harm has already happened.'),
   p('Someone attempting to use stolen account details is a threat to the student’s email. Accidental deletion is another possible threat to stored notes. Name the potential harm clearly instead of writing only dangerous internet.'),
   term('Vulnerability','A weakness that can contribute to harm when a threat takes advantage of it. It may be in software, configuration, a process or a habit.'),
   p('In our example, password reuse is a weakness. If the discussion website’s password is exposed, the same secret may work for email. A vulnerability does not prove that somebody has used the weakness to cause harm. It tells you something needs attention.'),
   term('Risk','The possibility of harm, considered with how likely it is and how serious the consequences would be in a particular situation.'),
   p('Email account takeover could be serious because it exposes messages and may enable recovery of other accounts. The risk depends on context: whether details have been exposed, whether an extra sign-in factor is enabled, and what the email controls. Risk is more than a scary name.'),
   term('Security control','A measure that reduces the chance or impact of harm. It can be technical, such as an access restriction, or procedural, such as independently checking an unusual request.'),
   h('2. Walk through the example carefully'),
   p('Asset: the student’s email account and messages.\nThreat: another person attempts to enter the account using exposed details.\nVulnerability: the same password is reused on another service.\nPossible impact: private messages are read and account recovery is misused.\nControls: give email a unique password and add an independent sign-in factor where supported.'),
   term('Multi-factor authentication (MFA)','Sign-in that uses factors from more than one category, such as something you know and something you have. A password plus a separate security key is an example. Two passwords are still the same kind of factor.'),
   p('The controls address different weaknesses. A unique password limits the usefulness of a password exposed elsewhere. MFA can make a password alone insufficient to sign in. Neither guarantees safety against every attack. We will study authentication methods and their limits in Week 4.'),
   h('3. Compare likelihood and impact'),
   term('Likelihood and impact','Likelihood asks how plausible an event is in the stated conditions. Impact asks what the consequences would be if it happened. Evidence, exposure and the importance of the asset help you judge both.'),
   p('Compare two students. One can replace a lost practice file in a minute. The other has no backup of a research project. Even if both devices face similar threats, the second student could suffer greater harm from data loss. A tested backup reduces that harm.'),
   p('For a beginner, use low, medium or high with a short reason. Do not pretend these labels are measured probabilities. Writing high impact because this is the only project copy is more useful than writing risk 97 without explaining where the number came from.'),
   term('Residual risk','The risk that remains after controls are applied. Protection usually reduces risk rather than making it disappear.'),
   key('Asset + a plausible harmful event + a weakness + consequences helps explain risk. A control should address the chance of that event, its impact, or both.'),
   h('4. Evidence before conclusions'),
   p('An unexpected sign-in alert deserves attention, but first check the event through the service’s own account activity page. It might be your new device, or it might be unauthorised activity. Record what you observed, what you do not yet know and what evidence would distinguish the explanations.'),
   tip('Common confusion: a slow computer is an observation, not proof of malware. An outdated application is a possible weakness, not proof of an attack. Separate facts from your interpretation.')
  ],
  checks:[
   check('A laptop holds the only copy of a project and may fail. Identify the asset, threat, weakness and a useful control.','Asset: project data. Threat: device failure. Weakness: dependence on one copy. Control: a separate backup with a checked recovery process.','A backup mainly reduces the impact of losing the original. It does not prevent every hardware failure.'),
   check('Is a long reused password automatically safe because it is difficult to guess?','No. If the exact password is exposed elsewhere, an attacker may not need to guess it.','Length and uniqueness address different problems. Explain the threat the control is meant to reduce.'),
   check('You see one failed login. What can you conclude with confidence?','A login attempt failed, according to the recorded event. More evidence is needed to identify who attempted it and why.','Do not turn one observation into a claim that your account was successfully accessed.')
  ],
  reflection:'Choose one imaginary situation. Write Asset, Threat, Vulnerability, Impact, Control and Remaining uncertainty. Keep facts and assumptions separate.'
 },
 '1.4':{
  objective:'Recognise common threat categories, explain how they differ, and choose a sensible first response to a suspicious message.',
  sections:[
   h('1. Malware is an umbrella word'),
   term('Malware','Software deliberately used to cause harm, gain unauthorised access or carry out unwanted actions. The name combines malicious and software.'),
   p('Malware describes harmful software, not every computer problem. A crashing app may have a normal bug. A deceptive message may steal information without installing software. Naming the mechanism helps you choose the right protection.'),
   term('Virus, worm and trojan','A virus spreads by infecting other files or programs. A worm can spread between systems without needing to attach itself to another program. A trojan pretends to be useful or legitimate while carrying out unwanted actions. Real malware can combine behaviours.'),
   term('Encryption','Turning readable information into a form that requires the appropriate key to read. Encryption normally helps protect information. An attacker can also misuse it to make a victim’s files unreadable without an attacker-controlled key.'),
   term('Ransomware and spyware','Ransomware is malware used for extortion, often by locking or encrypting data. Spyware secretly gathers information about a person or their activity. These names describe harmful behaviour; they are not mutually exclusive categories.'),
   p('Imagine a supposed study helper that secretly collects private documents. Its disguise is trojan-like, and its information gathering is spyware-like. You do not need to run a suspicious program to learn these categories. Focus on what the software claims to do and what it actually does.'),
   h('2. People can be targeted directly'),
   term('Social engineering','Manipulating a person into revealing information, granting access or performing an action. It exploits trust, pressure or confusion rather than relying only on a software weakness.'),
   term('Phishing','A deceptive communication that imitates a trusted source to get you to reveal information or take an unsafe action. It can arrive through email, text, messaging or other channels.'),
   p('Fictional example: a message says your learning account will close in ten minutes unless you sign in through its link. The pressure encourages you to act before checking. A realistic logo, familiar name or correct personal detail does not establish that the request is genuine.'),
   p('A useful first response is to pause and verify through the service’s known app or an independently obtained contact route. Do not use the suspicious message itself as your only source of verification. Good spelling is not a safety test, and a message with spelling errors is not automatically an attack.'),
   term('Scam','A dishonest scheme intended to obtain money, information or another benefit. Phishing is one method a scam can use. A scam may also involve a misleading sale or a phone conversation.'),
   h('3. Understand a data breach'),
   term('Data breach','A security incident involving unauthorised access to or disclosure of data. The visible effect may be information exposure rather than a broken device.'),
   p('A backup intended to be private becomes publicly accessible because of an incorrect sharing setting. That can expose information even if no malware is installed. When analysing it, ask what information was accessible, who could access it and what evidence of access exists.'),
   p('Website source sent to visitors is readable by those visitors. Putting an account secret in a public HTML or JavaScript file does not make it private. Changing its file name or hiding a button does not control access. If a real credential has been exposed, removing the visible copy does not invalidate copies already obtained; the credential must be replaced or revoked through its provider.'),
   p('A saved browser note is different from published website source. Whether someone can read it depends on access to the browser profile, device, exported backups and configured sync service. Use Day 1’s storage map to identify which location you actually mean.'),
   h('4. Use layers, and avoid blaming the victim'),
   p('A person can be deceived even when they are careful. Design should make mistakes less damaging: restrict access, keep recovery options and verify sensitive requests. Awareness matters, but it should not be the only protection.'),
   key('Malware is harmful software. Phishing is deceptive communication. Social engineering is manipulation. A breach describes unauthorised data access or disclosure. One incident may involve several of these.'),
   tip('You can recognise a suspicious pattern without proving who sent it. Record observable details and use a trusted route to check. Avoid entering real secrets into learning examples.')
  ],
  checks:[
   check('A fake sign-in page collects a password without downloading a program. Is this necessarily malware?','No. It is a phishing scenario; harmful software does not have to be installed.','Protection must address the deceptive request as well as device security.'),
   check('A private backup is accidentally shared with everyone. Which threat category and CIA goal are most relevant?','Unauthorised disclosure is a data breach concern. Confidentiality is the main CIA concern.','Investigate the exposure and access evidence. Do not assume malware was involved.'),
   check('A message says it is from your course provider and contains its logo. What would establish whether the request is genuine?','Check through the provider’s known app, independently opened website or trusted contact route.','A logo is easy to copy. The message should not be its own proof of authenticity.')
  ],
  reflection:'Write one fictional suspicious message and identify its pressure, requested action and independent verification route. Do not include a working deceptive link.'
 },
 '1.5':{
  objective:'Explain prevention, detection, response and recovery, then connect several controls into a complete protection plan.',
  sections:[
   h('1. Security continues after prevention'),
   p('Imagine that your study folder has a locked door. The lock helps prevent entry, but you still need to notice if someone enters, decide what to do and recover anything damaged. Digital security has the same continuing needs.'),
   term('Prevention, detection, response and recovery','Prevention reduces the chance of an incident. Detection helps notice possible problems. Response investigates and limits harm. Recovery restores usable, trustworthy systems or information after a disruption.'),
   p('In an imaginary account case: prevention limits unauthorised sign-in; detection highlights unexpected account activity; response checks what happened and limits further access; recovery restores the account and confirms important data is correct. These activities can overlap rather than happening in a perfect straight line.'),
   term('Security event and incident','An event is an observable occurrence, such as a sign-in attempt. An incident is a situation that compromises security or threatens security in a way that requires response. Many ordinary events are not incidents.'),
   p('A successful login by you is an event. A confirmed unauthorised login is an incident. An unexpected alert needs investigation before you know which explanation is correct. Detection produces information; it does not automatically produce the right conclusion.'),
   h('2. Give each layer a job'),
   term('Defence in depth','Using several complementary protective measures so that a weakness in one does not leave everything unprotected. The layers should address different failure paths.'),
   term('Patch, backup and restore','A patch is a software change that fixes an issue. A backup is a separate retained copy of information. Restore means recovering information from that copy. A backup is useful only if it is available and recoverable when needed.'),
   p('Worked example: an important study project has access restrictions to limit unwanted edits, appropriate software updates to fix known weaknesses, records of changes to help investigate problems, and a separate backup for recovery. Each measure has a reason. Buying several tools that all depend on the same failing device would not solve the missing recovery copy.'),
   p('A synchronised folder can copy deletions or unwanted changes to other devices. Some services provide version history or recovery features, but that must be checked. Sync and backup are not automatically interchangeable. A recovery exercise with harmless sample data helps establish whether the copy can actually be used.'),
   h('3. Think beyond individual tools'),
   p('The NIST Cybersecurity Framework 2.0 groups outcomes into Govern, Identify, Protect, Detect, Respond and Recover. Govern concerns decisions and responsibilities. Identify concerns understanding what matters and its risks. Protect, Detect, Respond and Recover address safeguards, observations, action and restoration. The framework helps organise work; it is not one piece of software you install.'),
   term('Least privilege','Giving a person or program only the access it needs for its task. Smaller permissions can limit the harm caused by an error or compromised account.'),
   term('Session','The continuing signed-in state that lets an account use a service without entering the password for every action. Ending an unwanted session can stop that particular signed-in access; the service’s security controls determine how to end it.'),
   p('A classmate who only needs to read a document does not automatically need permission to edit it or manage its sharing. Set the permission to fit the job. Restricting access should still allow legitimate work; a security control that blocks everyone permanently has failed availability.'),
   h('4. Learn what different security work covers'),
   term('Defensive security, application security and authorised testing','Defensive security protects and monitors systems. Application security builds and checks safeguards within software. Authorised testing evaluates an agreed system with explicit permission and defined limits.'),
   p('For a learning website, defensive work might monitor access and prepare recovery. Application security might ensure a user can access only permitted records. Authorised testing might check that boundary in a separate approved test environment. These activities support each other; no single role replaces the others.'),
   p('For a suspected personal account incident, start with verified account information. Use a trusted device and the provider’s recovery or security process, limit unwanted access and check recovery settings. If this is an organisation’s account, follow its reporting process. The exact actions depend on the evidence and service; a generic alert is not a reason to erase a device.'),
   key('A complete plan explains what you protect, how you reduce harm, how you notice trouble, how you respond and how you recover.'),
   tip('Common mistake: calling a backup a tool that prevents every attack. Its main value is recovery; it must be separate, protected and usable.')
  ],
  checks:[
   check('Classify these: fixing a known software weakness; reviewing unexpected activity; disabling a confirmed unwanted session; restoring a damaged document.','Prevention/protection; detection and investigation; response; recovery.','The categories can overlap, but naming each purpose helps you find gaps in a plan. A session is the continuing signed-in connection to an account.'),
   check('Your only backup is on the same storage drive as the original. What failure can still remove both?','Failure or loss of that drive can remove both copies.','Separation matters. Merely giving the second file a different name does not protect against the shared dependency.'),
   check('A reader is given permission to manage every user account. Which principle is missing?','Least privilege.','Match permissions to the actual task. Reading content does not require account administration.')
  ],
  reflection:'For one asset, describe a preventive control, a useful observation, a response decision and a recovery method. Explain how you would check that recovery works.'
 },
 '1.6':{
  objective:'Define a permitted learning scope, design a simple separate practice space, and explain where Python supports security work.',
  sections:[
   h('1. Permission comes before testing'),
   term('Authorisation and scope','Authorisation is permission from the person or organisation entitled to grant it. Scope defines exactly which systems, actions, times and conditions that permission covers.'),
   p('Owning a phone lets you manage that phone. It does not automatically let you test the mobile provider, a shared school network or another person’s account. Being able to open a website is permission to use its public pages, not permission to perform security tests on its infrastructure.'),
   p('A useful learning agreement says: these named sample files or lab systems; these permitted actions; this time window; these limits; this contact if something unexpected happens. If a boundary is unclear, stop that action and clarify it. Keeping the scope precise helps the test produce useful results.'),
   term('Learning lab','A deliberately chosen practice environment with permission, boundaries and a recovery plan. Its purpose is to make experiments understandable and manageable.'),
   h('2. Start with a small, harmless lab'),
   p('For Week 1, a folder of invented documents and account examples is enough. Create a fictional asset list, a fictional sign-in record and a spare copy of a sample document. Label everything as practice data. Discuss the risks and recovery steps without contacting real targets or collecting other people’s information.'),
   p('Separate learning files from important work. Decide which sample files may be edited and which are the original reference copies. Check that you can replace the practice files from the reference set. Learning cybersecurity does not require installing attack tools on your everyday computer today.'),
   term('Virtual machine (VM)','A software-based computer running within another computer. It can provide a separate operating system for later practice. It still depends on the host computer and its configuration.'),
   term('Snapshot and isolation','A snapshot records a VM state for returning to that state later. Isolation means restricting interaction with other systems. A VM is not automatically isolated: network settings, shared folders and copied data affect its boundaries.'),
   p('A snapshot can help undo a lab change, but it is not a substitute for an independent backup of valuable data. If its host drive is lost, the VM and its snapshots may be lost together. We will set up operating-system practice more carefully in Week 3; no VM is required to understand this week.'),
   h('3. Write an observation, not a dramatic conclusion'),
   term('Log and timestamp','A log is a recorded sequence of events. A timestamp states when an event was recorded or occurred, according to the recording system. Logs contain observations that need context.'),
   p('Imaginary record: 09:00 — student account sign-in succeeded; 09:05 — another sign-in failed; 09:10 — the student saved a document. You can say a failed attempt was recorded at 09:05. You cannot yet say a particular person attacked the account. The account, device, time accuracy and other evidence matter.'),
   p('A clear beginner report has four parts: observation, possible significance, uncertainty and next check. Example: a failed attempt is recorded; it may deserve review; its source is unknown; compare it with the student’s expected activity. This style helps someone act without mistaking a guess for a fact.'),
   h('4. Where Python helps security work'),
   term('Automation','Using software to repeat a defined task consistently. In security work, this may mean organising existing observations or generating a report.'),
   p('Python can read permitted sample records, group repeated entries, sort events by time and produce a summary. It can also help keep an asset inventory consistent. This saves repetitive work and makes gaps easier to see.'),
   p('The judgement remains yours. A script can count failed logins, but it cannot infer the person’s intent from a count alone. Wrong input, missing records or a wrong rule can produce a misleading report. Understand the source and the question before trusting the result.'),
   p('Your course remains cybersecurity first. We are discussing Python’s supporting role, not turning today into a programming assignment. Later, when the security concept is clear and the Python prerequisites are taught, a small authorised automation may help apply it.'),
   key('A good lab has permission, exact boundaries, invented or permitted data, and a way to recover. A good report separates observations from conclusions.')
  ],
  checks:[
   check('You own a laptop connected to school Wi-Fi. Does that authorise testing every device on the network?','No. Permission over your laptop does not give permission over other devices or the school’s network.','Authorisation must cover the specific system and action. Shared connectivity is not shared permission.'),
   check('What should a Week 1 lab contain if you are not ready to install new software?','A separate folder with invented assets, sample event records, reference copies and a clear list of permitted changes.','You can learn scope, risk and reporting through these examples. Tools come after the underlying concepts.'),
   check('Python reports five failed sign-ins. Can you identify an attacker from that number alone?','No. You need context and additional evidence.','The number is an observation. A report should explain what remains unknown and what to check next.')
  ],
  reflection:'Write your practice scope in four lines: allowed material, allowed actions, excluded systems, and recovery method. Then write one observation with an uncertainty.'
 },
 '1.7':{
  objective:'Connect the week’s concepts in one case, explain your decisions, and identify what needs another review before Week 2.',
  sections:[
   h('1. Recall before rereading'),
   p('Close or cover the explanations for a moment. Describe cybersecurity, an asset and the three CIA goals in your own words. Then explain the difference between a threat, a vulnerability, a risk and a control. If a definition is difficult, revisit that part rather than memorising a sentence without understanding it.'),
   p('Use these prompts: What matters? Who may access it? Which changes are appropriate? Can it be used when needed? What could cause harm? What weakness contributes? How serious would the consequences be? Which action reduces them? This sequence turns a collection of terms into a way of thinking.'),
   key('Understanding means being able to apply an idea to a new example and explain why it fits.'),
   h('2. A complete fictional case'),
   p('Maya studies on a laptop. Her course is publicly hosted, but her personal notes are saved in the browser. She uses email to recover her learning account. She has exported one backup to the laptop’s only drive. A message claims that her account will close unless she signs in immediately. Later, she sees one failed sign-in in the real account activity page.'),
   p('Pause here. There are several assets and observations, not one proven attack. The course’s public source, Maya’s local notes, her email and her backup have different locations and access rules. Her backup shares a device dependency with the original. The suspicious message and failed sign-in deserve attention, but the case does not say she entered a password or that a sign-in succeeded.'),
   p('Before reading the answers, write your analysis in the Day Notes box: assets; CIA concerns; potential threats; known weaknesses; observations; unknown facts; controls; and recovery. Keep your answer tied to what the case actually says.'),
   h('3. Review the week without skipping the connections'),
   p('Day 1: map device, software, data and services.\nDay 2: identify assets, dependencies and CIA goals.\nDay 3: describe threats, weaknesses, consequences and controls.\nDay 4: distinguish malware, deception and data exposure.\nDay 5: connect prevention, detection, response and recovery.\nDay 6: define permission, scope, lab boundaries and careful reporting.'),
   p('Check common confusions: data being unavailable does not prove theft; an authorised correction can improve integrity; a vulnerability does not prove exploitation; phishing does not require malware; sync does not automatically provide a recoverable backup; a VM does not automatically isolate every action; a script’s output is not a substitute for evidence.'),
   h('4. Explain a simple protection plan'),
   p('Choose a fictional study project. Name its important data and dependencies. Decide who should read or change it. Describe one realistic harmful event, one weakness and the likely consequence. Choose a control that addresses that particular concern. Add a way to notice problems and a way to recover. Explain each choice in one sentence.'),
   p('For example, a separate recoverable copy addresses loss of the original. Restricted edit access addresses unwanted changes. Checking a suspicious request through a known route addresses deception. The point is to connect the measure to its purpose rather than collecting unrelated tools.'),
   p('Python could later organise the inventory or summarise sample event records. It would support the plan, while permission, priorities and interpretation remain human decisions. Do not add programming work merely to make a security lesson look advanced.'),
   h('5. Readiness for Week 2'),
   p('You are ready to continue when you can explain the case, justify a control and admit what is unknown. You do not need perfect vocabulary or knowledge of network addresses yet. Week 2 introduces how clients, servers and networks carry information; today’s system map gives those ideas a place to fit.'),
   tip('Review gently: try the questions from memory, reveal the answers, correct one misunderstanding and rest. Return to the questions later and use a different example. Recalling and explaining is more useful than repeatedly staring at definitions.')
  ],
  checks:[
   check('Case: name four assets and one dependency.','Assets include Maya’s notes, laptop, email, learning account and backup. Account recovery depends on email. The local notes and local backup also depend on the laptop’s storage.','An asset can be information, an account, a device or a service. A dependency explains why one failure can affect more than one asset.'),
   check('Case: which CIA goals matter for the notes?','Confidentiality: only intended people should read private notes. Integrity: notes and progress should remain accurate. Availability: Maya should be able to use them and recover from loss.','CIA goals can all apply to the same information. Identify concrete consequences instead of selecting only one letter.'),
   check('Case: what do the suspicious message and failed sign-in prove?','The message makes a suspicious request, and the account records a failed attempt. Neither alone proves successful account takeover.','Check through independent trusted routes and compare activity with expected use. State the evidence separately from possible explanations.'),
   check('Case: why is the existing backup incomplete protection?','It shares the laptop’s only drive with the original. A failure or loss of the drive can remove both.','Recovery needs a suitably separate, protected copy and a checked restore process. A duplicate on the same failing storage is a shared dependency.'),
   check('Case: connect one control to one weakness.','Use a separate recoverable backup to reduce the impact of drive loss, or use a unique account password to limit harm from password reuse if that weakness is present.','The case states the backup weakness. It does not state password reuse, so label the latter as a conditional example rather than inventing a fact.'),
   check('Explain prevention, detection, response and recovery in order of purpose.','Reduce the chance of harm; notice possible trouble; investigate and limit harm; restore trustworthy access and information.','The activities can overlap. You need all four purposes, not a rigid timeline.'),
   check('Your course is public. Does that automatically make your local notes public?','No. Published website source and locally stored user data are different. Backups, sync settings and device access must be considered separately.','Use the storage map. Real secrets in published source would be exposed, but that is a different claim from all browser notes being public.'),
   check('What permission would you need before testing a classmate’s account?','Explicit permission covering the account, allowed actions and limits from someone entitled to grant it, plus any required service rules.','A classmate sharing a link or using the same Wi-Fi is not sufficient permission. Practise with your defined lab instead.'),
   check('A Python report labels every failed login an attack. What is wrong with its conclusion?','The rule turns an observation into a conclusion without enough context.','Revise the report to show recorded failures, possible significance, uncertainty and the next check.'),
   check('Final teach-back: explain how you would protect a fictional project in five sentences.','Name the asset and its value. State a realistic threat and weakness. Describe consequences using CIA. Choose a relevant control and observation. Explain response and recovery within your permitted scope.','Many answers are valid. Judge yours by clear reasoning, evidence, permission and whether your controls address the stated problem.')
  ],
  reflection:'Write what you can now explain, which two ideas need review, and one question to carry into Week 2. Return later and answer the case again without reading your old answer.'
 }
};
