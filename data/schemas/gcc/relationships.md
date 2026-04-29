# GCC Metabase — Table Relationships & Semantics

Knowledge map: what each table stores, how tables relate, what columns mean. Use this with `tables/*.yaml` (column lists) and `gotchas.md` (engine pitfalls) to compose SQL for any new incident — never copy a frozen query.

## Two engines, two roles

| | Postgres `einvoices_gcc` | ClickHouse `einvoicing_gcc_analytics` |
|---|---|---|
| Role | Operational/source mirror | Analytics layer (RCA primary) |
| Naming convention | camelCase (quote in SQL) | snake_case |
| Time storage | `timestamp with time zone` (or `text` for legacy) | `DateTime` / `DateTime64`, UTC |
| Use for | Workspace lookups, historical drill-downs, legacy `*_v1` / `old_*` mirrors | Incident analysis, audit-trail JOINs, time-windowed counts |

**When starting an RCA query, default to ClickHouse.** Cross to Postgres only for human-readable workspace lookups (gstin → name).

---

## Layer 1 — Customer-visible HTTP

### `api_details_v2`

Lives in **both** engines (different col conventions). Stores **one row per API call** hitting the e-invoicing service. This is the "what did the customer see?" view.

Key columns (ClickHouse, snake_case):

| Column | Meaning |
|---|---|
| `unique_identifier` | Per-invoice client-supplied key (PG: `uniqueIdentifier`) |
| `status` | HTTP status as String: `'200'`, `'400'`, `'500'` |
| `created_at` | `DateTime64(6)`, UTC |
| `analytics_event_name` | Endpoint identifier — see enum below |
| `ct_error` | `Bool`, true if ClearTax detected the error (vs. regulator) |
| `error`, `message`, `warning_message` | Free-text error explanations |
| `time_taken`, `non_nic_time_taken`, `non_nic_platform_time_taken` | Latency in ms |
| `pan`, `gstin`, `branch` | Workspace identification (raw, may be null) |
| `request_id`, `span_id` | Trace correlation |

`analytics_event_name` enum values (from KSA RCA — extend by `SELECT DISTINCT analytics_event_name`):
- `_response_final` — sync `/v2/einvoices/generate`
- `_async_response_final` — async `/v2/einvoices/generate/async`
- `xml_response_final` — `/v2/einvoices/generate-with-file`
- `xml_offline_response_final` — `/v2/einvoices/generate-with-file-offline`
- `base64_offline_async_response_final` — `/v2/einvoices/generate-with-base64-offline/async`

### Workspace ID cascade (CH `api_details_v2`)

5 columns hold workspace mapping in priority order:
1. `workspace_id` — direct
2. `workspace_id_from_branch`
3. `workspace_id_from_gstin`
4. `workspace_id_from_pan`
5. **`workspace_id_fin`** — the final resolved value after the cascade. **Use this** for grouping. Others are backfill audit.

---

## Layer 2 — Mongo-mirrored invoice records

Two parallel tables, one per flow:

| Table | Flow | Endpoints feeding it |
|---|---|---|
| `einvoice_gcc` | **Online** | `/v2/einvoices/generate`, `/v2/einvoices/generate-with-file` |
| `eInvoice_gcc_metadata` | **Offline** | `/v2/einvoices/generate-with-file-offline`, `/v2/einvoices/generate-with-base64-offline*` |

Stores **one row per invoice** (not per attempt). Mongo-shape, mirrored to CH.

Key columns:

| Column | Meaning |
|---|---|
| `uniqueIdentifier` | Invoice key (camelCase, Mongo origin — even in CH) |
| `invoice_status` | Terminal state. Enum: `REPORTED` (B2C cleared by regulator), `CLEARED` (B2B cleared), `PENDING` (in flight), `FAILED` (regulator rejected), `DISCARDED` (we discarded), `NOT_SUBMITTED`, `NOT_REPORTED`, `NOT_CLEARED` |
| `taxpayerOrgId` | Workspace UUID |
| `taxpayerParentOrgId` | Parent org UUID |
| `created_at`, `updatedAt` | UTC |

For "what made it into our DB during the window?" — query these. **Always run both** and union. Picking just online OR offline silently misses half the impact in offline-heavy markets.

---

## Layer 3 — Audit trails

| Table | What it logs |
|---|---|
| `eInvoiceAuditTrail` | Each `invoice_status` transition (online + offline both write here) |
| `einvoiceexternalaudittrail` | Outbound regulator calls (ZATCA, JoFotara, etc.) — request/response, timing |

