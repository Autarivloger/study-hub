const {p,key,tip,warn,term,code,out,mistake,page,lesson}=require('./web-development-teaching-tools.cjs');
const lessons={};
const add=(day,data)=>lessons['2.'+day]=lesson(2,day,data);
add(1,{
 title:"Web addresses",objective:"Read the parts of a URL and distinguish a file on your computer from a hosted resource.",
 parts:[
 ["An address identifies a resource",[
  p("Open the address bar of your Week 1 practice page. Do not change the file yet. Compare that address with the address of this hosted Study Hub. The same HTML text can be opened from a device or delivered by a website host. The content alone does not tell you which journey happened."),
  term("URL — Uniform Resource Locator","An address used to locate a resource, such as a document or image. A URL can describe a local file as well as an online resource. A valid-looking address does not guarantee that the resource exists."),
  term("Scheme and hostname","The scheme before the colon identifies the kind of address. In https://example.com/guide.html, https is the scheme and example.com is the hostname. A hostname names a host; it is not the page filename."),
  code("https://example.com/learn/day1.html?language=en#practice\nscheme:   https\nhostname: example.com\npath:     /learn/day1.html\nquery:    ?language=en\nfragment: #practice"),
  p("example.com is a reserved example domain. The invented /learn/day1.html path is for reading practice; this lesson does not claim that it is a real page. Read from the scheme toward the end rather than trying to memorise the whole string.")
 ]],
 ["Path, query and fragment",[
  term("Path","The part after the hostname that identifies a resource within that site. A path may resemble folders and a filename, but servers can generate responses without a matching physical file."),
  term("Query and fragment","A query begins with ? and can pass information such as a search term to the server. A fragment begins with # and is handled by the browser, often to jump to an element. The fragment is not included in the HTTP request target."),
  p("In our example, language=en is one query parameter: language is its name and en is its value. An ampersand can separate additional parameters. A server decides what its parameters mean; adding ?dark=true does not automatically give every website a dark theme."),
  code("https://example.com/search?q=html&page=2#results\nQuery parameters: q=html and page=2\nFragment: results\nHTTP request target: /search?q=html&page=2"),
  warn("Do not put passwords, tokens or private notes in URLs. Addresses can be copied, logged or stored in browser history. A fragment not being sent in an HTTP request does not make it a safe secret store.")
 ]],
 ["Local and hosted are different locations",[
  code("file:///C:/web-projects/first-page/index.html\nhttps://autarivloger.github.io/study-hub/study-hub.html"),
  p("The first address opens a file on a Windows device. It does not upload the file. The second asks a host for a resource over HTTPS. Copying a file:// address to a friend does not give them your file. They need the file itself or a hosted address they can access."),
  term("Absolute and relative address","An absolute address includes its scheme. A relative reference, such as about.html, is resolved against a base address, usually the current document URL. You will write links later; today only compare where these references point."),
  code("Base: https://example.com/study/index.html\nabout.html → https://example.com/study/about.html\n/about.html → https://example.com/about.html"),
  key("Identify scheme → host → path → query → fragment. For a file URL, check the local path instead of assuming there is a remote host.")
 ]]
 ],
 practice:[
  ["Identify the hostname and path.","https://example.com/library/books.html","Host: example.com. Path: /library/books.html.","The slashes after the hostname start the resource path."],
  ["What reaches the HTTP server in the request target?","https://example.com/find?q=kanji#answers","/find?q=kanji","The query is included; #answers is a browser-side fragment."],
  ["Will this share your local page with another phone?","Send: file:///C:/web-projects/index.html","No. Share the actual file or a hosted URL.","That local location belongs to your device."],
  ["Resolve the relative reference.","Base: https://example.com/a/index.html\nReference: notes.html","https://example.com/a/notes.html","The reference stays in the base document directory."],
  ["Does the extra parameter guarantee a translated page?","https://example.com/?language=ja","No. The site must implement that parameter.","A meaningful-looking query is not a universal command."]
 ],
 challenge:["Annotate your two addresses","Write your actual local practice address and the public Study Hub address in your notes. Label the parts you can identify. Do not include any private query values.","Local: file scheme and device path.\nHosted: https scheme, autarivloger.github.io host, /study-hub/study-hub.html path.","Your local path can differ. You should be able to explain why the hosted address can be opened on another device."],
 ready:"Read a new URL without confusing its hostname with its path. Explain why a local file address is not a public sharing link.",
 reflection:"Label one local and one hosted URL. Write what ? and # mean and one reason to keep secrets out of addresses.",
 quiz:[
  ["Which part names the host?","example.com in https://example.com/a","/a","https","The scheme identifies the address type and /a identifies a resource path."],
  ["Which part is excluded from the HTTP request target?","The fragment after #","The query after ?","The path","The browser handles the fragment separately."],
  ["What does file:// indicate here?","A local file address","An automatic public upload","A GitHub password","Opening a local file is not publication."],
  ["Does a URL path always name a physical file?","No, it can identify a generated resource","Yes, every path ends in a file","Only when it has no query","Servers choose how a path maps to a response."],
  ["What is ?q=html?","A query parameter","An HTML tag","The hostname","The query carries information that a server may interpret."],
  ["With base /study/index.html, where does notes.html resolve?","/study/notes.html on the same host","/notes.html at the host root","A file anywhere named notes.html","A relative reference is resolved against its base."]
 ]});
