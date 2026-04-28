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

<!-- Discovery 2026-04-28 from /v-country-brain session re: Tabby VAT rate prints 500 instead of 5 -->
### VAT rate prints 100× expected on PDF (e.g. `500` for 5%)

- **Symptom:** PDF renders VAT rate as 500 (or 600, 1500) when payload value is 5 (or 6, 15). Affects UAE templates (9, 10, 11, 12 confirmed; likely all UAE templates).
- **Diagnosis path (Step 3.5 — config-drift):**
  1. Confirm payload-type: UAE prints route through `EINVOICE_GLOBAL` (since Nov 2025, `pdfgenerator` PR #414).
  2. `EInvoiceGlobalDocumentData.kt` multiplies `percent × 100` by design — expects decimal-fraction input (0.05).
  3. einvoicing-core `PrintSchemaMapper.convertPercentForPrint` is supposed to convert 5 → 0.05 BEFORE sending. It only does so when `isPercentInWholeNumberFormat=true`.
  4. The flag is set from the Spring property `print-service.wholeNumberPercentCountryCodes`. If `AE` is not in that set, percent stays as 5 → renders 500.
- **Root cause:** env-var `WHOLE_NUMBER_PERCENT_COUNTRY_CODES` missing `AE` for one or more einvoicing-core pods (sync REST API, Kafka consumer, Temporal worker).
- **Fix (confirmed Apr 28 2026):** add `AE` to the Vault key `WHOLE_NUMBER_PERCENT_COUNTRY_CODES` for every einvoicing-core pod in EU region. Vault is the runtime source of truth — YAML defaults are fallback only.
- **Verification:** re-run the print curl from the original sub-thread (`https://cleartaxtech.slack.com/archives/C06JM8C19GR/p1777279094084079`); VAT rate should render as `5`.
- **Test gap:** `EInvoicePrintServiceImplTest.java:196-222` only asserts BE (true) and MY (false) — no AE assertion. Future fix should add an AE-flag-true test case.
- **Reference session:** `runbooks/countries/uae/_sessions/2026-04-28-100157.md`.

### Config layer — `WHOLE_NUMBER_PERCENT_COUNTRY_CODES` (and similar Spring flags)

**Source-of-truth hierarchy** for any einvoicing-core `@Value`-bound flag:

1. **Vault** (runtime, prod): the actual value loaded into each pod's env. `vault_path` per `data/countries.yaml` (UAE: `secret/einvoicing-core/`). This wins over everything below.
2. **Cloud-init / ct-app-config** (deploy-time): k8s ConfigMap or env-injection layer. Usually mirrors Vault.
3. **`application-prod.yml`** in each einvoicing-core module (build-time fallback): only used if env var unset. Defaults can — and do — diverge between modules.
4. **`@Value` annotation default** in Java code (last resort).

**Per-module YAML defaults observed Apr 2026** (each module is a separate Spring app with its own properties):

| Module | YAML default for `WHOLE_NUMBER_PERCENT_COUNTRY_CODES` |
|---|---|
| `application/` | `AE,BE` |
| `einvoicing-workflow-consumer/` | `BE` only |
| `einvoicing-temporal-worker/` | `BE` only |

If Vault drifts (e.g. AWS region migration env vars not carried over), pods fall back to YAML and AE-specific behaviour breaks silently — only visible at PDF render time.

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

<!-- Discovery 2026-04-28 from /v-country-brain session re: Tabby VAT rate prints 500 instead of 5 -->
- **`WHOLE_NUMBER_PERCENT_COUNTRY_CODES` per-pod parity** — must be set identically (including `AE`) across all three einvoicing-core pods (`application`, `einvoicing-workflow-consumer`, `einvoicing-temporal-worker`). YAML defaults diverge across modules; Vault is the source of truth. Verify on every region-migration / new-cluster spin-up.
- **Vault > YAML for env-var-bound Spring properties** — never trust `application-prod.yml` defaults as prod truth. They are fallback only. Real value is in Vault.

## Open items

- TODO: capture FTA error code reference table.
- TODO: link concrete debug paths for each of the 11 NV-173 follow-up PRs.

<!-- Discovery 2026-04-28 from /v-country-brain session re: Tabby VAT rate prints 500 instead of 5 -->
## Region-migration / cross-region drift checklist

Whenever AWS region / k8s cluster migration touches einvoicing-core (or any multi-pod Spring repo), run this BEFORE marking "migration done":

1. **Vault env-var parity check:** for each einvoicing-core pod (`application`, `einvoicing-workflow-consumer`, `einvoicing-temporal-worker`), dump the env vars in source region and target region. Diff. Any country-list env var (`WHOLE_NUMBER_PERCENT_COUNTRY_CODES`, similar) must match.
2. **YAML fallback safety check:** if Vault override is missing in target region, the pod will fall back to `application-prod.yml` default. Confirm those defaults are safe (i.e. include all live countries, not just defaults from the module's first-supported country). Today: `einvoicing-workflow-consumer` and `einvoicing-temporal-worker` defaults are `BE` only — unsafe for AE.
3. **Smoke-test the print path:** for each live country, render a B2C and B2B invoice PDF and confirm VAT rate displays correctly. The bug from the original session was invisible until a customer printed an invoice.
4. **Test fixture coverage:** confirm every live country is covered by a `*Test.java` assertion for any country-conditional flag (today's gap: `EInvoicePrintServiceImplTest.java` covers BE+MY, not AE).

Sources: `project_perf_review_fy26.md` §4 H2; §6 P&B; §7 (Translation Service Leadership); §9 Slack permalinks; `_sessions/2026-04-28-100157.md` (Tabby VAT 500 incident).
