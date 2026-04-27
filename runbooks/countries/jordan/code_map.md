# Jordan Code Map

Repos × files implementing JoFotara as of Apr 2026. The Recent activity section is append-only and updated by `country-knowledge-curator`.

## Repos

| Repo | Path on Desktop | Role |
|---|---|---|
| `einvoicing-core` | `~/Desktop/einvoicing-core` | Country module + schema mapping + XSLT (NV-266, NV-267, NV-268). |
| `clear-routing` | `~/Desktop/clear-routing` | Vendor module `clear-jofotara/` + RouterServiceEnum.JOFOTARA (NV-273). |
| `clear-sales` | `~/Desktop/clear-sales` | Shared model `ClientCredentialSetting` (NV-265, NV-269 ISS field). |

## einvoicing-core (`~/Desktop/einvoicing-core`)

Branch in active dev: `feat/NV-266-jordan-einvoice-core`.

| File | Purpose |
|---|---|
| `pom.xml` | `<module>einvoice-jo</module>` line 29 |
| `application/pom.xml` | runtime dep on einvoice-jo |
| `application/src/main/resources/application-local.yml` | `JO` in `deployment.enabled-countries`; `SchemaMapping/JO/...` appended to `schema-registry.schemaMappingFilePaths` |
| `einvoice-jo/pom.xml` | module pom (synced 1.532.1; test deps for schema-registry + xmlunit-assertj3) |
| `einvoice-jo/.../JoConstants.java` | API/status/S3 constants |
| `einvoice-jo/.../EInvoiceJoGovtActionService.java` | Throws on cancel/fetch (negative APIs); overrides `validateTaxpayerCredential` to skip gov verify |
| `einvoice-jo/.../EInvoiceJoSalesCtActionService.java` | Validates seller TIN matches taxpayer |
| `einvoice-jo/.../JoWorkflowInitiatorService.java` | No-ops async (sync flow only) |
| `einvoice-jo/.../dto/JoFotaraRequestDTO.java` | base64 invoice wrapper |
| `einvoice-jo/.../dto/JoFotaraResponseDTO.java` | Format A + Format B response with `getEffective*` helpers |
| `einvoice-interface/.../EInvoiceDefaultSalesGenerationService.java` | Add `JO` to `@ConditionalOnCountry` |
| `einvoice-interface/.../SchemaMapping/JO/SalesEinvoiceToJoFotaraXml.json` | JSON → UBL mapping (~320 lines, single file for 388 + 381) |
| `einvoice-interface/.../validation/JO/JO-validation.xslt` | ~20 BR-JO-### rules, MVP |
| `einvoice-interface/.../JofotaraRoutingServiceImpl.java` | Kushagra's PR #1323 — note local fix to extract `getDocument()` Base64 (contract bug, flag to him) |
| `einvoice-models/.../utils/ContextFieldName.java` | `JOFOTARA_CLIENT_ID` / `JOFOTARA_CLIENT_SECRET` / `JOFOTARA_AUTHENTICATOR_TYPE` |
| `einvoice-db-interactions/.../JO/EinvoiceFieldWithDBPath.json` | DB field mapping for UI |
| `einvoice-db-interactions/.../JO/EinvoiceFieldWithDbOptions.json` | UI labels → DB values |

## clear-routing (`~/Desktop/clear-routing`)

| File / Module | Purpose |
|---|---|
| `clear-jofotara/` | Vendor module (Kushagra's PR #134, ~2161 lines). Mock client, retry, send handler. |
| `clear-router-application/src/main/resources/application-local.yml` | `routing.countryRouterServiceMap` must include `"JO":"JOFOTARA"`. Locally added; mirror to env yamls per Vault row #20. |
| `RoutingService` enum | `JOFOTARA` value added (NV-273). |
| `Region` enum | `MEA` for Jordan. |

## clear-sales (`~/Desktop/clear-sales`)

| File | Purpose |
|---|---|
| `einvoice-global/.../models/settings/ClientCredentialSetting.java` | Add `incomeSourceSequence` + `deviceId` plaintext fields (NV-265 / NV-269). Branch `local/jordan-iss-field` based on `origin/hotfix/1.147.52`. PR not yet opened. |
| `einvoice-global/.../models/PartyIdentificationScheme.java` | `JO_NIN` added by Aquib's PR #392. |

## Test fixtures (einvoicing-core)

`einvoice-jo/src/test/resources/jo/inputs/` — 9 canonical fixtures covering 388/381, sub-types 011/012/021/022, buyer schemes TN/NIN/PN/None, tax categories S/Z/O, doc + line discounts, single + multi-line. Used by:
- `SalesToJoFotaraMapperTest.java` (50 tests)
- `SalesToJoFotaraEndToEndXmlTest.java` (93 tests)
- `EInvoiceJoGovtActionServiceTest.java` (10 tests)

153 tests total, all green as of Session 3.

## PRs (open / referenced)

| PR | Repo | Owner | NV ticket | Status |
|---|---|---|---|---|
| #1325 | einvoicing-core | Vashistha | NV-266 | Open |
| #1323 | einvoicing-core | Kushagra | NV-273 (routing impl) | Open |
| #134 | clear-routing | Kushagra | NV-273 (vendor module) | Open |
| #1313 | einvoicing-core | Aquib | NV-265 (Jordan country support in Pint + JO enums) | Open |
| #392 | clear-sales | Aquib | NV-265 (JO_NIN scheme) | Open |

## Vault / config items pending

See `live_state.md` "Vault Configuration Tracking" — 20 rows including `ENABLED_COUNTRIES`, `SCHEMA_MAPPING_FILE_PATHS`, `JOFOTARA_BASE_URL`, `countryRouterServiceMap`, licensing provisioning.

## Recent activity

(Append-only, populated by `country-knowledge-curator` from `/v-country-brain` runs.)

Sources: `project_jordan_einvoicing.md` §8-10; `jordan_implementation_log.md` Sessions 1-4.
