---
name: v-timed-feature
description: Wrap a feature build with a timer and retro template. Generates AI L4 promotion evidence (sprint→day before/after). Usage "/v-timed-feature start <feature-name>" begins a session; "/v-timed-feature end" produces a retro doc with quantified time savings. Updates promotion_state.json ai.competency.
---

You are timing Vashistha's feature build for AI L4 evidence (rubric line `ai.competency`, threshold: ≥3 features with quantified before/after time + ≥1 published workflow doc + ≥1 multi-step agent workflow live).

## Modes

### `start <feature-name>`

1. Slugify name (lowercase, hyphenated): e.g. "Jordan UBL validation v1" → `jordan-ubl-validation-v1`.
2. Create `~/dev/personal-skills/data/timed_features/<slug>/`.
3. Prompt user for: estimate without AI assistance (gut feel — "without Claude Code, this would take ~5 days"). Required.
4. Write `meta.yaml`:
   ```yaml
   feature_name: <name>
   slug: <slug>
   started_at: <ISO-8601 IST>
   estimate_without_ai: <user input, e.g. "5 days">
   tools: [claude-code]
   related_jira: <optional, prompt user>
   status: in_progress
   ```
5. Self-DM ack to `D088362AS65`: "⏱️ Timing started for `<feature>` at `<time>`. Estimated without AI: `<X>`. Run `/v-timed-feature end <slug>` when shipped."

### `end [<slug>]`

1. If `<slug>` not given: find the most recent `data/timed_features/*/meta.yaml` with `status: in_progress`.
2. Read `meta.yaml`.
3. Compute elapsed time (`started_at` → now, in days/hours).
4. Prompt user for:
   - PR links (one or more)
   - JIRA ticket(s) — optional
   - Files changed (number)
   - Lines added/removed
   - 3-line "what I'd have done without AI" (the manual approach)
   - 3-line "what changed with AI" (where AI saved time)
   - 1-line "learnings" (carry-forward)
5. Compute speedup ratio: `estimate_without_ai / actual_time`.
6. Write `retro.md` from `~/dev/personal-skills/prompts/timed_feature_retro.md`, filled in.
7. Update `meta.yaml`: `status: shipped`, `shipped_at: <ISO>`, `actual_time: <duration>`, `speedup: <ratio>`.
8. Update `~/dev/personal-skills/data/promotion_state.json`:
   - `rubric_lines[id="ai.competency"].current.timed_features_logged` += 1
   - Append to `current.evidence`: `{slug, retro_path, speedup}`
   - If `timed_features_logged >= 3` and `workflow_docs >= 1` and `agent_workflows_live >= 1`: flip status to `🟢 L4 attainable — needs team-adoption metric for L5`.
9. Self-DM: "✅ `<feature>` shipped in `<actual>`. Without-AI estimate: `<estimate>`. Speedup: `<ratio>×`. Retro: `<path>`."

## Constraints

- File-based timer. No background daemon.
- The "without AI" estimate is user-provided and subjective — that's the baseline. Don't try to auto-detect.
- Drafts only — `retro.md` lives locally; user decides when/whether to publish to Drive.
- Don't write the retro to `data/work-journal/` — that's auto-managed by `daily-documentation`. Keep `data/timed_features/` separate.

## Verifiable success

- After `start`: `data/timed_features/<slug>/meta.yaml` exists with `status: in_progress`.
- After `end`: `meta.yaml` `status: shipped`, `retro.md` exists, `promotion_state.json` `timed_features_logged` incremented.
- 5 logged retros over 2 quarters → user has the L4 evidence asked for in Section E of the rubric extraction.

## Don't

- Don't auto-publish the retro to Drive.
- Don't fabricate the "without AI" estimate.
- Don't trigger this for trivial tasks (1-line fixes, config tweaks). Only for features ≥1 day of focused work.
