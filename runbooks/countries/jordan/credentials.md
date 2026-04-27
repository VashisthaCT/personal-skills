# Jordan Credentials Model

Authoritative source: PRD §3A.

## Hierarchy

- 1 TIN → exactly **1 Portal Account** on JoFotara.
- 1 Portal Account → **N Devices** (one per branch / POS / integration point).
- Each Device has its own Client-Id, Secret-Key, Income Source Sequence.
- "Device" = virtual concept linked to ERP for managing API access.
- Income Source Sequence is *typically* consistent across devices under one TIN, but PRD says it "must be confirmed per device during onboarding."

## Storage shape (per device)

| Field | Encrypted? | Notes |
|---|---|---|
| `tin` | No | Taxpayer identifier |
| `deviceId` (a.k.a. branch/device name) | No | Admin-assigned human-readable label |
| `clientId` | No | Plaintext |
| `clientSecret` (Secret-Key) | **Yes (AES)** | Write-only from user perspective; show last 4 chars only (`••••••••xxxx`) |
| `incomeSourceSequence` | No | Plaintext, not a secret |

These live on `clear-sales/einvoice-global/.../models/settings/ClientCredentialSetting.java`. NV-269 added `incomeSourceSequence` and `deviceId` (branch `local/jordan-iss-field` → eventually `hotfix/1.147.52`).

## Architecture

- **Credentials are stored at the (TIN + Income Source Sequence) level.** Multiple branches under the same TIN each have their own credential set. Storage is at branch-level NodeSettings (one per branch, each carrying its own credentials).
- **On invoice submission:** lookup credential set by Income Source Sequence from the invoice payload. Inject `clientId` and `clientSecret` into request headers; ISS into the XML body.
- **If ISS on invoice doesn't match any Active credential** → hold in Pending with warning.

## UI (piggyback, not a separate page)

- **Location:** Settings → Business Settings → [Select Jordan] → Edit Business / Add Branch.
- **Three Jordan-specific fields** on the side drawer:
  - `Client-Id` (plain, mandatory)
  - `Secret-Key` (masked input, mandatory, show last 4 after save)
  - `Income Source Sequence` (numeric, mandatory)
- **On save:** one-time info banner — *"Credentials saved. These cannot be verified with ISTD until an invoice is submitted..."*
- **Edit:** `Secret-Key` is cleared on edit; admin must re-enter the full key.
- **Badge** on Business Settings row: green "Credentials set" or amber "Credentials missing".

NV-270 owns the frontend; Khushboo. Backend (NV-269) is Vashistha.

## Lifecycle

- No expiry, no rate limits, no IP restrictions.
- Can be revoked any time on the JoFotara portal.
- Toggling a device to Inactive on the portal → API returns 401/403 (handle both — see `api_contract.md`).

## Failure handling

| Failure | JoFotara response | ClearTax behavior |
|---|---|---|
| Invalid Client-Id / Secret-Key | 401 (PRD) / 403 (SDK) | Invoice Failed. Message: "Authentication failed. Check Settings > JoFotara Credentials." |
| Device Inactive on portal | 401 / 403 | Same as above |
| ISS mismatch | REJECTED + validation error | Invoice Rejected by ISTD with the ISTD error code |

## Retention

4 years minimum (ISTD mandate). Signed XML stored by ISTD AND by us. Data may be stored anywhere globally.

## Implementation cross-reference

- `clear-sales/einvoice-global/.../ClientCredentialSetting.java` — model.
- `clear-sales/einvoice-global/.../NodeSettings.java` — container.
- `einvoicing-core/settings/.../SettingsServiceImpl.java` — CRUD + validate. Country-aware verify-skip added in `EInvoiceJoGovtActionService.validateTaxpayerCredential` (no JO verify API).
- `einvoicing-core/settings/.../SettingsHelper.java` — encrypt/decrypt.
- `einvoicing-core/settings/.../SettingsController.java` — REST endpoint `/v1/settings`.
- `HttpServiceClient` forwards `x-clear-country-code` header onto internal `POST /admin/verify-credential` (fixed in commit `556ed02ed` — without it, the receiving-side country resolver throws 400).

## Working save curl (verified Apr 20)

```bash
curl --location 'http://localhost:21048/v1/settings' \
  --header 'Content-Type: application/json' \
  --header 'x-workspace-id: 90bc0416-...' \
  --header 'x-clear-country-code: JO' \
  --header 'x-cleartax-auth-token: <token>' \
  --data '[{
    "NodeId": "<branchId>", "NodeType": "VAT",
    "WorkspaceId": "<workspaceId>", "CountryCode": "JO",
    "Metadata": {
      "ClientCredentialSetting": {
        "tin": "1234567890",
        "clientId": "CT-MAF-AMM-01",
        "clientSecret": "<placeholder>",
        "incomeSourceSequence": "001",
        "deviceId": "Amman - Mall of Jordan"
      }
    }
  }]'
```

`NodeSettingsDTO` uses `@JsonNaming(UpperCamelCaseStrategy)` — outer keys are PascalCase. `ClientCredentialSetting` itself uses explicit `@JsonProperty` so its inner keys stay camelCase.

NEVER paste a real Client-Id or Secret-Key into a curl logged anywhere.

Sources: `project_jordan_einvoicing.md` §7; `jordan_implementation_log.md` Session 2.
