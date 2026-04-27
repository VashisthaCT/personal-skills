# Jordan — Oncall Runbook

Common errors, debug paths, and decision trees. Pre-go-live: most of this is theoretical. Will harden after MAF onboarding.

## Buyer ID matrix (PRD §8) — fast reference

| Scenario | Buyer Name | Buyer ID | Buyer ID Type |
|---|---|---|---|
| A/R invoices (021, 022, 023) | mandatory | mandatory | mandatory |
| Cash invoices > 10,000 JOD (011, 012, 013) | mandatory | mandatory | mandatory |
| Cash invoices ≤ 10,000 JOD | optional | mandatory | mandatory |

Scheme IDs:
- `TN` (numeric, NOT exactly 10 digits) → ClearTax internal code `TIN`.
- `NIN` (exactly 10 digits) → `JO:NIN`.
- `PN` (alphanumeric, >10 chars) → `PASSPORT`.

## Common error → debug paths

### Error: `UN-HD-1011 Country JO is not enabled in this deployment`

- **Cause:** `ENABLED_COUNTRIES` env var on the einvoicing-core deployment doesn't include `JO`.
- **Fix:** add `JO` to env via Vault row #1.

### Error: `Schema mapping not present with key: JO_EINVOICE_SALES_GOVT_SCHEMA_EINVOICE_DB_TEMPLATE_SCHEMA_MY`

- **Cause:** mapping file present in jar but not in the hardcoded whitelist.
- **Fix:** append `SchemaMapping/JO/SalesEinvoiceToJoFotaraXml.json` to `schema-registry.schemaMappingFilePaths` (Vault row #14). The legacy "MY" suffix is correct — `EINVOICE_DB_TEMPLATE_SCHEMA_MY` is the shared source schema name across BE/PL/DE/AE/JO.

### Error: `[Fatal Error] :1:1: Content is not allowed in prolog. → XSD_INVALID Document is not a valid XML`

- **Cause:** clear-routing's `JofotaraSendHandler` expects raw UBL XML; core's `JofotaraRoutingServiceImpl` returned the full `DocumentDTO` (Base64 + format + codeNumber).
- **Fix:** in core's routing impl, extract `getDocument()` (Base64), decode to raw XML string, return that. **This is a bug in Kushagra's PR #1323 — flag to him.**

### Error: `INVOICE_LINE_MISSING: Each InvoiceLine must have InvoicedQuantity and Price/PriceAmount`

- **Cause:** `EInvoiceUblCurrency.value` is a `Money` wrapper (its own `.value: BigDecimal` field). Mapping reading `.value` hits the Money object; need `.value.value`. Same for `EInvoiceUblTaxScheme.id` (plain String, not object) and `EInvoiceUblTaxCategory.id` (enum, not object with `.value`).
- **Fix:** mapping uses `.value.value` for amount paths, `taxScheme.id` directly, `taxCategory.id` directly.

### Error: `Country code 'JOR' not found in currency mapping, using default MYR`

- **Cause:** platform `CurrencyMappingUtil` lacks JOR→JOD entry (Vault row #16).
- **Fix:** non-blocking warning; file ticket against platform-lib team.

### Error: `Routing falls through to LHDN (400 invalid_client) for JO requests`

- **Cause:** clear-routing's `routing.countryRouterServiceMap` lacks `"JO":"JOFOTARA"` (Vault row #20). `RoutingFactory` defaults to `LHDN`.
- **Fix:** add JO entry to map.

### Error: `Validator files not present for document type: SALES in validation context: JO`

- **Cause:** `validationConfig` JSON blob lacks JO entry (Vault row #15).
- **Fix:** non-blocking — generate still runs; pre-submit XSLT validation is off until added.

### Error: `6002 Valid license is not present`

- **Cause:** test workspace lacks `E_INVOICING.SALES_INVOICE` license.
- **Fix:** licensing is per-customer-workspace; provisioned by licensing team. Local workaround: use AE-licensed workspace.

### Error: `ERR-10001 Supplier TRN not matching`

- **Cause:** payload's `companyID` does not match saved credentials' `tin`.
- **Fix:** ensure curl/payload `companyID` matches the TIN stored in `nodeSettings.clientCredentialSetting`.

### Error: `<cbc:ID schemeID="null"/>` in generated XML

- **Cause:** missing `skipIfEmpty: "true"` on a leaf inside an optional aggregate (PartyIdentification, PartyTaxScheme, PaymentMeans, AllowanceCharge, TaxTotal, TaxSubtotal).
- **Fix:** every leaf inside every optional aggregate must carry `skipIfEmpty: "true"`. Regression guard: `SalesToJoFotaraEndToEndXmlTest` no-null-leaks assertion.

## Decision trees

### REJECTED response with validation error

1. Decode `EINV_RESULTS.ERRORS[0].EINV_CODE` and `EINV_MESSAGE`.
2. If validation rule (V-prefix), surface to UI as "Invoice Rejected by ISTD" + the message.
3. Do NOT auto-retry rejected invoices. User must fix and resubmit (with fresh UUID v4; ID stays the same).
4. For corrections of an already-accepted invoice, generate a Credit Note (type 381) referencing original.

### Auth failure (401 or 403)

1. Distinguish: do NOT retry on 401/403.
2. Surface to UI: "Authentication failed. Check Settings > JoFotara Credentials."
3. Admin re-enters Secret-Key (Edit clears the field — admin must re-enter full key).
4. If the device was toggled Inactive on the JoFotara portal, no software fix. Coordinate with portal admin.

### Network / 500 / 503 / 429

1. Retry per PRD §6.2: 3 attempts at 5s → 30s → 2min.
2. After 3 failures → mark invoice Failed.
3. User can manually Retry Submission (fresh UUID v4).

## Logs to grep

- `JofotaraSendHandler` — vendor module submission entry point.
- `JofotaraRoutingServiceImpl.createDocumentSubmissionRoutingRequest` — core-side routing request shape (note the Base64-decode fix).
- `EInvoiceRouterClient.encryptHeaders` — AES encryption of `JOFOTARA_CLIENT_ID` / `JOFOTARA_CLIENT_SECRET` MDC values.
- `SchemaMappingRepository` startup load — confirms JO mapping was registered (look for the file path in `schemaMappingFilePaths` log line).

## Known good local end-to-end

Branch `feat/NV-266-jordan-einvoice-core` + Kushagra's `origin/jofotara-routing-changes` cherry-picked into working tree + clear-routing branch `jordan-router-client` running on `:11087` + `JofotaraMockClient` toggled on → `POST /v1/einvoice/generate` returns `Success: true`, Mongo status `SUBMITTED`, mock `submissionUID: MOCK-...`. See `jordan_implementation_log.md` Session 4 attempt #10.

## RCAs encountered

None yet (pre-go-live). Add entries here as they happen, using `prompts/rca_template.md` (VP-praised NIC RCF format).

Sources: `project_jordan_einvoicing.md` §3, §6; `jordan_implementation_log.md` Sessions 2-4.
