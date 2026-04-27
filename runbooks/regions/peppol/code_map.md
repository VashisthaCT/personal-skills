# Peppol Code Map

Repos × files implementing the EUSR/TSR pipeline as of Apr 2026.

## Repos

| Repo | Path on Desktop | Role |
|---|---|---|
| `clear-peppol-ap` | `~/Desktop/clear-peppol-ap` | Peppol AP — Oxalis, AS4, EUSR/TSR generation, transactions. |
| `einvoicing-be` | `~/Desktop/einvoicing-be` | Indirect — feeds documents to AP. |
| `clear-routing` | `~/Desktop/clear-routing` | `clear-peppol/` vendor module for outbound. |

## clear-peppol-ap — three components

### Component A: PR #156 (`save_vat_in_transactions_collection`) — MERGED to main 2026-04-23

Saves sender/receiver tax IDs on new transactions during document processing.

| File | Lines | Purpose |
|---|---|---|
| `clear-ap-common/.../utils/CoreProcessingUtils.java` | +47 | `getSenderTaxIdentifierFromDocument()` / `getReceiverTaxIdentifierFromDocument()` using `getElementValueFromXml`. |
| `clear-ap-common/.../models/TransactionEntity.java` | +2 fields | `senderTaxId` / `receiverTaxId`. |
| `clear-ap-common/.../mappers/TransactionUpdateMapper.java` | +7 | Calls extraction ONLY for `INVOICE` || `CREDIT_NOTE` — needs broadening to `EINVOICE_DOCUMENT_TYPES`. |
| `TransactionUpdateMapperTest.java` | +172 | Test coverage. |
| `CoreProcessingUtilsTest.java` | +535 | Test coverage. |

PR #156 review notable points:
- Refactored to use existing `getElementValueFromXml` (was custom DOM parsing).
- Removed unused `docElementName` param.
- Catch logging upgraded `debug` → `warn`.
- `VatNumber` → `TaxIdentifier` / `TaxId` rename for semantic correctness.
- Removed VAT-preference logic — first `PartyTaxScheme/CompanyID` wins.
- 95%+ coverage on new lines.
- Pre-existing XXE vuln in `DocumentBuilderFactory` flagged, deferred.

### Component B: `backfill_country_codes_e2e.py` (Desktop)

`/Users/vashistha.garg/Desktop/backfill_country_codes_e2e.py` (~36 KB, last modified 2026-04-05).

Backfills `senderCountry`, `receiverCountry`, `senderTaxId`, `receiverTaxId` for historical transactions.

- Cursor-based pagination (`_id > last_seen`).
- Idempotent reruns; selective field updates (preserves existing data).
- Permanent vs transient error handling (S3 errors don't mark UNAVAILABLE).
- AWS SSO refresh every 50 batches; auto-login on expiry.
- `PartyLegalEntity/CompanyID` fallback matches Java exactly.

QA result with old field names: 118,186 records, 0 errors, ~12h runtime. Re-run needed with new field names + self-billed types.

### Component C: `feat/peppol_report_automation` branch — 24 uncommitted files

| File (new) | Purpose |
|---|---|
| `application/.../controller/ReportController.java` | REST: `POST /internal/reports/generate`, `GET /internal/reports/status`. |
| `clear-ap-common/.../models/ReportSubmissionEntity.java` | Mongo doc for tracking idempotency. |
| `clear-ap-common/.../repository/ReportAggregationRepository.java` | Interface. |
| `clear-ap-common/.../repository/impl/ReportAggregationRepositoryImpl.java` | TSR + EUSR Mongo aggregation pipelines. |
| `clear-ap-common/.../repository/ReportSubmissionRepository.java` | Submission tracking. |
| `clear-ap-common/.../services/ReportGenerationService.java` | Interface. |
| `clear-ap-common/.../services/impl/ReportGenerationServiceImpl.java` | Pipeline orchestration. |
| `clear-ap-common/.../utils/ReportXmlBuilder.java` | TSR/EUSR XML builder with SBDH wrapper. |
| `clear-peppol-consumer/.../scheduler/ReportScheduler.java` | Cron scheduler. |
| `PEPPOL_REPORT_GENERATION_MANUAL.md` | Doc. |
| `docs/PEPPOL_REPORTING_AUTOMATION_PLAN.md` | Doc. |

| File (modified) | Purpose |
|---|---|
| `DocumentType.java`, `ClearAPConstants.java` | Constants. |
| `ConsumerApplication.java`, `ClearAPOutboundService.java` | Wiring. |
| `application-{dev,qa,prod,sandbox}.yml` | Config. |

**Files to EXCLUDE from PR (local dev artifacts):**
- `.DS_Store`
- `application/src/main/java/com/clear/ap/Main.java` — hardcoded local oxalis path.
- `application/src/main/resources/application-local.yml` — hardcoded dev DB creds.
- `clear-peppol-consumer/src/main/resources/application-local.yml`.

## Manual report scripts (Desktop)

- `/Users/vashistha.garg/Desktop/dbchanges/manual_eusr_report.py` — Python manual TSR/EUSR generator (used Jan-Mar 2026).
- `/Users/vashistha.garg/Desktop/backfill_country_codes_e2e.py` — backfill (Component B).

## PRs / merges

| PR | Repo | Owner | Status |
|---|---|---|---|
| #105 (self-billed types added) | clear-peppol-ap | Mayank Nagpal | Merged 2026-03-17 |
| #127 (EUSR/TSR base support) | clear-peppol-ap | Various | Merged 2026-02-11 |
| **#156** (`save_vat_in_transactions_collection`) | clear-peppol-ap | Vashistha | **Merged 2026-04-23** |

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_peppol_reporting.md` §4, §11, §12.
