# GCC — Cross-Country Spec Notes

GCC has no single regulator or single spec — each country has its own. This file pulls together the cross-cutting spec-level concerns the on-call engineer encounters.

## Active per-country regulator + protocol summary

| Country | Regulator | Protocol / Format |
|---|---|---|
| UAE | FTA | UBL via `clear-ae-fta` (dual OAuth2, Redis-cached) |
| KSA | ZATCA | ZATCA SDK 3.4.2 / 3.4.3 (signing + e-invoice generation) |
| Bahrain | TBD — TODO capture | TODO |
| Oman | TBD — TODO capture (touched in `#mea_jordan_egypt_oman_discovery`) | TODO |
| Qatar | TBD — TODO capture | TODO |
| Kuwait | TBD — TODO capture | TODO |

## Cross-region routing

- **`Region` enum:** `MEA` (in `clear-routing`).
- **`RoutingService` enum:** UAE = `FTA`, KSA = `ZATCA`. Others TBD as they go live.
- **Region-level routing facade:** `clear-routing` `RoutingFactory.getClearRouterService(routingService, countryCode)` dispatches per-country.

## Translation / Arabic strings (cross-MEA)

- Translation service (einvoicing-core#941) is cross-MEA, used by UAE, KSA, and any country that emits Arabic strings.
- pdfgenerator templates 5/6/8/9 route through Kramer for Arabic content.

## Validation rules pattern

UAE's `einvoice-ae` validation pattern (9 classes built on `ValidationContext` + `ValidationError` + `ValidationRule`) is the GCC reference. Any new GCC country should adopt this pattern.

## Sentry observability

- EINVI-1260 added Sentry for IND + GCC. PRs e-invoicing-be#3693/#3694/#3696.
- Sentry tag `country=<2-letter>` filters per-country.

## Cross-country specific spec items

### KSA postal-code → MEA-wide postal handling

- Mar 19 thread with Rahul Meena (PM, KSA): https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1773911560622319
- Filed as **EINVG-1983**.
- Trigger: country-conditional postal code validation. Memory note: "GST-rate derivation is a ClearTax-side problem, not a customer-side problem" — same philosophy applies to postal code derivation.

## TODO sections

- BH/OM/QA/KW regulator portals + spec versions.
- Per-country error code references (currently spread across country runbooks).
- Cross-region currency / TIN handling.

Sources: `project_perf_review_fy26.md` §4 H2 (KSA postal, NV-173, Sentry); §6 P&B; `platform_architecture.md` §4.
