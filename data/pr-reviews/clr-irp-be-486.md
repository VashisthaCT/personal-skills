---
pr_url: https://github.com/ClearTax/clr-irp-be/pull/486
author: UtsavClear
mode: others
review_date: 2026-05-14T13:00:00+05:30
verdict: request-changes
findings_count: 9
substantive: true
files_reviewed: 3
jira: NV-375
jira_project_mismatch: true
---

## Review — PR #486: [NV-375] API-SLA Update Response Format and CSAT Calculation for GSTN Integration

**Author:** UtsavClear (Utsav Pandey, intern) · **Repo:** ClearTax/clr-irp-be · **Mode:** others
**JIRA:** NV-375 (P0, Story, project=NV/E-INV-MEA, reporter=Prachi, assignee=Utsav)
**Verdict:** ⚠️ **request-changes** — scope-correct but acceptance criteria #2 not actually met; CI red; data-source gap glossed over; one semantic bug still present.

---

### 1. Correctness

**🔴 csatSla is still hardcoded — fails JIRA AC #2 in spirit**
[ServiceLevelAgreementService.java:652-654](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/services/impl/ServiceLevelAgreementService.java:652) — value changed `100.0 → 97.14`, but it is still a literal repeated 3× (24h / 7d / 30d).
JIRA AC #2 says: *"CSAT value returns 97.14 **based on the last 1 year of data**"*. The PR delivers the number, not the calculation.
**Root cause:** [IrpCaseDTO.java](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/dtos/sla/salesforce/IrpCaseDTO.java) has no CSAT field. There is no source data wired in. The intern picked the literal because the dependency doesn't exist. This is a Salesforce schema/integration gap, not laziness — but the PR description should call it out and a follow-up ticket should be linked.
**Risk:** value will become stale within a quarter; GSTN audit could spot the constant across long windows (24h ≡ 7d ≡ 30d ≡ 97.14 forever).

**🟡 perrequesttrans / tatrejectionresponse semantic still inverted**
[ServiceLevelAgreementService.java:501-507](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/services/impl/ServiceLevelAgreementService.java:501) and [:551-555](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/services/impl/ServiceLevelAgreementService.java:551) compute `1 − (within 500ms / total)` → that's **breach** ratio, not compliance. After `× 100`, the value reported to GSTN is breach %, but the metric name suggests compliance %. This is the *exact* ambiguity GSTN flagged in their email ("What 1 means here. Not clear.") that triggered NV-375.
The PR scales the wrong number. Out of NV-375 scope per the literal AC, but worth flagging back to Prachi before merge — otherwise GSTN will receive `0.443` (was `0.00443`) and still not understand it.

**🟡 Rejection-time fallback `return 100.0;`** [line 558](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/services/impl/ServiceLevelAgreementService.java:558)
When there are no rejection responses, returns hardcoded 100.0. Indistinguishable from a real "100% met SLA over thousands of rejections". Should return `null` so JSON serialises as `NULL` (matches `fnegtive/fpositive/timelyexecr` style in the table). Same concern existed pre-PR; PR carries it forward.

**🟢 × 100 conversion correctly applied** in 5 spots: success-transaction, IRP availability, validation accuracy, response-time compliance, rejection-time compliance. Math is right, precision preserved (`setScale(5, DOWN)`).

**🟢 `normalizeSmallValue()` removal is safe**
Function clipped values < 0.0001 to 0.0. After ×100 the equivalent threshold would be < 0.01. The dropped clamp now lets values like `0.082` flow through instead of being floored to 0. Real signal, slight precision win. But the removal isn't justified in the PR description.

---

### 2. Impact

**🟢 Blast radius is narrow.** [ServiceLevelAgreementController.java](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/controllers/ServiceLevelAgreementController.java) endpoints are all `@IrpApiAuthentication(userType = IRPUserType.GSTNUSER)` — **only GSTN consumes these**. No internal Coralogix/Grafana dashboards read this DTO. No `@Cacheable` on the service methods. Safe to roll out without coordinated downstream changes.

