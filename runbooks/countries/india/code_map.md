# India Code Map

Repos × files implementing India IRN/EWB. Append-only `Recent activity` section at the bottom.

## Repos

| Repo | Path | Role |
|---|---|---|
| `clr-irp-be` | `~/Desktop/clr-irp-be` | ClearTax IRP — IRN issuance, SLA monitoring, bulk operations. |
| `e-invoicing-be` | `~/Desktop/e-invoicing-be` | Broader India e-invoicing logic — NIC switcher (reverted), Redis EWB lock, Sentry, harvester migration. |
| `ingestion-overlord` | `~/Desktop/ingestion-overlord` | Excel/CSV upload, schema mappings, rule engines (Mitsuba). |

## clr-irp-be — recent significant work

| File area / PR | Purpose |
|---|---|
| `clr-irp-be#467` | 40% GST rate cutover (deployed Sep 22 2025). |
| `clr-irp-be#475/#476/#478` (CIRP-186/187/188) | IRP SLA Monitoring APIs — 6 endpoints, +764 LOC / 18 files. |
| `clr-irp-be#482` (NV-191) | Bulk `annualTurnover` for 26,063 GSTINs. InternalOnlyApi + slab mapper + dry-run + 3 CSV outputs. 26,062 / 1 / 0 result in <3 days. |
| CIRP-193 (RSP tobacco) | RSP field for tobacco HSN — cross-5-services cutover Feb 1 2026. Swiggy 3-hour pivot Jan 30 8:11 PM IST → demo-verified by 11:10 PM → FF flipped Feb 1 00:00. |

## e-invoicing-be — recent significant work

| File area / PR | Purpose |
|---|---|
| **`reconcile/ind-from-main` branch** (started 2026-03-20) | Reconcile e-invoicing-be `main` to create IND deployment candidate. |
| `e-invoicing-be#3670` (EINVI-1236) | NIC1 ↔ NIC2 auto switcher (merged Sep 29 2025) — **REVERTED post Nov 18-19 outage**. |
| `e-invoicing-be#3664` (EINVI-1243) | 40% GST rate cutover (Sep 2025). |
| `e-invoicing-be#3614, #3615` (EIOCJ-536, EINVI-1203) | Redis distributed lock for EWB. |
| `e-invoicing-be#3691` (EIOCJ-670) | H2 follow-up to EWB Redis lock. |
| `e-invoicing-be#3693/#3694/#3696` (EINVI-1260) | Sentry onboarding (IND + GCC). |
| `e-invoicing-be#3546` (EINVI-1852) | Filter-based harvester migration. |
| `e-invoicing-be#3626/#3639/#3640/#3642` | Devspace onboarding (self-initiated, +264 LOC). |
| `e-invoicing-be#3662` (EINVG-1521) | VAT in accounting currency (+511/-36, 13 comments). |
| `e-invoicing-be#3620` (EINVG-1692, EINVG-1877) | Device → Branch invoice mapping. |
| `e-invoicing-be#3583` (EINVG-1781) | Retry-failure after 15 retries. |
| `e-invoicing-be#3674` (Redis EWB lock) | **Closed-not-merged** — another dev shipped EINVI-1251. |

### `reconcile/ind-from-main` — what's done

- **Batch 1:** Workspace exclusion framework ported (5 new files + 45 annotations on 3 repo files).
- **Batch 2:** NIC2 auto-switching neutralized in `GenerationSourceAutoSwitch` — sources list, `getNicCredentialsType`, `getNextGenerationSource`, `isNic2SwitchingEnabledForCurrentWorkspace` all locked to NIC-only.
- All neutralization marked with `[IND-RECONCILE]` comments — `grep [IND-RECONCILE]` to find all neutralization points.
- CEWB rate limiting NOT ported (removed from main, controller already restructured).
- S3.copyObjects, Audit.INTERNAL, ProdDemo endpoints NOT ported (confirmed unused).

## ingestion-overlord — recent significant work

| File area / PR | Purpose |
|---|---|
| `ingestion-overlord#5008` (EINVI-1231) | Mitsuba auto-GST rule template (P0). |
| `ingestion-overlord#5104` | 40% GST rate cutover ingestion side. |
| `ingestion-overlord#4908, #4889` (EINVG-1692, EINVG-1877) | Device → Branch invoice mapping ingestion side. |
| `ingestion-overlord#5011` (EINVG-1895, EINVG-1906) | ZATCA SDK 3.4.2 / 3.4.3 (cross-country dependency, also touches India). |

## Build / config quirk

- `e-invoicing-be` build can't run locally due to Lombok 1.18.20 / JDK 17.0.14 incompatibility (pre-existing). Not blocking — CI handles build.

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_perf_review_fy26.md` §4 (H1 + H2 picks); `project_ind_reconciliation.md`.
