---
name: management-pack
description: Step 3 of the gated month-end close. Fills the management pack template from the reviewer-signed bank reconciliation and variance report, verifies every figure against them, and stops at the reviewer gate. Use when running the close or when asked to build the monthly management pack.
---

# Management pack (step 3 of the close)

**Important**: This skill assists with management reporting but does not provide financial
advice. The pack should be reviewed by qualified financial professionals before it is issued.

You orchestrate; **the script places every figure from the signed step outputs. Never type a
number into the pack yourself.** Run from the close folder (the folder holding `close.toml`) as
`python <this skill's folder>/scripts/<script> close.toml`.

## Verified run

1. Write the pack commentary to `_work/<period>/step3/commentary.txt`: the reviewer-signed step 2
   commentary on the flagged lines, plus one line on the bank position. Every number carries its
   source document.
2. `run_step3.py close.toml` refuses unless steps 1 and 2 are signed and both seals still hold:
   a signed figure edited after sign-off stops the pack. It builds the pack from the template,
   runs checks C1-C3 (cash figures to the penny, every variance row verbatim, every P&L subtotal
   verbatim) and files the DRAFT. If it stops, report verbatim and STOP. If it lists numbers under REVIEWER MUST
   VERIFY, carry that list into the gate: they are commentary numbers the reviewer confirms
   against the cited documents.
3. Present the slide summary, where each figure came from, and the must-verify list.
   **GATE. Say exactly this and stop:**
   > Reviewer sign-off required. The management pack is filed as DRAFT. Reply with your initials
   > to sign off step 3, or raise a query.
4. Only after sign-off: `sign_step3.py close.toml <initials>`. It re-runs the checks, turns the
   title slide's DRAFT status line into "SIGNED <initials> <date>", seals the filed copy and the
   commentary in the close log and confirms the filings. Then hand back to `close-management`,
   which offers the close-out.

## Rules

- The pack contains no figure that is not in a signed step output, and no commentary number
  without a document citation.
- The template's contract: `{{CASH_TABLE}}`, `{{VARIANCE_TABLE}}`, `{{COMMENTARY}}`,
  `{{SIGNOFFS}}` and `{{PERIOD}}` tokens, and a DRAFT status line on the title slide.
