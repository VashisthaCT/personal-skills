---
name: v-friday
description: Friday wrap. Composes weekly status (/v-status) + top-3 weakest promo lines (/v-promo-tracker output) + stuck-JIRA list + 1:1 flags for next Mon Ayush sync. Single Slack-formatted draft to self-DM. Triggered Fri 17:00 IST cron or manual.
---

You are running Vashistha's Friday wrap. Output: ONE Slack-formatted message drafted to self-DM `D088362AS65`. Sections divided by `———`. Total ≤ 100 lines.

## Output format

```
*Friday wrap — [Mon DD] – [Fri DD]*

*A. Weekly status (draft for Ayush):*
[Done / In-flight / Blockers / Next from /v-status]

———

*B. Promo gaps — top 3 weakest:*
- 🔴/🟡 [rubric_id]: current X / threshold Y — rationale: <one-line>
- ...

———

*C. What's stuck:*
- [JIRA-XXX] — <title> — <status> for <N>d — <one-line "what's stuck">
(skip section if nothing stuck)

———

*D. 1:1 flags for Mon with Ayush:*
*Decisions waiting on Ayush:*
- <thread permalink> — <topic>
*Promo gaps needing his input:*
- <Q from §7 of project_personal_skills>: <why this week>
*Concerns / risks:*
- 🔴 [rubric_id]: <blocker note>
(omit any subsection that is empty)
```

## Step 1 — Section A: weekly status

Run `/v-status` logic (or call the v-status skill directly). Embed its full output as Section A. The skill's draft goes to `D088362AS65` already — for `/v-friday`, capture the formatted body and inline it (don't double-post).

If `/v-status` fails / returns empty, write: `Status section unavailable — run /v-status manually before sending to Ayush.`

## Step 2 — Section B: promo top-3 weakest

Read `~/dev/personal-skills/data/promotion_state.json`. Filter `rubric_lines` where `status` starts with 🔴 or 🟡. Sort:
1. 🔴 first.
2. Then 🟡, ranked by `(current.value / threshold)` ratio ascending (most below first).

Take top 3. Each line:

`- 🔴/🟡 <id>: current <X> / threshold <Y> — rationale: <one-line>`

Rationale is derived from the rubric line's `data_source.type`:
- `gh_search` → "X substantive 3rd-party reviews this cycle, need Y"
- `drive_search` → "X LLDs filed, need Y"
- `mentees_yaml` → "X touchpoints logged, need Y"
- `slack_search` → "X broadcasts in #einv-devs, need Y"
- `ai_yaml` → "<level> AI competency, target <next level>"

If `promotion_state.json` doesn't exist or is empty, write: `Promo state not initialized — run /v-promo-tracker first.`

## Step 3 — Section C: what's stuck (JIRA)

Use the Atlassian MCP. JQL:

```
assignee = currentUser() AND status not in (Done, Closed, Cancelled, Resolved) AND updated <= -5d
```

(`accountId 712020:7bdcfdb0-f37e-47b8-80cb-54f774e7d913`, `cloudId e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`.)

For each ticket:
- `<key> — <summary (truncate 60)> — <status> for <Nd> — <one-line: what's stuck>`

`<one-line: what's stuck>` is inferred:
- Status `In Review` >5d → "PR review pending"
- Status `In Progress` >5d → "no movement — re-scope or unblock"
- Status `Blocked` (or label `blocked`) → "explicitly blocked — surface in §D"
- Status `To Do` >5d in active sprint → "claimed but not started — drop or pick up"
- Other → "stale — check status"

Cap at 5 tickets, sorted by days-since-last-update descending. If none stuck: omit Section C entirely (don't write "None" — just skip the divider too).

If Atlassian MCP is unavailable / errors, write: `JIRA stuck-detection unavailable — Atlassian MCP error. Check manually.`

## Step 4 — Section D: 1:1 flags for Mon with Ayush

Three subsections; omit any that are empty.

### D.1 — Decisions waiting on Ayush

Slack search via `slack_search_public_and_private`:

```
from:U087T0SHNCC after:<7d ago> ("@U0ABBKV5QDU need decision" OR "@U0ABBKV5QDU your call" OR "@U0ABBKV5QDU thoughts" OR "@U0ABBKV5QDU input needed")
```

Top 3 results. Format: `- <permalink> — <one-line topic>`

### D.2 — Promo gaps needing Ayush's input

Read the 10 deferred Ayush questions from `~/.claude/projects/-Users-vashistha-garg/memory/project_personal_skills.md` (§7, "10 questions for Ayush"). Pick the top 2 most relevant to the current week's work:

Heuristic for relevance:
- If Section B's top-3 weakest includes `org.hiring` → Q1.
- If Section B includes `org.mentoring` → Q2.
- If Section B includes `ai.competency` → Q3.
- If Section B includes `engineering.testing` → Q4.
- If Section B includes `engineering.lld` → Q5.
- If Section B includes `engineering.code_review` → Q6.
- If Section B includes `org.influence` → Q7.
- If recent journal mentions deploy / cloud-init / ct-app-config → Q8.
- If active project has cross-team coordination flag → Q9.
- If Peppol or Jordan in active projects with go-live ambiguity → Q10.

Take the top 2 matches. Each: `- Q<N>: <abbreviated question> — surfaces because <reason from heuristic>`

If nothing matches, fall back to Q3 + Q6 (most-evergreen).

### D.3 — Concerns / risks

For each rubric line in `promotion_state.json` where `status` starts with 🔴 AND a `blocker` field exists with non-empty value:

`- 🔴 <id>: <blocker text>`

Cap at 3. If none, omit subsection.

## Step 5 — Compose & post

Single Slack message via `slack_send_message_draft` to `D088362AS65`. Sections divided by `———`. Total ≤ 100 lines.

## Verifiable success criteria

- 4 sections (A/B/C/D) — Section C may be omitted if nothing stuck; Section D subsections may be omitted individually.
- Section A is the full `/v-status` output (Done / In-flight / Blockers / Next).
- Section B has exactly top-3 from `promotion_state.json` (or fewer if file has <3 🔴/🟡 lines).
- Section C JIRA list ≤ 5, sorted by stale-days desc.
- Section D.2 has 2 questions max (with fallback to Q3+Q6 if heuristic finds none).
- Posted to `D088362AS65` only.
- Total ≤ 100 lines.

## Failure modes

- `/v-status` returns empty → Section A says "unavailable", rest of skill still runs.
- `promotion_state.json` missing → Section B + D.3 say "Promo state not initialized"; D.2 falls back to Q3+Q6.
- Atlassian MCP not connected → Section C says "JIRA unavailable, check manually".
- Slack search returns 0 results for D.1 → omit subsection.
- Memory file `project_personal_skills.md` missing or §7 missing → D.2 falls back to Q3+Q6 from inline defaults below.

### Inline fallback for §7 questions (if memory file unreadable)

- Q3: AI competency target for next cycle (L4 vs sustained L3)?
- Q6: Code review volume — is ≥10 substantive 3rd-party per half right?

## Don't

- Don't auto-send to Ayush. Drafts to self-DM only — user reviews, edits, sends.
- Don't include hiring/mentoring evidence in Section A (that's Section B/D's job).
- Don't pad Section B beyond top-3 weakest — extras dilute the signal.
- Don't `git commit`.
- Don't fabricate JIRA tickets. If MCP fails, say so.
- Don't re-ask Ayush questions that the user has already pasted answers for (check `promotion_state.json` for `ayush_answer` fields on rubric lines — if present, drop the matching Q from D.2).
