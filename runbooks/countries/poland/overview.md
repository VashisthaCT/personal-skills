# Poland (PL) — KSeF E-Invoicing

**Code:** PL | **Region:** EU | **Status:** Live
**Regulator:** KSeF (Krajowy System e-Faktur, Poland)
**Repos:** `einvoicing-core/einvoice-pl`

## Summary

Poland operates KSeF — the national e-invoicing system. ClearTax has a country module `einvoice-pl` in `einvoicing-core`. Routing for Poland uses `RoutingService=VERTEX` (per `clear-routing` enum) — Vertex/Ecosio is the third-party provider for Polish e-invoicing.

## Key repos / files

- `einvoicing-core/einvoice-pl` — country module.
- `clear-routing/clear-vertex` — vendor module (covers PL via VERTEX). Static API key auth. Actions: `GENERATE`, `CANCEL`, `SYNC`, `FETCH_RECEIVED`, `ACKNOWLEDGE`.

## Slack & people

- `#einv-devs` (`C04U10T2DAN`) — broader EU coverage.

## Cross-reference

- Notable: Poland is exempt from the SBDH-wrap path in `EInvoiceGlobalGenerationService.processAndValidateLhdnDocumentFormation` (the `country!=PL` exclusion). Jordan was added to the same exclusion list per the local fix in Session 4.

## TODO sections

- `api_contract.md` — KSeF endpoints via Vertex.
- `ubl_structure.md` — KSeF schema (FA(1) / FA(2) / FA(3)).
- `credentials.md` — Vertex API key model.
- `code_map.md` — `einvoice-pl` files + Vertex touch points.
- `people.md` — KSeF regulator contacts + internal team.
- `live_state.md` — go-live + customers.
- `law_changes.md` — KSeF mandate updates (deadlines, FA version bumps).
- `runbook.md` — common errors, Vertex outage handling.

Sources: `platform_architecture.md` §3 (`@ConditionalOnCountry({"BE,PL,FR,HR,JO"})`); §4 (clear-vertex); `jordan_implementation_log.md` Session 4 attempt #6 (Poland SBDH exclusion).
