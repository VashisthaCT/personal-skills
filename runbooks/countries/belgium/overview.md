# Belgium (BE) — FOD Financiën E-Invoicing via Peppol

**Code:** BE | **Region:** EU | **Status:** Live
**Regulator:** FOD Financiën (Belgian Federal Public Service Finance)
**Repos:** `einvoicing-core/einvoice-be`, `clear-peppol-ap`

## Summary

Belgium uses Peppol as the delivery network for e-invoicing under the FOD Financiën mandate. ClearTax integrates as a Peppol Access Point (`POP000602`). The country module `einvoice-be` lives alongside Peppol common code; routing goes through the Peppol vendor.

## Key repos / files

- `einvoicing-core/einvoice-be` — country module.
- `clear-peppol-ap` — Access Point handles outbound + inbound + reporting (EUSR/TSR).
- `clear-routing/clear-peppol/` — vendor module for Peppol routing.

## Recent work

- **Belgium MLS state-machine** (Mar 24 thread #e-invoice-tech-internal): https://cleartaxtech.slack.com/archives/C09AC9XKTC5/p1774264263390699

## Slack & people

- `#einv-devs` (`C04U10T2DAN`) — broader EU/Peppol discussions.
- `#e-invoice-tech-internal` (`C09AC9XKTC5`).

## Cross-reference

- **`runbooks/regions/peppol/`** — the Peppol delivery network details.
- **MLS / MLR** flows are handled by the Peppol AP for Belgium documents.

## TODO sections

- `api_contract.md` — FOD Financiën / Peppol BIS endpoints.
- `ubl_structure.md` — Peppol BIS BE schema.
- `credentials.md` — AP cert (G3) and any BE-specific credential.
- `code_map.md` — `einvoice-be` files + AP touch points.
- `people.md` — FOD Financiën regulator contacts + internal team.
- `live_state.md` — go-live + customers.
- `law_changes.md` — FOD Financiën circulars + Peppol BIS BE updates.
- `runbook.md` — common errors and the Belgium MLS state-machine.

Sources: `platform_architecture.md` §3 (`@ConditionalOnCountry({"BE"})`); `project_perf_review_fy26.md` §9 (Belgium MLS Slack permalink); `data/countries.yaml`.
