# UAE Code Map

Repos × files implementing UAE/FTA as of Apr 2026.

## Repos

| Repo | Path | Role |
|---|---|---|
| `einvoicing-core` | `~/Desktop/einvoicing-core` | Country module `einvoice-ae/`. Validation rules pattern (9 classes). |
| `clear-routing` | `~/Desktop/clear-routing` | Vendor module `clear-ae-fta/`. Dual OAuth2 + Redis. |
| `einvoicing-integrations` | `~/Desktop/einvoicing-integrations` | Upload endpoint for UAE customers. |
| `pdfgenerator` | `~/Desktop/pdfgenerator` | Templates 5/6/8/9 with Arabic strings via Kramer. |
| `clear-peppol-ap` | `~/Desktop/clear-peppol-ap` | Indirect — Peppol-style 4-corner architecture; UAE participant. |
| `clear-sales` | `~/Desktop/clear-sales` | Shared models. |

## einvoicing-core/einvoice-ae

| Area | Notes |
|---|---|
| Validation rules (9 classes) | `BuyerValidationRules`, `SellerValidationRules`, `TaxTotalsValidationRules`, `DocumentTotalsValidationRules`, `LineItemValidationRules`, `HeaderValidationRules`, `AllowanceChargeValidationRules`, `PaymentValidationRules`, `CreditNoteValidationRules`. All built on `ValidationContext` + `ValidationError` + `ValidationRule` interface. Reference for new MEA modules. |
| `einvoicing-core#888` (Tabby B2B/B2C) | 49 files, 9 validation rule classes, 92.77% coverage. Live Dec 16, 2025. |
| `einvoicing-core#1167` (NV-173 MEA Re-routing) | P0 cross-country routing shift. |
| `einvoicing-core#941` (Arabic translation service) | 25 review comments. Cross-MEA. |
| `einvoicing-core#1282` (TaxCategory ordering fix) | + 18-test regression guard. |

## clear-routing/clear-ae-fta

| Property | Value |
|---|---|
| Auth | Dual OAuth2 (Redis) |
| Actions | `GET_TAXPAYER_DETAILS`, `SUBMIT_TAXPAYER_DETAILS` |
| Routing service enum | `FTA` |
| Region | `UAE` |

## einvoicing-integrations

| PR | Purpose |
|---|---|
| `einvoicing-integrations#493` | UAE integration upload endpoint. |

## NV-173 11-PR post-launch sweep

PRs touching MEA re-routing infrastructure:

- `einvoicing-core` #1167, #1258, #1254, #1072, #1099, #1069, #1026, #1033, #1003, #1047
- `cloud-init#6662`
- `ct-app-config#8098`
- `clear-peppol-ap#165`
- `e-invoicing-be#3716, #3714`

## Translation service (cross-MEA)

- `einvoicing-core#941` — service.
- `pdfgenerator#461` — PDF templates 5/6/8/9 + Kramer integration.

## Customers

- **Tabby** — first major B2C customer, live Dec 16 2025. Internal product line.

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_perf_review_fy26.md` §4 H2 picks 1, 2, 7, 8, 10; `platform_architecture.md` §1, §4.

<!-- Discovery 2026-04-28 from /v-country-brain session re: Tabby VAT rate prints 500 instead of 5 -->
## Print pipeline (cross-cutting, critical for UAE)

UAE invoices use the `EINVOICE_GLOBAL` print payload type (not `GCC_EINVOICE`) since Nov 2025 — see `pdfgenerator` PR #414 / commit `a5f8afc7 Changes for UAE einvoice schema`. The print path involves a country-aware percent-format normalizer:

| File | Role |
|---|---|
| `einvoicing-core/einvoice-interface/src/main/java/com/clear/einvoicing/services/impl/EInvoicePrintServiceImpl.java:71-187` | Sets `isPercentInWholeNumberFormat` flag from the `print-service.wholeNumberPercentCountryCodes` Spring property. Also defines `COUNTRIES_WITH_CUSTOM_PRINT_SCHEMA = Set.of("AE")`. |
| `einvoicing-core/einvoice-interface/src/main/java/com/clear/einvoicing/mappers/PrintSchemaMapper.java:27-42` | `convertPercentForPrint(percent, isPercentInWholeNumberFormat)` — divides by 100 when flag=true (e.g. `("5","true")` → `"0.05"`). |
| `einvoicing-core/einvoice-interface/src/main/resources/SchemaMapping/AE/einvoiceDBToPrintRequestMappingAE.json` | UAE-specific print schema mapping. References `convertPercentForPrint` in 7+ places (line 514 etc.). |
| `pdfgenerator/src/main/kotlin/com/procureli/templates/extensions/Extenstions.kt:103-155` | Payload-type dispatch — routes `EINVOICE_GLOBAL` to `EInvoiceGlobalDocumentData`. |
| `pdfgenerator/src/main/kotlin/com/procureli/templates/models/einvoiceGlobal/EInvoiceGlobalDocumentData.kt:222, 548, 570` | Three `updatePercent()` methods that multiply `percent × 100`. By design — expects decimal fraction input (0.05) from einvoicing-core, renders as 5. |

**Flow:** einvoicing-core sends `5 → 0.05` (when AE in WHOLE_NUMBER_PERCENT_COUNTRY_CODES) → pdfgenerator multiplies `0.05 × 100 → 5` for display. The system is internally consistent only when the env config is correct.

## Multi-module Spring config (einvoicing-core)

For any `@Value` flag in einvoicing-core, three modules can have divergent `application-prod.yml` defaults:

| Module | Path | Role |
|---|---|---|
| `application/` | `application/src/main/resources/application-prod.yml` | Sync REST API server (port 21048). Path: `POST /v1/einvoice/print`. |
| `einvoicing-workflow-consumer/` | `einvoicing-workflow-consumer/src/main/resources/application-prod.yml` | Kafka/SQS bulk consumer (BulkApi pattern). |
| `einvoicing-temporal-worker/` | `einvoicing-temporal-worker/src/main/resources/application-prod.yml` | Temporal workflow activities. |

**Rule:** when investigating any `@Value`-bound config in einvoicing-core, diff all 3 `application-prod.yml` files. Real prod values come from Vault env-var overrides — YAML defaults are fallback only.
