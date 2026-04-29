---
name: v-rca
description: Draft a Sev1/Sev2 RCA in the canonical 9+-section ClearTax format (VP-praised NIC RCF template). Takes an incident summary string OR a Slack thread permalink. Pulls Slack thread + Jira tickets + recent PRs + country runbook context. Writes a markdown draft to `data/incidents/<date>-<slug>/rca.md` and posts a Slack-formatted summary draft to self-DM (D088362AS65). Drafts only — user reviews before publishing to Drive.
---

You are drafting an RCA/RCF for Vashistha. Triggered by `/v-rca <incident-summary-OR-slack-permalink>`. The output is a **draft markdown file** plus a **draft Slack summary** — never auto-posted to incident channels, never auto-uploaded to Drive.

## Step 1 — Parse input

Input is one of:
- A free-text incident summary (e.g. `"EWB-via-IRN failures Nov 18 due to Redis NIC-down flag, 10h25m, 190 workspaces"`)
- A Slack thread permalink (`https://cleartaxtech.slack.com/archives/C.../p...`)

If permalink: derive `channel_id` and `thread_ts` from the URL, fetch the root message + replies via `slack_read_thread`. Use the root message text as the seed incident description; keep the thread as evidence.

Compose a slug: `<YYYY-MM-DD>-<short-kebab>` (e.g. `2025-11-18-ewb-irn-nic-redis`). Date = incident date if known, else today.

## Step 2 — Load context

Read in parallel:
1. **Template:** `~/dev/personal-skills/prompts/rca_template.md` — this is the section structure to fill.
2. **Active projects:** `~/dev/personal-skills/data/active_projects.yaml` — find any project whose keywords match the incident (e.g. NIC switcher → `india`/IRP; FTP → IND FTP migration; Tabby → UAE).
3. **Country runbook:** if the incident text mentions a country code or known country name (jordan / india / uae / ksa / malaysia / belgium / france / poland) or a region (peppol / gcc / mea), read `~/dev/personal-skills/runbooks/countries/<cc>/runbook.md` (or `runbooks/regions/<id>/runbook.md`). Use it for: prior RCAs in this area, error code references, escalation contacts.
4. **People:** `~/dev/personal-skills/data/people.yaml` — for Slack IDs / role attribution.
5. **Metabase schema (GCC scope only, v1):** if the incident touches `ksa` / `uae` / `bahrain` / `kuwait` / `oman` / `qatar` or region `gcc` / `mea`, read all four files:
   - `~/dev/personal-skills/data/schemas/gcc/relationships.md` — what each table holds, layer-by-layer semantics, JOIN recipes, identifier mismatches. **Start here** — this maps any incident question to the right tables.
   - `~/dev/personal-skills/data/schemas/gcc/gotchas.md` — engine pitfalls (TZ=UTC, camelCase quoting, hyphen↔underscore DB-name quirk).
   - `~/dev/personal-skills/data/schemas/gcc/tables/einvoicing_gcc_analytics.yaml` — ClickHouse column catalog (RCA primary target).
   - `~/dev/personal-skills/data/schemas/gcc/tables/einvoices_gcc.yaml` — Postgres column catalog (workspace lookups, legacy data).
   **Compose SQL from scratch** for this incident's window, region, and failure mode — do NOT copy queries from past RCAs. The schema knowledge is what enables fresh composition; templated queries would bias the analysis toward the prior incident's shape.
   If the incident is outside GCC scope (e.g. `ind` / `belgium` / `france`), skip this — IND metabase reference is deferred to v2.

## Step 3 — Pull related signals

Run these in parallel; each may fail — degrade gracefully and note "no signal" in the relevant section:

1. **Slack thread context** — if a permalink was provided, the full thread is already in hand. Otherwise search Slack last 7d for terms from the incident summary (`slack_search_public_and_private`, cap 20 msgs, paginate).
2. **Jira** — JQL via cloudId `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`:
   - `assignee = currentUser() AND text ~ "<keywords>" ORDER BY updated DESC` (cap 10) — to find the user's tickets touching this area
   - `project = SEV1BUGS AND text ~ "<keywords>" ORDER BY created DESC` (cap 10) — to find linked Sev1 action items
3. **Recent PRs** — `gh search prs --author=VashisthaCT --updated >=$(date -v-30d +%Y-%m-%d) <keywords>` (requires `dangerouslyDisableSandbox: true`). Cross-reference with prior PRs that touched the affected code path.
4. **Prior RCAs** — runbook's `RCAs encountered` section + memory file `project_perf_review_fy26.md` §6 (the 6 H2 user-owned RCA Drive IDs).

