# personal-skills

A private collection of Claude Code skills that automate Vashistha Garg's day-to-day as a multi-country e-invoicing engineer at ClearTax.

**19 skills installed.** Each one is a single command in Claude Code (e.g. `/v-standup`).

All skills have a `v-` prefix to avoid clashing with built-in skills like `slack:standup`.

---

## Quick start

```bash
# Symlink each skill folder into ~/.claude/skills/ (already done if reading this from VashisthaCT/personal-skills)
for skill in $(ls ~/dev/personal-skills/skills); do
  ln -s ~/dev/personal-skills/skills/$skill ~/.claude/skills/$skill
done
```

Restart Claude Code. Then any skill is callable as `/v-<name>`.

---

## The skills

### Daily comms

#### `/v-standup`
**What it does:** Drafts your daily standup (Yesterday / Today / Blockers) from the auto-harvested work-journal + GitHub last 24h + Jira + today's calendar.
**When to use:** Before the 10:00 IST IND/MEA standup.
**Example:**
```
/v-standup
```
→ posts a Slack-formatted draft to your self-DM. You copy + paste into the standup channel.

#### `/v-status`
**What it does:** Drafts a weekly status update for your manager (Done / In-flight / Blockers / Next) from last 7 days of activity.
**When to use:** Friday 5pm or before a Monday 1:1 with Ayush.
**Example:**
```
/v-status
```
→ draft in self-DM. You edit + send to Ayush's DM.

#### `/v-morning`
**What it does:** Daily morning digest combining standup + L3 triage queue + today's calendar prep + 1-line promo gap reminder + reading queue. The "one prompt that primes your day".
**When to use:** First thing in the morning. Auto-runs 8:45 IST if cron is set up.
**Example:**
```
/v-morning
```
→ all-in-one Slack message in your self-DM with 5 sections.

#### `/v-friday`
**What it does:** Weekly Friday wrap-up — `/v-status` output + `/v-promo-tracker` top-3 weakest + stuck tickets (>5d) + flags for next Monday's 1:1.
**When to use:** Friday 5pm. Cron-able.
**Example:**
```
/v-friday
```
→ composite digest for the week.

---

### Code & PRs

#### `/v-pr-prep`
**What it does:** Pre-flight check on your own PR before requesting reviewers. 10 checks: description structure, JIRA link, AI tag (for L4 evidence), design doc link (for LLD rubric), test coverage, instrumentation, CI status, branch staleness, TODOs in diff, reviewers requested.
**When to use:** Right before clicking "Request review".
**Example:**
```
/v-pr-prep https://github.com/ClearTax/einvoicing-core/pull/1325
```
→ pass/fail report + draft PR description rewrite. Add `--auto-fix` to apply the rewrite via `gh pr edit`.

#### `/v-pr-day`
**What it does:** PR ops dashboard — your review queue (sorted by author seniority + age) + your own PR pre-flight + draft DM nags for stale PRs.
**When to use:** Once a day, or as a slice of `/v-morning`.
**Example:**
```
/v-pr-day
```
→ 3 sections in self-DM.

#### `/v-rca`
**What it does:** Drafts a Root Cause Analysis using the 14-section format that VP-praised your NIC RCF (Nov 2025).
**When to use:** After a Sev1/Sev2 incident resolution.
**Example:**
```
/v-rca "ksa-redis-licensing-2026-04-27"
```
→ draft at `data/incidents/ksa-redis-licensing-2026-04-27/rca.md`. You publish to Drive when ready.

#### `/v-incident`
**What it does:** Sev1 reaction kit — creates a folder with timeline.md (append-only), rca.md (draft from template), comms_drafts.md (channel posts), meta.yaml. Drops 3 next-action prompts in self-DM.
**When to use:** First 5 minutes of a Sev1.
**Example:**
```
/v-incident "ksa-redis-licensing"
```
→ 4 files seeded; you start filling `timeline.md` immediately.

#### `/v-runbook`
**What it does:** Generates an oncall runbook section for a country/region/error pattern, drawing from your authored RCAs.
**When to use:** After accumulating 2+ similar RCAs for a country.
**Example:**
```
/v-runbook india
```
→ updates `runbooks/countries/india/runbook.md`.

---

### Country knowledge

#### `/v-country-brain`
**What it does:** Debug-focused deep-dive on country invoicing code. You paste a Slack thread / question / error and a country code — skill reads the actual code in `~/Desktop/<repos>` to answer with file:line citations. Self-corrects the country runbook when discoveries surface (asks `Y/n` per proposed update). Always writes a session log under `runbooks/countries/<cc>/_sessions/` for audit. Drops the old "what happened in country X" briefing — that capability is covered by `/v-status`, `/v-friday`, `/v-country-onboard checklist`.
**When to use:** When a thread asks "why does X fail for country Y" or "where is X handled in code" — replaces manual grep + read sessions.
**Example:**
```
/v-country-brain ae "https://cleartaxtech.slack.com/archives/.../p1769..."
```
→ skill fetches the thread, reads `runbooks/countries/uae/code_map.md`, greps relevant repos under `~/Desktop/`, traces the failure path, returns the answer with code citations + asks `Y/n` on any runbook updates it would make.

