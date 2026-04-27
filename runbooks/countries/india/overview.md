# India (IN) — IRP / EWB / GST E-Invoicing

**Code:** IN | **Region:** SEA-IND | **Status:** Live (long-running)
**Regulators:** GSTN (e-invoicing portal), NIC (IRP), CBIC (notifications)
**Repos:** `e-invoicing-be`, `clr-irp-be`, `ingestion-overlord` (also touches `einvoicing-temporal-core`, `clear-data-browser-be`)

## What India is

India operates two interlocking e-invoicing systems:

1. **IRN (Invoice Reference Number)** — issued by NIC's IRP for B2B invoices > ₹5 Cr aggregate turnover.
2. **EWB (E-Way Bill)** — required for goods movement; can be generated standalone or in conjunction with IRN.

Both have been live for years. ClearTax operates as an IRP (IRN issuance) and as an integrator for EWB.

## Architecture footprint

- **`clr-irp-be`** — ClearTax's IRP (Invoice Registration Portal) backend. Handles IRN generation, SLA monitoring, bulk operations like `annualTurnover` updates for 26K+ GSTINs.
- **`e-invoicing-be`** — broader India e-invoicing logic, including the NIC1 ↔ NIC2 switcher (now reverted), Redis distributed locking for EWB, Sentry onboarding, harvester migration.
- **`ingestion-overlord`** — Excel/CSV upload pipeline, schema mappings for India tenants, rule engines (Mitsuba auto-GST templates).

## Key recent work (FY26)

### H1 (Apr-Sep 2025)

- **NIC1 ↔ NIC2 auto switcher** (EINVI-1236, e-invoicing-be#3670, merged Sep 29 2025). Shipped, then a Redis-flag bug caused the **Nov 18-19 outage** (10h25m, 190 workspaces, 51,669 failed EWBs, 139,062 call failures). Code was later **reverted**.
- **40% GST rate cutover** (EINVI-1243, e-invoicing-be#3664, ingestion-overlord#5104, clr-irp-be#467) — 2-day dev Sep 15-17, deployed Sep 22.
- **Redis distributed lock for EWB** (EIOCJ-536, EINVI-1203, e-invoicing-be#3614, #3615) — H2 follow-up was EIOCJ-670 / #3691.
- **Mitsuba auto-GST rule template** (EINVI-1231, ingestion-overlord#5008, P0).
- **Filter-based harvester migration** (EINVI-1852, e-invoicing-be#3546, clear-data-harvester#724).
- **Devspace onboarding self-initiated** — e-invoicing-be#3626/#3639/#3640/#3642.

### H2 (Oct 2025-Mar 2026)

- **NIC RCF authored Nov-Dec 2025** for the Nov 18-19 outage — see `runbook.md`. Reviewed by senior leadership; action items SEV1BUGS-121, SEV1BUGS-122.
- **IRP SLA Monitoring APIs** (CIRP-186/187/188, clr-irp-be#475/#476/#478) — 6 endpoints, +764 LOC / 18 files.
- **NV-191 — Bulk annualTurnover for 26,063 GSTINs** (clr-irp-be#482) — 26,062 / 1 / 0 in <3 days.
- **Sentry onboarding (IND + GCC)** (EINVI-1260, e-invoicing-be#3693/#3694/#3696).
- **RSP tobacco HSN cross-5-services** (CIRP-193) — Feb 1 cutover, Swiggy 3-hour pivot Jan 30 8:11 PM IST.
- **IND reconciliation from main** — branch `reconcile/ind-from-main` started 2026-03-20. Ongoing batches; NIC2 auto-switcher neutralized, workspace exclusion framework ported. See `code_map.md`.

## Slack & people

- **L3 channel:** `#einvoice-l3-support` (`C055ABMAVCL`).
- **India + MEA mixed:** `#einvoice_india_mea` (`C0ADWHJ2V9S`).
- **FTP migration:** `#ftp-einvoice-india` (`C0APQH50274`).
- **QA:** `#einv-qa` (`C04AKPP1RL4`).

## Status today (Apr 2026)

- Live; on-call heavy.
- IND reconciliation from main is in progress — `reconcile/ind-from-main` branch.
- FTP einvoice migration to global SFTP workflow (4-5 week task) — Febin's direction is einvoicing-integrations as orchestrator with strategy pattern. Channel `#ftp-einvoice-india`.
- NIC switcher remains reverted — single-NIC mode locked in.

Sources: `project_perf_review_fy26.md` §4 H1+H2; `project_ind_reconciliation.md`; `project_ftp_einvoice_migration.md`.
