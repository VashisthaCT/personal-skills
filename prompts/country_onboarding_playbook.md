# Country Onboarding Playbook

The reference doc for `/v-country-onboard`. Every section here is distilled from Jordan implementation. Memory citations point back to original incidents in `~/.claude/projects/-Users-vashistha-garg/memory/jordan_implementation_log.md` and `project_jordan_einvoicing.md`.

**MVP scope:** the einvoice-<cc> module inside `~/Desktop/einvoicing-core`. Broader 6-repo orchestration (clear-routing, ingestion-overlord, clear-data-browser-be, etc.) is out of scope for this skill — listed as TODOs in Section E.

---

## A. Pre-flight context to gather (the interview)

The `init` mode walks the user through these questions. Answers land in `data/onboarding/<cc>/context.yaml`.

1. **Country basics.** Full name, 2-letter ISO code (UBL `IdentificationCode`), 3-letter ISO code (DB enum, e.g. `JOR`/`KWT`), region (MEA/EU/SEA/LATAM).
2. **Regulator + portal.** Regulator name (ISTD / ZATCA / FTA / NIC), public portal URL, technical/integrator portal URL.
3. **API endpoint.** Production base URL. Note absence of separate sandbox if applicable (Jordan: no sandbox — all live).
4. **Sandbox availability.** Yes/no. If no, plan for live-only debug + mock client in clear-routing.
5. **Authentication model.** OAuth2 / static headers (Client-Id + Secret-Key) / per-device credentials. **Confirm/correct** (Jordan PRD §3A.5 said HTTP 401 but SDK + Avtax Slack said 403 — code must handle both).
6. **Retry policy.** Number of attempts, backoff sequence in seconds, retryable HTTP codes. **Confirm/correct** (Jordan PRD said 5s/30s/2min; Avtax Slack said 2s/5s/10s — PRD wins by convention).
7. **Timeout.** Default request timeout in seconds (Jordan: 100s).
8. **Document types.** UBL `InvoiceTypeCode` values supported (Jordan: 388 standard / 381 credit note). Cancel/credit-note model — does the regulator support cancel as a separate flow, or only credit-note correction (Jordan: only credit note)?
9. **B2B / B2C / B2G scope.** Sales / purchase / both. (Jordan MVP: sales only.)
10. **Sub-type matrix.** `@name` attribute on InvoiceTypeCode. Jordan has 8 codes (011/021/012/022/013/023/111/121) decomposed as scope×payment×taxpayer. Capture: code, description, payment-means code, has VAT, has TaxTotal.
11. **Mandatory vs conditional fields.** Buyer name + buyer ID + buyer ID type — when mandatory by sub-type. Jordan rule: A/R always mandatory; cash >10K JOD mandatory; cash ≤10K JOD ID required, name optional.
12. **Currencies.** 3-letter for header (`DocumentCurrencyCode`, `TaxCurrencyCode`), 2-letter for amount-element `currencyID` attribute. **Confirm/correct** Jordan inconsistency: header uses `JOD`, amount elements use `JO` per PHP SDK + Odoo.
13. **Buyer ID schemes.** UBL `@schemeID` value × ClearTax internal enum API code × description × validation. Jordan example: `TN`/`TIN` (tax number, numeric, NOT exactly 10), `NIN`/`JO_NIN` (National ID, exactly 10 digits), `PN`/`PASSPORT` (alphanumeric, >10 chars).
14. **Allowance/charge rules.** Document-level only? Line-level only? Both? Jordan accepts only `ChargeIndicator=false` (no charges, only discounts) at document level; line-level discount via `cac:Price/cac:AllowanceCharge`.
15. **Tax category enum.** UN/ECE 5305 mapping: which IDs apply (S/Z/O/E/G/AE/...). Jordan: S/Z/O. **Confirm/correct** Jordan O = "Exempt" (NOT "Out of scope" / "fixed tax" as PHP SDK once labelled).
16. **Tax scheme enum.** UN/ECE 5153. Jordan: VAT for normal; OTH for Special Sales' second subtotal alongside VAT.
17. **Income source / device / ISS concept.** Regulator-assigned per-device identifier? Where in the XML does it live? Jordan: `cac:SellerSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID`, sourced from `ClientCredentialSetting.incomeSourceSequence` per device.
18. **Governorates / sub-divisions.** UBL `cac:PostalAddress/cbc:CountrySubentity` enum. Jordan has 12 governorates with **HYPHEN** delimiter (`JO-AM`, `JO-IR`, …) — never underscore. For foreign buyers, omit.
19. **Reference XML samples folder.** Drive folder URL with regulator-blessed sample XMLs (Jordan: Avtax shared 9 reference XMLs).
20. **Reference SDK URLs.** Open-source implementations to grep for shape. Jordan: PHP SDK `jafar-albadarneh/jofotara`, Odoo `odoo/addons/l10n_jo_edi`.
21. **`customizationID`.** UBL `cbc:CustomizationID`. Pint API requires it; some regulators don't emit it to the wire XML. Jordan: `urn:peppol:pint:billing-1@jo-1` at API layer; mapping does not emit to XML (handled by framework).
22. **ICV `AdditionalDocumentReference` convention.** What value goes in `UUID`? Jordan: invoice counter = document number (the `id.en` field at DB level). Workaround documented in Section B (Pint→DB drops the `uuid` field).
23. **Open queries / spec conflicts.** List every place the PRD, the consultant's xlsx, the SDK and the regulator portal disagree. These become the consultant's question list (Section F).

