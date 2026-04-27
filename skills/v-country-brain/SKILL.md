---
name: v-country-brain
description: One-prompt deep-dive briefing on a country or region in the e-invoicing portfolio. Reads the runbook directory, in-flight Jira tickets filtered by country, recent PRs touching country code paths, and the country's key Slack channel. Composes status + active work + open questions + recent PRs + who-to-ask. Output: synthesized briefing in chat (≤80 lines).
---

You are producing a one-page briefing on a single country or region in Vashistha's e-invoicing portfolio. Triggered by `/v-country-brain <id>` where `<id>` is one of the keys under `countries:` or `regions:` in `~/dev/personal-skills/data/countries.yaml` (jordan, india, uae, ksa, malaysia, belgium, france, poland, peppol, gcc).

## Step 1 — Resolve the entry

1. Read `~/dev/personal-skills/data/countries.yaml`. Find `<id>` under `countries:` or `regions:`.
2. If not found: list valid IDs and stop.
3. Note: `code`, `region`, `status`, `regulator`, `repos`, `runbook` path, `notes`.
4. Determine runbook dir: `~/dev/personal-skills/runbooks/countries/<id>/` or `~/dev/personal-skills/runbooks/regions/<id>/`.

## Step 2 — Read runbook

Read every `*.md` in the runbook dir. If `seed: stub` in countries.yaml, only `overview.md` exists — flag this in output as "stub runbook, expand via /v-runbook".

Key files (when present):
- `overview.md` — elevator pitch
- `live_state.md` — go-live status, customers, known issues
- `runbook.md` — common errors and debug steps
- `law_changes.md` (or `spec_changes.md` for regions) — recent regulatory deltas
- `api_contract.md` / `ubl_structure.md` / `credentials.md` — technical depth
- `code_map.md` — repos × files
- `people.md` — who to ask

## Step 3 — Pull live signal

Run these in parallel. Each may fail (rate limits, no recent activity) — continue without it:

1. **In-flight Jira tickets** filtered by country: JQL = `assignee = currentUser() AND text ~ "<country-name-or-code>" AND status in ("In Progress","In Review","To Do") ORDER BY updated DESC` (cloudId `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`). Cap at 10. For Jordan use `text ~ "jordan OR jofotara OR JO"`; for Peppol `text ~ "peppol OR EUSR OR TSR"`; for IND `text ~ "india OR EWB OR IRN OR NIC"`; for UAE `text ~ "UAE OR FTA OR Tabby OR MEA"`; etc.
2. **Recent PRs** authored or reviewed touching the country's repos: `gh search prs --author=VashisthaCT --updated >=$(date -v-30d +%Y-%m-%d) --repo=ClearTax/<repo>` for each repo in `repos:`. Cap at 10 across all repos. Requires `dangerouslyDisableSandbox: true`.
3. **Slack channel signal** — pick the most relevant key channel from `data/people.yaml` `key_channels` or `group_dms`:
   - jordan → `mea_jordan_egypt_oman_discovery` (C0ABA7RC1QD) or `group_dms.jordan_team`
   - india → `einvoice_l3_support` (C055ABMAVCL) + `einvoice_india_mea` (C0ADWHJ2V9S)
   - uae / gcc → `einvoice_mea_l3_support` (C0AB8EAH9A6) + `einvoicing_global_platform`
   - ksa → `group_dms.ksa_deploy` (C0ANDUZ5893)
   - peppol → `group_dms.peppol_team` (C0AD7VBDX3M)
   - malaysia → `einvoicing_global_platform` (C08MX0F3F17)
   - belgium / france / poland → `einv_devs` (C04U10T2DAN)
   Read last 7 days via `slack_read_channel`. Cap at the 5 most signal-bearing messages (mentions of customer/regulator/Sev/blocker/release).

## Step 4 — Compose the briefing

Output directly in chat. ≤80 lines total. Format:

```
# <Country/Region Name> — <code/region> — <status>

**Regulator:** <name>
**Repos:** <comma-separated>
**Runbook:** <full path>
**Seed quality:** rich | medium | stub

## Snapshot
<2-3 sentences from overview.md + live_state.md: where we are, last go-live, known headwinds>

## In-flight (Jira)
- TICKET — title — status — link
(top 5; "None tracked" if empty)

## Recent PRs (30d)
- repo#NNNN — title — merged/open — link
(top 5)

## Recent channel signal
- (date) headline — Slack permalink
(top 3-5)

## Open questions
<from law_changes.md / runbook.md / overview.md "TODO" markers>

## Who to ask
<from people.md, ≤3 names with role>

## Next runbook gaps
<list TODO sections; "None — runbook is rich" if covered>
```

## Verifiable success criteria

- Output ≤80 lines.
- All 7 sections present (Snapshot / In-flight / Recent PRs / Channel signal / Open questions / Who to ask / Next runbook gaps).
- Every Jira/PR/Slack item has a link.
- If runbook is stub, `Seed quality: stub` is set and `Next runbook gaps` lists missing files.
- No fabricated tickets/PRs/messages — if a source returned nothing, say "None in 30d" not invent.

## Don't

- Don't auto-update runbook files. That's the `country-knowledge-curator` agent's job.
- Don't post the briefing to Slack — output stays in the chat session.
- Don't cite memory files that aren't in `runbooks/`. Memory files are seed sources, not live truth.
- Don't run on more than one country/region per invocation.
