const {p,key,tip,warn,term,code,out,mistake,page,lesson}=require('./web-development-teaching-tools.cjs');
const articleBody="    <header>\n      <p>My study notebook</p>\n      <nav>\n        <a href=\"#plan\">Plan</a>\n        <a href=\"#review\">Review</a>\n      </nav>\n    </header>\n    <main>\n      <article>\n        <h1>A steady learning routine</h1>\n        <p>I learn more when I take <em>one clear step</em> at a time.</p>\n        <section id=\"plan\">\n          <h2>My plan</h2>\n          <ol>\n            <li>Read one idea.</li>\n            <li>Try it without copying.</li>\n            <li>Check and explain the result.</li>\n          </ol>\n        </section>\n        <section id=\"review\">\n          <h2>My review</h2>\n          <p><strong>Keep the original project safe.</strong></p>\n          <ul>\n            <li>Recall the idea from memory.</li>\n            <li>Repair one mistake at a time.</li>\n          </ul>\n        </section>\n      </article>\n    </main>\n    <footer>\n      <p>Written for my own learning practice.</p>\n    </footer>";
const article=page("A steady learning routine | My notebook",articleBody);
const lists=page("My practice lists","    <h1>My practice lists</h1>\n    <h2>Preparation</h2>\n    <ul>\n      <li>Open my project folder.</li>\n      <li>Prepare my tools.\n        <ul>\n          <li>Text editor</li>\n          <li>Browser</li>\n        </ul>\n      </li>\n    </ul>\n    <h2>Workflow</h2>\n    <ol>\n      <li>Edit one thing.</li>\n      <li>Save the file.</li>\n      <li>Reload and check.</li>\n    </ol>");
const lessons={},add=(day,d)=>lessons['5.'+day]=lesson(5,day,d);
add(1,{
 title:"Headings and page outline",objective:"Choose heading levels for meaning and build a readable outline independent of text size.",
 parts:[
 ["A heading tells you what follows",[
  p("Imagine scanning a long study notebook for the practice section. A meaningful heading lets you find it without reading every sentence. Heading elements also give navigation clues to assistive tools. Their job is structure, even though browsers give them different default sizes."),
  term("Heading hierarchy","A relationship between headings: h1 is the highest level, then h2 through h6. Use levels to show sections and subsections. For our simple pages use one main h1 and h2 sections underneath."),
  code("<h1>My HTML notebook</h1>\n<h2>Reading source</h2>\n<p>I identify tags and attributes.</p>\n<h2>My practice</h2>\n<p>I build a small document.</p>","html"),
  out("Outline:\n1. My HTML notebook\n   1.1 Reading source\n   1.2 My practice"),
  p("The numbers in this outline explain the relationships; they are not automatically printed by the h elements. Do not type an h3 merely because you want a smaller font. CSS will handle appearance later.")
 ]],
 ["Add a real subsection",[
  term("Subsection","A smaller topic within a section. In our outline, an h3 is appropriate under an h2 when its subject is part of that h2 topic."),
  code("<h1>My HTML notebook</h1>\n<h2>My practice</h2>\n<h3>Before opening the browser</h3>\n<p>I save the correct file.</p>\n<h3>After opening the browser</h3>\n<p>I compare the expected result.</p>\n<h2>My review</h2>\n<p>I explain mistakes.</p>","html"),
  p("The two h3 headings belong to My practice. The next h2 starts a new section at the same level as My practice. You can move back up levels when a subsection ends. Avoid skipping down from h1 to h4 just for a visual size."),
  p("One main h1 is our clear beginner convention, not a claim that a browser refuses every document with multiple h1 elements. Write headings that describe the actual content and review their relationships."),
  key("Choose the level from the relationship; choose the words from the topic.")
 ]],
 ["Audit the outline before styling",[
  mistake("<h1>My goals</h1>\n<h4>Daily practice</h4>","<h1>My goals</h1>\n<h2>Daily practice</h2>","Daily practice is a direct section, so use the next appropriate level rather than jumping down for size."),
  p("Read only the headings in order. Do they describe the document without the paragraphs? Replace vague labels like Stuff with a useful description such as My save-and-check workflow. A heading is not useful merely because it is short or large."),
  code("Outline audit:\n[ ] One clear main topic\n[ ] Sections at consistent levels\n[ ] Subsections fit their parent topic\n[ ] Descriptive wording\n[ ] No level chosen only for visual size"),
  tip("Use your editor to list the h elements or inspect them in Elements. You do not need a script or a styling framework to audit the outline."),
  p("Keep paragraphs under the headings they explain. Correct hierarchy helps both the source reader and the person scanning the page.")
 ]]
 ],
 practice:[
  ["Choose the level.","Main topic is h1; a direct section is Daily practice.","Use h2 for Daily practice.","It is one level below the main topic."],
  ["Choose the subsection level.","h2 is My practice; a smaller topic is Checking saved files.","Use h3 for that subsection.","It is inside the h2 topic."],
  ["Repair a visual-size choice.","<h1>Plan</h1><h5>Daily work</h5>","<h1>Plan</h1><h2>Daily work</h2>","Use the relationship rather than font size.","html"],
  ["Does returning h3 → h2 break the hierarchy?","A subsection ends and a new main section starts.","No. Moving back up is appropriate.","Avoid confusing a return to the parent level with a skipped descent."],
  ["Improve the heading text.","<h2>Stuff</h2> above a debugging checklist.","<h2>My debugging checklist</h2>","Describe what the reader will find.","html"]
 ],
 challenge:["Outline your own study page","Write an h1, two h2 sections and two h3 subsections under one h2. Add a short paragraph per section. Explain each level before opening the browser.","<h1>My study routine</h1>\n<h2>My practice</h2>\n<h3>Preparation</h3>\n<p>I open the right file.</p>\n<h3>Checking</h3>\n<p>I save and compare the result.</p>\n<h2>My review</h2>\n<p>I recall what I learned.</p>","The two h3 headings belong to My practice. My review returns to h2.","html"],
 ready:"Read an outline aloud and explain why each heading has its level without referring to font size.",
 reflection:"Save your outline and one heading you improved. How would a reader find the practice section quickly?",
 quiz:[
  ["What should determine a heading level?","Its structural relationship","Only desired font size","The number of letters","Levels communicate hierarchy."],
  ["Which is a direct section under our main h1?","h2","h6","p","Use the next appropriate level."],
  ["Which is a subsection under h2?","h3","h1","title","The hierarchy descends one level."],
  ["Can h3 be followed by h2 when starting a new section?","Yes","No","Only with JavaScript","Returning up the hierarchy is normal."],
  ["Which heading is more informative?","My debugging checklist","Stuff","More","Descriptive words help scanning."],
  ["Do h elements automatically print the outline numbers shown here?","No","Yes","Only when offline","Those numbers are an explanatory diagram."]
 ]});