---

## B. Schema mapping conventions (every Jordan gotcha)

Each entry: 1-line description + WRONG pattern + RIGHT pattern + memory citation.

### B1. Money wrapper on amount fields
**Memory:** `jordan_implementation_log.md` Session 4 lines 526–528, 596–606.

DB-level `EInvoiceUblDetails` wraps every amount in a `Money { value: BigDecimal }` object. Mappings against a Pint-shape fixture (flat) silently emit empty `<cbc:*Amount>` elements in production.

```json
// WRONG — reads the Money wrapper as a number, gets nothing
"sourcePath": "legalMonetaryTotal.taxExclusiveAmount.value"

// RIGHT — descend one more level into the wrapper's own .value
"sourcePath": "legalMonetaryTotal.taxExclusiveAmount.value.value"
```

Apply to **every** Amount path (15+ in a typical Jordan mapping): TaxExclusive, TaxInclusive, AllowanceTotal, Payable, line LineExtensionAmount, line PriceAmount, line TaxAmount, doc-level TaxAmount.

### B2. TaxScheme.id is plain String at DB level
**Memory:** Session 4 lines 526, 600–602.

Pint API has `taxScheme.id: {value: "VAT"}`; DB shape has `taxScheme.id: "VAT"` (plain).

```json
// WRONG
"sourcePath": "taxScheme.id.value"
// RIGHT
"sourcePath": "taxScheme.id"
```

### B3. TaxCategory.id is a TaxCategoryID enum at DB level
**Memory:** Session 4 lines 526, 600–602.

Same pattern as B2 — DB shape is plain enum-name string, not nested.

```json
// WRONG
"sourcePath": "taxCategory.id.value"
// RIGHT
"sourcePath": "taxCategory.id"
```

### B4. Country code 3-letter → 2-letter conversion
**Memory:** Session 4 lines 526, 549, 603, 651–656.

DB stores 3-letter enum names (`JOR`, `KWT`); UBL `IdentificationCode` requires 2-letter (`JO`, `KW`).

```json
// WRONG — emits "JOR" (rejected by regulator)
"sourcePath": "postalAddress.country.identificationCode.countryCode"

// RIGHT — use CountryCode helper expression (mirrors DE mapping)
"sourceMappingExpression": "@{CountryCode.getTwoDigitCodeFromEnum($postalAddress.country.identificationCode.countryCode)}"
```

`CountryCode` enum lives at `einvoice-models/.../my/enums/CountryCode.java`. Each entry maps `JOR("JO", "JORDAN")`. Apply to both supplier + customer.

### B5. ICV AdditionalDocumentReference UUID — Pint→DB drops the uuid field
**Memory:** Session 4 lines 657–663.

`EInvoiceUblAdditionalDocumentReference.uuid` exists at DB level but Pint→EInvoiceUbl conversion doesn't copy Pint's `AdditionalDocumentReferenceType.uuid` into it. Mongo record has no `uuid`.

