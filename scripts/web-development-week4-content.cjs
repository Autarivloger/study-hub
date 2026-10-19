const {p,key,tip,warn,term,code,out,mistake,page,lesson}=require('./web-development-teaching-tools.cjs');
const repaired=page("My repaired notebook","    <!-- Goals for today's practice -->\n    <h1>My repaired notebook</h1>\n    <p id=\"goal\" title=\"My learning goal\">I will check one change at a time.</p>\n    <p>I can reopen the saved file.</p>");
const comments=page("Comment practice","    <!-- Main introduction -->\n    <h1>My practice notebook</h1>\n    <p>I can read visible content and source notes separately.</p>\n    <!-- Next session: add another paragraph about my progress. -->");
const lessons={},add=(day,d)=>lessons['4.'+day]=lesson(4,day,d);
add(1,{
 title:"Reading documentation",objective:"Use an HTML reference to answer a small question and distinguish examples, requirements and optional choices.",
 parts:[
 ["Begin with a specific question",[
  p("Documentation is easier to use when you know what you are asking. Instead of searching how to make a website better, ask: Does p allow another p inside it? Or: Which attributes can meta use for an encoding declaration? You already know enough HTML to ask useful questions."),
  term("Documentation and reference","Documentation explains a tool or language. A reference describes a particular feature, such as one element, its attributes and allowed content. A tutorial teaches through a sequence. Use the kind of page that matches your question."),
  code("Question: What belongs inside a paragraph?\nKnown term: p element\nNeeded evidence: allowed content and an example\nNext step: compare the rule with my saved source"),
  p("MDN and the HTML Standard are useful reference sources. When online, use their search for the exact element name and confirm that you are reading HTML, not a similarly named API or another language. The lesson explains the needed facts offline; external reference pages require internet."),
  key("Write the question before opening more tabs. A narrow question gives you a way to decide when you have enough information.")
 ]],
 ["Read the rule before copying the example",[
  term("Content model","The rule describing what content an element can contain. A short reference may use formal categories. Translate unfamiliar terms into concrete examples rather than skipping them."),
  p("For our current elements: a paragraph can contain text and suitable inline phrasing content, but not another paragraph or a heading. You do not need to memorise every HTML category today. Check the rule needed for the actual element you are using."),
  code("Reference-reading notebook:\nFeature: p\nMy question: Can p contain another p?\nRule in my words: No; make separate paragraphs.\nTiny example: <p>One.</p><p>Two.</p>\nHow I checked: source review and browser inspection."),
  p("An example often contains choices that are not requirements. The sample title, filename and sentence are usually replaceable. By contrast, the requirement that meta is void is a syntax rule. Ask which parts demonstrate the feature and which parts are merely example content."),
  term("Deprecated and experimental","Deprecated features are discouraged for new work. Experimental features may still change or lack support. Prefer established beginner features in this course.")
 ]],
 ["Test one idea in your own file",[
  p("Create reference-check.html in your practice folder with the familiar full shell. Add the smallest fragment needed to answer the question. Predict the result, save, open and compare. This keeps a copied large page from hiding what you are trying to learn."),
  code("<h1>A reference check</h1>\n<p>First thought.</p>\n<p>Second thought.</p>","html"),
  out("One main heading followed by two separate paragraphs."),
  warn("Examples from forums or pages can contain scripts and network requests. Do not paste unknown Console commands or private credentials. For today's HTML checks, plain markup in your own practice file is enough."),
  p("When online documentation is unavailable, use the definitions and completed examples from Weeks 1–3. Record the unresolved reference question in notes and verify it later. Do not invent a rule just to complete the day.")
 ]]
 ],
 practice:[
  ["Turn this into a narrow documentation question.","My HTML is weird.","For example: Can p contain an h1?","Name the feature and the behaviour you need to check."],
  ["Choose a useful page type.","You need the attributes of the meta element.","An HTML meta reference.","A long framework tutorial is unlikely to answer the narrow question efficiently."],
  ["Separate rule from sample choice.","<title>Sam's notebook</title>","title belongs in head; the sample wording Sam's notebook is replaceable.","Examples contain both syntax and incidental content.","html"],
  ["What should you do with an unfamiliar formal term?","A reference says phrasing content.","Look up the term and connect it with small allowed/disallowed examples.","Do not assume all nested elements are permitted."],
  ["What would you record after checking a rule?","You verified separate p elements.","The question, rule in your words, tiny example and result.","A notebook makes the knowledge reusable."]
 ],
 challenge:["Build one reference card","Choose p, title or meta. Write a precise question, a rule in your words, an example and a check. If offline, use prior lessons and label the external verification pending.","Feature: meta\nQuestion: Does it need an end tag?\nAnswer: No; it is void.\nExample: <meta charset=\"utf-8\">\nCheck: compare source with the Week 3 shell.","Record an external source title/URL when you actually use it. Do not report a visit you did not make."],
 ready:"Ask a focused question, locate the right feature reference and distinguish a requirement from replaceable example text.",
 reflection:"Save your reference card and one unfamiliar term you resolved. Which part of the sample could you safely personalise?",
 quiz:[
  ["Which is a focused reference question?","Can p contain h1?","How do I learn all coding instantly?","Why is everything bad?","A specific element question can be checked."],
  ["What does a content model describe?","Allowed element contents","The website's price","The browser password","It constrains what may be nested."],
  ["Which part of a title example can usually change?","Its meaningful text","Its required location in head","Its closing-tag name","Sample wording is not a syntax requirement."],
  ["Which source type lists an element's attributes?","A reference page","Only a screenshot","Only the file icon","References describe feature details."],
  ["What should follow reading a rule?","A small prediction and check","Copying an unrelated whole site","Deleting the project","Testing a tiny example connects rule and evidence."],
  ["What does deprecated suggest for new beginner work?","Prefer an established supported alternative","Use it everywhere first","It is always a secret feature","Deprecated features are discouraged for new use."]
 ]});
