# GCC Code Map

Repos × files implementing GCC cross-cutting work. Per-country implementation lives in country runbooks (`runbooks/countries/uae/`, `runbooks/countries/ksa/`, etc.).

## Repos

| Repo | Path | Role |
|---|---|---|
| `einvoicing-core` | `~/Desktop/einvoicing-core` | Country modules (`einvoice-ae` rich; KSA in shared paths). |
| `clear-routing` | `~/Desktop/clear-routing` | Vendor modules `clear-ae-fta/`, ZATCA wiring. |
| `e-invoicing-be` | `~/Desktop/e-invoicing-be` | Sentry onboarding (IND + GCC). |
| `ingestion-overlord` | `~/Desktop/ingestion-overlord` | KSA ZATCA SDK touch points. |
| `pdfgenerator` | `~/Desktop/pdfgenerator` | Arabic translation templates 5/6/8/9. |
| `cloud-init`, `ct-app-config` | (infra repos) | NV-173 MEA Re-routing config. |

## Cross-country PRs

### NV-173 MEA Re-routing — 11 PRs

- `einvoicing-core` #1167 (lead), #1258, #1254, #1072, #1099, #1069, #1026, #1033, #1003, #1047
- `cloud-init#6662`
- `ct-app-config#8098`
- `clear-peppol-ap#165`
- `e-invoicing-be#3716, #3714`

Live Mar 26, 2026. P0.

### Sentry onboarding (IND + GCC)

- EINVI-1260
- `e-invoicing-be#3693, #3694, #3696`

### Translation Service (cross-MEA, includes GCC)

- `einvoicing-core#941`
- `pdfgenerator#461`
- Kramer templates 5/6/8/9 (template files in pdfgenerator)

## Routing module references

- `clear-routing/clear-ae-fta/` — UAE FTA dual OAuth2, Redis tokens.
- ZATCA wiring (KSA) — TODO capture exact module path.
- Future BH/OM/QA/KW vendor modules: TBD.

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_perf_review_fy26.md` §4 H2 picks 2, 6, 7; `platform_architecture.md` §4.
