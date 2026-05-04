# CLAUDE.md — personal-skills repo

## What this is
Vashistha Garg's private Claude Code plugin: personal productivity OS. Full plan in memory file `project_personal_skills.md`.

## Conventions
- Skills are prefixed `v-` (e.g. `v-standup`, `v-promo-tracker`).
- Skill format: `skills/<name>/SKILL.md` with frontmatter (name, description). Optional `prompt.md` for long bodies.
- Data store: `data/*.yaml` and `data/promotion_state.json` are the source of truth.
- Drafts only — no skill auto-sends to Slack/Email. Output lands in self-DM `D088362AS65`.
- Runbooks at `runbooks/countries/<cc>/` and `runbooks/regions/<name>/`.
- The RCA template at `prompts/rca_template.md` is the VP-praised NIC RCF format.

## Identifiers (for skill scripts)
| Field | Value |
|---|---|
| Email | vashistha.garg@clear.in |
| Slack user_id | `U087T0SHNCC` |
| Slack self-DM (drop zone) | `D088362AS65` |
| Atlassian accountId | `712020:7bdcfdb0-f37e-47b8-80cb-54f774e7d913` |
| Atlassian cloudId | `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86` |
| GitHub handle | `VashisthaCT` |
| Manager | Ayush Jain (Slack `U0ABBKV5QDU`, DM `D0AC1AKDJKT`) |

## When asked to add a skill
1. Create `skills/v-<name>/SKILL.md` with frontmatter.
2. Add the path to `.claude-plugin/plugin.json` `skills` array.
3. If the skill body exceeds ~80 lines, split into `skills/v-<name>/prompt.md` and reference from SKILL.md.

## When asked to refresh data
- `data/active_projects.yaml`, `countries.yaml`, `people.yaml`, `customers.yaml`: hand-edit or via `/v-sync-context`.
- `data/promotion_state.json`: updated weekly by `/v-promo-tracker`.

## Tooling quirks
- `gh` CLI requires `dangerouslyDisableSandbox: true` (sandbox blocks `api.github.com` + macOS keychain). Token comes from `gh auth token`.
- Drive search syntax: NO `'me' in owners`, NO `trashed = false`. Dates ISO 8601 with `Z` suffix. Filter out `parentId == "1i0Msm1KKgwpCdsWtfjfcoT_21zuxMcuF"` (auto Meet Transcripts).
- Slack MCP caps at 20 msgs/query — paginate.

## MCP routing (which MCP for which thing)

Skills that need live data should route by **country first**, then by **data type**:

| Need | MCP | Why |
|---|---|---|
| **IND prod logs** (e-invoicing-be, clr-irp-be, bifrostgsp, einvoicing-webapp) | `clarity-coralogix` (default tenant) | IND services are tagged in coralogix default region |
| **GCC / MEA / EU / SEA prod logs** (einvoicing-core, einvoice-<cc> modules, clear-routing) | `clarity-cubeapm` | Multi-region — non-IND services route here |
| **Service identifier resolution** ("where does <service> live?") | `clarity-service-map` | Cross-system: resolves PagerDuty + Grafana + Coralogix + CubeAPM + K8s IDs in one call |
| **Kubernetes pod state, restarts, releases** | `clarity-sight-agent` | Multi-region K8s + release tracking |
| **Error tracking** (Sentry issues, exception details) | `clarity-sentry` | Per-service Sentry projects |
| **Alert source-of-truth** (active incidents, AI analysis) | `clarity-pagerduty` | Auto-populates RCA timeline |
| **Dashboards & metric panels** | `clarity-grafana` | Prometheus + ClickHouse queries |
| **Athena SQL** (GCC analytics, ClickHouse `einvoicing_gcc_analytics`) | `athena` | Multi-region |
| **GST/PAN/MSME verification** | `clarity-clearidentity` | IND identity API |
| **GitHub commits/PRs** | `clarity-github` (richer) OR `gh` CLI | Either works |
| **Recon data** (advance-recon ClickHouse, matching tasks) | `clarity-recon-mcp` | Reconciliation data access |
| **One Integration / ERP connector lifecycle** | `clarity-one-integration` | User's product domain |

**Country routing rule:** IND → `coralogix`. Everything else (UAE, KSA, Jordan, Belgium, France, Malaysia, Poland, Peppol, GCC) → `cubeapm`. When uncertain, call `service-map` first.

### MCP gotchas (do not repeat past mistakes)

- **GCC / KSA logs MUST go through `sight-agent.search_cubeapm_logs` with `cluster=prod-oci`** — NOT the raw `cubeapm.discover_logs_stream_fields` / `cubeapm.get_log_hits` / `cubeapm.query_logs`. The raw tools don't auto-route to the OCI cluster for the `ksa` region and silently return `null` / empty hits even though logs are flowing. Verified 2026-05-04: `einvoicingbe-prod-oci-http`, `clear-harvester-gcc-prod-http`, `ingestionv2-einvoice-gcc-prod-http` all return 50-100+ logs/h via `sight-agent` but 0 via raw cubeapm.
- **`mea` cubeapm region** (`cubeapm-mea.internal.cleartax.co`) currently times out from this MCP token. Use `ksa` region or `sight-agent` instead until it's fixed.
- **`cubeapm.list_available_regions` shows `ksa` and `mea`** as available, but only `ksa` actually returns data via the raw tools — and even then only for a few service-name labels. **Heuristic: if the answer matters, route through `sight-agent`.**

## Don't
- Don't run `git commit` or `git push` (user does these).
- Don't fork existing skills (`cleartax-perf-review-builder`, country experts in AMClaudeKit). Wrap them.
- Don't add tests for prompts.
- Don't commit secrets — no pre-commit hook installed; self-check every diff.
- Don't auto-send to Slack channels or external DMs. Drafts to self-DM only.

## See also
- Memory: `project_personal_skills.md` (the plan, all locked decisions)
- Memory: `project_perf_review_fy26.md` (rubric source for `/v-promo-tracker`)
- Memory: `platform_architecture.md` (e-InvoiceVerse architecture for country runbooks)
- Memory: `project_jordan_einvoicing.md`, `project_peppol_reporting.md` (rich seeds for runbooks)