add(2,{
 title:"Paragraphs and emphasis",objective:"Use p, strong and em for meaning and explain why spaces or styling alone do not create semantic structure.",
 parts:[
 ["One paragraph, one connected thought",[
  p("A paragraph groups connected prose. When the subject changes, a new paragraph helps readers follow it. Pressing Enter several times in the source does not create several p elements. In ordinary HTML text, runs of whitespace usually collapse."),
  term("Paragraph and collapsed whitespace","p marks a paragraph. Ordinary source spaces and newlines are generally collapsed when displayed, so source formatting and document structure are different."),
  code("<p>I practise one skill.\nThen I check the result.</p>\n<p>Tomorrow I will repeat the difficult part.</p>","html"),
  out("First paragraph: I practise one skill. Then I check the result.\nSecond paragraph: Tomorrow I will repeat the difficult part."),
  p("Do not put headings, lists or other paragraphs inside p. You can put phrasing elements such as em and strong around words within a paragraph. Those elements give the text an additional meaning.")
 ]],
 ["Stress versus importance",[
  term("em","Marks stress emphasis: words you would emphasise when speaking to affect the sentence meaning. Browsers often show it in italics, but italic appearance is not its definition."),
  term("strong","Marks importance, seriousness or urgency. Browsers often show it in bold. Do not use it only because you want a heavier-looking font."),
  code("<p>I meant <em>this</em> saved file.</p>\n<p><strong>Keep a copy before the repair.</strong></p>","html"),
  p("The first sentence stresses which file. The second highlights an important instruction. If the only goal is visual styling, learn the relevant CSS later. Choose the element because it expresses meaning even when default styling changes."),
  code("<p><strong>Important:</strong> check the <em>same</em> file after saving.</p>","html")
 ]],
 ["Break a line only when the content needs it",[
  term("br","A void line-break element. It is useful where a line boundary is part of the content, such as an address or poem. It is not a substitute for separate paragraphs or layout spacing."),
  code("<p>Practice room<br>Second floor</p>","html"),
  out("Practice room\nSecond floor"),
  mistake("<p>First idea.<br><br>Another topic.</p>","<p>First idea.</p>\n<p>Another topic.</p>","Separate topics should be separate paragraphs. Use CSS later for spacing."),
  key("Use p for paragraphs, em for stress and strong for importance. Structure should remain meaningful without relying only on appearance.")
 ]]
 ],
 practice:[
  ["Predict ordinary whitespace.","<p>Read\n    and practise.</p>","Read and practise.","The source newline is not a separate paragraph.","html"],
  ["Choose stress emphasis.","You want to stress the word same.","<p>Check the <em>same</em> file.</p>","em gives spoken-style emphasis.","html"],
  ["Choose importance.","A warning says keep a copy before repair.","<p><strong>Keep a copy before repair.</strong></p>","strong expresses importance.","html"],
  ["Repair fake paragraph spacing.","<p>A.<br><br>B.</p>","<p>A.</p>\n<p>B.</p>","Use paragraphs for separate prose ideas.","html"],
  ["Does br need </br>?","<br>","No. It is void.","It creates a line break rather than containing text.","html"]
 ],
 challenge:["Make meaning visible in source","Write two paragraphs about your study routine. Add one genuine stress emphasis and one important instruction. Explain why each element is justified.","<p>I check the <em>saved</em> file, not only a temporary view.</p>\n<p><strong>Keep the working original safe.</strong> I practise in a copy.</p>","The first stresses which file state matters. The second marks an important instruction.","html"],
 ready:"Distinguish a paragraph from a source newline and choose em or strong based on meaning rather than default font style.",
 reflection:"Write two sentences where changing stress changes the meaning. Explain when br is appropriate.",
 quiz:[
  ["Which creates a paragraph?","p","Several source newlines alone","Only a title attribute","Paragraphs are elements."],
  ["Which marks stress emphasis?","em","strong in every case","meta","Stress and importance differ."],
  ["Which marks importance or urgency?","strong","br","title attribute","Use semantic meaning."],
  ["Is italic appearance the definition of em?","No","Yes","Only on phones","Presentation can change."],
  ["Which is a good br use?","An intentional line break in an address","Spacing between unrelated topics","A replacement for every p","Use line breaks where the boundary belongs to content."],
  ["Can p contain a heading?","No","Yes, for boldness","Only if short","Heading structure belongs outside the paragraph."]
 ]});
