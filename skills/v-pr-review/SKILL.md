---
name: v-pr-review
description: Review one or more PRs with deep codebase deep-dive. Auto-detects mode by author — own PRs run 10-check pre-flight + deep-dive (with optional --auto-fix to rewrite description); others' PRs run deep-dive only and log to data/pr-reviews/ for /v-promo-tracker rubric counting (engineering.code_review). Multi-PR mode reviews sequentially and waits for user "go" between PRs. Never auto-comments on PR.
---

You are reviewing one or more PRs for Vashistha. Mode is auto-detected per PR by checking the author. Multi-PR runs sequentially with user discussion between.

## Inputs

- `<pr>` — single PR URL or number (auto-detect repo from current branch if number-only)
- `<pr1> <pr2> ...` — multiple PRs reviewed sequentially (multi-PR mode)
- `--auto-fix` — only honored on own PRs. Rewrites description via `gh pr edit`. Ignored (with warn) on others' PRs.

## Mode auto-detection

For each PR:
```
gh pr view <repo> <pr> --json author --jq '.author.login'
```
(All `gh` calls require `dangerouslyDisableSandbox: true`.)

| Author | Mode | What runs | --auto-fix |
|---|---|---|---|
| `VashisthaCT` | **own** | 10-check pre-flight + deep-dive review | valid (rewrites your PR description) |
| anyone else | **others** | deep-dive review only; logged for `engineering.code_review` rubric | warn + ignore |

## Workflow per PR

### Step 1 — Resolve + fetch
- If `<pr>` is a number: get repo from `git -C $(pwd) remote get-url origin`. Else parse repo + PR# from URL.
- Fetch:
```
gh pr view <repo> <pr> --json url,title,body,files,additions,deletions,reviewRequests,statusCheckRollup,mergeable,labels,author,baseRefName,headRefName,commits
```

### Step 2 — Read changed files at HEAD
For each file in `files`:
1. Check `~/Desktop/<repo>/<file_path>`. If exists, use `Read` tool.
2. Else `gh api repos/<owner>/<repo>/contents/<file_path>?ref=<head_sha>`.
3. Read enough surrounding code to understand context (entire class/function for Java, entire module for Python).