add(2,{
 title:"Client and server",objective:"Trace a request and response, read basic response statuses, and separate receiving HTML from displaying a page.",
 parts:[
 ["Two roles in a conversation",[
  p("Imagine asking a library desk for one book. Your request names what you want; the reply tells you whether it is available and supplies the result. A browser and a web server also exchange messages. This analogy helps with the roles, but web responses carry data, not a physical object."),
  term("Client","Software that requests a service. For a web page visit, the browser acts as a client. Your phone and laptop can each run a client."),
  term("Server","Software that receives requests and returns responses, running on a computer. The word can also describe that computer. Client and server are roles; a single computer can run both for local development."),
  code("Browser (client)  ── request for a page ──→  Web server\nBrowser (client)  ←─ response and content ──  Web server"),
  p("A server does not normally send the pixels already painted for your screen. It sends HTML and other data. Your browser reads the HTML, builds its document structure, applies styles and displays the result. Different screens can arrange the same source differently.")
 ]],
 ["Read a simplified exchange",[
  term("HTTP request, response and GET","HTTP is a set of rules for exchanging web messages. A request goes to a server; a response returns. GET is a request method used to retrieve a resource. This diagram is an explanatory record, not a command to type."),
  code("Request:\n  Method: GET\n  Path: /study/index.html\n\nResponse:\n  Status: 200 OK\n  Content-Type: text/html\n  Body: <h1>My studies</h1>"),
  term("Status, headers and body","A status summarises a response result. Headers describe the response, such as its content type. The body contains the delivered content, when there is a body. The browser uses all of these pieces."),
  out("The browser can display a main heading: My studies"),
  p("200 means this request succeeded. 404 means the server responded that the resource was not found. A DNS error or no internet connection may prevent any HTTP response; that is different from receiving a 404. A status alone does not tell you whether the page says what you intended.")
 ]],
 ["One page can involve several resources",[
  term("Resource and cache","A resource is something addressed and retrieved, such as HTML, an image or a stylesheet. A cache keeps a reusable response so a later visit may not need to download the same bytes again."),
  code("Possible page load:\n1. index.html → HTML structure\n2. site.css → presentation\n3. app.js → behaviour\n4. photo.jpg → image\nThis is an example, not a required file count."),
  p("Some pages put CSS and JavaScript inside their HTML. Some need no custom scripts. Some get resources from a cache or a service worker, which is browser code that can help an app work offline. Therefore a page is not always one new network request and not always four."),
  tip("On your Week 1 file:// page there is no ordinary remote HTTP exchange for the local document. It is still a useful page. You do not need to install a server for these exercises."),
  key("Request asks; response answers; browser renders. Check which stage has evidence before deciding what failed.")
 ]]
 ],
 practice:[
  ["Name the client and server roles.","A phone browser asks a hosting service for index.html.","Client: phone browser. Server: hosting software answering the request.","The roles describe the conversation."],
  ["Did a server answer?","Status: 404 Not Found","Yes. It answered that this resource was not found.","A 404 response is evidence of an HTTP conversation, unlike some connection failures."],
  ["Where is the visible page assembled?","HTML response reaches a browser.","The browser reads and renders it.","HTML source and painted screen pixels are different things."],
  ["Must this page request app.js?","A document contains only h1 and p elements.","No. Text can display without a separate JavaScript file.","Resources depend on the document."],
  ["Explain a fast second visit without assuming magic.","A response is served from a browser cache.","The browser reused saved response data.","Not every display requires a fresh download."]
 ],
 challenge:["Tell the journey in your own words","Draw client → request → server → response → browser display. Add one successful response and one missing-resource response. Label which step has not happened if the network cannot connect.","GET /study.html → 200 plus HTML → browser display\nGET /missing.html → 404 response\nNo connection → an HTTP response may never arrive.","Use these as three distinct cases. Do not write that every error means the HTML is broken."],
 ready:"Explain client, server, request, response and rendering. Distinguish a 404 response from no connection, and explain why resource counts vary.",
 reflection:"Draw your own exchange and explain 200 versus 404. Give one reason a cached page might open without downloading everything again.",
 quiz:[
  ["Which software is the client during a normal page visit?","The browser requesting content","Only the Wi-Fi router","Only the HTML file","A client requests a service."],
  ["Which request method retrieves a resource in our example?","GET","DISPLAY","PAINT","GET is the HTTP method; display is browser work."],
  ["What does 404 show?","The server returned a not-found response","DNS always failed","The laptop is switched off","The server was able to send an HTTP status."],
  ["Where is HTML turned into a displayed document?","In the browser","Only in DNS","In the URL fragment","The browser parses and renders received HTML."],
  ["Must CSS always be a separate request?","No, it can be inside the HTML","Yes, exactly one request per page","No, because CSS never exists","Inline styles need no separate stylesheet request."],
  ["What can a cache do?","Reuse previously stored response data","Guarantee every page is up to date","Rewrite all source files","Caching saves some retrieval work; freshness still depends on rules."]
 ]});
