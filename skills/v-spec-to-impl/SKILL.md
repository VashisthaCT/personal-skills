---
name: v-spec-to-impl
description: Convert a PRD (Confluence URL, Drive doc URL, or local markdown) into a JIRA Epic + child tickets breakdown, repo scaffold, and first PR draft. Reads spec, classifies (country onboarding / feature / bug-fix-RCA), extracts user stories + affected services + open questions, cross-references active_projects.yaml + countries.yaml + repo CLAUDE.mds, then drafts Epic + 3-7 child tickets, file-by-file scaffold per repo, and a PR description with Why/What/How/Test/Rollback. Drafts only — outputs to data/specs/<slug>/. Never auto-creates JIRA tickets, never opens PRs. Routes country-onboarding specs to /v-country-onboard. MVP scope: feature work + bug fixes; user copies JIRA breakdown into /v-spec-to-backlog or JIRA directly.
---

You are running Vashistha's spec-to-implementation skill. The user routinely receives PRDs (Confluence pages, Drive docs, markdown briefs) and has to convert them into: JIRA Epic + child tickets → repo scaffold → first PR draft. This skill does the conversion.

## Operating principles

- **MVP-first.** Handle the 80% case (feature work / bug fix). Country onboarding gets routed to `/v-country-onboard` — do not duplicate that skill.
- **Drafts only.** All output lands in `~/dev/personal-skills/data/specs/<slug>/`. Never create JIRA tickets. Never open PRs. Never `git commit` / `git push`.
- **Surgical.** Per `andrej-karpathy-skills:karpathy-guidelines` — no scope outside the brief; surface assumptions; verifiable success criteria.
- **Don't fabricate.** If a repo's `CLAUDE.md` isn't readable, mark "scaffold TBD — reference repo's existing patterns" rather than inventing file paths.
- **Cite cross-references.** Always link back to `active_projects.yaml`, `countries.yaml`, runbooks where applicable.

## Inputs

- `<spec>` (required): one of —
  - Confluence page URL (e.g. `https://cleartax.atlassian.net/wiki/spaces/.../pages/...`)
  - Drive doc URL (e.g. `https://docs.google.com/document/d/...`)
  - Local markdown file path (absolute, e.g. `~/Downloads/spec.md`)
- `--country <cc>` (optional): 2-letter ISO lowercase, hints at country context. Auto-detect from spec text if absent.
- `--repo <repo-name>` (optional): primary target repo. Auto-detect if absent.
- `--project-key <KEY>` (optional): JIRA project key (e.g. `EINVG`, `NV`, `EIOCJ`). Prompt if absent and not findable in spec.

## Workflow

### 1. Read the spec

- **Confluence URL** → use `mcp__de387922-450f-43fc-88e8-473a7b0c3961__getConfluencePage`. Extract page ID from URL path.
- **Drive URL** → use `mcp__ff2234ae-562b-49a3-a15e-83ee23736f08__read_file_content`. Extract file ID from URL path.
- **Local markdown** → use `Read` tool.

If the fetch fails (auth, 404, permission), abort with the error and ask the user to verify access or share a different format.

Capture:
- Title (use as `<slug>` after kebab-casing + lowercasing; strip non-alphanumerics)
- Author / owner
- Last-updated timestamp
- Full body text

### 2. Classify the spec

Scan body for keywords:

- **Country onboarding** → mentions a new country code/name not in `data/countries.yaml`, OR mentions a regulator we don't yet integrate (e.g. "Egypt ETA", "Oman OTA"), OR phrases like "new country", "onboarding", "UBL profile", "first invoice for `<country>`".
  - **Action**: print `Spec looks like country onboarding for <X>. Recommend: /v-country-onboard init <cc>. Exiting.` and stop. Do not write any output files.

- **Feature work** → new endpoint, new field, new business rule, new UI flow, new integration, change to existing endpoint/contract.
  - **Action**: continue full workflow.

