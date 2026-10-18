# Charter — PLG Verified Close

Contract: C:/Projects/20261002_Ops/PROJECT-CONTRACT.md. Written 2026-10-18 with Karim.
Decisions taken 2026-10-18: name `verified-close`; new repo, `klameer/audited-ai-close` archived with
a pointer once v0.1 is live; README ends on a soft help door; v0.1 input = files folder first.

## 1. Identity
| field | answer |
|---|---|
| key, name | PLG, Verified Close |
| one line | Free plugin for Claude's month-end close: Anthropic's finance skills plus scripted figures, reviewer gates and an audit log. |
| kind | product |
| folder | C:/Projects/20261018_VerifiedClose |
| repo | github.com/klameer/verified-close (to create). Public from v0.1 with clean history, so anyone can install it free. Apache-2.0: the base is Anthropic's Apache-2.0 finance plugin, and Karim's close-pack code is relicensed from MIT to keep one licence. Local only until Karim creates the empty repo and says push. |
| live at | nowhere yet. v0.1: the GitHub repo (it is also the plugin marketplace), plus a codelessops.com record entry. |
| data | no app state. Sample data in `examples/caldergate/` (fictional, copied from BusinessAssets close-v2). Users' run outputs stay in their own folder. Backup: git, portfolio backup tier. |
| related | Supersedes klameer/audited-ai-close (Close Kit showcase). Source of the four close-pack skills: `C:/Projects/20260714_Grounded/close-kit/skills/close-pack/` (gets a pointer line once ported). Upstream: anthropics/knowledge-work-plugins `finance/`. Sibling: CLZ Close on Azure (same close, Microsoft stack). Data: BusinessAssets/caldergate. Feeds AGY (help door) and JOB (interview story). |
| logins | none. GitHub through Karim's `gh` CLI session. |

## 2. Why
| field | answer |
|---|---|
| problem | Finance teams trying Claude for the month-end close get skills that describe the method but compute nothing. The model does the arithmetic, nothing stops for a reviewer, and there is no record of who signed what. Anthropic's own finance plugin (8 skills, checked 2026-10-18) is prose only: no scripts, no gates. A controller cannot put that in front of an auditor. |
| for whom | Financial controller or finance manager at a UK SME or mid-market company who already uses Claude (Code, Cowork or desktop) and wants to try it on the close. No named first user yet. |
| lever | Both. Discoverable: a free repo built on Anthropic's most-starred finance plugins, found by people searching for Claude finance plugins, carried by an article series and LinkedIn. Interviewable: "I took Anthropic's finance plugin, found it computes nothing, and added scripts, reviewer gates and an audit log. Here is the run." |
| north star | Inbound conversations that cite the repo (recorded in CRM / JobSearch inbound). Stars, clones and issues are read alongside it. |
| not this | Not a hosted service or SaaS: it runs inside the user's own Claude. Not an ERP integration or posting engine: it never posts to a ledger, and the reviewer stays the control. |

