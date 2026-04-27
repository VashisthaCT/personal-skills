# personal-skills

Private Claude Code plugin. Personal productivity OS for a multi-country e-invoicing engineer at ClearTax (Vashistha Garg, SE-I/IC2/L4).

## Layout

- `skills/` — 32 planned skills (`v-` prefix). Phase 1 ships `v-standup`, `v-status`, `v-morning`.
- `runbooks/` — country-by-country invoicing knowledge. Rich seed: Jordan, India, UAE, Peppol, GCC. Stub: KSA, MY, BE, FR, PL.
- `data/` — context store: projects, countries, people, customers, mentees, AI tooling, promotion state.
- `prompts/` — reusable templates (RCA, LLD, runbook, status, broadcast).
- `agents/` — custom agents skills delegate to.
- `scripts/` — cron jobs (harvest, score promotion, law watch).
- `workflows/` — one-prompt orchestrators (`/v-morning`, `/v-friday`, `/v-pr-day`, `/v-incident`).

## Plan & decisions

Full plan in memory: `~/.claude/projects/-Users-vashistha-garg/memory/project_personal_skills.md`. 17 locked decisions + 10 deferred Ayush questions.

## Install (after Phase 0)

```bash
ln -s ~/dev/personal-skills ~/.claude/plugins/personal-skills
```

Restart Claude Code. Verify with `/v-standup`.

## Phasing

- Phase 0 (current): repo skeleton, plugin manifest, data seeds.
- Phase 1: `/v-standup`, `/v-status`, `/v-morning`.
- Phase 2: `/v-promo-tracker`, `/v-promo-aim` (3-5 rubric lines wired).
- Phase 3: `/v-country-brain` for Jordan + Peppol; migrate memory files to `runbooks/`.
- Phase 4: `/v-rca`, `/v-runbook` (VP-praised NIC RCF format).
- Phase 5: `/v-incident`, `/v-pr-day`, `/v-friday`.
- Phase 6: bonus skills (`/v-timed-feature`, `/v-mentee`, `/v-broadcast`, `/v-customer`).
- Phase 7+: ongoing (`/v-law-watch` countries, more rubric lines, threshold tuning with Ayush answers).
