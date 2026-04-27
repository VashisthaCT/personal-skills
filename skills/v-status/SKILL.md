---
name: v-status
description: Draft a weekly status DM to manager Ayush in Done / In-flight / Blockers / Next bulleted format. Reads last 7d of work-journal + Jira Done + PRs merged + Slack blockers + active_projects.yaml. Output lands as draft in self-DM. Drafts only.
---

You are drafting Vashistha's weekly status update to Ayush Jain (manager, Slack `U0ABBKV5QDU`, DM `D0AC1AKDJKT`). Triggered Friday 17:00 IST.

## Output format

```
*Week of [Mon DD] – [Fri DD]*

*Done:*
- [PROJECT/TICKET]: [what shipped] — [PR/Jira link]

*In-flight:*
- [PROJECT/TICKET]: [current state] — ETA [date or "next sprint"]

*Blockers:*
- [What's blocked] — waiting on [name/team]
(Skip section if empty)

*Next week:*
- [Top 3-5 items]
```

## Step 1 — Read sources

1. Last 7 days of `~/dev/personal-skills/data/work-journal/Projects.md` — sections moved to Shipped + new Log entries.
2. Last 7 days of `~/dev/personal-skills/data/work-journal/Small Wins.md`.
3. GitHub PRs authored merged in last 7d: `gh search prs --author=VashisthaCT --merged >=$(date -v-7d +%Y-%m-%d)` (`dangerouslyDisableSandbox: true`).
4. Jira tickets moved to Done in last 7d: `assignee = currentUser() AND status changed to Done after -7d`.
5. Active In-flight Jira: `assignee = currentUser() AND status in ('In Progress', 'In Review')`.
6. Slack threads with "blocked", "waiting on" by user in last 7d.
7. `data/active_projects.yaml` — for each project in state=active or solutioning, surface next milestone.

## Step 2 — Compose

- **Done:** top 3-5 items (P0 + P1 first). PR/Jira link per item.
- **In-flight:** top 3 items. ETA where you have one (from `next_milestone` in `active_projects.yaml`).
- **Blockers:** only if real (omit section if empty). Name what's blocking + who can unblock.
- **Next week:** 3-5 items from in-flight + active_projects next milestones.

Tone: terse, manager-ready. No culture/learning content (that goes in `/v-broadcast`, not status).

## Step 3 — Output

Post draft to self-DM `D088362AS65` via `slack_send_message_draft`. User reviews, edits, sends to Ayush DM `D0AC1AKDJKT` themselves.

## Verifiable success criteria

- 4 sections (Done / In-flight / Blockers / Next) — Blockers omitted if none.
- ≤5 bullets per section.
- Every Done bullet has a link.
- Posted to self-DM `D088362AS65`, NOT to Ayush's DM.

## Don't
- Don't auto-send to Ayush.
- Don't include hiring/mentoring evidence here (that's for `/v-promo-tracker`).
- Don't pad with low-priority chore PRs.
