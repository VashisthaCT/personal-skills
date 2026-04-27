---
name: v-pr-prep
description: Pre-flight Vashistha's own PR before requesting reviewers. Runs 10 checks (description structure, JIRA link, AI-tag, design-doc link, test coverage, instrumentation, CI, staleness, TODOs, reviewers) and emits a Slack-formatted self-DM draft + a local report file. Default report-only — `--auto-fix` flag must be explicit before any `gh pr edit` runs. Each catch generates engineering.code_review / engineering.testing / engineering.lld / ai.competency rubric signals.
---

You are running Vashistha's own-PR pre-flight kit. Output: one Slack-formatted self-DM draft to `D088362AS65` and a local report at `~/dev/personal-skills/data/pr-prep/<repo-slug>-<pr>.md`.

## Inputs

- `<pr>` (required) — PR URL (`https://github.com/<owner>/<repo>/pull/<n>`) OR PR number (`1234`).
- `--auto-fix` (optional flag) — when present and ONLY when present, post the rewritten description to the PR via `gh pr edit`. Default is report-only.

## Step 1 — Resolve the PR

Two cases:

1. **PR number only.** User must be running this from inside the repo's worktree. Resolve owner/repo via Bash with `dangerouslyDisableSandbox: true` (sandbox blocks macOS keychain `gh` reads):
   ```bash
   git -C $(pwd) remote get-url origin
   ```
   Parse `git@github.com:OWNER/REPO.git` or `https://github.com/OWNER/REPO.git` → `OWNER/REPO`.
2. **Full URL.** Parse `https://github.com/OWNER/REPO/pull/N` directly.

If neither works (cwd not a git repo, no `origin`, malformed URL), abort with: `Cannot resolve PR. Pass a full URL or run from inside the repo worktree.`

Set `<repo-slug>` = `<owner>__<repo>` for filenames (slashes replaced).

## Step 2 — Fetch PR data

One `gh` call (sandbox-disabled):
```bash
gh pr view <pr-ref> --repo <owner>/<repo> --json url,title,body,files,additions,deletions,reviewRequests,statusCheckRollup,mergeable,labels,headRefName,baseRefName,createdAt
```

If `gh` exits non-zero, surface error verbatim and stop. Common failure mode: rate-limit (`API rate limit exceeded`) — tell user to retry in 1h or set `GH_TOKEN`.

Cache the JSON in-memory for the rest of the run.

## Step 3 — Run 10 pre-flight checks

Each check returns `pass | fail` + a one-line action. Track `pass_count` and `action_items[]`.

### A. Description structure
Body must contain six sections (case-insensitive headings, allow `##`/`**Why**`/`Why:` styles): `Why`, `What`, `How`, `Test plan`, `Rollback plan`, `Linked JIRA`. Regex per section, e.g. `(?im)^(?:#+\s*|\*\*)?\s*why\b`. List the missing ones in the action.

### B. JIRA link
Body must contain a JIRA URL (`*.atlassian.net/browse/[A-Z]+-\d+`) OR a bare key (`\b[A-Z]{2,}-\d+\b`). If absent, fail. Cross-reference: link is required for `engineering.code_review` evidence + on-call traceability.

### C. AI-tag
Body must contain one of: `AI-assisted`, `Co-Authored-By: Claude`, `Claude Code`, `Cursor`, or `🤖 Generated`. If absent, fail with suggested phrasing:
> _Built with Claude Code (AI-assisted). See [v-timed-feature retro](link) for before/after timing._

This is the L4 evidence signal for `ai.competency` per `data/promotion_state.json`.

### D. Design doc link
Body must contain a link to Confluence (`*.atlassian.net/wiki/`), Drive (`docs.google.com/document/`, `drive.google.com/`), or an LLD/HLD heading reference. If absent, fail. This is the `engineering.lld` rubric signal — every non-trivial PR (>200 LOC additions) should link to a design doc.

