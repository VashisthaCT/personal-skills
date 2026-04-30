---
name: v-incident
description: Sev1/Sev2 reaction kit. Takes <incident-name>, scaffolds ~/dev/personal-skills/data/incidents/<name>/ with timeline.md, rca.md, comms_drafts.md, meta.yaml, cross-references country runbook if detectable, and drops a self-DM draft with folder path + first 3 actions. Drafts only — no auto Slack post, no Drive doc creation.
---

You are running Vashistha's Sev1/Sev2 reaction kit. Goal: in under 60 seconds, scaffold a working folder so the user can stop hunting for templates and start updating timeline + drafting comms during the live incident. Manual trigger only — there is no cron for this skill.

## Inputs

- `<incident-name>` (required): kebab-case slug. Convention: `<country-or-region>-<short-cause>-<YYYY-MM-DD>` (e.g. `ksa-redis-licensing-2026-04-27`, `ind-irn-503-2026-04-27`, `peppol-as4-tls-2026-05-02`).
- `<description>` (optional, free text): what the user observed when they hit the alert. If omitted, leave a placeholder in `timeline.md` for the user to fill.
- `<severity>` (optional, default `Sev2`): one of `Sev1` / `Sev2`.

If invoked with just a slug, prompt the user once for description + severity, then proceed. Don't loop on missing inputs — best-effort defaults are fine.

## Step 1 — Create the folder

Create `~/dev/personal-skills/data/incidents/<incident-name>/`. If it already exists, abort with: `Folder already exists. Pass a unique <incident-name> or rm the existing folder first.` (Don't auto-overwrite a live incident's notes.)

## Step 2 — Detect country / region from the slug

Match the leading token against:

- `jo` / `jordan` → `runbooks/countries/jordan/runbook.md`
- `in` / `ind` / `india` → `runbooks/countries/india/runbook.md`
- `ksa` / `sa` / `saudi` → `runbooks/countries/ksa/runbook.md`
- `uae` / `ae` → `runbooks/countries/uae/runbook.md`
- `my` / `malaysia` → `runbooks/countries/malaysia/runbook.md`
- `be` / `belgium` → `runbooks/countries/belgium/runbook.md`
- `fr` / `france` → `runbooks/countries/france/runbook.md`
- `pl` / `poland` → `runbooks/countries/poland/runbook.md`
- `peppol` → `runbooks/regions/peppol/runbook.md`
- `gcc` → `runbooks/regions/gcc/runbook.md`
- `mea` → `runbooks/regions/mea/runbook.md`

Store the resolved path (or `null` if no match) for use in Step 3 and the comms draft.

## Step 3 — Write the four scaffold files

### `timeline.md` (append-only event log, IST timestamps)

```
# Timeline — <incident-name>

All timestamps IST. Append-only. Most recent at the bottom.

## Events

- [HH:MM IST] Incident detected: <description>
- [HH:MM IST] (next event — fill in)
```

Pre-seed only the first event with the user's description. If description was omitted, write `<fill in observation>` as the placeholder.

### `rca.md` (draft using the RCA template)

```
# RCA — <incident-name>

> Drafting against `~/dev/personal-skills/prompts/rca_template.md` (VP-praised NIC RCF format).
> When ready to fill, run `/v-rca <incident-name>` to expand this stub against the timeline + Slack threads.

## Status
- Severity: <severity>
- Started: <started_at IST>
- Resolved: TBD
- Author: Vashistha Garg

## Sections to fill (per template)
1. Executive summary (1 paragraph)
2. Customer impact (who, how many, $)
3. Timeline (link to timeline.md)
4. Root cause (5-whys)
5. Contributing factors
6. Detection
7. Resolution
8. Action items (with owners + JIRA links)
9. Lessons learned
```

Note: `prompts/rca_template.md` is created in Phase 4 — reference it by path, do not block on its existence.

### `comms_drafts.md` (Slack drafts — three variants)

```
# Comms drafts — <incident-name>

Channel: <channel from meta.yaml, or "TBD — pick the on-call channel">

---

## (a) Initial channel post

Heads up team — opening incident `<incident-name>` (<severity>).

Symptom: <description>
Started: <HH:MM IST>
Impact: <fill in once known — customer count, regions, services>
Owner: Vashistha
Tracking: thread on this message; timeline + RCA at `~/dev/personal-skills/data/incidents/<incident-name>/`

Will post next update in 15 min.

---

## (b) Status update template (post every 15–30 min during active incident)

Update on `<incident-name>` (<severity>) — <HH:MM IST>:
- What we know: <one-liner>
- What we're trying: <one-liner>
- Customer impact so far: <fill in>
- Next update: <HH:MM IST>

---

## (c) All-clear / resolved post

`<incident-name>` resolved at <HH:MM IST>.

Root cause (1-line): <fill in>
Mitigation: <fill in>
Customer impact: <final tally>
RCA doc: <link will be posted once RCA is published>
Action items tracked under: <JIRA epic / labels>

Thanks <names of folks who helped> for the help. Closing the thread.
```

### `meta.yaml`

```
incident: <incident-name>
severity: <Sev1 | Sev2>
started_at: <ISO timestamp IST, e.g. 2026-04-27T14:32:00+05:30>
services: []         # fill in: einvoicing-be, clear-peppol-ap, ingestion-overlord, etc.
related_jira: []     # fill in: epic + bug ticket keys
runbook_pointer: <path from Step 2, or null>
channel: <slack channel id or name — TBD if not yet assigned>
```