add(2,{
 title:"HTML comments",objective:"Write useful source comments, explain their visibility and avoid malformed or nested comments.",
 parts:[
 ["A note for a source reader",[
  term("HTML comment","A source annotation written between <!-- and -->. Its contents are not ordinary rendered page text, but they remain in delivered source and can be inspected."),
  p("Comments can explain intent or remind your future self of a next step. Keep visible instructions in real page content. A reader should not need to inspect source to discover essential information about an article."),
  code("<!-- Main introduction -->\n<h1>My practice notebook</h1>\n<p>I am learning to review source.</p>","html"),
  out("Visible page: heading and paragraph.\nThe comment text is not displayed as ordinary page text."),
  p("Read the delimiters aloud: less-than, exclamation mark, two hyphens; then two hyphens and greater-than to finish. HTML comments are different from Python # comments and JavaScript comment syntax.")
 ]],
 ["Explain why, keep the note useful",[
  code("<!-- Keep this wording short so a new learner can understand it. -->\n<p>One change, then one check.</p>","html"),
  p("A useful comment explains a decision or a real next step. A comment saying paragraph starts here before every p repeats what the tag already says. Long, stale comments can become misleading. Update or remove an outdated comment when you change the source it describes."),
  term("TODO source note","A common convention for an unfinished task, such as <!-- TODO: add a second example. -->. TODO has no special HTML behaviour; it is simply text inside a comment."),
  code("<!-- TODO: add my next study goal after reviewing it. -->","html"),
  warn("Comments are not a private storage area. Never put passwords, tokens or private personal notes in public HTML comments. Hiding text from normal rendering does not hide it from visitors.")
 ]],
 ["Keep the boundaries clear",[
  p("Do not nest comments inside comments. Use separate complete comments. For beginner safety, avoid double-hyphen sequences inside the comment text and make sure the closing delimiter is present. A missing closing delimiter can make later source disappear from normal rendering."),
  mistake("<!-- First note <!-- second note --> -->","<!-- First note -->\n<!-- Second note -->","HTML comments do not nest. Use separate complete comments."),
  code("<!-- A note can span\n     more than one source line. -->\n<p>This paragraph remains visible.</p>","html"),
  p("Temporarily commenting out a whole block can help in some debugging situations, but do not hide study content as a substitute for fixing structure. First keep a working copy and change one small thing."),
  key("A comment is source-visible, normally display-hidden, and structurally bounded. Use it to explain useful intent.")
 ]]
 ],
 practice:[
  ["Write a source note.","Note: add another example next session.","<!-- Add another example next session. -->","Use the HTML comment delimiters.","html"],
  ["Predict normal visible text.","<!-- Private? No. -->\n<p>Hello.</p>","Hello.","The comment stays in source but is not ordinary visible text.","html"],
  ["Is this a secret store?","<!-- token goes here -->","No. Delivered comments are readable in source.","Do not place a real credential there.","html"],
  ["Repair nested comments.","<!-- A <!-- B --> -->","<!-- A -->\n<!-- B -->","Use separate comment blocks.","html"],
  ["Explain TODO.","<!-- TODO: improve my title. -->","A human reminder; it does not run a task.","The browser treats it as comment text.","html"]
 ],
 challenge:["Add two useful notes","Add a brief intent comment and one future-work comment to a practice document. Confirm that both are visible in source but absent from the ordinary displayed text.","<!-- Keep the introduction welcoming for a beginner. -->\n<h1>My learning notebook</h1>\n<!-- TODO: add another paragraph after the next practice session. -->","Keep the comments accurate. The real heading remains ordinary visible content.","html","My learning notebook"],
 ready:"Write and close comments correctly, explain their visibility and keep credentials out of them.",
 reflection:"Save one useful comment and explain why it helps a future reader. What would make it stale?",
 quiz:[
  ["Which opens an HTML comment?","<!--","//","#","HTML has its own comment delimiters."],
  ["Which closes it?","-->","</comment>","##","Both boundaries matter."],
  ["Can visitors inspect delivered comments?","Yes","No, never","Only the author","Source visibility differs from normal rendering."],
  ["Should comments nest?","No","Yes, without limits","Only on phones","Use separate comment blocks."],
  ["Does TODO automatically execute?","No","Yes","Only in head","It is a writing convention."],
  ["Which comment is useful?","A brief reason for a non-obvious decision","A real password","A paragraph starts here before every p","Explain helpful intent and avoid private data."]
 ]});
