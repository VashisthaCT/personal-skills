---
name: v-broadcast
description: Draft a broadcast post for #einv-devs (C04U10T2DAN). Templates design-pattern, learnings, post-mortem. Each broadcast counts toward SE-II "≥1 broadcast post per quarter" threshold (org.communication rubric line). Drafts only — user posts manually.
---

You are drafting Vashistha's broadcast post for the team channel `#einv-devs` (`C04U10T2DAN`). Broadcast cadence is the user's weakest culture-leadership signal (1 in H2 vs 23 working messages); each post improves the `org.communication` rubric line.

## Modes

### `design-pattern <topic-or-PR>`

1. Read `~/dev/personal-skills/prompts/broadcast_templates/design_pattern.md` template.
2. Source material:
   - If `<topic-or-PR>` is a PR URL: read the PR description + diff via `gh pr view` (sandbox-disabled).
   - If `<topic-or-PR>` is a topic string: search Drive (owner=user, last 30 days, title contains "design"/"LLD") and pick the most relevant.
3. Cross-reference `data/active_projects.yaml` for project context.
4. Cross-reference relevant `runbooks/<entry>/` if pattern is country-specific.
5. Fill template placeholders.
6. Output: Slack-formatted draft, ≤500 chars (Slack canonical post length for readability).

### `learnings <incident-or-RCA>`

1. Read `~/dev/personal-skills/prompts/broadcast_templates/learnings.md` template.
2. Source:
   - If `<incident-or-RCA>` is an incident slug: read `data/incidents/<slug>/rca.md`.
   - If a Drive RCA URL: read via Drive MCP.
   - If a topic: search recent RCAs (Drive, owner=user, title contains "RCA"/"RCF", last 60 days).
3. Translate the lessons to team-applicable patterns (don't just paraphrase the RCA — extract the *general* learning).
4. Fill template.
5. Output: ≤500 chars draft.

### `post-mortem <feature-name>`

1. Read `~/dev/personal-skills/prompts/broadcast_templates/post_mortem.md` template.
2. Source:
   - If `<feature-name>` is a slug from `data/timed_features/`: read its `retro.md` + `meta.yaml`.
   - Otherwise: search work-journal `data/work-journal/Projects.md` for the feature in `## Shipped` (last 30 days).
3. Pull metrics from work-journal Outcome line + GitHub PR stats.
4. Fill template.
5. Output: ≤500 chars draft.

## Output

Single Slack-formatted post draft. Posted to self-DM `D088362AS65` via `slack_send_message_draft` (NOT to `#einv-devs` directly). User reviews, edits, posts to channel themselves.

## After user posts

When user runs `/v-promo-tracker` next, it will pick up the new post in `org.communication.current.broadcast_posts` count.

## Constraints

- Drafts only.
- Match team Slack tone: terse, technical, links inline. No hype emojis unless template specifies one.
- Cite specific PRs/Drive docs/JIRA IDs.
- Don't promise what others will do — frame as your work + invitation to discuss.
- ≤500 chars (Slack readability sweet spot). If template needs to exceed, split into a thread (post + reply).

## Verifiable success

- Draft posted to self-DM.
- ≤500 chars (or threaded if longer).
- All citations are real (PRs verified via `gh`, Drive docs verified via Drive read).

## Don't

- Don't auto-post to `#einv-devs`.
- Don't fabricate metrics.
- Don't claim team consensus you didn't validate.
- Don't broadcast platform-team-only content to a wider audience without checking the right channel.
