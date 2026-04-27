# India — Live State

**As of memory snapshot Apr 2026.**

## Status: Live (long-running, on-call heavy)

- Both IRN issuance and EWB are live across multiple customers.
- ClearTax IRP is operating; SLA monitoring APIs in place.

## Active workstreams

### IND reconciliation from main

- Branch: `reconcile/ind-from-main` (started 2026-03-20).
- Goal: stop bi-directional drift between `main` (GCC trunk) and IND-deployed `hotfix/2.401.104` (diverged at `2.401.0`). End state: `main` is a superset of hotfix.
- Done: Batch 1 (workspace exclusion framework — 5 new files + 45 annotations), Batch 2 (NIC2 auto-switching neutralized in `GenerationSourceAutoSwitch`).
- Remaining: continue future batches on the same branch; grep `[IND-RECONCILE]` to find neutralization points.
- Build can't run locally due to Lombok 1.18.20 / JDK 17.0.14 incompatibility (pre-existing). Not blocking — CI handles.

### FTP einvoice migration

- Channel: `#ftp-einvoice-india` (`C0APQH50274`).
- Direction (Febin): einvoicing-integrations as orchestrator with strategy pattern. 4-5 week task.
- PM: Manish Tripathi.
- Goal: IND + KSA → global SFTP workflow.

### Single-NIC mode (post-Nov 2025 outage)

- NIC1 ↔ NIC2 auto-switcher is REVERTED. System runs on NIC-only.
- Action items from RCA: SEV1BUGS-121, SEV1BUGS-122 (filed; statuses TODO).

## Customers onboarded (mentioned in memory)

- **Mitsuba** — auto-GST rule template live (EINVI-1231).
- **Swiggy** — RSP tobacco cutover Feb 1 2026.
- **Eicher** — referenced RCA (not user-owned).
- (Many others — list is much larger; this is just the top-of-mind set from FY26 work.)

## Known issues / warnings

1. **NIC1/NIC2 switcher** is reverted. Re-enabling requires fixing the Redis-flag bug that caused the 10h25m outage on Nov 18-19 2025.
2. **Lombok / JDK incompatibility** for local builds of `e-invoicing-be`. Pre-existing. Workaround: use CI.
3. **EWB Redis distributed lock** — H2 follow-up shipped (EIOCJ-670). Watch for race conditions under load.
4. **40% GST rate cutover** (Sep 2025) — was a 2-day dev sprint with low margin. Future rate changes should follow this template (Sept 22 deployment was clean).
5. **Sentry onboarding** — IND + GCC are wired (EINVI-1260). Ensure new code paths emit `skill.*` style tags.

## Recent SEV1 / outage history

- **Nov 18-19 2025** — 10h25m outage. 190 workspaces, 51,669 failed EWBs, 139,062 call failures. NIC switcher Redis-flag bug. RCA authored Nov-Dec 2025 by Vashistha; reviewed by senior leadership. Switcher reverted. SEV1BUGS-121, SEV1BUGS-122 filed.

## Recent activity

(Append-only, populated by `country-knowledge-curator`.)

Sources: `project_ind_reconciliation.md`; `project_perf_review_fy26.md` §5 (NIC outage), §6 (RCAs); `project_ftp_einvoice_migration.md`.
