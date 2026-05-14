---
tags: [runbooks, index, catalog]
summary: Top-level catalog of every runbook entry. Start here — read this before drilling into a specific country/region.
last_updated: 2026-05-12
related: [purpose.md, log.md]
---

# Runbooks — index

Every entry the LLM should know about. Updated by skills that add new entries (`/v-country-onboard`, `/v-country-brain` on first discovery).

For *why* this directory exists and how to adopt the pattern, see [`purpose.md`](purpose.md).
For *what happened when*, see [`log.md`](log.md).

## Countries (8)

| ID | Code | Region | Status | Seed | Path | Summary |
|---|---|---|---|---|---|---|
| jordan | JO | MEA | dev-complete | rich | [`countries/jordan/`](countries/jordan/) | JoFotara clearance model; MAF go-live May 15 2026 |
| india | IN | SEA-IND | live | rich | [`countries/india/`](countries/india/) | NIC IRN + EWB; on-call heavy; FTP migration in progress |
| uae | AE | MEA | live | rich | [`countries/uae/`](countries/uae/) | FTA; Tabby B2B/B2C live Dec 16 2025; MEA re-routing live Mar 26 2026 |
| ksa | SA | MEA | live | stub | [`countries/ksa/`](countries/ksa/) | ZATCA SDK 3.4.2/3.4.3; Sev1 Apr 27 2026 (Redis/licensing) |
| malaysia | MY | SEA | live | stub | [`countries/malaysia/`](countries/malaysia/) | LHDN |
| belgium | BE | EU | live | stub | [`countries/belgium/`](countries/belgium/) | FOD Financiën + Peppol BE |
| france | FR | EU | accreditation-track | stub | [`countries/france/`](countries/france/) | PPF; CEO all-hands milestone Apr 24 2026 |
| poland | PL | EU | live | stub | [`countries/poland/`](countries/poland/) | KSeF |

## Regions (2)

| ID | Status | Seed | Path | Summary |
|---|---|---|---|---|
| peppol | live | rich | [`regions/peppol/`](regions/peppol/) | Peppol network; EUSR/TSR reporting live; ClearTax AP ID POP000602 |
| gcc | oncall-driven | rich | [`regions/gcc/`](regions/gcc/) | UAE + KSA + BH + OM + QA + KW; cross-country oncall |

## Files per entry

Each entry contains 7-9 markdown files (see [`purpose.md`](purpose.md) § Structure). Highest-leverage to read first:

| File | Read when |
|---|---|
| `overview.md` | New to this country — what it is, our delivery model |
| `runbook.md` | Oncall / debug — causes, decision tree, error codes, escalation |
| `code_map.md` | Need to know where in `~/Desktop/<repo>/` the code lives |
| `api_contract.md` | API failure / regulator integration question |
| `ubl_structure.md` | Mapping / schema / validation question (countries with UBL) |
| `credentials.md` | Auth failure / per-customer credential question |
| `live_state.md` | "Is this live? Who's onboarded? What's the latest customer issue?" |
| `law_changes.md` | Regulatory update / spec drift question |
| `people.md` | Who to ask — regulator contact, consultant, internal devs |

## Session logs

Every `/v-country-brain` invocation writes a session log to `<entry>/_sessions/<YYYY-MM-DD-HHMMSS>.md`. Browse those for "what was being debugged when". Each has structured frontmatter (date, country, severity, customer, escalated, query_category, resolution) so they're queryable.

## Next steps for new contributors

- **Add a new country**: `/v-country-onboard init <cc>` then `/v-country-onboard parse-mapping`. Updates this index automatically.
- **Promote a stub to rich**: run `/v-country-brain <cc>` repeatedly; discoveries accumulate via the Y/n loop.
- **Lint health**: `/v-runbook lint <cc>` or `lint all` — finds stale claims, orphans, missing cross-refs.
