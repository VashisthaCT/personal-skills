---
name: v-country-brain
description: Debug-focused deep-dive on country invoicing code. Paste a Slack thread / question / error + country code, and the skill reads the actual code in ~/Desktop/<repos> to answer. Self-corrects the country runbook when discoveries surface — interactively asks Y/n per proposed update before writing. Always writes a session log for audit. Drops the old "status briefing" output entirely; use /v-status / /v-friday for that.
---

You are running Vashistha's debug-focused country deep-dive skill. The user gives you a question about a specific country's invoicing implementation. Read the country runbook for context, then go into the actual codebase in `~/Desktop/<repos>` to answer it. Whenever the deep-dive surfaces information that contradicts or extends the runbook, propose an update and ask Y/n per discovery before writing.

## Inputs

- `<country>` (required): country code (e.g. `jo`, `in`, `uae`) OR region ID (`peppol`, `gcc`).
- `<query>` (required) — one of:
  - Slack thread permalink (e.g. `https://cleartaxtech.slack.com/archives/C04U10T2DAN/p1769575265650159`)
  - Pasted thread text (multi-line)
  - Question string (e.g. `"why does foreign currency validation fail for AE?"`)
  - Error message / stack trace
- `--draft` (optional): post the answer to self-DM `D088362AS65` instead of chat.

## Workflow

### Step 1 — Resolve the country

1. Read `~/dev/personal-skills/data/countries.yaml` for the country's `repos` list + regulator + status. Abort with `Unknown country '<cc>'. Add to data/countries.yaml first.` if not found.
2. Read all files in `~/dev/personal-skills/runbooks/countries/<cc>/` (or `runbooks/regions/<name>/` for regions). 7-9 files: `overview`, `api_contract`, `ubl_structure`, `credentials`, `code_map`, `people`, `live_state`, `law_changes`, `runbook`.
3. Note `seed: rich/medium/stub` from `countries.yaml` — stub means runbook will be thin; expect more discoveries.

### Step 2 — Parse the query

- **Slack permalink:** fetch via `slack_read_thread` MCP. Capture: top message, all replies, links shared, any error logs pasted in thread.
- **Pasted thread text:** use as-is.
- **Question / error:** use as-is.

Categorize the query:
- **Trace** — error/failure path (e.g. "why does invoice X fail with error Y")
- **How-it-works** — concept explanation (e.g. "explain UAE credit note flow")
- **Find** — locate code (e.g. "where is TaxCategory ordering applied for AE")
- **Diff** — compare implementations across countries (e.g. "how does India's IRN flow differ from KSA's")

### Step 3 — Identify candidate code paths

- Seed list comes from `runbooks/countries/<cc>/code_map.md`.
- Cross-reference query keywords against file/class/method names using `Grep`:
  - Class names: pattern `class.*<Keyword>.*`
  - Method calls: pattern `[^a-zA-Z]<keyword>\(`
  - Config refs: literal `<keyword>` in `*.yaml`, `*.json`, `*.properties`, `pom.xml`
- Repos to grep: from `data/countries.yaml.countries.<cc>.repos` — typically 3-6 paths under `~/Desktop/`. Common ones: `einvoicing-core`, `clear-routing`, `einvoicing-integrations`, `clear-sales`, `clear-peppol-ap`, `ingestion-overlord`, `e-invoicing-be`, `clr-irp-be`.
- If a repo isn't cloned at `~/Desktop/<repo>`: skip with a note in the final answer.

### Step 4 — Deep-dive the code

Use `Read` tool on each candidate file. Trace logic:

- **Trace queries:** follow the call chain from entry point (controller / scheduler / worker) → service → mapper → validator → routing client → external call. Stop at the failure point. Note error sources, exception types, log lines.
- **How-it-works:** read relevant service classes, mappers, validators top-to-bottom for the country's module (e.g. `einvoicing-core/einvoice-<cc>/`).
- **Find:** locate the class/method, read enough surrounding context (10-30 lines) to explain what it does and where it's called from. Use `Grep` for callers.
- **Diff:** read both country implementations side-by-side.

Note file path + line numbers for every claim you'll make in the answer.

### Step 5 — Compose the answer

Output format (markdown, default to chat; if `--draft`, post to self-DM `D088362AS65`):

```
## Answer

<1-3 line summary of root cause / explanation / location>

## Code path

1. **<entry point name>** — `<repo>/<relative-path>:<line-range>`
   ```<lang>
   <5-15 line snippet>
   ```
   <1-line what it does>

2. **<next step name>** — `<repo>/<path>:<lines>`
   ```<lang>
   <snippet>
   ```
   <explanation>

3. ... (continue until the answer is fully grounded in code)

## Root cause / observation

<the actual answer to the query, citing the code path above>

## Suggested fix (if applicable)

- File: `<repo>/<path>:<line>`
- Change: <description of the change>
- Test: <which test file would catch this>
- Risk: <high/medium/low + reasoning>

(or "No change needed — works as designed.")

## Related

- Recent PR: <gh PR link from last 30d if relevant>
- RCA: <Drive link if a past RCA covers this>
- Runbook section: <runbook file path that should be consulted>
```

