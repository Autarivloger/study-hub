const {p,key,tip,warn,term,code,out,mistake,page,lesson}=require('./web-development-teaching-tools.cjs');
const essentials=page("My learning notes","    <h1>My learning notes</h1>\n    <p>I can explain each part of this document.</p>");
const about=page("About my studies","    <h1>About my studies</h1>\n    <p>I practise a small skill, check it and explain it.</p>\n    <h2>My next goal</h2>\n    <p>I will write a complete page from memory.</p>");
const reading=page("Reading practice","    <h1>Reading practice</h1>\n    <p>This page is mainly English.</p>\n    <p lang=\"ja\">日本語を勉強しています。</p>");
const lessons={},add=(day,d)=>lessons['3.'+day]=lesson(3,day,d);
add(1,{
 title:"Elements and tags",objective:"Identify each part of an element, write matching tags and display literal special characters correctly.",
 parts:[
 ["Read one element carefully",[
  p("Week 1 introduced a heading and a paragraph. Today slow down and inspect their syntax. Syntax means the rules for writing something so a tool can interpret it. Do not judge source correctness only by whether a browser shows some text."),
  term("Element, tag and content","In <p>One clear step.</p>, <p> is the opening tag, One clear step. is text content, and </p> is the closing tag. The complete structure is the paragraph element."),
  code("<p>One clear step.</p>\n<h1>My practice page</h1>","html"),
  out("Paragraph: One clear step.\nMain heading: My practice page"),
  p("Angle brackets delimit tags; the slash before the closing name marks an end tag. Type p in both paragraph tags. A tag name is not the visible content: changing the sentence does not require inventing a new tag name.")
 ]],
 ["Paired and void elements",[
  term("Paired element","A beginner name for an element written with a start tag, content and an end tag, such as h1 or p. Some HTML end tags can legally be omitted in certain cases; our course writes them explicitly for clarity."),
  term("Void element","An element that cannot contain child content and has no end tag. The meta element from Week 1 is an example. Write <meta charset=\"utf-8\"> without </meta>. Do not treat every tag as paired."),
  code("<p>I write a full paragraph element.</p>\n<meta charset=\"utf-8\">","html"),
  mistake("<h1>My notes</p>","<h1>My notes</h1>","The end tag must match the intended heading. The browser may recover from the wrong tag."),
  p("In HTML, adding a trailing slash does not turn an ordinary element into a self-closing one. <p /> is not our substitute for <p></p>. You may see <meta ... /> in examples, but the slash is unnecessary for an HTML void element.")
 ]],
 ["When you want to show the brackets",[
  term("Character reference","A spelling beginning with & that represents a character in HTML source. &lt; represents <, &gt; represents > and &amp; represents &. These let you write text that could otherwise be confused with markup."),
  code("<p>Write &lt;p&gt; for an opening paragraph tag.</p>\n<p>Tea &amp; water</p>","html"),
  out("Write <p> for an opening paragraph tag.\nTea & water"),
  p("Do not replace every angle bracket in a real page with character references. Real tags such as <p> provide structure. Use references where the bracket itself is content. You are learning the difference between writing an element and writing text about an element."),
  key("Read the whole element. Match paired tags, recognise void elements and distinguish literal text from markup.")
 ]]
 ],
 practice:[
  ["Label the three parts.","<p>I am practising.</p>","Opening: <p>; content: I am practising.; closing: </p>.","The element includes all three parts.","html"],
  ["Repair the heading.","<h1>Practice</hl>","<h1>Practice</h1>","Use the digit 1, not a letter l.","html"],
  ["Remove the invalid end tag.","<meta charset=\"utf-8\"></meta>","<meta charset=\"utf-8\">","meta is void and does not have an end tag.","html"],
  ["Show the characters <h1> in a sentence.","<p>Type ... for a heading.</p>","<p>Type &lt;h1&gt; for a heading.</p>","The bracket characters are text, not a real nested heading.","html"],
  ["Predict the visible text.","<p>Read &amp; practise.</p>","Read & practise.","&amp; represents one ampersand character.","html"]
 ],
 challenge:["Write and annotate three elements","In your practice file body, write one h1 and two p elements. In the second paragraph show the literal text <p>. Point to every opening tag, content and closing tag.","<h1>Reading my source</h1>\n<p>I can match the tags.</p>\n<p>This is the spelling &lt;p&gt;.</p>","The third element displays bracket text without creating another paragraph opening.","html","Heading: Reading my source\nI can match the tags.\nThis is the spelling <p>."],
 ready:"You can distinguish an element from a tag, repair a mismatched pair and explain why meta has no closing tag.",
 reflection:"Annotate your own paragraph. Explain why <p /> is not the paragraph pattern used in this course.",
 quiz:[
  ["What is the whole <p>Hello</p> structure called?","An element","Only an end tag","Only an attribute","It includes tags and content."],
  ["Which closes <h1>?","</h1>","</hl>","<h1/>","The name and digit must match."],
  ["Which element is void?","meta","p","h1","meta has no child content or end tag."],
  ["What displays a literal < in HTML text?","&lt;","<p>","</","The character reference represents the bracket."],
  ["What does &amp; represent?","An ampersand","A paragraph","A space","One reference produces one & character."],
  ["Does <p /> replace a matching paragraph end tag in HTML?","No","Yes, always","Only if the text is short","A trailing slash does not self-close an ordinary HTML element."]
 ]});
