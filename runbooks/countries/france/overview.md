# France (FR) — PPF Accreditation Track

**Code:** FR | **Region:** EU | **Status:** Accreditation track
**Regulator:** PPF (Plateforme Publique de Facturation, France)
**Repos:** `clear-peppol-ap`

## Summary

France is in the **accreditation track** — ClearTax is positioning to become a PA (Plateforme de Dématérialisation Partenaire) under the French e-invoicing mandate. CEO all-hands milestone on **Apr 24, 2026**. User is currently **tracking, not coding actively**.

The French model is a 4-corner / 5-corner Peppol-flavoured architecture with PPF as the central orchestrator. ClearTax's Peppol AP (`POP000602`) is the foundation; France-specific compliance docs (CDAR, Annuaire directory) layer on top.

## Key concepts

- **PPF** — Plateforme Publique de Facturation (state-run platform).
- **CDAR** — France compliance lifecycle status doc (open question for Peppol EUSR/TSR scope; "France expert needs to answer" per OpenPeppol Apr 8).
- **E-reporting** — F1-F14 flows.
- **Annuaire** — France's directory service.

## Slack & people

- `#einv-devs` (`C04U10T2DAN`).
- France PA expert skill (in AMClaudeKit): `france-pa-expert`.

## TODO sections

- `api_contract.md` — PPF endpoints, Annuaire interactions.
- `ubl_structure.md` — France-specific UBL extensions.
- `credentials.md` — PA accreditation and credential model.
- `code_map.md` — `clear-peppol-ap` France module touch points.
- `people.md` — PPF regulator contacts + internal team.
- `live_state.md` — accreditation milestones.
- `law_changes.md` — French e-invoicing mandate updates (deadlines, F1-F14 changes).
- `runbook.md` — France-specific oncall (will be thin pre-launch).

## CDAR open question

The Peppol EUSR/TSR scope still has CDAR handling open — Prachi to ask the France expert at OpenPeppol. See `runbooks/regions/peppol/spec_changes.md` 2026-04-08 entry.

Sources: `data/countries.yaml`; `project_peppol_reporting.md` §5 (Q4 CDAR); skill `france-pa-expert`.
