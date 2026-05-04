---
name: v-journal
description: Append-only artefact log for SE-II promo prep (Oct 2026 review cycle). Harvests Slack DMs/threads, JIRA tickets resolved, GitHub PRs (authored + reviewed), Drive docs since the last journal entry date and buckets each artefact into Small Wins / Big Wins / Reviews. Skips noise (status pings, in-flight chatter, recommendations without docs). Scope: cycle FY27-H1 onwards (≥2026-04-01).
---

You are running Vashistha's work-journal harvester. The journal at `~/dev/personal-skills/data/work-journal/` is the canonical artefact log for Oct-2026 SE-II review cycle prep. Append-only — never rewrite past entries.

## Step 0 — Sanity

Working dir: `~/dev/personal-skills/data/work-journal/`. Standalone git repo (remote `VashisthaCT/work-journal`); the parent `personal-skills` gitignores it.

```bash
cd ~/dev/personal-skills/data/work-journal && git pull origin main
```

After updates, commit + push back to `origin/main`. Use `dangerouslyDisableSandbox: true` for git push (macOS keychain access for the GitHub credential helper).

## Step 1 — Determine harvest window

`harvest_from` = max date heading found across `Big Wins.md`, `Small Wins.md`, `Reviews.md` — regex `^### (\d{4}-\d{2}-\d{2})`. If none found, `harvest_from = 2026-04-01` (FY27-H1 cycle start).

`harvest_to` = today (IST).

If `harvest_from >= harvest_to`, skip — print `Journal is current.` and exit.

## Step 2 — Harvest sources

Delegate to a single subagent (`perf-evidence-harvester` or `general-purpose`) so the parent context stays light. Brief prompt template:

> Harvest Vashistha's completed work artefacts for the window `<harvest_from>` → `<harvest_to>`. Identifiers: email `vashistha.garg@clear.in`, Slack `U087T0SHNCC`, accountId `712020:7bdcfdb0-f37e-47b8-80cb-54f774e7d913`, cloudId `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`, github `VashisthaCT`. Sources to pull: (A) merged PRs I authored, with LOC + files + JIRA cross-link; (B) PRs I reviewed (any author except me), with my comment count + change-request flag; (C) JIRA tickets I resolved; (D) Drive docs I created — RCA / LLD / HLD / design / 1-pager / broadcast; (E) Slack design / solution threads in #einv-devs (C04U10T2DAN), #einvoice-india-mea (C0ADWHJ2V9S), #einvoice-l3-support (C055ABMAVCL), #einvoicing-global-pr (C09TU9UMJJ2); (F) Slack DMs / group DMs from me containing PR or doc URLs. Return a JSON blob with one record per artefact: `{type, date, title, url, jira_key, jira_url, jira_priority, repo, pr_number, pr_url, pr_loc, pr_files, pr_status, doc_url, slack_permalink, my_review_comments, change_requests, author, summary}`. Skip standup posts, status pings, meeting messages, in-flight chatter without a stable URL.

If subagent fails, surface error and don't fabricate entries. Don't proceed to Step 3.

## Step 3 — Bucket each artefact

Read existing `(JIRA-key, PR-URL)` tuples from all 3 files for idempotency. Skip any new artefact that matches an existing tuple.

For remaining artefacts:

### Reviews.md
- Goes here if: I reviewed the PR, I am NOT the author.
- All reviews logged. Mark `[substantive]` if `my_review_comments >= 5 AND change_requests >= 1`.
- Format:
  ```
  ### YYYY-MM-DD — <PR title (truncate 80)>
  - **PR:** [repo#NNN](url)
  - **Author:** @author-handle
  - **My comments:** N
  - **Substantive:** ✅ / ❌
  ```

### Big Wins.md
- Goes here if ANY of:
  - Multiple PRs linked to the same JIRA epic/parent
  - Single PR with `(additions + deletions) > 500` LOC OR `changedFiles > 10`
  - Has a Drive/Confluence doc (RCA, LLD, HLD, broadcast, 1-pager) — even without a fix-PR yet
  - JIRA Bug at P0/P1 with shipped PR
  - Long-form Slack design thread (≥150 chars + technical content + PR/doc link in thread) — log everything per philosophy; filter at promo-prep time
