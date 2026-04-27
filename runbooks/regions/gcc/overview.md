# GCC Region — Cross-Country On-Call

**Countries:** Saudi Arabia (`SA`), United Arab Emirates (`AE`), Bahrain (`BH`), Oman (`OM`), Qatar (`QA`), Kuwait (`KW`)
**Status:** On-call driven (active code is mostly UAE + KSA, but on-call comes for any GCC country)
**Repos:** `einvoicing-core`, `e-invoicing-be` (cross-cutting)

## What this region is

GCC = Gulf Cooperation Council. Six countries, all with their own e-invoicing posture but sharing routing infrastructure (Region enum `MEA` in clear-routing, with country-specific vendor modules). Active e-invoicing code today is mostly UAE (`einvoice-ae`) and KSA (ZATCA SDK 3.4.2/3.4.3). On-call rotation covers all 6.

## Why this region exists separately

The user's on-call duties span the GCC bloc, but the rich technical content lives in `runbooks/countries/uae/`, `runbooks/countries/ksa/` (and future `bahrain/`, `oman/`, `qatar/`, `kuwait/` once they get rich runbooks). This region runbook is the **on-call-first** view — what does the on-call engineer need to know about all six together?

## Cross-country invariants

- **Routing region:** `MEA` (used in `clear-routing` for all 6).
- **L3 channel:** `#einvoice_mea_l3_support` (`C0AB8EAH9A6`).
- **Sentry tag:** `country=<2-letter>`.
- **MEA Re-routing (NV-173)** — touched all GCC countries; live Mar 26 2026.

## Per-country quick-status

| Country | Code | Status | Primary repos | Key channels |
|---|---|---|---|---|
| UAE | AE | Live (Tabby B2C live Dec 16 2025) | `einvoice-ae`, `clear-ae-fta` | See `runbooks/countries/uae/` |
| KSA | SA | Live (ZATCA SDK 3.4.2/3.4.3 H1 2025; Sev1 Apr 27 2026) | `einvoicing-core`, `ingestion-overlord` | `group_dms.ksa_deploy` (`C0ANDUZ5893`) |
| Bahrain | BH | TODO | TODO | TODO |
| Oman | OM | TODO — referenced in `#mea_jordan_egypt_oman_discovery` (`C0ABA7RC1QD`) | TODO | TODO |
| Qatar | QA | TODO | TODO | TODO |
| Kuwait | KW | TODO | TODO | TODO |

## Slack & people

See `people.md`. Primary channels:
- `#einvoice_mea_l3_support` (`C0AB8EAH9A6`) — MEA L3, primary signal.
- `#einvoicing_global_platform` (`C08MX0F3F17`) — platform discussions.
- `#e-invoice-tech-internal` (`C09AC9XKTC5`) — tech architectural.
- KSA deploy DM: `C0ANDUZ5893`.
- Jordan/MEA discovery (Egypt, Oman): `C0ABA7RC1QD`.

## Status today (Apr 2026)

- UAE: live + mature (see country runbook).
- KSA: live; **Sev1 Apr 27 2026** referenced in countries.yaml (Redis/licensing) — see `runbook.md`.
- BH/OM/QA/KW: limited memory; expand once user provides material.

## Cross-country recent work

- **NV-173 MEA Re-routing** — affected all 6 GCC countries; live Mar 26 2026.
- **Sentry onboarding (IND + GCC)** — EINVI-1260 (e-invoicing-be#3693/#3694/#3696).
- **GCC Outage RCF** by Shashank Jannu (H2; not user-owned).

Sources: `project_perf_review_fy26.md` §4 H2 (NV-173, Sentry); `data/countries.yaml` (regions.gcc); `platform_architecture.md` §13.
