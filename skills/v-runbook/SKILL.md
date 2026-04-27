---
name: v-runbook
description: Draft or extend an oncall runbook section for a country/region OR for a recurring error code/pattern. Reads existing runbook + recent user-owned RCAs + active Jira/Slack signals, generates a section using the canonical runbook template, appends/drafts to `runbooks/countries/<cc>/runbook.md` (or `runbooks/regions/<id>/runbook.md`). Drafts only — user reviews before merging.
---

You are drafting (or extending) an oncall runbook for Vashistha. Triggered by `/v-runbook <id>` where `<id>` is one of:
- A country: `jordan`, `india`, `uae`, `ksa`, `malaysia`, `belgium`, `france`, `poland`
- A region: `peppol`, `gcc`, `mea`
- An error code or recurring pattern: `nic-100203`, `ewb-redis-lock`, `ftp-stuck`, `peppol-mls-stuck`, etc.

## Step 1 — Resolve mode

**Country/region mode:** if `<id>` matches a key under `countries:` or `regions:` in `~/dev/personal-skills/data/countries.yaml`, you are extending that entry's runbook.
- Path: `~/dev/personal-skills/runbooks/countries/<id>/runbook.md` or `runbooks/regions/<id>/runbook.md`.
- If the file doesn't exist yet, create it from `prompts/runbook_template.md`.
- If it exists, you are appending one or more **Common Cause** sub-sections, refining decision tree branches, or filling in error code rows.

**Pattern mode:** if `<id>` is an error code / recurring symptom, infer the country/region from context and treat as a country/region drafting task — append a new `### Cause: [TITLE]` block to the most-relevant runbook. If ambiguous, list candidates and stop.

## Step 2 — Load context

Read in parallel:
1. **Template:** `~/dev/personal-skills/prompts/runbook_template.md` — section shapes.
2. **Existing runbook:** the resolved `runbook.md` from Step 1 (if present). Note: existing `Common Cause`, `Decision Tree`, `Related Error Codes`, `RCAs encountered` blocks. The draft must **append** without duplicating.
3. **Country runbook siblings:** `overview.md`, `live_state.md`, `code_map.md`, `api_contract.md` — for service names, code paths, regulator URLs, error code references.
4. **People:** `~/dev/personal-skills/data/people.yaml` — for escalation block (EM, PM, regulator liaison Slack IDs).
5. **Country code maps:** `~/dev/personal-skills/runbooks/countries/<cc>/code_map.md` for repos × files implementing this country.

## Step 3 — Pull RCA evidence

Identify recent RCAs to mine for cause patterns:

1. **In-runbook history:** existing `RCAs encountered` table.
2. **Memory:** `project_perf_review_fy26.md` §6 — the 6 H2 user-owned RCA Drive IDs (filter by country relevance):
   - prod-http error% einvoicing-integrations: `1QAvRouyroO9D7UfY8vN8JnXfUhtxxmz-0a6FyCKPkJ4`
   - EWB-with-IRN Nov 18 (NIC RCF): `127Sry5vBhB0Jm5Im1PLRr45acxZ8CJemNDHasHy8Z_A`
   - Duplicate EWBs: `1uwXqEWcDkTRIHeJXNO7tqd5yKLTyxMayM9NOlhPHcNw`
   - EWB-via-IRN 100203: `1DMhuqr6vNx808HaBb-jcpErKem3U5Dkjp_F4FnK1v94`
   - FTP stuck: `1UJfGZFXU2FfAj35HJWzmo_fb-ClZTVjMxNv1qctdGis`
   - autoTaxCalculate: `151X87SrjG6IPQs61dY4q30eUUqq6kbviXuCOhZxpIEI`
   - B2C invoice gen: `1oPwpjXEiolMe68FrE7EH8KcsweFCHOgw7ejDUX5medE`