**🔴 JIRA filed under wrong project — CI is red for this reason**
PR title `[NV-375]`. NV = "E-INV-MEA" (Middle East/Africa). Repo `clr-irp-be` is India IRP. The "Jira Story/Task Key Checker" workflow has **failed 6 times** on consecutive pushes ([statusCheckRollup confirms](https://github.com/ClearTax/clr-irp-be/actions/runs/25792503690)) — almost certainly because the checker expects an IRP-prefix ticket for this repo. **Action:** clone NV-375 into the IRP Jira project, update PR title, retrigger CI.

**🟡 TimePeriodStats default flipped 1.0 → 100.0**
[TimePeriodStats.java:17,21,25](Desktop/clr-irp-be/gstn-data-sync/src/main/java/in/clear/irp/gst/data/sync/dtos/sla/TimePeriodStats.java:17). Any `TimePeriodStats.builder().build()` without explicit setters now serialises as a perfect 100% score across all three windows. This is a "fail-open" default — uninitialised metrics now look like SLA met. Same trap as before just at 100× magnitude. Should be `null` (so missing → JSON null → GSTN sees no value), matching `fnegtive/fpositive/timelyexecr` pattern.

**🟢 No DB / Vault / config touched.** Pre-merge checklist boxes in PR body are unticked but that's because there are no config changes — author should explicitly check "no config changes" before merge, not leave blank.

---

### 3. Test quality

**🔴 Tests are renumbered constants only.** [ServiceLevelAgreementControllerTests.java](Desktop/clr-irp-be/gstn-data-sync/src/test/java/in/clear/irp/gstn/data/sync/tests/ServiceLevelAgreementControllerTests.java) lines 108, 149, 173, 186-188 — every change is `1.0 → 100.0` or `0.9876 → 98.76`. The tests don't actually verify the **conversion**; they verify the final number. If the `× 100` line were silently removed tomorrow, these tests would still pass against a mock that returns 100.0 directly.

**Missing test coverage:**
- No assertion of the multiplication itself (input ratio `0.9999` → output `99.99000`)
- No test for csatSla = 97.14 (not even a getter assertion)
- No test for rejection-time fallback (returns 100.0 when prometheus null)
- No edge case: prometheus returns 0.0 → output 0.0; prometheus returns 1.0 → output 100.0
- No regression test for the dropped `normalizeSmallValue` (input 0.00008 → was clipped to 0, now passes through as 0.008)

**🔴 Local test run did not complete** — `mvn -pl gstn-data-sync test -Dtest=ServiceLevelAgreementControllerTests` blew up on JDK module-access for `com.sun.tools.javac.processing` (annotation processor on lombok/jacoco). Repo needs older JDK + `--add-opens` flags. Did not verify pass/fail locally.

---

### 4. Concerns / nits

- **Repeated literal `BigDecimal.valueOf(100)`** — 5 occurrences. Extract `private static final BigDecimal PERCENT_MULTIPLIER = BigDecimal.valueOf(100);`. Minor.
- **PR description**: claims "All ServiceLevelAgreementControllerTests pass" — that's true after the rebase but doesn't prove the conversion works (see Test quality).
- **No mention of the csatSla data-source gap** — should be in the PR body as a known limitation + follow-up ticket reference.
- **No ai-tag / AI-Assisted marker** in body. Not applicable for intern PRs but worth noting if intern used Cursor/Copilot.
- **AC #3 ("UAT sign-off against GSTN format")** — not addressable in code review; needs Prachi to UAT post-merge.

---

### 5. Country / runbook context (India IRP)

Read `~/dev/personal-skills/runbooks/countries/india/`:
- `code_map.md` — SLA endpoints at `/irpsla/v1.0/*`, GSTN-locked. Matches PR.
- `runbook.md` — no prior SLA-format RCA; this is a fresh GSTN ask.
- No conflict with runbook claims.

**Regulatory-submission caveat:** This data goes to GSTN — a *regulator*. Wrong format flagged in an audit can trigger compliance reviews. Tier per `reference_cleartax_rca_review_tiers.md`: VP (Apoorva) reviews patterns. A hardcoded `97.14` that drifts from real CSAT for 6+ months is the kind of pattern VP review catches. Recommend a TODO + JIRA follow-up linked in code:

```java
// TODO(NV-XXX): Compute CSAT from Salesforce trailing 12-month survey data
// once IrpCaseDTO exposes the csat__c field. Currently hardcoded per AC #2.
```

---

### 6. TL;DR

PR delivers the **format change** (× 100) cleanly and tests still pass conceptually. But:
1. **CSAT AC #2 is met in number, not in spirit** — still a literal, no data source.
2. **CI is red** because the JIRA project key is wrong (NV-* vs IRP-*).
3. **Tests don't actually test the conversion** — they test the post-conversion constant.
4. **Pre-existing perrequesttrans/tatrejectionresponse semantic ambiguity** carried forward (out of JIRA scope, but it's the actual GSTN pain point).

**Ask intern to:**
- Re-file ticket under IRP project, update PR title, unblock CI.
- Add a TODO + follow-up JIRA for dynamic CSAT computation; document data-source gap in PR body.
- Add one input-output test that exercises the `× 100` multiplication explicitly (mock prometheus to return `0.9999`, assert response is `99.99000`).
- Decide with Prachi: flip `return 100.0` fallback to `return null` (matches NULL pattern in spec).
- Consider `TimePeriodStats` defaults to `null` not `100.0` so uninitialised fields don't fail-open.
