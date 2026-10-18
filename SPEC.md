# Verified Close — SPEC (signed 2026-10-18)

Status: **signed by Karim 2026-10-18 ("spec is fine, continue").** §8 answered as recommended,
except Q4 (see §0).

## 0. Showcase first (Karim, 2026-10-18)

"This is more for display and giving away free stuff than actual usage... the idea is they will see
it and ask me to implement it in their business." So the repo is written to be read, not
implemented:
- **Effort goes to what a reader sees.** That means committed outputs from a real run (signed rec
  workbook, variance report, pack, close log, audit binder), a diagram of the gated flow, a gate
  walkthrough, and the scripted-vs-guidance table.
- **It must still run.** The sample close runs end to end and CI is green, because credibility is
  the point. But it is built for Caldergate, not for any ledger.
- **Generalisation is cut to the minimum:** period, materiality and paths in `close.yaml`. There
  are no column mappings and no second fixture (Q4 reversed).
- **What is not generalised is the help door.** The README section "Running this on your ledger"
  lists what an implementation adds (your ERP or exports, chart of accounts, materiality, reviewers,
  pack template). That is the work Karim is hired for.

## 1. What it is

One Claude plugin, free on GitHub. It starts from Anthropic's `finance/` plugin
(anthropics/knowledge-work-plugins, Apache-2.0, 8 prose skills) and merges in the four close-pack
skills (`C:/Projects/20260714_Grounded/close-kit/skills/close-pack/`). Their skills supply the
method. Ours add what theirs lack: a script computes every figure, every step stops at a reviewer
gate, and a log records who signed what, sealed by file hash.

Teardown evidence (2026-10-18, Ops PLG-1 note): no close, rec or variance skill in either Anthropic
finance repo has a computing script or a gate.

## 2. Merge grid (sign-off item)

| Anthropic skill | close-pack skill | v0.1 treatment | label |
|---|---|---|---|
| close-management | close-checklist | Merge. Their T-3..T+5 checklist, dependency map and status definitions stay as method. Our orchestrator, gates, status board and close log become the run path. | scripted + gated |
| reconciliation | bank-rec | Merge. Their GL-to-subledger, bank and intercompany method stays. The bank account gets our scripted path (parse, reconcile, checks, workbook, gate). GL and intercompany stay method. | bank: scripted + gated; others: guidance only |
| variance-analysis | variance-report | Merge. Their decomposition and narrative template are applied on top of our script's numbers. Materiality comes from config. | scripted + gated |
| financial-statements | pack-build | Both ship. Statements as upstream. pack-build fills the management pack from signed figures only. | statements: guidance only; pack: scripted + gated |
| journal-entry, journal-entry-prep | — | As upstream. | guidance only |
| audit-support | (binder) | As upstream. Our close-out binder is cited as the evidence it asks for. | guidance only |
| sox-testing | — | As upstream. | guidance only |

The README carries this table. A guidance-only skill is never presented as verified.

## 3. Repo layout (proposed)

```
.claude-plugin/marketplace.json      marketplace "verified-close", one plugin
verified-close/                      the plugin
  .claude-plugin/plugin.json
  CONNECTORS.md                      upstream, plus the files-folder input
  skills/<8 upstream names + pack-build>/SKILL.md (+ scripts/ where scripted)
examples/caldergate/                 fictional close folder (close-v2) + close.yaml
tests/                               unit, goldens G1-G6, gate tests, structure
tools/sync_upstream.py               diff against the pinned upstream SHA
tools/build_zips.py                  claude.ai skill zips into dist/
UPSTREAM.md  LICENSE  README.md
```

## 4. Generalisation (today about 56 places hardcode Caldergate or May-26)

`close.yaml` in the user's close folder holds:
- entity, currency, period, period end, materiality threshold;
- file paths: bank statement, cashbook, prior rec, trial balance, budget, pack template;
- column mapping for each CSV/xlsx export.

Input defaults to that files folder. If an `~~erp` connector is present, the skill may pull from it
and file the raw pull as evidence first, as the kit does today.

Proof of generality: a second tiny fictional fixture (different currency and period) passes the same
pipeline in the test suite.

## 5. Gate and log contract (kept from the kit)

- Each step writes DRAFT outputs and one gate message, then stops.
- The reviewer signs with initials (plus an optional decision note). `audit_record.py` appends one
  record to `audit/close-log.jsonl`: period, step, reviewer, time, output files with sha256, check
  results, decision note. Signed files are renamed `SIGNED <initials>`.
- A step without a signed predecessor refuses to run. The log is the only source of run state.
- Close-out builds the audit binder from the log.

## 6. Tests

| tier | what |
|---|---|
| unit | each script (parse, reconcile, variance, build_pack, audit_record) |
| goldens | G1-G6 on Caldergate May-26 (existing `golden-set.yaml`) |
| gates | unsigned step 1 blocks step 2; a hash mismatch blocks sign-off; a failed check stops the step |
| generality | the second fixture runs end to end |
| structure | `claude plugin validate`; frontmatter lint; every modified upstream file carries its notice; every skill appears in the README table |
| install | clean machine: marketplace add, install, sample close (Claude Code and Cowork) |

## 7. Phases (exit checks, no dates)

| phase | exit check | Ops |
|---|---|---|
| P0 decide + teardown | charter decisions taken; teardown logged | PLG-7, PLG-1 (done) |
| P1 design | this SPEC signed by Karim | PLG-9 |
| P2 build | goldens 6/6, gate + generality tests green, clean-machine install proven | PLG-10, 2, 11, 3; article 1 PLG-8 can run alongside |
| P3 publish v0.1 | repo public; a stranger can run the sample close; old repo points here | PLG-4, 13, 12 |
| P4 iterate | v0.2 chosen from issues and PLG-14 | PLG-14, 6, 5, 15 |

## 8. Open questions for sign-off

1. Skill names after a merge: keep the upstream names (`reconciliation`, `variance-analysis`,
   `close-management`) so Anthropic plugin users recognise them (recommended), or use ours?
2. Guidance-only upstream skills ship byte-identical, with attribution in UPSTREAM.md
   (recommended)? Merged skills carry the modified-file notice.
3. Run log (PLG-3): v0.1 keeps `close-log.jsonl` as is, and one-file-per-record waits for a second
   plugin (recommended)?
4. Second generality fixture in v0.1 (recommended): yes or no?