add(2,{
 title:"Document structure",objective:"Build a complete document and explain doctype, html, head, title and body without confusing metadata with visible headings.",
 parts:[
 ["Start with the outer structure",[
  p("A fragment is useful for studying one element. A saved page needs a dependable document structure. You saw this shell in Week 1; now rebuild it deliberately. Write the outside first, then fill the correct region instead of pasting a whole page without understanding it."),
  term("Doctype declaration","<!doctype html> is the modern HTML doctype. It tells the browser to use standards mode. It is a declaration before the root element, not a paired element and not the page title."),
  term("Root html element","The outer document element. It contains the head and body. In our examples lang=\"en\" declares English as the main human language; this does not translate the page."),
  code("<!doctype html>\n<html lang=\"en\">\n  <head>\n  </head>\n  <body>\n  </body>\n</html>","html"),
  p("Indent head and body one step inside html. Their order is head then body. We write explicit tags even where HTML has omission rules, because the full structure is easier to learn and review.")
 ]],
 ["Give each region the right job",[
  term("head and title","head contains document metadata. title provides the document title used in the browser tab and often bookmarks. The head element is not the h1 heading."),
  term("body","The region for document content, including headings and paragraphs that readers encounter. The title element belongs in head; the visible h1 belongs in body."),
  code(essentials,"html"),
  out("Browser tab: My learning notes\nPage heading: My learning notes\nParagraph: I can explain each part of this document."),
  p("The tab title and h1 can share words, but they are separate elements with different jobs. Changing title alone does not change h1. The meta lines describe encoding and viewport; Day 5 studies these carefully. Keep them in this shell rather than deleting unexplained-looking lines.")
 ]],
 ["Save, reopen and compare",[
  p("Create essentials.html in your existing practice folder using UTF-8. Save and open the exact file in a browser. Change only title to My HTML notebook, save and refresh. Check that the tab changes while the visible heading remains My learning notes."),
  mistake("<body>\n  <title>My notebook</title>\n  <p>My notes.</p>\n</body>","<head>\n  <title>My notebook</title>\n</head>\n<body>\n  <p>My notes.</p>\n</body>","The corrected region fragment shows where title and visible content belong. A complete file also needs the outer shell."),
  p("Browsers can supply missing elements and repair source. Seeing head and body in Elements does not prove you wrote both correctly in the saved file. Compare the source with the current DOM when they seem different."),
  tip("When the tab seems unchanged, first check the exact file address, saved state and which title you edited. Avoid repeatedly creating copies with similar filenames."),
  key("Declaration → html root → head metadata → body content. Tab title and visible heading are independent.")
 ]]
 ],
 practice:[
  ["Place the element.","<title>My notes</title>","Inside head.","title is document metadata.","html"],
  ["Place the element.","<h1>My notes</h1>","Inside body.","It is visible content structure.","html"],
  ["Explain this first line.","<!doctype html>","It selects modern standards-mode HTML parsing/rendering behaviour.","It is a declaration, not an opening html tag.","html"],
  ["Predict the change.","Only <title>Old</title> becomes <title>New</title>.","The tab/document title changes; h1 need not change.","The two elements are independent."],
  ["Can Elements prove your shell was explicit?","Elements shows body even though source omitted it.","No. The parser can insert document elements.","Inspect source as well as the resulting DOM."]
 ],
 challenge:["Build the shell from memory","Write a full file with a useful title, one h1 and one paragraph. Use the encoding and viewport lines from essentials.html, then explain their location.","<!doctype html>\n<html lang=\"en\">\n  <head>\n    <meta charset=\"utf-8\">\n    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n    <title>My HTML notebook</title>\n  </head>\n  <body>\n    <h1>A clean beginning</h1>\n    <p>I know where each part belongs.</p>\n  </body>\n</html>","Metadata is inside head. The body contains the heading and paragraph. Save as UTF-8.","html","Tab: My HTML notebook\nHeading: A clean beginning\nParagraph: I know where each part belongs."],
 ready:"Write the shell without copying and change the tab title independently from the page heading.",
 reflection:"Draw the document tree. Explain head, title and h1 to someone who thinks they mean the same thing.",
 quiz:[
  ["Which element is the document root?","html","title","p","head and body belong within html."],
  ["Where does title belong?","head","Inside every paragraph","After </html>","It is metadata for the document."],
  ["Where does the visible main heading belong?","body","Only head","Only the filename","h1 marks content structure."],
  ["What goes before the root in our shell?","<!doctype html>","</body>","<h1>","The doctype precedes the root element."],
  ["Does changing title automatically rewrite h1?","No","Yes","Only with short titles","They are different elements."],
  ["A browser displays incomplete source. What should you do?","Check and repair source structure","Assume it is all valid","Delete the head region","Error recovery can conceal mistakes."]
 ]});
