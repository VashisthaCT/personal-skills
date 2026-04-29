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

## 13. Audit trail JOIN — the right one

Q11 (definitive bucket distribution) JOINs `api_details_v2` on `trace_id`/`requestId` to `eInvoiceAuditTrail.invoice_status`. Multiple audit-trail rows per invoice — take the **latest** by `created_at`, not the first. Otherwise you count transient PENDING states as terminal.

## 14. `analyticsEventName` enum values

Maps customer-side endpoint to action. From KSA RCA Q4b, the values that appear:
- `_response_final` — sync `/v2/einvoices/generate`
- `_async_response_final` — async `/v2/einvoices/generate/async`
- `xml_response_final` — `/v2/einvoices/generate-with-file`
- `xml_offline_response_final` — `/v2/einvoices/generate-with-file-offline`
- `base64_offline_async_response_final` — `/v2/einvoices/generate-with-base64-offline/async`

(Not exhaustive. Run `SELECT DISTINCT "analyticsEventName" FROM api_details_v2 LIMIT 100` to refresh.)
