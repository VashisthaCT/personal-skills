# Evidence — `/v-rca` test invocation 2026-04-30

## Test scope

This was a synthetic `/v-rca` invocation to validate that the new GCC Metabase schema files (committed `1ba3229`) actually steer the agent to compose fresh, schema-grounded SQL — not pattern-match against the KSA Apr-27 RCA.

Test prompt: *"In KSA, last 30 minutes, we saw a 502 spike on /v2/einvoices/generate-with-file for one specific customer with gstin 310451897400003. Was this regulator-side or our side? How many invoices affected? Did any reach ZATCA?"*

Differs from KSA Apr-27 in: customer scope (single gstin, not platform-wide), endpoint scope (single endpoint, not all 8 GCC generate APIs), status code (502, not 500), window length (30 min, not 58 min), question framing (regulator-side vs our-side, not silent-success bucket math).

## Sources read

- `~/dev/personal-skills/prompts/rca_template.md` — section structure
- `~/dev/personal-skills/data/active_projects.yaml` — matched `ksa-uae-prod-support` project (P0, oncall-driven, with note about Apr-27 Sev1 RCA in flight)
- `~/dev/personal-skills/runbooks/countries/ksa/runbook.md` — **DOES NOT EXIST**. Action item candidate: write KSA runbook.
- `~/dev/personal-skills/data/people.yaml` — referenced but no individuals named in body (functional roles only)
- `~/dev/personal-skills/data/schemas/gcc/relationships.md` — read for layer mapping
- `~/dev/personal-skills/data/schemas/gcc/gotchas.md` — read for TZ + quoting + naming convention rules
- `~/dev/personal-skills/data/schemas/gcc/tables/einvoicing_gcc_analytics.yaml` — read for `api_details_v2`, `eInvoiceAuditTrail`, `einvoiceexternalaudittrail`, `einvoice_gcc`, `eInvoice_gcc_metadata` column lists
- `~/dev/personal-skills/data/schemas/gcc/tables/einvoices_gcc.yaml` — not directly used; gstin filter applied at `api_details_v2` level

## Slack / Jira / PR signals

None pulled — synthetic test scenario with no live signal. In a real invocation, this section would list slack permalinks, Jira ticket keys, and PR URLs.

## Schema-knowledge findings during composition

These are the points where the YAML files actively prevented a hallucination or guided a correction:

### 1. `eInvoiceAuditTrail` does NOT have `invoice_status` or `unique_identifier` columns

Looking at the catalog YAML, `eInvoiceAuditTrail` has: `gstinOrgId`, `_class`, `apiPriority`, `spanId`, `traceId`, `response`, `request`, `auditType`, `operation`, `userId`, `updatedAt`, `panOrgId`, `createdAt`, `entity`, `nodeId`, `branchOrgId`, `_id`. **No status column. No invoice-key column.**

This contradicts the JOIN recipe in `relationships.md` (which I wrote earlier this session) that said:
> "What terminal state did each 500 response end in?" → `api_details_v2` LEFT JOIN `(SELECT uniqueIdentifier, argMax(invoice_status, created_at) FROM eInvoiceAuditTrail …)`

**That recipe is wrong.** `eInvoiceAuditTrail` is a request-level audit log keyed by `traceId`/`spanId`, with full `request`/`response` payloads. To get terminal invoice status, JOIN must go through `einvoice_gcc` (online) or `eInvoice_gcc_metadata` (offline) where the `status` column actually lives.

**Action for the schema repo:** fix `relationships.md` JOIN-recipes table. New entry should be:
> "What terminal state did each invoice end in?" → `api_details_v2` LEFT JOIN `einvoice_gcc` USING `unique_identifier` (online) OR LEFT JOIN `eInvoice_gcc_metadata` USING `uniqueIdentifier` / `unique_identifier`-cast (offline) — read `inv.status`.

This corrected JOIN is what was used in Impact-Q2 of the rca.md.

### 2. Column-naming inconsistency WITHIN ClickHouse

- `einvoice_gcc` (online flow) uses snake_case: `unique_identifier`, `taxpayer_org_id`, `status`
- `eInvoice_gcc_metadata` (offline flow) uses camelCase: `uniqueIdentifier`, `taxpayerOrgId`, `status`

Both are in the same ClickHouse database. Mongo-origin shapes preserved differently per pipeline. **A union query across online + offline needs explicit column aliasing.** The `gotchas.md` doc has the camelCase-vs-snake_case caution between engines, but missed this within-engine variation. Add a §15.

### 3. `api_details_v2` workspace_id cascade

`api_details_v2` has 5 workspace_id columns: `workspace_id`, `workspace_id_from_branch`, `workspace_id_from_gstin`, `workspace_id_from_pan`, `workspace_id_fin`. For this incident, gstin filter is direct (gstin column on api_details_v2), so workspace cascade is irrelevant. But noted for future incidents that filter by workspace UUID.

### 4. `einvoiceexternalaudittrail` enum unknown

`service` and `operation` columns exist but their enum values are not in `gotchas.md`. Impact-Q3 has a caveat noting the user should run `SELECT DISTINCT service FROM einvoiceexternalaudittrail LIMIT 50` first to know the right filter for ZATCA-specific calls.

## Composition-freshness checks (vs. KSA Apr-27)

- ✅ gstin filter — Apr-27 had no per-customer scope; this query has `gstin = '310451897400003'`
- ✅ endpoint filter — Apr-27 was platform-wide (8 endpoints); this is `analytics_event_name = 'xml_response_final'` only
- ✅ status filter — Apr-27 was `status = '500'`; this is `status = '502'`
- ✅ window — Apr-27 was 58 min specific to that day; this uses placeholders `[WINDOW_START_UTC]` / `[WINDOW_END_UTC]` adaptable to the actual reported 30-min window
- ✅ question framing — Apr-27 was silent-success bucket math; this is regulator-side-vs-our-side classification (Q1's `ct_error` split)

No SQL was copy-pasted from `query_patterns.yaml` (because we deleted it; that was the point).

## Action items for the schema repo (separate PR)

1. Fix `relationships.md` JOIN-recipes table — terminal-status JOIN goes through `einvoice_gcc` / `eInvoice_gcc_metadata`, not `eInvoiceAuditTrail`.
2. Add `gotchas.md` §15: within-ClickHouse naming inconsistency between online (snake) and offline (camel) Mongo-mirror tables.
3. Pin `einvoiceexternalaudittrail.service` enum values once a sample query is run.
4. Pin `einvoice_gcc.status` and `eInvoice_gcc_metadata.einvoiceStatus` enum values (suspected: REPORTED / CLEARED / PENDING / FAILED / NOT_SUBMITTED — but should be confirmed).
5. Open: write `runbooks/countries/ksa/runbook.md` (file currently missing).
