# RCA — KSA customer-specific 502 spike on `/v2/einvoices/generate-with-file`

> **Note:** This is a `/v-rca` synthetic test invocation, not a real incident.
> Test scope: validate that the GCC schema files steer the agent to compose
> fresh, schema-grounded SQL for an incident shape that does NOT match prior
> RCAs (different gstin, different endpoint, 502 not 500, 30-min window).

> This is for Clear internal use only and not to be shared outside.

## Incident Title: 502 spike on `/v2/einvoices/generate-with-file` for gstin 310451897400003 (KSA)

**Date of occurrence:** 30/04/2026
**Date of review:** [TBD — test scenario]

### Incident Summary

> Between [HH:MM] and [HH:MM] IST on 30 Apr 2026, a single KSA customer (gstin `310451897400003`) saw a sustained 502 spike on `POST /v2/einvoices/generate-with-file` (analytics_event_name `xml_response_final`, online flow). No other customers affected. Whether the upstream regulator (ZATCA) was unhealthy or the 502 originated in our gateway is the central open question — see Impact section queries.

### Timeline Summary of Occurrence

**Incident Timeline:**
- **Incident Start Time:** ~09:54 IST (~04:24 UTC) — start of reported 30-min window
- **Incident Reported Time:** [TBD]
- **Customer Reported to Clear:** [TBD]
- **Incident Resolved:** [TBD — ongoing]
- **Clear Responded to Customer:** [TBD]
- **Total Duration:** ~30 min reported, full duration TBD

**Terminology Overview**
- **502 Bad Gateway:** HTTP status returned when an upstream/proxy received an invalid response from the next-hop server. Differs from 500 (server error inside the application) — 502 specifically indicates the failure was at the gateway/proxy boundary.
- **ZATCA:** Saudi Arabia's Zakat, Tax and Customs Authority — the regulator that clears B2B and reports B2C invoices for KSA.
- **`xml_response_final`:** `analytics_event_name` enum value in `api_details_v2` corresponding to the synchronous `/v2/einvoices/generate-with-file` endpoint (online flow with XML upload).
- **`ct_error`:** Boolean column in `api_details_v2`. `true` = ClearTax detected the error; `false` = error originated upstream (regulator, network).
- **gstin:** 15-digit Saudi tax registration number (KSA's analog to India's GSTIN).

### Background & System Overview

The endpoint `/v2/einvoices/generate-with-file` accepts a customer-provided signed XML invoice and forwards it to ZATCA for clearance (B2B) or reporting (B2C). The flow:

1. Customer POSTs signed UBL XML.
2. We validate, persist to `einvoice_gcc` (online collection) with `status = PENDING`.
3. We call ZATCA's clearance/reporting API.
4. Update `einvoice_gcc.status` to `REPORTED` / `CLEARED` / `FAILED` based on regulator response.
5. Return 200/4xx/5xx to customer.

A 502 response is unusual for this path — the application typically returns 200/400/500. 502 strongly suggests a gateway/proxy layer (LB, API gateway, or service-mesh sidecar) failing before the request reached the application — OR the application bubbling up an upstream 502 from ZATCA.

### Immediate Fix (Timeline Summary)

[TBD — test scenario, no fix executed]

### 30 Apr 2026 Timeline

- **~09:54 IST:** First 502 observed (per reported window start)
- **[TBD]:** Customer report received
- **[TBD]:** L2 escalation
- **[TBD]:** Mitigation applied

### Impact

***Which areas got impacted?***

[TBD pending Impact-Q1 results below]
- KSA, online flow (`xml_response_final`), single customer (gstin `310451897400003`)

***How many customers got impacted?***

- 1 unique workspace (single gstin reported)
- [TBD] total unique invoices failed in 30 min — see Impact-Q1
- [TBD] total call failures — see Impact-Q1

***How many tickets were raised in the system?***

[TBD]

***Other impact (if any)***

[TBD]

#### Data queries — composed from schema for THIS incident

All queries against `einvoicing_gcc_analytics` (ClickHouse, Altinity 24.3). Storage TZ: UTC. Window placeholder `[WINDOW_START_UTC]` / `[WINDOW_END_UTC]` — fill before running. For the reported 30-min window starting 09:54 IST: `WINDOW_START_UTC = '2026-04-30 04:24:00'`, `WINDOW_END_UTC = '2026-04-30 04:54:00'`.