## Step 4 — Compose the RCA draft

Open the template and replace every `[BRACKETED]` placeholder with grounded content from steps 1–3. Rules:

- **Don't fabricate.** If a section has no signal (e.g. unknown customer count), write `[TBD — pending L2 metrics]`. Never invent numbers.
- **5 Whys → 5–9 Whys.** The NIC RCF has 9 layers. Stop only when you've named a code/monitoring/process gap that maps to a concrete action item. Don't bottom out at "human error".
- **Action items must be actionable.** Each one resolves a specific Why above it, ends with `— [JIRA_TICKET_LINK]` (or `[TBD]` if not yet filed), and would be closeable.
- **Terminology Overview is mandatory.** A non-IND reviewer must follow along.
- **Keep the verbatim section headers** from the template — panel reviewers look for them.
- **No name-dropping.** Functional roles only ("L2 team", "engineering", "platform team"). Names belong in Slack permalinks where they appear naturally.
- **Cite sources inline.** PR numbers, Jira tickets, Slack permalinks at the relevant section. **Every count/bucket/percentage in the Impact section must name the source table inline** — e.g. "1,234 invoices terminally REPORTED despite 500 response (`einvoicing_gcc_analytics.api_details_v2` ⨝ `eInvoiceAuditTrail`, window 14:30-15:00 UTC)". Apoorva-tier preempt — the VP review expects this.
- **Don't hallucinate column names.** Column names come from `data/schemas/gcc/tables/*.yaml`. Postgres uses camelCase (`uniqueIdentifier`, `analyticsEventName` — quoted in queries); ClickHouse uses snake_case (`unique_identifier`, `analytics_event_name`). Cross-engine column copy-paste = silent bug.
- **Compose SQL fresh per incident.** Don't fit a new incident's data section into a past incident's query shape. `relationships.md` tells you which tables answer which question; column YAMLs give you the names; gotchas tell you the timezone and quoting rules. Compose from those — do not pattern-match on past RCAs.

## Step 5 — Write the draft file

Create the directory + file:
- Dir: `~/dev/personal-skills/data/incidents/<slug>/`
- File: `~/dev/personal-skills/data/incidents/<slug>/rca.md`

If the directory already exists, use a numeric suffix (`-2`, `-3`) — never overwrite a prior draft.

Also drop a sibling `evidence.md` capturing: source Slack permalink (if any), Jira tickets pulled, PR list, runbook entry referenced. This is the audit trail for the draft.

## Step 6 — Compose Slack summary draft

Build a ≤15-line Slack-formatted summary:

```
*RCA draft — [INCIDENT_TITLE]*

*When:* [DATE_RANGE], [DURATION]
*Impact:* [N] workspaces, [N] failed [docs], [N] call failures
*Root cause (1 line):* [ROOT_CAUSE_SUMMARY]
*Action items:*
- [AI_1] — [TICKET]
- [AI_2] — [TICKET]
- [AI_3] — [TICKET]

*Full draft:* `data/incidents/<slug>/rca.md`
*Next:* review → publish to Drive (Sev1 RCF folder) → link from runbook.
```

Post this draft to self-DM `D088362AS65` via `slack_send_message_draft` (NOT `slack_send_message`).

## Verifiable success criteria

- File exists at `~/dev/personal-skills/data/incidents/<slug>/rca.md`.
- File contains every section header from `prompts/rca_template.md` verbatim.
- Every `[BRACKETED]` placeholder is either filled with grounded content or marked `[TBD — <reason>]`.
- 5+ Whys layered; bottoms out at a code/monitoring/process gap.
- Each Action Item has a Jira link or `[TBD]`.
- `evidence.md` sibling file captures sources used.
- Slack draft (not send) posted to `D088362AS65`.

## Don't

- Don't auto-publish to Drive. User reviews and copies to the Sev1 RCF folder themselves.
- Don't post to incident or L3 support channels. Self-DM only.
- Don't name individuals in the body. Functional roles only.
- Don't claim numbers (workspaces, failures, durations) that aren't in source data — mark `[TBD]`.
- Don't fork prior RCAs blindly — use them as evidence, not paragraph templates.
- Don't run if `prompts/rca_template.md` is missing — abort and tell the user.
