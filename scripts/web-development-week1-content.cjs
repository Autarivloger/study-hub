// Original beginner teaching. No terminal, CSS or JavaScript syntax is assumed.
const h=v=>({t:'h',v}),p=v=>({t:'p',v}),key=v=>({t:'key',v}),tip=v=>({t:'tip',v}),warn=v=>({t:'warn',v});
const term=(v,note)=>({t:'new',v,note});
const code=(v,lang='text')=>({t:'code',v,lang});
const out=v=>({t:'out',v});
const mistake=(wrong,right,why)=>({t:'mis',wrong,right,why,lang:'text'});
const solution=(v,why,lang='text',output)=>({t:'sol',code:v,why,lang,...(output?{out:output}:{})});
const exercise=(q,code,a,why,lang='text')=>({t:'try',q,code,a,why,lang});
const quiz=(q,answer,a,b,why,i=0)=>{const options=[answer,a,b],n=i%3;return{q,options:options.slice(n).concat(options.slice(0,n)),correct:(3-n)%3,why};};
const skeleton=(title,body)=>`<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>${title}</title>
  </head>
  <body>
${body}
  </body>
</html>`;
const first=skeleton('My first page','    <h1>My learning page</h1>\n    <p>I am learning web development.</p>');
const revised=skeleton('My web journey','    <h1>One small change at a time</h1>\n    <p>I can edit, save and refresh my own page.</p>');
const project=skeleton('Maya | Learning journal','    <h1>Maya\'s learning journal</h1>\n    <p>I am starting web development from the beginning.</p>\n    <h2>Why I am learning</h2>\n    <p>I want to build useful pages for my studies.</p>\n    <h2>My next step</h2>\n    <p>I will practise changing one sentence and checking it in the browser.</p>');
const rebuild=skeleton('My practice page','    <h1>Building from memory</h1>\n    <p>I can create and reopen my own HTML file.</p>');

