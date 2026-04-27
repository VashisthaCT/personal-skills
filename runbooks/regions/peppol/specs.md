# Peppol Specs (replaces api_contract for protocol-only region)

## Authoritative spec sources

- **Spec index:** https://docs.peppol.eu/edelivery/specs/reporting/
- **EUSR BIS:** https://docs.peppol.eu/edelivery/specs/reporting/eusr/bis/
- **TSR BIS:** https://docs.peppol.eu/edelivery/specs/reporting/tsr/bis/
- **TSR data-gathering rule (the Apr 17 scope-fix link):** https://docs.peppol.eu/edelivery/specs/reporting/tsr/bis/#_data_gathering
- **SP Operational Guideline v1.0.2:** https://docs.peppol.eu/edelivery/guidelines/reporting/2024-01-15%20Peppol%20Reporting%20-%20SP%20Operational%20Guideline%20v1.0.2.pdf
- **Participant Identifier Schemes v8.5:** https://docs.peppol.eu/edelivery/codelists/old/v8.5/Peppol%20Code%20Lists%20-%20Participant%20identifier%20schemes%20v8.5.html
- **PAE Code List (Peppol Authority Specific):** https://docs.peppol.eu/poac/ae/v1.0.3/pint-ae/trn-invoice/codelist/eas/
- **Reference impl (phax):** https://github.com/phax/peppol-reporting

## XSLT versions used in validation

- EUSR Schematron v1.1.4
- TSR Schematron v1.0.4

## Country extraction strategy per doc type (post-Apr 17)

| Doc Type | Sender Country (C1) | Receiver Country (C4) | Dedup Key | Count? |
|---|---|---|---|---|
| INVOICE / CREDIT_NOTE / SELF_BILLED_INVOICE / SELF_BILLED_CREDIT_NOTE | SBDH `COUNTRY_C1` | UBL `AccountingCustomerParty/Party/PostalAddress/Country/IdentificationCode` | Tax ID (`PartyTaxScheme/CompanyID` → `PartyLegalEntity/CompanyID` → PID) | YES |
| TAX_DATA_DOCUMENT (TDD) | Copy from linked business doc's sender country | Tax authority country (hardcoded per region — AE, FR, etc.) | Sender: tax ID from linked invoice; Receiver: fixed tax authority PID | TBD — Apr 17 wording ambiguous |
| CDAR | TBD | TBD | TBD | TBD — waiting on France expert |
| APPLICATION_RESPONSE (MLS / MLR) | — | — | — | NO (Apr 17 change) |
| EUSR / TSR | — | — | — | NO |

## Tax-ID extraction priority (PR #156)

1. `cac:PartyTaxScheme/cbc:CompanyID` (BT-31 sender, BT-48 receiver) — VAT/TRN/GST.
2. Fallback: `cac:PartyLegalEntity/cbc:CompanyID` (BT-30 sender, BT-47 receiver) — covers SIREN/SIRET for France.
3. Final fallback: null → EUSR pipeline falls back to Peppol Participant ID.

## SchemeID → Country mapping

OpenPeppol confirmed (2026-04-09 via Kunal Arora) that schemeID can be extracted using country codes — there is a code list to use. Caveat: some schemeIDs map to "International" rather than a specific country. Less critical post-Apr 17 since MLS/MLR (the main schemeID-fallback consumers) are now excluded.

Reference: Participant identifier schemes v8.5 link above.

## Aggregation filter (post-Apr 17)

```
$in: [INVOICE, CREDIT_NOTE, SELF_BILLED_INVOICE, SELF_BILLED_CREDIT_NOTE]
```

Or `DocumentType.EINVOICE_DOCUMENT_TYPES` constant — added in PR #105 by Mayank Nagpal on 2026-03-17. Possibly + TDD if confirmed.

Earlier plan (Apr 8 era) used `$nin: [EUSR, TSR]` — superseded.

## SBDH tax-ID save rule (current PR #156 logic — NEEDS BROADENING)

PR #156 currently saves `senderTaxId`/`receiverTaxId` ONLY for `INVOICE` and `CREDIT_NOTE`. Must broaden to `EINVOICE_DOCUMENT_TYPES` to cover self-billed variants. APPLICATION_RESPONSE no longer needs handling because MLS/MLR are excluded from counting.

## Critical formatting nits (caught by manual submissions)

- `CreationDateAndTime` — omit `+00:00` timezone offset. Use UTC-Z form or no offset at all (Prachi flagged Feb 2026).
- `DOCUMENTID InstanceIdentifier` format — fixed in hotfix 1.50.5 (Feb 2026).

## Testbed certs

- Currently uses G3 keychain cert; updated from G2 in March 2026 ahead of testbed run.

Sources: `project_peppol_reporting.md` §5, §7, §8, §9, §12.