3. **Drive search** for additional user-owned RCAs in this country (last 90d): `mcp__ff2234ae-562b-49a3-a15e-83ee23736f08__search_files` with `fullText contains "<country/error>" AND fullText contains "RCA OR RCF"` and ISO 8601 `Z`-suffixed `modifiedTime`. Filter client-side by `owner == "vashistha.garg@clear.in"`. Skip parent `1i0Msm1KKgwpCdsWtfjfcoT_21zuxMcuF` (Meet Transcripts).
4. **Local incident drafts:** `~/dev/personal-skills/data/incidents/*/rca.md` matching the country/pattern.
5. **Drafts you read should land in `RCAs encountered`** with date + title + Drive URL.

For each RCA found, extract: cause title, identifying signal, fix path, prevention. These become **Common Cause** sub-sections.

## Step 4 — Pull live signals

1. **Jira** — JQL via cloudId `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`: `text ~ "<country>" AND project = SEV1BUGS ORDER BY created DESC` (cap 10) — recent Sev tickets for error code references and prevention items.
2. **Slack** — last 7 days in the country's L3 channel (from `data/people.yaml` `key_channels` / `group_dms`):
   - india → `einvoice_l3_support` (C055ABMAVCL), `einvoice_india_mea` (C0ADWHJ2V9S)
   - uae / gcc → `einvoice_mea_l3_support` (C0AB8EAH9A6)
   - ksa → group DM `C0ANDUZ5893`
   - jordan → `mea_jordan_egypt_oman_discovery` (C0ABA7RC1QD)
   - peppol → group DM `C0AD7VBDX3M`
   - other → `einv_devs` (C04U10T2DAN)

   Cap at 5 signal-bearing messages (mentions of error code, customer, Sev). Use to find symptom phrasings + escalation triggers.

## Step 5 — Compose the draft

Open `prompts/runbook_template.md`. For each new piece (cause, decision branch, error code row, escalation update):

- **Common Cause block:** mandatory triplet — how-to-identify, resolution, prevention. Link the source RCA under "Related RCAs".
- **Decision Tree update:** if a new symptom routes to an existing cause, add a numbered branch. If it's a new branch, slot it into existing numbering — don't renumber the whole tree.
- **Error code row:** code | meaning | source (regulator/vendor) | action (retry / surface / escalate).
- **Escalation:** keep functional roles. Update only if `data/people.yaml` shows a change.

Rules:

- **No name-dropping** in the body. Functional roles only ("L2 team", "EM", "platform team"). Slack permalinks may carry names naturally.
- **Don't fabricate signals.** If a cause's "how to identify" is uncertain, mark `[TODO — capture signal from next occurrence]`.
- **Don't duplicate existing blocks.** Read the file first; if `Cause: X` already exists, refine it, don't re-add.
- **Cross-reference RCAs.** Every new Common Cause cites at least one Drive RCA URL or local `data/incidents/<slug>/rca.md` path.
- **Keep template section headers verbatim** so `/v-country-brain` can parse them.

## Step 6 — Write the draft

**Mode A — file exists:** append the new sections in place (insert before `## Logs to grep` if that's the last section, otherwise after the last `### Cause:` block). Do NOT touch unrelated sections.

**Mode B — file doesn't exist:** create from template, fill the country/region-specific scaffolding (services, regulator URL, escalation channel from `data/people.yaml`), leave non-evidenced sections as `[TBD]`.

In both modes, output a diff summary in chat:
```
Updated: runbooks/countries/<cc>/runbook.md
+ Cause: <title> (sources: <RCA URLs>)
+ Decision branch: step <n>.<x>
+ Error code: <code>
+ RCAs encountered row: <date> — <title>
```

Do **not** post to Slack. This skill is local-write only — `/v-runbook` is a build-time tool, not a comms tool.

## Verifiable success criteria

- The target `runbook.md` exists after the run.
- Every new Common Cause block has all three sub-sections (how-to-identify, resolution, prevention).
- At least one new block references a real Drive RCA URL or a `data/incidents/<slug>/rca.md` path.
- No prior content was deleted or renumbered without reason.
- Diff summary printed in chat.

## Don't

- Don't post the draft to Slack — local-write only.
- Don't auto-publish or sync to Drive.
- Don't run on more than one `<id>` per invocation.
- Don't introduce names into the runbook body. Functional roles only.
- Don't fabricate decision branches. If you don't know the routing question, mark `[TODO]`.
- Don't run if `prompts/runbook_template.md` is missing — abort.