const lessons={
 '1.1':{
  id:'webdev:1.1',title:'Files and folders',objective:'Create a separate practice folder, identify a filename and extension, and locate a file without changing your existing Study Hub files.',
  sections:[
   h('Part 1 · Give your work a home'),
   p('A website starts as files that you can find, open and change. Before writing code, create a small place for your practice. If you save different copies in Downloads, Desktop and Documents without noticing, you can edit one file while looking at another. Today you will prevent that confusion.'),
   term('File','A named item stored on your device, such as a photograph or a text document. A web page can be stored in a text file. Its name helps you find it again.'),
   term('Folder (directory)','A container that organises files and other folders. A project folder keeps the files belonging to one piece of work together.'),
   p('Use your file manager. On Windows it is called File Explorer; Windows key + E opens it. Open Documents, create a folder named web-projects, open it, then create a folder named first-page. Use the New folder command or right-click an empty area and choose New → Folder. These are folder names you type, not commands to run.'),
   p('Your study website already contains an index.html file. Keep this practice project in its own first-page folder. Do not replace the Study Hub index.html or study-hub.html. The new practice page will be a different file in a different location.'),
   code('Documents/\n  web-projects/\n    first-page/','files'),
   term('Folder tree','A drawing of which folder contains which item. Indentation here means inside. Documents contains web-projects; web-projects contains first-page. The slash in this drawing is a separator, not part of a folder name.'),
   h('Part 2 · Names, extensions and paths'),
   term('Filename and extension','In index.html, index is the base name and .html is the extension. The extension gives software a clue about the file type. It is not part of the page title that readers see.'),
   code('index.html       → HTML page\nwelcome.txt      → plain text\nphoto.jpg        → an image\nindex.html.txt   → a .txt file, not the intended .html filename','files'),
   p('On some computers extensions are hidden. In Windows File Explorer, look under View for Show → File name extensions; some versions show a File name extensions checkbox directly on the View tab. Enable it so that you can see the full name. If your menus differ, use the file Properties or Details to check the actual name and type. Knowing the full name matters more than memorising a particular menu.'),
   term('Path','The location of an item, described by its containing folders and name. Two files can both be called index.html if they are in different folders.'),
   code('Documents/web-projects/first-page/index.html\nDocuments/web-projects/second-page/index.html','files'),
   p('These two paths point to different files. A Windows path may use backslashes instead, such as C:\\Users\\YourName\\Documents\\web-projects\\first-page\\index.html. Your account name and the location of Documents can differ, especially when Documents is managed by OneDrive. Use the folder you actually created rather than copying this sample path literally.'),
   term('Plain text','Text stored without word-processor formatting such as bold fonts or page layout. HTML source is plain text containing markup. Changing an image file name to .html does not turn its contents into HTML.'),
   h('Part 3 · A naming habit you can trust'),
   p('For this project use lower-case names and hyphens: first-page, learning-notes.txt, index.html. This is a convention, not a rule that every computer enforces. Consistency makes later file references easier to get right. Some hosting systems distinguish Index.html from index.html even if your local computer appears more forgiving.'),
   mistake('first-page/index.html.txt\nSecond copy somewhere in Downloads','first-page/index.html\nOne known practice folder','Check the real extension and full location. Renaming a plain-text file can correct an accidental .txt suffix, but changing an extension alone never converts arbitrary file content.'),
   key('Before coding, be able to say: this is my project folder, this is my file, and this is its real extension.'),
   h('Practice · Find it without guessing'),
   exercise('Which line describes a folder, and which describes an HTML filename?','first-page\nindex.html','first-page is our project folder. index.html is the filename we will create on Day 4.','A folder is the container; a filename identifies an item within it.'),
   exercise('Both files have the same name. Are they the same file?','first-page/index.html\nbackup-copy/index.html','No. They occupy different folders. Editing one does not automatically edit the other.','Compare the containing folder as well as the final name.'),
   exercise('The icon looks like a browser, but Properties says index.html.txt. What should you check?','Name: index.html.txt','Check the actual contents and extension. For our plain-text HTML page the intended final name is index.html.','Icons and hidden extensions are clues, not proof of the file you intended to create.'),
   h('Mini challenge · Navigate away and return'),
   p('Create the two folders, move to a different location in your file manager, then find first-page again without using the Recent files list. Write its actual location in your day notes. You do not need to create an HTML document yet.'),
   solution('Documents → web-projects → first-page\nFolder name: first-page\nFuture filename: index.html','Your path can differ. Success means that you can find your own folder again and distinguish it from the folder containing Study Hub.'),
   h('Ready to continue?'),p('You can find the folder again, explain .html versus .txt, and recognise two different files with the same name. If this still feels uncertain, repeat today before opening an editor.')
  ],
  quiz:[
   quiz('What is the main job of a project folder?','Keep related project files together','Change every file into HTML','Publish files automatically','A folder organises work; it does not convert or publish its contents.',0),
   quiz('What is the extension of index.html.txt?','.txt','.html','.index','The final suffix is .txt. Showing full extensions exposes this common beginner mistake.',1),
   quiz('Two index.html files are in different folders. What is true?','They can contain different content','They must always be the same file','Saving one must update both','Their paths identify different locations. A filename alone is not enough.',2),
   quiz('Which location should you use for this practice?','A separate first-page project folder','The existing Study Hub index.html','An unknown copy in Recent files','Practise in a separate folder so your learning app remains intact.',0),
   quiz('Does renaming photo.jpg to photo.html create HTML content?','No, the contents have not been converted','Yes, all extensions convert data','Yes, if the icon changes','A name is not a content conversion. HTML requires suitable text markup.',1)
  ],reflection:'Write the actual location of your first-page folder. Explain file, folder, extension and path using your own examples.'
 },
 '1.2':{
  id:'webdev:1.2',title:'Your browser and editor',objective:'Use a plain-text editor to create and save a file, then use a browser to open a local file and recognise the difference between editing and viewing.',
  sections:[
   h('Part 1 · Two tools, two jobs'),
   p('Keep the first-page folder from Day 1. You need a tool that edits text and a tool that displays a page. A code editor does not have to be complicated. If you already have one, use it. A plain-text editor such as Notepad is enough for this week; installing extensions, a server or a framework is not required.'),
   term('Text editor and code editor','A text editor changes plain-text files. A code editor adds conveniences such as coloured syntax, indentation and a project sidebar. These conveniences help you read and change source; they are not what makes HTML work.'),
   term('Browser','An application such as Chrome, Edge or Firefox that reads web content and displays pages. You will use it to view the file that your editor saves.'),
   p('Do not use a word-processing document such as .docx as your HTML source. A word processor can store formatting and other structures that are not the plain-text file we need. Also, the page you are reading in Study Hub is the instruction page; your practice page opens in another tab.'),
   h('Part 2 · Save one small text file'),
   p('Open your text editor. Create a new document and type the sentence below yourself. Save it inside first-page as welcome.txt. In most desktop editors Ctrl + S saves; the first save asks for a location and filename. On macOS, use Command + S. Confirm the location rather than accepting an unfamiliar default folder.'),
   code('I know where my project files are.'),out('Saved file: first-page/welcome.txt\nContents: I know where my project files are.'),
   term('Save and unsaved changes','Typing changes the editor’s current document. Saving writes those changes to the stored file. A dot, star or other marker near an editor tab may mean unsaved changes, but the exact indicator depends on the editor.'),
   p('Close the document, reopen welcome.txt from first-page in the editor and check the sentence. Reopening tests whether you saved the correct file. If it is missing, look at the path and save location before rewriting everything.'),
   h('Part 3 · Find the browser address bar'),
   term('Tab and address bar','A browser tab contains a page. The address bar shows or accepts its location. The search box inside a website is part of that page; typing a filename there does not normally open your local project.'),
   p('Open the browser and use Ctrl + L to focus the address bar (Command + L on macOS). You can drag welcome.txt from your file manager into a browser tab to open it. The browser may display its plain text. If your browser instead offers a download or refuses that file, this does not mean saving failed; check it in the editor and use the .html page on Day 4 for the web-page test.'),
   term('Local file','A file opened from your device rather than fetched from a website host. Its browser address commonly starts with file://. Opening it locally does not publish it to the internet.'),
   code('Editor: open the file and change its saved source.\nBrowser: open the saved file and view its content.\nFile manager: find the file and check its location.'),
   p('Typing into the browser address bar changes the location you are visiting; it does not change the file’s text. Editing a page temporarily in browser developer tools is also a different action from saving your project source. We will learn those tools in Week 2.'),
   key('Editor → save a file. Browser → open the saved file. Keep the two jobs separate.'),
   h('Practice · Choose the right tool'),
   exercise('Where would you change a sentence in your saved source?','A. Text editor\nB. Browser address bar\nC. Website search field','A. Open the correct project file in the text editor, change it and save.','The other fields navigate or search; they do not edit this saved source.'),
   exercise('You closed the editor and your sentence is missing on reopening. What do you check first?','Expected file: first-page/welcome.txt','Check whether the document was saved, then confirm its actual path and filename.','The same filename in another folder can hide a save-location mistake.'),
   exercise('What does a file:// address tell you in this exercise?','file:///.../first-page/welcome.txt','The browser opened a local file. It does not prove the file is hosted publicly.','The hosted versus local page journey is the main subject of Week 2.'),
   h('Mini challenge · Explain your workflow'),
   p('Change welcome.txt to say “I can edit and save a plain-text file.” Save, close and reopen it in the editor. Explain the three tool roles to an imaginary classmate. Keep the file for your debugging practice.'),
   solution('1. Editor: change the sentence.\n2. Save: write the change to first-page/welcome.txt.\n3. Reopen: verify the saved contents.\n4. Browser: view a saved file when that type is supported.','The critical evidence is the text that survives closing and reopening. Your editor’s exact menu names may differ.'),
   h('Ready to continue?'),p('You have one known project folder, a working text editor and a browser. You can reopen a saved text file. You do not need a terminal command to begin Week 1.')
  ],
  quiz:[
   quiz('Which tool changes the saved source text?','A text/code editor','The address bar','The browser tab label','Use the editor, then save the file.',0),
   quiz('Which format do you need for HTML source?','Plain text containing HTML markup','A .docx document renamed .html','A screenshot of some code','The source must contain actual text markup, not an image or word-processor package.',1),
   quiz('You type changes but never save. What may a browser reopening the file show?','The previous saved contents','Always the unsaved editor contents','A guaranteed error message','The browser reads the file, not your unsaved editor buffer.',2),
   quiz('Opening a practice page with file:// means…','You opened a file from your device','You published it to GitHub','Your notes were sent to a server','A local file address is different from hosting. Other sharing/sync tools have their own behaviour.',0),
   quiz('What is a reliable way to confirm a save?','Close and reopen the exact file in the editor','Assume every tab autosaves','Only check whether the icon changed','Reopening the same path gives evidence of the saved contents.',1)
  ],reflection:'Name your editor and browser. Record how you save, how you reopen a file and how you confirm the path. What confused you today?'
 },
 '1.3':{
  id:'webdev:1.3',title:'The three web languages',objective:'Distinguish HTML structure, CSS presentation and JavaScript behaviour, and read your first heading and paragraph without needing CSS or JavaScript code.',
  sections:[
   h('Part 1 · Start with the job, then the name'),
   p('Imagine a page introducing your study goals. It contains a main heading and a paragraph. You might later choose a green background. A button might later show or hide a note. These are related but different jobs. Learn to name each job before combining the languages.'),
   term('HTML — HyperText Markup Language','A language for marking the meaning and structure of web content: this is a heading, this is a paragraph, this is a link. It is a markup language, not a general-purpose programming language like Python.'),
   term('CSS — Cascading Style Sheets','A language for presentation: colours, spacing, font choices and layouts. HTML can display without your own CSS, using the browser’s default styles.'),
   term('JavaScript','A programming language used for behaviour and logic in web pages, such as responding to a click or updating a score. JavaScript and Java are different languages. A simple reading page can work without custom JavaScript.'),
   code('Content is a heading or paragraph → HTML\nChoose colour, spacing or columns → CSS\nRespond to a click or update a total → JavaScript'),
   p('These are useful starting roles, not absolute boundaries: HTML provides some built-in interactions, and CSS can animate presentation. You do not need JavaScript merely to display text. In this roadmap we build a dependable HTML foundation first. Detailed CSS comes later, and JavaScript foundations begin in Week 25.'),
   h('Part 2 · Your first two elements'),
   term('Element and tag','An HTML element gives content a role. In <p>Hello.</p>, <p> is the opening tag, Hello. is the content and </p> is the closing tag. The slash belongs inside the closing tag. Most elements you meet today have both tags.'),
   term('h1 and p','h1 marks the main heading of a page; the character after h is the digit 1, not a lowercase L. p marks a paragraph. The browser usually styles h1 larger, but meaning is the reason to use the element.'),
   code('<h1>My learning page</h1>\n<p>I am learning web development.</p>','html'),
   out('Main heading: My learning page\nParagraph: I am learning web development.'),
   p('This small example is an HTML fragment: only part of a document. On Day 4 you will place these exact elements inside a complete page. For now point to each opening tag, text and closing tag. The browser uses the tags to build the page, so correctly parsed <h1> and <p> tags are not printed as visible angle-bracket text.'),
   h('Part 3 · Structure is not appearance'),
   p('If you want the paragraph to have more space around it, that is usually a CSS decision. If you want the paragraph to be a real heading, change its HTML role. Choosing a heading only to make text look large produces a confusing structure for readers and assistive tools. We will practise heading levels in later weeks.'),
   mistake('<h1>My learning page</p>','<h1>My learning page</h1>','Match the closing element name to its opening name. Browsers may attempt to recover from bad markup, so a page appearing on screen does not prove the source is correct.'),
   key('First make the content meaningful. Then style it. Add behaviour when the page needs it.'),
   h('Practice · Read before writing'),
   exercise('Identify the opening tag, content and closing tag.','<p>I practise every day.</p>','Opening: <p>. Content: I practise every day. Closing: </p>.','The whole structure is the paragraph element.','html'),
   exercise('Which task needs which main language?','1. Mark the main heading\n2. Change the heading colour\n3. Update a quiz result after a click','1 HTML; 2 CSS; 3 JavaScript.','Use the role, not the number of lines of code, to classify the work.'),
   exercise('Spot the typo before the browser tries to recover.','<h1>Learning</hl>','The closing tag uses a letter l. It should use the digit 1: </h1>.','A similar-looking character can make a different tag name.','html'),
   h('Mini challenge · Mark your own content'),
   p('On paper or in your text editor, write a main heading about your studies and one paragraph about why you want to learn. Use only h1 and p. First try without copying the example; then compare the tags.'),
   solution('<h1>My study goal</h1>\n<p>I want to build a useful learning page.</p>','Both elements have matching tags. Your own wording can differ. This is a fragment, not yet the full document.','html','Heading: My study goal\nParagraph: I want to build a useful learning page.'),
   h('Ready to continue?'),p('You can explain the three language roles and identify two matching tag pairs. You are not expected to write CSS rules or JavaScript functions today.')
  ],
  quiz:[
   quiz('Which language marks a paragraph as a paragraph?','HTML','CSS','JavaScript','HTML supplies content structure and meaning.',0),
   quiz('Which task is mainly a CSS task?','Adjust paragraph spacing','Mark text as a heading','Calculate a quiz score after a click','Spacing is presentation. The other tasks concern structure and behaviour.',1),
   quiz('Which is the matching closing tag for <h1>?','</h1>','</hl>','<h1/>','The closing tag has a slash before h and the digit 1.',2),
   quiz('Can a simple HTML text page display without your own CSS and JavaScript?','Yes, the browser can display the HTML','No, all three files are compulsory','Only when a database is installed','Browsers have default rendering. Custom styling and scripting are additional tools.',0),
   quiz('A heading appears large despite a mismatched closing tag. What follows?','Check the source; the browser may have recovered','The markup must be correct','HTML does not use closing tags','Visible output alone is not a complete correctness check.',1)
  ],reflection:'Write one example each of structure, presentation and behaviour. Draw the parts of one HTML element and explain why a heading is more than large text.'
 },
 '1.4':{
  id:'webdev:1.4',title:'Your first HTML file',objective:'Create a complete index.html, explain every new line at a basic level, and open the exact saved file in a browser.',
  sections:[
   h('Part 1 · Create the right file'),
   p('Open first-page in your editor or create a new plain-text document there. Save it as index.html. If your editor offers a file-type selector and automatically adds .txt, choose All files and check the result in your file manager. Choose UTF-8 when an encoding choice is offered. Check the actual final name; do not assume a coloured icon proves it.'),
   term('index.html','A conventional name for a site’s entry page. When you open a local file you can use other names too. Hosting services have their own entry-page rules. Here we use one consistent name to avoid unnecessary choices.'),
   h('Part 2 · Build the document from the outside in'),
   term('Doctype and root html element','<!doctype html> tells the browser to use its modern HTML rendering mode. It is a declaration, not a paired element. The html element contains the document. Its lang="en" setting says the main language is English.'),
   term('Attribute','Extra information written inside an opening tag, usually as name="value". In lang="en", lang is the attribute name and en is its value. Quotes keep the value clear. Do not replace the straight quotes with word-processor curly quotes.'),
   term('head and body','head holds document information such as the tab title and character encoding. body holds the content readers see on the page. head is not a heading; h1 is the main visible heading in this example.'),
   term('meta charset="utf-8"','Sets the document character encoding so saved text can be interpreted correctly. UTF-8 supports English, Nepali and Japanese. Save the file itself as UTF-8 too; this declaration cannot repair text already saved incorrectly.'),
   term('Viewport metadata','The viewport meta line tells mobile browsers to use the device width as the page width and start at scale 1. It is a useful foundation, but it does not make every possible layout responsive by itself.'),
   term('title','The document title commonly shown in the browser tab. It belongs in head. It is separate from the h1 heading inside body.'),
   term('Void element and nesting','A void element such as meta has no closing tag. Paired elements fit inside one another: head and body inside html, title inside head, h1 and p inside body. Indentation shows that relationship for humans.'),
   code(first,'html'),
   out('Browser tab: My first page\nPage heading: My learning page\nPage paragraph: I am learning web development.'),
   p('Read the example in order. The declaration is first. html opens, head opens and closes, then body opens and closes, then html closes. The two meta elements do not need </meta>. The h1 and p use the same matching pairs you met on Day 3. You do not need to memorise the viewport spelling before you understand the document’s two main containers.'),
   h('Part 3 · Open the saved page'),
   p('Save the file, then locate first-page/index.html in your file manager. Drag it into a browser tab or use Open with and choose your browser. Double-clicking may open a browser or an editor depending on your device’s file associations. Either choice is normal; deliberately choose the browser when you want to view the page.'),
   p('Check that the address points to first-page/index.html and commonly starts with file://. Check the browser tab title and the large visible heading separately. You are opening a local page; no hosting account or internet connection is needed for this self-contained example.'),
   mistake('<head>\n  <h1>My learning page</h1>\n</head>','<body>\n  <h1>My learning page</h1>\n</body>','Place the visible heading in body. Browsers can move invalid content while recovering, so put the source in the right place even if you see something on screen.'),
   tip('If the browser displays the literal source, confirm the actual file type and extension. If you opened a view-source: address, return to the normal file address. If you changed another file with the same name, reopen the intended file.'),
   h('Practice · Explain your own page'),
   exercise('Which line changes the browser tab rather than the visible heading?','<title>My first page</title>\n<h1>My learning page</h1>','title changes the document/tab title; h1 changes the visible main heading.','They serve separate purposes, even if you choose identical wording.','html'),
   exercise('Which elements in the example have no closing tag?','<!doctype html>\n<meta charset="utf-8">\n<p>Hello.</p>','meta is a void element. The doctype is a declaration, not an element. p is paired.','Do not invent </meta> or </doctype>.','html'),
   exercise('Where does lang="en" belong in our document?','<html lang="en">','Inside the opening html tag. It labels the main language of the document.','If a future page is mainly Nepali or Japanese, use an appropriate language value rather than blindly keeping en.','html'),
   exercise('Why can the example open with Wi-Fi turned off?','index.html contains only its own HTML and text.','The browser can read this local file. No remote font, script, image or server response is required.','This statement concerns this self-contained example, not every website.'),
   h('Mini challenge · Make it yours'),
   p('Change the tab title to “My web journey” and the main heading to “One small change at a time”. Keep the paragraph. Save, open the same file and check both places. If only one changed, compare which element you edited.'),
   solution(skeleton('My web journey','    <h1>One small change at a time</h1>\n    <p>I am learning web development.</p>'),'title is in head; h1 and p are in body. The whole document structure stays intact.','html','Tab: My web journey\nHeading: One small change at a time\nParagraph: I am learning web development.'),
   h('Ready to continue?'),p('You have opened the correct HTML file and can point to doctype, html, head, body, title, both meta lines and your content. Save the file for tomorrow.')
  ],
  quiz:[
   quiz('Where should the visible h1 be placed?','Inside body','Inside title','Inside meta','body holds visible page content; title and meta are document information.',0),
   quiz('Which text appears in the tab in the first complete example?','My first page','My learning page','utf-8','title defines My first page. The heading has separate wording.',1),
   quiz('What is true about meta?','It is a void element without a closing tag','It must end with </meta>','It replaces body','Void elements do not wrap child content.',2),
   quiz('What is lang="en"?','An attribute setting the primary document language','A JavaScript function','The name of the file','It is name/value information on the html opening tag.',0),
   quiz('Does the viewport line guarantee every future design fits a phone?','No, layout and content still need responsive design','Yes, overflow becomes impossible','Yes, it compresses all images automatically','The viewport setting establishes a useful page width; later design choices still matter.',1),
   quiz('What is the safest first check when you see a different page?','Confirm the exact path and filename','Replace the whole project immediately','Install a JavaScript framework','A second file or wrong path is a common cause. Diagnose before rewriting.',2)
  ],reflection:'Record the actual path that opened in the browser. Explain title versus h1, head versus body, and why your file is saved as UTF-8.'
 },
 '1.5':{
  id:'webdev:1.5',title:'The edit–save–refresh cycle',objective:'Make a small change, verify the browser result and diagnose unsaved files, wrong paths and confusing copies in a predictable order.',
  sections:[
   h('Part 1 · Change one thing you can check'),
   p('Keep the editor and browser open together. Start with the page from Day 4. Before changing it, predict exactly what should be different. For example: “The paragraph will say I can edit, save and refresh my own page.” A specific prediction is easier to check than “make it work”.'),
   term('Edit–save–refresh','Edit changes the document in the editor. Save writes it to the file. Refresh tells the browser to load the page again. A browser tab does not always update just because you typed or saved.'),
   code('1. EDIT the paragraph in the editor.\n2. SAVE the file: Ctrl + S (Command + S on macOS).\n3. SWITCH to the matching browser tab.\n4. REFRESH: Ctrl + R (Command + R on macOS) or the reload button.\n5. CHECK the actual text against your prediction.'),
   p('Change just the paragraph first and verify it. Then change the heading or title separately. Small changes make it easier to find which action caused an unexpected result. Auto-save and live preview tools can automate some steps, but learn the explicit cycle before relying on them.'),
   code(revised,'html'),
   out('Tab: My web journey\nHeading: One small change at a time\nParagraph: I can edit, save and refresh my own page.'),
   h('Part 2 · A calm troubleshooting checklist'),
   term('Debugging','Finding and correcting the cause of an unexpected result. Start with what you expected, what happened and the smallest check that can distinguish possible causes.'),
   p('If the old sentence remains: first confirm that the editor saved. Then compare the editor’s full path with the browser address. Check the final extension. Reopen the exact file if necessary. Finally refresh that tab. Check these ordinary causes before assuming the browser is broken or deleting the page.'),
   code('Expected: New paragraph after refresh.\nObserved: Old paragraph remains.\nCheck 1: Did I save?\nCheck 2: Are editor and browser on the SAME full path?\nCheck 3: Is the final extension .html?\nCheck 4: Did I refresh the correct tab?'),
   p('A useful controlled experiment: change a sentence but deliberately do not save. Refresh and observe the previous saved version. Now save and refresh again. If your editor auto-saves, the first observation may differ; record that setting instead of assuming every editor behaves identically.'),
   h('Part 3 · Diagnose before replacing'),
   mistake('Editor: Documents/first-page/index.html\nBrowser: Downloads/first-page/index.html','Editor and browser: the same actual file path','Even perfect code saved in Documents cannot update a separate copy in Downloads. Reopen the saved project file in the browser.'),
   p('If you see odd text layout, inspect your markup too. A missing closing tag may cause the browser to recover in an unexpected way. If text such as <h1> appears literally, check whether you opened a .txt copy, selected View Source, or typed escaped markup. Different symptoms suggest different checks.'),
   key('Expected → observed → one check → one change → save → refresh → compare. Keep the evidence in your notes.'),
   h('Practice · Name the missing step'),
   exercise('What is missing from this sequence?','Edit → switch to browser → refresh','Save the edited file before refreshing.','Unless auto-save is confirmed, the browser can only read the previous saved file.'),
   exercise('The new title shows in the tab, but the heading is old. What did you probably edit?','Tab: My web journey\nHeading: My learning page','You probably edited title but not h1. Check the body heading in the source.','The two elements are independent; this is not automatically a cache problem.'),
   exercise('What will changing page-copy.html update?','Browser is showing: index.html\nEditor is saving: page-copy.html','The saved page-copy.html changes. The browser showing index.html will not automatically switch files.','Different names are different resources. Open the intended file.'),
   exercise('Does visible output guarantee that all tags are correct?','<h1>Learning</h2>','No. The tags do not match. Change the closing tag to </h1> and check again.','Browser recovery can hide a source mistake.','html'),
   h('Mini challenge · Repair a reproducible problem'),
   p('Create a temporary copy named practice-copy.html inside your practice folder. Open index.html in the browser, change only practice-copy.html in the editor and save. Explain why refreshing index.html shows no change. Then open the copy directly and prove which file changed. Keep the original intact.'),
   solution('Symptom: Refreshing index.html shows no new sentence.\nCause: I edited practice-copy.html.\nFix: Open practice-copy.html to view its changes, or edit index.html if that is the intended page.\nEvidence: The browser path and visible sentence now match.','The repair is about selecting the correct file. Rewriting the markup or refreshing repeatedly cannot merge two separate files.'),
   h('Ready to continue?'),p('You can deliberately cause and diagnose one save/path mismatch. You can make a heading change and a paragraph change separately, checking each after saving.')
  ],
  quiz:[
   quiz('Which is the normal explicit cycle?','Edit → save → refresh → check','Refresh → edit → assume saved','Edit → rename every file → publish','The saved file and the browser result are separate stages.',0),
   quiz('The browser shows Downloads/index.html; the editor saves Documents/index.html. What is the first issue?','They are different file paths','HTML cannot display local files','The viewport value is too small','Correct code in a different file does not update the open page.',1),
   quiz('A changed title appears only in the tab. Is that expected?','Yes, title is separate from h1','No, title must replace every heading','No, JavaScript is always missing','Edit h1 if you also want to change the visible heading.',2),
   quiz('Why change one thing at a time?','It helps connect a change to its observed result','HTML permits only one change per day','Saving several changes is forbidden','Small experiments improve diagnosis; they are a learning habit, not a language restriction.',0),
   quiz('What should a debugging note contain?','Expected result, actual result and the check/fix','Only “it does not work”','An untested guess presented as fact','Specific evidence makes the next attempt more useful.',1)
  ],reflection:'Write one real experiment as Expected / Observed / Cause / Fix / Verification. Include the exact file involved; do not rely only on its short filename.'
 },
 '1.6':{
  id:'webdev:1.6',title:'Build a first page',objective:'Build a small personal learning page, make its document title and headings meaningful, and verify it offline without adding untaught CSS or JavaScript.',
  sections:[
   h('Part 1 · Plan before the template'),
   p('Your project is a short learning journal page. It needs a document title, one main heading, a short introduction and two smaller sections: why you are learning and your next step. Write your content in ordinary sentences first. You can use a practice name rather than personal information you do not want to share.'),
   term('Requirement and acceptance check','A requirement says what the page must do or contain. An acceptance check is an observable way to confirm it. “Looks professional” is vague; “the tab says Maya | Learning journal and the page has one main heading” can be checked.'),
   code('Required content\n[ ] One meaningful tab title\n[ ] One h1 introducing the page\n[ ] One short introduction paragraph\n[ ] Two smaller section headings with one paragraph each\n[ ] File saved as index.html inside the known project folder\n[ ] Page reopened from that exact file while offline'),
   h('Part 2 · Add one small concept: h2'),
   term('h2 — second-level heading','A heading for a major section below the page’s h1. Here “Why I am learning” and “My next step” are sections of the same page, so they use h2. Choose heading levels for structure, not merely for the size you prefer.'),
   p('Use the same document shell from Day 4. Inside body, put one h1 and the introduction paragraph, then the first h2 and its paragraph, then the second h2 and its paragraph. Close each paired element before starting the next. Indentation is for readability; adding spaces in the source is not a reliable way to create a visual page layout.'),
   code('<h2>Why I am learning</h2>\n<p>I want to build useful pages for my studies.</p>','html'),
   out('Section heading: Why I am learning\nParagraph: I want to build useful pages for my studies.'),
   h('Part 3 · Build, test and explain'),
   p('Try creating the complete page before opening the solution. You may consult the meaning of an unfamiliar tag, but type the structure and your own content. Save and open the file. Change one sentence, save and refresh. Then close the tab and reopen the file from your folder.'),
   p('Temporarily disconnect Wi-Fi if convenient and reopen this self-contained file. It should still show its text because you did not add remote dependencies. This is different from proving that every online website works offline. Reconnect when you need other online services.'),
   warn('Your goal is a clear, correct first page. CSS layouts, links, images, forms, event handlers and a database are later topics. If you choose to explore them, label them as later learning rather than copying unfamiliar code into this checkpoint.'),
   key('You should be able to explain every line you use. A small page you understand is a useful foundation for the larger roadmap.'),
   h('Practice · Check the structure'),
   exercise('Choose heading levels for this page.','Page: Learning journal\nSection: Why I am learning\nSection: My next step','h1 for Learning journal; h2 for each of the two sections.','Both sections belong at the same level below the page heading.'),
   exercise('Repair the structure.','<h2>My next step</p>\n<p>I will practise tomorrow.</p>','Change </p> on the first line to </h2>. Keep the paragraph as its own paired element.','A heading and paragraph are different elements.','html'),
   exercise('Name two independent checks for a title/heading change.','I changed the title and h1.','Check the browser tab for title and the visible main heading for h1.','Looking at only one place cannot verify both requirements.'),
   exercise('How can you show that you understand the page rather than only copied it?','A complete page opens.','Explain head/body/title/h1/h2/p, then change a requested sentence and verify the result.','A working copy is a starting point; explanation and controlled changes show understanding.'),
   h('Mini project solution · Open after your attempt'),
   solution(project,'The page has one h1 and two h2 sections. title is separate in head. Each paragraph closes before the next heading. The viewport and UTF-8 metadata are retained. Replace the sample name and sentences with your own wording.','html','Tab: Maya | Learning journal\nMain heading: Maya\'s learning journal\nIntroduction paragraph\nSection: Why I am learning + its paragraph\nSection: My next step + its paragraph'),
   h('Readiness demonstration'),
   p('Ask yourself: Can I locate the file? Can I explain why the two meta lines have no closing tags? Can I change only the next-step paragraph? Can I reopen it and see the saved change? Record one uncertainty for the review day rather than hiding it.')
  ],
  quiz:[
   quiz('Which describes an acceptance check?','The browser tab shows my chosen title','The page should somehow be amazing','The code has many lines','An acceptance check is observable and specific.',0),
   quiz('What heading suits two equal sections below the page h1?','h2 for both','h1 for every sentence','Choose a tag only by its default size','The heading levels express the content relationship.',1),
   quiz('Why can this project work without internet?','Its text and markup are inside the local file','All websites ignore network connections','The folder name provides hosting','This claim applies to this self-contained example.',2),
   quiz('What should you do before opening the complete solution?','Attempt the page using the requirements','Mark complete without creating a file','Copy extra unfamiliar frameworks','An attempt makes the comparison and explanation useful.',0),
   quiz('What should you carry into Day 7?','Your page and a note of what you still cannot explain','A claim that all future web topics are finished','Only a screenshot with no source file','Review uses both your actual work and your remaining questions.',1)
  ],reflection:'Paste or describe your acceptance checks. Which passed? Which line can you not explain yet? Record the next small improvement without adding new languages.'
 },
 '1.7':{
  id:'webdev:1.7',title:'Review, rebuild and catch up',objective:'Rebuild a complete first page from an empty practice folder, repair beginner mistakes and demonstrate the Week 1 checkpoint before moving on.',
  sections:[
   h('Part 1 · Retrieve before looking'),
   p('Today is a review day, not a new list of technologies. Close the worked examples. Explain file/folder/path/extension, the three tool roles, the three web-language roles and edit–save–refresh. Then rebuild a complete page in a new folder named first-page-review. Keep the first project as evidence of your earlier work.'),
   p('Use a heading about building from memory and one paragraph explaining what you can now do. Include the document shell, meaningful tab title, UTF-8 and viewport metadata. Work without a timer first. If you need a hint, note which part you looked up and retry that part later.'),
   h('Part 2 · Six-day retrieval set'),
   exercise('Day 1 · Compare a name and a location.','first-page/index.html\nfirst-page-review/index.html','These are two separate files with the same filename in different project folders.','A full path prevents you from editing one and testing the other.'),
   exercise('Day 1 · Find the actual extension.','index.html.txt','The final extension is .txt. For a plain-text HTML document saved under the intended name, check that it ends in .html.','An extension is a naming/type clue, not a converter.'),
   exercise('Day 2 · Assign the tool roles.','Find the path / change the source / view the page','File manager / text editor / browser.','A single application may offer additional features, but these core roles remain useful.'),
   exercise('Day 2 · Verify a save without trusting a tab marker.','The editor says the document is open.','Save, then close and reopen the exact file. Inspect its contents.','An open document may have changes that have not been written to the file.'),
   exercise('Day 3 · Classify three changes.','Mark a paragraph / change colour / update a score after a click','HTML / CSS / JavaScript.','These are the starting roles; Week 1 code only needs HTML.'),
   exercise('Day 3 · Name the parts.','<p>I can explain my page.</p>','Opening tag <p>, content I can explain my page., closing tag </p>; together a paragraph element.','The visible content is not the same as the complete element.','html'),
   exercise('Day 4 · Where do these belong?','title / h1 / p / meta charset','title and meta charset go in head. h1 and p go in body.','Document information and visible content are distinct.'),
   exercise('Day 4 · Identify one declaration and one void element.','<!doctype html>\n<meta charset="utf-8">','doctype is the declaration; meta is the void element. Neither takes a corresponding closing tag here.','html, head, title, body, h1 and p are paired in our example.','html'),
   exercise('Day 5 · Diagnose the unchanged page.','Editor: first-page-review/index.html\nBrowser: first-page/index.html','Different files. Open the review file or edit the file the browser actually displays.','Refresh cannot make one path become another.'),
   exercise('Day 5 · The tab changed but the page heading did not.','<title>New title</title>\n<h1>Old heading</h1>','This is expected from the shown source. Change h1 separately if you intend a new heading.','Do not diagnose a cache problem before inspecting the correct element.','html'),
   exercise('Day 6 · Choose a hierarchy.','One page heading with two equal major sections','One h1, then an h2 for each section with a paragraph beneath it.','The hierarchy describes meaning, not just default text size.'),
   exercise('Day 6 · Name a test that proves more than a screenshot.','The screenshot shows a complete page.','Change a requested paragraph, save, refresh and reopen the exact file; explain which element changed.','A screenshot cannot prove the saved source or your ability to edit it.')
  ],
  quiz:[
   quiz('Which identifies a particular saved page most reliably?','Its full path and filename','Only its icon','Only the word index','Location distinguishes separate files.',0),
   quiz('Which is an accidental text suffix to check?','index.html.txt','index.html','first-page/index.html','Show real extensions and inspect the final name.',1),
   quiz('Which tool normally changes your source file?','The text/code editor','The browser tab label','The website search field','Write source in an editor and save it.',2),
   quiz('What makes the unsaved-edit experiment useful?','It separates editor changes from saved file contents','It proves saving is unnecessary','It guarantees every editor behaves identically','Auto-save may change the observation; identify that setting explicitly.',0),
   quiz('Which language provides content structure?','HTML','CSS','JavaScript','HTML gives elements their roles.',1),
   quiz('Which is a valid matching pair?','<h1>Learning</h1>','<h1>Learning</p>','<p>Learning</h1>','Match the element name at both ends.',2),
   quiz('Where is title placed?','Inside head','Inside the visible h1','Inside meta as a child element','The document/tab title is document information.',0),
   quiz('What should you do with the viewport line?','Retain it and still test the layout on small screens','Assume every later layout must fit','Replace all paragraphs with it','Viewport setup supports mobile rendering; responsive design still needs checks.',1),
   quiz('Old text remains after a refresh. What is a good first check?','Saved state and the exact file path','Add an unrelated framework','Delete the project immediately','Ordinary save/path problems should be checked before drastic changes.',2),
   quiz('Which tag suits a section below the main page heading?','h2','title inside body','meta','h2 provides a second-level heading.',0),
   quiz('Does opening your self-contained file locally publish it?','No, opening it is different from hosting/sharing','Yes, every open file becomes a public website','Yes, if the heading is large','Publishing and local viewing are separate actions.',1),
   quiz('When is it sensible to continue to Week 2?','When you can rebuild, reopen and explain this small page','Only after perfect visual design','After marking complete without checking','Use the practical readiness demonstration, and revisit weak parts when needed.',2)
  ],reflection:'Score yourself on the six-day retrieval set. Record which questions needed a hint, the cause of each error and the task you will repeat tomorrow. Completion is your own decision after the practical check.'
 }
};
lessons['1.7'].sections.push(
 h('Part 3 · Repair before comparing'),
 p('Try the four repairs below without reading the sample solution. State the cause, make the smallest repair and predict the visible result.'),
 exercise('Repair 1 · Fix both mismatched tag pairs.','<h1>My review page</p>\n<p>I can rebuild.</h1>','<h1>My review page</h1>\n<p>I can rebuild.</p>','Each element must close with its own name.','html'),
 exercise('Repair 2 · A title is used instead of a visible heading.','<body>\n  <title>My learning page</title>\n</body>','Move title into head. Use <h1>My learning page</h1> in body if you want a visible page heading.','Correct placement matters even if the browser tries to recover.','html'),
 exercise('Repair 3 · The filename is correct, but edits still do not show.','Edited: first-page-review/index.html\nOpened: first-page/index.html','Select the same actual file in both tools, save and refresh.','Correct extensions do not rule out wrong-folder mistakes.'),
 exercise('Repair 4 · The paragraph is new in the editor but old on disk.','Editor has unsaved changes.\nBrowser has just refreshed.','Save the editor document, then refresh the matching browser tab.','Reloading does not write the editor buffer to disk.'),
 h('Part 4 · Rebuild solution and readiness demonstration'),
 solution(rebuild,'A complete shell surrounds the visible h1 and p. Your own words can differ. If you needed this solution, hide it and rebuild once more before calling the skill secure.','html','Tab: My practice page\nMain heading: Building from memory\nParagraph: I can create and reopen my own HTML file.'),
 p('Demonstrate all six checks: (1) find the project folder, (2) show the real .html extension, (3) explain head and body, (4) change the tab title separately from h1, (5) change one paragraph through edit–save–refresh, (6) close and reopen the exact saved file without relying on a copied template. Mark complete only after your own attempt.'),
 key('Week 1 checkpoint: Create and reopen a simple HTML page from an empty folder, and explain the source you wrote.'),
 tip('If files/extensions were difficult, revisit Day 1–2. If tags or document structure were difficult, revisit Day 3–4. If changes did not appear, repeat Day 5. If the page works but you cannot explain it, repeat Day 6 with new wording.'),
 p('Next week explains URLs, clients, servers and the journey of a hosted page. That is a roadmap preview, not a requirement to publish today. CSS, images and JavaScript can wait until their place in the curriculum.')
);
module.exports={lessons,examples:{first,revised,project,rebuild}};
