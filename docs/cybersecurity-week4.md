# Cybersecurity Week 4 — Accounts, identity and data protection

Seven English lessons follow the existing roadmap. The existing lesson renderer,
heading notes, visible daily notes, answer reveal and previous/next navigation
are reused. No localStorage schema, app function or other course changes.

## Study order

1. Identity/passwords: authentication versus authorisation, password uniqueness,
   passphrase unpredictability, manager/recovery dependencies and a fictional
   account-role map.
2. MFA/passkeys: factors, OTP/push limitations, service-bound credentials,
   device/sync dependencies, sessions, token scope/expiry/revocation and recovery.
3. Phishing: requested action, independent task verification, full URL host,
   lookalikes, polished-message limitations and evidence-based response.
4. Transformations: encoding versus encryption versus hashing, bytes, keys,
   trusted baselines, guessing limitations and Python integrity-report support.
5. Checksums/HTTPS: trusted release digest, specialised password verification,
   salt/work cost, connection versus content trust and transit/rest boundaries.
6. Backups/sensitive data: sync versus retained recovery, separate restore test,
   public code versus browser data, localStorage limitations, exposed-token
   response and redacted sample-data triage with Python.
7. Weekly retrieval: integrated fictional case, dependency reasoning, four
   learning deliverables and twelve closed-notes checks with model answers.

The six main lessons contain four reasoned checks each, for36 checks overall.
Notes should contain fictional reasoning and questions, not actual credentials
or personal backup content. No scripts collect credentials, scan a real account,
change permissions or rewrite repository history. Python is described only as a
supporting tool, preserving the user's cybersecurity-first learning preference.

All essential explanations and answers are embedded for offline learning.
Reference links below each lesson are optional further reading. Advice does not
claim an account or device is completely safe from a single indicator.

## Sources consulted

- [NIST authenticator/password guidance](https://pages.nist.gov/800-63-4/sp800-63b.html)
- [NCSC password managers](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/password-managers)
- [MDN WebAuthn](https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API)
- [MDN cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies)
- [FTC phishing awareness](https://consumer.ftc.gov/articles/how-recognize-avoid-phishing-scams)
- [Python Base64](https://docs.python.org/3/library/base64.html)
- [Python cryptographic digests](https://docs.python.org/3/library/hashlib.html)
- [OWASP cryptographic storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [OWASP password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [MDN TLS](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Transport_Layer_Security)
- [NCSC backups](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/always-back-up-your-most-important-data)
- [OWASP browser storage](https://cheatsheetseries.owasp.org/cheatsheets/HTML5_Security_Cheat_Sheet.html)
- [GitHub sensitive-data response](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

Explanations, decision scenarios and questions are original teaching material.
NIST guidance is identified as implementer guidance rather than a universal rule
followed by every website. MFA/passkeys and recovery are presented with their
actual dependencies; HTTPS and digest matching are not treated as blanket trust.

## Verification

Static checks compare every previous lesson and all code outside the teaching
map against commit452ec98. Isolated-browser checks use invented notes/progress
to verify all seven days, answer show/hide, heading/day note persistence,
navigation across week boundaries, old quizzes, mobile themes and console.
Existing backup/import merge-and-replace checks run with fictional data.