add(3,{
 title:"Connecting to a website",objective:"Explain DNS and HTTPS at a useful beginner level without confusing encryption with trust in the site owner.",
 parts:[
 ["Find a destination",[
  p("Yesterday you traced messages. Today ask how a browser finds the host. Humans recognise names such as example.com. Network delivery needs addresses. The browser and operating system can use remembered lookup results or ask a resolver for DNS information."),
  term("DNS — Domain Name System","A distributed system that supplies records about names. For a beginner page journey, a useful role is resolving a hostname to IP addresses. DNS does not return the HTML page."),
  term("IP address and resolver","An IP address is a numeric network address. A resolver helps look up DNS answers. IPv4 and IPv6 are two address formats; you do not need to memorise numeric addresses to build HTML."),
  code("URL: https://example.com/study/day1.html\nName to look up: example.com\nResource to request later: /study/day1.html"),
  p("A hostname can resolve to several addresses, and answers can change. A cached result may remove the need for a new lookup during a visit. DNS does not look up the full path or your #fragment. This is a useful sequence model, not a promise that every visit makes the same set of fresh requests.")
 ]],
 ["Protect the connection",[
  term("HTTPS and TLS","HTTPS is HTTP carried over a connection protected by TLS. TLS helps encrypt data in transit, detect changes in transit and authenticate the server for the hostname using certificates."),
  term("Certificate","Information used during secure connection setup to help verify the server identity for the requested hostname. Browsers check this information and can show a warning when verification fails."),
  code("Simplified uncached visit:\n1. Resolve hostname using DNS information.\n2. Establish a secure connection for HTTPS.\n3. Send HTTP request over that connection.\n4. Receive response and display content."),
  p("Encryption in transit protects the journey between connection endpoints. The destination still receives the request you send it. HTTPS does not make a malicious shop honest or prevent a page owner from seeing information you submit. Read the hostname and decide whether to trust the destination."),
  warn("If a browser shows a certificate warning, do not bypass it as a beginner debugging step. Check the address, device clock and the site's official guidance. Never paste a password into an unexpected page to test whether it works.")
 ]],
 ["Use a layered explanation",[
  p("If the hostname cannot be resolved, rewriting h1 text cannot repair DNS. If HTTPS verification fails, changing paragraph indentation cannot fix the certificate. If the server returns 404, you have reached a responding server and should investigate the requested path or publication."),
  code("Cannot resolve name → check hostname and connection evidence.\nCertificate warning → check secure connection evidence.\n404 response → check requested resource/path.\nWrong heading after 200 → inspect content, version and rendering."),
  term("Internet and Web","The internet is the underlying network of connected networks. The Web is one service using it, commonly through HTTP/HTTPS. Other internet services also exist."),
  tip("You can learn every distinction here offline using the supplied cases. An online Network panel observation is optional. Do not invent DNS timings or IP addresses when you have not measured them."),
  key("DNS helps find; HTTPS protects the connection; HTTP exchanges messages; the browser displays the result.")
 ]]
 ],
 practice:[
  ["What does DNS need from this URL?","https://example.com/a?q=b#c","The hostname example.com.","The path, query and fragment are not the hostname to resolve."],
  ["Does a padlock make the seller trustworthy?","A fake shop uses valid HTTPS.","No. The connection can be protected while the shop is dishonest.","Transport protection and the trustworthiness of the business are separate."],
  ["Choose the relevant layer.","The browser says it cannot resolve the hostname.","Check the name and network/DNS evidence before HTML markup.","The HTML response may not have arrived."],
  ["Must the IP address stay the same forever?","A site has several servers.","No. A name can resolve to multiple or changing addresses.","Names avoid requiring users to memorise those changes."],
  ["What should you do with a certificate warning?","A login page shows a secure connection warning.","Stop and check the address and official guidance; do not bypass it to log in.","A warning is not a request to expose credentials."]
 ],
 challenge:["Explain four jobs without mixing them","Write one sentence each for DNS, HTTPS, HTTP and the browser. Then diagnose an invented 404 and an invented DNS failure separately.","DNS: find name records.\nHTTPS: protect and authenticate the connection.\nHTTP: request/response messages.\nBrowser: interpret and display content.\n404: responding host, missing resource.\nDNS failure: name resolution problem before this HTTP exchange.","Your wording may differ. Keep the layers separate and say when the evidence is insufficient."],
 ready:"You can explain where DNS and HTTPS fit, why HTTPS is not a guarantee of honest content, and why a 404 is not a DNS failure.",
 reflection:"Write the four jobs from memory. What information would you collect before blaming HTML for a connection error?",
 quiz:[
  ["What is the DNS lookup input in our URL example?","The hostname","The entire HTML source","Only the fragment","DNS records concern names, not the document body."],
  ["What does HTTPS mainly protect here?","The connection carrying HTTP messages","The honesty of every website owner","Every file stored on your device","TLS protects transport, not all aspects of trust or storage."],
  ["Does DNS deliver the HTML body?","No, a later resource response delivers it","Yes, DNS paints the heading","Only if the title is missing","DNS lookup and HTTP delivery have different roles."],
  ["Can a hostname have several IP addresses?","Yes","No, exactly one forever","Only for local files","Sites can use multiple destinations and changing answers."],
  ["What is the safest beginner response to a certificate warning?","Stop and investigate rather than bypass","Disable all browser checks","Type a password to see if it works","Do not use credentials while the connection identity is in doubt."],
  ["Is the Web the entire internet?","No, it is one service using the internet","Yes, they are identical terms","No, the Web only works offline","The underlying network supports other services too."]
 ]});
