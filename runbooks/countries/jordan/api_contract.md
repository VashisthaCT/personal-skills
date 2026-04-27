# Jordan API Contract — JoFotara

## Endpoint

`POST https://backend.jofotara.gov.jo/core/invoices/`

## Headers

| Header | Required | Notes |
|---|---|---|
| `Client-Id` | yes | From per-device credentials. Exact case. |
| `Secret-Key` | yes | From per-device credentials. Exact case. |
| `Content-Type` | yes | `application/json` |

**Income Source Sequence is NOT a header.** It lives inside the UBL XML body at:
`/Invoice/cac:SellerSupplierParty/cac:Party/cac:PartyIdentification/cbc:ID`.

## Request body

```json
{ "invoice": "<base64-encoded UBL 2.1 XML>" }
```

## Success response (HTTP 200)

```json
{
  "EINV_STATUS": "SUBMITTED",
  "EINV_NUM": "EIN00091",
  "EINV_INV_UUID": "1ad1fccc-...",
  "EINV_SINGED_INVOICE": "<base64 portal-signed UBL>",
  "EINV_QR": "<base64 QR>",
  "EINV_RESULTS": { "status": "SUCCESS", "ERRORS": [] }
}
```

`EINV_STATUS` may also be `ALREADY_SUBMITTED` for replay scenarios.
Note the `SINGED` typo is in the live API — do not "fix" it in DTOs.

## Failure response (HTTP 200, EINV_STATUS=REJECTED)

```json
{
  "EINV_STATUS": "REJECTED",
  "EINV_RESULTS": {
    "status": "ERROR",
    "ERRORS": [{
      "Type": "Validation",
      "EINV_CODE": "V001",
      "EINV_MESSAGE": "..."
    }]
  }
}
```

## Auth failure response

- **PRD §3A.5 says:** HTTP **401**.
- **Avtax Slack (Apr 14) + PHP SDK + Odoo say:** HTTP **403**.
- **Action:** handle BOTH 401 and 403 as auth failure. TODO: get authoritative answer from Avtax — currently ambiguous.

## Response format variants

The reference SDK handles two formats (Format A used legacy field names like `invoiceStatus`, `qrCode`, `submittedInvoice`, `invoiceNumber`; Format B uses the `EINV_*` keys above). Our `JoFotaraResponseDTO` handles both with `getEffective*` helpers. Format B is the current production format.

## Retry policy

- **PRD §6.2:** 3 attempts, exponential backoff **5s → 30s → 2min**. Retry on: network timeout, HTTP 500/503, HTTP 429. Do NOT retry on: REJECTED, 400, 401 (auth).
- **Avtax Slack (Apr 14):** 3 attempts, backoff **2s → 5s → 10s**. Retry on 502/504 only.
- **Decision:** PRD wins (product spec). TODO: confirm with Prachi B. / Kushagra and lock in code.
- **Retry location:** `clear-routing` (NV-273), NOT core.

## Timeouts

- Typical response: 1–5s.
- Peak: 5–15s.
- Default client timeout: 100s.
- Occasional 502/504 during ISTD maintenance windows.

## What ISTD adds server-side (do NOT include in our payload)

- The signature block (UBLExtensions) — JoFotara signs server-side; we ship an unsigned envelope and store the returned `EINV_SINGED_INVOICE` to S3.
- The QR code itself — included via `AdditionalDocumentReference[ID=QR]`, but the value is added by the portal.

## Negative APIs (deliberately absent)

| Operation | Available? |
|---|---|
| Cancel invoice | No — use Credit Note (381). |
| Validate credentials | No — first signal is submission failure. |
| Bulk submit | No — one invoice per call. |
| Fetch invoice | No — no GET API. |
| List invoices | No. |
| Sandbox env | No — production only. |

Sources: `project_jordan_einvoicing.md` §3; `jordan_implementation_log.md` Sessions 1-2.
