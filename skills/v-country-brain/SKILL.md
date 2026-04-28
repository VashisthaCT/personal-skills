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
- `--capture-fix "<one-line>"` (optional): after the user reports a fix worked (e.g. "Vault key X did it"), regenerates a structured **Fix Recipe** entry for `runbook.md` (symptom → check → fix → verification) and asks Y/n to append.

## Core principle: VERIFY BEFORE CLAIM

**This is the most important rule of the skill. Read it twice.**

Every architectural claim, payload-type binding, config flag, country mapping, or fix recommendation in your output MUST be backed by a grep/Read citation from the actual code OR an existing runbook entry. If you are inferring something from architecture/naming/convention without a direct citation, mark it explicitly as **Hypothesis** in the answer (see Step 5) — never as Recommendation.

If the user pushes back on a claim, **do not defend** until you have re-checked the citation. Default to retraction-first (see Step 6.5).

Failures from past sessions this rule prevents:
- Inventing "templates were on GCC_EINVOICE in MEA" without grep evidence (April 2026 — UAE VAT 500 session). Cost: one wrong fix recommendation, one user pushback round-trip.
- Asserting "X is multiplied by Y in module Z" without reading module Z.
- Recommending payload-type re-bindings without checking the payload-type dispatch code.

## Workflow

### Step 1 — Resolve the country

1. Read `~/dev/personal-skills/data/countries.yaml` for the country's `repos`, `config_repos`, `vault_path`, regulator + status. Abort with `Unknown country '<cc>'. Add to data/countries.yaml first.` if not found.
2. Read all files in `~/dev/personal-skills/runbooks/countries/<cc>/` (or `runbooks/regions/<name>/` for regions). 7-9 files: `overview`, `api_contract`, `ubl_structure`, `credentials`, `code_map`, `people`, `live_state`, `law_changes`, `runbook`.
3. Note `seed: rich/medium/stub` from `countries.yaml` — stub means runbook will be thin; expect more discoveries.

### Step 2 — Parse the query (auto-traverse linked threads)

- **Slack permalink:** fetch via `slack_read_thread` MCP. Capture: top message, all replies, links shared, any error logs pasted in thread.
- **Auto-traverse:** if the parent thread links other Slack permalinks (sub-threads, prior RCAs, related issues), fetch them too (up to 3 deep) BEFORE composing the answer. The actual question often lives in a sub-thread, not the parent. Examples: "this is the issue raised <permalink>" → fetch. "earlier it was fixed by einvoice team <permalink>" → fetch.
- **Pasted thread text:** use as-is. Still scan for embedded permalinks and fetch those.
- **Question / error:** use as-is.

Categorize the query:
- **Trace** — error/failure path (e.g. "why does invoice X fail with error Y")
- **How-it-works** — concept explanation (e.g. "explain UAE credit note flow")
- **Find** — locate code (e.g. "where is TaxCategory ordering applied for AE")
- **Diff** — compare implementations across countries (e.g. "how does India's IRN flow differ from KSA's")
- **Config-drift** — flag/value/percent mismatch between environments (e.g. "VAT rate prints 500 instead of 5"). Triggers Step 3.5 mandatorily.

### Step 3 — Identify candidate code paths

- Seed list comes from `runbooks/countries/<cc>/code_map.md`.
- Cross-reference query keywords against file/class/method names using `Grep`:
  - Class names: pattern `class.*<Keyword>.*`
  - Method calls: pattern `[^a-zA-Z]<keyword>\(`
  - Config refs: literal `<keyword>` in `*.yaml`, `*.json`, `*.properties`, `pom.xml`
- Repos to grep: from `data/countries.yaml.countries.<cc>.repos` — typically 3-6 paths under `~/Desktop/`. Common ones: `einvoicing-core`, `clear-routing`, `einvoicing-integrations`, `clear-sales`, `clear-peppol-ap`, `ingestion-overlord`, `e-invoicing-be`, `clr-irp-be`, `pdfgenerator`.
- If a repo isn't cloned at `~/Desktop/<repo>`: skip with a note in the final answer.

### Step 3.5 — Config / env / Vault layer enumeration (mandatory for config-drift queries)

If the query is **Config-drift** category OR the suspected fault touches a `@Value`-bound flag, env variable, Spring property, or any feature flag, enumerate the config layer BEFORE concluding:

