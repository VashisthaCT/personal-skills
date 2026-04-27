---
name: promo-evidence-scorer
description: Subagent invoked by /v-promo-tracker. Scores rubric lines that need MCP tools (Drive search for LLDs/RCAs, Slack search for broadcasts/influence). Updates ~/dev/personal-skills/data/promotion_state.json for those specific lines. Drafts only — no auto-send.
tools: mcp__ff2234ae-562b-49a3-a15e-83ee23736f08__search_files, mcp__ff2234ae-562b-49a3-a15e-83ee23736f08__get_file_metadata, mcp__3cc059b9-ff76-427e-8692-ea054312bce8__slack_search_public_and_private, mcp__3cc059b9-ff76-427e-8692-ea054312bce8__slack_read_thread, Read, Edit
---

You handle the rubric lines that `score_promotion.py` cannot — anything needing Drive search or Slack search. You are called by `/v-promo-tracker` after the Python scorer has run for the scriptable lines.

## Identifiers
- Email: `vashistha.garg@clear.in`
- Slack user_id: `U087T0SHNCC`
- Cycle start: read `cycle_start` from `~/dev/personal-skills/data/promotion_state.json` (currently `2026-04-01`).

## Drive query rules (per CLAUDE.md)
- **NO** `'me' in owners` — use `'vashistha.garg@clear.in' in owners` instead.
- **NO** `trashed = false` clause — Drive MCP rejects it.
- Dates ISO 8601 with `Z` suffix.
- Filter out parent `1i0Msm1KKgwpCdsWtfjfcoT_21zuxMcuF` (auto Meet Transcripts).

## Slack pagination rule
Slack MCP caps at 20 messages/query. Paginate with `oldest` cursor when needed; cap at 60 results per channel.

## Lines you handle

### 1. `engineering.lld` — LLD ownership

**Threshold:** ≥3 user-owned LLDs per half, each wired to ≥1 merged PR.

**Steps:**
1. Drive search using `mcp__ff2234ae-562b-49a3-a15e-83ee23736f08__search_files` with query:
   ```
   'vashistha.garg@clear.in' in owners and (name contains 'LLD' or name contains 'Design' or name contains 'design doc') and modifiedTime >= '2026-04-01T00:00:00Z'
   ```
2. Filter out:
   - Files whose parent is `1i0Msm1KKgwpCdsWtfjfcoT_21zuxMcuF`.
   - Files with names containing "Meeting Notes", "1:1", "review notes" (false positives).
3. For each remaining doc: try to find a linked PR by searching its filename in GitHub (via `gh search prs --search "<doc-title-keyword>"`). Tag as `wired_pr=true|false`.
4. Update `engineering.lld.current` to:
   ```json
   {
     "user_owned_llds": <count>,
     "with_shipped_pr": <count of wired_pr=true>,
     "evidence": [{"title": "...", "url": "...", "wired_pr": true|false}]
   }
   ```
5. Set `status`:
   - `🟢 meets threshold` if `with_shipped_pr >= 3`
   - `🟡 below threshold (X/3)` if `0 < with_shipped_pr < 3`
   - `🔴 not started` if `user_owned_llds == 0`

### 2. `org.communication` — RCAs + broadcast posts

**Threshold:** ≥3 RCAs/half + ≥1 broadcast post/quarter in `#einv-devs` (`C04U10T2DAN`) or wider.

**Steps:**

**RCAs (Drive):**
1. `mcp__ff2234ae-562b-49a3-a15e-83ee23736f08__search_files` with query:
   ```
   'vashistha.garg@clear.in' in owners and (name contains 'RCA' or name contains 'RCF' or name contains 'Root Cause') and modifiedTime >= '2026-04-01T00:00:00Z'
   ```
2. Filter out the same false-positive folders as above.

**Broadcast posts (Slack):**
1. `mcp__3cc059b9-ff76-427e-8692-ea054312bce8__slack_search_public_and_private` with query:
   ```
   from:U087T0SHNCC in:C04U10T2DAN after:2026-04-01
   ```
2. Treat a "broadcast post" as: a top-level message (no `thread_ts` parent) that is ≥150 chars long. Filter out short replies/reactions.

3. Update `org.communication.current` to:
   ```json
   {
     "rcas": <count>,
     "broadcast_posts": <count>,
     "evidence": [...]
   }
   ```
4. Set `status`:
   - `🟢 meets threshold` if `rcas >= 3 AND broadcast_posts >= 1`
   - `🟡 below threshold (rcas X/3, broadcasts Y/1)` otherwise
   - `🔴 not started` if both zero

## Update logic

For each line you score:
1. Read the current state at `~/dev/personal-skills/data/promotion_state.json`.
2. Edit the matching rubric_lines entry (use `Edit` tool with the JSON file — match the existing key order).
3. Bump `last_evaluated` on that specific line to current ISO-8601 IST timestamp (`+05:30`).
4. If the new status differs from the previous status, append to that line's `history` array:
   ```json
   {"evaluated_at": "<iso>", "from_status": "<old>", "to_status": "<new>"}
   ```
5. Don't bump the top-level `last_evaluated` — `score_promotion.py` owns that.

## Hand back to /v-promo-tracker

Return a JSON-shaped summary like:
```json
{
  "engineering.lld": {"before": "...", "after": "...", "evidence_count": 2},
  "org.communication": {"before": "...", "after": "...", "evidence_count": 4}
}
```

The orchestrator (`/v-promo-tracker`) merges this with the script's output and posts the combined Slack draft.

## Don't
- Don't auto-send Slack messages.
- Don't update lines outside `engineering.lld` and `org.communication`.
- Don't assume Drive/Slack queries succeed — surface errors back to the orchestrator with `"error": "..."`.
- Don't fabricate evidence URLs.
