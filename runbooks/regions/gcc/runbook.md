# GCC — Oncall Runbook

The on-call-first view across UAE, KSA, BH, OM, QA, KW. Country-specific deep detail lives in country runbooks; cross-cutting on-call material lives here.

## RCAs (cross-GCC)

| Item | Notes |
|---|---|
| **GCC Outage RCF** (H2) | Author: Shashank Jannu. Cross-GCC. NOT user-owned. TODO link Drive doc. |
| **Sev1 RCF Dec 10** | Author: Nichelle Aranha. NOT user-owned. |
| **KSA Sev1 Apr 27 2026** | Referenced in `data/countries.yaml` (Redis/licensing). TODO link RCA when authored. |

## Common errors / debug paths

### MEA Re-routing follow-up bugs

- **Symptom:** Various — surface as routing/region misalignment after the Mar 26 NV-173 launch.
- **Reference PRs:** `einvoicing-core` #1258, #1254, #1072, #1099, #1069, #1026, #1033, #1003, #1047 — search by NV-173 label.
- **Decision tree:** check Region enum, RoutingService enum, country code propagation through MDC.

### Arabic string render wrong

- **Cause:** pdfgenerator templates 5/6/8/9 use Kramer translation; cache may be stale or template not aligned with translation service deploy.
- **Fix:** coordinate with pdfgenerator team. Refresh Kramer templates and/or translation cache.

### Country-conditional postal code wrong

- **Cause:** UAE and KSA postal-code schemas differ; unconditioned validation falsely passes/fails.
- **Fix:** Track via EINVG-1983.
- **Reference thread:** Mar 19 with Rahul Meena: https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1773911560622319

### Redis / licensing interaction (KSA Sev1 Apr 27 2026)

- **Cause:** TBD — capture from RCA when authored.
- **Hypothesis:** Redis cache for licensing tokens went stale or got evicted, blocking new submissions.
- **Fix:** TODO when RCA lands.

### Sentry alert noise (post EINVI-1260)

- **Cause:** Initial Sentry rollout for IND + GCC may have surface-level noise on existing prod paths.
- **Fix:** tune alert thresholds; coordinate with Yash + Roshan.

### MEA XSLT drift

- **Cause:** Shared XSLTs accumulate per-country branches.
- **Architectural line (Mar 24):** prefer per-country XSLT subdirectory over branching the shared XSLT.
- **Reference thread:** https://cleartaxtech.slack.com/archives/C09AC9XKTC5/p1774356638215179

## Decision trees

### Sev1 alert from #einvoice_mea_l3_support

1. Identify country (`country=<2-letter>` Sentry tag).
2. Check the country's `runbook.md` (e.g. `runbooks/countries/uae/runbook.md`) for the failure path.
3. If cross-GCC pattern (multiple countries failing simultaneously), suspect:
   - MEA Re-routing config drift (Region/RoutingService).
   - Shared service degradation (translation service, schema-registry).
   - Redis token cache.
4. Open RCA template (`prompts/rca_template.md`).

### KSA-specific Sev1

1. KSA group DM (`C0ANDUZ5893`) — primary signal.
2. Check ZATCA SDK version (3.4.2 vs 3.4.3 may matter).
3. Check Redis/licensing tokens.
4. Coordinate with Rahul Meena (PM) + senior engineering.

### UAE-specific Sev1

- Defer to `runbooks/countries/uae/runbook.md`.

## Architectural lines that govern GCC engineering

1. **Translation Service for MEA** — single cross-MEA service over per-template embedding (Jan 12 design + Jan 19 deploy).
2. **MEA XSLT** — per-country subdirectory over shared XSLT branching (Mar 24 internal).
3. **Validation rules pattern** — UAE's 9-class structure is the GCC reference; replicate for new countries.

## Logs to grep (cross-GCC)

- Sentry filter: `country IN (AE, SA, BH, OM, QA, KW)`.
- `clear-routing` `RoutingFactory` selection — confirm correct vendor module dispatched.
- Translation service logs — Arabic string lookups.
- Redis cache for OAuth2 tokens (UAE FTA) and licensing (KSA).

## Open questions

- TODO: capture KSA Apr 27 2026 RCA detail when authored.
- TODO: BH/OM/QA/KW go-live status and primary repos.
- TODO: cross-region currency / TIN handling matrix.

Sources: `project_perf_review_fy26.md` §4 H2 picks 2, 6, 7; §6 P&B (KSA postal); §7 (Translation Service Leadership); §9 Slack permalinks; `data/countries.yaml`.
