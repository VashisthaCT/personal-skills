---
name: v-pr-day
description: On-demand PR-day kit. Composes 3 sections into one self-DM draft — (A) review queue PRs awaiting your review sorted by author seniority then age, (B) own open PRs with pre-flight gaps + age heuristics, (C) gentle DM nag drafts for stale review-waits. Drafts only. Triggered manually.
---

You are running Vashistha's PR-day kit. Output: a single Slack-formatted message drafted to self-DM `D088362AS65`.

## Output format

```
*PR day — [DDD MMM DD]*

*A. Review queue (PRs awaiting your review):*
- repo#PR — author — title — age — link
(up to 10; flag any requested >5d ago)

———

*B. Own PR pre-flight (your open PRs):*
- repo#PR — title — age — action: <one-liner>
(up to 10)

———

*C. Waiting-on-review nags (DM drafts):*
> To <name> (DM <dm-id>):
> Hey <name>, any chance you can take a look at <repo#PR> — the <feature> for <project>? Happy to walk through over a call if helpful.
(max 3 drafts; one per stale reviewer)
```

## Step 1 — Section A: review queue

Use Bash with `dangerouslyDisableSandbox: true` (gh hits api.github.com + macOS keychain — both blocked by sandbox):

```bash
gh search prs review-requested:VashisthaCT is:open --limit 30 --json url,title,author,createdAt,repository
```

For each PR returned:
1. Compute `age_days = today - createdAt` (round down).
2. Compute author seniority bucket from `~/dev/personal-skills/data/people.yaml`:
   - **Tier 1 (managers / architects / directors)** — `relationship` in `manager`, `architect`, `director`, `em`, `tech-lead`. From the file: Ayush Jain (manager), Febin Sathar (architect), Vikas Jethnani (director), Abhilash Pareek (em), Anand Mohan (tech-lead).
   - **Tier 2 (PMs)** — `relationship: pm`.
   - **Tier 3 (peers + everyone else)** — default.
3. Sort: Tier 1 → Tier 2 → Tier 3, then by `age_days` descending within each tier.
4. Take top 10.
5. Format each as: `<repo>#<number> — @<author> — <title (truncate at 60 chars)> — <age_days>d — <url>`
6. If `age_days > 5`, prefix with `⚠️ ` (the user has been requested for >5 days).

If no PRs returned, write `None — review queue clear.`

## Step 2 — Section B: own PR pre-flight

```bash
gh search prs author:VashisthaCT is:open --limit 30 --json url,title,createdAt,statusCheckRollup,reviewDecision,reviewRequests
```

For each own open PR, derive a pre-flight action with these heuristics (apply in order, first match wins):

1. `reviewRequests` empty (zero reviewers requested) → action: `request review` (note repo CLAUDE.md may have a default reviewer set).
2. `reviewDecision == "CHANGES_REQUESTED"` AND `age_days > 7` → action: `address feedback (CHANGES_REQUESTED, sitting >7d)`.
3. `statusCheckRollup` contains any `state: "FAILURE"` → action: `fix failing CI`.
4. `age_days > 14` → action: `is this still alive? close or rebase`.
5. `reviewDecision == "APPROVED"` → action: `merge (approved, mergeable)`.
6. None of above → action: `wait — review pending`.

Format: `<repo>#<number> — <title (truncate 60)> — <age_days>d — action: <action>` — `<url>`

Take top 10 sorted by age descending. If empty: `None — no open PRs.`

## Step 3 — Section C: waiting-on-review nag drafts

For each PR from Section B where `reviewRequests` is non-empty AND any single reviewer has been requested for >5 days without a review:

1. Identify the stalest single reviewer per PR (one DM draft per stale reviewer, even if PR has multiple).
2. Look up reviewer in `~/dev/personal-skills/data/people.yaml`:
   - Match by GitHub login → fall back to slack `id` field if it matches the GH handle pattern (e.g. `clearsushant` → `id: sushant-gupta`).
   - Pull `name`, `dm` (if present), and `role`.
3. If no `dm` field on the person, skip the draft (the user can DM via Slack manually) and surface as a one-liner: `<name> — no DM id on file; ping manually`.
4. If reviewer is not in `people.yaml`, skip (don't draft DMs to strangers).

Cap at 3 drafts (most-stale-first by request age). For each, write:

```
> To <name> (<role>) — DM <dm-id>:
> Hey <first-name>, any chance you can take a look at <repo>#<number> — <feature> for <project>? Happy to walk through over a call if helpful.
> Link: <url>
```

`<feature>` and `<project>` come from the PR title — trim aggressively, no editorializing. If the title is opaque, just use the title verbatim.

If no stale reviewers, write: `None — no nag drafts needed.`

## Step 4 — Compose & post

Single Slack message via `slack_send_message_draft` to `D088362AS65`. Sections divided by `———`. Total ≤ 80 lines.

## Verifiable success criteria

- 3 sections present (A / B / C), each with content or `None`.
- Section A sorted by tier (manager/architect/director first → PM → peer), then age desc.
- Section B has a one-line action per own PR matching the heuristics above.
- Section C nag drafts only for reviewers in `people.yaml` with a `dm` field.
- Posted to `D088362AS65` only — no auto-DM-send to reviewers.
- Total ≤ 80 lines.

## Failure modes

- `gh` not authenticated → both gh calls fail. Surface `gh search failed: <error>` in place of the affected section.
- `gh` returns >30 PRs (rare) → top-10-by-tier-then-age in Section A; truncate Section B to top 10; note "+N more truncated".
- `people.yaml` malformed → fall back to Tier 3 sort by age desc; print warning in the draft footer.
- Reviewer GH handle doesn't match any `id` in `people.yaml` → skip nag draft for that reviewer (don't guess).

## Don't

- Don't auto-DM the reviewers — drafts to self-DM only.
- Don't include closed/merged PRs in any section.
- Don't editorialize PR titles ("seems important", "high-priority"). Just pass through.
- Don't draft a nag to Ayush — he's the manager, the user nags him in 1:1 (covered by `/v-friday`), not via DM.
- Don't `git commit`.
