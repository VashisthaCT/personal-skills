# KSA (SA) — ZATCA E-Invoicing

**Code:** SA | **Region:** MEA (GCC) | **Status:** Live
**Regulator:** ZATCA (Zakat, Tax and Customs Authority, Saudi Arabia)
**Repos:** `einvoicing-core`, `ingestion-overlord`, `clear-routing`

## Summary

KSA operates a ZATCA-mandated e-invoicing scheme. ClearTax integrates via the ZATCA SDK. Latest tracked SDK versions: **3.4.2** and **3.4.3** (live H1 2025; PRs EINVG-1895, EINVG-1906, ingestion-overlord#5011 + e-invoicing-be#3630, #3649). A **Sev1 on Apr 27, 2026** was referenced in `data/countries.yaml` — Redis / licensing related; full RCA TODO.

## Key repos / files

- `einvoicing-core` (cross-cutting; ZATCA SDK touch points).
- `ingestion-overlord` (PR #5011 — SDK upgrade).
- `e-invoicing-be` (PRs #3630, #3649 — SDK 3.4.2 + 3.4.3 wiring).
- `clear-routing` (vendor wiring — TODO module name).

## Slack & people

- KSA deploy DM: `C0ANDUZ5893`.
- L3: `#einvoice_mea_l3_support` (`C0AB8EAH9A6`).
- PM: Rahul Meena (`U08R0HS205A`).

## TODO sections

- `api_contract.md` — ZATCA endpoints, auth, error codes.
- `ubl_structure.md` — ZATCA UBL schema and validation rules.
- `credentials.md` — credential model for ZATCA SDK.
- `code_map.md` — full repo × file map.
- `people.md` — ZATCA regulator contacts + internal team.
- `live_state.md` — go-live status, customers, Sev1 history (capture Apr 27 2026 RCA).
- `law_changes.md` — ZATCA notification log.
- `runbook.md` — common errors and Sev1 debug paths.

Sources: `project_perf_review_fy26.md` §4 H1 pick 2 (ZATCA SDK 3.4.2/3.4.3); `data/countries.yaml`.
