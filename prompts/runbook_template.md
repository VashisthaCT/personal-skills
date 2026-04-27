> Oncall runbook section template — matches the e-InvoiceVerse `troubleshooting/_TEMPLATE.md` format used across countries.
> One file = one country/region. Each repeating block (a "common cause" or a decision-tree branch) follows the structure below.
> Replace every `[BRACKETED]` placeholder. Keep section headers verbatim so `/v-country-brain` can parse them.

# [COUNTRY_OR_REGION_NAME] — Oncall Runbook

## Affected Services

> List the services involved when an incident touches this country/region. Use service names from `platform_architecture.md` §1 (einvoicing-core, einvoicing-integrations, clear-routing, ingestion-overlord, clear-peppol-ap, ftp-magnet-3, etc.).

- [SERVICE_1] — [role, e.g. "primary API gateway", "country module owner"]
- [SERVICE_2] — [role]
- [SERVICE_3] — [role]

## Symptoms

> What does the customer / oncall see first? Error message text, dashboard signals, channel where complaints land.

- [SYMPTOM_1] — e.g. error message verbatim: "[ERROR_TEXT_OR_CODE]"
- [SYMPTOM_2] — e.g. dashboard "[DASHBOARD_NAME]" shows [METRIC] crossing threshold
- [SYMPTOM_3] — e.g. customer escalation in `#[SLACK_CHANNEL]`

---

## Common Causes

> One sub-section per recurring cause. Each MUST have all three: how-to-identify, resolution, prevention.
> When a cause traces to a published RCA, link it under "Related RCAs" in the cause body.

### Cause: [CAUSE_TITLE_1]

**How to identify**
- [SIGNAL_1] (e.g. log line, Redis key state, NIC error code, S3 object key pattern)
- [SIGNAL_2]

**Resolution**
1. [STEP_1]
2. [STEP_2]
3. [STEP_3]

**Prevention**
- [PREVENTIVE_MEASURE] (alert / circuit breaker / config change / test gap to close)

**Related RCAs**
- [RCA_TITLE] — [DRIVE_DOC_URL]

### Cause: [CAUSE_TITLE_2]

**How to identify**
- [SIGNAL_1]

**Resolution**
1. [STEP_1]

**Prevention**
- [PREVENTIVE_MEASURE]

---

## Diagnostic Steps (Decision Tree)

> Numbered tree from "alert just fired" to "we know what to do". Each step is a yes/no or branching question. Include the channel/dashboard/JQL/log query inline so oncall doesn't have to remember it.

1. **Is this a regulator-side outage?**
   - Check: [REGULATOR_PORTAL_URL or status page]
   - If yes → wait + post status to `#[CUSTOMER_CHANNEL]`. Stop.
   - If no → continue.

2. **Which action class is failing?**
   - Run: [JQL_OR_LOG_QUERY]
   - If [CONDITION_A] → go to step 3.
   - If [CONDITION_B] → go to step 4.

3. **Is `[ERROR_CODE]` in the audit trail?**
   - If yes → see `Cause: [CAUSE_TITLE_1]` above.
   - If no → escalate.

4. **[NEXT_BRANCH_QUESTION]**
   - [BRANCH_ANSWER]

---

## Related Error Codes

> Country/region error code reference. Link upstream regulator docs.

| Code | Meaning | Source | Action |
|---|---|---|---|
| [CODE_1] | [meaning] | [Regulator/Vendor] | [retry / surface / escalate] |
| [CODE_2] | [meaning] | [Regulator/Vendor] | [action] |
| [CODE_3] | [meaning] | [Regulator/Vendor] | [action] |

Upstream references:
- [REGULATOR_DOCS_URL]
- [VENDOR_API_DOCS_URL]

---

## Escalation

**When to escalate**
- [TRIGGER_1] (e.g. >N customers reporting in 30 min)
- [TRIGGER_2] (e.g. failed > 10% of calls for 15 min)
- [TRIGGER_3] (e.g. cause not in this runbook)

**To whom**
- L3 oncall: `#[L3_CHANNEL]` (channel ID `[CHANNEL_ID]`)
- Country EM / PM: [NAME] — Slack DM `[SLACK_USER_ID]`
- Regulator liaison (if applicable): [NAME] — [CONTACT]
- DevOps: `#[DEVOPS_CHANNEL]`

**What artifacts to capture before escalating**
- `mongo-id` of the failing document(s)
- `s3Key` of the inbound XML / FTP file
- `requestId` from headers (`X-Request-Id`)
- `taxpayerOrgId` + `branchOrgId` + workspace ID
- Audit-trail entries for the affected `[ENTITY_TYPE]`
- Sentry / Cubeapm trace link
- Approximate failure-volume window (start/end timestamps)

---

## Logs to grep

- `[SERVICE_1]` — `[LOG_PATTERN_OR_LOGGER_NAME]`
- `[SERVICE_2]` — `[LOG_PATTERN_OR_LOGGER_NAME]`
- Sentry tag `country=[CC]`
- Cubeapm filter `[FILTER_EXPR]`

## RCAs encountered

| Date | Title | Drive doc |
|---|---|---|
| [DATE] | [TITLE] | [URL] |
| [DATE] | [TITLE] | [URL] |

## Known good design references

- [DESIGN_TITLE] — [SLACK_PERMALINK or DRIVE_URL]
- [DESIGN_TITLE] — [SLACK_PERMALINK or DRIVE_URL]