add(3,{
 title:"Inspecting page structure",objective:"Compare saved source and live DOM, select an element and explain a discrepancy without assuming that developer tools saved the file.",
 parts:[
 ["Choose the right representation",[
  p("Open a practice file in your editor and browser side by side. The editor shows the saved source, plus any unsaved changes in its buffer. The browser has a parsed live document. They are related representations, but they answer different questions."),
  term("Source versus live DOM","Source is the markup supplied to the browser. The DOM is the browser's current tree after parsing and any later changes. It may contain inserted or repaired structure."),
  term("Text node","A piece of text within the document tree. An element such as p can contain a text node. Indentation whitespace can also create text nodes even though it does not appear as separate visible paragraphs."),
  code("Source question: What did I actually save?\nDOM question: What structure does the browser currently have?\nDisplay question: What is the reader seeing?"),
  p("Use your editor to inspect the exact local source. For your own local page, View page source may also help. For complex generated or changing sites, do not assume every source view proves exactly what an earlier network response contained.")
 ]],
 ["Select and follow parents",[
  p("Right-click a paragraph in your practice page and choose Inspect. In Elements, find the highlighted p row. Expand its parent body and locate the neighbouring h1. Browsers differ in the highlighting and breadcrumbs shown."),
  code("<body>\n  <h1>Inspection practice</h1>\n  <p id=\"evidence\">I can find this paragraph.</p>\n</body>","html"),
  out("Target: p with id evidence\nParent: body\nSibling: h1"),
  p("Select text inside the p to see that the sentence belongs to the paragraph. Do not confuse the word appearing inside a text node with an attribute name. The id is element information in the opening tag."),
  tip("The element-selection pointer in DevTools can help when a page has many elements. Keep experiments on your disposable practice page.")
 ]],
 ["Investigate a mismatch",[
  code("Saved fragment:\n<p>First.<p>Second.</p></p>\n\nQuestion: Does the DOM really show one p inside another?","text"),
  p("HTML does not allow nested paragraphs. A browser can close the first p when it encounters another. Exact recovery can create extra nodes. Use Elements to observe your browser's result; then fix the source into two explicit sibling paragraphs."),
  mistake("<p>First.<p>Second.</p></p>","<p>First.</p>\n<p>Second.</p>","Correct the source rather than accepting parser recovery as your intended structure."),
  p("If the source and DOM differ, consider parsing recovery, temporary tool edits and page scripts. Check your exact file and reload. Do not assume every difference is caused by JavaScript; even plain HTML parsing can explain a mismatch."),
  key("Compare source, current tree and display. Each supplies evidence; none should be confused with the others.")
 ]]
 ],
 practice:[
  ["Which view answers this?","Did I save lang=\"en\" in the local file?","Open the exact file in the editor.","The DOM alone may include parser-created structure."],
  ["Which view answers this?","What is the paragraph's current parent?","Elements/live DOM.","That shows the current tree."],
  ["Name the text node content.","<p>Inspect me.</p>","Inspect me.","The p element contains that text.","html"],
  ["Explain an extra DOM node.","Invalid paragraph nesting led to an unexpected empty p.","The parser may have repaired the malformed source.","Correct the source and compare again."],
  ["Persist the fix.","You edited a DOM node to look right.","Make the corresponding correction in the saved source and reload.","A normal DOM edit is temporary."]
 ],
 challenge:["Create an evidence comparison","Save a small correct practice document, select its paragraph in Elements and record parent/sibling/text. Then compare an intentionally malformed paragraph fragment and repair the saved source.","Correct case: p is a child of body; h1 is its sibling.\nMalformed case: observe recovery; do not assume nested p survives.\nRepair: two explicit sibling paragraphs.\nFinal check: save, reload, inspect again.","Write observed results only if you performed the experiment. Otherwise label your explanation as a prediction."],
 ready:"Select an element, trace its relationship and explain at least two reasons the live tree can differ from source.",
 reflection:"Record your source/DOM comparison. Which result was observed, and which was inferred?",
 quiz:[
  ["Which describes the live DOM?","The current parsed document tree","Always the exact saved bytes","Only the file path","Parsing and later actions can change the tree."],
  ["Can a parser insert structure?","Yes","No","Only if Python runs","HTML recovery can create or rearrange nodes."],
  ["What is a text node?","A text piece in the tree","Always an attribute","The server computer","Elements can contain text nodes."],
  ["Does every source/DOM difference prove JavaScript ran?","No","Yes","Only with paragraphs","Parsing or temporary edits can also explain it."],
  ["How do you keep a repair after reload?","Save the corrected source","Only change Elements","Only rename the tab","Ordinary DOM edits are not a saved-file change."],
  ["Which statement is careful?","I observed this parent in Elements","The DOM always proves my original source","No Console error proves valid markup","State the evidence and its limits."]
 ]});
