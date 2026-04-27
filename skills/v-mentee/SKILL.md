---
name: v-mentee
description: Log mentoring touchpoints per SE-I mentee in data/mentees.yaml. Each touchpoint counts toward the SE-II "≥2 named mentees with ≥10 touchpoints/half" threshold (org.mentoring rubric line). Modes add, log, list, status.
---

You are managing Vashistha's mentee touchpoints. Source of truth: `~/dev/personal-skills/data/mentees.yaml`.

## Modes

### `add <id> "<name>" <slack_id>`

Append a new mentee entry. Use `Edit` tool (not Write) to preserve other mentees + comments in the file.

Schema:
```yaml
- id: <id>
  name: <name>
  role: SE-I
  slack: <slack_id>
  started: <today ISO>
  touchpoints: []
```

Confirm in chat: "✓ Added mentee `<name>` (`<id>`). Currently `<count>` mentees logged."

### `log <id> <type> [<link>]`

Where `type` ∈ `1:1` | `slack-thread` | `dm` | `pr-review` | `doc-review`.

1. Find mentee entry by `id` exact match in `mentees.yaml`. If not found: error and suggest `/v-mentee add`.
2. Prompt user for a 1-line `summary` (what was discussed/reviewed).
3. Append to that mentee's `touchpoints` array:
   ```yaml
   - date: <today ISO>
     type: <type>
     link: <link or null>
     summary: <user input>
   ```
4. Save (via Edit, preserving structure).
5. Confirm: "✓ Logged `<type>` with `<name>`. Total touchpoints: `<count>`."

### `list`

Print all mentees with summary stats:
```
<name> (<id>) — <count> touchpoints since <started>
  Last: <YYYY-MM-DD> — <type> — <summary>
```

### `status`

Cross-reference `mentees.yaml` with `~/dev/personal-skills/data/promotion_state.json` `org.mentoring`.

Show:
- Mentees count: `<n>` (target: ≥2)
- Per mentee: touchpoint count vs threshold (≥10 per half)
- Days since last touchpoint per mentee — flag if >14 days as "drift risk"
- Aggregate: which mentees would need flipping the rubric line to 🟢

## Constraints

- Use `Edit` tool, not `Write`, to avoid clobbering manual edits to `mentees.yaml`.
- Preserve YAML structure: indentation matters. The file uses 2-space indent. Touchpoints nest under `touchpoints:` with 2 more spaces.
- Don't fabricate touchpoints — only log when user explicitly invokes `log`.
- Slack ID format: `U` followed by alphanumeric (e.g. `U08R0HS205A`). Validate format.

## Verifiable success

- After `add`: `mentees.yaml` has new entry, parses as valid YAML.
- After `log`: target mentee's `touchpoints` array has new entry with valid date.
- `status` correctly counts per-mentee touchpoints and compares to threshold.

## Caveats

- The SE-II rubric calls out "Mentors SE-Is" — PM mentoring (e.g. Rahul Meena threads) does NOT count here per Q2 in the deferred Ayush questions. Track those separately under `org.influence` if applicable.
- Per `feedback_backend_ownership`: backend (the YAML file) is source of truth. If you edit the file directly, fine — `/v-mentee` reads it on next invocation.
