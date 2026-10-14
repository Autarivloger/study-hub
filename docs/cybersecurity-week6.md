# Cybersecurity Week 6 — Security controls and vulnerability management

Seven English lessons,36 reasoned self-checks, worked fictional cases and first-use
concept explanations. The existing lesson renderer, visible daily notes, answer
show/hide and previous/next navigation are reused. No app functions, localStorage
defaults or other course content change.

## Study sequence

1. Baselines and maintenance: approved role-specific controls, inventory identity,
   support/version context, match/mismatch/unknown, update activation, authorised
   change/recovery and Python's role in record comparison.
2. Vulnerability reasoning: advisory applicability, CVE identity, CVSS severity
   versus local risk, exposure/reachability/exploitability, known exploitation,
   confidence, priority reasons and temporary restrictions.
3. Network/host layers: firewall conditions, stateful filtering, necessary paths,
   enforced segmentation, endpoint-control coverage and approved positive/negative
   verification without disabling protective settings.
4. Cloud: service-dependent shared responsibility, IaaS/PaaS/SaaS, IAM/scoped
   workload access, public resource policies, encryption boundaries, recovery/key
   dependencies and an accountable task/evidence matrix.
5. Repositories and recovery: visibility versus delivered content, private versus
   unlisted links, GitHub secret-gist readership, exposed-token response, RPO/RTO,
   usable restore points, retained data and a separate controlled restore test.
6. Findings: requirement/asset/source/time, bounded evidence, confidence and
   priority, remediation/mitigation/accepted risk, owner/review/closure criteria,
   preserved report identities and Python's supporting aggregation role.
7. Closed-notes review: an integrated maintenance/cloud/exposure/recovery case,
   four fictional deliverables, uncertainty, residual risk, review triggers and
   twelve questions with model answers and reasons.

The six main days have four checks each; the review has twelve. Essential material
is embedded in the offline HTML. Primary-reference links are optional further
reading. No additional external account, cloud subscription, scanning tool or
Python coding worksheet is needed.

## Teaching boundaries

All assets/products/findings are explicitly fictional; TRAIN-A/B and TRAIN-01
are not CVE records or claims about an actual product. No real account, Gist,
credential, firewall, router or cloud setting is read/changed. Activities are
policy diagrams, evidence rows, priority reasoning and recovery plans.

Important distinctions are stated directly:

- Configuration drift does not establish an attack.
- Downloaded/installed/active updates require different evidence.
- Unknown applicability is retained as unknown.
- CVSS severity is not attack probability or the complete local priority.
- Exposure and catalog membership do not prove a local incident.
- Segmentation needs enforcement; labels alone do not demonstrate protection.
- Shared responsibility depends on the actual service/task.
- GitHub secret gists are unlisted, not authenticated private stores.
- A public-source cleanup or privacy change does not revoke copied credentials.
- RPO/RTO targets must be compared with current usable recovery evidence.
- Mitigation or an unavailable retest is not a verified underlying fix.

The existing integration implementation is preserved. The lesson explains reader
boundaries accurately without claiming an audit of the user's actual storage or
silently restructuring sync. Sensitive-data response and repository-history
cleanup are teaching concepts, not operations performed by this update.

## Primary references

- [NIST patch-management lifecycle](https://csrc.nist.gov/pubs/sp/800/40/r4/final)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CVE identifier overview](https://www.cve.org/ResourcesSupport/FAQs)
- [FIRST CVSS4 specification](https://www.first.org/cvss/v4.0/specification-document)
- [CISA known exploitation catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [Microsoft host firewall](https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/)
- [AWS shared responsibility](https://aws.amazon.com/compliance/shared-responsibility-model/)
- [Microsoft cloud responsibility](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)
- [GitHub visibility](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility)
- [GitHub gist readership](https://docs.github.com/en/get-started/writing-on-github/editing-and-sharing-content-with-gists/creating-gists)
- [GitHub sensitive-data response](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
- [NCSC backup/recovery](https://www.ncsc.gov.uk/collection/top-tips-for-staying-secure-online/always-back-up-your-most-important-data)
- [OWASP protected event evidence](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)

Explanations, fictional scenarios, questions and paper templates are original.
Specific current vulnerability lists, deadlines and product claims are not copied
into a static lesson or represented as actual findings.

## Verification

Static checks compare all35 previous cybersecurity lessons and every byte of
app/storage/other-course code outside the teaching map with commit a5c7b27.
Isolated-browser checks use fictional progress and notes to test all seven views,
36 answer show/hide checks, note labels/save/hide/show/refresh, week boundaries,
old quizzes,375px layouts and light/dark themes with console-error capture.
Existing backup/import merge-and-replace checks also use fictional browser data.
The Week5 companion lab remains intact; no real browser profile or secret is read.
