# India — People

## Internal team (engineering / product)

| Person | Role | Slack |
|---|---|---|
| Ayush Jain | EM (manager) | `U0ABBKV5QDU`, DM `D0AC1AKDJKT` |
| Abhilash Pareek | EM (India e-invoicing) | `U01C78HQ8Q4` |
| Prachi Bajaj | PM (Tobacco RSP, IND, custom-fields) | `U08QV1Y655K` |
| Manish Tripathi | PM (FTP einvoice migration) | `U0889KF29LP` |
| Vikas Jethnani | Engineering Director | `U08U2MAV068` |
| Febin Sathar | Architect (FTP einvoice direction — einvoicing-integrations as orchestrator with strategy pattern) | `U020XCP3DEW` |
| Yash Doshi | Engineer | `U08C0D2ULSD` |
| Roshan Abhishek | Engineer | `U08QV1TT1D3` |
| Aquib Jawed | Engineer (Jordan + FTP) | `U01FSG6S057` |
| Ishaan Bhatnagar | Engineer (Peppol L3 + FTP) | TODO |
| Vashistha Garg | Engineer | `U087T0SHNCC`, self-DM `D088362AS65` |

## Customers (top-of-mind)

- **Mitsuba** — auto-GST rule template (EINVI-1231).
- **Swiggy** — RSP tobacco cutover Jan 30 - Feb 1 2026; pivot moment Jan 30 8:11 PM IST.
- **Eicher** — RCA referenced (Vikas Jethnani-owned doc, NOT user's).

## Channels

| Channel | ID | Purpose |
|---|---|---|
| `#einvoice-l3-support` | `C055ABMAVCL` | India L3 — primary signal for on-call. |
| `#einvoice_india_mea` | `C0ADWHJ2V9S` | India + MEA mixed (RCAs land here). |
| `#einv-qa` | `C04AKPP1RL4` | QA-driven design discussions (EWB Redis lock thread Jun 3). |
| `#ftp-einvoice-india` | `C0APQH50274` | FTP migration coordination. |
| `#einv-devs` | `C04U10T2DAN` | Cross-team broadcast. |

## When to ask whom

- **NIC outage / RCA tooling** → Abhilash → Ayush.
- **GST rate / HSN policy** → Prachi B. → CBIC notifications + GSTN circulars.
- **Customer-specific rule templates (Mitsuba/Swiggy/Eicher)** → Prachi B. + L3 channel.
- **FTP migration architecture** → Febin (architect direction) → Manish T. (PM).
- **IND deployment / reconcile/ind-from-main** → Ayush → senior engineering.
- **Sentry / observability** → Yash + Roshan.

## Notes

- TODO: collect Slack IDs for Ishaan Bhatnagar.
- TODO: extend `data/people.yaml` with NIC-side regulator contacts if user has them.

Sources: `project_perf_review_fy26.md` §9 (people IDs); `project_ftp_einvoice_migration.md`; `data/people.yaml`.