#### `/v-country-onboard`
**What it does:** Codifies the **country onboarding playbook**. Six modes that turn a regulator's xlsx + sample XMLs into: schema mapping JSON + 50 mapper-layer tests + 93 E2E XML tests + curl docs HTML + Vault deployment checklist. Encodes 18 Jordan gotchas (Money wrapper, TaxScheme.id plain, country 2-letter, ICV UUID, skipIf cascade, customizationID handling, namespace-config workaround, etc.).
**When to use:** When a new country lands in your queue (Egypt, Oman, etc.).
**Example:**
```
/v-country-onboard init eg
/v-country-onboard parse-mapping eg --xlsx ~/Downloads/Egypt_field_mapping.xlsx
/v-country-onboard generate-mapper eg
/v-country-onboard generate-tests eg
/v-country-onboard generate-curls eg
/v-country-onboard checklist eg
```
→ all artifacts in `data/onboarding/eg/output/`. Projected ~half-day per country vs ~5-6 days for Jordan.

#### `/v-law-watch`
**What it does:** Monthly poll of govt portals (ZATCA, FTA, ETA, ISTD, NIC, GSTN, LHDN, KSeF, PPF) + invoicenavigator newsletter. Diffs against last fetch. Appends new regulatory updates to `runbooks/countries/<cc>/law_changes.md`.
**When to use:** First of each month. Cron-able.
**Example:**
```
/v-law-watch all
```
→ updates law_changes.md across all rich-seed countries + summary in self-DM.

---

### Performance & promotion (SE-II tracking)

#### `/v-promo-tracker`
**What it does:** Scores your work against the SE-II rubric (12 lines: code review, LLD ownership, mentoring, AI L4, customer understanding, etc.). Flags status changes since last run.
**When to use:** Sunday evening. Cron-able.
**Example:**
```
/v-promo-tracker
```
→ updates `data/promotion_state.json` + Slack-formatted gap diff to self-DM.

#### `/v-promo-aim`
**What it does:** Reads `promotion_state.json`, picks the 3 weakest rubric lines, suggests one concrete action per line for the week.
**When to use:** Monday morning when planning the week.
**Example:**
```
/v-promo-aim
```
→ 3 action items keyed off your weakest gaps.

#### `/v-timed-feature`
**What it does:** Wraps a feature build with a timer + retro template. Generates AI L4 promotion evidence (sprint→day before/after).
**When to use:** Start of any 1+ day feature.
**Example:**
```
/v-timed-feature start "Jordan UBL validation v1"
# work happens over the next N days
/v-timed-feature end
```
→ retro.md with elapsed time + speedup ratio + before/after prose. Auto-increments `ai.competency.timed_features_logged` in promotion_state.json.

---

### Mentoring & culture

#### `/v-mentee`
**What it does:** Logs mentoring touchpoints per SE-I mentee in `data/mentees.yaml`. Each touchpoint counts toward the SE-II "≥2 named mentees with ≥10 touchpoints/half" threshold.
**When to use:** After a 1:1, a substantive PR review on a junior's PR, a mentoring DM.
**Example:**
```
/v-mentee add jane-doe "Jane Doe" U08XXXXXXX
/v-mentee log jane-doe 1:1 "discussed L4 abstractions in PR #1234"
/v-mentee status
```
→ tracks toward your SE-II mentoring rubric line.

#### `/v-broadcast`
**What it does:** Drafts a broadcast post for `#einv-devs` (your weakest culture-leadership signal — 1 broadcast in H2 vs 23 working messages). Three templates: design-pattern / learnings / post-mortem.
**When to use:** After a notable ship or incident-derived learning.
**Example:**
```
/v-broadcast learnings ksa-redis-sev1
```
→ ≤500-char Slack draft in self-DM. You review + post to `#einv-devs`.

#### `/v-customer`
**What it does:** Aggregates ALL your work for a specific customer (top-10 curated in `data/customers.yaml` — MAF, Tabby, Mitsuba, Swiggy, Eicher + 5 placeholders). JIRA + Slack + PRs + RCAs over the last 180 days.
**When to use:** Before a customer-specific call, or when triaging a customer issue.
**Example:**
```
/v-customer tabby
```
→ composite briefing covering JIRA, Slack threads, PRs, RCAs.

---

### Coding (heaviest)

#### `/v-spec-to-impl`
**What it does:** Reads a PRD (Confluence page / Drive doc / local markdown) and produces: JIRA Epic + child tickets + scaffold across affected repos + first PR description draft. If the spec is country onboarding, routes you to `/v-country-onboard` instead.
**When to use:** When a PRD lands and you need to figure out where to start.
**Example:**
```
/v-spec-to-impl https://confluence.cleartax.com/.../tabby-b2c-uae-spec
```
→ 5 files in `data/specs/<slug>/`: summary.md, jira_breakdown.md, scaffold.md, pr_draft.md, open_questions.md. Self-DM with 3 next actions.

