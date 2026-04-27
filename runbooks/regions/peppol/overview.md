# Peppol Network — EUSR/TSR Reporting

**Governing body:** OpenPeppol | **ClearTax AP ID:** `POP000602`
**Status:** Live (with EUSR/TSR reporting active — manual submissions Jan-Apr 2026; automation in flight)
**Repos:** `clear-peppol-ap` (primary), `einvoicing-be`, `clear-routing`

## What this region is

Peppol (Pan-European Public Procurement OnLine) is a 4/5-corner network for cross-border e-invoicing. ClearTax operates a certified Access Point (AP). This runbook focuses on the SP-level operational obligations — specifically the monthly EUSR/TSR reports that keep Peppol certification.

## Two reports, every month, by the 15th

| Report | Counts | Risk if missed |
|---|---|---|
| **EUSR** (End User Statistics Report) | Unique businesses active on the network during the previous calendar month | Loss of Peppol certification |
| **TSR** (Transaction Statistics Report) | Volume of business-transaction AS4 messages exchanged in the previous calendar month | Loss of Peppol certification |

Reminder email lands on the 11th if not received. Non-compliance mark on the 16th.

## Submission track record

| Month | Status | Submitted | Notes |
|---|---|---|---|
| Jan 2026 | Submitted | Feb 11, 2026 | First submission. Hotfix 1.50.5 fixed `DOCUMENTID InstanceIdentifier` format. |
| Feb 2026 | Submitted | Mar 10, 2026 | Manual. Prachi flagged `+00:00` must be omitted in `CreationDateAndTime`. |
| Mar 2026 | Submitted | Apr 14, 2026 | Manual. Updated keychain G2 → G3 cert for testbed. |
| **Apr 2026** | Target automated | Due May 15, 2026 | `feat/peppol_report_automation` branch — work is in flight. |

## Scope lock — what the reports count

OpenPeppol clarified on 2026-04-17 (via Prachi from OpenPeppol email): only AS4 messages that contain a *business transaction* may be counted. MLS, MLR, TSR, EUSR, and receipts are explicitly excluded.

**Final count-scope (4 doc types):**

1. `INVOICE`
2. `CREDIT_NOTE`
3. `SELF_BILLED_INVOICE`
4. `SELF_BILLED_CREDIT_NOTE`

**Excluded:** APPLICATION_RESPONSE (MLS/MLR), TAX_DATA_DOCUMENT (TDD — derived; pending re-confirmation), CDAR (France compliance doc — TODO France expert), EUSR/TSR themselves, receipts.

This 2026-04-17 scope correction supersedes the earlier "everything except EUSR/TSR" reading. Eliminates SP cert C2/C3 parsing complexity, tax authority country map, and most CDAR / PerSP-DT-PR-CC edge cases.

## ClearTax architecture (high level)

Pipeline: **Extract → Transform → Validate → Transmit**

1. Cron scheduler (consumer module) triggers on the 1st of each month at 02:00 UTC.
2. Aggregation runs MongoDB pipeline over `transactions` collection for the previous calendar month.
3. Report XML generation builds Peppol-compliant EUSR/TSR XML with SBDH wrapper.
4. Schematron validation against official XSLTs (EUSR v1.1.4, TSR v1.0.4).
5. S3 upload stores report XML.
6. SQS publish triggers AS4 transmission via existing outbound pipeline.
7. Status tracking via `report_submissions` MongoDB collection with idempotency.

## Slack & people

- **Group DM:** `C0AD7VBDX3M` (Anand Mohan, Prachi Singhal, Vashistha, Ayush, Vinay Hegde, Ishaan Bhatnagar, Kunal Arora) — read this DM first every session.

## Status today (Apr 2026)

- PR #156 (`save_vat_in_transactions_collection`) merged to main on 2026-04-23.
- Backfill script needs re-run on QA with new field names (`senderTaxId`/`receiverTaxId`), then on prod.
- `feat/peppol_report_automation` branch has 24 uncommitted files (last touched Apr 5) — needs commit + PR.
- Open question: Apr 14 manual submission included MLS counts. Resubmit corrected versions, or leave?

Sources: `project_peppol_reporting.md` §1-3, §5, §10.