add(3,{
 title:"Lists",objective:"Choose ordered, unordered and description lists and nest a sublist inside its parent item.",
 parts:[
 ["Order is a meaning choice",[
  term("ul and li","ul marks an unordered list, where item sequence is not essential to the meaning. li marks each list item. Browsers often display bullets, but the structural grouping is the main point."),
  term("ol","An ordered list, where sequence or rank matters. It also contains li items. Browsers normally display numbers, but you should choose it because order matters."),
  code("<ul>\n  <li>Text editor</li>\n  <li>Browser</li>\n</ul>\n<ol>\n  <li>Edit the file.</li>\n  <li>Save it.</li>\n  <li>Reload and check.</li>\n</ol>","html"),
  p("The tools list can be read in either order. The workflow cannot: reloading before saving may show old contents. Do not type literal bullet symbols or 1., 2., 3. into a paragraph to imitate a structural list."),
  out("Tools: two grouped items.\nWorkflow: three ordered steps.")
 ]],
 ["Nest within the item it explains",[
  code("<ul>\n  <li>Prepare the tools.\n    <ul>\n      <li>Open the editor.</li>\n      <li>Open the browser.</li>\n    </ul>\n  </li>\n  <li>Begin practice.</li>\n</ul>","html"),
  p("The inner ul is inside the first outer li. Keep that li open until its sublist ends. This says the two tool actions belong to Prepare the tools. Indent the inner list to reveal that relationship."),
  mistake("<ul>\n  <li>Prepare tools.</li>\n  <ul><li>Editor</li></ul>\n</ul>","<ul>\n  <li>Prepare tools.\n    <ul><li>Editor</li></ul>\n  </li>\n</ul>","Put a nested list within the li whose subject it expands."),
  p("For ordinary list content, ul and ol have li children, not bare paragraphs replacing list items. A list item can contain text and suitable additional content, including paragraphs or a nested list."),
  key("Close the inner list before closing its containing item, then continue with the next outer item.")
 ]],
 ["An additional tool for terms and descriptions",[
  term("dl, dt and dd","dl groups terms/names and descriptions. dt marks the term; dd marks its description. Use this when the content is an association such as a small glossary, not a ranked sequence."),
  code("<dl>\n  <dt>HTML</dt>\n  <dd>Content structure and meaning.</dd>\n  <dt>CSS</dt>\n  <dd>Presentation and layout.</dd>\n</dl>","html"),
  p("This glossary has term/description relationships rather than steps. Do not use li inside dl as if every list had the same child elements. A description list can be more complex, but these simple pairs are enough for now."),
  tip("Read your list without its visual markers. If the order still matters, use ol. If the content is a group with no required order, use ul."),
  p("Lists make repeated items easier to scan and easier for tools to recognise. Choose them for content relationships, not merely to indent text.")
 ]]
 ],
 practice:[
  ["Choose ul or ol.","A list of tools with no required sequence.","ul with li items.","Order is not essential."],
  ["Choose ul or ol.","Steps to save and then reload.","ol with li items.","Sequence matters."],
  ["Where does a sublist belong?","A sublist expands Prepare tools.","Inside the Prepare tools li.","It belongs to that item."],
  ["Repair the child.","<ul><p>Browser</p></ul>","<ul><li>Browser</li></ul>","A normal list item uses li.","html"],
  ["Choose a glossary structure.","Term HTML with a description.","dl containing dt and dd.","Term/description association differs from a numbered workflow."],
  ["Explain why typed numbers are weaker structure.","<p>1. Edit 2. Save 3. Check</p>","Use an ol and separate li elements.","The relationship should be in markup, not only text appearance.","html"]
 ],
 challenge:["Build a preparation list and workflow","Write an unordered preparation list with one nested sublist, then an ordered three-step workflow. Optionally add a two-term glossary.",lists,"This is a full example document. Explain each li relationship and why the workflow uses ol.","html","One main heading; a preparation list with a nested tools list; an ordered edit/save/check workflow."],
 ready:"Choose ul, ol or dl from the content relationship and correctly nest a sublist within an li.",
 reflection:"Save your lists and draw the parent of each nested ul. Explain one case where order changes the meaning.",
 quiz:[
  ["Which list communicates essential sequence?","ol","ul in every case","p","Ordered steps have meaningful sequence."],
  ["Which element marks an ordinary ul item?","li","dt","meta","ul and ol use li items."],
  ["Where does a nested list belong?","Inside its containing li","As a bare sibling of li under ul","Inside head","The sublist expands one item."],
  ["Which is appropriate for term/description pairs?","dl with dt and dd","ol with title","Only line breaks","Use the relationship-specific structure."],
  ["Should you choose ul only to indent a sentence?","No","Yes","Only on desktop","Markup should express content meaning."],
  ["Why use real list markup instead of typed numbers?","Tools can recognise the structure","It guarantees perfect design","It automatically creates a database","Semantic relationships are represented explicitly."]
 ]});
