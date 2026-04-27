# Peppol — Live State

**As of memory snapshot 2026-04-18.**

## Status: Live (with EUSR/TSR active — manual mode, automation in flight)

- ClearTax AP ID: `POP000602`.
- Cert: G3 (updated from G2 in Mar 2026).

## Submission track record

| Month | Status | Submitted | EUSR tx UUID | TSR tx UUID |
|---|---|---|---|---|
| Jan 2026 | Done | Feb 11, 2026 | `a6eb4231-00a5-482e-8e6b-8bd4a0847c29` | `69ca26d0-6bfd-4381-8269-c1234f46a585` |
| Feb 2026 | Done | Mar 10, 2026 | — | — |
| Mar 2026 | Done | Apr 14, 2026 | `fe3a6b2f-fc94-413d-bddf-ac7938de28fc` | `24157942-7cba-4004-a1f7-aca9dc97900a` |
| Apr 2026 | Target automated | Due May 15, 2026 | — | — |

Apr 14 manual submission was the third manual one — automation target. Includes MLS counts (pre-Apr 17 scope reading); the new automation will exclude them. Expect numerical differences vs Apr 14 baseline.

## Component status

| Component | Status |
|---|---|
| A — PR #156 (`save_vat_in_transactions_collection`) | **Merged to main 2026-04-23.** Tax-ID filter still scoped to `INVOICE \|\| CREDIT_NOTE` — needs broadening to `EINVOICE_DOCUMENT_TYPES`. |
| B — `backfill_country_codes_e2e.py` | Updated. Needs re-run on QA with new field names + self-billed; then prod. |
| C — `feat/peppol_report_automation` branch | 24 files uncommitted, last touched Apr 5. 0 commits ahead of main as of Apr 15. Needs commit + push + PR. |

## Outstanding open questions

1. **CDAR handling** — Prachi to ask France expert at OpenPeppol. Open since Apr 8.
2. **TDD inclusion** — Apr 17 wording "AS4 messages with business transaction" is ambiguous. Ask Prachi to clarify.
3. **Retroactive correction** — Jan/Feb/Mar submissions counted MLS. Resubmit corrected, or leave as-is?

## Resolved by Apr 17 scope change (no longer issues)

- MLS/MLR receiverCountry null problem.
- SP cert C2/C3 country extraction.
- SchemeID → Country map for MLS fallback.
- Self-exchange case (C2 == C3).
- SCH-TSR-11/12 PerSP-DT-PR-CC blocker (largely moot now).

## Implementation gaps remaining (post-Apr 17 simplification)

1. `ReportAggregationRepositoryImpl` filter → `$in: [INVOICE, CREDIT_NOTE, SELF_BILLED_INVOICE, SELF_BILLED_CREDIT_NOTE]`. Use `EINVOICE_DOCUMENT_TYPES` constant. + TDD if confirmed.
2. PR #156 follow-up — broaden tax-ID filter from `INVOICE \|\| CREDIT_NOTE` → `EINVOICE_DOCUMENT_TYPES` (add self-billed variants).
3. Hardcoded tax authority country map (AE, FR, ES, etc.) for TDD receiver country — only if TDD confirmed in scope.
4. Test coverage for self-billed doc types.
5. Backfill script verification — already handles self-billed correctly? Re-check before prod run.

## Execution order (post-Apr 17 reset)

1. Confirm TDD inclusion with Prachi (clarify "business transaction" wording).
2. Finalize PR #156 follow-up — broaden tax-ID filter.
3. Re-run backfill on QA with new field names + self-billed.
4. Run backfill on prod for historical records.
5. Commit `feat/peppol_report_automation` (24 files) and push.
6. Update branch with simpler changes — aggregation filter, possibly TDD tax authority map.
7. Create PR for `feat/peppol_report_automation`.
8. Test on QA — manually trigger via `/internal/reports/generate?yearMonth=2026-03`.
9. Compare output against manual Apr 14 report — expect differences (no MLS counts).
10. Deploy to prod before May 15 deadline for April 2026 report.

## Compliance deadlines

- **Reporting period:** previous calendar month (1st to last day).
- **Submission deadline:** 15th of following month.
- **Reminder email:** 11th if not received.
- **Non-compliance mark:** 16th if still not received.
- **Next target:** April 2026 report — due May 15, 2026.

## Reference docs

- LLD (current): https://docs.google.com/document/d/13bO2gzIkKEa2p9jEckawTsWMqQEYIVIheWd4pOzON4E/edit
- Parent HLD: "Global Clear Peppol AP - HLD" by Anand Mohan (team Google Docs).
- PRD: `/Users/vashistha.garg/Desktop/EUSR & TSR Details.docx` (may have moved — not found 2026-04-15).

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_peppol_reporting.md` §2, §4, §9, §10, §13.
