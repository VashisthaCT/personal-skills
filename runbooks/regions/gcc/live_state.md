# GCC — Live State

**As of memory snapshot Apr 2026.**

## Per-country status

| Country | Code | Status | Latest milestone |
|---|---|---|---|
| UAE | AE | Live | Tabby B2C live Dec 16 2025; MEA Re-routing live Mar 26 2026; TaxCategory ordering fix live H2 |
| KSA | SA | Live | ZATCA SDK 3.4.2 / 3.4.3 live H1 2025; **Sev1 Apr 27 2026** (Redis/licensing per countries.yaml note) |
| Bahrain | BH | TODO | TODO |
| Oman | OM | TODO | TODO |
| Qatar | QA | TODO | TODO |
| Kuwait | KW | TODO | TODO |

## Cross-region active workstreams

- **MEA Re-routing post-launch** — Mar 26 2026 launch was clean; 11 PRs of follow-up complete.
- **Translation Service** — live Jan 19 2026; cross-MEA.
- **Sentry observability** — IND + GCC tagged; EINVI-1260 PRs landed H2.
- **EINVG-1983** (KSA postal-code, cross-MEA postal handling) — open; filed via Mar 19 thread with Rahul Meena.

## Recent SEV1 / outage history

- **Apr 27 2026 — KSA Sev1** (Redis / licensing) — reference in `data/countries.yaml`. TODO capture full RCA reference.
- **GCC Outage RCF** (H2) — author Shashank Jannu (NOT user-owned). TODO link Drive doc.
- **Sev1 RCF Dec 10** — author Nichelle Aranha (NOT user-owned).
- **Eicher RCA** — author Vikas Jethnani (India-side; referenced for cross-region context).

## Known issues

1. **MEA XSLT drift** — shared XSLTs accumulate per-country branches. Architectural line held Mar 24 (#e-invoice-tech-internal): prefer per-country XSLT subdirectory over branching the shared XSLT.
2. **KSA postal-code variance** — countries.yaml hints at country-specific postal handling. EINVG-1983 is the consolidating ticket.
3. **Redis/licensing** — KSA Sev1 Apr 27 2026 suggests Redis-licensing interaction needs hardening across MEA.
4. **Arabic string staleness** — translation service may emit stale strings if Kramer templates aren't refreshed in sync.

## Customers onboarded (cross-GCC)

- Tabby (UAE, B2C, Dec 16 2025).
- (KSA customers and others — TODO list from data/customers.yaml + memory.)

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_perf_review_fy26.md` §4 H2 picks 1, 2, 7; `data/countries.yaml`; `platform_architecture.md` §13.