add(4,{
 title:"Finding basic mistakes",objective:"Use a layered checklist to find filename, path, spelling, quoting and structure mistakes without replacing a working document.",
 parts:[
 ["Check the file before the markup",[
  p("A correct paragraph in the wrong file does not fix the page you are viewing. First compare the browser address with the editor's full file location. Then check the real extension and saved state. This often solves a problem before any HTML change is needed."),
  term("Symptom and cause","A symptom is what you notice, such as the old heading remaining visible. A cause is the actual reason, such as editing another file. Several causes can produce the same symptom."),
  code("Symptom: old heading still visible.\nPossible causes:\n- Unsaved edit\n- Wrong file or browser tab\n- Wrong local path\n- Hosted version not published yet\n- Cached response"),
  p("Use evidence to narrow the cause. For a local practice page, confirm the path and save/reload first. For a hosted page, compare the published resource/version; a successful local save does not publish it."),
  key("Write the symptom precisely before deciding which file or component to change.")
 ]],
 ["Read small syntax details",[
  code("Check names: h1 versus hl\nCheck closing tags: </h1> versus </p>\nCheck quotes: title=\"My goal\"\nCheck duplicate ids\nCheck root language: ja for Japanese, ne for Nepali, en for English"),
  mistake("<p title=My goal>I practise.</p>","<p title=\"My goal\">I practise.</p>","Unquoted spaces split the intended attribute value."),
  mistake("<h1>My goal</p>","<h1>My goal</h1>","Matching names matter even if the browser displays a large heading."),
  p("An omitted language or viewport setting may not stop a page displaying. It can still fail a project requirement or reduce usability. Separate a syntax defect from a missing quality/accessibility requirement."),
  term("Validation","Checking markup against language rules. An HTML checker can help identify errors, but it does not judge whether your writing is useful or every design decision is good.")
 ]],
 ["Use checks with limits",[
  p("When online you can use the W3C Nu HTML Checker with a disposable nonprivate example. Do not upload private pages or tokens. Offline, compare your saved document against the full shell and inspect the tree; online validation is a useful extra check, not a condition for reading these lessons."),
  code("Audit order:\n1. Correct file and saved state\n2. Expected visible result\n3. Tag names and matching pairs\n4. Quotes and attributes\n5. Allowed nesting and document regions\n6. Language, encoding, viewport and useful title"),
  p("If a checker reports several issues, fix the first structural problem and run it again. One malformed quote or boundary can create confusing later messages. Keep each original sentence unless changing it is part of the intended task."),
  tip("A missing optional attribute is not automatically invalid HTML. Explain whether a rule is required by HTML itself or by your course project's quality checklist."),
  key("Find the smallest supported cause. Preserve the rest of the document while checking your correction.")
 ]]
 ],
 practice:[
  ["Choose the first check.","Editor: drafts/index.html\nBrowser: first-page/index.html","Confirm and open the intended same path.","Identical filenames can hide different files."],
  ["Find the split value.","<p title=My study plan>Text</p>","Quote title=\"My study plan\".","The spaces need to remain in one value.","html"],
  ["Find the similar-looking character.","<h1>Goal</hl>","Replace the letter l with digit 1 in </h1>.","Read names carefully.","html"],
  ["Does no viewport prove HTML cannot display?","A simple page has no viewport meta.","No. It may display but fail mobile quality expectations.","Rendering and meeting requirements are different."],
  ["Should a checker receive a page containing a real token?","You want to paste the entire source online.","No. Use a nonprivate minimal example.","Do not submit credentials to a public validation service."]
 ],
 challenge:["Audit a copy, keep the original","Copy your own practice page to audit.html. Introduce and repair one filename/path mismatch, one tag typo and one attribute quoting error. Write a reason for each fix.","Path: open the same actual file in editor and browser.\nTag: use </h1> to close h1.\nAttribute: quote title=\"My study plan\".\nRetest: save, reload and inspect source.","Keep the working original for comparison. Do not introduce mistakes into Study Hub."],
 ready:"Use the checklist to distinguish wrong-file problems, syntax errors and missing quality settings.",
 reflection:"Record one symptom with two plausible causes. What evidence would distinguish them?",
 quiz:[
  ["What is a symptom?","The old heading is still visible","Always the exact cause","The same as a password","An observation needs investigation."],
  ["Which should you check early?","Exact editor and browser paths","Install a new framework","Delete the project","Wrong-file edits can mimic markup failure."],
  ["Which closes h1 correctly?","</h1>","</hl>","</p>","Names must match."],
  ["Does missing viewport necessarily prevent display?","No","Yes","Only on desktop","It can be a usability/quality issue even if content appears."],
  ["Can a validator decide whether your explanation is helpful?","No","Yes, completely","Only if the title is short","Rule checking and teaching quality differ."],
  ["How should several checker errors be approached?","Fix an early structural cause, then check again","Rewrite everything at once","Ignore all errors","One cause can trigger later diagnostics."]
 ]});
