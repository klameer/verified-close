# AI close: guardrails and data policy (one page)

**Organisation:** Caldergate Distribution Group Ltd (fictitious demo estate)
**Scope:** the month-end close run in Claude with the verified-close plugin
**Owner and signatory:** Financial Controller. **Review:** annually, or on any change to the
plugin, the close folder or the data it can reach.

## 1. What the AI can reach (least access)

| Connection | Access | Enforced by |
|---|---|---|
| The close folder | Read the exports, templates and prior months; write only into `_work/` and the period's filing folder | The session is opened on this folder and nothing else |
| The ERP | **None.** The close runs on exports placed in `02 System Exports/` | Nothing is connected; an ERP connector, if added, is read-only |

## 2. What may enter the conversation

Close working data (statements, cashbooks, trial balances, budgets, packs): yes. **Never:**
payroll or personal data, credentials or keys, anything outside the close's need-to-know. If a
document would be redacted for an auditor, it does not enter the conversation.

## 3. Human gates (nothing bypasses them)

1. Each step ends in a hard stop with its output filed as a **DRAFT** document. A **named
   reviewer signs with initials** before anything advances.
2. The scripts enforce the order: a step will not run until the step before it is signed in the
   close log.
3. Judgement items (a stale cheque, an unexplained variance) are put to the reviewer as explicit
   questions. The step cannot be signed without the decision, and the decision is kept in the log.
4. A failed check, a failed filing or a broken seal stops the close at that step.

## 4. Show your working (the audit trail)

Every figure is computed by a script, never by the model, and re-derived by independent checks
before the gate and again at sign-off. Every sign-off appends a sealed record to the close log:
reviewer, time, decision, and the sha256 of every file signed. A file edited after signing stops
the next step. Close-out compiles the **audit binder** (PDF) from the log. Commentary numbers
that are not in the signed sources are listed for the reviewer to verify: unattributed numbers
do not ship.

## 5. If something goes wrong

Suspect a figure: stop the close, keep the conversation (it is evidence), rerun the step's checks
and the golden set, and escalate to the owner. A signed step is never re-run; reset the period and
start again.

**Signed (Financial Controller):** ______________________  **Date:** ____________