1. **Spring property — multi-module drift check:** for any property name (e.g. `wholeNumberPercentCountryCodes`, `enableXxx`), grep ALL `application*.yml` and `application*.properties` files across every module of the relevant repo. If multiple modules have divergent defaults, flag it. Pattern: `cd ~/Desktop/<repo> && grep -rn "<propertyName>" --include="*.yml" --include="*.properties" --include="*.java" --include="*.kt"`.
2. **Env-var override:** YAML defaults are not the runtime source of truth. The runtime value comes from env vars set in deploy config (Vault, k8s ConfigMap, cloud-init). Grep `config_repos` from `data/countries.yaml` for the env var name. State explicitly in the answer: "YAML default = X. Actual prod env-var override likely sourced from Vault path Y / cloud-init Z — verify."
3. **Test fixture check:** look for the property in test fixtures and `*Test.java` to confirm what countries the test suite exercises. If the country in question (e.g. `AE`) isn't in any test assertion, flag a test-coverage gap.
4. **Multi-module Spring repos to know:**
   - **einvoicing-core:** 3 modules with diverging defaults seen in the wild — `application/` (sync REST), `einvoicing-workflow-consumer/` (Kafka bulk), `einvoicing-temporal-worker/` (Temporal activities). Always diff all 3 `application-prod.yml` for any property under investigation.
   - **clear-routing, clear-peppol-ap, ingestion-overlord:** similar multi-module shapes — extend the same diff.

### Step 4 — Deep-dive the code (with verify-before-claim guardrail)

Use `Read` tool on each candidate file. Trace logic:

- **Trace queries:** follow the call chain from entry point (controller / scheduler / worker) → service → mapper → validator → routing client → external call. Stop at the failure point. Note error sources, exception types, log lines.
- **How-it-works:** read relevant service classes, mappers, validators top-to-bottom for the country's module (e.g. `einvoicing-core/einvoice-<cc>/`).
- **Find:** locate the class/method, read enough surrounding context (10-30 lines) to explain what it does and where it's called from. Use `Grep` for callers.
- **Diff:** read both country implementations side-by-side.
- **Config-drift:** read the schema mapping JSON, the `@Value` consumer, the YAML default, and (if available) the env-var override repo.

**Verify-before-claim gate** (run before composing Step 5 answer):

Mentally check each substantive claim you're about to make. For each one, ask: "Have I read the file:line that supports this?" If not, either:
- (a) Go read it now, OR
- (b) Demote the claim to **Hypothesis** in the output and explicitly say what verification is missing.

**Hard rules:**
- Never say "X was on Y in MEA region" or "the previous binding was Z" without a git log / git blame citation.
- Never recommend a fix that contradicts an existing runbook entry without a code citation that overrides the runbook (and flag the contradiction as a discovery in Step 6).
- Never invent payload-type / route / binding history. If git log doesn't show it, it didn't happen.

Note file path + line numbers for every claim you'll make in the answer.

### Step 5 — Compose the answer (split Verified vs Hypothesis)

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

## Verified (cited)

- <fact 1> — `<repo>/<path>:<line>`
- <fact 2> — `<repo>/<path>:<line>`
- <fact N> — `<repo>/<path>:<line>`

## Hypothesis (untested)

- <inference 1> — would need to verify <what>
- <inference 2> — likely true if <condition>, but no direct citation
- (or "None — answer is fully grounded in citations.")

## Suggested fix (if applicable)

- File: `<repo>/<path>:<line>` (or "Config — see Step 3.5 enumeration")
- Change: <description>
- Verification step: <exact command/curl/log line that proves the fix>
- Test: <which test file would catch this; flag if no test exists for this country>
- Risk: <high/medium/low + reasoning>

(or "No change needed — works as designed.")

## Related

- Recent PR: <gh PR link from last 30d if relevant>
- RCA: <Drive link if a past RCA covers this>
- Runbook section: <runbook file path that should be consulted>
- Sub-threads fetched: <list of permalinks if Step 2 auto-traversed>
```

The **Verified vs Hypothesis** split is mandatory. If a claim doesn't have a citation, it goes under Hypothesis. The user must be able to read the answer and immediately know which claims are grep-backed.

### Step 6 — Discovery + self-correction (interactive)

While composing the answer, track everything you learned that ISN'T in the current runbook. Categorize:

- **Missing in `code_map.md`:** file paths you read but aren't listed there
- **Contradicts `api_contract.md` / `ubl_structure.md` / `credentials.md`:** a claim in the runbook that the code disproves
- **New error pattern for `runbook.md`:** a debug recipe worth saving (error code → root cause → fix)
- **New regulatory detail for `law_changes.md`:** something code or thread mentions that isn't logged
- **New person to add to `people.md`:** a non-team-member who diagnosed correctly in the thread (e.g. an L2 / sister-team engineer who'd be the right callpoint next time)
- **Config layer reality for `runbook.md`:** the actual env-var / Vault / cloud-init source of truth (not the YAML default) for a flag that mattered

After the main answer, list discoveries and ask Y/n per item:

```
## Discoveries

I noticed these aren't in the runbook (or contradict it):