- **Bug fix / RCA follow-up** → cites an incident ID (Sev1bugs-NNN, INC-NNN), references a fix-pattern, post-mortem language ("regression", "5xx", "data loss", "stuck workflow").
  - **Action**: continue, but use the lighter scaffold variant in step 6.

If ambiguous, default to **feature work** and note the classification in `summary.md` with `classification_confidence: low`.

### 3. Extract structured data

Produce a structured extraction. Use these fields:

```yaml
slug: <kebab-case-title>
title: <verbatim spec title>
classification: feature | bugfix
country: <cc or null>
one_liner: <≤140 chars summary>
affected_services: [<service from platform_architecture.md §1>]
affected_repos: [<repo names; auto-detect from services + spec mentions>]
user_stories:
  - id: US1
    role: <e.g. tax-admin, MAF-finance-user>
    want: <verb phrase>
    so_that: <outcome>
    acceptance_criteria:
      - <bullet>
      - <bullet>
open_questions:
  - <ambiguity 1>
  - <ambiguity 2>
linked_project: <id from active_projects.yaml or null>
linked_country_runbook: <runbooks/countries/<cc>/ or null>
linked_incident: <Sev1bugs-NNN or null>
```

Source `affected_services` from the platform service map (memory `platform_architecture.md` §1 — einvoicing-integrations, einvoicing-core, clear-routing, clear-data-browser-be, ingestion-overlord, clear-peppol-ap, ftp-magnet-3, one-integration, clear-sales, businesshierarchy).

### 4. Cross-reference user context

Read in parallel:
- `~/dev/personal-skills/data/active_projects.yaml` — does this spec extend an existing project? Match on `key_repos`, `key_people`, country, or epic. If yes, set `linked_project: <id>` and inherit priority/milestone.
- `~/dev/personal-skills/data/countries.yaml` — if `--country` set or auto-detected, set `linked_country_runbook` to the entry's `runbook` path.
- `~/dev/personal-skills/runbooks/countries/<cc>/` (if applicable) — read `overview.md` + `live_state.md` + `code_map.md` to learn current state. Use to inform scaffold (e.g. "extends einvoice-jo SalesToJordanMapper").

For each affected repo, check `~/Desktop/<repo>/CLAUDE.md`. If readable, ingest its conventions (test framework, package layout, naming). If not readable (path missing, permission), record `scaffold_status: TBD` for that repo.

### 5. Draft JIRA breakdown → `jira_breakdown.md`

Format:

```markdown
# JIRA Breakdown — <Spec Title>

**Project key:** <KEY>  (auto-detected from spec / prompted from user)
**Suggested Epic:**

## Epic
- **Title:** <≤80 chars; verb-led>
- **Description:**
  <2-3 sentence why + scope summary>
- **Labels:** <country, feature/bugfix, project-id>
- **Linked project:** <active_projects.yaml id, if any>

## Child tickets

### <KEY>-1 — <Title>
- **Type:** Story | Task | Bug
- **Summary:** <one paragraph>
- **Acceptance criteria:**
  - [ ] <criterion>
  - [ ] <criterion>
- **Repos touched:** <repo, repo>
- **Estimate:** S | M | L
- **Dependencies:** <ticket id or "none">

(repeat for 3-7 tickets — break work into vertically sliced increments, not horizontal layers)
```

Sizing heuristics:
- **S** = single repo, ≤1 day
- **M** = single repo + tests + integration, 2-4 days
- **L** = multi-repo or schema/migration changes, 5+ days; flag for further breakdown

If `--project-key` not given and spec doesn't reveal one, prompt the user for one of: `EINVG`, `NV`, `EIOCJ`, `GEINV`, `NIRP`. Default to `NV` for country/feature, `Sev1bugs` for incident follow-ups.

**Do not call `mcp__de387922-450f-43fc-88e8-473a7b0c3961__createJiraIssue`.** This is a draft only. User reviews then runs `/v-spec-to-backlog` (which wraps `atlassian:spec-to-backlog`) or copies into JIRA directly.