add(4,{
 title:"Static and dynamic websites",objective:"Distinguish prebuilt files from server-generated responses and explain how a static learning app can still be interactive.",
 parts:[
 ["When is a response prepared?",[
  p("A server can deliver an already prepared HTML file. It can also run application code to construct a response when a request arrives. Both approaches can produce HTML that a browser displays. The distinction concerns how the response is produced, not whether the result looks modern."),
  term("Static delivery","Delivering prebuilt resources rather than generating each page with application logic for that request. A deployment can replace those resources when the author publishes a new version."),
  term("Server-side dynamic response","Content constructed by application code on a server, perhaps using request data and stored records. A timetable service might generate a result for a particular route and date."),
  code("Static example:\nAuthor saves timetable.html → host delivers that file.\n\nDynamic server example:\nRequest for a route/date → server builds a result → sends HTML or data."),
  p("A database stores organised records. Some dynamic systems use one, but dynamic responses do not always require a database. Likewise, a simple HTML page does not require accounts, a backend framework or database installation.")
 ]],
 ["Interactive does not mean server-generated",[
  term("Client-side behaviour","Code running in the browser can respond to input, show answers or update a display after a page loads. That can happen even when the original HTML was delivered as a static file."),
  p("Study Hub is a useful example. GitHub Pages delivers its published files. JavaScript in the browser powers quizzes and many interface actions. Calling it static hosting does not mean that its buttons cannot work. Some features can also contact a separate service, such as the configured sync service."),
  code("Delivery question: Was this response prebuilt or generated for the request?\nBehaviour question: What can the browser do after loading it?\nStorage question: Where are user changes saved?"),
  term("Browser storage and backend","Browser storage keeps data for a browser/profile and site. A backend is service-side application logic. Local storage is not automatically shared with another phone or uploaded into the public HTML."),
  warn("Do not put a password or private API token in a public HTML or JavaScript file. Splitting a secret into another public .js file does not hide it. A static host serves those files to visitors.")
 ]],
 ["Choose the smallest system for the job",[
  p("For a public reading page, HTML files may be enough. For a personal checklist saved on one device, browser storage may be enough. For shared account data across many devices, you need an appropriate sync or backend design. Match the design to the requirement rather than adding infrastructure because it sounds advanced."),
  code("Reading article → prebuilt HTML can work.\nReveal an answer offline → browser behaviour can work.\nShow a user's private account records → authentication and suitable service/storage design.\nKeep progress between devices → explicit sync; local storage alone is insufficient."),
  p("Different origins and browser profiles have separate storage. Opening file:// and opening the hosted HTTPS app can therefore show different progress. Publishing a new page does not by itself copy local progress between them. Use the app's existing backup/import and configured sync."),
  tip("Today you classify systems; you do not need to build login or sync code. Browser storage APIs, servers and databases are later topics with their own prerequisites."),
  key("Separate delivery, behaviour and storage. A static site can be useful, interactive and professionally designed.")
 ]]
 ],
 practice:[
  ["Classify the delivery.","A host returns a saved about.html file.","Static delivery.","The file was prepared before this request."],
  ["Classify the behaviour.","A quiz button reveals an answer without contacting a service.","Client-side behaviour; it can exist on a static site.","Interactivity does not prove server-side generation."],
  ["Will another phone get this automatically?","A completion checkbox is saved only in browser storage.","No. A separate sync/import mechanism is needed.","Storage is not inherently shared across devices."],
  ["Is this a safe place for a secret?","Public site loads private-token.js.","No. Visitors can retrieve a publicly served JavaScript file.","A different filename is not access control."],
  ["Is a database compulsory?","You want to publish a short reading article.","No. A prebuilt HTML document can meet that need.","Choose infrastructure for the actual requirement."]
 ],
 challenge:["Classify three features of your hub","Describe the published lesson file, an offline reveal button and cross-device progress. State delivery, behaviour and storage responsibilities separately.","Published lesson: prebuilt file delivery.\nReveal button: browser behaviour.\nProgress: saved in browser; explicit configured sync or backup/import for another device.","Do not claim that hosting alone transfers progress or hides secrets."],
 ready:"You can explain why static hosting and interactive buttons fit together and why browser storage is not automatic cross-device sync.",
 reflection:"Give a static-delivery example and a server-generated example. Explain where your practice source and your Study Hub progress are stored.",
 quiz:[
  ["A static site can have…","Browser-side interactive features","Only an unclickable screenshot","No HTML","Delivery and client behaviour are separate questions."],
  ["A server generates a page for a requested date. This is…","Server-side dynamic generation","Always a local file","DNS lookup only","Application logic produced the response for this request."],
  ["Does browser storage automatically sync across phones?","No","Yes, through the page title","Only when the heading is h1","A separate sync design is necessary."],
  ["Where can visitors see a publicly served token.js file?","By retrieving the file","Nowhere, because .js is private","Only if they own your laptop","Public client files cannot conceal embedded secrets."],
  ["What does a static-host deployment do?","Publish prepared resource versions","Copy every visitor's local notes into HTML","Turn every button off","Publication updates site resources, not automatically private browser records."],
  ["Which is necessary for a simple public article?","A suitable HTML document and delivery method","A database in every case","A Python server in every case","Use the simplest system that meets the requirement."]
 ]});
