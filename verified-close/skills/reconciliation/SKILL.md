---
name: reconciliation
description: Reconcile accounts by comparing GL balances to subledgers, bank statements, or third-party data. Runs the bank reconciliation as step 1 of the gated close (script-computed, checked, signed by a named reviewer). Use when performing bank reconciliations, GL-to-subledger recs, intercompany reconciliations, or identifying and categorizing reconciling items.
argument-hint: "<account> [period]"
---

# Reconciliation

> **Modified file** (Apache-2.0 §4(b)). Changed for verified-close, October 2026, from [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) @ `33eeda1`, `finance/skills/reconciliation/SKILL.md`: added "Verified run: bank reconciliation" and scripts/ (scripted bank rec, checks, sign-off); description extended. The title, disclaimer and intro above the Verified run, and everything after the horizontal rule, are the upstream text, unchanged.

**Important**: This skill assists with reconciliation workflows but does not provide financial advice. All reconciliations should be reviewed by qualified financial professionals before sign-off.

Methodology and best practices for account reconciliation, including GL-to-subledger, bank reconciliations, and intercompany. Covers reconciling item categorization, aging analysis, and escalation.

## Verified run: bank reconciliation (step 1 of the close)

**The scripts do all matching and arithmetic. Never match, total or classify a figure
yourself.** Every number you show comes from script output. Run from the close folder (the
folder holding `close.toml`) as `python <this skill's folder>/scripts/<script> close.toml`.

1. `run_step1.py close.toml` copies the bank statement and cashbook exports, takes last month's
   signed reconciliation as the opening position, then runs parse, reconcile, checks C1-C5
   (running balance, every line explained, rec identity to the penny, cashbook integrity,
   conservation) and files a DRAFT workbook in the filing folder. If it stops, report its output
   verbatim and STOP. Never present results from a run whose checks failed.
2. Present, from the script output only: the reconciliation statement, and each item under
   DECISIONS FOR THE REVIEWER as a question. An aged item is the reviewer's call, not yours.
   Point the reviewer at the DRAFT workbook in the filing folder: they sign a document, not a
   chat message.
3. **GATE. Say exactly this and stop:**
   > The draft reconciliation is filed for review. Nothing is signed until a named reviewer
   > signs. Reply with your initials and name to sign off step 1, with your decision on each
   > stale item, or raise a query.
4. Only after sign-off: `sign_step1.py close.toml <initials> "<name>" "<decision on each stale
   item>"`. It re-runs the checks on the files as they stand, refuses to sign a stale item
   without a decision, writes the SIGNED copy (next month's opening position: the close feeds
   itself), seals it in the close log and confirms the filings. Then hand back to
   `close-management`, or finish if run alone.

The scripted path applies the method below: the bank reconciliation format, the reconciling item
categories (timing differences clear on their own; aged items go to investigation) and the aging
escalation. GL-to-subledger and intercompany reconciliations have no scripted path yet: for those
this skill is guidance only.

---

*The rest of this file is the method from Anthropic's finance plugin, unchanged.*

## Reconciliation Types

### GL to Subledger Reconciliation

Compare the general ledger control account balance to the detailed subledger balance.

**Common accounts:**
- Accounts receivable (GL control vs AR subledger aging)
- Accounts payable (GL control vs AP subledger aging)
- Fixed assets (GL control vs fixed asset register)
- Inventory (GL control vs inventory valuation report)
- Prepaid expenses (GL control vs prepaid amortization schedule)
- Accrued liabilities (GL control vs accrual detail schedules)

**Process:**
1. Pull GL balance for the control account as of period end
2. Pull subledger trial balance or detail report as of the same date
3. Compare totals — they should match if posting is real-time
4. Investigate any differences (timing of posting, manual entries not reflected, interface errors)

**Common causes of differences:**
- Manual journal entries posted to the control account but not reflected in the subledger
- Subledger transactions not yet interfaced to the GL
- Timing differences in batch posting
- Reclassification entries in the GL without subledger adjustment
- System interface errors or failed postings

### Bank Reconciliation

Compare the GL cash balance to the bank statement balance.

**Process:**
1. Obtain the bank statement balance as of period end
2. Pull the GL cash account balance as of the same date
3. Identify outstanding checks (issued but not cleared at the bank)
4. Identify deposits in transit (recorded in GL but not yet credited by bank)
5. Identify bank charges, interest, or adjustments not yet recorded in GL
6. Reconcile both sides to an adjusted balance

**Standard format:**

```
Balance per bank statement:         $XX,XXX
Add: Deposits in transit            $X,XXX
Less: Outstanding checks           ($X,XXX)
Add/Less: Bank errors               $X,XXX
Adjusted bank balance:              $XX,XXX

Balance per general ledger:         $XX,XXX
Add: Interest/credits not recorded  $X,XXX
Less: Bank fees not recorded       ($X,XXX)
Add/Less: GL errors                 $X,XXX
Adjusted GL balance:                $XX,XXX

Difference:                         $0.00
```