If the mapping reads `uuid` and finds nothing, schema-registry's `DynamicExpressionEvaluator` falls back to enclosing Invoice's `uuid` → emits invoice UUID instead of document number.

```json
// WRONG — falls back to Invoice.UUID
"sourcePath": "uuid"

// RIGHT (workaround) — relies on Jordan convention: ICV counter = document number = id.en
"sourcePath": "id.en"
```

Platform-level proper fix: Pint→EInvoiceUbl converter should preserve uuid field. Flag to platform team. Workaround stable for any country where ICV-counter = document-number.

**Also:** destination path `Invoice.AdditionalDocumentReference[0].UUID` does NOT work — `[0]` ends up in the XML element name and the parser dies with `INVALID_CHARACTER_ERR`. Array indexing in destination paths is unsupported.

### B6. Note / notes[] Pint shape
**Memory:** Session 4 lines 642, 694.

Pint at API layer has `Note { value: String, languageID?, languageLocaleID? }`. After an over-aggressive MultiLingualString unwrap, the value collapses to a plain string and the API returns `UN-HD-1011: Invalid value for field documents.[0].einvoice.note`.

```json
// WRONG (post-unwrap)
"note": "Discount applied"

// RIGHT
"note": {"value": "Discount applied"}
```

### B7. Signature stub (UBLExtensions)
**Memory:** Session 3 lines 416, 425.

Most regulators sign server-side. We send an unsigned envelope with a fixed-literal `cac:Signature` block; portal returns the full signed XML.

```json
// In the mapping JSON
{
  "destinationPath": "Invoice.Signature.ID",
  "sourceMappingExpression": "urn:oasis:names:specification:ubl:signature:Invoice"
},
{
  "destinationPath": "Invoice.Signature.SignatureMethod",
  "sourceMappingExpression": "urn:oasis:names:specification:ubl:dsig:enveloped:xades"
}
```

No source path. Pure literal `sourceMappingExpression`.

### B8. AccountingContact (not Contact) for Telephone
**Memory:** Session 3 line 417.

Reference XMLs use `cac:AccountingContact/cbc:Telephone` — not `cac:Contact/cbc:Telephone`. Pure naming gotcha.

```json
// WRONG
"destinationPath": "Invoice.AccountingCustomerParty.Party.Contact.Telephone"
// RIGHT
"destinationPath": "Invoice.AccountingCustomerParty.Party.AccountingContact.Telephone"
```

### B9. TaxCategory + TaxScheme attribute ordering
**Memory:** Session 3 line 418.

UBL validators reject `<TaxCategory>` and `<TaxScheme>` ID elements without `schemeAgencyID` + `schemeID` attributes. Split the destination path into `.text` + `._schemeAgencyID` + `._schemeID`.

```json
// RIGHT — split TaxCategory.ID
{"destinationPath": "...TaxCategory.ID.text", "sourcePath": "taxCategory.id"},
{"destinationPath": "...TaxCategory.ID._schemeAgencyID", "sourceMappingExpression": "6"},
{"destinationPath": "...TaxCategory.ID._schemeID", "sourceMappingExpression": "UN/ECE 5305"},

// And TaxScheme.ID — same pattern but with UN/ECE 5153
{"destinationPath": "...TaxCategory.TaxScheme.ID.text", "sourcePath": "taxScheme.id"},
{"destinationPath": "...TaxCategory.TaxScheme.ID._schemeAgencyID", "sourceMappingExpression": "6"},
{"destinationPath": "...TaxCategory.TaxScheme.ID._schemeID", "sourceMappingExpression": "UN/ECE 5153"}
```

Apply to **both** doc-level and line-level TaxTotal blocks. (Lesson originally encoded for UAE; carries forward.)

### B10. The 3-flag pattern: `skipIfEmpty + skipIfSourceEmpty + pathResolutionMode: RELATIVE`
**Memory:** Session 5 Part 6 lines 1385–1446 + Part 7 lines 1452–1546.

Schema-registry has TWO empty-handling flags:

| Flag | Stage | Behavior |
|---|---|---|
| `skipIfEmpty` | post-process | Drops the destination write when the resolved result is empty. |
| `skipIfSourceEmpty` | pre-process | Bypasses children evaluation + write entirely when source is empty. |

