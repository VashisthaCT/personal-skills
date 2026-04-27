# Peppol — Oncall Runbook

Common errors, debug paths, and troubleshooting for the AP and EUSR/TSR pipeline.

## Existing AP troubleshooting docs

`e-InvoiceVerse/docs/agent/troubleshooting/EU-PEPPOL/` covers:
- Missing purchase invoices.
- PDF values missing.
- Receiver doc type not supported.
- Stuck "Delivered to BN".

This runbook focuses on the EUSR/TSR-specific issues encountered Jan-Apr 2026.

## EUSR / TSR generation

### Error: Schematron rejects `CreationDateAndTime`

- **Cause:** trailing `+00:00` timezone offset is not accepted.
- **Fix:** generate without offset (UTC-Z form or no offset).

### Error: `DOCUMENTID InstanceIdentifier` fails Schematron

- **Cause:** format mismatch (Jan 2026 first submission).
- **Fix:** hotfix 1.50.5 corrected the format. Confirm current generator emits the post-hotfix shape.

### Testbed cert mismatch

- **Cause:** keychain held G2 cert; testbed expects G3.
- **Fix:** swap keychain cert to G3 before testbed run.

### SCH-TSR-11 / SCH-TSR-12 (`PerSP-DT-PR-CC` is MUST)

- **Cause:** Testbed Schematron treats PerSP-DT-PR-CC subtotals as MUST even though BIS text says "MAY". Required `senderCountry` AND `receiverCountry` for every transaction including MLS/MLR (which had null receiver).
- **Status post-Apr 17:** Largely moot. MLS/MLR excluded from counting → every counted transaction has both country codes from UBL body + SBDH.
- **Apr 14 manual:** used the old interpretation (C2/C3 for MLS, tax authority for TDD); accepted by OpenPeppol but built on now-superseded Apr 8 guidance.

## Tax-ID extraction (PR #156)

### Tax ID null for SELF_BILLED_*

- **Cause:** PR #156 filter is `INVOICE \|\| CREDIT_NOTE`. Self-billed slips through.
- **Fix:** broaden filter to `EINVOICE_DOCUMENT_TYPES` (the 4-member constant from PR #105).

### Tax ID null for some legitimate docs

- **Cause:** Neither `cac:PartyTaxScheme/cbc:CompanyID` nor `cac:PartyLegalEntity/cbc:CompanyID` present.
- **Fallback:** EUSR pipeline uses Peppol Participant ID (PID).
- **No code fix needed.**

## Backfill script

### S3 download fails

- **Behaviour:** Permanent vs transient — S3 errors do NOT mark the record UNAVAILABLE (preserves retry).
- **Fix:** restart script; cursor-based pagination resumes from `_id > last_seen`.

### AWS SSO token expires

- **Behaviour:** Auto-refresh every 50 batches; auto-login on expiry.
- **Fix:** none — re-runs are idempotent.

### Old field names in QA after schema rename

- **Cause:** QA records saved with `senderVatNumber`/`receiverVatNumber`; new code reads `senderTaxId`/`receiverTaxId`.
- **Fix:** Either rename in DB OR re-run backfill with new schema. Re-run preferred.

## Routing / outbound

### `clear-peppol` vendor module errors

- See `~/Desktop/clear-routing/clear-peppol/` and the AP's troubleshooting docs.

## Decision trees

### Monthly report cycle

1. 1st of month, 02:00 UTC — cron triggers.
2. If automation OK → automated report goes out.
3. If automation fails → manual fallback via `/Users/vashistha.garg/Desktop/dbchanges/manual_eusr_report.py`.
4. Submit by the 15th. Watch for reminder email on the 11th.
5. If non-compliance mark on 16th — escalate to Anand + Prachi.

### Schematron rejection on submit

1. Capture full Schematron error messages.
2. Cross-reference with `feat/peppol_report_automation` test fixtures.
3. If timezone or `InstanceIdentifier` issue, see common errors above.
4. If `PerSP-DT-PR-CC` related, confirm post-Apr 17 scope filter is in place.
5. If novel — escalate to Anand + Prachi; OpenPeppol may need to clarify spec.

## Logs to grep

- `clear-peppol-consumer` ReportScheduler — confirm cron triggered.
- `ReportGenerationServiceImpl` — orchestrates aggregation → XML → validation → S3 → SQS.
- `ReportXmlBuilder` — XML generation; null leaks would surface here.
- `clear-peppol/` vendor module logs — outbound AS4 transmission.

## RCAs / incidents encountered

None recorded yet. Add entries here as they happen, using `prompts/rca_template.md`.

Sources: `project_peppol_reporting.md` §6, §7, §11, §12.
