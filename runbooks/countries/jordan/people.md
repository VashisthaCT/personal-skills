# Jordan — People

## Internal team

| Person | Role | Slack |
|---|---|---|
| Aquib Jawed | Engineer (Jordan core/enums — NV-264, NV-265) | `U01FSG6S057` (DM `D097RE9HL5Q`) |
| Kushagra Bhardwaj | Engineer (Mappers, XSLT, routing — NV-267, NV-268, NV-273, NV-271, NV-272, NV-274) | DM `D0A8G1XJPMJ` |
| Khushboo Kundnani | Engineer (Frontend — NV-270, NV-283..289) | (Slack ID — TODO) |
| Ayush Jain | Engineering Manager (NV-263 epic owner, manager) | `U0ABBKV5QDU`, DM `D0AC1AKDJKT` |
| Prachi Bajaj | PM (planning + Jordan PRD owner) | `U08QV1Y655K` |
| Vashistha Garg | Engineer (NV-266, NV-269 — module + creds backend) | `U087T0SHNCC`, self-DM `D088362AS65` |

## Channels

| Channel | ID | Purpose |
|---|---|---|
| `#mea_jordan_egypt_oman_discovery` | `C0ABA7RC1QD` | Jordan + MEA discovery channel — primary signal |
| Jordan team group DM | `C0ASEKS03K8` | Day-to-day eng coordination |
| `#einv-devs` | `C04U10T2DAN` | Broader engineering broadcast |

## Regulator / consultant

| Entity | Role | Notes |
|---|---|---|
| ISTD (Income & Sales Tax Department, Jordan) | Regulator | Operates the JoFotara portal at https://portal.jofotara.gov.jo/en. No publicly listed support contact for SP-level integrators. |
| Avtax | Tax-tech consultant | 3-month engagement (~$2,200). Authoritative source for Avtax data dictionary slides + ClearTax tech sheet. Contact via shared Slack channel + email Prachi B. has. |

## When to ask whom

- **API contract / payload shape ambiguity** → Avtax (via shared Slack), then PRD §6.2 / §3A.5 for tie-break.
- **PRD scope / spec clarification** → Prachi B. → Avtax.
- **Routing / vendor-client behaviour** → Kushagra (PR #1323, #134).
- **Pint / shared model fields** → Aquib (PR #1313, #392).
- **Frontend / UI fields** → Khushboo.
- **Vault / Ops / deployment config** → Ayush J. → DevOps.
- **Licensing provisioning** → Licensing team (per-customer-workspace).

## Notes

- TODO: collect Khushboo's Slack ID and add to `data/people.yaml`.
- TODO: confirm Avtax primary contact name + email.

Sources: `project_jordan_einvoicing.md` §1; `jordan_implementation_log.md` Sessions 1-2; `data/people.yaml`.