Skip this check (auto-pass) for PRs with `additions + deletions < 100` (small fixes don't need LLDs) — note as `pass (small PR; LLD not required)`.

### E. Test coverage
From `files[]`, classify each non-test file as needing tests:
- Java: `src/main/java/.../Foo.java` → expect `src/test/java/.../FooTest.java` or `.../FooIT.java`
- Kotlin: same pattern with `.kt`
- Python: `src/foo.py` → expect `tests/test_foo.py` or `src/tests/test_foo.py`
- TypeScript: `src/foo.ts` → expect `src/foo.test.ts` or `src/foo.spec.ts` or `__tests__/foo.test.ts`

Heuristic: a file is "covered" if ANY test-file with the matching base name appears in `files[]` (added or modified). List files without coverage in the action.

Skip files matching: `*.md`, `*.yaml`, `*.yml`, `*.json`, `*.properties`, `*.lock`, `pom.xml`, `build.gradle*`, `package.json`, `package-lock.json`, files under `migrations/`, `db/migration/`, `resources/`, `META-INF/`.

Note in the report: heuristic only — file-existence based, not test-execution.

### F. Instrumentation
Skip if no new files added (only modifications). Otherwise, for each newly-added non-test file in `files[]` whose path matches a "controller / job / handler" pattern:
- `*Controller.java`, `*Resource.java`, `*Endpoint.java` (REST)
- `*Workflow.java`, `*Activity.java` (Temporal)
- `*Consumer.java`, `*Listener.java`, `*Producer.java` (Kafka)
- `*Job.java`, `*Scheduler.java` (cron/quartz)

Pull diff with one extra `gh` call (sandbox-disabled):
```bash
gh pr diff <pr-ref> --repo <owner>/<repo>
```
Search the diff for instrumentation tokens: `@Timed`, `MeterRegistry`, `Counter.builder`, `Sentry.captureException`, `log.info`, `log.warn`, `log.error`, `Span.current`, `Tracer.spanBuilder`. Fail if any flagged file has zero such tokens. List files in action.

### G. CI status
From `statusCheckRollup[]`: collect entries where `state` (or `conclusion`) is `FAILURE` / `FAILED` / `ERROR` / `TIMED_OUT`. If non-empty, fail. List check names + URLs.

### H. Stale dependencies
Sandbox-disabled:
```bash
git -C $(pwd) fetch origin --quiet 2>/dev/null && git -C $(pwd) log --oneline -5 origin/<baseRef>..origin/<headRef> 2>/dev/null | wc -l
```
Then check branch age:
```bash
git -C $(pwd) log -1 --format=%ct origin/<baseRef>
git -C $(pwd) merge-base origin/<baseRef> origin/<headRef>
```
If branch's merge-base with main is >7 days behind tip of base, fail with: `rebase needed — branch is N days behind <baseRef>`.

If `git -C $(pwd)` fails (running outside the worktree because PR was given as URL), skip with note `staleness: skipped (not in worktree)`. Do not fail the check; report-only signal.

### I. TODOs in diff
From the `gh pr diff` output (already fetched in F or fetch now), grep added lines (`^+` excluding `^+++`) for `TODO`, `FIXME`, `XXX`, `HACK`. List file:line + comment. Cap at 10 hits.

### J. Reviewers requested
If `reviewRequests[]` is empty, fail. Suggest reviewers by reading `~/dev/personal-skills/data/people.yaml`:
- For "code review" (default suggestion): peers with `relationship: peer` who've authored PRs in the same repo (low-fidelity heuristic — emit names with `(peer)` tag).
- For "design review" (suggest only if check D failed): EM / architect / tech-lead. From `people.yaml`: Ayush Jain (manager), Febin Sathar (architect), Abhilash Pareek (em), Anand Mohan (tech-lead).

If `people.yaml` is missing, surface action: `request reviewers — people.yaml not found`.

## Step 4 — Compose draft PR description

Build a candidate description with the six required sections, populated from existing body when possible:
```
## Why
<copy existing Why section if present, else: TODO — problem statement>

## What
<copy What if present, else: TODO — change summary>

## How
<copy How if present, else: TODO — implementation approach>

## Test plan
<copy Test plan if present, else: TODO — verification steps>

## Rollback plan
<copy Rollback plan if present, else: TODO — revert strategy>

## Linked JIRA
<existing JIRA link/key, else: TODO — paste JIRA URL>

## Design doc
<existing Confluence/Drive link, else: TODO — paste LLD link>

---
_Built with Claude Code (AI-assisted)._
```

Save the candidate to `~/dev/personal-skills/data/pr-prep/<repo-slug>-<pr>.md` (create dir if needed). Include both old and new bodies in the file:
```
# PR pre-flight: <owner>/<repo>#<pr>

## Original description
<old body>

## Suggested rewrite
<new body>

## Pre-flight results
A. Description structure: <pass|fail — reason>
... (J)
```

## Step 5 — Auto-fix (gated)

ONLY if user passed `--auto-fix`:
```bash
gh pr edit <pr-ref> --repo <owner>/<repo> --body-file <path-to-new-body-only>
```
(write the rewrite to a temp file under `$TMPDIR/v-pr-prep-body-<pr>.md`; `gh pr edit --body-file` reads it). Sandbox-disabled.

If `--auto-fix` was NOT passed, do NOT call `gh pr edit`. Surface a one-liner in the Slack draft: `_Re-run with --auto-fix to apply the rewrite to the PR._`

## Step 6 — Slack draft

Single Slack message via `slack_send_message_draft` to `D088362AS65`:
```
⚙️ *PR pre-flight: <owner>/<repo>#<pr>* — <title>

*Pass:* <count>/10
*Action items:* <count>

✅ <comma-list of pass labels: A, C, G, ...>
⚠️ <one line per fail: "B: missing JIRA link", "E: 3 files without test coverage (Foo.java, Bar.java, Baz.java)", ...>

Description rewrite: `~/dev/personal-skills/data/pr-prep/<repo-slug>-<pr>.md`
<if --auto-fix: `Applied to PR.`>
<else: `Re-run with --auto-fix to apply.`>
```

Total ≤ 30 lines. Use Slack `*bold*` and ` `code` ` formatting. No emojis except ✅⚠️⚙️.

## Verifiable success criteria

- `~/dev/personal-skills/data/pr-prep/<repo-slug>-<pr>.md` exists with original + rewrite + per-check results.
- Slack draft posted to `D088362AS65` with pass count out of 10 and action items.
- All 10 checks (A–J) reported as pass/fail/skip with one-line reason each.
- `gh pr edit` is called ONLY if user passed `--auto-fix`; otherwise no PR mutation.
- No `git commit` / `git push` / auto-comment / auto-merge.

## Failure modes

- **PR not found** (`gh` returns 404) → abort with: `PR <pr-ref> not found in <owner>/<repo>. Check the number/URL.`
- **gh rate-limit** → abort with: `gh API rate limit hit. Retry in 1h or set GH_TOKEN.`
- **gh not authenticated** → abort with: `gh auth token expired. Run \`gh auth login\`.`
- **Branch not on main remote** (Step H git fetch fails) → skip H only, continue rest. Note `staleness: skipped`.
- **Repo not in cwd** when PR was passed as number-only → abort per Step 1.
- **`people.yaml` missing** → check J emits action with no suggested reviewers; do not fail the run.
- **`gh pr diff` exceeds 10MB** (huge PR) → fall back to `gh pr view --json files` only; skip checks F + I with note `diff too large; instrumentation + TODO checks skipped`.
- **`--auto-fix` on a PR with no fail items** → no-op. Print `Nothing to apply.` and skip `gh pr edit`.

## Don't

- Don't auto-fix without explicit `--auto-fix`. Default is report-only.
- Don't post comments on the PR. Don't request reviewers automatically (just suggest).
- Don't `git commit` / `git push` / `gh pr merge`.
- Don't include closed/merged PRs (warn user if PR state is closed/merged: `PR is <state>; pre-flight is for open PRs only.`).
- Don't editorialize action items ("this is critical", "high-risk"). Be terse and surgical per karpathy guidelines.
- Don't invent JIRA keys or design-doc links. If missing, the action is `add link`, not a fabricated URL.
- Don't run inside sandbox — every `gh` and `git` call needs `dangerouslyDisableSandbox: true`.
