# UAE UBL Structure

## TaxCategory ordering

The most-known UBL detail for UAE is the **TaxCategory element ordering** within `TaxSubtotal`. This was fixed in einvoicing-core#1282 with 18 regression tests guarding the order.

TODO: capture the exact ordering (`cbc:ID` first vs. `cac:TaxScheme` first, etc.) from the PR diff. Memory cites the issue but not the canonical sequence.

## Validation rules (replicated pattern)

`einvoice-ae` is the validation-rules reference module for MEA:

- `BuyerValidationRules`
- `SellerValidationRules`
- `TaxTotalsValidationRules`
- `DocumentTotalsValidationRules`
- `LineItemValidationRules`
- `HeaderValidationRules`
- `AllowanceChargeValidationRules`
- `PaymentValidationRules`
- `CreditNoteValidationRules`

All built on `ValidationContext` + `ValidationError` + `ValidationRule` interface. Jordan currently has zero validation rule classes — replicate this pattern (NV-266 follow-up).

## B2B vs B2C

UAE supports both B2B and B2C flows (B2C added with Tabby launch Dec 2025). Schema differences between the two: TODO — capture from `einvoicing-core#888`.

## Tax authority country code

For Peppol TDD receiver country (when TDD is in scope): `AE`.

## Arabic strings / translation

UAE templates 5/6/8/9 route Arabic strings through Kramer; design Jan 12 thread (22 replies): https://cleartaxtech.slack.com/archives/C09TU9UMJJ2/p1768202789046269. Deploy Jan 19 thread (90 replies): https://cleartaxtech.slack.com/archives/C04U10T2DAN/p1768812228954269. The translation service is cross-MEA, not UAE-only.

## TODO sections

- Document type code list.
- Tax category enum reference.
- Mandatory vs optional field matrix.
- Currency rules (AED).
- Buyer ID schemes.

Sources: `project_perf_review_fy26.md` §4 H2 (TaxCategory ordering, Tabby B2B/B2C, translation service), §9 (Slack permalinks); `platform_architecture.md` §3.