add(3,{
 title:"Attributes",objective:"Read and write quoted name/value attributes and distinguish element information from visible text.",
 parts:[
 ["Information in the opening tag",[
  p("An element name identifies a kind of content. Attributes give extra information about that element. You already used lang and charset. Today read their syntax rather than treating the entire line as a mysterious formula."),
  term("Attribute name and value","In lang=\"en\", lang is the name and en is the value. A space separates the attribute from the element name. The equals sign joins name and value; straight quotes surround our value."),
  code("<html lang=\"en\">\n<p title=\"A short learning note\">Practise carefully.</p>","html"),
  term("title attribute versus title element","The title attribute adds advisory information to an element and may appear as a hover tooltip on desktop. The title element sets the document title. A tooltip is not a dependable replacement for visible instructions or an accessible label."),
  p("The visible paragraph is Practise carefully. The attribute text is not ordinary paragraph content. On touch devices there may be no convenient hover. Put essential information in visible content.")
 ]],
 ["Several attributes and useful identifiers",[
  term("id","An identifier for one element in a document. Use unique values without spaces, such as study-goal. An id can be a fragment target and later help styling or scripts locate an element. It does not automatically change appearance."),
  term("class","A reusable label for grouping elements. Multiple elements can have the same class; multiple class names on one element are separated by spaces. A class alone does not create a style rule."),
  code("<p id=\"study-goal\" class=\"note important\">Practise daily.</p>\n<p class=\"note\">Check one change at a time.</p>","html"),
  p("Here the first paragraph has one unique id and two class names, note and important. The second shares note. Order of these ordinary attributes does not change their meaning. Do not repeat the same attribute name twice on an element."),
  key("Keep names, values and visible content separate. Write attributes only in the opening tag.")
 ]],
 ["Quote values and check spelling",[
  mistake("<p title=My study goal>Practise.</p>","<p title=\"My study goal\">Practise.</p>","Without quotes, spaces split the intended value into separate tokens. Quote values consistently."),
  p("Use plain straight double quotes in your editor. If you need a double quote inside a double-quoted attribute value, &quot; represents it. You can also choose single quotes around a value, but keep matching delimiters. Do not use word-processor curly quotes as HTML delimiters."),
  code("<p title=\"She said &quot;keep going&quot;.\">One step today.</p>","html"),
  out("Visible paragraph: One step today.\nAdvisory attribute value: She said \"keep going\"."),
  p("Boolean attributes, which express true/false through presence rather than a normal text value, exist in HTML. They appear with controls later. Do not generalise today's name/value pattern into a claim that every HTML attribute needs a value.")
 ]]
 ],
 practice:[
  ["Name the attribute and its value.","<html lang=\"en\">","Name: lang. Value: en.","html is the element name.","html"],
  ["Count class names.","<p class=\"note important\">Text</p>","Two: note and important.","Spaces separate class tokens.","html"],
  ["Repair the value.","<p title=My next step>Text</p>","<p title=\"My next step\">Text</p>","Quote the full value with spaces.","html"],
  ["Find the identifier problem.","<p id=\"goal\">A</p>\n<p id=\"goal\">B</p>","The id is duplicated; choose unique ids or a shared class.","An id identifies one element in the document.","html"],
  ["Is the vital instruction available to everyone?","Only a title tooltip says when work is due.","No. Put the due date in visible text.","Hover-only information is not dependable on touch or keyboard use."]
 ],
 challenge:["Annotate a practice paragraph","Write a paragraph with a unique id and a class named learning-note. Add a short nonessential title attribute. Explain what changes in the visible page.","<p id=\"daily-goal\" class=\"learning-note\" title=\"Optional hint\">I will practise HTML.</p>","The sentence is visible. id and class are labels, not automatic styling. Keep essential information in the sentence.","html","I will practise HTML."],
 ready:"Write a quoted attribute, explain id versus class and avoid relying on title tooltips for essential content.",
 reflection:"Label the name and value of three attributes. Explain why a class named red does not automatically turn text red.",
 quiz:[
  ["Where do ordinary attributes go?","In the opening tag","Only inside the closing tag","Only in the filename","Attributes describe the element at its start tag."],
  ["Which value is fully quoted?","title=\"My study goal\"","title=My study goal","title=“My study goal”","Straight matching quotes delimit the value."],
  ["Which identifier should be unique in a document?","id","class","The word p","Multiple elements can share class names."],
  ["Does class=\"red\" automatically colour text?","No","Yes","Only in an h1","A class is a label; styling needs CSS rules."],
  ["What is the risk of essential tooltip-only text?","Some users cannot readily access it","It always becomes a heading","It changes the filename","Touch and other input modes may not provide hover."],
  ["What does &quot; represent inside a value?","A double quote character","A paragraph","A closing html element","The reference avoids ending the surrounding quoted value."]
 ]});
