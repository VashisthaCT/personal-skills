# Peppol — Spec Changes

Append-only log of OpenPeppol spec deltas and ClearTax-side scope adjustments. Newest at top. Curator agent owns appends.

## 2026-04-17 — MLS/MLR/receipts EXCLUDED from TSR/EUSR counting

- Source: OpenPeppol email forwarded by Prachi Singhal at 23:27 IST; confirmed in conversation with Vashistha 2026-04-18 12:19 IST.
- Quote: *"The AS4 messages that contain a business transaction may be counted, but the MLS, MLR, TSR, EUSR, receipts shouldn't be counted as TSR."*
- Spec ref: https://docs.peppol.eu/edelivery/specs/reporting/tsr/bis/#_data_gathering
- What changed: Final count-scope is exactly 4 doc types — `INVOICE`, `CREDIT_NOTE`, `SELF_BILLED_INVOICE`, `SELF_BILLED_CREDIT_NOTE`. APPLICATION_RESPONSE (MLS/MLR), TDD (pending), CDAR, receipts, EUSR/TSR themselves are excluded.
- Impact: Eliminates SP cert parsing complexity, tax authority country map, and most CDAR / PerSP-DT-PR-CC edge cases. Aggregation filter changes from `$nin: [EUSR, TSR]` to `$in: EINVOICE_DOCUMENT_TYPES` (+ TDD if confirmed). Open retroactive question: Jan/Feb/Mar submissions counted MLS — resubmit corrected versions or leave?
- Status: actioned-in-progress — `feat/peppol_report_automation` branch needs the filter change before PR.

## 2026-04-09 — SchemeID → Country mapping confirmed

- Source: Kunal Arora question to OpenPeppol; answer confirmed.
- Quote: *"Scheme ID can be extracted using the Country Codes yes. There is a code list which can be used."*
- Reference list: https://docs.peppol.eu/edelivery/codelists/old/v8.5/Peppol%20Code%20Lists%20-%20Participant%20identifier%20schemes%20v8.5.html
- Caveat (Vashistha found): some schemeIDs map to "International" rather than a specific country.
- Impact: less critical post-Apr 17 since MLS/MLR (the main schemeID-fallback consumers) are excluded.
- Status: noted

## 2026-04-08 — OpenPeppol Q1-Q4 answers (some superseded by Apr 17)

- Source: OpenPeppol email via Prachi.
- Q1 (dedup hierarchy): *"Based on the 'Legal Entity' that represents C4 — decide on your side."* → ClearTax decision: VAT/TaxID. **Still valid.**
- Q2 (which doc types): *"Yes, MLR, MLS, TDD — everything counts. Only EUSR/TSR don't."* → **SUPERSEDED 2026-04-17.**
- Q3 (PID vs Tax ID dedup): *"Business level decision. Tax ID for business docs."* → ClearTax decision. **Still valid.**
- Q4 (country codes for MLS/TDD/CDAR): MLS = SP country codes (C2/C3) → MOOT (MLS excluded). TDD = sender country same as business doc; receiver = tax authority country. CDAR = "France expert needs to answer." → **STILL UNRESOLVED for CDAR.**
- Status: partially superseded

## 2026-03-17 — Self-billing doc types added

- Source: PR #105 by Mayank Nagpal (`clear-peppol-ap`).
- What changed: `SELF_BILLED_INVOICE` and `SELF_BILLED_CREDIT_NOTE` added to `DocumentType` enum. `EINVOICE_DOCUMENT_TYPES` constant added covering all 4 e-invoice types.
- Impact: Before Mar 17, AP couldn't distinguish self-billed docs. Reports for Feb 2026 and earlier correctly excluded them (couldn't have counted). March 2026 onward must include them.
- Status: actioned

## 2026-02-XX — Cert keychain updated G2 → G3

- Source: Testbed run prep, March 2026.
- What changed: Updated keychain cert from G2 to G3 to pass testbed validation.
- Impact: Live AP cert in use is now G3.
- Status: actioned

## 2026-02-XX — `CreationDateAndTime` timezone fix

- Source: Manual submission Feb 2026 — Prachi flagged.
- What changed: Omit `+00:00` from `CreationDateAndTime` (use UTC-Z form or no offset).
- Impact: Manual + automated XML generators must respect this.
- Status: actioned

## 2026-02-XX — `DOCUMENTID InstanceIdentifier` format fix

- Source: Hotfix 1.50.5, Feb 2026.
- What changed: Fixed `InstanceIdentifier` format on first submission (Jan 2026 report).
- Status: actioned

---

This log is bootstrapped from project memory. Future entries should come from `/v-law-watch peppol` runs scraping docs.peppol.eu + the openpeppol-developer mailing list + BIS bulletins + the group DM.

Sources: `project_peppol_reporting.md` §5, §8, §10.