---

## What's auto-running

- **`daily-documentation`** cron — daily at 8:00 IST. Harvests Jira + Slack + GitHub last 24h. Updates `data/work-journal/{Projects.md, Small Wins.md, PR Reviews.md, Review Evidence.md}`. Powers `/v-standup`, `/v-status`, `/v-morning`, `/v-friday`.

If you want the morning/Friday/promo-tracker/law-watch crons set up, see `~/.claude/scheduled-tasks/` and add new entries (or use `mcp__scheduled-tasks__create_scheduled_task` from a Claude session).

---

## Where things live

```
personal-skills/
├── skills/                 # 19 skills, one folder each (SKILL.md)
├── runbooks/
│   ├── countries/          # jordan/, india/, uae/ rich; ksa/, malaysia/, belgium/, france/, poland/ stub
│   └── regions/            # peppol/, gcc/ rich
├── prompts/                # Templates: rca, runbook, status, country-onboarding playbook, schema-mapping, mapper tests, broadcast (3)
├── data/
│   ├── active_projects.yaml      # 10 workstreams
│   ├── countries.yaml            # 8 + 2 regions
│   ├── people.yaml               # top 20 collaborators with Slack IDs
│   ├── customers.yaml            # top 10 (5 named + 5 placeholders)
│   ├── mentees.yaml              # populate as you mentor
│   ├── ai_tooling.yaml           # Claude Code only at MVP
│   ├── law_feeds.yaml            # govt portal URLs per country
│   ├── promotion_state.json      # 12 SE-II rubric lines
│   ├── work-journal/             # auto-populated by daily-documentation cron (separate git repo)
│   ├── curated-jira/             # hand-curated ticket notes
│   └── historical-report.md      # 190-commit historical snapshot
├── scripts/
│   ├── score_promotion.py        # weekly cron for /v-promo-tracker
│   └── parse_country_mapping.py  # xlsx parser for /v-country-onboard
├── agents/
│   ├── promo-evidence-scorer.md
│   └── country-knowledge-curator.md
├── workflows/              # one-prompt orchestrator docs (currently empty — workflows live inside skills/)
└── .claude-plugin/
    └── plugin.json         # registers all 19 skills
```

The plan + every locked decision: `~/.claude/projects/-Users-vashistha-garg/memory/project_personal_skills.md`.

---

## Conventions

- **Drafts only.** No skill auto-sends to Slack channels or Drive. They write to your self-DM (`D088362AS65`) or to local files. You review and post manually.
- **Real customer/colleague names** are OK in runbooks (privacy-by-private-repo).
- **Real TINs / API secrets / private credentials** NEVER in commits (no pre-commit hook installed; manual diligence).
- **`v-` prefix** on every skill to avoid clashes with built-ins.
- **No silent commits** — `git commit` and `git push` are user-triggered (one exception: when you explicitly ask the skill to commit, e.g. during repo bootstrap).

---

## What's NOT built yet

13 skills still planned. All are smaller wraps or polish:

| Skill | What it would do |
|---|---|
| `/v-slack-reply` | Draft a reply to an L3-support thread or manager DM |
| `/v-spec-to-backlog` | Wraps `atlassian:spec-to-backlog` with country defaults |
| `/v-triage-issue` | Wraps `atlassian:triage-issue` |
| `/v-weekly-report` | Wraps `atlassian:generate-status-report` for project status |
| `/v-jira-bulk` | Bulk JIRA: column move, label, epic-link via JQL |
| `/v-perf-review` | Wraps `cleartax-perf-review-builder` |
| `/v-inbox-triage` | Gmail → action items in self-DM |
| `/v-reading-queue` | Aggregate links from Slack/Drive/Email |
| `/v-meeting-prep` | Calendar event → 1-page brief (attendees + related tickets/PRs) |
| `/v-sync-context` | Refresh `data/*` files (manual override of cron) |
| `/v-describe-me` | "Who I am right now" synth — for fresh chat sessions |
| `/v-skill-create` | Wraps `anthropic-skills:skill-creator` for adding new skills |
| `/v-repo-brief` | CLAUDE.md + git log + recent PRs → arch summary |

Battle-test the 19 first; ship targeted skills based on real friction.

---

## Phasing recap

- Phase 0 — Repo skeleton + plugin manifest + data seeds + migration
- Phase 1 — `v-standup`, `v-status`, `v-morning`
- Phase 2 — `v-promo-tracker`, `v-promo-aim`
- Phase 3 — `v-country-brain` + 45 runbook files
- Phase 4 — `v-rca`, `v-runbook` + NIC-RCF template
- Phase 5 — `v-incident`, `v-pr-day`, `v-friday`
- Phase 6 — `v-timed-feature`, `v-mentee`, `v-broadcast`, `v-customer`
- Phase 7 (partial) — `v-country-onboard`, `v-spec-to-impl`, `v-pr-prep`, `v-law-watch`

13 skills remaining for "full" coverage. No timeline.