add(4,{
 title:"Semantic regions",objective:"Use header, main, footer, nav and section to describe page regions and connect a small in-page navigation example.",
 parts:[
 ["Describe the page's regions",[
  term("Semantic HTML","Choosing elements that express the meaning of content. A page region can be identified as main content or navigation rather than only as a generic box."),
  term("header, main and footer","header introduces a page or section. main identifies the dominant content of the document; use one visible main in these simple pages. footer holds closing information for its page or section, such as authorship. header is not the head metadata element."),
  code("<body>\n  <header><p>My study notebook</p></header>\n  <main>\n    <h1>My practice routine</h1>\n    <p>I learn one idea and test it.</p>\n  </main>\n  <footer><p>Written for my own practice.</p></footer>\n</body>","html"),
  p("These names do not automatically create columns, a fixed top bar or a sticky footer. They describe roles. CSS will later style and position them. Keep a page usable with its natural reading order first."),
  out("Reading order: introduction → main heading/content → closing note.")
 ]],
 ["Group related topics",[
  term("section","A thematic grouping within a document, usually identified by a heading. Use it for a meaningful section, not for every wrapper needed only for styling."),
  code("<main>\n  <h1>My routine</h1>\n  <section id=\"plan\">\n    <h2>My plan</h2>\n    <p>Read, try and check.</p>\n  </section>\n  <section id=\"review\">\n    <h2>My review</h2>\n    <p>Recall the idea again.</p>\n  </section>\n</main>","html"),
  p("The section headings remain h2 because they are below the page h1. A section element does not automatically reset heading levels. Its id can identify the section as a fragment target."),
  term("Landmark","A recognisable page region exposed to assistive technology, such as the main content or navigation. Appropriate native elements help users move around a page; not every section becomes a landmark merely by existing."),
  key("Use regions that describe actual content. A section should have a subject you can name.")
 ]],
 ["Make a small navigation example",[
  term("nav","A region containing major navigation links. Not every isolated link needs its own nav. For this single-page notebook, a small contents navigation is a useful example."),
  term("a and href","a with an href creates a hyperlink. href gives its destination. In href=\"#plan\", #plan refers to the element whose unique id is plan in the same document. Link text tells the reader where the link goes."),
  code("<nav>\n  <a href=\"#plan\">Plan</a>\n  <a href=\"#review\">Review</a>\n</nav>","html"),
  p("Place this nav in the header above the main example. It uses the ids already shown. Click Plan: the browser can move to that target. Use Tab to focus links and Enter to activate one. If the entire short page already fits, the jump may not visibly scroll."),
  p("This is an explained first link example so the nav is functional. More detailed links, external destinations and path management belong to later lessons. Keep the native link instead of a script-controlled text imitation.")
 ]]
 ],
 practice:[
  ["Distinguish the similar names.","head versus header","head: document metadata. header: introductory content region.","They have different roles."],
  ["Choose the main content region.","Your central study article.","main.","Use one visible main in this simple document."],
  ["Should every styling wrapper be section?","A box has no thematic subject.","No. Use section when it groups a real topic.","Generic wrappers are covered next."],
  ["Connect the destination.","<section id=\"plan\"> ... </section>","<a href=\"#plan\">Plan</a>","The fragment matches the unique id.","html"],
  ["Does section automatically reset h2 to h1?","A section is inside main under a page h1.","No. Keep a deliberate heading hierarchy.","Section nesting does not replace heading-level decisions."],
  ["Why might clicking Plan appear to do nothing?","The whole document fits the screen.","The target may already be visible; also verify matching id/href.","A lack of scrolling is not by itself proof the link failed."]
 ],
 challenge:["Give your notebook meaningful regions","Wrap your introduction in header, central content in main and closing note in footer. Add Plan and Review sections with h2 headings and a nav with matching fragment links.","header → notebook introduction and nav\nmain → h1, section#plan with h2, section#review with h2\nfooter → authorship or closing note\nnav links → #plan and #review","Use real elements and native links. The full Week 5 project demonstrates this arrangement."],
 ready:"Explain region roles, keep headings deliberate and connect a fragment link to a unique section id.",
 reflection:"Draw the regions in reading order. Explain why header and head are not interchangeable and test both nav links.",
 quiz:[
  ["Which contains metadata?","head","header","main","head is distinct from the content header."],
  ["Which marks the dominant page content?","main","Every div","title","Use the semantic region appropriately."],
  ["What does section usually group?","A named thematic topic","Any arbitrary colour box","Only scripts","A heading helps identify its subject."],
  ["What is nav for?","Major navigation links","All bold text","Private notes","Use it for navigation regions."],
  ["What does href=\"#review\" target?","The element with id=\"review\"","A class named review automatically","A new server named review","The fragment refers to a matching id."],
  ["Do semantic regions automatically create a styled layout?","No","Yes, always a grid","Only on phones","CSS handles appearance and positioning."]
 ]});