`eInvoiceAuditTrail` is the **terminal-state truth source**. An invoice has multiple rows; each row is a state-change event with `created_at`. To classify an invoice's final state for a window, take `argMax(invoice_status, created_at)` grouped by `uniqueIdentifier`.

`einvoiceexternalaudittrail` is the answer to "did this invoice reach the regulator?" If a row exists with success status, regulator received it.

---

## Layer 4 — Validation errors

| Table | Engine | Use |
|---|---|---|
| `aggregate_validation_errors` | CH | **Preferred for RCAs** — pre-aggregated by error code, time-bucketed |
| `validation_errors` | PG | Per-invoice raw validation failures (current schema) |
| `validation_error_v1` / `old_validation_errors` | PG | Legacy mirrors — don't query unless comparing pre/post a migration |

Key columns: `errorCode`, `errorMessage`, `errorSource`, `validationType`, `uniqueIdentifier`, `gstin`, `caller`.

These are **our own validation failures** (pre-regulator), not regulator-side rejections. For regulator rejections, look at `eInvoiceAuditTrail.invoice_status = 'FAILED'` joined with the audit-trail's error fields.

---

## Layer 5 — Workspace identity / lookup

For going from gstin/UUID/pan to a human workspace name:

| Table | Engine | Holds |
|---|---|---|
| `gstins` | PG | 15-digit gstin → workspace mapping, legal/trade names |
| `workspaces` | PG | workspace_id → name + billing details |
| `organisations` | PG | org-level metadata, `workspace_id` foreign |
| `gcc_client_list` | CH | gstin / vat / tin → org name (newer, denormalized) |
| `gcc_mapping` | CH | additional mapping layer (varies — check schema YAML) |

**Identifier mismatch**: same workspace appears under different keys across tables — `gstin` (15-digit), `taxpayerOrgId` (UUID), `pan` (10-digit). Always unify before reporting numbers to humans. The KSA Apr-27 RCA had this trip-up: top-10 by gstin and top-10 by UUID were different lists for the same workspaces.

---

## Common JOIN recipes

| Question | JOIN logic |
|---|---|
| "What terminal state did each 500 response end in?" | `api_details_v2` LEFT JOIN `(SELECT uniqueIdentifier, argMax(invoice_status, created_at) FROM eInvoiceAuditTrail WHERE created_at IN [window_start, window_end+10min] GROUP BY uniqueIdentifier)` ON `unique_identifier` |
| "Online vs offline split for an invoice list" | UNION ALL of `einvoice_gcc` + `eInvoice_gcc_metadata` on `uniqueIdentifier` |
| "Did this invoice reach the regulator?" | invoice record LEFT JOIN `einvoiceexternalaudittrail` on `uniqueIdentifier` — non-null success row = reached |
| "What workspace does this gstin map to?" | CH `api_details_v2` ⨝ PG `gstins` — cross-engine, requires CSV export from CH then PG join, or use `gcc_client_list` (CH-side gstin lookup) if it has the gstin you need |
| "Customer retries during incident" | `api_details_v2` self-join on `unique_identifier` where one side has status='500' and other has status='400' with message LIKE 'already approved' |

When composing for a new incident, **identify the question first**, then map to one of the above layers, then compose the SQL using the column names from `tables/*.yaml`. If the question doesn't fit a recipe, write SQL fresh — relationships in this doc are guidance, not a closed list.

---

## Time windows — always

- Convert IST → UTC at the WHERE clause boundary: `WHERE created_at >= toDateTime('2026-04-27 14:21:00', 'UTC')`
- For `eInvoiceAuditTrail` joins, extend the window by 10 minutes — audit rows can settle after the HTTP response is logged.
- Verify with `Q-tz` style probe (see `gotchas.md` §3) before any time-windowed query if you haven't run one in this session.

---

## What this knowledge enables

For a new incident — say "30-min Sev2 in UAE, ~200 invoices throwing 500s" — the agent:

1. Identifies the question(s): impact count, terminal classification, top affected workspaces, regulator-side verification.
2. Maps to layers: HTTP-side (`api_details_v2`) → DB-side (`einvoice_gcc` + `eInvoice_gcc_metadata`) → audit-trail (`eInvoiceAuditTrail`) → workspace lookup.
3. Writes SQL grounded in **this incident's window**, **this incident's affected endpoints**, **this incident's regional filter** — not by tweaking some old KSA query.
4. Cites tables inline in the RCA Impact section: e.g., "1,234 of 200 invoices terminally REPORTED despite 500 response (api_details_v2 ⨝ eInvoiceAuditTrail, window 14:30-15:00 UTC)".

That's the goal. Schema + relationships + gotchas → any incident's queries.