add(4,{
 title:"Nesting and indentation",objective:"Read parent, child and sibling relationships and use indentation to reveal structural errors.",
 parts:[
 ["The document is a tree",[
  p("Nesting means putting an element inside another element that is allowed to contain it. Think of the document as a family tree rather than a pile of lines. A child belongs inside its parent's boundaries. Some elements have restrictions on what can go inside them."),
  term("Parent, child and sibling","A parent directly contains an element. That element is its child. Elements with the same parent are siblings. A descendant is nested somewhere inside an ancestor, possibly more than one level down."),
  code("<html lang=\"en\">\n  <head>\n    <title>Tree practice</title>\n  </head>\n  <body>\n    <h1>My plan</h1>\n    <p>Read and practise.</p>\n  </body>\n</html>","html"),
  code("html\n├─ head\n│  └─ title\n└─ body\n   ├─ h1\n   └─ p"),
  p("head and body are siblings. title is a child of head. h1 and p are children of body and descendants of html. h1 is not the parent of the paragraph merely because it appears before it.")
 ]],
 ["Indent to show the relationship",[
  term("Indentation","Spaces at the start of a source line that make nesting easier to read. In ordinary HTML text, indentation is mainly for source readability, not a command to create visible page columns."),
  p("Use one consistent indentation step, such as two spaces. Align an end tag with its start tag when they span lines. Do not rely on indentation alone: tags establish the structure. Incorrectly indented valid tags may still parse correctly; beautifully indented invalid nesting is still wrong."),
  code("<body>\n  <h1>One main heading</h1>\n  <p>First paragraph.</p>\n  <p>Second paragraph.</p>\n</body>","html"),
  out("Heading, then two paragraphs. Source indentation does not produce two visible columns."),
  tip("When a file becomes confusing, collapse a region in your editor if supported, or draw the tree. Do not delete content merely to make the file shorter.")
 ]],
 ["Close the inner structure first",[
  p("Paired element boundaries must fit together. When an allowed child is inside a parent, close that child before closing the parent. Also check the HTML content rules: p holds phrasing content, not another p or an h1. The browser can automatically close a paragraph when it sees a new paragraph."),
  mistake("<p>First thought.\n  <p>Second thought.</p>\n</p>","<p>First thought.</p>\n<p>Second thought.</p>","These are separate paragraphs, so make them siblings rather than nesting p inside p."),
  mistake("<p><h1>My goal</h1>Study daily.</p>","<h1>My goal</h1>\n<p>Study daily.</p>","A heading does not belong inside a paragraph. The parser may rearrange the intended tree."),
  p("Use Elements to compare the tree with your source on the disposable practice file. If the DOM contains an unexpected empty p, investigate source structure rather than assuming the browser copied your nesting literally."),
  key("Tags define relationships; indentation reveals them; content rules decide which relationships are allowed.")
 ]]
 ],
 practice:[
  ["Name the siblings.","body directly contains h1, p and p.","h1 and both p elements are siblings.","They share body as their parent."],
  ["Is the earlier heading a parent?","<h1>Plan</h1>\n<p>Read.</p>","No. The heading and paragraph are siblings in this body fragment.","Being earlier is not the same as containing.","html"],
  ["Repair nesting.","<p>One<p>Two</p></p>","<p>One</p>\n<p>Two</p>","Separate paragraphs are siblings.","html"],
  ["Explain the effect of indentation.","You add two spaces before each p in the source.","The source is easier to read; it does not create a visible layout column.","HTML whitespace normally collapses in ordinary text."],
  ["Find the descendant.","html contains head, which contains title.","title is a descendant of html and child of head.","Direct and indirect relationships differ."]
 ],
 challenge:["Draw and repair a tree","Use essentials.html. Draw its tree, label head/body as siblings and title as a child. Then intentionally misindent one line, predict whether the tags changed and restore the readable indentation.","html → head → meta, meta, title\nhtml → body → h1, p","The two meta elements and title share head as parent. Changing indentation alone does not change these element names or boundaries."],
 ready:"Explain parent, child, sibling and descendant, repair nested paragraphs and use source indentation without confusing it with CSS layout.",
 reflection:"Draw your own document tree. Describe one case where the live DOM could differ from the intended source nesting.",
 quiz:[
  ["Elements sharing a direct parent are…","Siblings","Always parents of each other","Attributes","The relationship comes from containment."],
  ["Which directly contains title in our shell?","head","h1","p","title is a child of head."],
  ["What primarily establishes nesting?","Element boundaries and content rules","Only the number of spaces","The file icon","Indentation helps people read the structure."],
  ["Can one p contain another p?","No","Yes, if indented","Only if both are short","Use sibling paragraphs instead."],
  ["Does an h1 belong inside a p?","No","Yes, for large text","Only when offline","A heading is not paragraph phrasing content."],
  ["Why compare source with Elements?","Parsing can repair and change the intended tree","They always show identical text","Elements automatically saves the file","The live DOM is a parsed representation."]
 ]});