add(5,{
 title:"Choosing elements",objective:"Choose meaningful elements before generic wrappers and distinguish a standalone article from a thematic section.",
 parts:[
 ["Ask what the content means",[
  p("Start with a sentence about the content: This is a set of steps, this is a paragraph, this is a navigation region. Then choose the element. Starting with I want a green rectangle skips the meaning decision and makes a page harder to understand."),
  code("Meaning → candidate element\nMain title → h1\nConnected prose → p\nImportant instruction → strong\nOrdered steps → ol with li\nMain navigation → nav with links\nDominant document content → main"),
  term("article","A self-contained composition that could make sense independently, such as a study article or post. It can contain sections with headings. It does not mean every small piece of text should be an article."),
  p("A notebook article explaining a routine can be independently readable. My plan and My review are thematic sections inside that article. Ask whether the content would still have a coherent purpose outside its current page."),
  key("Choose by content relationship, then decide whether any extra grouping is actually needed.")
 ]],
 ["Use generic wrappers when appropriate",[
  term("div","A generic container with no special content meaning. In ordinary browser styling it is a block-level box. Use it when grouping is needed and no more appropriate semantic element describes the content."),
  term("span","A generic phrasing container, commonly inline by default. Use it to identify a small text range without adding an emphasis or importance meaning. It does not automatically colour or emphasise the text."),
  code("<div class=\"study-group\">\n  <p>Topic: <span class=\"topic-name\">HTML structure</span></p>\n  <p>Next step: practise.</p>\n</div>","html"),
  p("class values are labels for later styling or behaviour. In this example the div groups related elements and span labels a text range. The default block/inline appearances are CSS defaults, not unchangeable semantic definitions."),
  p("A wrapper is optional if it adds no useful grouping. A page with headings and paragraphs does not need a div around every sentence. Keep the structure as clear as the content requires.")
 ]],
 ["Repair an appearance-first choice",[
  mistake("<div>My main heading</div>","<h1>My main heading</h1>","A main heading should carry heading meaning, even if a generic div could later be styled to look similar."),
  mistake("<span>Keep a copy before repairing.</span>","<strong>Keep a copy before repairing.</strong>","If the content is an important instruction, express importance rather than only wrapping the text."),
  p("A section is not interchangeable with a div: section groups a meaningful topic, usually with a heading. An article is not required just because a box has a border. Keep semantic decisions separate from decorative boxes."),
  tip("Native elements often provide useful built-in semantics. Do not add complex roles or custom click behaviour to imitate a link or heading you can write directly."),
  code("Decision questions:\nWhat is this content?\nIs there an element that says that directly?\nDoes a group have a named topic?\nCould this composition stand alone?\nDo I need a generic wrapper at all?")
 ]]
 ],
 practice:[
  ["Choose the element.","A sequence of steps to open a file.","ol with li.","The sequence matters."],
  ["Choose the element.","A standalone study article.","article, with appropriate headings/content.","It is independently meaningful."],
  ["Choose section or div.","A titled topic inside an article.","section with a heading.","The grouping has a thematic subject."],
  ["Choose a neutral text wrapper.","A word range needs a label but no added emphasis.","span.","Do not invent semantic emphasis for a neutral label."],
  ["Repair fake heading meaning.","<div class=\"big\">My goal</div>","<h1>My goal</h1>","Visual size alone does not provide heading semantics.","html"],
  ["Does a span automatically become red?","<span class=\"red\">HTML</span>","No. A class is a label; CSS would have to define presentation.","Use a class name for a real purpose.","html"]
 ],
 challenge:["Explain six choices","Review your planned Week 5 article. Identify one heading, paragraph, list, important instruction, section and article. Justify each. Remove any generic wrapper that has no purpose.","h1 → main article topic\np → connected prose\nol → sequenced learning steps\nstrong → important preservation instruction\nsection → a named topic such as My plan\narticle → complete independently readable routine","A clean result may use no div or span at all. They remain useful when generic grouping is genuinely needed."],
 ready:"Choose semantic elements by meaning and use div/span deliberately rather than as substitutes for headings, lists or emphasis.",
 reflection:"Save six element choices with reasons. Write one legitimate div use and one case where a semantic element is clearer.",
 quiz:[
  ["Which can represent a standalone composition?","article","Every span","meta","An article can make sense independently."],
  ["Which is a generic container?","div","h1","nav","div has no special content role."],
  ["Which is a generic phrasing wrapper?","span","main","ol","span can label a small text range."],
  ["Does class=\"red\" supply semantic importance?","No","Yes","Only inside div","A class label does not create importance."],
  ["Which best marks a main heading?","h1","A big-looking div","Several br elements","Use native heading structure."],
  ["When should you use section?","For a meaningful thematic grouping","For every decorative box","For every word","A section normally has a subject identified by a heading."]
 ]});
