# Jordan (JO) — JoFotara E-Invoicing

**Code:** JO | **Region:** MEA | **Status:** Dev Complete (NOT live as of Apr 2026)
**Regulator:** ISTD (Jordan) via the JoFotara portal
**Go-live target:** May 15, 2026 | **First client:** MAF (Majid Al Futtaim)
**Priority:** P0 | **Sprint anchor:** EINV-Pla Sprint 6 (Apr 13 → Apr 26 2026)
**Consultant:** Avtax (3-month engagement, ~$2,200)

## What JoFotara is

JoFotara is Jordan's clearance-model e-invoicing system. An invoice has no legal standing until ISTD returns a signed XML + QR code via API. Live production only — there is no sandbox. ClearTax MVP scope is sales-only (outbound submission). No buy/fetch flow.

## Delivery model

- **Format:** UBL 2.1 XML, base64-encoded inside JSON `{"invoice":"<base64>"}`.
- **Endpoint:** `POST https://backend.jofotara.gov.jo/core/invoices/`
- **Auth:** static `Client-Id` + `Secret-Key` headers per device.
- **No bulk:** one invoice per call.
- **No cancel:** corrections are Credit Notes (type 381) referencing the original.
- **No fetch:** no GET / status / list APIs. First signal of credential failure = first submission failure.
- **Immutability:** once `Valid` from ISTD, the invoice is immutable.
- **Dedup key:** `(sellerTIN, ID, UUID)`. On retry of a rejected submission, generate a fresh UUID v4; the ID stays the same.

## Architecture footprint

- `einvoicing-core/einvoice-jo/` — country module (this repo holds the bulk of NV-266 work).
- `clear-routing/clear-jofotara/` — vendor module added by Kushagra under NV-273.
- `clear-sales/einvoice-global` — `ClientCredentialSetting` extended with `incomeSourceSequence` + `deviceId` (NV-265 / NV-269).
- `einvoice-interface/SchemaMapping/JO/SalesEinvoiceToJoFotaraXml.json` — JSON → UBL mapping.
- `einvoice-interface/validation/JO/JO-validation.xslt` — pre-submit validation rules (~20 BR-JO-### rules).

## Slack & people

- **Channel:** `#mea_jordan_egypt_oman_discovery` (`C0ABA7RC1QD`)
- **Engineering DM:** `C0ASEKS03K8` (Jordan team)
- **PM:** see `people.md`. Avtax is the regulatory consultant on shared Slack.

## Status today (Apr 2026)

- Scaffolding merged on PR #1325; mapper + 153 tests green; XSLT MVP shipped.
- Aquib's NV-265 enums (PRs #1313 + #392) and Kushagra's NV-273 (PRs #1323 + #134) are open and gating end-to-end.
- Vault config still pending on dev for `ENABLED_COUNTRIES`, `SCHEMA_MAPPING_FILE_PATHS`, `JOFOTARA_*`, and `countryRouterServiceMap` — see `live_state.md`.

## Open spec questions

Tracked in `runbook.md`. Most-pressing: retry backoff (PRD vs Avtax conflict), auth HTTP code (401 vs 403), Special Sales tax shape (slides vs tech mapping), and Buyer Name mandatory for exports.

Sources: `project_jordan_einvoicing.md` §1-3, §11; `jordan_implementation_log.md` Sessions 1-4.
