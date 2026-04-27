---
name: v-country-onboard
description: Drive a new e-invoicing country onboarding (einvoice-<cc> module in einvoicing-core). Six modes — `init`, `parse-mapping`, `generate-mapper`, `generate-tests`, `generate-curls`, `checklist`. Reads regulator spec + consultant xlsx, produces draft schema mapping JSON + 50 mapper-layer tests + 93 E2E XML tests + curl docs + Vault config checklist. Drafts only — output to `data/onboarding/<cc>/output/`; user copies into einvoicing-core. Codifies every Jordan gotcha (Money wrapper, TaxCategory enum, country 2-letter, ICV UUID, skipIf cascade, customizationID, namespace config, etc.) so each new country takes hours not weeks. MVP scope: einvoice-<cc> module only; broader 6-repo orchestration (clear-routing, ingestion-overlord, etc.) tracked as TODOs.
---

You are running Vashistha's country-onboarding skill. The user is onboarding a new e-invoicing country (Jordan now, Egypt next, Oman after, …) into `~/Desktop/einvoicing-core`. Each onboarding repeats the same pattern; this skill codifies it.

## Operating principles

- **MVP-first.** Ship the einvoice-<cc> module first. Skip broader 6-repo work unless asked.
- **Drafts only.** All output lands in `~/dev/personal-skills/data/onboarding/<cc>/output/`. Never touch `~/Desktop/einvoicing-core/` or any source repo.
- **Cite the playbook.** Every Jordan-learned gotcha lives in `~/dev/personal-skills/prompts/country_onboarding_playbook.md`. Reference it; don't re-derive.
- **Surgical.** No features beyond what the user asked for. Don't generate scope outside the brief.
- **Don't `git commit` or `git push`.** User does both.

## Inputs

- `<mode>` (required): one of `init` / `parse-mapping` / `generate-mapper` / `generate-tests` / `generate-curls` / `checklist`.
- `<cc>` (required): 2-letter ISO country code. Lowercase. e.g. `jo`, `eg`, `om`.
- Mode-specific args below.

If `<cc>` does not match `[a-z]{2}`, abort with: `Country code must be 2-letter ISO lowercase (e.g. jo, eg, om).`

## Folder convention

```
~/dev/personal-skills/data/onboarding/<cc>/
├── context.yaml              # interview answers (mode init writes; other modes read)
├── field_mapping.yaml        # parsed from xlsx (mode parse-mapping writes)
├── enums.yaml                # parsed from xlsx
├── open_queries.md           # spec conflicts to ask consultant
└── output/
    ├── SalesEinvoiceTo<Provider>Xml.json     # draft schema mapping
    ├── SalesTo<Country>MapperTest.java       # draft 50-test skeleton
    ├── SalesTo<Country>EndToEndXmlTest.java  # draft 93-test skeleton
    ├── xml-namespace-configs.json            # local copy without `_comment` fields
    ├── curl-examples.html                    # 9 fixtures rendered as Pint-API curls
    └── vault-checklist.md                    # 18-row Vault config table
```

`<Provider>` = JoFotara, ZatcaEgypt, etc. (PascalCase). Read from `context.yaml.provider_name`.

## Mode 1 — `init <cc>`

Goal: gather every piece of context once, save to `context.yaml`, so subsequent modes auto-fill.

If `data/onboarding/<cc>/context.yaml` exists: ask whether to overwrite or amend. Default: amend.

If `data/onboarding/<cc>/field_mapping.yaml` already exists (from `parse-mapping`): pre-fill smart defaults from it before asking the user.

Conduct an interview using the 18+ questions in `prompts/country_onboarding_playbook.md` Section A. For each question:
1. State the question.
2. Show smart default if known (from field_mapping.yaml or playbook).
3. Wait for user response.
4. Record answer.

After every Jordan gotcha (Section B of the playbook), ask a confirm/correct question — e.g. "Confirm Money wrapper applies (Amount.value lives at value.value at DB level)? [Y/n]". Default Y means same-as-Jordan.

Write all answers to `data/onboarding/<cc>/context.yaml` with this top-level shape:

