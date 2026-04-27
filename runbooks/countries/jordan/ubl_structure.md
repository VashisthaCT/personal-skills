# Jordan UBL 2.1 Structure

Authoritative source: Avtax/ClearTax tech-mapping sheet (Apr 2026). MVP schema lives at `einvoice-interface/src/main/resources/SchemaMapping/JO/SalesEinvoiceToJoFotaraXml.json`.

## Document header (mandatory for all types)

| Element | Value |
|---|---|
| `cbc:ProfileID` | `reporting:1.0` (fixed) |
| `cbc:ID` | Internal invoice number, unique per seller |
| `cbc:UUID` | Client-generated GUID v4 |
| `cbc:IssueDate` | YYYY-MM-DD |
| `cbc:InvoiceTypeCode` | `388` (standard) or `381` (credit note); `@name` = sub-type code |
| `cbc:DocumentCurrencyCode` | `JOD`, `USD`, `SAR`, etc. (not restricted to JOD) |
| `cbc:TaxCurrencyCode` | Usually same as `DocumentCurrencyCode` |

## Sub-type codes (`@name` on InvoiceTypeCode) — only 8 allowed

Structure = scope digit (0=local, 1=export) × payment digit (1=cash, 2=A/R) × taxpayer digit (1=income bill, 2=general sales, 3=special sales).

| Code | Description | Payment Means | Has VAT | Has TaxTotal |
|---|---|---|---|---|
| 011 | Cash Income Bill (Local) | 10 | No | No |
| 021 | A/R Income Bill (Local) | 30 | No | No |
| 012 | Cash General Sales (Local) | 10 | Yes | Yes |
| 022 | A/R General Sales (Local) | 30 | Yes | Yes |
| 013 | Cash Special Sales (Local) | 10 | Yes + OTH | TBD |
| 023 | A/R Special Sales (Local) | 30 | Yes + OTH | TBD |
| 111 | Cash Export Income Bill | 10 | No | No |
| 121 | A/R Export Income Bill | 30 | No | No |

The slide deck once mentioned 2xx (Development Area) and 3xx (Odoo) codes — IGNORE these. The authoritative enum sheet has only the 8 above.

## AdditionalDocumentReference

- `ID=ICV`, `UUID={invoice counter}` — mandatory.
- `ID=QR` — present, but the QR value is added by the portal (we do not send it).

## Signature (UBLExtensions)

JoFotara signs server-side. We ship the `cac:Signature` stub block with fixed-literal URN values:
- `urn:oasis:names:specification:ubl:signature:Invoice`
- `urn:oasis:names:specification:ubl:dsig:enveloped:xades`

Mapping uses `sourceMappingExpression` with literal strings (no source path).

## Billing Reference & Payment Means (Credit Notes ONLY, type=381)

- `cac:BillingReference/cac:InvoiceDocumentReference`:
  - `cbc:ID` = original invoice ID
  - `cbc:UUID` = original invoice UUID
  - `cbc:DocumentDescription` = original full amount
- `cac:PaymentMeans/cbc:PaymentMeansCode` = `10` (Cash, fixed; listID=UN/ECE 4461)
- `cac:PaymentMeans/cbc:InstructionNote` = credit note reason

## Supplier Party (all mandatory)

- `PostalAddress/.../IdentificationCode` = `JO`
- `PartyTaxScheme/cbc:CompanyID` = seller TIN
- `PartyTaxScheme/.../cbc:ID` = `VAT` (fixed)
- `PartyLegalEntity/RegistrationName` = seller legal name
- `SellerSupplierParty/.../cbc:ID` = **Income Source Sequence** (ISTD-assigned per device)

## Customer Party

- `PartyIdentification/cbc:ID` + `@schemeID` — conditional, see `runbook.md` for buyer-ID matrix.
- `PostalAddress/cbc:CountrySubentity` — optional, **HYPHEN not underscore**: `JO-AM`, `JO-IR`, `JO-AZ`, `JO-BA`, `JO-MA`, `JO-KA`, `JO-AT`, `JO-MN`, `JO-AJ`, `JO-JA`, `JO-MD`, `JO-AQ` (12 governorates). For foreign buyers: omit.
- `PostalAddress/.../IdentificationCode` — customer country code (JO default; all country codes supported).
- `PartyTaxScheme/.../cbc:ID` = `VAT` (fixed, mandatory).
- `PartyLegalEntity/RegistrationName` — conditional: mandatory if A/R OR cash > 10,000 JOD.

## Tax Category IDs (`TaxCategory/cbc:ID`, UN/ECE 5305)

- `S` — Standard rate (with `TaxScheme=VAT` + `Percent`, e.g. 16).
- `Z` — Zero rated (`TaxScheme=VAT`).
- `O` — **Exempt** (NOT "fixed tax"; the slide deck once called it "OOS" — ignore that).

## Tax Schemes (`TaxScheme/cbc:ID`, UN/ECE 5153)

- `VAT` — normal VAT.
- `OTH` — used for Special Sales to carry a SECOND tax subtotal alongside VAT.
  - Slide deck says Special Sales has no line tax — contradicts tech mapping. TODO: resolve.

## Currency on amount elements

- **Header-level** `DocumentCurrencyCode` and `TaxCurrencyCode` use 3-letter `JOD`.
- **Amount-element** `currencyID="JO"` (2-letter) per PHP SDK and Odoo. Yes, this is inconsistent with the header — keep this in mind when generating XML.
- **Country code** — `cbc:IdentificationCode` should emit 2-letter `JO`. Default Java enum serializes as 3-letter `JOR` — explicit `CountryCode.getTwoDigitCodeFromEnum(...)` expression needed in mapping (DE has it as reference).

## Invoice Lines

- `cbc:ID`, `cbc:InvoicedQuantity` (`unitCode=PCE` default; other values untested), `cbc:LineExtensionAmount = Qty × Price − Discount`.
- `cac:Item/cbc:Name`.
- `cac:Price/cbc:PriceAmount` — **GROSS price in Jordan** (not net) per Avtax response.
- `cac:Price/cac:AllowanceCharge` — line discount: conditional if discount > 0. Reason=`DISCOUNT` (fixed).
- `cac:TaxTotal` / `cac:TaxSubtotal` per line — General Sales only per slides; Avtax still testing for Special Sales.

## Allowance/Charge

- `AllowanceCharge`: only `ChargeIndicator=false` accepted (no charges allowed, only discounts).
- Reason = `discount` (fixed).
- No VAT rate / code on allowance.

## LegalMonetaryTotal

`TaxExclusiveAmount` (mandatory), `TaxInclusiveAmount` (mandatory), `AllowanceTotalAmount` (mandatory, can be 0), `PayableAmount` (mandatory).

## Mapping null-leak guard

Every optional aggregate's leaf elements must carry `skipIfEmpty: "true"` to prevent `<cbc:ID schemeID="null"/>` generation. Customer `PartyIdentification`, `PartyTaxScheme.TaxScheme.ID`, `PaymentMeans`, doc + line `AllowanceCharge`, doc + line `TaxTotal` are all guarded. Regression test in `SalesToJoFotaraEndToEndXmlTest` asserts no XML contains `="null"` or `>null<`.

Sources: `project_jordan_einvoicing.md` §4-5; `jordan_implementation_log.md` Session 3 (mapping fixes).
