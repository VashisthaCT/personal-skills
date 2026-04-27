# India Credentials Model

TODO — current memory does not have a clean credential-model writeup for India. Capture from `clr-irp-be` config + Vault paths in a future session.

## What we know

- **NIC environments:** NIC1 (legacy primary) and NIC2. Auto-switcher between them was reverted post-Nov 18-19 outage; today the system is locked to NIC-only.
- **GSTIN-level credentials:** stored per-GSTIN in NodeSettings (similar pattern to other countries — see `clear-sales/einvoice-global/.../ClientCredentialSetting.java`).
- **Bulk identity operations:** NV-191 (clr-irp-be#482) updated `annualTurnover` for 26,063 GSTINs in <3 days using InternalOnlyApi + slab mapper.

## TODO sections

- Auth model (NIC API user/password, AES encryption strategy).
- Token lifecycle if applicable.
- Rotation policy.
- Vault path conventions for IRP credentials.
- Failure modes and surface-area in UI.
- How NIC1/NIC2 credential mapping was done before the switcher revert.

## Cross-reference

- `e-invoicing-be` `GenerationSourceAutoSwitch` is the file that was neutralized in `reconcile/ind-from-main` Batch 2. All neutralization marked `[IND-RECONCILE]`. Sources list, `getNicCredentialsType`, `getNextGenerationSource`, `isNic2SwitchingEnabledForCurrentWorkspace` all locked to NIC-only.
- Workspace exclusion framework (Batch 1) — 5 new files + 45 annotations on 3 repo files.

Sources: `project_perf_review_fy26.md` §4 (NIC switcher revert); `project_ind_reconciliation.md`. Mark TODO where memory lacks concrete credential-store detail.
