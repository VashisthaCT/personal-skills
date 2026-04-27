# UAE API Contract — FTA

## Routing module

`clear-routing/clear-ae-fta` — vendor module for UAE FTA integration.

| Property | Value |
|---|---|
| Auth | Dual OAuth2, Redis-cached |
| Actions | `GET_TAXPAYER_DETAILS`, `SUBMIT_TAXPAYER_DETAILS` |

## RoutingService enum

`FTA` — registered in `clear-routing` `RoutingService` enum.

## Region

`UAE` — Region enum entry; routing context for all FTA traffic.

## TODO sections

- Endpoint URLs per environment.
- Header structure including dual-OAuth2 token interplay.
- Error code reference.
- Retry / backoff policy.
- Timeout defaults.
- Rate limits.
- Sandbox vs prod differences.

## Integration upload endpoint

Owned by `einvoicing-integrations` (PR #493). Provides upload-side API for UAE customers ingesting via the integrations service. See `code_map.md`.

## What ISN'T in current memory

Field-level request/response shapes for FTA API endpoints. Mark TODO; capture from `clear-ae-fta` source + Confluence in a future session.

## Cross-country notes

UAE was the **template reference** for the Jordan module's validation pattern — `einvoice-ae` has 9 validation rule classes. When fleshing out Jordan validation, mirror this structure.

Sources: `platform_architecture.md` §4 (vendor modules); `project_perf_review_fy26.md` §4 H2 (UAE work). Mark TODO where memory lacks contract-level detail.
