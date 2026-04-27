# India — Law / Spec Changes

Append-only log. Newest at top. Curator agent owns appends.

## 2026-02-01 — Tobacco RSP (Retail Sale Price) cutover

- Source: CIRP-193; thread root https://cleartaxtech.slack.com/archives/C04U10T2DAN/p1769575265650159
- What changed: GST circular requires RSP field on tobacco HSN invoices. Cross-5-services impact (clr-irp-be + e-invoicing-be + ingestion-overlord + + 2 more).
- Impact: Pivot moment Jan 30 8:11 PM IST → demo-verified by 11:10 PM → FF flipped Feb 1 00:00. Swiggy 3-hour pivot.
- Status: actioned

## 2025-09-22 — 40% GST rate slab introduced

- Source: GST Council notification.
- What changed: New 40% rate slab introduced. HSN-level rate updates required across `e-invoicing-be`, `ingestion-overlord`, and `clr-irp-be`.
- Impact: 2-day dev sprint Sept 15-17 2025; deployed Sept 22 2025. PRs e-invoicing-be#3664, ingestion-overlord#5104, clr-irp-be#467. Ticket EINVI-1243.
- Status: actioned

## 2025-XX-XX — Mitsuba auto-GST rule template

- Source: Customer (Mitsuba) requirement.
- What changed: Customer kept providing wrong GST rates in their feed. Decision: GST-rate derivation is a ClearTax-side problem, not a customer-side problem. Built rule template to auto-derive.
- Impact: Ingestion-overlord rule engine extended. PR ingestion-overlord#5008. Ticket EINVI-1231 (P0).
- Status: actioned

---

This log is bootstrapped from project memory. Future entries should come from `/v-law-watch india` runs scraping docs.ewaybillgst.gov.in + GSTN circulars + CBIC notifications.

TODO: backfill historical entries — IRN turnover threshold reductions over the years, EWB introduction milestones, IRP onboarding deadlines.

Sources: `project_perf_review_fy26.md` §4 (40% cutover, RSP, Mitsuba).
