// Original Week 2 lessons: networking concepts before security tools.
const h=v=>({t:'h',v}),p=v=>({t:'p',v}),key=v=>({t:'key',v}),tip=v=>({t:'tip',v});
const term=(v,note)=>({t:'new',v,note});
const check=(q,a,why)=>({q,a,why});
const ref=(title,url)=>({title,url});
module.exports={
 '2.1':{
  objective:'Distinguish a local network from the internet and the Web, explain what common network devices do, and follow a request from your browser to a website.',
  sections:[
   h('1. Connect Week 1 to a real journey'),
   p('Last week, you mapped devices, applications, data and services. Today, imagine Maya opens a hosted learning page on her laptop. The page is stored somewhere else, so information must travel between her browser and the service. Networking is the part that makes that communication possible. Cybersecurity asks which parts should communicate, how the communication is protected and what evidence shows when something goes wrong.'),
   term('Network and local area network (LAN)','A network connects devices so they can exchange information. A LAN connects devices within a limited local area, such as a home, classroom or office. Being on one LAN does not imply that every device is trustworthy.'),
   p('Two classroom computers can exchange information locally even when the internet connection is down. Conversely, seeing a Wi-Fi symbol only tells you something about a local connection; it does not prove that the school’s internet connection or the learning website is working.'),
   term('Internet and Web','The internet connects many networks. The Web is one service using that infrastructure: browsers request pages and other resources from web services. Email and other applications can also use the internet.'),
   h('2. Give each device a job'),
   term('Switch','A device that forwards traffic between connections in a local network. In a typical Ethernet LAN, it uses local network interface addresses to help deliver traffic to the intended connection.'),
   term('Router','A device that forwards traffic between different IP networks. It chooses a next step based on destination addresses and routing information. We will introduce IP addresses tomorrow.'),
   term('Wi-Fi access point','A device that provides a wireless connection into a network. Wi-Fi is the local radio connection; it is not another name for the internet.'),
   p('At home, one box may combine an access point, a switch and a router. Some installations have a separate modem or fibre connection device that connects to the provider’s service. The box count is not the job count. Learn the roles so that a different physical layout does not confuse you.'),
   term('Internet service provider (ISP)','An organisation that supplies internet connectivity. Its network connects your network towards other networks; it does not store every website you visit.'),
   h('3. Follow the request and the reply'),
   p('A simplified path is:\nLaptop/browser → access point → home router → provider network → other networks → website service.\nA reply travels back towards the laptop. There may be many intermediate routers, and the return path is not guaranteed to be identical. This is a learning diagram, not a precise map of every real request.'),
   term('Request, response and resource','A request asks a service to do something or provide something. A response is the service’s reply. A resource can be a page, image, style file or other item the browser needs.'),
   p('The browser is the client for this interaction; the website service acts as the server. Client and server describe roles, not permanent categories of people or hardware. A computer can provide one service while requesting another.'),
   p('A page may require several requests for its images and scripts. Your browser may also reuse a previously stored copy. Therefore, opening one page does not necessarily mean one network exchange, and seeing a page does not prove that every part was freshly downloaded. The details will make more sense after DNS and protocols later this week.'),
   h('4. Keep boundaries and evidence clear'),
   p('Imagine the browser can display an offline course copy, but it cannot sync your progress. One path works and another does not. This could concern connectivity, the sync service or account access. The observation alone does not establish an attack. Start by saying exactly which action failed.'),
   p('Draw three groups: your device, your local network and external services. Under each, write who manages it and what you depend on. This makes the Week 1 ideas of assets, dependencies and scope visible. Owning the laptop does not give permission to test every device along the route.'),
   key('An access point provides a wireless local connection. A switch connects local traffic. A router forwards between networks. The Web uses the internet to deliver resources.'),
   tip('A useful first description is specific: the Wi-Fi connection exists, the offline page opens, but the online service does not reply. Avoid jumping straight to my internet was hacked.')
  ],
  checks:[
   check('Two school computers can share a permitted file, but the online course will not load. Is the local network necessarily broken?','No. Local communication can work while internet access or an external service is unavailable.','Separate the local path from the external path. Identify which dependency the failed action needs.'),
   check('One home networking box provides Wi-Fi and connects the home to the provider. Does it have only one role?','No. It may combine access point, switch and router functions, and sometimes additional functions.','Describe the work it performs rather than assuming one physical box equals one networking job.'),
   check('A browser requests a lesson and the hosting service returns it. Identify the client, server and response.','The browser is the client. The hosting service is the server. The returned lesson resource is a response.','These are roles in this interaction. The same machine can play another role in another interaction.')
  ],
  reflection:'Draw your imaginary request path. Label the device, LAN, router, provider and website service. Write one failure that could affect only part of the path.',
  references:[ref('MDN: how the internet works','https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Web_mechanics/How_does_the_Internet_work')]
 },
 '2.2':{
  objective:'Read simple IPv4 and IPv6 examples, distinguish local interface addresses from routed addresses, and explain a subnet and gateway without confusing an address with a person.',
  sections:[
   h('1. Addresses answer different questions'),
   term('Network interface and IP address','An interface is a device’s connection to a network, such as Wi-Fi or Ethernet. An Internet Protocol (IP) address identifies an interface for IP communication and helps networks deliver packets. A device can have several interfaces and addresses.'),
   term('Packet','A unit of information carried across a network, with addressing information and other details. A longer communication is carried in many units rather than one giant object.'),
   p('Think of sending labelled parcels between buildings. The destination label guides delivery, but it is not a statement about the sender’s character. Similarly, an IP address helps communication reach a destination. It does not prove a particular person’s identity, permission or intent.'),
   term('MAC address','An address used by a network interface for local link delivery, commonly written as six pairs of hexadecimal characters. Hexadecimal uses digits 0–9 and letters a–f. The address may change or be set by software. It is not a permanent proof of device identity.'),
   p('A router forwards the packet towards another network. Local delivery information is updated for each link; the laptop’s MAC address is not simply carried as the destination label across the entire internet. IP and MAC addresses solve different delivery problems.'),
   h('2. Read an IPv4 address and a prefix'),
   term('IPv4','An IP version with 32-bit addresses, commonly written as four decimal numbers from 0 to 255 separated by dots. Example: 192.168.50.20. A bit is a binary digit, either 0 or 1.'),
   term('Subnet and prefix length','A subnet is an IP network subdivision. A prefix length states how many initial address bits describe the network. In 192.168.50.20/24, the /24 is network information, not a port or part of the device name.'),
   p('For this simple /24 example, 192.168.50.20 and 192.168.50.30 belong to the network 192.168.50.0/24. The first three decimal groups match because 24 bits cover those groups. 192.168.60.20 is outside that /24. Do not use this visual rule for every prefix: /23 and /25 have different boundaries. Binary subnet calculations are a later topic.'),
   term('Default gateway','The router address a device normally uses for destinations without a more specific route. It is usually reachable on the device’s local network.'),
   p('Imaginary configuration: laptop 192.168.50.20/24; default gateway 192.168.50.1. The laptop can identify that a website outside its local subnet needs a route beyond that LAN. The gateway is a next step, not the website’s address. A broken gateway setting can affect external access even when some local communication works.'),
   h('3. Private addresses, public addresses and translation'),
   p('The standard private IPv4 ranges are 10.0.0.0–10.255.255.255, 172.16.0.0–172.31.255.255 and 192.168.0.0–192.168.255.255. They can be reused inside separate private networks and are not globally routed as public addresses. An address outside these ranges is not automatically public; other special-use ranges also exist.'),
   term('Network address translation (NAT)','Rewriting address information as traffic crosses a boundary. A common home IPv4 arrangement lets multiple private-address devices share a provider-facing address. NAT is an addressing mechanism; it does not replace firewall policy or application security.'),
   p('Two different homes may each have a laptop called 192.168.50.20. Several devices may also appear behind one outward address. Address information needs the network, time and observation location to be meaningful. A private address does not mean a device is immune to attacks.'),
   h('4. Recognise IPv6 and avoid identity claims'),
   term('IPv6','An IP version using 128-bit addresses. It is commonly written in hexadecimal groups separated by colons. Hexadecimal uses digits 0–9 and letters a–f. A double colon can shorten one consecutive run of zero groups.'),
   p('Example for reading only: 2001:db8::20. The 2001:db8::/32 range is reserved for documentation; do not treat it as a real reachable server. Likewise, later examples use 203.0.113.20 from an IPv4 documentation range. IPv6 has globally routable and special-purpose addresses, including local scopes. The IPv4 private-range list does not describe all IPv6 behaviour.'),
   p('Python can later organise permitted address lists, distinguish valid formats and group networks. It should use address-aware rules rather than assuming that every address starting with 172 is private. The security task is accurate inventory; the code comes after you understand the categories.'),
   key('Address + prefix + context helps explain delivery. An address alone does not establish identity or trust.'),
   tip('Common mistake: assuming all 172.x.x.x addresses are private. Only the 172.16.0.0/12 private range is covered by the rule above.')
  ],
  checks:[
   check('Are 192.168.50.20 and 192.168.50.30 in the same 192.168.50.0/24 example subnet? What about 192.168.60.20?','The first two are inside that /24; the third is outside it.','Use the stated prefix. Matching the first three groups is a shortcut for this /24 example, not a universal subnet rule.'),
   check('Does seeing one outward IP address prove that exactly one person used the connection?','No. Several devices or users may share it, and the address may change over time.','Interpret addresses with timestamps, network context and additional evidence. Avoid turning a delivery label into an identity claim.'),
   check('A device has a private IPv4 address. Does that prove its files are secure?','No. Private addressing describes routing scope, not file permissions, software safety or trustworthy users.','Security still needs access controls, updates, evidence and recovery. NAT and private addressing do not replace those protections.')
  ],
  reflection:'Describe the imaginary laptop address, subnet and gateway. Explain what each tells you, what it does not prove, and how Python could help keep an address inventory accurate.',
  references:[ref('Private IPv4 ranges: RFC 1918','https://www.rfc-editor.org/rfc/rfc1918.html'),ref('IPv4 example addresses: RFC 5737','https://www.rfc-editor.org/rfc/rfc5737.html'),ref('IPv6 example addresses: RFC 3849','https://www.rfc-editor.org/rfc/rfc3849.html')]
 },
 '2.3':{
  objective:'Explain how DNS finds name-related information and DHCP provides network settings, then distinguish their failures using an imaginary example.',
  sections:[
   h('1. A name and an address are different'),
   p('Maya remembers a learning site’s name more easily than its network address. Her device also needs local network settings before it can communicate normally. Two separate services help: DNS handles name-related information; DHCP can supply network configuration. They are frequently confused because both are involved in getting online.'),
   term('Domain name and DNS','A domain name is a structured name such as learn.example. The Domain Name System (DNS) stores and retrieves records associated with names. Finding an IP address for a name is a common DNS use; DNS does more than that.'),
   p('We use learn.example as an invented teaching name, not a website to visit. Imagine its address record points to the documentation address 203.0.113.20. This means a record provides address information. It does not mean DNS contains the lesson page or that the returned website is trustworthy.'),
   h('2. Follow a simple name lookup'),
   term('DNS resolver, authoritative server and cache','A resolver obtains answers to DNS queries. An authoritative server supplies records for names it is responsible for. A cache temporarily keeps earlier results so a new lookup may not need the same work again.'),
   p('Simplified fresh lookup: the browser or operating system asks its configured resolver about learn.example; the resolver may consult DNS servers; an address answer comes back; the browser can attempt a connection to that address. If an appropriate answer is already cached, fewer queries may be needed. This is why every page load does not produce an identical DNS sequence.'),
   term('A, AAAA and CNAME records','An A record provides an IPv4 address. An AAAA record provides an IPv6 address. A CNAME record gives an alias to another name. These are record types, not names of security tools.'),
   p('A service may have multiple address records or change them. One name does not always equal one machine, and one address may serve several names. Learn the relationship without making one-to-one assumptions. Cached results also help explain why a recent change can take time to be seen.'),
   term('Time to live (TTL)','For a DNS record, a value limiting how long an answer can normally be kept in a cache. It is a time limit, not a judgement that the website is safe.'),
   h('3. DHCP provides configuration'),
   term('DHCP and lease','Dynamic Host Configuration Protocol can supply IPv4 network configuration automatically. A lease is a time-limited assignment. Configuration can include an address, subnet information, a default gateway and DNS server settings.'),
   p('Imaginary new laptop: it joins the home LAN and asks for configuration. A DHCP server offers 192.168.50.20/24, gateway 192.168.50.1 and a DNS resolver setting. The laptop accepts suitable offered configuration and the server confirms it. The familiar beginner sequence is Discover → Offer → Request → Acknowledge, often remembered as DORA.'),
   p('The exchange helps agree on configuration; it does not prove that the network is safe. A home router may provide DHCP as another role. Some devices use manually configured settings instead. IPv6 can use other mechanisms, including router advertisements and DHCPv6; today’s DORA example is specifically about DHCP for IPv4.'),
   h('4. Separate failures before choosing a fix'),
   p('Situation A: the laptop has no usable address or route for the intended connection. Check local configuration and the connection first. Situation B: configuration appears correct and a known service can be reached, but a particular name cannot be resolved. Name lookup becomes a possible area to investigate. Situation C: the name resolves, but the website refuses account access. DNS answering is not proof that account permissions are correct.'),
   p('Do not randomly change DNS settings just because a page fails. Write the failing action and the evidence first. A stale record, incorrect configuration, service outage or account problem can require different responses. An inability to reach a guessed IP address is also inconclusive: websites may need the correct name and TLS details to work.'),
   key('DHCP can tell your device how to participate in the network. DNS can tell it information associated with a name. Neither is the website content or a guarantee of safety.'),
   tip('A DNS answer is a useful observation. It does not establish that the request reached the server, that encryption succeeded, or that the application accepted you.')
  ],
  checks:[
   check('Which service can assign the laptop an address and gateway: DNS or DHCP?','DHCP can supply those network settings.','DNS handles records associated with names. The DHCP configuration may include which DNS resolver to use, but the jobs remain different.'),
   check('A name lookup returns an address. Has the browser already downloaded the lesson?','No. Name lookup is a step towards reaching the service.','A connection and application request may still be needed. The service can be unavailable even when DNS is working.'),
   check('Why might opening the same page again not produce a new DNS query visible in your sample?','A suitable name result may already be cached, or the browser may reuse an existing connection.','Absence of a fresh visible query does not by itself show that DNS was bypassed maliciously. Consider how the example was observed.')
  ],
  reflection:'Write two separate journeys: joining a LAN using DHCP, and finding an address using DNS. Add one observation that would help distinguish a configuration problem from a name-lookup problem.',
  references:[ref('DNS concepts: RFC 1034','https://www.rfc-editor.org/rfc/rfc1034.html'),ref('DHCP for IPv4: RFC 2131','https://www.rfc-editor.org/rfc/rfc2131.html')]
 },
 '2.4':{
  objective:'Distinguish IP delivery, TCP/UDP transport and application protocols, then interpret an address-and-port pair without treating it as proof of a particular service.',
  sections:[
   h('1. Communication needs agreed rules'),
   term('Protocol','Agreed rules for exchanging information: how messages are formed, sent and interpreted. Different protocols address different parts of communication.'),
   p('A parcel comparison helps: an address guides delivery to a building, a numbered desk guides delivery inside, and the document itself follows rules its reader understands. In networking, IP addresses help reach interfaces, transport protocols help applications exchange data, and application protocols describe requests and responses. The comparison is a memory aid; the actual system is more precise.'),
   term('Transport and application protocols','Transport protocols help move data between communicating applications. Application protocols define the meaning of application messages, such as a request for a web resource. A transport connection succeeding does not prove the application accepted the request.'),
   h('2. TCP and UDP offer different services'),
   term('TCP','Transmission Control Protocol provides applications with a reliable, ordered stream of bytes over a connection. It tracks delivery, retransmits missing data where possible and reports connection failures. Reliability does not mean a failed network can always deliver everything.'),
   p('Imagine a practice document is split for transmission. If underlying pieces arrive out of order or one is lost, TCP works to present the receiving application with the correct ordered stream. The application still needs its own rules for recognising a complete document or request.'),
   term('TCP handshake','The initial exchange used to establish a TCP connection. In the usual basic example, the client sends SYN, the server replies SYN-ACK and the client sends ACK. These are TCP control flags, not application content.'),
   p('A handshake agreeing to exchange data does not sign you into a website or encrypt the information. Those are separate concerns. This distinction matters when reading records: a successful connection is evidence of transport progress, not proof that a lesson was loaded or an account was accessed.'),
   term('UDP','User Datagram Protocol sends individual messages called datagrams. UDP itself does not provide TCP-style delivery guarantees or ordered retransmission. Applications can add their own reliability and security mechanisms when using it.'),
   p('A voice application may prefer timely updates over waiting for every old sound fragment. This is a reason some applications use UDP; it is not a universal rule that UDP is always faster or that all video uses UDP. HTTP/3 uses QUIC over UDP, with additional mechanisms for reliable streams and protected communication. QUIC is a transport protocol built over UDP; you only need to recognise the exception today.'),
   h('3. Ports help identify a communication endpoint'),
   term('Port and endpoint','TCP and UDP use numbered ports to distinguish application communication endpoints. An endpoint includes an address and port, in a particular transport context. Ports are numbered from 0 to 65535; not every number has an identical purpose or usage.'),
   term('Listening service and temporary client port','A listening service waits for incoming communication on a configured port. A client commonly uses a temporary source port for its side of an exchange. The source and destination roles can reverse in a reply.'),
   p('Imaginary example: laptop 192.168.50.20 uses TCP source port 51000 to contact server 203.0.113.20 at destination port 443. The reply is directed back towards the client’s port 51000. Remember that the server address is documentation-only; this is a reading exercise, not a target to contact.'),
   p('Common conventions include HTTP on port 80, HTTPS on 443, traditional DNS on 53 and SSH on 22. SSH is a protocol for protected remote access and other services. Actual services can use other ports. TCP port 53 and UDP port 53 belong to different transport spaces, even though both can be used for DNS.'),
   h('4. Interpret evidence, not just numbers'),
   p('Seeing destination port 443 suggests a common HTTPS endpoint, but it does not prove the traffic is safe or even correctly implemented HTTPS. A port label is a convention. To understand a communication, consider the transport, application evidence, endpoint context and whether the action was expected.'),
   p('An open or listening port means something is available to communicate under the relevant conditions. It is not automatically a vulnerability. Risk depends on what service is exposed, who can reach it, its configuration and its purpose. We will learn exposure and vulnerability assessment later in the course.'),
   key('IP helps with delivery. TCP or UDP describes transport behaviour. A port distinguishes an endpoint. The application protocol gives messages their meaning. None of those labels alone proves authorisation.'),
   tip('TCP reliability is not encryption. UDP transport is not automatically insecure: applications using it may add strong protection. Keep these questions separate.')
  ],
  checks:[
   check('A TCP handshake finishes. Does that prove the user signed in successfully?','No. A transport connection was established; application authentication is a separate step.','The website could reject the later request, or the application exchange could fail before sign-in.'),
   check('The laptop sends from port 51000 to server port 443. Which destination port appears in the server’s reply to that client?','The reply is directed towards the client’s port 51000 in this example.','The receiving application needs the reply associated with the right endpoint. A boundary doing address translation may change what another observation point sees.'),
   check('Which statement is correct: TCP always encrypts data, UDP can never be secure, or transport and security are separate questions?','Transport and security are separate questions.','TCP gives ordered reliable transport, not confidentiality by itself. Additional protocols can protect communication over either transport.')
  ],
  reflection:'Explain one imaginary exchange using source address, source port, destination address, destination port and transport. Write what those details do and do not prove.',
  references:[ref('TCP: RFC 9293','https://www.rfc-editor.org/rfc/rfc9293.html'),ref('UDP: RFC 768','https://www.rfc-editor.org/rfc/rfc768.html'),ref('QUIC over UDP: RFC 9000','https://www.rfc-editor.org/rfc/rfc9000.html'),ref('IANA: service and port conventions','https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml')]
 },
 '2.5':{
  objective:'Explain HTTP, HTTPS and TLS, identify their protection boundaries, and reason about a basic firewall decision.',
  sections:[
   h('1. HTTP gives web messages meaning'),
   term('HTTP','Hypertext Transfer Protocol defines how clients and servers exchange web requests and responses. A request can ask for a resource; a response describes the result and may include content.'),
   term('Method, status and headers','An HTTP method states the intended action; GET commonly requests a representation of a resource. A status code reports a result; 200 commonly means success and 404 means the resource was not found. Headers carry additional message information.'),
   p('Imaginary request: the browser asks for the learning page. The service returns a successful status and page content. A 404 result instead tells you that the requested resource was not found; it does not prove your laptop was attacked. Even a 200 status does not mean every learning activity succeeded, because the application content and later requests still matter.'),
   h('2. TLS protects a communication channel'),
   term('TLS and HTTPS','Transport Layer Security protects communication against eavesdropping and tampering and supports authentication of communicating endpoints. HTTPS is HTTP used over a protected connection. For the usual browser case, the browser checks the server’s certificate for the requested name.'),
   term('Certificate','A signed statement connecting identity information, such as a website name, with a public cryptographic key. The browser checks the certificate under its trust rules. A certificate does not certify that the business is honest.'),
   p('A simplified HTTPS journey is: obtain address information; reach the endpoint; negotiate and validate a protected connection; exchange HTTP messages. Existing connections and cached information can reduce repeated work. Different HTTP versions have different transport details, so this is a concept map rather than a script every page follows exactly.'),
   p('Maya wants the intended learning site. A protected connection to a misleading lookalike site can still be protected communication with the wrong destination. Encryption can prevent an observer on the path from reading protected content while the recipient can still read what Maya deliberately sends to it. Correct destination and appropriate trust remain essential.'),
   p('TLS protection also ends at its endpoints. It does not prevent a compromised device from reading information after it is decrypted, fix a website’s account permissions or keep secrets private after you place them in published source. It is one control with a defined purpose.'),
   term('Metadata','Information about communication, such as timing, endpoints and sizes. Protected content and visible metadata are different. What an observer can see depends on the protocol and observation point.'),
   p('Avoid promising that HTTPS hides every fact about your browsing. It protects the HTTP content in transit, but observers may still see network addresses, timing and traffic volume. Some name information may be visible depending on DNS and TLS features. We will examine privacy boundaries more carefully later.'),
   h('3. Firewalls apply traffic rules'),
   term('Firewall and rule','A firewall controls traffic according to a policy. A rule may consider direction, addresses, protocol, ports and connection state. Firewalls can run on a device or at a network boundary.'),
   term('Inbound, outbound and stateful filtering','Inbound traffic arrives towards the protected device or network; outbound traffic leaves it. Stateful filtering tracks exchanges so replies can be treated in the context of permitted communication. Direction depends on the boundary being described.'),
   p('Imaginary policy: a laptop may initiate web access to an approved service, and replies for that exchange are allowed. Unsolicited inbound access to a remote management service is not allowed. You must define the boundary and purpose before calling a rule correct. This is reasoning practice; you are not asked to change your real firewall settings.'),
   h('4. Combine controls without overclaiming'),
   p('A firewall allowing port 443 does not guarantee every website reached through it is trustworthy. Likewise, blocking an unused service can reduce exposure without fixing a reused password. Ask which failure the control addresses and which ones remain. Week 1’s residual risk applies to network controls too.'),
   p('If a lesson fails to open, work through the observations: is there usable configuration; does the name resolve; can the relevant connection proceed; does TLS validation succeed; what does the application return? These are questions to investigate with permission, not reasons to disable safeguards randomly.'),
   key('HTTP describes the web exchange. TLS protects a channel and supports endpoint authentication. A firewall decides which traffic is permitted. None of them alone decides whether content or a person is trustworthy.'),
   tip('Treat certificate warnings as a reason to investigate the intended name, device time and service configuration through trusted routes. Bypassing a warning is not a normal troubleshooting shortcut.')
  ],
  checks:[
   check('A phishing site uses HTTPS. Is the site therefore honest?','No. The channel can be encrypted while the recipient’s purpose is deceptive.','Check the intended destination and request. A certificate is not a review of the service’s honesty.'),
   check('A firewall allows an outgoing web connection and its reply, but blocks unsolicited inbound remote access. Are those contradictory decisions?','No. They concern different directions, services and connection contexts.','A policy can permit intended work while limiting unnecessary access. Stateful rules can recognise replies to permitted exchanges.'),
   check('Does TLS protect a secret after it has been published inside downloadable website JavaScript?','No. Visitors receiving the file can read its contents.','Transport protection does not make intentionally delivered content private. Secrets need an appropriate storage and access boundary.')
  ],
  reflection:'Describe what HTTPS protects, what it does not protect, and a fictional firewall rule with a clear direction, service and purpose.',
  references:[ref('MDN: HTTP overview','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview'),ref('TLS 1.3: RFC 8446','https://www.rfc-editor.org/rfc/rfc8446.html')]
 },
 '2.6':{
  objective:'Read an invented network diagram and traffic summary, separate metadata from application content, and write conclusions supported by the available observations.',
  sections:[
   h('1. Draw the network before interpreting traffic'),
   p('Use this entirely imaginary network: laptop 192.168.50.20/24, gateway and local resolver 192.168.50.1, and learning service 203.0.113.20. The server address is reserved for documentation. No connection to that address is required. In this example, the home router also provides a DNS resolver role; real networks may arrange these roles differently.'),
   p('Draw the roles:\nLaptop → access point → router → external networks → learning service.\nFor a name lookup in this example: laptop → local resolver on the router.\nMark the local subnet, the gateway and where an observation was made. A diagram should help someone interpret the record, not merely decorate the page.'),
   term('Observation point','The place where information is recorded. A capture on the laptop, a record at the router and a log at the service can show different views of the same activity.'),
   h('2. Understand what a capture can contain'),
   term('Packet capture, header and payload','A packet capture records network traffic visible at a particular observation point. Headers contain delivery or protocol details; payload is the carried content at that layer. Encrypted application content may be present as unreadable data rather than readable words.'),
   p('Wireshark is a tool for inspecting captured traffic. You do not need to install it for today’s reading exercise. Real captures can contain private information and may include only part of an exchange. Use authorised sample material and respect the scope established in Week 1.'),
   term('Traffic summary and flow','A traffic summary selects useful fields from records. A flow groups related communication using context such as endpoints, transport and time. A summary may leave out facts that exist in the original capture.'),
   h('3. Read the invented teaching record'),
   p('The following is a deliberately simplified teaching summary, not a real capture:\n09:00:00 — laptop → local resolver — DNS query for learn.example.\n09:00:00.020 — resolver → laptop — address answer: 203.0.113.20.\n09:00:00.030 — laptop:51000 → server:443 — TCP SYN.\n09:00:00.050 — server:443 → laptop:51000 — TCP SYN-ACK.\n09:00:00.060 — laptop:51000 → server:443 — TCP ACK.\n09:00:00.070 onward — same endpoints — TLS negotiation and encrypted application records.'),
   p('Interpretation, step by step: a lookup was requested; an answer was recorded; the client attempted a TCP connection; the handshake progressed; later records show protected communication in the summary. The temporary client port 51000 links the replies with this example exchange. The named layers describe progress, not a single all-or-nothing event.'),
   p('What is missing? We have no readable HTTP response body, no user account log and no independent browser result. We therefore cannot prove which lesson content was read or that sign-in succeeded. The phrase encrypted application records does not reveal the protected message itself. A separate trusted application observation could answer that question.'),
   h('4. Compare another observation carefully'),
   p('Second imaginary summary: the laptop sends two TCP SYN messages towards the server, and no reply appears in the recorded sample. You can say no reply was observed there during that interval. You cannot conclude that the server is malicious or definitely offline. Possible explanations include a dropped packet, filtering, a route problem, capture limits or an unavailable endpoint.'),
   term('Retransmission and capture limitation','Retransmission means data or a control message is sent again after delivery is uncertain. A capture limitation is a reason your recording may be incomplete, such as its location, filters, timing or lost records.'),
   p('A repeated message can be normal recovery from network loss. Many records from one address do not automatically mean an attack. Start with expected activity, time and the source of the records; state the limits before deciding on a cause.'),
   h('5. Where Python helps, and where judgement stays'),
   p('Python can later organise a permitted saved summary: group endpoint pairs, count recorded messages, sort times and make a report. It can help you avoid overlooking a repeated pattern. It cannot recover missing evidence by guessing, and it cannot identify intent from a count alone.'),
   p('Write a four-line report: observation; possible meaning; uncertainty; next permitted check. Example: a handshake was recorded; transport progressed; lesson delivery is unknown; compare with the browser result or a permitted server log. This turns technical detail into a useful security explanation.'),
   key('Record what is visible, distinguish the layers and name what is missing. A summary of network activity is evidence with limits.'),
   tip('Do not copy a real shared-network capture into a public lesson or personal notes without permission. Today’s invented records give you the same reasoning practice without collecting anyone’s traffic.')
  ],
  checks:[
   check('In the teaching record, what tells you that the TCP handshake progressed?','The SYN, SYN-ACK and ACK sequence between the stated endpoints.','That supports a transport conclusion. It does not reveal the later protected application content.'),
   check('The sample has encrypted records on port 443. Can you conclude that Maya completed a particular lesson?','No. The summary lacks readable application evidence and completion records.','A plausible network exchange is not proof of a specific user action. Say what additional permitted evidence would be needed.'),
   check('Two requests appear and no replies are recorded. Give one observation and two possible explanations.','Observation: no replies appear in this sample interval. Possible explanations include filtering and an incomplete capture.','Other possibilities include loss, route problems or an unavailable service. Keep them as possibilities until more evidence distinguishes them.')
  ],
  reflection:'Write a four-line report about one invented exchange. Include the observation point, one supported conclusion, one uncertainty and a permitted next check.',
  references:[ref('Wireshark: introduction and capture concepts','https://www.wireshark.org/docs/wsug_html_chunked/ChapterIntroduction.html'),ref('TCP connection establishment: RFC 9293','https://www.rfc-editor.org/rfc/rfc9293.html')]
 },
 '2.7':{
  objective:'Explain the complete journey of a web request, analyse a network problem without overclaiming, and connect the week’s concepts to Week 1 security goals.',
  sections:[
   h('1. Rebuild the journey from memory'),
   p('Before rereading, explain how an imaginary laptop joins a local network, finds a learning service, communicates with it and receives a resource. You may draw boxes or write sentences. Name the role of each step rather than memorising a string of acronyms.'),
   p('A useful simple sequence is: obtain usable local settings; use DNS when name information is needed; route traffic towards an endpoint; use an appropriate transport; establish protection for HTTPS; exchange application messages. Caches, existing connections and different HTTP versions can change the visible sequence. The roles remain useful even when the exact messages differ.'),
   h('2. Analyse a connected fictional case'),
   p('Maya’s laptop has 192.168.50.20/24 and gateway 192.168.50.1. A fictional DNS result gives learn.example the documentation address 203.0.113.20. A permitted sample on the laptop shows a TCP handshake to port 443 and protected application traffic. A separate browser observation says the lesson page displayed. Maya’s progress still does not appear on a second phone.'),
   p('State the supported conclusions: the first laptop has stated configuration; name information was available; a transport exchange and protected traffic were recorded; a page displayed according to the browser observation. The second phone’s missing progress remains a separate question. Local storage, optional sync configuration, service behaviour and account access may matter. A successful page request does not establish successful progress sync.'),
   p('Connect this to Week 1: course access concerns availability; private sync content concerns confidentiality; accurate saved progress concerns integrity. Decide which specific information is missing before proposing a remedy. Removing a firewall or bypassing a certificate warning without evidence is not a useful conclusion from this case.'),
   h('3. Review the differences that matter'),
   p('Network vs Web: infrastructure vs a service using it.\nSwitch vs router: local forwarding vs forwarding between IP networks.\nIP vs MAC: routed addressing vs local link addressing.\nAddress vs identity: a delivery detail vs a claim about a person.\nDNS vs DHCP: name records vs network configuration.\nTCP vs UDP: different transport services.\nPort vs application proof: an endpoint convention vs observed behaviour.\nHTTPS vs trust: protected communication vs the recipient’s honesty.\nCapture vs conclusion: recorded evidence vs your interpretation.'),
   p('Give a fresh example of each difference. A precise explanation should include one limitation: a private address is not a safety guarantee; a port number is not proof of a service; a certificate is not a business recommendation; a repeated message is not automatically malicious.'),
   h('4. Mini challenge: explain a failure by layers'),
   p('Imagine the laptop has valid-looking configuration, DNS returns an address, but no server reply appears in a permitted ten-second sample. Write what works according to the observations, what is not shown and three possible explanations. Then describe a next check that stays inside your allowed lab scope. Do not invent a confirmed attacker.'),
   p('A sound answer says configuration and name information were observed; a successful exchange was not recorded; filtering, route failure or a limited recording might explain the gap. The next check should help distinguish explanations, such as reviewing the approved lab’s firewall record or comparing a second authorised observation. The exact action depends on the lab and permission.'),
   h('5. Prepare for Week 3'),
   p('You are ready when you can follow a request, identify where addresses and ports fit, distinguish DNS from DHCP and explain what protected communication does not prove. You do not need to calculate every subnet or operate a capture tool from memory yet.'),
   p('Week 3 studies operating systems, users, files, permissions, processes and a learning lab. The network picture explains how a service can be reached; the operating-system picture explains what runs on the device and what it may access. Together, these support careful defensive reasoning.'),
   key('Ask four questions of any record: where was it observed, which layer does it describe, what does it support, and what remains unknown?'),
   tip('Try the ten review questions without looking, reveal the reasoning and correct your explanation. Later, repeat with a different imaginary network. Aim for understanding rather than a memorised answer.')
  ],
  checks:[
   check('The Wi-Fi symbol appears. Does that prove an external lesson service is reachable?','No. It concerns a local wireless connection; the external path and service may still fail.','Separate access point connectivity, routing, name lookup and the service response.'),
   check('The laptop is 192.168.50.20/24. Is 192.168.60.30 in the stated local subnet?','No. It is outside 192.168.50.0/24.','Use the given /24 boundary. Do not assume that every private IPv4 address belongs to the same local network.'),
   check('Can a MAC address prove who performed an internet action?','No. It is local link addressing, may change, and is not a reliable personal identity claim.','Evidence about an account or person needs appropriate context and records beyond an address label.'),
   check('Which supplies local configuration, and which supplies a name’s address records?','DHCP can supply local configuration. DNS supplies name-related records.','A device may use manual settings and may reuse cached DNS information. The roles still differ.'),
   check('A TCP SYN-ACK is recorded. Does that reveal the password or HTTP response?','No. It is a transport control message.','TCP establishment is separate from protected content and application results. Observe the complete relevant evidence.'),
   check('Is TCP port 443 enough evidence that a service is safe?','No. The number is a common convention, not a security verdict.','Consider intended destination, actual protocol behaviour, authentication, permissions and expected activity.'),
   check('Name one protection HTTPS provides and one thing it does not guarantee.','It protects HTTP content in transit. It does not guarantee that the recipient is honest or that the endpoint device is uncompromised.','Protection has a boundary. A phishing recipient can receive data through a protected channel.'),
   check('Why can a firewall allow a web reply while rejecting unrelated incoming management traffic?','The traffic has different direction, service and connection context under the policy.','Stateful filtering can recognise replies to a permitted exchange. Explain the specific boundary you are describing.'),
   check('The first laptop displays the page, but the second phone lacks progress. What is the careful conclusion?','Page delivery was observed on the first device; cross-device progress availability remains unverified.','Check storage and configured sync separately. Page delivery does not prove that private data was transferred or restored.'),
   check('Write the four parts of a useful report for the no-reply sample.','Observation: no reply recorded in the interval. Possible meaning: exchange may not have completed. Uncertainty: source of the gap is unknown. Next check: compare a permitted lab record that can distinguish filtering, routing or capture limits.','State the observation point and permission. Python can organise records later, but cannot turn missing evidence into proof.')
  ],
  reflection:'Explain the complete fictional journey, then write three misunderstandings you corrected this week. Pick one weak topic to revisit before starting operating-system security.',
  references:[ref('MDN: HTTP request and response concepts','https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Overview'),ref('Wireshark: interpreting captured traffic','https://www.wireshark.org/docs/wsug_html_chunked/ChapterIntroduction.html')]
 }
};
