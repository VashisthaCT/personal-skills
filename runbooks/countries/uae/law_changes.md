# UAE — Law / Spec Changes

Append-only log. Newest at top.

## 2026-03-XX — KSA postal-code triggers cross-MEA postal handling discussion

- Source: Mar 19 thread #einvoice-l3-support (https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1773911560622319) with Rahul Meena (PM).
- What changed: Discussion identified need for country-conditional postal-code handling. UAE has its own postal nuances vs KSA.
- Impact: Filed EINVG-1983 (cross-MEA postal handling).
- Status: ticketed

## 2026-01-XX — Arabic translation service deploy

- Source: Jan 12 design thread (#einvoicing_global_pr, 22 replies); Jan 19 deploy thread (#einv-devs, 90 replies).
- What changed: Cross-MEA Arabic translation service for PDF generation. UAE templates 5/6/8/9 routed through Kramer.
- Impact: einvoicing-core#941 + pdfgenerator#461 + Kramer template updates + MEA QA passes.
- Status: actioned

## 2025-12-XX — Tabby B2B/B2C launch (UAE B2C precedent)

- Source: Dec 2 2025 kickoff thread (#einvoicing_global_platform).
- What changed: First major B2C customer (Tabby) live Dec 16, 2025. Schema and validation paths for B2C documented in einvoicing-core#888 (49 files, 9 validation rule classes, 92.77% coverage).
- Impact: Sets precedent for future B2C customers in UAE.
- Status: actioned

## 2025-XX-XX — UAE TaxCategory ordering fix

- Source: einvoicing-core#1282.
- What changed: TaxCategory element ordering within TaxSubtotal corrected. 18 regression tests added to guard order.
- Impact: TODO — capture exact ordering rule from PR diff.
- Status: actioned

---

This log is bootstrapped from project memory. Future entries should come from `/v-law-watch uae` runs scraping the FTA portal.

TODO: Capture FTA portal URL + scrape strategy.

Sources: `project_perf_review_fy26.md` §4 H2 picks 7, 10, §6 P&B (KSA postal); §9 Slack permalinks.
