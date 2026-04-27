# UAE — Oncall Runbook

Common errors, debug paths, RCAs encountered.

## RCAs (UAE / MEA)

| Item | Notes | Drive doc |
|---|---|---|
| GCC Outage RCF | Author: Shashank Jannu (NOT user-owned). Cross-GCC. | (TODO — link if needed) |
| Sev1 RCF Dec 10 | Author: Nichelle Aranha (NOT user-owned). | (TODO) |
| Eicher RCA | Author: Vikas Jethnani (NOT user-owned). India-side but referenced. | (TODO) |

User has not authored a UAE-specific RCA in current memory. Future RCAs should land here using `prompts/rca_template.md` (VP-praised NIC RCF format).

## Common errors / debug paths

### TaxCategory ordering regression

- **Cause:** Historic UBL serialization bug in `einvoice-ae`. UBL spec requires elements in a specific order within `TaxSubtotal/TaxCategory`.
- **Fix:** einvoicing-core#1282 + 18-test regression guard. Re-run regression suite on any UBL changes.

### Arabic string rendering wrong on PDF

- **Cause:** Templates 5/6/8/9 route through Kramer; translation service may have stale strings.
- **Fix:** Coordinate with pdfgenerator team. Refresh translation cache.
- **Reference threads:** Jan 12 design thread (https://cleartaxtech.slack.com/archives/C09TU9UMJJ2/p1768202789046269); Jan 19 deploy (https://cleartaxtech.slack.com/archives/C04U10T2DAN/p1768812228954269).

### MEA XSLT architectural drift

- **Cause:** Shared validation XSLTs across MEA tend to accumulate country-specific branches.
- **Discussion:** Mar 24 thread #e-invoice-tech-internal (https://cleartaxtech.slack.com/archives/C09AC9XKTC5/p1774356638215179) — Vashistha held architectural line.
- **Decision tree:** when a new country wants a tweak, prefer per-country XSLT subdirectory over branching the shared XSLT.

### Postal code cross-MEA inconsistency

- **Cause:** UAE and KSA postal-code schemas differ. Without country conditioning, validation falsely passes/fails.
- **Fix:** Filed as EINVG-1983. KSA postal-code thread Mar 19 with Rahul Meena (PM): https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1773911560622319

### NV-173 MEA Re-routing post-launch issues

- **Symptom:** Various — 11 follow-up PRs after the Mar 26 launch.
- **Reference PRs:** see `live_state.md` and `code_map.md`.

## Decision trees

### Tabby (or any B2C) submission failure

1. Validate B2C-specific validation rules from `einvoice-ae` (9 classes).
2. Cross-reference einvoicing-core#888 (the launch PR).
3. Check `clear-routing/clear-ae-fta` OAuth2 token freshness in Redis.
4. If reproducible — file ticket and grab Tabby thread context from #einvoicing_global_platform.

### FTA submission failure (B2B)

1. Capture FTA error code.
2. Check Redis-cached OAuth2 tokens — both tokens of the dual-OAuth.
3. Validate UBL XML against the 9 validation rule classes.
4. Confirm TaxCategory order regression suite passed pre-deploy.

## Logs to grep

- `einvoice-ae` validation rule logs.
- `clear-ae-fta` vendor module logs.
- `einvoicing-integrations` upload endpoint logs (PR #493).
- `pdfgenerator` Kramer template logs (templates 5/6/8/9).

## Architectural lines held

- **Translation Service for MEA cross-service** — Jan design + Jan deploy. Vashistha-led decision: build a single translation service that all MEA countries can use, rather than embedding strings per template.
- **MEA XSLT architectural line** — Mar 24 thread.
- **Tabby UAE kickoff — questions before code** — Dec 2 2025.

## Open items

- TODO: capture FTA error code reference table.
- TODO: link concrete debug paths for each of the 11 NV-173 follow-up PRs.

Sources: `project_perf_review_fy26.md` §4 H2; §6 P&B; §7 (Translation Service Leadership); §9 Slack permalinks.
