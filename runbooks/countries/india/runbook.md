# India — Oncall Runbook

Common errors, debug paths, RCAs encountered.

## RCAs encountered (FY26, user-authored or co-authored)

| Date | RCA | Drive doc |
|---|---|---|
| Nov-Dec 2025 | **EWB with IRN Generation issue 18th Nov** (the VP-praised NIC RCF) — Nov 18-19, 10h25m, 190 workspaces, 51,669 failed EWBs. NIC switcher Redis-flag bug. Switcher reverted; SEV1BUGS-121/122 filed. | https://docs.google.com/document/d/127Sry5vBhB0Jm5Im1PLRr45acxZ8CJemNDHasHy8Z_A/edit |
| H2 FY26 | RCF: prod-http error% >10% einvoicing-integrations | https://docs.google.com/document/d/1QAvRouyroO9D7UfY8vN8JnXfUhtxxmz-0a6FyCKPkJ4/edit |
| H2 FY26 | RCA — Duplicate E-Way Bills Same Document Number | https://docs.google.com/document/d/1uwXqEWcDkTRIHeJXNO7tqd5yKLTyxMayM9NOlhPHcNw/edit |
| H2 FY26 | RCA — EWB via IRN Failing Error 100203 | https://docs.google.com/document/d/1DMhuqr6vNx808HaBb-jcpErKem3U5Dkjp_F4FnK1v94/edit |
| H2 FY26 | RCA — FTP Invoice Processing Stuck | https://docs.google.com/document/d/1UJfGZFXU2FfAj35HJWzmo_fb-ClZTVjMxNv1qctdGis/edit |
| H2 FY26 | RCA: autoTaxCalculate Logic Issue | https://docs.google.com/document/d/151X87SrjG6IPQs61dY4q30eUUqq6kbviXuCOhZxpIEI/edit |
| H2 FY26 | RCA — B2C Invoice Generation Failure | https://docs.google.com/document/d/1oPwpjXEiolMe68FrE7EH8KcsweFCHOgw7ejDUX5medE/edit |
| Sep 2025 (H1) | Invoice Generation Failure RCA (Sep 26-27) | (Drive doc owned by Vashistha — H1) |

The Nov 18-19 RCF is the canonical template — see `prompts/rca_template.md` (VP-praised NIC RCF format).

## Common errors / debug paths

### Duplicate E-Way Bills (same document number)

- See RCA above.
- TODO: capture trigger conditions + Redis lock interaction.

### EWB via IRN Failing — Error 100203

- See RCA above.
- TODO: capture trigger conditions + NIC error code reference.

### FTP Invoice Processing Stuck

- See RCA above.
- Channel: `#ftp-einvoice-india`.
- Migration in progress to global SFTP workflow (Febin's einvoicing-integrations orchestrator + strategy pattern).

### autoTaxCalculate logic issue

- See RCA above.
- TODO: capture conditions + module path.

### B2C Invoice Generation Failure

- See RCA above.
- TODO: capture trigger conditions.

### Custom-field case-preservation

- Sep 16 thread: https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1757999969991669
- TODO: capture root cause + fix path.

### IRN/EWB address mismatch

- Sep 26 thread: https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1758889938622379
- TODO: capture conditions.

### Delayed retrospective

- Jul 25 thread: https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1753424799447469
- TODO: ingestion-side issue.

### uniqueIdentifier date drift

- Jul 30 thread: https://cleartaxtech.slack.com/archives/C055ABMAVCL/p1753881044087989
- TODO.

## Decision trees

### High error rate alert on einvoicing-integrations

1. Check Sentry / Cubeapm dashboard.
2. Check GST/NIC portal status — is it the regulator?
3. Check Redis for lock leak (EWB).
4. Open the RCF doc above as template.

### NIC error response

1. Capture NIC error code.
2. Cross-reference with EWB GST docs (https://docs.ewaybillgst.gov.in/).
3. Distinguish: transient (retry) vs. validation (surface to user).

### FTP processing stuck

1. Check `#ftp-einvoice-india` for ongoing incident.
2. See RCA above.
3. Coordinate with Manish T. (PM) + FTP migration owners.

## Logs to grep

- `clr-irp-be` IRN issuance logs.
- `e-invoicing-be` `GenerationSourceAutoSwitch` (post-revert: NIC-only path).
- `ingestion-overlord` activity-processor-v2 (DuckDB columnar).
- Sentry tag `country=IN`.

## Known good design references

- **EWB Redis distributed-lock design** — Jun 3 #einv-qa thread (62 replies): https://cleartaxtech.slack.com/archives/C04AKPP1RL4/p1748934216844369
- **409 ingestion conflict policy-up-the-stack** — Jun 3 #einv-qa: https://cleartaxtech.slack.com/archives/C04AKPP1RL4/p1748936389620009
- **HSN master sync design** — Feb 12: https://cleartaxtech.slack.com/archives/C0ADWHJ2V9S/p1770884142931509
- **Redis SEV1 RCA** — Feb 13: https://cleartaxtech.slack.com/archives/C0ADWHJ2V9S/p1770971710394479

Sources: `project_perf_review_fy26.md` §4 (H1+H2 picks), §6 (RCAs), §9 (Slack permalinks).