1. **`code_map.md`** missing `einvoicing-core/einvoice-<cc>/.../EInvoice<Cc>ValidationRules.java:45-89`. Add to code_map.md? [Y/n]
2. **`ubl_structure.md` line 23** says "TaxCategory order is fixed" but `<repo>/<path>:<line>` shows conditional ordering. Append correction note? [Y/n]
3. **New error pattern**: HTTP 500 on customizationID mismatch — saw at `<file:line>`. Append to runbook.md "Common errors" section? [Y/n]
4. **New person**: Vaibhav Pawar (`U087MLS1PPX`) — pdfgenerator print payload. Append to people.md? [Y/n]
5. **Config reality**: env var `<NAME>` actual source is Vault path `<path>` (not YAML). Append to runbook.md "Config layer"? [Y/n]
```

Wait for the user's response per item. Accept these reply forms:
- `Y all` / `yes apply all` → apply every discovery
- `Y 1,4,5` → apply only listed numbers
- `Y` (alone, after a single discovery) → apply that one
- `n` or `skip` → record as `[SKIPPED]` in session log

For each `Y`:
- Use `Edit` tool to **append** to the named runbook file (never overwrite)
- Format the appended block as:
  ```markdown
  <!-- Discovery YYYY-MM-DD from /v-country-brain session re: <1-line query summary> -->
  <the new content>
  ```
- Confirm: `✓ Appended to runbooks/countries/<cc>/<file>.md`

For each `n`: discovery stays in the session log (Step 7) only.

If the user replies "yes" ambiguously (could mean confirming the diagnosis OR applying discoveries), ask one clarifying question: "Apply all discoveries, or just confirming the diagnosis?"

### Step 6.5 — Retraction protocol (when user pushes back)

If the user pushes back on any claim with skepticism ("are you sure", "I don't think so", "that doesn't match my memory", "we recently did X but I'm not sure about your claim"):

1. **Pause. Do not defend.** Re-run the verification step for the disputed claim — read the actual code, git log, blame, or config that would prove or disprove it.
2. **Lead the next response with the verification result**, not with a defense. If the claim was wrong, say "You're right — [evidence]." If the claim was right, say "Re-checked: [evidence]. Confidence is now [high/medium]."
3. **Append a `## Retraction` block to the session log** capturing:
   - The original wrong claim (verbatim)
   - The contradicting evidence (file:line / git commit)
   - The corrected diagnosis
   - 1-line lesson for the runbook (e.g. "UAE has been on EINVOICE_GLOBAL since Nov 2025, PR #414")
4. **Revise the discovery list** in the next turn. If discoveries were premised on the wrong claim, retract them and propose corrected ones.

This protocol exists because confidently-wrong answers are the highest-cost failure mode of this skill. Pushback is a signal to re-verify, not to argue.

### Step 7 — Session log (always written, with structured frontmatter)

Always create a session log at `~/dev/personal-skills/runbooks/countries/<cc>/_sessions/<YYYY-MM-DD-HHMMSS>.md`. `mkdir -p _sessions/` if missing. Format:

```markdown
---
date: <YYYY-MM-DD HH:MM:SS IST>
country: <cc>
customer: <customer name if from thread, else "">
severity: <sev1/sev2/sev3/none>
escalated: <yes/no>
query_category: <trace|how-it-works|find|diff|config-drift>
resolution: <resolved | pending | open>
---

# Session: <YYYY-MM-DD HH:MM:SS IST>

## Query
<the user's input — thread URL, pasted text, question, or error>
- Auto-traversed sub-threads: <list of permalinks>

## Initial hypothesis (if later retracted)
<original claim — only present if retraction happened>

## Retraction (if applicable)
<wrong claim → evidence → corrected diagnosis → lesson>

## Answer (final summary)
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

## Resolution (if `--capture-fix` invoked)
- Symptom: <what was observed>
- Check: <how to confirm root cause next time>
- Fix: <exact action — env var, code change, config>
- Verification: <how to verify the fix worked>
```

This gives an audit trail. User can review `_sessions/` periodically. Frontmatter enables future querying ("all Tabby sessions Q2-2026", "all sev2-adjacent UAE sessions").

### Step 8 — Optional: capture fix recipe (when `--capture-fix` is passed OR user reports resolution)

If the user reports the fix worked (e.g. "added AE to Vault key X and it worked"), proactively offer to convert it into a structured **Fix Recipe** in the runbook:

```markdown
<!-- Fix Recipe YYYY-MM-DD from /v-country-brain session -->
### <Symptom one-liner>

- **Symptom:** <observed behavior>
- **Diagnosis path:** <which Step 3.5 / Step 4 path led to root cause>
- **Root cause:** <one line>
- **Fix:** <exact action: env var name + value, file:line + change, config repo + path>
- **Verification:** <command/curl/log line that proves it>
- **Reference session:** `runbooks/countries/<cc>/_sessions/<timestamp>.md`
```