Plus path-resolution mode:
- Default `RELATIVE_WITH_FALLBACK` walks up to root scope on missing local paths → silently injects doc-level values into line-level mappings.
- `RELATIVE` disables the fallback.

For any optional/conditional block (especially nested inside arrays):

```json
{
  "destinationPath": "Invoice.PaymentMeans",
  "sourcePath": "paymentMeans",
  "skipIfEmpty": "true",
  "skipIfSourceEmpty": "true",
  "pathResolutionMode": "RELATIVE"
}
```

Without `skipIfSourceEmpty`, the children fire and emit empty constants like `<cbc:PaymentMeansCode listID="UN/ECE 4461"/>`. Without `pathResolutionMode: RELATIVE`, line-level `taxTotal` falls back to doc-level `taxTotal` and injects wrong values.

Add **absence-assertion tests** (not just presence) to catch regressions. Jordan unit-test gap caught only by live curl: tests asserted `<TaxAmount>` was correct in taxed scenarios but never asserted PaymentMeans was *absent* in cash sub-types.

### B11. `skipIfEmpty` cascade on every inner leaf of an optional aggregate
**Memory:** Session 3 line 419.

Even with B10, every inner leaf of an optional block needs `skipIfEmpty: "true"` to prevent `<cbc:ID schemeID="null"/>` null-leaks. Apply to: customer `PartyIdentification`, customer `PartyTaxScheme.TaxScheme.ID`, `PaymentMeans`, doc + line `AllowanceCharge`, doc + line `TaxTotal` (and nested `TaxSubtotal.TaxCategory.*`), `InvoicedQuantity._unitCode`.

### B12. `sourceSchemaName=_MY` (template inheritance)
**Memory:** Session 4 lines 521 row #4, 754.

`schema-registry-config.generate.sales.source` defaults to `EINVOICE_DB_TEMPLATE_SCHEMA_MY` (legacy name shared across BE/PL/DE/AE/HR/JO). New countries that name their source `EINVOICE_DB_TEMPLATE_SCHEMA_<CC>` get `SchemaParsingException: ..._<CC>_<DEST>_..._MY not found`.

```json
// WRONG (in mapping JSON)
"sourceSchemaName": "EINVOICE_DB_TEMPLATE_SCHEMA_<CC>"
// RIGHT — match the legacy shared name
"sourceSchemaName": "EINVOICE_DB_TEMPLATE_SCHEMA_MY"
```

Test class `SOURCE_SCHEMA` constants must match.

### B13. `customizationID` required by Pint, not emitted to XML
**Memory:** Session 4 line 643, 737.

Pint `customizationID` is mandatory at the API layer for validation, but our mapping does not emit it to the wire XML — handled at framework level. Capture the value (e.g. `urn:peppol:pint:billing-1@jo-1`) in `context.yaml` for use in curl examples; do not add it to the schema mapping.

### B14. ICV `AdditionalDocumentReference` skeleton
**Memory:** Section 4 of `project_jordan_einvoicing.md` + Section B5 above.

Every invoice needs:
```xml
<cac:AdditionalDocumentReference>
  <cbc:ID>ICV</cbc:ID>
  <cbc:UUID>{invoice counter}</cbc:UUID>
</cac:AdditionalDocumentReference>
```

Encode the constant `"ICV"` via `sourceMappingExpression`; encode the UUID via the workaround in B5.

### B15. JaCoCo coverage exclusions for country DTOs
**Memory:** Session 5 Part 8 lines 1551–1640.

CI 80% coverage gate fails on Lombok-generated DTO classes. Add to `test-coverage-report/pom.xml`:

```xml
<exclude>com/clear/einvoicing/<cc>/dto/**</exclude>
```

Mirror the existing `com/clear/einvoicing/dtos/**` exclusion pattern. `*Constants.class` is already auto-excluded globally.

### B16. Mockito + JDK 23 — final-class mock failure
**Memory:** Session 3 lines 444–446 + Session 5 Part 8 line 1596.

JDK 23 + mockito-inline 5.2.0 → ByteBuddy can't self-attach. Mocks of `EInvoiceDocument` and Pint model classes fail with "Could not modify all classes". Replace with real `Pint.InvoiceData` builders (mirror einvoice-ae's pattern) populated with the minimum fields.