add(5,{
 title:"Browser developer tools",objective:"Inspect your own local page with Elements, recognise Console and Network, and understand which edits are temporary.",
 parts:[
 ["Open an inspection tool",[
  p("Use your own Week 1 practice file in a separate tab. Right-click the main heading and choose Inspect. On desktop Chrome or Edge, Ctrl + Shift + I usually opens developer tools; on macOS use Command + Option + I. Menu wording and panel placement can differ. A phone browser may require remote inspection; you can still complete the paper exercises."),
  term("Developer tools and Elements panel","Browser tools for inspecting a loaded page. Elements shows the live document tree and associated information. The tree is the browser's current structured representation, not necessarily an exact copy of your saved source."),
  term("DOM — Document Object Model","The browser's representation of document elements and their relationships. Parsing can repair source mistakes, and scripts or developer-tool edits can change the live tree after loading."),
  p("Select the h1 row in Elements. Expand its parent to see where it sits in body. Look for the paragraph below it. You are observing the document already loaded; this does not require Python, JavaScript commands or changing app data."),
  code("Saved source → browser parses → live DOM → rendered page\nElements panel → inspect the live DOM")
 ]],
 ["Make one temporary change",[
  p("On your practice page only, edit the heading text using the Elements panel's text editing command. Change it to Temporary inspection. Observe the page. Then reopen the saved file in your editor: the original text should still be there. Reload the browser page; your temporary DOM change normally disappears."),
  out("Expected comparison:\nLive page after tool edit: Temporary inspection\nSaved editor file: original heading\nAfter reload from saved file: original heading"),
  tip("DevTools has optional persistence features such as workspaces/overrides, but this lesson does not configure them. In the normal inspection workflow, saving project source is still an editor task."),
  mistake("I edited the heading in Elements, so my saved HTML must be updated.","I changed the current DOM. I must edit and save my project source to persist the change.","Check the file and reload instead of assuming a visible change is saved.","text"),
  p("Never use the live Study Hub to practise deleting nodes or clearing storage. Use the disposable practice page. Reading tools is safe, but some tool commands can modify data.")
 ]],
 ["Orient yourself in Console and Network",[
  term("Console","A panel for messages, errors and running JavaScript. For now read messages only. An empty console does not prove HTML is valid; many HTML parsing mistakes are repaired without JavaScript errors."),
  term("Network panel","A record of resource requests while the tools are recording. Open it before reloading so it can record the page load. Name, type, status and source/cache information help explain what happened."),
  p("Open Console and look for messages. Do not paste unknown code. Open Network, then reload your local file. A file:// document may not have an ordinary HTTP status. On a hosted page, entries may come from memory cache, disk cache or a service worker. Exact rows and labels depend on the browser."),
  code("Observation log:\nPage address:\nPanel used:\nWhat I actually saw:\nWhat I think it means:\nWhat I have not verified:"),
  key("Elements shows the current document; Console shows messages; Network records resource activity. Use evidence and keep your saved source separate.")
 ]]
 ],
 practice:[
  ["Which view shows the current document tree?","Elements or your saved editor file?","Elements.","The saved file is input; the live tree is the parsed current document."],
  ["Why did a temporary heading change disappear?","You edited text in Elements, then reloaded.","The browser loaded the unchanged saved source again.","A normal DOM edit does not write to the project file."],
  ["Why are early requests absent?","You opened Network after the page finished loading.","Open Network before a new reload to record that load.","The panel cannot reconstruct every previously unrecorded event."],
  ["Does no red Console message prove valid HTML?","A mismatched tag still displays.","No. HTML parsing recovery may not produce a JavaScript error.","Check source structure as well."],
  ["Should you expect HTTP 200 for every local file?","Address starts file://.","No. It is not an ordinary HTTP document response.","Interpret panel results in the context of the address."]
 ],
 challenge:["Collect evidence from your own file","Inspect the heading, change it temporarily, reload, then write a five-line observation log. If DevTools is unavailable on your device, explain the expected results on paper and repeat the tool experiment later.","Address: my local first-page/index.html\nElements: h1 inside body\nTemporary edit: visible before reload\nSaved file: unchanged\nAfter reload: original heading","Do not claim observations you did not make. Separate a predicted result from a measured one."],
 ready:"Locate the three panels, explain a temporary DOM edit and record an observation without clearing your learning app's data.",
 reflection:"Describe the temporary edit experiment. What did you see in Network, and what have you not verified?",
 quiz:[
  ["What does Elements primarily show?","The live document tree","Your GitHub token store","Only DNS records","The DOM may differ from the original source."],
  ["How do you persist a normal project text edit?","Edit and save the source file","Only edit the temporary DOM","Only change the address bar","The editor writes your project file."],
  ["When should Network be open to capture a reload?","Before reloading","Only after closing the tab","Only after clearing all storage","It records activity while active."],
  ["What does Console mainly help you inspect today?","Messages and errors","The physical server room","File manager folder icons","Running commands is unnecessary for this orientation."],
  ["Should you paste an unknown script to fix an error?","No","Yes, every Console suggestion is trusted","Only if it is long","Console code can act with page permissions."],
  ["A local file has no ordinary HTTP status. Is that necessarily broken?","No, check the file:// context","Yes, every file must return 200","Yes, reinstall the editor","Local file loading differs from an HTTP exchange."]
 ]});