## 3. Spec
| field | answer |
|---|---|
| spec doc | SPEC.md (draft; Karim signs the merge grid before any code, PLG-9) |
| v0.1 in | Anthropic `finance/` 8 skills imported at a pinned SHA, licence kept, changed files marked. The 4 close-pack skills ported and generalised: entity, period, currency, materiality and folder layout move into config. Three merges: close-management + close-checklist, reconciliation + bank-rec, variance-analysis + variance-report. Files-folder input (CSV/xlsx exports); ERP connector optional through Anthropic's `~~erp` placeholder. Caldergate example folder with a one-line sample close. Close log and audit binder. Tests: goldens, gate tests, `claude plugin validate` in CI. |
| v0.1 out | Scripted GL/intercompany recon, accruals and roll-forward (v0.2, using ideas from Anthropic's financial-services agents). Xero/QuickBooks export adapters. Hosted ERP MCP. Run-log portal (PLG-6). Anaplan variance commentary. Anthropic partner content. |
| first items | 1. PLG-9 merge grid and design signed (SPEC.md). 2. PLG-10 scaffold: repo, marketplace, clean-machine install. 3. PLG-2 port and merge the close-pack skills. |
| done means | On a clean machine, adding the marketplace `klameer/verified-close` and installing the plugin, then "run the May-26 close" on the bundled Caldergate folder completes three gated steps with goldens 6/6 and an audit binder. CI is green and the repo is public. |

## 4. Build
| field | answer |
|---|---|
| stack | Claude plugin format (plugin.json, marketplace.json, SKILL.md). Python 3.11+ scripts (openpyxl, python-pptx, reportlab). pytest. GitHub Actions running `claude plugin validate`, pytest and gitleaks. |
| runs where | Inside the user's Claude: Claude Code, Cowork or desktop with a connected folder; claude.ai through skill zips. No server, no port, no launch entry. Dev: `pytest` from the repo root. |
| depends on | BusinessAssets/caldergate close-v2 (copied once into `examples/`, frozen). Upstream knowledge-work-plugins (manual sync script against a pinned SHA). Cost £0: no hosting; test runs use Karim's Claude subscription. |
| tests gate | Pre-commit: pytest (script unit tests, goldens G1-G6, gate tests: step 2 refuses an unsigned step 1, corrupted input fails the checks) plus the structure validator. Before active: CI green, and a clean-machine install proven on Claude Code and Cowork. |
| budget | Phase-gated with no dates: each phase ends on its exit check. Money cap £0. Any cost that appears means stop and ask. |
| rules | See AGENTS.md: Apache notices on modified upstream files; no Anthropic or Claude marks in names; fictional data only; never the Board Pack Test score; never posts to a ledger; no push without Karim. |

## 5. Live
| field | answer |
|---|---|
| live looks like | (planned) github.com/klameer/verified-close. In 60 seconds a visitor reads the skill table (scripted + gated vs guidance only) and the two install lines; in about 15 minutes they run the sample Caldergate close. |
| first user | (planned) Karim's clean-machine run at v0.1; first stranger recorded when an issue or inbound conversation arrives. |
| run cost | £0 a month (GitHub public repo). |
| support | GitHub issues, read weekly. Upstream drift: the sync script is run before each release. |

## 6. Publicity
| field | answer |
|---|---|
| public artefact | The repo. The audited-ai-close README points here once v0.1 is live. |
| site record | `/record-update`: Projects index row plus a hub page for the article series. |
| LinkedIn | PLG-8 teardown post (article 1), PLG-12 testing post (article 2), PLG-13 v0.1 launch with a recorded Caldergate run (article 3). |
| long form | Three-article series on codelessops.com: the teardown, how I test an agent skill, the launch. |
| CV line | Built verified-close, a free Claude plugin that adds scripted figures, reviewer gates and an audit log to Anthropic's finance skills for the month-end close. |

## 7. Events and decide
| field | answer |
|---|---|
| events logged | Releases: git tags (from v0.1). Stars, clones, issues: GitHub (`gh api repos/klameer/verified-close/traffic/clones`), read weekly. Posts: LinkedIn ledger, project `verified-close`. Inbound citing the repo: CRM / JobSearch inbound. |
| experiment or measure | Weekly metric after v0.1: inbound conversations citing the repo. |
| review date | When the v0.1 launch post's Ops follow-ups close. |
| kill condition | No inbound mention and no outside issue or star movement once all three articles are out: HOLD (the repo stays public; building stops). |

## 8. Risks
- Upstream churn: knowledge-work-plugins changes nightly. Pin the SHA and sync by hand before each release.
- The upstream root LICENSE carries junk text (PR #193); copy the clean `finance/LICENSE` instead.
- Anthropic may ship scripted close skills of its own. Position the repo as the gate and evidence layer, and keep the merge grid current.
- Trademark: Apache §6 grants no marks. Describe origin only.
- Upstream skills carry a "not financial advice" disclaimer. Keep it, and add the same line to ours.
