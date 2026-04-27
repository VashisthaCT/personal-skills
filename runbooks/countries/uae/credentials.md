# UAE Credentials Model

## What we know

- **Routing-side auth:** Dual OAuth2, tokens cached in Redis (per `clear-routing/clear-ae-fta`).
- **Token actions:** `GET_TAXPAYER_DETAILS`, `SUBMIT_TAXPAYER_DETAILS`.

## TODO sections

- Per-customer credential storage shape — likely follows the `ClientCredentialSetting` pattern in `clear-sales/einvoice-global` but UAE specifics are not in current memory.
- AES encryption fields on the storage model.
- UI / Settings page location (TODO — likely Settings → Business Settings → [UAE] but unverified).
- Rotation policy / expiry.
- Failure modes (401/403 handling).
- License model (similar to the `E_INVOICING.SALES_INVOICE` per-workspace license used for Jordan).

## Cross-reference

- Tabby B2B/B2C launch Dec 2025 — first major B2C customer; kickoff "questions before code" thread Dec 2: https://cleartaxtech.slack.com/archives/C08MX0F3F17/p1764661242981169.
- 49 files / 9 validation rule classes / 92.77% coverage in einvoicing-core#888 + clear-sales#342.

Sources: `platform_architecture.md` §4 (UAE FTA dual OAuth2); `project_perf_review_fy26.md` §4 H2 (Tabby work). Mark TODO where memory lacks concrete credential-model detail.