- Format:
  ```
  ### YYYY-MM-DD — <name>
  - **JIRA:** [KEY](url) [P0/P1/P2/none]
  - **PRs:** [repo#NNN](url) (merged main YYYY-MM-DD), ...
  - **Doc:** [title](drive/confluence url)  (omit row if no doc)
  - **Slack:** [thread](permalink)  (omit row if no slack)
  - **Note:** 1-2 line summary of what shipped + business impact if known
  ```

### Small Wins.md
- Goes here if: single PR, < 500 LOC, single module, bug-fix-y title, no design doc.
- Format:
  ```
  ### YYYY-MM-DD
  - [JIRA-KEY](url) — short description ([repo#NNN](pr-url), merged main YYYY-MM-DD)
  ```

### One-incident, multiple-entry rule
RCAs and their subsequent action-item PRs are SEPARATE entries. The RCA goes in Big Wins (always Big — solution doc). When an action-item PR ships later, it gets its own Small or Big Win entry depending on size. Cross-reference both via the JIRA epic key.

## Step 4 — Append to files

For each new entry, INSERT under the file's `## Entries` heading, in **reverse-chronological order** (most recent first).

If a date heading already exists in Small Wins.md, append the new bullet under that date. For Big Wins / Reviews, each artefact gets its own `### YYYY-MM-DD — <name>` heading.

## Step 5 — Commit + push

```bash
cd ~/dev/personal-skills/data/work-journal
git add "Big Wins.md" "Small Wins.md" Reviews.md
git commit -m "v-journal: <harvest_from> → <harvest_to> harvest"
git push origin main
```

Use `dangerouslyDisableSandbox: true` on the push (keychain).

## Step 6 — Report

Print to chat:
```
Harvest window: <from> → <to>
Added: <N> Big Wins, <M> Small Wins, <K> Reviews (<S> substantive)
Skipped (already in journal): <X>
Skipped (filtered noise): <Y>
Pushed to origin/main: <commit-sha>
```

## Verifiable success criteria

- `harvest_from` correctly determined from the max date heading across the 3 files (or `2026-04-01` if files have no entries).
- 6 source types harvested (GitHub authored + reviewed, JIRA, Drive, Slack channels, Slack DMs).
- Every entry has at least: date heading + (JIRA URL OR PR URL OR doc URL) + 1-line description.
- Reviews entries flagged `[substantive]` correctly per ≥5 comments + ≥1 change-request.
- Idempotency: re-running the same window doesn't duplicate (verified by re-running with `--dry-run` semantically — search for tuples).
- Working tree clean after commit + push.

## Failure modes

- `gh` not authenticated → abort with `gh auth login required`. Don't proceed.
- Drive MCP returns 0 results → log warning, continue with other sources.
- Slack pagination cap hit (>20 msgs) → annotate "Slack search incomplete for window — verify manually".
- Push rejected (non-fast-forward) → run `git pull --rebase origin main` once, then retry. Never `git push --force`.
- `harvest_from` is in the future (clock skew) → abort.

## Don't

- Don't track in-flight tickets — that's `/v-status` / `/v-friday`.
- Don't track standup posts, meetings, status pings.
- Don't track Slack messages without a PR / doc / Slack-permalink artefact reference.
- Don't track JIRA tickets that aren't merged-to-main, **except** internal RCAs (RCA is a Big Win on its own).
- **Don't include customer-facing RCAs** — sanitized for external sharing, no engineering signal. Only internal Sev1/Sev2 briefs / engineering post-mortems with root-cause analysis qualify. Heuristic: drop docs whose title is framed as "<Customer> Issue" or "<Product> Generation Issue" — those are client-comms artefacts. Keep docs whose title starts "Sev 1:" / "Sev 2:" or names the technical component (e.g. "Redis Unavailability", "Kafka Consumer Lag").
- Don't auto-classify aggressively. When unsure between Small / Big, default to Small. User upgrades during /v-perf-review prep.
- Don't `git push --force`.
- Don't write outside `data/work-journal/*`.
- Don't track work pre-2026-04-01 (cycle start). H2-FY26 is documented separately in `perf-review-fresh/`.