add(6,{
 title:"Build a study article",objective:"Combine headings, prose, emphasis, lists, regions and working in-page navigation into one accessible beginner document.",
 parts:[
 ["Plan the content and outline",[
  p("Create study-article.html in your practice folder. The article should help a beginner follow your learning routine. Write the content plan before markup: introduction, ordered plan, review checklist and a closing authorship note."),
  code("Page: My study notebook\nArticle h1: A steady learning routine\nSection h2: My plan\nSection h2: My review\nNavigation: Plan and Review\nFooter: authorship note"),
  p("Use the main language of your actual text on html. Keep UTF-8, the standard viewport line and a useful title. Choose native elements first; polished CSS comes later after the content foundation."),
  term("Reading order","The sequence in which content appears in the source and is normally encountered by a reader or assistive technology. Keep it sensible before any visual rearrangement."),
  key("Content plan → outline → semantic markup → save/open → source and interaction checks.")
 ]],
 ["Build in small stages",[
  p("First create the full document shell and h1. Save and open it. Then add the Plan section with an ordered list. Add Review with a paragraph and unordered list. Finally add header/nav, article grouping and footer. Check after each addition."),
  code(article,"html"),
  out("Tab: A steady learning routine | My notebook\nPage: notebook introduction and two links\nMain article: heading, introduction, ordered plan and review list\nClosing authorship note"),
  p("The nav links match the unique section ids. The article is self-contained inside main. Its h2 sections remain below h1. strong marks an important instruction; em stresses a useful phrase. The lists express sequence and unordered review items."),
  tip("This is a complete working HTML example with no external resources. Type your own version before comparing. You may split the project across multiple sessions.")
 ]],
 ["Check content, structure and interaction",[
  code("Acceptance checks:\n[ ] Exact saved filename and useful title\n[ ] Root language, UTF-8 and viewport\n[ ] One clear h1 with h2 sections\n[ ] Meaningful p, em and strong usage\n[ ] Correct ol/ul with li children\n[ ] header, nav, main, article, section, footer roles\n[ ] Unique ids and matching fragment links\n[ ] Links work with mouse and Tab/Enter\n[ ] Natural reading order and zoom remain usable\n[ ] Reopen/reload retains every sentence"),
  p("Use Tab to focus Plan and Review, then Enter. Inspect each target id if a link does not work. On a short page the target can already be visible; the address fragment still gives useful evidence. Do not add JavaScript just to produce a bigger visual jump."),
  p("Resize the browser and zoom the simple document. Text should wrap naturally without your own fixed-width layout. Read the headings alone to audit the outline. Check saved source and the live tree as complementary evidence."),
  warn("Do not replace your earlier practice pages or Study Hub with this project. Keep it as a new file so you can compare your progress."),
  key("A finished article is meaningful, navigable and explainable before decoration.")
 ]]
 ],
 practice:[
  ["Explain the ordered choice.","Read → try → check.","Use ol because the sequence is meaningful.","The numbered order communicates the workflow."],
  ["Explain the unordered choice.","Two review reminders with no required sequence.","Use ul.","The items form a group rather than a procedure."],
  ["Find a broken fragment.","href=\"#review\" but id=\"reviews\".","Make href and unique id agree, such as review.","The destination names differ."],
  ["Find the region mistake.","The important article content is outside main; main is empty.","Place the dominant article content within main.","Use the region to describe actual content."],
  ["Explain article versus section.","A complete routine contains Plan and Review topics.","The routine can be article; Plan and Review can be sections.","Composition and subtopics have different scopes."],
  ["Test a native link without a mouse.","Plan link is in nav.","Press Tab to focus it and Enter to activate.","Native links include keyboard behaviour."]
 ],
 challenge:["Finish and teach your article","Build the document in your own words. Then walk through the source aloud, explaining every element and why the lists use their chosen forms. Test both links and save a final acceptance checklist.",article,"The example is one valid structure. Your text can differ as long as each semantic choice matches the actual content.","html","A complete article with two working in-page destinations, meaningful headings, prose, emphasis and lists."],
 ready:"Reopen a complete article, navigate it by keyboard and explain each element choice without referring only to appearance.",
 reflection:"Record the file location, your outline and both link test results. What would you improve with CSS later, without changing the semantic meaning?",
 quiz:[
  ["What should precede decorative styling?","A meaningful content structure","Random wrappers around every word","A database","The project focuses on HTML meaning."],
  ["What must match an in-page link?","The target id and fragment","The class and filename only","The tab colour","href=\"#plan\" points to id=\"plan\"."],
  ["Which structure represents the complete routine?","article within main","Only a title attribute","Only br elements","An independently readable composition fits article."],
  ["How can you test the link with a keyboard?","Tab to focus, Enter to activate","Only hover","Only rename the file","Native links support keyboard use."],
  ["Which preserves a sensible reading order?","Source follows introduction, plan and review","Randomise source and hope","Hide every heading","Structure should be readable before styling."],
  ["What should final verification include?","Save/reopen, structure and link checks","Only a screenshot","Only a large heading","Persistent and usable behaviour matters."]
 ]});
