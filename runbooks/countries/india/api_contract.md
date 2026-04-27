# India API Contract

TODO — this section is thin. Below is a high-level pointer set; deep field-by-field detail is not in current memory.

## IRP (NIC) — IRN Issuance

- **Authoritative spec docs:** https://docs.ewaybillgst.gov.in/
- **NIC environments:** NIC1 (legacy primary) and NIC2 (newer). Auto-switcher between them was reverted post-Nov 18-19 outage; today the system is locked to NIC-only (single-NIC).
- **Auth:** TODO — capture from clr-irp-be config.
- **Endpoints:** TODO — list canonical endpoints.

## EWB

- **Authoritative spec docs:** https://docs.ewaybillgst.gov.in/
- **Endpoints:** TODO.
- **Atomic locking model:** Redis distributed lock used to prevent duplicate EWB submissions. EIOCJ-536 (initial), EIOCJ-670 (H2 follow-up). See PR e-invoicing-be#3614, #3615, #3691.

## ClearTax IRP (`clr-irp-be`)

- **SLA Monitoring APIs:** CIRP-186/187/188 (PRs #475/#476/#478). 6 endpoints, mostly internal-only-API style.
- **Bulk APIs:** NV-191 (clr-irp-be#482) processed 26,063 GSTINs annual-turnover updates in <3 days. Pattern: InternalOnlyApi + slab mapper + dry-run + 3 CSV outputs.

## TODO sections

- IRN request/response field-level JSON shape.
- EWB request/response field-level JSON shape.
- Error code reference.
- Timeout / retry policy.
- Rate limits.
- ClearTax-specific headers and MDC propagation.

## Reference resources

- **GST notifications:** CBIC (cbic.gov.in) + GSTN circulars.
- **EWB GST docs:** https://docs.ewaybillgst.gov.in/
- **clr-irp-be repo:** see `code_map.md`.

Sources: `project_perf_review_fy26.md` §4 (NIC, EWB, SLA, NV-191, RSP); existing on-call runbooks not yet migrated. Mark TODO where memory lacks contract-level detail.