Append to `runbook.md` "Common errors / debug paths" section. This is the highest-leverage output of the whole skill — turns one-off debug into reusable knowledge.

## Constraints

- DO NOT auto-update runbook files without Y/n confirmation per discovery.
- DO NOT silently overwrite runbook content. All updates are appends with the discovery comment marker.
- DO NOT modify `~/Desktop/` source repos. Read-only.
- DO NOT `git commit` / `git push`.
- DO NOT make architectural claims without grep/Read citations (Step 4 verify-before-claim gate).
- DO NOT defend a disputed claim before re-verifying (Step 6.5 retraction protocol).
- Output destination: chat by default; `--draft` posts to self-DM `D088362AS65`.
- Honor karpathy-guidelines: surgical scope, no expansion beyond the query.

## Verifiable success

- Answer cites at least 1 file:line from `~/Desktop/<repo>` (not just runbook quotes).
- Every claim in **Verified** section has a file:line citation that resolves.
- **Hypothesis** section explicitly lists what's untested (or says "None").
- Session log written at `runbooks/countries/<cc>/_sessions/<timestamp>.md` with frontmatter.
- Runbook files only modified after explicit `Y` per discovery.
- If no discoveries: session log still written with `Discoveries: none` line.
- If retraction occurred: session log has `## Retraction` block.
- All file:line citations resolve (no fabricated paths).
- Config-drift queries: Step 3.5 enumeration explicitly performed and surfaced in answer.

## Failure modes

- Country not in `data/countries.yaml` → abort with `Unknown country '<cc>'. Add to data/countries.yaml first.`
- Runbook directory missing → `mkdir -p`, write a TODO-marked stub for missing files, then proceed.
- Slack permalink fetch fails → fall back to `Slack fetch failed. Paste the thread text directly and re-run.`
- Repos not cloned at `~/Desktop/<repo>` → list missing repos in the answer, skip grep for those, proceed with what's available.
- Grep returns no matches → say `No code matches found. Runbook may be the only source — answer based on runbook + suggest specific grep terms to try.`
- User closes session before answering Y/n → session log records each pending discovery as `[PENDING]`.
- Config-drift query but `config_repos` missing in `data/countries.yaml` → explicitly note in answer: "config_repos not configured for this country in data/countries.yaml; YAML defaults are the only source checked. Verify Vault / k8s ConfigMap manually."

## Don't

- Don't produce "what happened in country X" status briefings — dropped per user instruction. Use `/v-status`, `/v-friday`, `/v-country-onboard checklist` for related needs.
- Don't auto-write to runbook without Y/n confirmation.
- Don't speculate beyond what code shows. If code doesn't say it, say so explicitly: `code doesn't confirm this; runbook claims X but I can't verify in <repo>:<path>`.
- Don't include real TINs / API secrets / customer credentials in session logs.
- Don't lecture or pad. Answer the question.
- Don't defend a disputed claim — re-verify first (Step 6.5).
- Don't conflate YAML defaults with prod runtime values — env-var overrides win (Step 3.5).
- Don't claim a fix recommendation without identifying its verification step.

## Anti-patterns observed in past sessions (don't repeat)

1. **The GCC_EINVOICE invention (Apr 2026):** confidently claimed UAE templates were on `GCC_EINVOICE` payload type in MEA region without grep evidence. Wrong. PR #414 (Nov 2025) had explicitly placed UAE on `EINVOICE_GLOBAL`. Real bug was env-var drift on `WHOLE_NUMBER_PERCENT_COUNTRY_CODES`. **Lesson:** binding/payload-type/routing claims need git log evidence — never inferred from convention.

2. **Single-module config blindness:** read only `application/application-prod.yml` for a flag, missed that `einvoicing-workflow-consumer/` and `einvoicing-temporal-worker/` had divergent defaults. **Lesson:** Step 3.5 multi-module diff is mandatory for any `@Value` flag.

3. **YAML-as-source-of-truth fallacy:** assumed YAML defaults reflected prod state. Vault/cloud-init env vars override them. **Lesson:** YAML is fallback only; real value is in Vault.

4. **Missed sub-thread:** the actual question was in a sub-thread linked from the parent, not in the parent itself. Took an extra round-trip to surface. **Lesson:** Step 2 auto-traverse links.

## See also

- `runbooks/countries/<cc>/` — the country knowledge base this skill reads from + writes back to
- `runbooks/countries/<cc>/_sessions/` — session audit log (auto-created)
- `agents/country-knowledge-curator.md` — append-only formatter for runbook updates (called by the Y path of Step 6)
- `data/countries.yaml` — repos × country mapping (now includes `config_repos`, `vault_path`)
- Memory: `platform_architecture.md` — service map + country module pattern
- Memory: `project_jordan_einvoicing.md` — example country deep-context (Jordan)