### B17. MDC thread-local leak in tests
**Memory:** Session 5 Part 8 line 1601.

MDC is thread-local; tests can leak state. Always:

```java
@AfterEach
void clearMdc() { MDC.clear(); }
```

In any test that touches `MDC.put(...)`.

### B18. SBDH country-exclusion list
**Memory:** Session 4 line 523.

`EInvoiceGlobalGenerationService.processAndValidateLhdnDocumentFormation` wraps the XML in an SBDH envelope when `routerService=PEPPOL && country!=PL`. Non-PEPPOL non-PL countries (Jordan, KSA, Egypt) hit the condition incorrectly.

```java
// Add the country to the exclusion list
&& !country.equalsIgnoreCase("<CC>")
```

Already excludes PL + HR + JO. New countries that don't use Peppol/SBDH need to join the list.

---

## C. Test patterns

### Two test layers per country

| Layer | File | Count | What it asserts |
|---|---|---|---|
| Mapper-layer | `SalesTo<Provider>MapperTest.java` | ~50 | JSON fixture → schema-mapping → target JsonNode field-by-field |
| E2E XML | `SalesTo<Provider>EndToEndXmlTest.java` | ~93 | JSON fixture → Pint → EInvoiceUbl → real XML → XPath assertions |

### 9 canonical fixtures
Stored at `einvoice-<cc>/src/test/resources/<cc>/inputs/0{1..9}_*.json`. Cover:
- All sub-type codes
- All buyer ID schemes (TN/NIN/PN/None)
- All tax categories (S/Z/O)
- Invoice (388) + Credit Note (381)
- Doc-level + line-level discounts
- Single-line + multi-line (up to 6 lines)

### Pint API shape vs DB shape transforms (the inverse helper)
**Memory:** Session 4 lines 631–644.

API curl body uses Pint shape; mapper tests use DB shape. The HTML curl-generator runs an inverse transform:
- Unwrap `MultiLingualString {en: "X"}` → `"X"` (id, registrationName, item.name)
- Unwrap `Money {value: {value: X}, currencyID: Y}` → `{value: X, currencyID: Y}`
- Unwrap `UblDate {localDate: "X"}` → `"X"`
- Rewrap `taxScheme.id` plain → `{value: "VAT"}` for Pint
- Unwrap `additionalDocumentReference[].id` `{value: "ICV"}` → `"ICV"`
- Rewrap `note` plain → `{value: "..."}` (Pint Note shape)
- Add `customizationID` from context.yaml

Do NOT flatten: `additionalDocumentReference.id`, `partyIdentification.id`, `billingReference[].billDocumentReference.id`, `paymentMeansCode.value` — these stay nested.

### Local namespace config workaround
**Memory:** Vault row #18 + Session 3 lines 425–428.

The library-shipped `sample-xml-namespace-configs.json` has `_comment` fields that the library's own Jackson rejects. Workaround: clean local copy at `einvoice-<cc>/src/test/resources/<cc>/xml-namespace-configs.json` with only `UBL_INVOICE` and no `_comment` fields. E2E test reflection-injects an `XmlNamespaceConfigRegistry("<cc>/xml-namespace-configs.json")` into the production `JsonValidationProcessor`.

### Test harness details
- **No `@SpringBootTest`** — instantiate `JsonValidationProcessor` directly, reflection-inject `nsConfigRegistry`, leave `schemaRegistryService` null (unused on the JSON-input path).
- **XMLUnit `assertj3`** for XPath: `at(xml).valueByXPath("/inv:Invoice/cbc:InvoiceTypeCode/@name").isEqualTo("012")`.
- **No-null-leaks sanity check** runs every fixture and asserts XML doesn't contain `="null"` or `>null<`. Regression trap for missing `skipIfEmpty`.
- **`LocalDateTimeSchemaMapping` test stub** — production has copies in `einvoicing-workflow-consumer` and `einvoice-my`; einvoice-<cc> doesn't depend on those, so test classpath needs its own at `mapper/testsupport/`.

### Pom additions
- `einvoice-<cc>/pom.xml`: `schema-registry` (test) + `xmlunit-assertj3:2.9.1` (test).
- `test-coverage-report/pom.xml`: add `einvoice-<cc>` runtime dep + the dto exclude from B15.

---

## D. Deployment / Vault config matrix