Pre-fill what can be inferred from inputs: `incident`, `severity`, `started_at` (use current time IST), `runbook_pointer` (Step 2). Leave the rest as listed defaults for the user to fill while paging on the incident.

### `queries.md` (only if Step 2 resolved to a GCC-scope runbook)

If `runbook_pointer` matches `runbooks/countries/(ksa|uae|bahrain|kuwait|oman|qatar)/` or `runbooks/regions/(gcc|mea)/`, also write `queries.md`:

```
# Queries — <incident-name>

Schemas: ~/dev/personal-skills/data/schemas/gcc/
- relationships.md                       — what each table holds, JOIN keys, semantic layers
- gotchas.md                             — engine pitfalls (TZ=UTC, camelCase quoting, etc.)
- tables/einvoicing_gcc_analytics.yaml   — ClickHouse column catalog (RCA primary target)
- tables/einvoices_gcc.yaml              — Postgres column catalog (workspace lookups)

## Window (UTC) — fill once known
Start: <YYYY-MM-DD HH:MM:SS>
End:   <YYYY-MM-DD HH:MM:SS>

## Questions to answer (typical RCA shape — adapt per incident)
1. HTTP-side impact — distinct invoices × workspaces affected per endpoint × status code
2. DB-side state — invoice_status distribution within the window (online + offline)
3. Terminal classification — for failed responses, what state did they actually end in?
4. Top workspaces — by impact, unifying gstin and UUID identifiers
5. Regulator-side verification — did affected invoices reach the regulator?

For each, **compose SQL grounded in the schema files** for THIS incident's window and scope.
Do NOT copy-paste queries from past RCAs — different incidents have different filters,
endpoints, and bucketing rules. Paste the SQL you actually run + its output below.

## Logs
- [HH:MM IST] Query: <intent>
  ```sql
  ...
  ```
  Output: <paste or summarize>
```

If `runbook_pointer` doesn't match GCC scope (e.g. India, Belgium, France) or is `null`, skip this file. `/v-rca` will look for it later and will skip-with-warning if absent.

## Step 3.5 — Enrich rca.md with runbook gotchas (if country detected in Step 2)

If `runbook_pointer` is non-null, read the *adjacent* runbook files in the same directory (not just `runbook.md`):

- `code_map.md` — known code paths
- `ubl_structure.md` — schema gotchas (if invoicing-related)
- `api_contract.md` — endpoint spec (if regulator API call involved)
- `credentials.md` — auth model

Skip files that don't exist (stub countries). For each loaded file, extract the 2-4 most-relevant lines for this incident's symptoms and append them as a new section in `rca.md` (right after "Sections to fill"):

```
## Known gotchas from runbook (auto-loaded)
> Source: `<runbook_pointer dir>/`
- [Gotcha 1 from runbook — paste the line; cite filename]
- [Gotcha 2]
- ...
```

Don't fabricate. If the runbook files are sparse/stub, write: `(no gotchas in runbook yet — fill <cc>/runbook.md post-incident via /v-runbook).`

If `runbook_pointer` is `null`, skip this step entirely.

## Step 4 — Self-DM draft

Compose a single Slack-formatted message to self-DM `D088362AS65` via `slack_send_message_draft`:

```
*Incident scaffold ready: <incident-name> (<severity>)*

Folder: `~/dev/personal-skills/data/incidents/<incident-name>/`
Runbook: <path from Step 2, or "no runbook match for slug — create one post-incident">

*Next 3 actions:*
1. Update `timeline.md` with first observations (every event, IST timestamps).
2. Post `comms_drafts.md` (a) to channel `<channel>` (edit channel in `meta.yaml` first if unknown).
3. Drop runbook link in thread: `<runbook path>` (skip if no match).

Reminder: drafts only. RCA Drive doc happens later via `/v-rca`.
```

## Step 5 — Done

Don't auto-Slack-post. Don't create a Drive doc. Don't touch the channel. The user pages on the incident; the skill just gives them the kit.

## Verifiable success criteria

- 4 files exist at `~/dev/personal-skills/data/incidents/<incident-name>/`: `timeline.md`, `rca.md`, `comms_drafts.md`, `meta.yaml`.
- 5th file `queries.md` exists IFF Step 2 resolved to a GCC-scope runbook (ksa/uae/bahrain/kuwait/oman/qatar/gcc/mea).
- `timeline.md` has the first event line pre-seeded with `Incident detected: <description>` and an IST timestamp.
- `meta.yaml` has `incident`, `severity`, `started_at`, `runbook_pointer` pre-filled (last is `null` if no slug match).
- A self-DM draft exists in `D088362AS65` with the folder path + 3 actions.
- No Slack channel post. No Drive doc. No `git commit`.

## Failure modes

- Folder already exists → abort with the message in Step 1; do not overwrite.
- `<incident-name>` is not kebab-case → fix it (lowercase, dashes for spaces) and proceed; note the rewrite in the self-DM draft.
- `slack_send_message_draft` fails → still leave the 4 scaffold files; print the would-have-been draft to stdout for manual paste.
- `runbooks/` directory doesn't exist yet (pre-Phase 3 for some countries) → leave `runbook_pointer: null` and note in self-DM draft "no country runbook found — flag for /v-runbook later".

## Don't

- Don't `git commit`.
- Don't auto-post to channels.
- Don't create a Drive RCA doc — user does that themselves once RCA is ready.
- Don't link a runbook that doesn't exist — leave `null` instead.
- Don't loop on missing inputs more than once. MVP-first.