add(5,{
 title:"Small-step debugging",objective:"Record expected and actual behaviour, test one hypothesis at a time and verify a persistent repair.",
 parts:[
 ["Make the problem reproducible",[
  term("Debugging","The process of finding, understanding and correcting a defect. Good debugging gathers evidence instead of repeatedly changing unrelated lines."),
  term("Reproduction steps","The sequence of actions that produces a symptom. A useful record includes the file, action, expected result and actual result."),
  code("File: practice/index.html\nSteps: edit h1, save, refresh the same browser tab.\nExpected: heading says My revised goal.\nActual: heading still says My old goal."),
  p("Do not write it does not work. That gives you no comparison. Name the exact text or structure that should change. If the issue occurs only sometimes, note the circumstances rather than claiming it always happens."),
  p("Before editing, keep a copy of the working source or use your editor's undo/history. You do not need Git commands for this week. A clearly named backup copy is enough for these small disposable files.")
 ]],
 ["Form and test one hypothesis",[
  term("Hypothesis","A possible explanation that you can test. For example: I am viewing another index.html. A useful test could confirm or weaken that explanation."),
  code("Hypothesis: wrong file.\nTest: compare the full editor path and browser address.\nEvidence: paths differ.\nChange: open the intended saved file.\nRetest: heading now matches."),
  p("Change one relevant thing at a time. If you edit the title, rename the folder and remove metadata together, a successful result will not tell you which change mattered. A failed result may contain new mistakes."),
  p("When a test fails, record it. That is useful evidence, not wasted work. Return unrelated trial changes to the prior state so your next test starts from a known source."),
  key("Hypothesis → test → observation → focused change → retest. State why the evidence supports the fix.")
 ]],
 ["Verify beyond the first visible success",[
  term("Regression check","Checking that a change did not break a previously working behaviour. For our page, verify that the other paragraph, title and metadata remain intact."),
  code("After the fix:\n[ ] Expected result now appears\n[ ] Exact saved file retains the fix\n[ ] Reload still works\n[ ] Other content is present\n[ ] Source structure remains understandable"),
  p("A temporary Elements edit can show the desired result without persisting it. Save the real source and reload. Also inspect the surrounding content: a missing comment delimiter can hide half a page while the first heading still looks correct."),
  tip("When asking for help, share a small nonprivate example, your reproduction steps and the tests already tried. Remove private values; never send passwords or tokens."),
  p("If the problem is outside the HTML layer, say so. A hosted deployment still waiting to publish needs publication evidence; rewriting local paragraphs does not advance that remote job.")
 ]]
 ],
 practice:[
  ["Improve the report.","My page is broken.","After saving practice/index.html and refreshing that tab, I expected New goal but saw Old goal.","Specific action and result make a test possible."],
  ["Choose a test for the hypothesis.","Hypothesis: I edited the wrong file.","Compare full paths and reopen the intended file.","The test targets the proposed cause."],
  ["Why avoid five simultaneous edits?","You want to know which fix mattered.","Multiple changes hide cause and effect and may add new defects.","Controlled changes make evidence clearer."],
  ["What verifies persistence?","The heading looks right after a DevTools edit.","Save the source, reload and reopen it.","A live edit alone is temporary."],
  ["Name a regression check.","You repaired h1.","Check that the paragraph and title still exist and are correct.","Preserve surrounding working content."]
 ],
 challenge:["Write a complete debugging log","Choose one harmless error in audit.html and document the full process from symptom to regression check. Explain one hypothesis that did not fit the evidence.","Expected: title My notebook.\nActual: title Untitled.\nHypothesis: title source unchanged.\nTest: inspect saved head.\nFix: change title text, save.\nRetest: tab now My notebook after reload.\nRegression: h1 and paragraphs unchanged.","Your log should be short enough to follow but detailed enough for someone else to repeat."],
 ready:"Write a reproducible report, test a relevant hypothesis and verify both the fix and surrounding content.",
 reflection:"Save your debugging log. Which test gave the clearest evidence, and what did you avoid changing?",
 quiz:[
  ["Which report is most useful?","Exact steps plus expected and actual results","It is weird","Nothing ever works","Specific comparisons support diagnosis."],
  ["What is a hypothesis?","A testable possible explanation","A guaranteed fact without evidence","A filename extension","Test it rather than treating it as proven."],
  ["Why make one relevant change?","To understand cause and effect","To make learning slower","Because two lines are forbidden","Controlled tests isolate causes."],
  ["What is a regression check?","Check that previous working content still works","Only rename the folder","Erase all history","A fix should preserve surrounding behaviour."],
  ["What should follow a visible repair?","Save, reload and verify persistence","Stop without checking the file","Only take a screenshot","A temporary display state is insufficient."],
  ["What belongs in a help request?","Small nonprivate example and tests tried","A real token","Only an angry screenshot","Evidence enables useful help without exposing secrets."]
 ]});