### Step 6 — Discovery + self-correction (interactive)

While composing the answer, track everything you learned that ISN'T in the current runbook. Categorize:

- **Missing in `code_map.md`:** file paths you read but aren't listed there
- **Contradicts `api_contract.md` / `ubl_structure.md` / `credentials.md`:** a claim in the runbook that the code disproves
- **New error pattern for `runbook.md`:** a debug recipe worth saving (error code → root cause → fix)
- **New regulatory detail for `law_changes.md`:** something code or thread mentions that isn't logged

After the main answer, list discoveries and ask Y/n per item:

```
## Discoveries

I noticed these aren't in the runbook (or contradict it):

1. **`code_map.md`** missing `einvoicing-core/einvoice-<cc>/.../EInvoice<Cc>ValidationRules.java:45-89`. Add to code_map.md? [Y/n]
2. **`ubl_structure.md` line 23** says "TaxCategory order is fixed" but `<repo>/<path>:<line>` shows conditional ordering. Append correction note? [Y/n]
3. **New error pattern**: HTTP 500 on customizationID mismatch — saw at `<file:line>`. Append to runbook.md "Common errors" section? [Y/n]
```

Wait for the user's response per item. For each `Y`:
- Use `Edit` tool to **append** to the named runbook file (never overwrite)
- Format the appended block as:
  ```markdown
  <!-- Discovery 2026-04-28 from /v-country-brain session re: <1-line query summary> -->
  <the new content>
  ```
- Confirm: `✓ Appended to runbooks/countries/<cc>/<file>.md`

For each `n`: discovery stays in the session log (Step 7) only.

### Step 7 — Session log (always written)

Always create a session log at `~/dev/personal-skills/runbooks/countries/<cc>/_sessions/<YYYY-MM-DD-HHMMSS>.md`. `mkdir -p _sessions/` if missing. Format:

```markdown
# Session: <YYYY-MM-DD HH:MM:SS IST>

## Query
<the user's input — thread URL, pasted text, question, or error>

## Answer (summary)
<1-2 lines>

## Discoveries
- [APPLIED] <description> — appended to `<runbook-file>.md`
- [SKIPPED] <description> — user chose not to update
- [PENDING] <description> — user closed session before answering

## Files touched
- `runbooks/countries/<cc>/<file>.md` — appended <N> lines

## Code files read
- `<repo>/<path>:<lines>`
- ...
```

This gives an audit trail. User can review `_sessions/` periodically.

## Constraints

- DO NOT auto-update runbook files without Y/n confirmation per discovery.
- DO NOT silently overwrite runbook content. All updates are appends with the discovery comment marker.
- DO NOT modify `~/Desktop/` source repos. Read-only.
- DO NOT `git commit` / `git push`.
- Output destination: chat by default; `--draft` posts to self-DM `D088362AS65`.
- Honor karpathy-guidelines: surgical scope, no expansion beyond the query.

## Verifiable success

- Answer cites at least 1 file:line from `~/Desktop/<repo>` (not just runbook quotes).
- Session log written at `runbooks/countries/<cc>/_sessions/<timestamp>.md`.
- Runbook files only modified after explicit `Y` per discovery.
- If no discoveries: session log still written with `Discoveries: none` line.
- All file:line citations resolve (no fabricated paths).

## Failure modes

- Country not in `data/countries.yaml` → abort with `Unknown country '<cc>'. Add to data/countries.yaml first.`
- Runbook directory missing → `mkdir -p`, write a TODO-marked stub for missing files, then proceed.
- Slack permalink fetch fails → fall back to `Slack fetch failed. Paste the thread text directly and re-run.`
- Repos not cloned at `~/Desktop/<repo>` → list missing repos in the answer, skip grep for those, proceed with what's available.
- Grep returns no matches → say `No code matches found. Runbook may be the only source — answer based on runbook + suggest specific grep terms to try.`
- User closes session before answering Y/n → session log records each pending discovery as `[PENDING]`.

## Don't

- Don't produce "what happened in country X" status briefings — dropped per user instruction. Use `/v-status`, `/v-friday`, `/v-country-onboard checklist` for related needs.
- Don't auto-write to runbook without Y/n confirmation.
- Don't speculate beyond what code shows. If code doesn't say it, say so explicitly: `code doesn't confirm this; runbook claims X but I can't verify in <repo>:<path>`.
- Don't include real TINs / API secrets / customer credentials in session logs.
- Don't lecture or pad. Answer the question.

## See also

- `runbooks/countries/<cc>/` — the country knowledge base this skill reads from + writes back to
- `runbooks/countries/<cc>/_sessions/` — session audit log (auto-created)
- `agents/country-knowledge-curator.md` — append-only formatter for runbook updates (called by the Y path of Step 6)
- `data/countries.yaml` — repos × country mapping
- Memory: `platform_architecture.md` — service map + country module pattern
- Memory: `project_jordan_einvoicing.md` — example country deep-context (Jordan)
