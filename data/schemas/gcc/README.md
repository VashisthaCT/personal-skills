# GCC Metabase Schemas

Schema reference for the two OCI Metabase databases that back **GCC region** RCAs and incident queries.

## Databases

| Metabase connection | Actual DB name | Engine | Role |
|---|---|---|---|
| `einvoices_gcc` | `einvoices_gcc` | **PostgreSQL** | Operational/source mirror — accounts, branches, contacts, monthly metrics partitions, legacy `*_v1` / `old_*` tables |
| `einvoicing-gcc-analytics` | `einvoicing_gcc_analytics` | **ClickHouse** (Altinity 24.3) | Analytics layer — Mongo-mirror collections, audit trails, the canonical RCA query target |

Note the hyphen ↔ underscore mismatch: Metabase displays `einvoicing-gcc-analytics`, but the actual ClickHouse database is `einvoicing_gcc_analytics`. Use the underscore form in `FROM` / `DESCRIBE` clauses.

The KSA Apr-27 RCA's Q1-Q12 queries all hit the ClickHouse side. Postgres is mostly used for workspace ↔ org lookups and historical metric drill-downs.

## Layout

```
data/schemas/gcc/
├── README.md                              ← this file
├── tables/
│   ├── einvoices_gcc.yaml                 ← Postgres, 39 tables (extracted 2026-04-30)
│   └── einvoicing_gcc_analytics.yaml      ← ClickHouse, 42 tables (extraction pending)
├── relationships.md                       ← JOIN keys, identifier mismatches (gstin ↔ UUID)
├── query_patterns.yaml                    ← Q1-Q12 from KSA RCA, parameterized
└── gotchas.md                             ← TZ=UTC, camelCase quoting, online-vs-offline split
```

## Refresh recipe

### Postgres (`einvoices_gcc`)
Run in Metabase, download as CSV, drop in `~/Downloads/`:
```sql
SELECT
  table_schema, table_name, column_name, data_type,
  ordinal_position, is_nullable, column_default
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name, ordinal_position;
```

Then run the parser:
```bash
python3 ~/dev/personal-skills/data/schemas/gcc/parse_csv_to_yaml.py \
  ~/Downloads/<csv-file>.csv \
  ~/dev/personal-skills/data/schemas/gcc/tables/einvoices_gcc.yaml \
  einvoices_gcc postgresql
```

### ClickHouse (`einvoicing_gcc_analytics`)
Run in Metabase against the `einvoicing-gcc-analytics` connection:
```sql
SELECT
  database, table, name AS column_name, type, comment, position,
  is_in_primary_key, is_in_partition_key
FROM system.columns
WHERE database = 'einvoicing_gcc_analytics'
ORDER BY table, position;
```

If `system.columns` is denied for your user, fall back to per-table `DESCRIBE TABLE einvoicing_gcc_analytics.<name>;` and concatenate.

## Refresh cadence

Manual. Re-run when:
- An RCA query hits an unknown column ("ah, that table got a new field")
- A new monthly partition appears (`einvoice_gen_metrics_2026_04` etc.)
- Quarterly check at minimum

Last refreshed: see top comment in each `tables/*.yaml`.

## Consumers

These files are read by:
- `/v-rca` — when drafting Impact / data-source sections of RCAs
- `/v-incident` — when scaffolding query templates for a live Sev1
- `/v-metabase-schema` (planned) — explicit-invoke "what cols in table X"

When citing a metric in an RCA, **always name the source table inline** (Apoorva-tier preempt). E.g. "Q11 against `einvoicing_gcc_analytics.api_details_v2`".