add(6,{
 title:"Repair a broken page",objective:"Repair a prepared document and wrong-file scenario in small steps, retaining its learning content and recording evidence.",
 parts:[
 ["Prepare a safe repair exercise",[
  p("Create repair-lab.html in your practice folder using the complete shell from Week 3. Keep a working copy. Use the deliberately broken body fragment below in the lab copy only. The content is supposed to be one main heading and two separate paragraphs."),
  code("<h1>My repaired notebook</p>\n<p id=\"goal\" title=My learning goal>I will check one change at a time.\n  <p id=\"goal\">I can reopen the saved file.</p>\n</p>","html"),
  p("Expected meaning: one h1; first paragraph with a unique goal id and full advisory title; second sibling paragraph without a duplicate id. The source contains several errors even if a browser displays the sentences."),
  code("Also simulate this location problem:\nEditor file: practice/repair-lab.html\nBrowser tab: practice/old-copy/repair-lab.html\nFirst action: align the file locations before judging repairs."),
  key("Keep both sentences. The task is to repair their structure, not delete the difficult part.")
 ]],
 ["Repair with a log",[
  p("First correct the location mismatch. Then fix the h1 closing name, quote the full title value, make the paragraphs siblings and remove the duplicate id. Save and reload after each focused change. Use the same file throughout."),
  code("<h1>My repaired notebook</h1>\n<p id=\"goal\" title=\"My learning goal\">I will check one change at a time.</p>\n<p>I can reopen the saved file.</p>","html"),
  out("One main heading and two separate paragraphs, preserving both original sentences."),
  p("Compare the editor source and live DOM. Browser recovery may have made the broken version look similar, so use the intended tree as evidence too. A repair can improve correctness without dramatically changing pixels."),
  code("Log columns:\nSymptom or source defect | hypothesis/check | one change | retest result")
 ]],
 ["Finish the document audit",[
  p("Put the repaired body in a complete document. Check root language en, early UTF-8, standard viewport and a meaningful title. Add a useful comment above the goal if you want to practise comments. Do not add secret values."),
  code(repaired,"html"),
  p("Close and reopen the saved file. Confirm one h1 and two p elements, unique id goal, the correct title attribute value and unchanged sentence text. Verify that your original working files still exist."),
  tip("If tools are unavailable, perform the source audit and draw the intended tree on paper. Later repeat the browser observation rather than claiming a tool result you did not see."),
  key("A successful repair has a reason, preserved content, a persistent saved result and a regression check.")
 ]]
 ],
 practice:[
  ["Fix the heading boundary.","<h1>My repaired notebook</p>","<h1>My repaired notebook</h1>","The end tag matches the heading.","html"],
  ["Fix the advisory phrase.","title=My learning goal","title=\"My learning goal\"","Quotes keep the full phrase as one value.","html"],
  ["Fix the duplicate identifier.","Two p elements both have id=\"goal\".","Keep goal on one; remove or change the other id.","An id must identify one element in this document."],
  ["Fix the structure.","One p is inside another p.","Use two explicit sibling paragraphs.","Do not delete either sentence."],
  ["What comes before checking the repair?","Browser and editor show different paths.","Open the same intended file.","The right fix in another file will not change this tab."],
  ["What should the final log prove?","All repairs are done.","Each change addressed evidence, persisted and preserved other content.","A list of guesses is not a completed debugging account."]
 ],
 challenge:["Submit the repaired notebook","Rebuild the corrected full file from your own attempt, then compare with the supplied repaired example. Retain a four-row repair log and one wrong-file diagnosis.",repaired,"The document retains the two original learning sentences. Correctness is checked through structure, attributes, persistence and file identity.","html","Tab: My repaired notebook\nHeading: My repaired notebook\nTwo original paragraphs remain visible."],
 ready:"Explain every repair, prove the saved result survives reload and show that the original learning content was retained.",
 reflection:"Save the repair log. Which defect changed the DOM most, and which was mainly a source-quality issue?",
 quiz:[
  ["Which fix should happen first if paths differ?","Open the intended same file","Change every tag","Delete the old heading","File identity is necessary to interpret later tests."],
  ["Which closing tag repairs the heading?","</h1>","</p>","</title>","Match the start tag."],
  ["How should the title phrase be written?","title=\"My learning goal\"","title=My learning goal","title==My goal","Use one equals sign and quoted value."],
  ["How should the two paragraphs relate?","Siblings","Nested p inside p","Attributes of h1","Separate thoughts use separate sibling paragraphs."],
  ["What should happen to the duplicate id?","Keep it unique or remove the unnecessary duplicate","Ignore it because display looks fine","Add the same id to h1 too","Identifiers must be unambiguous."],
  ["What must the repair preserve?","Both original learning sentences","Only the first heading","Only the icon","The goal is focused repair while retaining content."]
 ]});
