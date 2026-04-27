# Malaysia (MY) — LHDN E-Invoicing

**Code:** MY | **Region:** SEA | **Status:** Live
**Regulator:** LHDN (Lembaga Hasil Dalam Negeri / Inland Revenue Board of Malaysia)
**Repos:** `einvoicing-core/einvoice-my`, `clear-routing/clear-my-lhdn`

## Summary

Malaysia operates an LHDN-mandated e-invoicing scheme. ClearTax integrates via OAuth2-tokened LHDN APIs (50-min token TTL stored in MongoDB). Earliest country module in `einvoicing-core`; the routing pattern (`@ConditionalOnProperty(name = "region", havingValue = "MY")`) was the legacy single-country-per-deployment template before `@ConditionalOnCountry` arrived.

## Key repos / files

- `einvoicing-core/einvoice-my` — country module. Has the only Malaysia-specific `CallableClass` in the platform (other countries manage with shared helpers).
- `clear-routing/clear-my-lhdn` — vendor module. OAuth2, Mongo-cached token, 50-min TTL.
- Routing actions: `GENERATE`, `CANCEL`, `SUBMISSION_CHECK`, `VERIFY_CREDENTIALS`, `SEARCH_TIN`.

## Recent work (FY26)

- **Malaysia recon multi-mismatch fix** (EINVMY-617, advance-recon#865) — H2 pick.

## Slack & people

- `#einvoicing_global_platform` (`C08MX0F3F17`) — primary discussion.

## Special note

Naming inconsistency: `clear-my-lhdn` MDC keys (`LHDN_CLIENT_ID`, `LHDN_CLIENT_SECRET`, etc.) are used **country-agnostically** despite the `LHDN_*` prefix. Jordan's PR #1323 added country-specific `JOFOTARA_*` constants; `EInvoiceRouterClient.resolveClientId()` checks JOFOTARA_* first, falls back to LHDN_*.

## TODO sections

- `api_contract.md` — LHDN endpoints, OAuth2 flow, error codes.
- `ubl_structure.md` — LHDN UBL schema.
- `credentials.md` — OAuth2 credential model + token refresh flow.
- `code_map.md` — full repo × file map.
- `people.md` — LHDN regulator contacts + internal team.
- `live_state.md` — go-live status + customers.
- `law_changes.md` — LHDN circular log.
- `runbook.md` — recon mismatch fixes + common errors.

Sources: `platform_architecture.md` §1, §3 (legacy `@ConditionalOnProperty`), §4 (clear-my-lhdn); `project_perf_review_fy26.md` §4 H2 pick 4 (recon).
