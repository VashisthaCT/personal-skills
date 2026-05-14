---
tags: [runbooks, meta, purpose, llm-wiki]
summary: Why this directory exists, how the LLM-wiki pattern is adapted here, and how other teams can adopt it.
last_updated: 2026-05-12
related: [index.md, log.md, ../CLAUDE.md]
---

# Runbooks — purpose

This directory is a **self-maintaining knowledge base** for the multi-country e-invoicing platform. It follows the [Karpathy LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) adapted to engineering operations.

## The architecture (3 layers — Karpathy)

- **Raw sources** — code at `~/Desktop/<repo>`, Slack threads, Drive RCAs, memory files. Immutable. Skills read but never modify these.
- **The wiki** — this directory. Plain markdown. LLM-owned + LLM-maintained.
- **The schema** — [`../CLAUDE.md`](../CLAUDE.md) + skill files at `../skills/v-*/SKILL.md`. Tells skills how to read + update the wiki.

## Why this exists

- **Compounding context** — every prod incident, debug session, design decision flows back into a country/region/service entry. No knowledge lost to chat history.
- **Self-correcting** — when a skill finds the code disproves a runbook claim, it asks `Y/n` and appends a correction note. Stale claims surface naturally.
- **Cross-skill** — `/v-country-brain` debugs, `/v-rca` drafts, `/v-incident` reacts, `/v-runbook` curates. All read this directory, all write back via the same append-only discovery loop.
- **Domain-agnostic** — currently countries/regions, but the same pattern applies to services, customers, products, teams. Generalizing to [`ClearTax/vibes`](https://github.com/ClearTax/vibes) is the planned next step.

## Structure

```
runbooks/
├── index.md             # catalog of every entry — start here
├── log.md               # chronological append-only record of all skill operations (Karpathy log.md)
├── purpose.md           # this file
├── countries/<cc>/      # 7-9 files per country
│   ├── overview.md      # 1-page elevator pitch
│   ├── api_contract.md  # endpoints, auth, error codes
│   ├── ubl_structure.md # schema, validation, enums
│   ├── credentials.md   # auth model, storage, lifecycle
│   ├── code_map.md      # repos × files implementing this country
│   ├── people.md        # regulator, consultant, internal devs
│   ├── live_state.md    # go-live status, customers onboarded, known issues
│   ├── law_changes.md   # append-only regulatory log
│   ├── runbook.md       # oncall: causes, decision tree, error codes, escalation
│   └── _sessions/       # per-invocation audit trail (auto-created by /v-country-brain)
└── regions/<id>/        # 6-8 files per region (peppol, gcc, mea — schemas differ slightly)
```

## The 3 operations (Karpathy: ingest, query, lint)

| Karpathy op | Skill in this repo | Notes |
|---|---|---|
| **Ingest** — drop a new source, LLM reads + updates wiki | `/v-country-onboard parse-mapping`, `/v-rca`, `/v-incident` | All append to relevant runbook + `log.md` |
| **Query** — ask question against wiki | `/v-country-brain <cc> <question>` | Reads runbook + live code; verified-vs-hypothesis split; **good answers file back via Y/n discovery loop** |
| **Lint** — periodic health check | `/v-runbook lint <cc>` or `lint all` | Finds contradictions, stale claims, orphans, missing cross-refs |

## Conventions

- **YAML frontmatter on every page** with `tags`, `summary` (one line), `last_updated`, `related`. Lets the model relevance-filter without reading full file. *Currently only `_sessions/*` and the top-level files (purpose/index/log) have it consistently — bulk-applying to the 45 country pages is a follow-up batch.*
- **Append-only for `log.md` and `law_changes.md`.** Never rewrite. Use `<!-- Discovery YYYY-MM-DD -->` HTML comments to mark inserted blocks.
- **Cross-references** as wikilinks where useful: `[[countries/jordan/api_contract]]`. Plain markdown links also OK. Wikilinks are preferred for Obsidian compatibility.
- **No real TINs / API secrets / private credentials** in any file. Manual diligence — no pre-commit hook.
- **Log every skill invocation** to `log.md` per the CLAUDE.md "Runbook log convention" section.

## How to adopt this pattern (other teams reading this for `ClearTax/vibes`)

1. **Define your `domains.yaml`** (could be `countries.yaml`, `services.yaml`, `customers.yaml`) — one row per entry. Required fields: `id`, `repos`. Optional: `config_repos`, `vault_path`, `runbook`, `seed: rich/medium/stub`.
2. **Create the `runbooks/<type>/<id>/` directory.** 8-9 files per entry. Adapt the file list to your domain (services may skip `api_contract`, customers may skip `code_map`).
3. **Wire your debug skill** (your `/v-debug-deep-dive` equivalent) to:
   - Read all runbook files for an entry
   - Deep-dive in the actual codebase
   - Return verified-vs-hypothesis split
   - Ask `Y/n` per discovery
   - Append confirmed discoveries back via a curator agent
4. **Wire your RCA skill** to: load runbook + live signals (logs, PagerDuty, Sentry), draft using template, write session log.
5. **Wire your lint skill** to: scan for contradictions, stale claims, orphan files, missing cross-refs.

The pattern is domain-agnostic. This instance is e-invoicing-country-specific; yours might be `service/<name>` or `customer/<id>` or `product/<sku>`.

## What's missing vs the canonical Karpathy pattern (tracked for future)

| Gap | Status | Plan |
|---|---|---|
| YAML frontmatter on all 45 country pages | ⚠️ Partial — example: [`countries/jordan/overview.md`](countries/jordan/overview.md) | Bulk-apply script as follow-up |
| Wikilinks `[[...]]` cross-references | ⚠️ Plain markdown links work; wikilinks not consistently used | Small mechanical migration |
| `/v-runbook lint` enforcement on schedule | ✅ Mode exists (see [`../skills/v-runbook/SKILL.md`](../skills/v-runbook/SKILL.md) §6); not yet cron'd | Wire a weekly cron post-MVP |

## See also

- [`../CLAUDE.md`](../CLAUDE.md) — repo conventions + MCP routing + log convention
- [`../skills/v-country-brain/SKILL.md`](../skills/v-country-brain/SKILL.md) — debug deep-dive (Karpathy "query" op)
- [`../skills/v-runbook/SKILL.md`](../skills/v-runbook/SKILL.md) — curator skill (Karpathy "ingest" + "lint" ops)
- [Karpathy's original `llm-wiki.md`](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — the source pattern
- [`nashsu/llm_wiki`](https://github.com/nashsu/llm_wiki) — reference implementation