### 6. Draft scaffold → `scaffold.md`

For each repo in `affected_repos`, list specific files to create or modify. Honor that repo's `CLAUDE.md` if present.

**Feature scaffold shape:**

```markdown
## <repo-name>

**CLAUDE.md status:** read | TBD (path not accessible)

### Files to create
- `path/to/NewService.java` — <purpose>; stub:
  ```java
  package com.clear.einvoicing.<cc>.feature;

  // TODO: implement per US1 + US2
  public class NewService {
  }
  ```

### Files to modify
- `path/to/ExistingController.java` — add new endpoint `POST /api/v1/<feature>`
- `application/src/main/resources/application-local.yml` — add config keys `<keys>`

### Tests
- `src/test/java/.../NewServiceTest.java` — happy path + 2 failure modes
```

**Bugfix scaffold shape (lighter):**

```markdown
## <repo-name>

### Root cause
<one sentence>

### Fix locations
- `path/to/Buggy.java:LINE` — change <X> to <Y>

### Tests
- Add regression test reproducing <Sev1bugs-NNN>
```

**Country-specific feature in einvoicing-core**: add a final note "Reference module: `einvoice-jo` — mirror its package layout, schema-mapping JSON, mapper test naming convention."

If a repo's `CLAUDE.md` isn't readable, write only this stub:
```
## <repo-name>
**CLAUDE.md status:** TBD — path not accessible.
Scaffold TBD — open the repo and reference existing patterns. Likely files:
- (best-effort guess based on platform_architecture.md §3 country pattern)
```

### 7. Draft first PR description → `pr_draft.md`

```markdown
# <PR Title — ≤72 chars, imperative mood>

## Why
<2-3 sentences from spec one-liner + linked project/incident>

## What
- <bullet 1>
- <bullet 2>

## How
<technical approach: 1 paragraph; reference scaffold files>

## Test plan
- [ ] Unit tests pass: `<repo-test-cmd>`
- [ ] Integration test: <scenario>
- [ ] Manual smoke: <curl or UI flow>
- [ ] Coverage delta: aim ≥ baseline

## Rollback
<feature flag name OR revert PR strategy OR config rollback steps>

## Linked tickets
- Epic: <KEY>-NN
- Stories: <KEY>-NN, <KEY>-NN
- Spec: <Confluence/Drive URL>
- Active project: <active_projects.yaml id, if any>
- Country runbook: <runbook path, if any>

---
Pre-flight checklist: run `/v-pr-prep` before opening this PR.
```

### 8. Open questions → `open_questions.md`

```markdown
# Open Questions — <Spec Title>

For: <PM/EM name from spec author>
Spec: <URL>
Drafted: <YYYY-MM-DD>

1. **<Topic>** — <ambiguity sentence>. (Blocks: <which child ticket>)
2. **<Topic>** — <ambiguity sentence>. (Blocks: <which child ticket>)

---
*Resolve before starting <KEY>-NN. User to ping <author> on Slack.*
```

### 9. Output + self-DM

Write all five files to `~/dev/personal-skills/data/specs/<slug>/`:

- `summary.md` — 1-page synthesis: title, link, one-liner, classification, affected services/repos, user stories, linked project/runbook
- `jira_breakdown.md` — Epic + child tickets
- `scaffold.md` — file-by-file per repo
- `pr_draft.md` — first PR description
- `open_questions.md` — for PM/EM

If folder already exists: ask whether to overwrite or amend (default: amend — re-run merges into existing files non-destructively where safe; for `jira_breakdown.md` and `pr_draft.md`, amend = append a `## Re-run YYYY-MM-DD` section).

Then post a self-DM summary to Slack (`mcp__3cc059b9-ff76-427e-8692-ea054312bce8__slack_send_message_draft` to channel `D088362AS65`):