### Step 3 — Cross-reference codebase
For each modified function/symbol:
- Grep call-sites: `grep -rn "<symbol>" ~/Desktop/<repo>/src/`
- Check downstream consumers
- Verify backwards-compatibility (does old caller still work after this change?)
- Look for similar-pattern usages elsewhere — catches whole bug-classes (e.g. EInvoiceUblFields enum: one typo' path led you to verify the entire enum)
- For schema/DB changes: trace producer + consumer paths
- For API changes: enumerate all callers
- For new features: check feature-flag gating (`@ConditionalOnCountry`, `@ConditionalOnProperty`, etc.)

### Step 4 — Test verification (if local checkout)
If `~/Desktop/<repo>/` exists and PR adds tests:
- Run only the new test class:
```
cd ~/Desktop/<repo> && mvn test -Dtest=<NewTestClass>
```
- Note pass/fail. If didn't run, say "didn't run" — never fabricate.

### Step 5 — Classify findings
Bucket every observation into:
- **Correctness** — does the logic work? cite `file:line`
- **Impact** — call-sites, backwards-compat, downstream consumers, side-effects
- **Test quality** — new tests added? cover the change? edge cases? gating tests?
- **Concerns / nits** — non-blocking but worth flagging (PR description issues, missing docs, code-style)

### Step 6 — Own PR pre-flight (own mode only)
Run 10 checks. Report each as ✅ / ⚠️ / ❌:

A. **Description structure** — body has Why / What / How / Test plan / Rollback / Linked tickets sections?
B. **JIRA link** — body contains `[A-Z]+-\d+` or JIRA URL?
C. **AI tag** — body mentions "AI-assisted" / "Co-Authored-By Claude" / Claude Code / Cursor? (For `ai.competency` L4 evidence.)
D. **Design doc link** — body has Confluence/Drive link to LLD/HLD/design doc? (For `engineering.lld` rubric.)
E. **Test coverage heuristic** — for each changed `.java` file, does a corresponding `*Test.java` exist in the diff or in the codebase?
F. **Instrumentation** — for new endpoints/jobs/handlers, does diff add `@Timed`, `MeterRegistry`, `Counter`, `log.info`, `Sentry.captureException`?
G. **CI status** — any failing checks in `statusCheckRollup`?
H. **Branch staleness** — `git -C ~/Desktop/<repo> log --oneline main..HEAD`. Flag if base branch behind by >7 days.
I. **TODOs in diff** — search PR diff for `TODO`/`FIXME`/`XXX`. List with file:line.
J. **Reviewers requested** — `reviewRequests` empty? Suggest reviewers from `data/people.yaml` (peer/EM/architect by relevance).

### Step 7 — Compose review

```
## Review — PR #<pr>: <title>

**Author:** <author> · **Repo:** <repo> · **Mode:** own | others
**Verdict:** ✅ approve | ⚠️ request-changes | ❌ block

### 1. Correctness
[bullets — cite file:line]

### 2. Impact
[backwards-compat, call-sites, downstream consumers]

### 3. Test quality
[new tests? gaps? edge cases?]

### 4. Concerns / nits
[non-blocking items]

### 5. Pre-flight (own mode only)
A. Description structure: ✅ / ⚠️ — <detail>
B. JIRA link: ...
... (J. Reviewers)

### 6. TL;DR
[1-3 line summary]
```

### Step 8 — Auto-fix (own + --auto-fix only)
If user passed `--auto-fix` AND mode == own:
1. Generate rewritten PR description (filling missing sections with stubs based on diff/commits).
2. Write to `data/pr-reviews/<repo>-<pr>-rewrite.md`.
3. Run `gh pr edit <repo>/<pr> --body-file <path>`.
4. Confirm: "✅ PR description rewritten + posted."

Skip (with warn) if mode == others or PR is closed/merged.

### Step 9 — Persist
Write the review to `data/pr-reviews/<repo>-<pr>.md` with frontmatter:

```yaml
---
pr_url: <url>
author: <login>
mode: own | others
review_date: <ISO 8601 IST>
verdict: approve | request-changes | block
findings_count: <N>
substantive: true | false   # true if findings ≥ 5 (counts toward engineering.code_review when mode == others)
files_reviewed: <N>
---

[full review markdown body from Step 7]
```

`/v-promo-tracker` reads `data/pr-reviews/*.md` weekly to count substantive 3rd-party reviews against the `engineering.code_review` threshold (≥10 per half across ≥3 distinct authors and ≥2 repos).

### Step 10 — Multi-PR handoff
If multiple PRs queued:
- Print: `PR <i> of <N> reviewed. Discuss findings, type 'go' for PR <i+1>, or 'stop' to halt.`
- Wait for user response.
- On `go`: repeat from Step 1 with next PR.
- On `stop` or discussion: hold + respond to discussion. Wait for explicit `go`.

## Hard rules

- **NEVER post comments via `gh pr comment` or similar.**
- **NEVER auto-merge or auto-approve via `gh pr review --approve`.**
- `--auto-fix` rewrites PR DESCRIPTION ONLY (own PR), not comments or reviews.
- No `git commit` / `git push` (user does these).
- Sandbox-disabled needed for: `gh` (api.github.com + macOS keychain), `git -C <repo>` log/remote, test execution.

## Verifiable success
- Review markdown at `data/pr-reviews/<repo>-<pr>.md` with valid frontmatter.
- `verdict` field set to one of: approve / request-changes / block.
- `findings_count` ≥ 1 for any non-trivial PR.
- No PR comments posted (verify via `gh pr view <pr> --comments` should match pre-review comment count).

## Failure modes
- PR not found → abort with `gh pr view` error.
- gh rate-limit → suggest retry in N min.
- gh auth missing → run `gh auth status`, prompt user.
- Branch not in local worktree → use `gh api contents/...` for file reads.
- Diff too large (>1000 lines) → focus on logic-bearing files; note skipped boilerplate.
- `--auto-fix` on others' PR → warn and proceed without auto-fix.
- `--auto-fix` on closed/merged PR → warn and proceed without auto-fix.
- `--auto-fix` when description already complete → still safe; no destructive change.

## Don't
- Don't auto-comment on PR.
- Don't auto-merge.
- Don't auto-approve.
- Don't move to next PR in multi-PR mode without explicit `go`.
- Don't fabricate test execution results — actually run tests or say "didn't run".
- Don't include real TINs / API secrets in review reports.
- Don't fork into "review my own" vs "review others'" subskills — that defeats the consolidation. Keep auto-detection clean.

## See also
- `data/people.yaml` — for reviewer suggestions
- `data/pr-reviews/` — review history (counted by /v-promo-tracker)
- `data/promotion_state.json` `engineering.code_review` — rubric counter
- `~/Desktop/<repo>/CLAUDE.md` — repo conventions per repo
- `prompts/rca_template.md` — for incident-related PR review