##### Impact-Q1 — Confirm 502 spike scope; split by `ct_error` (regulator-side vs our-side)

```sql
-- Source: einvoicing_gcc_analytics.api_details_v2
-- Answers: how many 502s, was the error our-side (ct_error=true) or upstream (false)
SELECT
  status,
  ct_error,
  countDistinct(unique_identifier) AS distinct_invoices,
  count()                          AS attempts,
  toUInt32(avg(time_taken))        AS avg_ms,
  max(time_taken)                  AS max_ms
FROM einvoicing_gcc_analytics.api_details_v2
WHERE created_at >= toDateTime('[WINDOW_START_UTC]', 'UTC')
  AND created_at <  toDateTime('[WINDOW_END_UTC]',   'UTC')
  AND analytics_event_name = 'xml_response_final'        -- /v2/einvoices/generate-with-file
  AND gstin = '310451897400003'
GROUP BY status, ct_error
ORDER BY status, ct_error;
```

**Reading the result:**
- 502 row with `ct_error = true` → **our-side** failure (we logged + classified the error). Likely gateway/proxy issue, network blip to ZATCA, or our code surfacing upstream 5xx as 502.
- 502 row with `ct_error = false` → **regulator-side / unclassified**. Worth correlating with Impact-Q3.
- Compare `attempts` to `distinct_invoices` — high ratio means customer retried on the same invoice many times.

##### Impact-Q2 — Did any 502'd invoice persist to our DB? What terminal state?

```sql
-- Source: einvoicing_gcc_analytics.api_details_v2 ⨝ einvoice_gcc (online collection)
-- Answers: of the 502 responses, how many invoices reached PENDING/REPORTED/CLEARED/FAILED
-- NOTE: einvoice_gcc uses snake_case unique_identifier; matches api_details_v2.unique_identifier.
SELECT
  coalesce(inv.status, 'no_record') AS terminal_status,
  countDistinct(api.unique_identifier) AS invoices,
  count() AS http_500_attempts
FROM einvoicing_gcc_analytics.api_details_v2 api
LEFT JOIN einvoicing_gcc_analytics.einvoice_gcc inv
  ON api.unique_identifier = inv.unique_identifier
WHERE api.created_at >= toDateTime('[WINDOW_START_UTC]', 'UTC')
  AND api.created_at <  toDateTime('[WINDOW_END_UTC]',   'UTC')
  AND api.analytics_event_name = 'xml_response_final'
  AND api.gstin   = '310451897400003'
  AND api.status  = '502'
GROUP BY terminal_status
ORDER BY invoices DESC;
```

**Reading the result:**
- `terminal_status = REPORTED` / `CLEARED` → invoice reached ZATCA and got back terminal-success **despite** the customer-visible 502. Silent-success bucket — matters for customer comms.
- `terminal_status = PENDING` → record persisted but ZATCA call didn't complete. Reconcile-required bucket.
- `terminal_status = FAILED` → ZATCA returned a non-recoverable error.
- `terminal_status = no_record` → request died before persisting. Either gateway-layer 502 (request never reached app) or app crashed mid-flow.

##### Impact-Q3 — Did any of these invoices' outbound ZATCA calls land?

```sql
-- Source: einvoicing_gcc_analytics.einvoiceexternalaudittrail
-- Answers: did our service even attempt ZATCA for this customer's invoices in the window?
-- JOIN through traceId (eInvoiceAuditTrail uses traceId; api_details_v2 uses request_id — verify mapping; if not 1:1, drop to two queries)
-- This query stands alone: count outbound ZATCA calls regardless of HTTP outcome
SELECT
  service,
  operation,
  count() AS calls,
  countDistinct(traceId) AS distinct_traces
FROM einvoicing_gcc_analytics.einvoiceexternalaudittrail
WHERE createdAt >= toDateTime('[WINDOW_START_UTC]', 'UTC')
  AND createdAt <  toDateTime('[WINDOW_END_UTC_PLUS_10MIN]', 'UTC')   -- +10min audit settle buffer
GROUP BY service, operation
ORDER BY calls DESC;
```

