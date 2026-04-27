# Jordan — Live State

**As of memory snapshot Apr 20-23 2026. Verify before quoting.**

## Status: Dev Complete (NOT live)

- **Go-live target:** May 15, 2026
- **First customer:** MAF (Majid Al Futtaim)
- **Current sprint:** EINV-Pla Sprint 6 (Apr 13 → Apr 26)

## What's done

- Scaffolding committed (PR #1325 open) — module wired, condition-on-country, S3 constants, no-op workflow initiator, govt action service overrides.
- Schema mapping JSON shipped (~320 lines, single file for 388 + 381).
- XSLT MVP shipped (~20 BR-JO-### rules).
- 153 tests green (50 mapper + 93 E2E XML + 10 service).
- Credential save flow works locally end-to-end (NV-269) with new `incomeSourceSequence` + `deviceId` fields.
- `validateTaxpayerCredential` overridden to skip gov verify (no JO verify API).
- `HttpServiceClient.x-clear-country-code` MDC-forwarding fix shipped.
- Local generate flow reaches Mongo `SUBMITTED` against `JofotaraMockClient` (Session 4 attempt #10).

## What's blocked or pending

| # | Blocker / pending | Owner | Notes |
|---|---|---|---|
| 1 | Aquib's NV-265 PRs (#1313 + #392) | Aquib | Blocks `incomeSourceSequence` production wiring + missing GovtResponse fields. |
| 2 | Kushagra's NV-273 PRs (#1323 + #134) | Kushagra | Blocks routing integration. Also has a contract bug — core's `JofotaraRoutingServiceImpl` returns the full DocumentDTO; routing's `JofotaraSendHandler` expects raw XML. Local fix applied; flag to him. |
| 3 | Vault / Ops config on dev | Ops | See table below — 20 rows including `ENABLED_COUNTRIES`, `SCHEMA_MAPPING_FILE_PATHS`, `JOFOTARA_*`, `countryRouterServiceMap` per env. |
| 4 | Real JoFotara sandbox smoke | — | No sandbox exists. Must wait for prod credentials at MAF go-live. |
| 5 | clear-sales PR for `incomeSourceSequence` + `deviceId` | Vashistha (or Aquib follow-up) | Local branch `local/jordan-iss-field` — coordinate with Aquib's NV-265 follow-up. |
| 6 | NV-266 follow-ups | Vashistha | S3 persistence of signed/submitted XML, Java validation rules (10K JOD threshold, sub-type consistency), unit tests for the validation rules, integration with Kushagra's routing impl post-merge. |

## Open spec questions (not blocking code, blocking correctness)

1. Retry backoff: PRD says 5s/30s/2min vs Avtax says 2s/5s/10s.
2. Auth HTTP code: PRD says 401 vs Avtax+SDK say 403 — handle both.
3. Special Sales tax shape: slides say no line tax, tech mapping has OTH scheme.
4. Buyer Name mandatory for exports? (Open queries #20 — NEW)
5. Exchange rate field for exports? (Open queries #22 — NEW)
6. Base Quantity field — keep or remove from schema?
7. Unit of measure other than `PCE` — untested.

## Vault Configuration Tracking (truncated; see `jordan_implementation_log.md` for full table)

| # | Item | Vault path (guess) | Status |
|---|---|---|---|
| 1 | `ENABLED_COUNTRIES` += `,JO` | `vault/einvoicing-core/{env}/ENABLED_COUNTRIES` | Needed on dev |
| 3 | `JO_JOFOTARA_ENCRYPTION_KEY` | `vault/einvoicing-core/{env}/JO_JOFOTARA_ENCRYPTION_KEY` | Not configured |
| 11 | `JOFOTARA_BASE_URL` | `vault/clear-routing/{env}/JOFOTARA_BASE_URL` | Not configured |
| 12 | `JOFOTARA_MOCK_ENABLED` | `vault/clear-routing/{env}/JOFOTARA_MOCK_ENABLED` | Not configured |
| 13 | `JOFOTARA_ENABLED` | `vault/clear-routing/{env}/JOFOTARA_ENABLED` | Not configured |
| 14 | `SCHEMA_MAPPING_FILE_PATHS` += `SchemaMapping/JO/SalesEinvoiceToJoFotaraXml.json` | env yml | Needed on all envs |
| 15 | `validationConfig` += JO entry | env yml | Strongly recommended pre-prod |
| 19 | E_INVOICING.SALES_INVOICE license per customer workspace | Licensing service DB | Per customer at onboarding |
| 20 | `countryRouterServiceMap` += `"JO":"JOFOTARA"` | `vault/clear-routing/{env}/COUNTRY_ROUTER_SERVICE_MAP` | Needed on all envs |

**First Ops ask (minimum to test on dev):** rows #1, #14, #11-13.

## Customers onboarded

- MAF — target onboarding before May 15, 2026.

## Recent in-flight activity (refreshed by `/v-country-brain`)

(Updated by `country-knowledge-curator`.)

Sources: `project_jordan_einvoicing.md` §11-12; `jordan_implementation_log.md` Sessions 1-4 + Vault Configuration Tracking table.