add(7,{
 title:"Week 5 review and semantic workshop",objective:"Rebuild the article, repair semantic and list mistakes, and justify the outline in your own words.",
 parts:[
 ["Recall the choices before seeing the answer",[
  p("Write a meaning-to-element table from memory. Include headings, paragraphs, emphasis, importance, lists, regions, article and generic wrappers. Use a concrete sentence or content group for each. If a choice depends only on desired colour or size, reconsider it."),
  code("Main title → ?\nConnected prose → ?\nStress emphasis → ?\nImportant instruction → ?\nOrdered steps → ?\nUnordered tools → ?\nTerm/description → ?\nDominant content → ?"),
  p("Then rebuild a shortened study article from a blank file. Keep a full shell. Use at least two h2 sections, one ordered list, one unordered list and meaningful region elements."),
  term("Semantic audit","Checking whether element choices express the actual content relationships. A page can look similar while communicating a different structure to tools and readers."),
  key("Explain each choice in terms of meaning, not only its default visual style.")
 ]],
 ["Inspect the tree and interactions",[
  p("Read headings alone. Check list children and nested list parents. Inspect unique ids and the two fragment links. Verify the document title is not confused with h1 or a title attribute."),
  code("Review sequence:\n1. Outline\n2. Paragraph and emphasis meaning\n3. List structure\n4. Page regions\n5. Links and ids\n6. Saved source and reading order"),
  p("The extra glossary pattern dl/dt/dd is for associations. It does not replace ol for steps. br is a line break, not a paragraph or spacing system. A div can group content but does not become a heading because it is big."),
  tip("Use the same small-step debugging log from Week 4 if you find a defect. Correct a specific issue and preserve the rest of your article."),
  warn("Do not remove useful sentences to make a difficult structural problem disappear. Repair the relationships.")
 ]],
 ["Finish the five-week foundation",[
  p("Explain how your file reaches the browser using Week 2 concepts. Explain its shell with Week 3 concepts. Describe one repair using Week 4's method. Then justify the semantic structure with Week 5. The topics should now connect into one coherent workflow."),
  out("Retain: full article file, outline, element-choice table,\nkeyboard link results and one documented repair."),
  p("These five weeks do not cover all of web development. Continue with the next roadmap topics after this foundation is comfortable. Keep unanswered questions in notes and repeat any workshop item that still requires guessing."),
  p("A strong result is a simple page you can create, explain, reopen, inspect and improve safely. Visual polish can be added progressively as the relevant CSS topics are learned."),
  key("The checkpoint is to choose elements for meaning and explain the outline of your own page.")
 ]]
 ],
 practice:[
  ["Choose a main heading.","My learning routine is the main page topic.","h1.","Use heading meaning, not a generic big box."],
  ["Choose a direct section level.","My plan is under the page's h1.","h2.","One level below the main topic."],
  ["Choose a subsection.","Preparation is within My plan h2.","h3.","It is a subtopic of that section."],
  ["Repair a skipped descent.","h1 immediately followed by h5 for a direct section.","Use h2 for that section.","Do not choose the level for size."],
  ["Choose stress.","You mean this file, not another.","em around this.","The stress affects the sentence meaning."],
  ["Choose importance.","A serious instruction says keep a copy.","strong.","It marks importance or urgency."],
  ["Repair fake paragraphs.","<p>A<br><br>B</p>","<p>A</p><p>B</p>","Use separate prose paragraphs.","html"],
  ["Choose a line break.","Two lines of a room address.","br can mark the intentional line boundary.","The break is part of content."],
  ["Choose a list.","Tools in no required order.","ul with li.","The group has no essential sequence."],
  ["Choose a list.","Save before reload.","ol with li.","Order changes the workflow."],
  ["Repair a bare list child.","<ul><p>Editor</p></ul>","<ul><li>Editor</li></ul>","Use normal list item structure.","html"],
  ["Place the nested list.","Tools sublist belongs to Preparation.","Inside the Preparation li before its closing tag.","The nesting reflects ownership."],
  ["Choose a glossary.","HTML paired with its description.","dl with dt and dd.","This is a term/description association."],
  ["Distinguish two names.","head versus header","head holds metadata; header introduces content.","Similar words have different roles."],
  ["Choose a thematic group.","My review has its own heading and related content.","section.","It is a named topic."],
  ["Choose the standalone composition.","The whole learning routine can be reused independently.","article.","It forms a self-contained composition."],
  ["Choose a generic wrapper.","A neutral word range needs a label.","span.","It adds no stress or importance meaning."],
  ["Repair a fragment mismatch.","href=\"#plan\" with id=\"plans\".","Use matching plan values, keeping the id unique.","Fragments identify a specific target."],
  ["Test without a mouse.","You need to activate the Review link.","Tab to focus it, Enter to activate.","Use the native keyboard behaviour."],
  ["Explain what region elements do not supply.","header, main and footer are present.","They do not automatically create a polished positioned layout.","Meaning and CSS presentation are separate responsibilities."]
 ],
 challenge:["Pass the semantic checkpoint","Rebuild your own article and explain its outline. Include a meaningful list choice, a genuine emphasis choice, two working fragment links and one documented repair. Compare only after trying.",article,"Your article should retain natural reading order, useful metadata, unique targets and meaningful native elements. Explain any variation from the sample.","html"],
 ready:"Choose elements for meaning and explain the page outline. Repeat uncertain items before proceeding to the next roadmap week.",
 reflection:"Save your final outline, three justified choices and one weak item to revisit. Explain how the first five weeks now fit together.",
 quiz:[
  ["Which should decide heading level?","Content hierarchy","Only size","Only word count","Structure comes first."],
  ["Which marks stress?","em","div","meta","em communicates stress emphasis."],
  ["Which marks importance?","strong","span automatically","br","strong communicates importance or urgency."],
  ["Which marks ordered steps?","ol with li","A paragraph with typed numbers only","dl with meta","Use a sequence structure."],
  ["Where should a nested ul go?","Inside its parent li","Directly beside li under ul","Inside title","The sublist belongs to an item."],
  ["Which is for a glossary?","dl, dt and dd","Only ul in every case","Only p with spaces","Term/description pairs have their own structure."],
  ["Which is the dominant content region?","main","head","Every span","Use one visible main for these simple pages."],
  ["Which describes a thematic group?","section","charset","br","A section has a coherent subject."],
  ["Which describes a self-contained composition?","article","A class name alone","Every div","An article can stand independently."],
  ["Which is generic phrasing?","span","h1","nav","span carries no special semantic role."],
  ["What must a fragment link match?","A unique target id","A random visible word","Only the document title","The href fragment names the target id."],
  ["What proves readiness?","Explain, rebuild and check your own article","Only recognise a copied page","Only click complete","The checkpoint tests understanding and application."]
 ]});
module.exports={lessons,examples:{article,lists}};