The 18-row matrix from Jordan log Session 2 Deployment Tracking. Substitute `{{CC}}`, `{{COUNTRY_NAME}}`, `{{PROVIDER_NAME}}` as appropriate. Each row: env var, vault path, env coverage, what to set, status.

| # | Item | Env var / Key | Vault path (guess) | Environments | Value | Notes |
|---|------|---------------|--------------------|--------------|-------|-------|
| 1 | Enable {{CC}} in deployment | `ENABLED_COUNTRIES` | `vault/einvoicing-core/{env}/ENABLED_COUNTRIES` | dev, qa, sandbox, prod | Append `,{{CC}}` to existing list | First request blocker. Without this, generate returns `UN-HD-1011 — Country {{CC}} is not enabled`. |
| 2 | {{PROVIDER_NAME}} client credentials | — | `vault/einvoicing/countries/{{CC}}/{customerId}/client-id`, `/secret-key` | prod primarily | Per-customer values from regulator portal | Stored per-device per customer. Model is `ClientCredentialSetting`. |
| 3 | {{PROVIDER_NAME}} encryption key | `{{CC}}_{{PROVIDER_NAME_UPPER}}_ENCRYPTION_KEY` | `vault/einvoicing-core/{env}/...` | all | AES key for encrypting Client-Id/Secret-Key in MDC | Used by `EInvoiceRouterClient.encryptHeaders()`. |
| 4 | Error events Kafka topic | `ERROR_EVENT_KAFKA_TOPIC` | `vault/einvoicing-core/{env}/...` | all | e.g. `einvoice_{{cc}}_error_events_topic_dev` per env | Used for ClickHouse analytics. |
| 5 | Error event schema path | `EINVOICE_{{CC}}_ERROR_EVENT_SCHEMA_FILE_PATH` | — | all | `event-streaming/einvoice-{{cc}}-error-event-schema.json` | File must exist in resources too. |
| 6 | **Schema registry source schema** | `EINVOICE_DB_TEMPLATE_SCHEMA_{{CC}}` | — | all | Schema ID for source of Pint→UBL mapping | Registered in Schema Registry service. **Note B12 in playbook — many countries reuse `_MY` instead.** |
| 7 | Schema registry destination schema | `EINVOICE_{{CC}}_SCHEMA` | — | all | Schema ID for target ({{REGULATOR}} UBL XML) | Registered in Schema Registry service. |
| 8 | Data Browser tenant config | — | Data Browser config DB | all | Logical `EINVOICE_{{CC}}` + DB `EINVOICE_{{CC}}_ERROR_EVENT`, OR reuse `EINVOICE_GLOBAL` with country filter | clear-data-browser-be ticket. |
| 9 | CloudFront country→region map | — | CloudFront Function code | all | `'{{CC}}': 'me-origin'` (or appropriate region) | Instant propagation via JS function update. |
| 10 | Ingestion-overlord schema | `EINVOICE_{{CC}}` tenant + `SCHEMAS/EINVOICE_{{CC}}/V1/` + `SCHEMA_MAPPINGS/EINVOICE_{{CC}}/V1/` | — | all | Upload schema + mapping files | ingestion-overlord ticket. |
| 11 | clear-routing {{PROVIDER_NAME}} base URL | `{{PROVIDER_NAME_UPPER}}_BASE_URL` | `vault/clear-routing/{env}/...` | all | regulator API URL | clear-routing PR introduces this. |
| 12 | clear-routing {{PROVIDER_NAME}} mock toggle | `{{PROVIDER_NAME_UPPER}}_MOCK_ENABLED` | `vault/clear-routing/{env}/...` | dev, qa, sandbox | `true` if no regulator sandbox | Use mock client. |
| 13 | clear-routing {{PROVIDER_NAME}} enabled toggle | `{{PROVIDER_NAME_UPPER}}_ENABLED` | `vault/clear-routing/{env}/...` | all | `true` | Pre-merge checklist mentions this. |
| 14 | **{{CC}} mapping file in classpath-registered list** | `SCHEMA_MAPPING_FILE_PATHS` (yaml `schema-registry.schemaMappingFilePaths`) | `vault/einvoicing-core/{env}/SCHEMA_MAPPING_FILE_PATHS` | dev, qa, sandbox, prod | **Append** `,SchemaMapping/{{CC}}/Sales{{COUNTRY_NAME}}To{{PROVIDER_NAME}}Xml.json` to existing list | **Hardcoded whitelist** — the jar has the file but `SchemaMappingRepository` only loads files named here. Jordan log Session 4 row #14: discovered when curl returned `UN-HD-1010 — Schema mapping not present with key …`. |
| 15 | {{CC}} XSLT validator config | yaml `schema-validation.validationConfig` | `vault/einvoicing-core/{env}/SCHEMA_VALIDATION_CONFIG` | all | Add {{CC}} entry pointing to `validation/{{CC}}/{{CC}}-validation.xslt` | Non-blocking but pre-submit validation off until added. |
| 16 | `CurrencyMappingUtil` {{CC3}}→{{CURRENCY_3LETTER}} entry | Platform library config | Platform-lib resource | all | Map 3-letter country enum → 3-letter currency code | Non-blocking warning. File ticket against platform-lib team. |
| 17 | `CustomPlatformPreProcessor` country→resource map | platform-auth-licensing library | Platform-lib config | all | Add {{CC}} entry for audit/metering resource-name | Non-blocking. File ticket against platform-auth team. |
| 18 | **{{PROVIDER_NAME}} namespace config** (UBL) | jar-bundled `sample-xml-namespace-configs.json` (has `_comment` fields that break Jackson) | NA (library fix) | all | Library's shipped config needs `_comment` removed OR Jackson should ignore unknowns | **Workaround:** local clean copy at `einvoice-{{cc}}/src/test/resources/{{cc}}/xml-namespace-configs.json`. Confirm whether prod schema-validation parses OK or silently falls back. |

