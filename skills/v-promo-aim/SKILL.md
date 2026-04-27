---
name: v-promo-aim
description: Read promotion_state.json and surface the 3 weakest rubric lines with one concrete action per line for this week. Sorts 🔴 first, then 🟡 by current/threshold ratio. Fast, no MCP calls — just file read + heuristics. Output to chat or self-DM D088362AS65.
---

You are answering "what should Vashistha grind on this week to close his SE-II promo gap?". Pure read-only on `promotion_state.json` — no Drive/Slack/gh calls. Run this any time, frequently.

## Step 1 — Read state

Load `~/dev/personal-skills/data/promotion_state.json`. If `last_evaluated` is `null` or older than 14 days, prepend a warning: `"⚠️ promotion_state.json is stale — run /v-promo-tracker first."` (don't refuse to run; just warn).

## Step 2 — Filter + sort

Filter `rubric_lines` where `status` starts with `🔴` or `🟡`. (`🟢` lines are met — exclude.)

Sort:
1. 🔴 first (most behind).
2. Then 🟡, ranked by ratio ascending. Compute the ratio from the line's `current` field — use whichever numeric field appears first in `current`, divided by a threshold parsed from the `threshold` string (best-effort; if parsing fails, treat ratio as 0.5).

Take the top 3.

## Step 3 — Compose action per line

For each of the 3 lines, write ONE concrete action the user can do in the next 7 days. Hardcode the suggestions from the table below — no LLM creativity here, MVP wants determinism.

| rubric_id | concrete action |
|---|---|
| `engineering.code_review` | "Review 2 substantive PRs this week from `e-invoicing-be` or `einvoicing-integrations` (≥5 review comments, ≥1 change-request). Prioritize PRs from authors not yet in `distinct_authors`." |
| `engineering.lld` | "Spend 90 min Friday converting one in-flight ticket into an LLD doc (Drive). Use the LLD template at `prompts/lld_template.md` (Phase 4). Wire it back to the ticket + a draft PR." |
| `engineering.testing` | "Pick the lowest-coverage service you touched this half. Add 5+ tests covering the new flow you shipped. PR description must cite before/after coverage delta." |
| `engineering.debugging` | "Be the first responder on 2 cross-author threads in `#einvoice-l3-support` or `#einv-devs` this week. Resolve with a PR link or a code-pointer reply." |
| `org.mentoring` | "Add 2 named SE-I mentees to `data/mentees.yaml` (id, name, slack handle, started date). Schedule a first 1:1 with each. Then log the touchpoint via `/v-mentee log <id>` (Phase 6)." |
| `org.influence` | "Find one design thread in `#einvoice-mea-l3-support` or `#einv-devs` this week, push back with a concrete alternative + tradeoff. Track whether the design changed in the follow-up PR." |
| `org.communication` | "Write one RCA-format post-mortem (NIC RCF template at `prompts/rca_template.md`) for the most recent Sev2 you handled. Post a 1-paragraph broadcast to `#einv-devs` summarizing it." |
| `org.hiring` | "Ask Ayush in next 1:1 whether SE-I/SE-II hiring panels are open to non-confirmed SE-IIs (deferred Q1). Until answered, this line stays `🔴 N/A`." |
| `product.customer_understanding` | "Pick one customer from `data/customers.yaml` (top-10). Trace one of their tickets end-to-end (JIRA + repo + Slack). Write a 1-pager learning into `data/customers.yaml` notes." |
| `product.metrics` | "In your next status update, cite at least 2 concrete numbers (failure %, p99 latency, IRN/EWB volume). Track in `current.metric_citations` evidence." |
| `ai.competency` | "Wrap your next feature in `/v-timed-feature` (Phase 6) with before/after timer. Once 3 features are logged, AI L4 flips to 🟢." |
| `execution.delivery_timeliness` | "For every Jira you have In Progress, set a `duedate`. Currently script can't measure timeliness without due dates." |

If the rubric_id isn't in the table, write: `"(no canned action — write a manual plan in 1:1 prep)"`.

## Step 4 — Output

Default: print to chat. If user said `--draft` in args, post to self-DM `D088362AS65` via `slack_send_message_draft`.

Format:

```
*This week's promo aim — top 3 weakest rubric lines*

1. 🔴/🟡 [rubric_id]: [name]
   Current: [X] / Threshold: [Y]
   This week: [action from table]

2. ...

3. ...

*Run /v-promo-tracker on Sunday to refresh state.*
```

Keep total output under 30 lines.

## Verifiable success criteria

- 3 lines surfaced, sorted 🔴 first, then 🟡 by ratio.
- Each line has a concrete action (from table; no improvisation).
- No MCP calls (this skill is fast, deterministic).
- If `--draft`: posted to `D088362AS65`. Else: printed to chat.

## Don't

- Don't query Drive/Slack/gh — that's `/v-promo-tracker`'s job.
- Don't write to `promotion_state.json` (read-only skill).
- Don't surface 🟢 lines — user has cleared those.
- Don't fabricate actions outside the canned table.