add(7,{
 title:"Week 4 review and troubleshooting workshop",objective:"Find and explain several beginner HTML mistakes using evidence, documentation and focused repairs.",
 parts:[
 ["Recall your debugging process",[
  p("Write the process from memory: observe, reproduce, hypothesise, test, change, retest and check surrounding content. Then add the early checks for exact file path and saved state. You are practising a repeatable method rather than memorising one repaired file."),
  code("Expected:\nActual:\nReproduction steps:\nHypothesis:\nTest/evidence:\nFocused change:\nRetest:\nRegression check:"),
  p("Keep the original source for comparison. Try the workshop before revealing answers. For a mistake, write one sentence about the cause and one about the test that would confirm the fix."),
  term("Minimal reproduction","A small example that still demonstrates the problem. It removes irrelevant material for investigation while keeping the original project safe."),
  key("A smaller reproduction helps you understand a defect; it is not permission to remove content from the real project.")
 ]],
 ["Review the week's evidence tools",[
  code("Reference → rule or feature information\nEditor → saved source and file location\nElements → live document relationships\nConsole → messages, not proof of valid HTML\nNetwork → recorded resource evidence"),
  p("Comments can annotate intent but are not private. A validator can report markup errors but cannot tell you that an essay is meaningful. A visible page can still contain repaired malformed markup. Use each tool for the question it can answer."),
  p("Repeat the Day 6 repair without the corrected example. When source and DOM disagree, explain the likely recovery and verify the saved correction."),
  warn("Never include private values in an online validator, shared log or comment. A nonprivate minimal example is enough."),
  tip("Keep unresolved questions with exact feature names. A useful question prepares you for documentation and for asking someone for help.")
 ]],
 ["Prove the checkpoint",[
  p("Choose three distinct defects: wrong file, malformed tag or quote, and invalid nesting. For each show a repair and explain why it works. Save, reopen and inspect the result. Keep every intended sentence."),
  out("Checkpoint deliverables:\nA corrected file, three explained repairs,\na debugging log and one regression check."),
  p("Redo any workshop item answered by guessing. If two possible causes remain, write the next evidence-gathering step rather than pretending certainty."),
  p("Next week focuses on choosing HTML for meaning: headings, paragraphs, emphasis, lists and semantic regions. This week's debugging method will be used with those new elements."),
  key("Move on when you can repair and explain without replacing the whole document.")
 ]]
 ],
 practice:[
  ["Narrow a search question.","Everything about HTML is confusing.","How do I write the title element, and where does it belong?","A specific question makes a reference useful."],
  ["Separate sample from rule.","A sample title says Nima's notebook.","The wording is replaceable; title still belongs in head.","Keep syntax rules while personalising content."],
  ["Write a useful comment.","Explain that the introduction is intentionally brief.","<!-- Keep the introduction brief for new learners. -->","Explain intent.","html"],
  ["Close the comment.","<!-- Next session: review tags.","<!-- Next session: review tags. -->","Missing boundaries can affect later content.","html"],
  ["Repair nesting comments.","<!-- A <!-- B --> -->","<!-- A -->\n<!-- B -->","Comments do not nest.","html"],
  ["Evaluate a secret comment.","<!-- real token here -->","Do not store a real token in source comments.","Delivered comments are inspectable.","html"],
  ["Choose the right representation.","What was saved in the local file?","Read the exact saved source in the editor.","The live DOM can be repaired or changed."],
  ["Name a DOM relationship.","p directly inside body.","p is a child of body.","Containment defines the relationship."],
  ["Explain an inserted DOM element.","Source omitted body, but Elements shows body.","The parser can create missing document structure.","DOM presence does not prove explicit source."],
  ["Check the path.","Editor shows folder A; browser shows folder B.","Open the intended same file before judging the result.","Wrong-file symptoms imitate failed edits."],
  ["Repair a tag.","<h1>Repair</p>","<h1>Repair</h1>","Use a matching end name.","html"],
  ["Repair a quoted phrase.","<p title=Two words>Text</p>","<p title=\"Two words\">Text</p>","Keep the phrase in one value.","html"],
  ["Repair paragraphs.","<p>A<p>B</p></p>","<p>A</p><p>B</p>","Paragraphs should be siblings here.","html"],
  ["Write expected versus actual.","You wanted New but saw Old.","Expected heading: New. Actual heading after saving and reloading: Old.","Include the action and the exact result."],
  ["Test a hypothesis.","Maybe the edit was unsaved.","Save the exact file and reload its tab; compare the result.","The test addresses that specific cause."],
  ["Explain a failed test.","Saving did not fix it.","Record that result and inspect the next supported cause, such as path mismatch.","A failed test narrows the investigation."],
  ["Name a regression check.","The heading now works.","Verify the other paragraph, title and metadata remain intact.","A repair should preserve working content."],
  ["Prepare a help request.","You still cannot explain the issue.","Provide a small nonprivate example, reproduction steps and tests tried.","Do not send private tokens or a vague complaint alone."]
 ],
 challenge:["Run your own repair review","Take a copy of a practice page, diagnose three different mistakes and produce a complete debugging log. Retain all intended content and explain the final source tree.","1. Confirm file and save state.\n2. Reproduce exact symptom.\n3. Test one cause at a time.\n4. Repair matching tags, quoted values and allowed nesting as needed.\n5. Save, reopen and reload.\n6. Verify content, title and metadata remain correct.","There can be several valid logs. The requirement is evidence, a focused correction and a persistent result."],
 ready:"Find and explain several beginner HTML mistakes without replacing the whole page. Repeat weak workshop items before Week 5.",
 reflection:"Record your three repairs and one question that still needs a reference. Which debugging habit saved the most confusion?",
 quiz:[
  ["Which question best supports documentation lookup?","Does p allow an h1 child?","Why is my entire life broken?","Can I learn everything now?","Use a precise feature question."],
  ["Which syntax is a comment?","<!-- Note -->","// Note","# Note","Use the HTML delimiters."],
  ["Are comments private?","No","Yes","Only on static sites","Source is available to visitors."],
  ["Which shows the current document tree?","Elements","Only the editor","Only the filename","Use DOM inspection for current relationships."],
  ["Can parsing cause a source/DOM mismatch?","Yes","No","Only with CSS","HTML recovery can alter structure."],
  ["What should you check before rewriting markup?","File path and saved state","A new framework","A new computer","Wrong-file and unsaved states are common causes."],
  ["Which is a useful symptom report?","After refresh I expected New but saw Old","It is weird","Everything is broken","Make the observation reproducible."],
  ["What makes a hypothesis useful?","It can be tested against evidence","It sounds advanced","It blames a random tool","A testable explanation can be confirmed or weakened."],
  ["Why avoid changing many unrelated things?","It obscures cause and can add defects","HTML forbids multiple edits","It always deletes the file","Controlled changes improve diagnosis."],
  ["What does a regression check protect?","Previously working content and behaviour","Only the page icon","Only the new heading","Preserve surrounding functionality."],
  ["Does a validator replace all judgement?","No","Yes","Only if online","It checks rules, not all content/design goals."],
  ["What completes a repair?","Persistent expected result plus checks","A temporary appearance change only","Deleting the difficult sentence","Save, reload, explain and preserve content."]
 ]});
module.exports={lessons,examples:{repaired,comments}};