### Intercompany Reconciliation

Reconcile balances between related entities to ensure they net to zero on consolidation.

**Process:**
1. Pull intercompany receivable/payable balances for each entity pair
2. Compare Entity A's receivable from Entity B to Entity B's payable to Entity A
3. Identify and resolve differences
4. Confirm all intercompany transactions have been recorded on both sides
5. Verify elimination entries are correct for consolidation

**Common causes of differences:**
- Transactions recorded by one entity but not the other (timing)
- Different FX rates used by each entity
- Misclassification (intercompany vs third-party)
- Disputed amounts or unapplied payments
- Different period-end cut-off practices across entities

## Reconciling Item Categorization

### Category 1: Timing Differences

Items that exist because of normal processing timing and will clear without action:

- **Outstanding checks:** Checks issued and recorded in GL, pending bank clearance
- **Deposits in transit:** Deposits made and recorded in GL, pending bank credit
- **In-transit transactions:** Items posted in one system but pending interface to the other
- **Pending approvals:** Transactions awaiting approval to post in one system

**Expected resolution:** These items should clear within the normal processing cycle (typically 1-5 business days). No adjusting entry needed.

### Category 2: Adjustments Required

Items that require a journal entry to correct:

- **Unrecorded bank charges:** Bank fees, wire charges, returned item fees
- **Unrecorded interest:** Interest income or expense from bank/lender
- **Recording errors:** Wrong amount, wrong account, duplicates
- **Missing entries:** Transactions in one system with no corresponding entry in the other
- **Classification errors:** Correctly recorded but in the wrong account

**Action:** Prepare adjusting journal entry to correct the GL or subledger.

### Category 3: Requires Investigation

Items that cannot be immediately explained:

- **Unidentified differences:** Variances with no obvious cause
- **Disputed items:** Amounts contested between parties
- **Aged outstanding items:** Items that have not cleared within expected timeframes
- **Recurring unexplained differences:** Same type of difference appearing each period

**Action:** Investigate root cause, document findings, escalate if unresolved.

## Aging Analysis for Outstanding Items

Track the age of reconciling items to identify stale items requiring escalation:

| Age Bucket | Status | Action |
|-----------|--------|--------|
| 0-30 days | Current | Monitor — within normal processing cycle |
| 31-60 days | Aging | Investigate — follow up on why item has not cleared |
| 61-90 days | Overdue | Escalate — notify supervisor, document investigation |
| 90+ days | Stale | Escalate to management — potential write-off or adjustment needed |

### Aging Report Format

| Item # | Description | Amount | Date Originated | Age (Days) | Category | Status | Owner |
|--------|-------------|--------|-----------------|------------|----------|--------|-------|
| 1      | [Detail]    | $X,XXX | [Date]          | XX         | [Type]   | [Status] | [Name] |

### Trending

Track reconciling item totals over time to identify growing balances:

- Compare total outstanding items to prior period
- Flag if total reconciling items exceed materiality threshold
- Flag if number of items is growing period over period
- Identify recurring items that appear every period (may indicate process issue)

## Escalation Thresholds

Define escalation triggers based on your organization's risk tolerance:

| Trigger | Threshold (Example) | Escalation |
|---------|---------------------|------------|
| Individual item amount | > $10,000 | Supervisor review |
| Individual item amount | > $50,000 | Controller review |
| Total reconciling items | > $100,000 | Controller review |
| Item age | > 60 days | Supervisor follow-up |
| Item age | > 90 days | Controller / management review |
| Unreconciled difference | Any amount | Cannot close — must resolve or document |
| Growing trend | 3+ consecutive periods | Process improvement investigation |

*Note: Set thresholds based on your organization's materiality level and risk appetite. The examples above are illustrative.*

## Reconciliation Best Practices

1. **Timeliness:** Complete reconciliations within the close calendar deadline (typically T+3 to T+5 business days after period end)
2. **Completeness:** Reconcile all balance sheet accounts on a defined frequency (monthly for material accounts, quarterly for immaterial)
3. **Documentation:** Every reconciliation should include preparer, reviewer, date, and clear explanation of all reconciling items
4. **Segregation:** The person who reconciles should not be the same person who processes transactions in that account
5. **Follow-through:** Track open items to resolution — do not just carry items forward indefinitely
6. **Root cause analysis:** For recurring reconciling items, investigate and fix the underlying process issue
7. **Standardization:** Use consistent templates and procedures across all accounts
8. **Retention:** Maintain reconciliations and supporting detail per your organization's document retention policy