add(5,{
 title:"Page metadata",objective:"Set language, UTF-8 encoding, viewport and a useful title, and explain what each setting does and does not do.",
 parts:[
 ["Describe the language and characters",[
  term("Metadata","Information describing a document rather than ordinary article content. Some metadata is in head, while the root lang attribute describes the document's main human language."),
  p("A browser and assistive tools need clues about the document. The language setting can help pronunciation and language processing. Character encoding explains how saved bytes represent text. These are different jobs: lang=\"ja\" does not convert English text into Japanese."),
  code("<html lang=\"en\">\n  <head>\n    <meta charset=\"utf-8\">\n    <title>My language notes</title>\n  </head>\n  <body>\n    <p lang=\"ja\">日本語を勉強しています。</p>\n  </body>\n</html>","html"),
  term("UTF-8 encoding","A way to store text as bytes that supports Unicode characters from many writing systems. Declare it early in head and save the file itself using UTF-8. A declaration alone cannot repair already corrupted text."),
  p("Set the root language for the main content. When a passage is in another language, a lang attribute on that passage can identify the change. In this fragment the main language is English and one paragraph is Japanese.")
 ]],
 ["Give small screens a useful viewport",[
  term("Viewport","The area through which the browser presents the document. On mobile, the viewport setting helps the layout use the device width instead of a wider default virtual layout."),
  code("<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">","html"),
  p("name=\"viewport\" identifies the metadata type. content contains its settings. width=device-width uses the device width in CSS pixels; initial-scale=1 chooses the initial zoom scale. The comma separates the settings inside one quoted value."),
  warn("The viewport line alone does not make a complex layout responsive. Flexible CSS and suitable content are still necessary later. Do not add user-scalable=no or maximum-scale=1 to stop people from zooming."),
  tip("For now use simple content that wraps naturally and keep the standard viewport line. You do not need to write media queries before learning CSS.")
 ]],
 ["Write a useful title and optional description",[
  p("A useful title distinguishes the page in a crowded tab strip. My notes is less specific than HTML nesting | My study notes. Choose words that describe this page rather than reusing Untitled everywhere."),
  term("Description metadata","A short description can summarise the document for tools and search systems. A search engine may choose another snippet, and local files do not become indexed merely because a description is present."),
  code("<title>HTML nesting | My study notes</title>\n<meta name=\"description\" content=\"A short beginner notebook about HTML document structure.\">","html"),
  p("Put the description inside head. Keep it accurate and omit private data. It is not a hidden private note. Metadata is part of the delivered source and can be inspected by visitors."),
  key("lang identifies language; charset declares encoding; viewport guides the initial viewport; title identifies the document. None replaces good content structure.")
 ]]
 ],
 practice:[
  ["Does this translate the content?","<html lang=\"ja\"> containing English sentences.","No. It declares a language; it does not translate text.","Use a value that matches the actual primary content.","html"],
  ["What two UTF-8 steps matter?","Text contains नेपाली and 日本語.","Save the file as UTF-8 and declare UTF-8 early in head.","Declaration and actual bytes should agree."],
  ["Can this line fix every layout?","<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">","No. It helps mobile viewport behaviour; responsive layout still needs suitable design.","Do not mistake one prerequisite for the whole solution.","html"],
  ["Improve the title.","<title>Untitled</title>","<title>HTML structure | My study notebook</title>","A specific title helps identify the page.","html"],
  ["Is a description private?","A secret is placed in meta content.","No. Source metadata is delivered to visitors.","Use no private values in public source."]
 ],
 challenge:["Audit the document head","Check your practice file for root lang, an early UTF-8 declaration, the standard viewport line and a meaningful title. Add a concise description if useful. Save and check both tab and content.","<head>\n  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n  <title>My HTML essentials</title>\n  <meta name=\"description\" content=\"My beginner HTML practice notebook.\">\n</head>","This is a head fragment; retain the full html/body shell. Root lang belongs on html, outside this fragment.","html"],
 ready:"Explain all four core settings, preserve zoom and distinguish language declarations from translation.",
 reflection:"Record your title and primary language. Explain why saving bytes as UTF-8 matters in addition to writing a meta line.",
 quiz:[
  ["What does lang declare?","Human language","Text colour","Automatic translation","Tools use it as a language clue."],
  ["What does charset=\"utf-8\" describe?","Text encoding","A font size","A password","The declared encoding should match saved bytes."],
  ["Where should the charset declaration go?","Early in head","Only in a paragraph","After every heading","It should be available early when parsing."],
  ["Does a viewport tag guarantee responsive design?","No","Yes","Only on large monitors","Layout still needs suitable content and CSS."],
  ["Should a beginner block pinch zoom?","No","Yes, for a premium look","Only on reading pages","Keep user zoom available."],
  ["What is true of metadata?","Visitors can inspect delivered metadata","It is a private password vault","It cannot affect tools","Metadata describes the document and is not secret storage."]
 ]});
add(6,{
 title:"Build two clean documents",objective:"Create two independently valid pages with distinct titles and content, then verify their source and displayed results.",
 parts:[
 ["Plan both pages before typing",[
  p("The project uses only skills taught so far. Create a new folder named week3-pages in your practice area. Make about.html and reading.html. These are separate documents, not tabs that automatically share a title. Do not replace Study Hub files."),
  code("week3-pages/\n  about.html\n  reading.html"),
  p("about.html will describe your learning goal with a main heading, two short paragraphs and a section heading. reading.html will contain English text and a short Japanese passage with lang=\"ja\". You are not expected to translate Japanese to learn HTML; the passage demonstrates language metadata."),
  term("Acceptance check","A concrete result that tells you whether a piece of work meets its goal. Here use saved filenames, correct titles, explicit structure and intended text rather than whether the page looks fancy."),
  key("Keep the two filenames, tab titles and visible headings distinguishable.")
 ]],
 ["Write, predict, open",[
  code(about,"html"),
  p("Type about.html, explaining each line as you go. Predict the tab title and the visible heading before opening it. Then create reading.html with the same complete shell, a distinct title and the body fragment below."),
  code("<h1>Reading practice</h1>\n<p>This page is mainly English.</p>\n<p lang=\"ja\">日本語を勉強しています。</p>","html"),
  out("about.html tab: About my studies\nabout.html main heading: About my studies\nreading.html tab: Reading practice\nreading.html includes Japanese characters."),
  p("Save both as UTF-8. Open each actual file in its own browser tab. If a change appears in the wrong tab, compare full local paths before editing more.")
 ]],
 ["Audit without destroying work",[
  code("For each document:\n[ ] Exact filename and .html extension\n[ ] Doctype, html, head and body\n[ ] Correct root language\n[ ] UTF-8 bytes and declaration\n[ ] Standard viewport\n[ ] Distinct useful title\n[ ] Matching tags and readable indentation\n[ ] Text survives save, close and reopen"),
  p("Use Elements to locate the h1 within body. Use the editor for source checking. If a problem appears, change one thing and retest. Keep the working copy so you can compare it rather than starting from a blank file."),
  tip("No links are required yet. Open both files from your file manager. Linking documents is a later topic, after these foundations."),
  p("Personalise sentences only after the baseline works. If you write mainly Nepali, use lang=\"ne\" on that page; if mainly Japanese, use lang=\"ja\". Match the declaration to the content you actually wrote."),
  key("Completion means both files can be reopened, explained and corrected independently.")
 ]]
 ],
 practice:[
  ["What should differ between these pages?","about.html and reading.html","Their filenames, useful titles and intended content.","Each is its own document."],
  ["Where does the Japanese passage language go?","A Japanese p inside an English page.","On that p as lang=\"ja\", keeping root lang=\"en\".","Declare the local language change.","html"],
  ["Predict the tab.","<title>Reading practice</title>","Reading practice.","The browser tab uses the document title.","html"],
  ["What evidence tests persistence?","The page looked right before closing the editor.","Close and reopen the exact saved file and refresh its browser tab.","A visible temporary state is insufficient."],
  ["Should you add a framework to fix a missing end tag?","about.html has a mismatched h1 end tag.","No. Repair that source error directly.","A small problem should receive a focused fix."]
 ],
 challenge:["Finish the two-page notebook","Build both files from your own memory. Compare with the examples only after the first attempt, then audit every acceptance check. Explain one mistake you found.","about.html: distinct title, h1, h2 and meaningful paragraphs.\nreading.html: distinct title, English root language and Japanese passage language.\nBoth: modern doctype, UTF-8, viewport, matching explicit structure.","The complete example files are available under docs/web-development-week3/examples in your downloaded project. Your own wording is welcome."],
 ready:"Reopen both documents, explain their trees and show one deliberate text change saved to only the correct file.",
 reflection:"Record both file locations, a passed check for each and a mistake you repaired without replacing the whole page.",
 quiz:[
  ["Why use distinct useful titles?","To identify documents in tabs and bookmarks","To automatically sync files","To make both files identical","Each document should be recognisable."],
  ["How do you open the second document before learning links?","Use the file manager or open-file action","Install a database","Rename the first tab","Opening a file does not require an HTML link."],
  ["Which check confirms source persistence?","Reopen the same saved file","Only edit Elements","Only inspect the icon","Reopening tests saved contents."],
  ["Which language value matches mainly Nepali content?","ne","ja","css","Use a language identifier matching the actual content."],
  ["Should a Japanese paragraph force the entire English page to lang=ja?","No, set the passage language","Yes, always","Remove all language declarations","Local language attributes can mark a passage."],
  ["What is a good response to one nesting error?","Repair it and retest","Delete both pages","Add a JavaScript framework","Use focused debugging on the actual issue."]
 ]});
add(7,{
 title:"Week 3 review and rebuild",objective:"Write a complete document from memory, diagnose source errors and explain the week checkpoint.",
 parts:[
 ["Rebuild the shell without a reference",[
  p("Use a blank review.html in your practice folder. Write the full shell from memory, including language, encoding, viewport and a useful title. Add a main heading and two paragraphs. Stop before copying; note the lines you cannot yet explain."),
  code("Recall: declaration → root → metadata → content.\nCheck: names → quotes → matching tags → nesting → saved file."),
  p("Now compare with Day 2. Repair one thing at a time and explain each correction. If you forgot the viewport line, revisit Day 5 rather than memorising it as unexplained punctuation."),
  term("Source audit","A deliberate review of saved markup for structure, meaning and syntax. It complements browser observation because the parser can recover from some mistakes."),
  key("A document that happens to display is not automatically a document you understand.")
 ]],
 ["Recheck relationships and metadata",[
  code("head and body: siblings within html\ntitle: child of head\nh1 and p: siblings within body\nlang: human language\ncharset: text encoding\nviewport: initial viewport guidance"),
  p("Explain the difference between an attribute and an element, and between a tag and its text content. Then explain title as an element versus title as an attribute. These similar names cause mistakes when learned only by appearance."),
  p("Inspect the live DOM of your review file if tools are available. Compare it with the saved source. Do not claim an automatically inserted element was explicitly written in your file."),
  warn("Do not place private data in metadata or attributes as a hiding technique. Delivered source is available to visitors."),
  tip("Keep a short list of errors you made. It is more useful for next week's troubleshooting than a perfect copied document.")
 ]],
 ["Check readiness through explanation",[
  p("Ask yourself: Can I explain every line? Can I find a missing closing tag? Can I keep two document titles separate? Can I describe why nested paragraphs are wrong? Complete the workshop below without opening answers first."),
  out("Evidence to retain:\nA saved review.html, its tree, a list of corrections,\nand your explanation of the four core metadata settings."),
  p("If you are unsure on two or more items, repeat the relevant day and rebuild again. You can take more than one session. The next week uses these exact foundations to troubleshoot prepared mistakes."),
  p("Finally reopen both Day 6 pages to confirm that your review work did not overwrite them. Your project folder should now contain several clearly named pages."),
  key("Finish the checkpoint by writing and explaining, not by increasing a completion number alone.")
 ]]
 ],
 practice:[
  ["Name the opening and closing tags.","<p>Hello.</p>","<p> and </p>.","Hello. is text content.","html"],
  ["Repair the digit typo.","<h1>Goal</hl>","<h1>Goal</h1>","The closing tag uses the digit 1.","html"],
  ["Remove the impossible end tag.","<meta charset=\"utf-8\"></meta>","<meta charset=\"utf-8\">","meta is void.","html"],
  ["Show literal tag text.","Display <p> as characters.","&lt;p&gt;","Use references for literal brackets.","html"],
  ["Decode this text.","Read &amp; practise.","Read & practise.","&amp; represents &."],
  ["Place the title.","<title>Review</title>","Inside head.","It identifies the document.","html"],
  ["Place the main heading.","<h1>Review</h1>","Inside body.","It is visible content structure.","html"],
  ["Explain doctype.","<!doctype html>","Modern HTML standards-mode declaration.","It is not a paired content element.","html"],
  ["Repair the attribute.","<p title=My goal>Study.</p>","<p title=\"My goal\">Study.</p>","The full spaced value needs quotes.","html"],
  ["Choose id or class.","Several notes need one shared label.","Use a class such as note.","Keep ids unique."],
  ["Repair the relationship.","<p>One<p>Two</p></p>","<p>One</p><p>Two</p>","Paragraphs are siblings.","html"],
  ["Name the relationship.","head directly contains title.","head is parent; title is child.","Both are within the document tree."],
  ["What changes with indentation alone?","Add two spaces before a normal paragraph source line.","Readability, not automatically visible columns.","Tags define nesting and CSS controls layout."],
  ["Does lang translate?","English text with lang=\"ja\".","No. Correct the declaration or content.","Language metadata is not a translation tool."],
  ["What must accompany charset?","<meta charset=\"utf-8\">","Actual UTF-8 file encoding.","A label cannot restore corrupted bytes.","html"],
  ["What is still needed beyond viewport for complex layouts?","Responsive page design.","Appropriate flexible CSS and content.","Viewport is one part of mobile support."],
  ["Find the persistence mistake.","A heading was edited only in Elements.","Edit and save the correct source file.","Temporary DOM changes normally vanish on reload."],
  ["Is identical appearance proof of valid source?","Browser displays the malformed page.","No; audit source and inspect the parsed tree.","Error recovery can conceal defects."]
 ],
 challenge:["Pass the Week 3 checkpoint","Build a full page without the solution, draw its tree and deliberately find three mistakes in a copied practice fragment. Explain each correction rather than replacing the entire file.",essentials,"Use this as a comparison only after your attempt. Explain declaration, language, encoding, viewport, title and body elements.","html","Tab and heading: My learning notes\nParagraph: I can explain each part of this document."],
 ready:"You can write a correctly nested complete document and find a missing closing tag. Carry any unclear topic into a focused repeat before Week 4.",
 reflection:"Save the three mistakes you repaired, your document tree and the line you most need to practise again.",
 quiz:[
  ["What is a complete p element?","<p>Text</p>","Only <p>","Only Text","An element includes structure and content."],
  ["Which is void?","meta","h1","title","meta takes no end tag."],
  ["What is <html> in the shell?","Root element","Tab title","Paragraph","head and body sit within it."],
  ["Which is metadata?","The title element in head","A visible paragraph","The file manager icon","title describes the document."],
  ["Which value quotes a phrase correctly?","title=\"My next step\"","title=My next step","title=“My next step”","Use matching straight delimiters."],
  ["Which label may be shared by several elements?","class","id","The file extension","An id should identify one element."],
  ["Which relation is correct?","head and body are siblings","h1 always contains the next p","title contains body","Containment defines the tree."],
  ["Which nesting needs repair?","p inside p","p inside body","title inside head","Paragraphs cannot contain other paragraphs."],
  ["What does lang identify?","Human language","Byte encoding","CSS layout","Language and encoding are different settings."],
  ["What does UTF-8 concern?","Text encoding","Automatic translation","Server passwords","Save bytes and declare their encoding."],
  ["Should viewport settings block user zoom?","No","Yes","Only during study","Keep zoom accessible."],
  ["What proves a lasting source edit?","The saved file retains it on reopening","Only a temporary DOM change","Only no Console errors","Check the actual file, not a transient view."]
 ]});
module.exports={lessons,examples:{essentials,about,reading}};
