> Canonical RCF/RCA template — VP-praised NIC RCF format (Nov 18-19 2025 EWB-via-IRN incident).
> This is for Clear internal use only and not to be shared outside.
> Replace every `[BRACKETED]` placeholder. Keep section headers verbatim — panel reviewers expect them.

## Incident Title: [SHORT_DESCRIPTIVE_TITLE]

**Date of occurrence:** [DD/MM/YYYY]
**Date of review:** [DD/MM/YYYY]

### Incident Summary

> 2-3 sentences. What broke, when (start–end with timezone), who saw it, what error message they got, and whether the underlying system was actually unhealthy or only appeared so.

[INCIDENT_SUMMARY]

### Timeline Summary of Occurrence

**Incident Timeline:**
- **Incident Start Time:** [DATE_TIME_TZ]
- **Incident Reported Time:** [DATE_TIME_TZ]
- **Customer Reported to Clear:** [DATE_TIME_TZ]
- **Incident Resolved:** [DATE_TIME_TZ]
- **Clear Responded to Customer:** [DATE_TIME_TZ]
- **Total Duration:** [HH MM]

**Terminology Overview**
> Define every domain acronym used below (EWB / IRN / NIC / etc.) so a non-IND/non-domain reviewer follows along.
- **[ACRONYM_1]:** [definition]
- **[ACRONYM_2]:** [definition]

### Background & System Overview

> One paragraph + an optional table: how the affected subsystem normally works, the design decision that gave rise to the failure mode, and any prior context (earlier reverts, hotfixes) that frame this incident.

[BACKGROUND_NARRATIVE]

### Immediate Fix (Timeline Summary)

> What action stopped the bleed. One line for the fix, then the comms timeline (customer report → L2 escalation → L3 ticket → revert/hotfix). Include Slack permalinks.

[IMMEDIATE_FIX_DESCRIPTION]

- Customer reported the issue: [TIME]
- L2 escalation: [TIME]
- L3 ticket created: [TIME] — [SLACK_PERMALINK]
- Reverted/hotfixed: [TIME] — [PR_LINK]

### [DATE_DAY_N] Timeline
> Hourly bullets per affected day. Each bullet = wall-clock + what happened + which signal (Redis key write count / log error / dashboard). Repeat this section per day (Day_1, Day_2, ...).
- **[HH:MM]:** [event]

### Impact

***Which areas got impacted?***
[AREAS_IMPACTED]

***How many customers got impacted?***
- [N] unique workspaces
- [N] total unique [documents] failed in [DURATION]
- [N] total call failures

***How many tickets were raised in the system?***
- [N] customers reported the issue
- [N] L3 ticket(s) — [LINK]

***Other impact (if any)***
[OTHER_OR_NA]

### Incident Analysis

***How was the event detected (e.g. application alarm, manual etc.)?***
[DETECTION_DESCRIPTION]

***How could time to detection be improved? As a thought exercise, how could you have cut the time in half?***
[DETECTION_IMPROVEMENT]

***How did you reach the point where you knew how to mitigate the impact?***
[MITIGATION_REASONING]

### Root Cause Analysis

#### Problem Statement:
> One precise sentence: customer-visible failure + the misleading signal (e.g. error said NIC was slow but NIC was healthy).

[PROBLEM_STATEMENT]

> Continue the chain to depth 5–9. Stop at the layer that names a code/process/monitoring gap that's directly fixable. Don't bottom out at "human error" — find the system condition.

#### 1. Why did [PRIMARY_FAILURE] happen?
[WHY_1]
#### 2. Why [LAYER_2_QUESTION]?
[WHY_2]
#### 3. Why [LAYER_3_QUESTION]?
[WHY_3]
#### 4. Why [LAYER_4_QUESTION]?
[WHY_4]
#### 5. Why [LAYER_5_QUESTION]?
[WHY_5]

#### Summary of contributing factors

| Area | Gaps / Issues |
|---|---|
| Code Logic | [GAP] |
| [INFRA_LAYER, e.g. Redis TTL Behaviour] | [GAP] |
| Monitoring | [GAP] |
| Operational | [GAP] |

### Post Incident Analysis

***How was the root cause diagnosed?***
[DIAGNOSIS_NARRATIVE]

***Did you have an existing backlog item that would have prevented or greatly reduced the impact of this event?***
[YES_OR_NA]

***If yes, why was this not completed prior to the event?***
[REASON_OR_NA]

***Is it possible to programmatically audit for the vulnerability or failure mode that you experienced?***
[PROGRAMMATIC_AUDIT_PROPOSAL]

***If the change was automated, should this have been caught and rolled back in testing?***
[TESTING_GAP]

***If this change was manual, how was the change reviewed and tested?***
[REVIEW_PROCESS_OR_NA]

### Action Items

> Each item ends with a Jira ticket linked. Add label `#sev1bug` (or appropriate Sev tag) for tracking.

1. [ACTION_1] — [JIRA_TICKET_LINK]
2. [ACTION_2] — [JIRA_TICKET_LINK]
3. [ACTION_3]
4. [ACTION_4]

### Learnings

1. [LEARNING_1]
2. [LEARNING_2]
3. [LEARNING_3]

### Metrics and Graphs

> Attach: top-N affected users, hourly failure curve, error-rate dashboard screenshot. Note explicitly if no spikes appeared in error rate (= alerting gap).

[METRICS_NOTES]

### Checklist before panel review

- [ ] Timelines are clear and precise (supported by metrics)
- [ ] Communication timelines (Customer↔Tech/Delivery, Tech/Delivery↔Customer) are stated separately from incident timelines
- [ ] No. of tickets and no. of customers impacted are both stated (they differ)
- [ ] Each Action Item is tracked through Jira (with `#sev1-bug` label)
- [ ] All open comments are answered and closed
