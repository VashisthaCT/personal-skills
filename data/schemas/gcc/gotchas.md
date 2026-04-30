# GCC Metabase — Gotchas

Things that have burned us before. Read before writing any RCA query.

## 1. Two databases, two engines

- `einvoices_gcc` is **PostgreSQL** — `SHOW TABLES FROM x` won't work; use `information_schema`. Permissions are looser; `information_schema.columns` works.
- `einvoicing_gcc_analytics` is **ClickHouse** (Altinity 24.3) — `information_schema.columns` is grant-locked for the BI user; `system.columns` works only with the correct DB name.

## 2. Metabase display name ≠ actual DB name

Metabase shows `einvoicing-gcc-analytics` (hyphens). The actual ClickHouse database is `einvoicing_gcc_analytics` (underscores). Use the underscore form in SQL. Hyphenated form will throw `Code: 81. Database does not exist`.

## 3. Timezone storage

ClickHouse `api_details_v2`, audit trails: stored in **UTC** (`DateTime64`). Convert IST → UTC before filtering. Verify with:
```sql
SELECT now() AS now_raw, toTimeZone(now(), 'UTC') AS now_utc
-- now_raw should equal now_utc → confirms UTC storage
```
(This is `Q-tz-final` from KSA RCA memory.)

Postgres `created_at` columns: many are `timestamp with time zone` (TZ-aware) but a worrying number are `text` (string-stored, ambiguous). When in doubt, check the column type before filtering.

## 4. Postgres camelCase columns require double-quotes

Postgres folds unquoted identifiers to lowercase. Tables like `api_details_v2` have columns `userId`, `uniqueIdentifier`, `analyticsEventName`, `requestUserAgent` etc. that were created with quotes. To query them you MUST also quote:
```sql
SELECT "userId", "uniqueIdentifier", "analyticsEventName"
FROM api_details_v2
WHERE "ctError" = true;
```
Forgetting the quotes returns `column "userid" does not exist`.

## 5. Two tables that need quoting

- `Sf_customer_data` (capital S) → use `"Sf_customer_data"`
- `table` (literal SQL reserved word) → use `"table"`

## 6. api_details_v2 exists in BOTH databases — with DIFFERENT naming conventions

Two physical tables, different engines, different schemas, **different column naming conventions**:

| | Postgres `einvoices_gcc.api_details_v2` | ClickHouse `einvoicing_gcc_analytics.api_details_v2` |
|---|---|---|
| Naming | camelCase (`userId`, `uniqueIdentifier`, `timeTaken`, `analyticsEventName`) | snake_case (`user_id`, `unique_identifier`, `time_taken`, `analytics_event_name`) |
| Column count | 50 | varies — see `tables/einvoicing_gcc_analytics.yaml` |
| Quote required | Yes (camelCase forces double-quotes) | No (snake_case is unquoted-safe) |
| Used for | Raw mirror, less-common drill-downs | **The primary RCA target** — Q4b, Q11 hit this one |

**Never copy-paste a column reference between engines.** Same logical field has two names. The KSA RCA queries use the ClickHouse snake_case form throughout.

## 7. Workspace identifier mismatch

Same workspace appears under different keys across tables:
- `einvoices_gcc.gstins.gstin` — 15-digit GCC tax ID (used in online flow)
- `einvoices_gcc_data_v3.taxpayerOrgId` — UUID (used in offline flow)
- `gcc_client_list.tin` / `gcc_client_list.vat` — yet another set

KSA RCA Q6a (gstin) and Q6b (UUID) returned overlapping workspace counts. Always JOIN through `gstins` or `gcc_client_list` to unify before customer outreach.

## 8. Online vs offline invoice split

Two parallel collections (Mongo-mirrored as ClickHouse tables):
- `einvoice_gcc` — online flow (sync `/v2/einvoices/generate`)
- `eInvoice_gcc_metadata` — offline flow (`/v2/einvoices/generate-with-file-offline`, `/generate-with-base64-offline`)

Different `invoice_status` enum values may appear. Different lifecycle. Always run impact queries on **both** and union the results — never pick one and assume coverage.

## 9. Monthly partition tables