```yaml
country_code_2: <cc>           # e.g. jo
country_code_3: <cc3>          # e.g. JOR
country_name: <Name>           # e.g. Jordan
region: <Region>               # MEA / EU / SEA / LATAM
regulator: <Name>              # ISTD / ZATCA / FTA / ...
portal_url: <url>
api_endpoint: <url>
sandbox_available: <true|false>
provider_name: <PascalCase>    # JoFotara / ZatcaEgypt — used in file/class names
customization_id: <urn>        # e.g. urn:peppol:pint:billing-1@jo-1
auth_model: <oauth|static|per-device>
auth_failure_codes: [401, 403] # multiple if PRD/SDK conflict
retry_attempts: 3
retry_backoff: [5, 30, 120]    # seconds; PRD wins on conflict
timeout_seconds: 100
document_types: [388, 381]     # InvoiceTypeCode values
sub_types:                     # @name attribute matrix
  - {code: '011', desc: 'Cash Income Bill (Local)', payment_means: '10', has_vat: false, has_tax_total: false}
  ...
governorates:                  # if applicable; use HYPHEN not underscore (Jordan lesson)
  - {code: 'JO-AM', name: 'Amman'}
  ...
buyer_id_schemes:              # UBL @schemeID values
  - {ubl: 'TN', internal: 'TIN', desc: 'Tax Number'}
  - {ubl: 'NIN', internal: 'JO_NIN', desc: 'National ID'}
  - {ubl: 'PN', internal: 'PASSPORT', desc: 'Passport / Residence Permit'}
currency_amount_2letter: 'JO'  # currencyID attr on amount elements (PHP-SDK style)
currency_header_3letter: 'JOD' # DocumentCurrencyCode / TaxCurrencyCode
tax_categories:                # UN/ECE 5305
  - {id: 'S', desc: 'Standard rate', scheme: 'VAT'}
  - {id: 'Z', desc: 'Zero rated', scheme: 'VAT'}
  - {id: 'O', desc: 'Exempt', scheme: 'VAT'}
tax_schemes: ['VAT', 'OTH']    # OTH for Special Sales second subtotal
income_source_concept: <name>  # e.g. "Income Source Sequence" (Jordan); "Device ID" (KSA)
reference_xml_drive_folder: <url>
reference_sdk_urls:
  php: <url>
  odoo: <url>
open_queries: <count>          # number of spec conflicts to ask consultant
```

Then write the per-section open queries to `data/onboarding/<cc>/open_queries.md` using the template in playbook Section F.

Done message: print folder path + next-mode suggestion (`/v-country-onboard parse-mapping <cc> --xlsx <path>` or `generate-mapper <cc>`).

## Mode 2 — `parse-mapping <cc> --xlsx <path>`

Wraps `~/dev/personal-skills/scripts/parse_country_mapping.py`. Run:

```
python3 ~/dev/personal-skills/scripts/parse_country_mapping.py --country <CC> --xlsx <path>
```

(`<CC>` uppercase for the script.) Outputs:
- `data/onboarding/<cc>/field_mapping.yaml`
- `data/onboarding/<cc>/enums.yaml`
- `data/onboarding/<cc>/open_queries.md`

If the script complains about missing `openpyxl`, print the install command and abort:
```
pip3 install --user openpyxl
```

After success, suggest the user runs `init` next (or re-runs `init` to amend with the new defaults).

## Mode 3 — `generate-mapper <cc>`

Read `data/onboarding/<cc>/context.yaml` and `field_mapping.yaml`. If `context.yaml` is missing, abort with: `Run /v-country-onboard init <cc> first.`

Load template `~/dev/personal-skills/prompts/schema_mapping_template.json` and substitute placeholders:
- `{{COUNTRY_CODE_2}}` → context.country_code_2.upper()
- `{{COUNTRY_CODE_3}}` → context.country_code_3.upper()
- `{{COUNTRY_NAME}}` → context.country_name
- `{{PROVIDER_NAME}}` → context.provider_name
- `{{CUSTOMIZATION_ID}}` → context.customization_id
- `{{CURRENCY_3LETTER}}` → context.currency_header_3letter
- `{{CURRENCY_2LETTER}}` → context.currency_amount_2letter
- `{{REGULATOR_NAME}}` → context.regulator

Apply every gotcha from playbook Section B (Money wrapper, TaxScheme/TaxCategory plain, country 2-letter expression, ICV UUID via id.en, skipIfEmpty cascade, sourceSchemaName=_MY pattern, etc.).

Write to `data/onboarding/<cc>/output/SalesEinvoiceTo<Provider>Xml.json`.

Validate it parses as JSON. If it doesn't, abort and print the parse error.

Print: filename + line count + reminder *"Drafts only. Copy to `~/Desktop/einvoicing-core/einvoice-interface/src/main/resources/SchemaMapping/<CC>/` after review."*

## Mode 4 — `generate-tests <cc>`

Generate two Java test skeletons.

Read `prompts/mapper_test_template.java` and `prompts/e2e_xml_test_template.java`. Substitute placeholders:
- `{{COUNTRY_CODE_2}}` (lowercase, e.g. `jo`) → for resource paths
- `{{COUNTRY_CODE_2_UPPER}}` (e.g. `JO`) → for schema-name constants
- `{{COUNTRY_NAME_PASCAL}}` (e.g. `Jordan`) → for class names like `SalesToJordanMapperTest`
- `{{PROVIDER_NAME}}` (e.g. `JoFotara`) → for class names like `SalesToJoFotaraMapperTest`
- `{{PACKAGE}}` → e.g. `com.clear.einvoicing.<cc>.mapper`

Output both to `data/onboarding/<cc>/output/`. Naming:
- `SalesTo<Provider>MapperTest.java` (50-test skeleton — 5–6 representative methods + a comment block listing the remaining 44 test names to fill)
- `SalesTo<Provider>EndToEndXmlTest.java` (93-test skeleton — same shape, more E2E pipeline assertions)

Also generate `data/onboarding/<cc>/output/xml-namespace-configs.json` — clean copy of `sample-xml-namespace-configs.json` without `_comment` fields. Drop a 2-line note in the file header explaining the workaround (Jordan lesson — playbook Section C).

