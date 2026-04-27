# UAE — Live State

**As of memory snapshot Apr 2026.**

## Status: Live (mature, multiple customers)

- **Tabby B2B/B2C** live Dec 16, 2025 — first major B2C customer.
- **MEA Re-routing (NV-173)** live Mar 26, 2026 — P0 cross-country shift.
- **Arabic translation service** live Jan 19, 2026 — cross-MEA, 90-reply deploy thread.
- **TaxCategory ordering fix** + 18-test regression guard merged earlier in H2.

## Active workstreams

- MEA on-call rotation handles UAE incidents.
- KSA postal-code with Rahul Meena (PM) thread Mar 19 → ticket EINVG-1983 (cross-MEA postal handling).
- Continuous validation rule maturity (9 classes in `einvoice-ae`).

## Customers onboarded

- **Tabby** — Dec 16, 2025. B2C-led launch.
- (Others — list extends to all UAE customers using ClearTax FTA submissions; specifics not in current memory.)

## Known issues / warnings

1. **TaxCategory ordering** — historic UBL serialization bug; fixed in einvoicing-core#1282 with 18-test regression guard. Future UBL changes must run the regression suite.
2. **Arabic translation correctness** — pdfgenerator templates 5/6/8/9 use Kramer; updates need MEA QA review.
3. **MEA Re-routing complexity** — NV-173 required 11 follow-up PRs across 5 repos. Future cross-region routing changes are similarly broad.
4. **Country-conditional postal code** — KSA postal-code with Rahul Meena (PM) flagged need for country-aware postal handling. Filed as EINVG-1983.

## Recent SEV1 / outage history

- See `regions/gcc/runbook.md` and `regions/gcc/live_state.md` for cross-MEA outages.
- "GCC Outage RCF" by Shashank Jannu (H2; not user-owned but referenced).
- "Sev1 RCF Dec 10" by Nichelle Aranha (H2; not user-owned).

## NV-173 — what shipped

Live Mar 26, 2026. P0. 11 PRs:

- `einvoicing-core` #1167 (lead PR), #1258, #1254, #1072, #1099, #1069, #1026, #1033, #1003, #1047
- `cloud-init#6662`, `ct-app-config#8098`, `clear-peppol-ap#165`
- `e-invoicing-be#3716, #3714`

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_perf_review_fy26.md` §4 H2 picks 1-2, 7, 10; §9 (Slack permalinks).