`einvoices_gcc` has 9 partitioned monthly metric tables (`einvoice_gen_metrics_2021_12` through `_2022_08`) plus `_def`. These all share a 20-col schema. Use `einvoice_generation_metrics` (the rolling/current view) for time-spanning queries, not the partitioned tables.

## 10. Legacy `old_*` and `*_v1` tables

Tables prefixed `old_` or suffixed `_v1` are deprecated mirrors. Don't query them in new RCAs unless explicitly comparing pre/post a migration. They drift from current schema.

## 11. Metabase row truncation

Metabase UI caps results at 2000 rows by default. Always click **"Download full results" → CSV** (the cloud-with-arrow icon) — NOT "Export visible rows" — when extracting for analysis. Otherwise half your data is silently missing.

## 12. ClickHouse `DateTime64` vs `DateTime`

`api_details_v2.created_at` may be `DateTime` (second precision) or `DateTime64(3)` (millisecond precision) depending on table version. Use `toUnixTimestamp()` for consistent epoch math; don't compare DateTime to DateTime64 directly without casting.

## 13. `eInvoiceAuditTrail` is NOT a terminal-state source

It's tempting to think of `eInvoiceAuditTrail` as "the table that records every invoice_status transition". It's not. The table has columns `traceId`, `spanId`, `request`, `response`, `auditType`, `operation`, `entity`, `gstinOrgId`, `panOrgId`, `branchOrgId` — **no `invoice_status`, no `unique_identifier`** at the column level. The invoice key and status are inside the `request`/`response` JSON payloads (String columns).

For terminal invoice state, JOIN through `einvoice_gcc.status` (online) or `eInvoice_gcc_metadata.status` (offline) using `unique_identifier` / `uniqueIdentifier`. See `relationships.md` Common JOIN recipes.

For invoice-level state-change history (offline only): `eInvoices_gcc_metadata_status` exists as a dedicated state-transition table — has `uniqueIdentifier`, `status`, `einvoiceStatus`, `createdAt`, `updatedAt`. Use `argMax(status, updatedAt) GROUP BY uniqueIdentifier` to get the latest state per invoice.

Use `eInvoiceAuditTrail` when you actually need the **full request/response payload** for a `traceId` — debugging what the customer sent, what we returned, what the regulator said.

## 14. `analyticsEventName` enum values

Maps customer-side endpoint to action. From KSA RCA Q4b, the values that appear:
- `_response_final` — sync `/v2/einvoices/generate`
- `_async_response_final` — async `/v2/einvoices/generate/async`
- `xml_response_final` — `/v2/einvoices/generate-with-file`
- `xml_offline_response_final` — `/v2/einvoices/generate-with-file-offline`
- `base64_offline_async_response_final` — `/v2/einvoices/generate-with-base64-offline/async`

(Not exhaustive. Run `SELECT DISTINCT "analyticsEventName" FROM api_details_v2 LIMIT 100` to refresh.)

## 15. Within-ClickHouse naming inconsistency (online snake_case vs offline camelCase)

Even within the same ClickHouse database (`einvoicing_gcc_analytics`), Mongo-mirrored tables don't share a naming convention. The pipelines that mirrored each Mongo collection preserved different cases:

| Concept | `einvoice_gcc` (online) | `eInvoice_gcc_metadata` (offline) |
|---|---|---|
| Invoice key | `unique_identifier` | `uniqueIdentifier` |
| Workspace UUID | `taxpayer_org_id` | `taxpayerOrgId` |
| Created / updated | `created_at` (snake) | `createdAt` / `updatedAt` (camel) |

**Implications for queries:**

A union across online + offline needs explicit column aliasing:
```sql
SELECT unique_identifier AS inv_id, status FROM einvoice_gcc WHERE created_at >= ...
UNION ALL
SELECT uniqueIdentifier  AS inv_id, status FROM eInvoice_gcc_metadata WHERE createdAt >= ...
```

A JOIN from `api_details_v2.unique_identifier` to the offline table needs cross-naming:
```sql
... LEFT JOIN eInvoice_gcc_metadata meta ON api.unique_identifier = meta.uniqueIdentifier
```

When unsure, `DESCRIBE TABLE einvoicing_gcc_analytics.<name>` before writing the JOIN. The column YAML at `tables/einvoicing_gcc_analytics.yaml` is the canonical reference.