add(6,{
 title:"Trace a page journey",objective:"Build and explain two page-loading diagrams and classify resource roles using evidence rather than guesses.",
 parts:[
 ["Plan the investigation",[
  p("Today is a project, not a new programming language. Keep your Week 1 page unchanged while you study the journey. Your deliverable is a diagram, a resource-role table and a short explanation. First make a prediction; then compare it with evidence when tools are available."),
  term("Trace","A step-by-step account of what happened. A useful trace separates directly observed facts from a simplified explanation and from information you have not measured."),
  code("Deliverables:\nA. Local file journey\nB. Hosted HTTPS journey\nC. Resource role table\nD. Two failure diagnoses"),
  p("For the local case, record your actual file:// address. For a hosted case you can observe public Study Hub when online. If you are offline, use the model trace below and label it supplied example. Both routes satisfy the reasoning exercise; only the online route supplies a real network observation."),
  key("Do not write an invented IP address, timing or request count as an observation.")
 ]],
 ["Draw and classify",[
  code("A. Local file:\nEditor saves HTML → browser opens file → parses DOM → displays content.\n\nB. Simplified fresh HTTPS visit:\nURL → DNS information → secure connection → HTTP request\n→ server response → browser parses HTML → needed resources → display."),
  p("A real load can reuse existing connections and cached data. Resource loading and display can overlap. This diagram is a beginner model, not a stopwatch ordering every browser operation."),
  code("Supplied trace (illustrative, not a live capture):\nindex.html | document   | 200\nsite.css   | stylesheet | 200\napp.js     | script     | 200\nphoto.jpg  | image      | 404"),
  p("HTML identifies content structure. CSS describes presentation. JavaScript can add logic and behaviour. The last row shows a missing image while other resources succeeded. Do not say the whole server is down. The HTML may still display with a missing image."),
  term("Embedded versus external resource","HTML can contain styles or script text within the same document, or reference separate files. Filename extensions are useful clues, but response types and the actual content are stronger evidence of a resource's role.")
 ]],
 ["Explain and check your project",[
  p("Use a known local page to inspect h1 and p. With an online hosted page, open Network before reload and record the document row plus any stylesheet or script rows you actually see. An app with embedded code may not request separate CSS or JavaScript files. Do not invent them to match the example."),
  code("For each row record:\nName/address | observed type/status | likely role | source of evidence\n\nThen ask:\nDid I observe DNS/TLS, or only explain where they fit?\nCould a cache or service worker have supplied this response?"),
  warn("Keep private account data, tokens and full sensitive URLs out of screenshots and shared logs. Use public or local practice content."),
  p("Your explanation is complete when another beginner can follow both paths and understand why a page can partly load. Point out uncertainty. For example: I saw a cached document row; I did not measure a new DNS lookup."),
  tip("You may finish this project across several sessions. Keep the diagrams in day notes and revisit any missing term from Days 1–5 before proceeding.")
 ]]
 ],
 practice:[
  ["Diagnose only what the trace supports.","document 200; photo.jpg 404","The document arrived; the image resource was not found.","One missing asset does not prove all resources failed."],
  ["Classify a resource.","Type: stylesheet","Presentation, normally CSS.","The recorded type supports the role."],
  ["State a limit of your evidence.","You only inspected Elements.","You observed the live document, not a full DNS or request history.","A tool view does not reveal every layer."],
  ["Explain a page with no app.js row.","All JavaScript is embedded in HTML.","The behaviour can arrive in the document itself.","A separate file is not compulsory."],
  ["Compare the two journeys.","file:// page versus https:// page","Local reads a device file; hosted retrieval can involve DNS, TLS and HTTP.","Both can eventually be parsed and displayed by the browser."]
 ],
 challenge:["Submit your journey notebook","Write both diagrams, a role table for four resource types and two diagnoses: a 404 image and a DNS failure. Add one observed-versus-inferred statement.","HTML: structure; CSS: presentation; JS: behaviour; image: visual asset.\n404 image: host answered, requested image missing.\nDNS failure: hostname resolution failed before this HTTP exchange.\nEvidence limit: my diagram describes TLS; it does not measure a handshake.","The strongest project distinguishes what was seen from what was inferred and uses terms accurately."],
 ready:"Explain the whole path in your own words, identify resource roles, and diagnose partial failure without blaming every component.",
 reflection:"Save your diagrams and evidence table. Which step was hardest to explain, and what would you inspect next?",
 quiz:[
  ["Which is a measured observation?","A Network row shows 404 for photo.jpg","DNS probably took exactly 20 ms","The server must use Python","Only the first statement follows directly from the supplied record."],
  ["Which role matches CSS?","Presentation","Hostname resolution","Server identity verification","CSS controls presentation."],
  ["What does a missing image with a successful document imply?","A partial resource failure","Every server is unreachable","HTML cannot display","Resources can succeed or fail separately."],
  ["Why may there be no separate script request?","Script text may be embedded in HTML","The page cannot have behaviour","DNS executed the script","Embedded code arrives with the document."],
  ["Does a simplified fresh-load diagram describe every cached visit exactly?","No","Yes, always four new requests","Only on phones","Caches and existing connections can change the work performed."],
  ["What belongs in your final trace?","Evidence, explanation and limits","Only guesses written as facts","Private tokens for completeness","A useful account is accurate about uncertainty."]
 ]});
