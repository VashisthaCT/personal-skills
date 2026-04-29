---
name: v-help
description: Cheat sheet of all personal `/v-*` skills grouped by use case (rituals, promotion, incidents/RCA, country work, PRs/specs, comms). Use when the user asks "which skill should I use for X", says "/v-help", lists v-skills, or you can't decide between two v-skills with overlapping triggers.
---

# v-help — personal skill catalog

Flat reference of every `/v-*` skill in this repo, grouped by intent. The agent reads this when (a) the user asks "which skill for X?", or (b) two skills could match and the agent needs to disambiguate.

When invoked, **list the relevant group(s) only** for the user's question — do not dump the entire catalog unless asked.

---

## Daily / weekly rituals

| Skill | Fire when user says… | NOT for |
|---|---|---|
| `/v-morning` | "morning digest", "what's on today", 8:45 IST cron | end-of-day wrap |
| `/v-standup` | "today's standup", "yesterday/today/blockers", IND/MEA/Malaysia standup | weekly status |
| `/v-status` | "weekly status", "DM Ayush", "Friday wrap to manager", Done/In-flight/Blockers/Next | daily standup |
| `/v-friday` | "Friday wrap", weekly status + promo gaps + 1:1 flags combined | mid-week check-in |

## Promotion tracking (SE-II rubric)

| Skill | Fire when user says… | NOT for |
|---|---|---|
| `/v-promo-tracker` | "score my promo", "rubric check", "FY27-H1 gaps" — runs full scoring | quick-glance answer |
| `/v-promo-aim` | "what should I grind on this week", "weakest 3 rubric lines" — fast, no MCP calls | full rescoring |
| `/v-mentee` | "log mentee touchpoint", "mentoring update", SE-I mentee 1:1 notes | promo scoring |
| `/v-timed-feature` | "start timer for feature X", "end timed feature", AI L4 evidence wrap | unrelated work timing |

## Incidents / RCA / customer

| Skill | Fire when user says… | NOT for |
|---|---|---|
| `/v-incident` | Sev1/Sev2 incident, "scaffold incident folder", new incident going live | post-mortem doc |
| `/v-rca` | "draft RCA", "9-section RCF", post-mortem after incident closed | live debugging |
| `/v-customer` | Customer name from `data/customers.yaml` (MAF/Tabby/Mitsuba/Swiggy/Eicher), "all tickets for customer X" | unknown customer |
| `/v-broadcast` | "draft broadcast post", customer comms / wider announcement | DM to single person |

## Country work

| Skill | Fire when user says… | NOT for |
|---|---|---|
| `/v-country-brain` | "debug X for country Y", paste Slack thread + country code, "why is Jordan failing" | new country onboarding |
| `/v-country-onboard` | "onboard new country", "einvoice-XX module", parse mapping xlsx, generate mapper/tests/curls | existing-country debug |
| `/v-runbook` | "draft/extend runbook for country/region", oncall SOP update | one-off bug fix |
| `/v-law-watch` | "regulator portal scrape", "any new e-invoicing rules", monthly regulatory diff | code-level changes |

## PR / spec / planning

| Skill | Fire when user says… | NOT for |
|---|---|---|
| `/v-pr-review` | "review PR #X", own PR pre-flight, others' PR deep-dive | PR-day overview |
| `/v-pr-day` | "PR day", review queue + own open PRs + nag drafts (composite view) | single PR review |
| `/v-spec-to-impl` | "PRD to JIRA", "Confluence URL → Epic + tickets", spec → repo scaffold | grilling an unclear spec |

## Comms

| Skill | Fire when user says… |
|---|---|
| `/v-broadcast` | "draft broadcast post", customer-wide announcement |

---

## Disambiguation hints (most common confusions)

- **"status update"** → `/v-status` (weekly to Ayush) vs `/v-standup` (daily today's standup) vs `/v-friday` (Friday wrap with extras). Ask: "weekly to manager, daily standup, or Friday composite?"
- **"RCA"** → `/v-incident` (live, scaffolds folder) vs `/v-rca` (after the dust settles, full draft). Ask: "is the incident still live, or are we writing the post-mortem?"
- **"country X is broken"** → `/v-country-brain` (debug existing code) vs `/v-runbook` (write/update SOP) vs `/v-incident` (Sev1/Sev2 alert just fired). Ask: "debug, document, or incident response?"
- **"promo update"** → `/v-promo-aim` (this week's 3 actions, fast) vs `/v-promo-tracker` (full re-score, slow). Default to `/v-promo-aim` unless user wants the heavy version.

## Not in this catalog (out of scope)

- `clear-peppol-ap-expert`, `einvoicing-core-expert`, `ingestion-overlord-expert`, `oxalis-expert`, `official-peppol-expert`, `france-pa-expert` — domain Agent subagents, not skills. Invoke via Agent tool when the question is repo-architecture deep.
- `clear-ap-local-setup` — infra bootstrap, not a v-skill but lives in this repo.
- `atlassian:*`, `slack:*`, `anthropic-skills:*` — third-party skill libraries; refer to their own descriptions.