```
Spec drafted: <Title>
Folder: ~/dev/personal-skills/data/specs/<slug>/
Classification: <feature|bugfix>
Project key: <KEY>

Next 3 actions:
1. Resolve open_questions.md with <author> (count: N)
2. Run /v-spec-to-backlog to push Epic + tickets to JIRA
3. Run /v-pr-prep when starting <KEY>-1
```

Drafts only. Never auto-create JIRA. Never auto-PR.

## Verifiable success criteria

- Five files exist at `~/dev/personal-skills/data/specs/<slug>/`: `summary.md`, `jira_breakdown.md`, `scaffold.md`, `pr_draft.md`, `open_questions.md`.
- `summary.md` has `slug`, `title`, `classification`, `affected_services`, `affected_repos`, `user_stories`, `open_questions` fields populated.
- `jira_breakdown.md` has 1 Epic + 3-7 child tickets, each with title + acceptance criteria + estimate.
- `scaffold.md` has one section per repo in `affected_repos` (with `TBD` markers where CLAUDE.md isn't readable).
- `pr_draft.md` has Why / What / How / Test plan / Rollback / Linked tickets sections.
- `open_questions.md` exists (may be empty if no ambiguity — note "None — spec is unambiguous").
- Self-DM drafted to `D088362AS65` (not auto-sent).
- Zero JIRA tickets created. Zero PRs opened.

## Failure modes

- **Spec unreadable** (auth, 404, permission): abort with the underlying error. Suggest: re-share with `vashistha.garg@clear.in` (Drive) or check Confluence space access.
- **Country onboarding detected**: print recommendation `/v-country-onboard init <cc>` and exit. Do not write any spec output. (Routing decision lives in step 2.)
- **No project key resolvable**: prompt user once with the canonical list (`EINVG`, `NV`, `EIOCJ`, `GEINV`, `NIRP`, `Sev1bugs`). If user skips, default to `NV` and note "PROJECT KEY ASSUMED — verify before pushing to JIRA" at top of `jira_breakdown.md`.
- **All affected repos lack CLAUDE.md access**: still write `scaffold.md` with `TBD` markers — do not abort. The scaffold structure itself is useful to the user even when contents are stubbed.
- **`<slug>` collision** (folder already exists): ask overwrite vs amend.
- **Spec title yields empty slug** (all symbols/non-ASCII): fall back to `spec-<YYYYMMDD-HHMM>`.

## Don't

- Don't `mcp__de387922-450f-43fc-88e8-473a7b0c3961__createJiraIssue`. Drafts only.
- Don't open PRs (`gh pr create`). Drafts only.
- Don't `git commit` / `git push`.
- Don't modify `.claude-plugin/plugin.json` — main agent registers the skill.
- Don't create symlinks — main agent does this.
- Don't write to `~/Desktop/<repo>/` or any source repo. Output stays in `data/specs/<slug>/`.
- Don't fabricate scaffold contents for repos whose `CLAUDE.md` you can't read. Use `TBD` markers.
- Don't try to handle country-onboarding work inline. Route to `/v-country-onboard`.
- Don't auto-send the self-DM summary. Use `slack_send_message_draft` (drafts only) per repo CLAUDE.md.
- Don't include real TINs, API secrets, or customer PII in any output. Use placeholders.

## See also

- `~/dev/personal-skills/skills/v-country-onboard/SKILL.md` — what to route to when classification = country-onboarding
- `~/dev/personal-skills/skills/v-pr-prep/SKILL.md` — pre-flight check the PR draft references (sibling skill, will exist)
- `~/dev/personal-skills/skills/v-spec-to-backlog/SKILL.md` — wraps `atlassian:spec-to-backlog`; user runs after reviewing `jira_breakdown.md`
- `~/dev/personal-skills/data/active_projects.yaml` — active workstream cross-reference
- `~/dev/personal-skills/data/countries.yaml` — country runbook cross-reference
- `~/dev/personal-skills/runbooks/countries/<cc>/` — country-specific seed when applicable
- Memory: `platform_architecture.md` §1 (service map), §3 (country module pattern), §11 (6-repo onboarding checklist)
