---
name: v-standup
description: Draft today's standup (Yesterday / Today / Blockers) for the IND/MEA + Malaysia standups from the auto-harvested work-journal + GitHub last 24h + Jira in-progress + today's calendar. Output lands as a draft in self-DM (D088362AS65). Drafts only — never auto-sends.
---

You are drafting Vashistha's standup for today's `EInvoice India/Mea Standup` (10:00 IST, ~30 min) and `Standup: E-Invoicing Malaysia` (15 min). Output ONE shared draft both standups can use.

## Output format

```
*Yesterday:*
- bullet — link
- bullet — link

*Today:*
- bullet — link

*Blockers:*
- bullet (or "None")
```

Each section ≤3 bullets. Slack-formatted bullets (`-`). Links inline.

## Step 1 — Read sources

1. Yesterday's section in `~/dev/personal-skills/data/work-journal/Projects.md` (auto-populated by `daily-documentation` cron).
2. Yesterday's section in `~/dev/personal-skills/data/work-journal/Small Wins.md`.
3. GitHub PRs authored or merged in last 24h: `gh search prs --author=VashisthaCT --updated >=$(date -v-1d +%Y-%m-%d)` — requires `dangerouslyDisableSandbox: true`.
4. Jira tickets in In Progress / In Review assigned to user (cloudId `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`, accountId `712020:7bdcfdb0-f37e-47b8-80cb-54f774e7d913`) — JQL: `assignee = currentUser() AND status in ('In Progress', 'In Review')`.
5. Today's calendar 9:00–19:00 IST (skip recurring standups; flag warrooms / 1:1s / meeting-prep-needed events).
6. Active blockers: search yesterday's Slack messages by user `U087T0SHNCC` for "blocked", "waiting on", "stuck on", "need help".

## Step 2 — Compose

- Cap each section at 3 bullets (5 max). Brevity matters.
- PR/Jira links inline as Slack-style links: `<https://github.com/.../pull/1234|repo#1234>`.
- Don't editorialize. Don't claim work that's not in the harvested data.
- If a workstream from `data/active_projects.yaml` (priority P0) had no movement in 24h, flag in Blockers.

## Step 3 — Output

Post the draft as a Slack message to self-DM `D088362AS65` via `slack_send_message_draft` (NOT `slack_send_message`). User reads, edits, copies to actual standup channel.

## Verifiable success criteria

- Output is a Slack-formatted draft posted to `D088362AS65`.
- 3 sections (Yesterday/Today/Blockers) each ≤3 bullets.
- All claims trace to one of the 6 sources.
- No auto-send to channels.

## Don't
- Don't fabricate yesterday work that's not in the journal.
- Don't post to standup channels.
- Don't mark something as done without a merged PR or Jira "Done" status.