Print: file paths + reminder *"Use `~/Desktop/einvoicing-core/einvoice-jo/...` as a structural reference. Drafts only."*

## Mode 5 — `generate-curls <cc>`

Read `data/onboarding/<cc>/output/SalesEinvoiceTo<Provider>Xml.json` (must exist).

Generate 9 canonical fixtures (per Jordan pattern — see playbook Section C):
1. minimal-invoice — happy path, single sub-type
2. credit-note-with-buyer — 381 + BillingReference + PaymentMeans
3. customer-walkin — no PartyIdentification
4. customer-passport — PN scheme
5. customer-tin — TN scheme
6. credit-note-passport — 381 + PN buyer
7. ar-invoice — A/R sub-type
8. cash-multiline — multi-line + line discounts
9. invoice-with-discount — doc + line discount + AccountingContact

Inverse-transform DB shape → Pint API shape (Jordan lesson — playbook Section C "API shape vs DB shape transforms"):
- Unwrap MultiLingualString `{en: "X"}` → `"X"`
- Unwrap Money wrapper `{value: {value: X}, currencyID: Y}` → `{value: X, currencyID: Y}`
- Unwrap UblDate `{localDate: "X"}` → `"X"`
- Rewrap `taxScheme.id` plain → `{value: "VAT"}` for Pint
- Rewrap `note` plain → `{value: "..."}` (Pint Note shape)
- Add `customizationID: "<from context.yaml>"`

Render to `data/onboarding/<cc>/output/curl-examples.html` — self-contained HTML with copy buttons + collapsible cards (mirrors Jordan style — dark theme #1a1a2e, cyan #00d4ff accent). Each card title = reference XML filename. Headers baked in (workspace, country, node, auth token placeholders). Supplier `companyID` placeholder for user to override locally.

Print: file path + reminder *"Replace placeholder workspace/auth-token with real local values before testing."*

## Mode 6 — `checklist <cc>`

Read `data/onboarding/<cc>/context.yaml`. Generate `data/onboarding/<cc>/output/vault-checklist.md` from playbook Section D — the 18-row Vault config matrix. Substitute `{{CC}}`, `{{COUNTRY_NAME}}`, `{{PROVIDER_NAME}}`. For each row, also fill in any concrete values known from context (e.g. retry policy, base URL).

After the table, append a "Build wiring TODOs" section listing the broader 6-repo work (clear-routing vendor module, ingestion-overlord schema, clear-data-browser-be tenant, etc.) — these are out of MVP scope; the skill is just naming them so they're tracked.

Print: file path.

## Verifiable success criteria

- For each mode invocation, the expected output files exist at `data/onboarding/<cc>/output/` (or `data/onboarding/<cc>/` for `init` and `parse-mapping`).
- `context.yaml` has at least the 18 top-level fields listed above after `init`.
- Generated `SalesEinvoiceTo<Provider>Xml.json` parses as valid JSON.
- Generated Java test files have correct package + class name + at least one `@Test` method.
- No file is written outside `~/dev/personal-skills/data/onboarding/<cc>/`.
- No `git commit` / `git push`.

## Failure modes

- `data/onboarding/<cc>/` doesn't exist → mkdir on demand.
- `context.yaml` missing for non-init mode → abort with: `Run /v-country-onboard init <cc> first.`
- xlsx file missing for `parse-mapping` → abort with file-not-found error.
- openpyxl missing → print install command + abort.
- Template files missing under `prompts/` → abort with: `Repo template missing: <path>. Re-run repo setup.`
- User's xlsx has weird sheet names → script fuzzy-matches; if no match, prints sheet list and asks user to re-run with `--sheet-name`.

## Don't

- Don't write to `~/Desktop/einvoicing-core/` or any source repo. Drafts only, in `data/onboarding/<cc>/output/`.
- Don't `git commit` / `git push`.
- Don't auto-modify `.claude-plugin/plugin.json` — main agent registers the skill.
- Don't enumerate every Vault row from memory — read it from the playbook so updates flow through one file.
- Don't include real TINs or API secrets in any output. Use placeholders.
- Don't try to handle the broader 6-repo orchestration (clear-routing, ingestion-overlord, etc.) inline. Call them out in the checklist; mark as TODO.

## See also

- `~/dev/personal-skills/prompts/country_onboarding_playbook.md` — every Jordan gotcha + interview questions + Vault matrix
- `~/dev/personal-skills/prompts/schema_mapping_template.json` — schema mapping skeleton
- `~/dev/personal-skills/prompts/mapper_test_template.java` — mapper test skeleton
- `~/dev/personal-skills/prompts/e2e_xml_test_template.java` — E2E XML test skeleton
- `~/dev/personal-skills/scripts/parse_country_mapping.py` — xlsx parser
- `~/dev/personal-skills/runbooks/countries/jordan/` — reference seed (already populated)
- Memory: `project_jordan_einvoicing.md`, `jordan_implementation_log.md` — original incident sources
- Memory: `platform_architecture.md` §3, §11 — country pattern + 6-repo onboarding checklist
