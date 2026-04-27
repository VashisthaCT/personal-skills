# Jordan — Law / Spec Changes

Append-only log of regulatory and spec deltas. Newest at top. Curator agent owns appends.

## 2026-04-13 — PRD revision (Apr 13 version)

- Source: `~/Downloads/Jordan eInvoicing_ 15th May.docx` (re-exported by user)
- What changed: Confirmed retry backoff 5s/30s/2min (PRD §6.2); confirmed auth = 401 (PRD §3A.5) — though Avtax/SDK still report 403; locked sub-type list to 8 codes (no 2xx Development Area / 3xx Odoo); confirmed Income Source Sequence is in XML body, NOT a header.
- Impact: TODO — reconcile retry & auth-code conflict in code; add to discussion with Avtax for authoritative answer.
- Status: noted

## 2026-04-15 — Avtax tech sheet update (Open Queries tab)

- Source: `~/Downloads/Jordan Einvoicing Explanation.xlsx` (12 sheets; Open Queries + Explanation Document + Enums)
- What changed: Multiple new open queries — Buyer Name for Exports (#20), Exchange Rate for Exports (#22), Base Quantity (keep/remove), Unit of Measure other than `PCE` (untested), Special Sales line tax shape ("to be tested"), document vs line allowance ("Avtax seemed doubtful").
- Impact: TODO — track answers as they come in; impacts XSLT validation rules and schema mapping.
- Status: noted

## 2026-04-16 — RoutingService enum naming locked

- Source: Group DM `C0ASEKS03K8`, Apr 15 (Ayush confirmed).
- What changed: Routing enum value finalized as `JOFOTARA`. Region = `MEA`. Initial channel discussion considered `JOFATORA` (typo).
- Impact: Code uses `RouterServiceEnum.JOFOTARA` — Kushagra's PR #1323. No further action.
- Status: actioned-in-NV-273

## 2026-04-17 — Buyer schemeID convention clarified

- Source: Avtax+ClearTax enum sheet.
- What changed: UBL schemeID values are `TN` / `NIN` / `PN`. ClearTax internal API code uses `TIN` (legacy). Earlier memory said "use TN" for the XML emission; PHP SDK said "TIN"; the enum sheet clarifies ClearTax stores `TIN` internally but emits `TN` in XML.
- Impact: Mapping must convert internal `TIN` → emitted `TN`. Currently shipping correct mapping.
- Status: actioned-in-mapping

## 2026-04-15 — Subdivision code separator clarified

- Source: Avtax data dictionary slides.
- What changed: 12 governorates use **HYPHEN** (`JO-AM`), not underscore (`JO_AM`).
- Impact: Schema mapping + XSLT validation must enforce hyphen.
- Status: actioned-in-mapping

---

This log is bootstrapped from project memory. Future entries should come from `/v-law-watch` runs scraping jofotara.gov.jo + Slack `#mea_jordan_egypt_oman_discovery` + PRD revisions in `~/Downloads`.

Sources: `project_jordan_einvoicing.md` §3 (corrections), §11; `jordan_implementation_log.md` Session 1-2.