**Reading the result:**
- Non-zero calls with ZATCA service → outbound layer was reaching ZATCA. 502s are likely gateway-side (incoming 502 to customer ≠ outbound 502 from ZATCA).
- Zero calls but Q1 shows attempts → request died before the outbound layer. Strongly suggests our gateway/proxy.
- Caveat: `service` enum values not yet pinned in `gotchas.md` — run `SELECT DISTINCT service FROM einvoiceexternalaudittrail LIMIT 50` first to know what to filter by (e.g. `'zatca'`, `'fatoora'`, `'zatca-clearance'`).

##### Impact-Q4 — Customer retry signal

```sql
-- Source: einvoicing_gcc_analytics.api_details_v2
-- Answers: did the customer retry the same unique_identifier multiple times (and what response)
SELECT
  unique_identifier,
  groupArray(status) AS status_sequence,
  count() AS attempts
FROM einvoicing_gcc_analytics.api_details_v2
WHERE created_at >= toDateTime('[WINDOW_START_UTC]', 'UTC')
  AND created_at <  toDateTime('[WINDOW_END_UTC]',   'UTC')
  AND analytics_event_name = 'xml_response_final'
  AND gstin = '310451897400003'
GROUP BY unique_identifier
HAVING attempts > 1
ORDER BY attempts DESC
LIMIT 50;
```

### Incident Analysis

***How was the event detected?***

[TBD — test scenario; in real incident: customer report or 5xx alert]

***How could time to detection be improved?***

[TBD]

***How did you reach the point where you knew how to mitigate?***

[TBD]

### Root Cause Analysis

#### Problem Statement:

Customer received HTTP 502 on `/v2/einvoices/generate-with-file`; whether the failure was internal (our gateway/proxy/app) or external (ZATCA returning 502 we propagated) is unconfirmed pending Impact-Q1/Q3 results.

#### 1. Why did the 502 spike happen?

[WHY_1 — pending Q1 ct_error split. If `ct_error=true`: investigate gateway/app. If `ct_error=false`: investigate upstream/regulator path.]

#### 2. Why [LAYER_2_QUESTION]?

[TBD — depends on Why_1]

#### 3. Why [LAYER_3_QUESTION]?

[TBD]

#### 4. Why [LAYER_4_QUESTION]?

[TBD]

#### 5. Why [LAYER_5_QUESTION]?

[TBD]

#### Summary of contributing factors

| Area | Gaps / Issues |
|---|---|
| Code Logic | [TBD pending root cause] |
| Network / Gateway | [TBD — 502 strongly hints at this layer] |
| Monitoring | Per-customer per-endpoint 5xx alert: present? alert threshold? [TBD] |
| Operational | [TBD] |

### Post Incident Analysis

***How was the root cause diagnosed?***
[TBD]

***Did you have an existing backlog item that would have prevented this?***
[TBD]

***If yes, why was this not completed prior to the event?***
[N/A — TBD]

***Is it possible to programmatically audit for this failure mode?***
[TBD — e.g. per-customer per-endpoint p99 5xx-rate alert with deviation from baseline]

***If the change was automated, should this have been caught and rolled back in testing?***
[TBD — depends on root cause]

***If this change was manual, how was the change reviewed and tested?***
[N/A — TBD]

### Action Items

1. [TBD — likely: investigate gateway-layer 502 source if Q1 shows ct_error=true] — [TBD]
2. [TBD — alert: per-customer per-endpoint 5xx spike] — [TBD]
3. [TBD — runbook: KSA-specific runbook missing — write one] — [TBD]

### Learnings

1. [TBD]
2. [TBD]
3. [TBD]

### Metrics and Graphs

[TBD — attach: 5xx-rate over time, per-status-code breakdown, ZATCA outbound success rate, customer-specific traffic chart]

### Checklist before panel review

- [ ] Timelines are clear and precise (supported by metrics) — pending
- [ ] Communication timelines stated separately — pending
- [ ] No. of tickets and no. of customers impacted both stated — pending Q1
- [ ] Each Action Item is tracked through Jira — pending
- [ ] All open comments are answered and closed — pending