add(7,{
 title:"Week 2 review and catch up",objective:"Explain a complete page journey from memory, repair common misconceptions and finish the Week 2 checkpoint.",
 parts:[
 ["Retrieve before rereading",[
  p("Close the earlier explanations. On paper write URL, client, server, request, response, DNS, HTTPS, DOM and cache. Give each a job in one sentence. Mark unsure terms with a question mark. Then open only the lesson needed to repair the uncertainty."),
  code("Round 1: label an address.\nRound 2: draw two journeys.\nRound 3: diagnose resource cases.\nRound 4: explain tools and storage.\nRound 5: teach the explanation aloud."),
  term("Retrieval practice","Trying to recall an idea before looking at the answer. A mistake shows what needs another attempt; it is not a reason to copy a solution without explaining it."),
  p("Work in short rounds. For every wrong answer, write why your first idea was tempting, then state the correction. Repeat that item after completing a different round. No time limit is required."),
  key("You are ready when you can explain, diagnose and distinguish the ideas, not merely recognise their names.")
 ]],
 ["Connect the layers",[
  code("URL → destination and resource\nDNS → name records\nHTTPS → protected connection\nHTTP → request and response\nBrowser → live document and display\nCache/storage → different forms of saved browser data"),
  p("Cache responses and personal progress storage are different responsibilities. A page being available offline does not prove that progress has synced to another phone. A file can be hosted publicly while personal notes remain in that browser. Always describe the actual storage and sync design."),
  p("A 404 is a response. A certificate warning concerns secure connection verification. A malformed paragraph concerns source structure. Choose the relevant evidence before changing anything."),
  code("Explain separately:\nA. Where the response came from.\nB. What it contained.\nC. How the browser displayed it.\nD. Where user changes were stored."),
  tip("Keep your Week 1 files. They will be used for deeper HTML work in Week 3; you do not need a new framework or hosting account.")
 ]],
 ["Rebuild the project explanation",[
  p("Redraw the two Day 6 journeys from memory. Use a fresh invented URL and label it illustrative. Add an HTML/CSS/JavaScript role table. Ask a friend or an imaginary learner to interrupt with: Which component does that? Answer with a specific role."),
  out("Checkpoint evidence:\nTwo clear diagrams, one annotated URL, three language roles,\none tool observation or labelled prediction, two reasoned diagnoses."),
  p("If your diagram says that DNS stores the HTML, revisit Day 3. If it says a static site cannot have a quiz, revisit Day 4. If it says an Elements edit saved the file, repeat the Day 5 experiment."),
  warn("Do not erase learning data or expose credentials while experimenting. Your practice files and supplied traces are enough for this review."),
  key("Move on after fixing the uncertain items. Repeating a lesson is part of the course, not falling behind.")
 ]]
 ],
 practice:[
  ["Label all parts.","https://example.com/learn.html?mode=read#notes","https scheme; example.com host; /learn.html path; ?mode=read query; #notes fragment.","Read each delimiter's job."],
  ["What is requested without the fragment?","https://example.com/a?x=1#b","/a?x=1","Fragments are not included in the HTTP request target."],
  ["Does a friend get your file from this message?","file:///C:/first-page/index.html","No, they need the file or an accessible hosted URL.","A device path is not an upload."],
  ["Name the direction.","Browser asks for /a.html.","Client to server: request.","The answer travels back as a response."],
  ["Name the status meaning.","200 OK","This request succeeded.","It does not prove the author wrote the correct lesson."],
  ["Name the status meaning.","404 Not Found","Server responded that the resource was not found.","It is not identical to no connection."],
  ["What does DNS supply in this model?","Browser needs to find example.com.","Name records including useful address information.","DNS does not paint the page."],
  ["What does HTTPS fail to guarantee?","A suspicious shop has HTTPS.","It does not guarantee an honest owner or safe content.","Connection protection has a limited purpose."],
  ["Is this impossible?","Static hosting plus an offline quiz.","No, browser-side JavaScript can provide interaction.","Delivery and behaviour are separate."],
  ["Will storage transfer automatically?","You open the app in another browser profile.","No, use configured sync or backup/import.","Profiles and origins can hold separate data."],
  ["What changes after a normal Elements edit?","You replace h1 text in DevTools.","The current DOM, not normally the saved source.","Reload tests this distinction."],
  ["Does an empty Console prove valid source?","No messages appear.","No. HTML recovery may be silent.","Inspect source structure too."],
  ["Why open Network before reload?","You want to see document loading.","To record the requests as they happen.","An already completed load may not be available."],
  ["What can explain a reused response?","Network says from cache.","Previously stored response data was reused.","Not every visit downloads every byte."],
  ["Which layer would you check?","Cannot resolve hostname.","Hostname, connectivity and DNS evidence.","Changing h1 is unrelated to name resolution."],
  ["Which resource job is this?","A stylesheet sets spacing.","Presentation through CSS.","HTML structure and JS logic have other roles."],
  ["Can HTML, CSS and JS arrive in one file?","A single-file learning app.","Yes, style and script can be embedded.","Separate filenames are organisational choices."],
  ["Improve the evidence statement.","I saw Elements, so DNS took 5 ms.","I inspected the DOM; I did not measure DNS.","Do not turn an unmeasured claim into a fact."]
 ],
 challenge:["Teach the whole journey","Without copying, explain how a hosted page reaches a browser, how a local file differs, where the three web languages fit and how you would investigate one failure.","A hosted visit uses its URL, name/address information and a suitable connection to exchange HTTP messages. The browser receives resources and renders them. A local file is read from the device. HTML supplies structure, CSS presentation and JavaScript logic/behaviour. Inspect evidence at the failing layer.","Your explanation should include caching as a possible variation and avoid claiming that HTTPS means the owner is trustworthy."],
 ready:"Complete the week's checkpoint aloud and redo every unsure exercise. If any part still needs copying, return to the matching day before Week 3.",
 reflection:"List three ideas you can explain from memory and two items to revisit. Save your final diagram and one corrected misconception.",
 quiz:[
  ["Which item identifies the resource within a host?","The path","Only the scheme","Only the tab title","A URL path identifies the requested resource on that host."],
  ["Which item stays out of the HTTP request target?","Fragment","Query","Path","The fragment is browser-side information."],
  ["Which is evidence of an HTTP response?","404 status","A DNS lookup failure alone","A disconnected cable alone","A status belongs to a response."],
  ["Which role returns a response?","Server","Only the text editor","Only the heading","The server answers the client request."],
  ["Which system looks up name records?","DNS","CSS","The h1 tag","DNS resolves names rather than formatting text."],
  ["Which statement about HTTPS is accurate?","It protects the connection, not the owner's honesty","It guarantees all content is safe","It automatically hides public JS secrets","TLS secures transport within its scope."],
  ["Can prebuilt HTML have interactive behaviour?","Yes","No","Only if called dynamic.html","Browser code can add behaviour after static delivery."],
  ["Which action persists source changes?","Save the edited project file","Only edit Elements","Only reload","The saved source is what a fresh local load reads."],
  ["Which panel records resources during a reload?","Network","Only Elements","The file manager","Open it before loading to capture events."],
  ["Which language primarily describes presentation?","CSS","HTML","DNS","CSS handles styling."],
  ["Which statement about local progress is correct?","It needs explicit sync/import to transfer devices","Hosting the page always transfers it","It is automatically inserted into public HTML","Storage and publication are different."],
  ["What makes a sound diagnosis?","Observed facts plus a clearly limited explanation","An invented exact timing","Reinstalling everything first","Use evidence and change the relevant layer."]
 ]});
const examples={journey:page("Week 2 | Inspection practice","    <h1>Trace this local page</h1>\n    <p>This document can be inspected without a server.</p>\n    <h2>My observation</h2>\n    <p>A temporary Elements edit does not normally save this file.</p>")};
module.exports={lessons,examples};
