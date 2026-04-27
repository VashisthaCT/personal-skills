# India UBL Structure

TODO — IRN/EWB schema is JSON, not UBL. India is one of the few countries in the platform that does NOT use UBL; ClearTax IRP issues IRN against the NIC JSON schema.

## What's actually used

- **IRN payload schema:** NIC's published IRN JSON schema (B2B Invoice). Maintained by NIC; CBIC notifications drive version bumps.
- **EWB payload schema:** NIC's EWB JSON schema (separate from IRN).

## File this section as TODO

The repo runbook structure assumes UBL-shaped countries; for India this file is essentially a pointer document. If a future need arises (e.g., a country-comparison brief that must mention India's schema model), expand here.

## What we *do* know about field handling

- **40% GST rate cutover** (Sep 2025) required HSN-level rate updates across `e-invoicing-be`, `ingestion-overlord`, and `clr-irp-be`. PRs e-invoicing-be#3664, ingestion-overlord#5104, clr-irp-be#467.
- **Tobacco RSP** (Feb 2026) — RSP (Retail Sale Price) field for tobacco HSN required cross-service handling across 5 services. CIRP-193, Feb 1 cutover, Swiggy 3-hour pivot Jan 30.
- **Mitsuba auto-GST rule template** (EINVI-1231, ingestion-overlord#5008) — auto-derives GST rate from HSN/SAC codes during ingestion.

These touch field-handling logic but aren't strict schema spec.

## TODO sections

- IRN JSON schema reference (point to NIC docs).
- EWB JSON schema reference.
- HSN/SAC code reference behaviour.
- Tax category / rate enums.
- Mandatory vs optional field matrix.

Sources: `project_perf_review_fy26.md` §4 (40% cutover, RSP, Mitsuba). Mark TODO where memory has no concrete schema detail.
