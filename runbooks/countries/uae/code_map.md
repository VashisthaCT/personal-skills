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