Plus per-country `application-<env>.yml` entries:
- `deployment.enabled-countries`: append `{{CC}}`
- `schema-registry.schemaMappingFilePaths`: append the mapping file path (mirror env-var row #14)
- Kafka topic name overrides for the country's error events (row #4)
- `routing.countryRouterServiceMap` (clear-routing yml): append `"{{CC}}":"{{PROVIDER_NAME_UPPER}}"`. Row #20 in Jordan log — without this, clear-routing's `RoutingFactory` falls through to default LHDN.

**First-ask-Ops minimum (to unblock dev curl):** rows #1, #14, #11–#13, #20.

**Pre-prod blocking:** rows #1, #3, #11, #14, #15, #19 (licensing per-customer), #20.

---

## E. Build wiring (6-repo) — TODOs out of MVP scope

This skill ships only the einvoice-<cc> module. The broader 6-repo onboarding work needs separate tracking.

### einvoicing-core (this skill's MVP — covered)
- Create `einvoice-<cc>/` module (GovtActionService, SalesCtActionService, WorkflowInitiator, DTOs)
- Add to parent pom, application pom, enabled-countries
- Add CC to `@ConditionalOnCountry` on `EInvoiceDefaultSalesGenerationService`
- DB-interactions JSON configs (`{CC}/EinvoiceFieldWithDBPath.json`, `EinvoiceFieldWithDbOptions.json`)
- XSLT/Schematron validation files in `validation/{CC}/`
- Schema registry mapping files
- Unit + integration tests

### clear-routing — TODO
- Create `clear-{vendor}/` module (Client, Endpoint, RoutingService, ActionHandlers, Config)
- Add `{VENDOR}` to `RoutingService` enum
- Wire in `RoutingFactory`
- Add `{VENDOR}` to `Region` enum if needed
- Circuit breaker config
- Application YAML per environment (incl. `countryRouterServiceMap` row #20)
- MDC header forwarding via `ContextFieldName` (Jordan added `JOFOTARA_CLIENT_ID` etc.)

### einvoicing-integrations — TODO (if custom API needed)
- Country module with controller, service, client, DTOs
- Schema mapping file paths

### clear-data-browser-be — TODO
- Tenant registration (logical + DB)
- Country-specific SQL queries, projection templates, report templates
- Localization (date/time format, currency)

### ingestion-overlord — TODO
- Schema files (`SCHEMAS/EINVOICE_{CC}/V1/`)
- Schema mappings (`SCHEMA_MAPPINGS/EINVOICE_{CC}/V1/`)
- Tenant enum entry
- Template mapper, validation rules

### Infrastructure — TODO
- CloudFront Function: add `{CC} → {REGION}` mapping
- Vault secrets for govt credentials (rows #2, #3)
- Kafka topics for error events (row #4)
- Monitoring dashboards + alarms

### clear-sales (shared models) — TODO if model gaps
- New fields on `ClientCredentialSetting` (Jordan added `incomeSourceSequence`, `deviceId`)
- New `GovtResponse` fields if regulator returns extra data
- Coordinate with whoever owns NV-265-style model tickets

---

## F. Open-question template (for the consultant)

Generated to `data/onboarding/<cc>/open_queries.md`. The user hands this to the regulator's consultant (Avtax, KPMG, Deloitte, …) and updates the playbook when answers come back.

```markdown
# Open Queries — <Country> e-invoicing

Authoritative source for spec conflicts between PRD / consultant xlsx / regulator portal / open-source SDK.

## Spec conflicts (PRD vs SDK)

1. **Authentication failure HTTP code.** PRD says X; SDK says Y. Confirm authoritative answer.
2. **Retry policy.** PRD prescribes [a, b, c] seconds; consultant communication on Slack mentioned [d, e, f]. Confirm.
3. **Tax-category enum ID for "Out of scope" / "Exempt".** PRD vs SDK vs UN/ECE 5305 — confirm semantic mapping.

## Edge cases for special sales / non-standard documents

4. **Special-sales tax shape.** Slide deck says no line tax; tech mapping has OTH scheme wired. To-be-tested?
5. **Line-vs-document AllowanceCharge.** Consultant doubt — confirm where allowances live.
6. **Unit of measure.** Default `PCE`; other UN/ECE 21 codes — supported?

## Currency on amount elements

7. **3-letter (header) vs 2-letter (amount-element `currencyID`).** Confirm regulator's own validator parses both correctly.
8. **Foreign-currency invoices.** Cross-currency handling (`TaxCurrencyCode` ≠ `DocumentCurrencyCode`).

## Sub-type field requirements

9. **Mandatory fields per sub-type.** Buyer name + buyer ID + ID type — confirm matrix against PRD §X.
10. **Threshold rule.** Cash invoice >X (currency) triggers buyer-ID requirement — confirm threshold + currency.

## Signature handling

11. **Server-side vs client-side signing.** Confirm regulator signs server-side; client sends unsigned envelope.
12. **Signed XML retention.** Min retention period per regulator mandate.

## Retry policy

13. **Retryable HTTP codes.** Confirm: 429, 502, 503, 504. NOT retryable: 400, 401, 403 (auth), REJECTED.
14. **Idempotency.** On retry of REJECTED, regulator expects fresh UUID v4 vs same UUID? (Jordan: fresh UUID, ID stays.)

## Sandbox availability

15. **Sandbox endpoint.** Yes/no. If no, mock-client strategy + production-only debug protocol.
16. **Test taxpayer credentials.** Provided by regulator? Self-provisioned?

## Document-fetch / cancel APIs

17. **Cancel API.** Available? Or only credit-note model?
18. **Status fetch / GET.** Available? Or response-only on submit?

## Buyer / customer rules

19. **Foreign buyers.** Country code 2-letter only? CountrySubentity omitted?
20. **Buyer Name on exports.** Mandatory? Optional?

## Reference resources

21. **Regulator portal URL** (admin) and **API base URL** (machine).
22. **Reference XML samples folder.** Drive folder URL with regulator-blessed sample XMLs.
23. **Reference open-source SDKs.** PHP / Odoo / etc. Used to triangulate spec ambiguities.
```

User edits this file as answers come back; running `init` again ingests the answers and updates `context.yaml`.

---

## G. Resume points

When picking up a country onboarding mid-flight:
1. Read `data/onboarding/<cc>/context.yaml` — confirms what's already gathered.
2. Check `data/onboarding/<cc>/output/` directory listing — see which artifacts exist.
3. Read `data/onboarding/<cc>/open_queries.md` — what's still pending consultant answer.
4. Read this playbook for the conventions.
5. Re-run any of the 6 modes; each is idempotent (will overwrite its output).

---

*Playbook seeded from Jordan onboarding (Apr 2026). Update with new gotchas after each country.*
