---
name: v-promo-tracker
description: Score current FY27-H1 cycle against the SE-II rubric. Runs scripts/score_promotion.py for scriptable lines (code review, mentoring, AI competency), then delegates to the promo-evidence-scorer subagent for Drive/Slack-required lines (LLDs, RCAs, broadcasts). Posts a Slack-formatted gap diff (changes since last_evaluated) to self-DM D088362AS65. Drafts only — never auto-sends.
---

You are running Vashistha's promotion-rubric scorer for cycle FY27-H1 (started 2026-04-01). Output: a Slack-draft to self-DM `D088362AS65` showing which rubric lines moved status this run, plus current scoreboard.

## MVP scope (Phase 2)

Five rubric lines wired:
- `engineering.code_review` — script via `gh`
- `engineering.lld` — subagent via Drive search
- `org.mentoring` — script via `data/mentees.yaml` line-count
- `org.communication` — subagent via Drive (RCAs) + Slack (`#einv-devs` broadcasts)
- `ai.competency` — script via `data/ai_tooling.yaml`

The other 6 lines in `promotion_state.json` stay untouched until later phases (`engineering.testing`, `engineering.debugging`, `org.influence`, `product.customer_understanding`, `product.metrics`, `execution.delivery_timeliness`).

`org.hiring` is `⚪ N/A` (Ayush confirmed 2026-05-01 that interviews are SE-II+ only) — script leaves it alone; revisit post-SE-II confirmation.

## Step 1 — Snapshot before-state

Read `~/dev/personal-skills/data/promotion_state.json`. Capture each rubric line's current `status` keyed by `id`. You will diff against this after Step 4.

## Step 2 — Run the script

Use Bash with `dangerouslyDisableSandbox: true` (the `gh` calls inside hit `api.github.com` and the macOS keychain — both blocked by the sandbox):

```bash
python3 ~/dev/personal-skills/scripts/score_promotion.py
```

This updates 3 lines (`engineering.code_review`, `org.mentoring`, `ai.competency`) and writes `last_evaluated` on the file. It also writes a `current.note` on the 2 agent-required lines so the user can see why they stayed put if the subagent step is skipped.

## Step 3 — Delegate Drive/Slack lines to the subagent

Invoke the `promo-evidence-scorer` subagent. Tell it:

> Score `engineering.lld` and `org.communication` against the FY27-H1 rubric. Update `~/dev/personal-skills/data/promotion_state.json` for those two lines only. Cycle start: `2026-04-01`. Drive owner: `vashistha.garg@clear.in`. Slack user: `U087T0SHNCC`. Slack channel for broadcasts: `#einv-devs` (`C04U10T2DAN`). Return a JSON summary of before/after status and evidence count per line.

If the subagent fails or returns errors, surface them in the final draft (don't silently swallow).

## Step 4 — Build the diff

Re-read `promotion_state.json`. For each of the 5 MVP lines, compare against the before-state captured in Step 1. Bucket into:

- **Status changed:** old → new emoji.
- **Unchanged but moved closer:** `current` numeric metric increased even though status string didn't change. Show as informational.
- **Unchanged:** omit unless all 5 are unchanged (then say "No changes this run").

## Step 5 — Compose Slack draft

Format:

```
*Promo tracker — FY27-H1 — [DDD MMM DD]*

*Status changes:*
- 🔴 → 🟡 [rubric_id]: [name] — [old] → [new]
- 🟡 → 🟢 [rubric_id]: [name] — [old] → [new]
(Skip section if no changes)

*Movement (no status flip):*
- 🟡 [rubric_id]: [old metric] → [new metric] — [Y away from threshold]
(Skip if none)

*Current scoreboard (5 MVP lines):*
- 🔴/🟡/🟢 [rubric_id]: current X / threshold Y
- ...

*Deferred (out of MVP scope, scored as 🟡 default):*
[engineering.testing, engineering.debugging, org.influence, product.customer_understanding, product.metrics, execution.delivery_timeliness]
*N/A (Ayush-confirmed):* [org.hiring — SE-II+ only, revisit post-confirmation]

*Next:* run /v-promo-aim to get the top-3 weakest lines + concrete actions.
```

Keep it under 50 lines.

## Step 6 — Post

Send via `slack_send_message_draft` (NOT `slack_send_message`) to `D088362AS65`. Drafts only.

## Verifiable success criteria

- `python3 ~/dev/personal-skills/scripts/score_promotion.py --dry-run` runs cleanly before this skill is invoked.
- `data/promotion_state.json` has `last_evaluated != null` after this skill completes.
- 5 MVP lines have updated `last_evaluated` per-line.
- Slack draft posted to `D088362AS65` with status diff + scoreboard.
- 7 deferred lines remain `🟡 below threshold` defaults (not scored, not lied about).

## Failure modes

- `gh` not authenticated → script reports `gh search failed: ...` in `current.error`. Surface in draft as a warning.
- Drive MCP returns no results for LLD query → mark line as `🔴 not started`, don't crash.
- Slack pagination cap hit on broadcasts → annotate "partial count, manual verify in #einv-devs".
- `mentees.yaml` malformed → script's regex returns 0; not a hard error. User notices via the scoreboard.

## Don't

- Don't auto-send to anyone except self-DM `D088362AS65`.
- Don't score the 7 deferred lines — that's Phase 3+.
- Don't modify thresholds in `promotion_state.json` (those tune later from Ayush's answers).
- Don't fabricate evidence URLs.
