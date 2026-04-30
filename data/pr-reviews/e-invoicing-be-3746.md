---
pr_url: https://github.com/ClearTax/e-invoicing-be/pull/3746
author: ayushjain-clear
mode: others
review_date: 2026-04-30T15:30:00+05:30
verdict: request-changes
findings_count: 11
substantive: true
files_reviewed: 13
---

## Review — PR #3746: Isolate ZATCA HTTP path with dedicated OkHttpClient + bulkhead

**Author:** ayushjain-clear (Ayush) · **Repo:** ClearTax/e-invoicing-be · **Mode:** others
**Verdict:** ⚠️ request-changes (CI red + JIRA missing; design sound)

### Context
This is the ZATCA-side remediation following the **27-Apr-2026 KSA outage RCA** (ref `project_ksa_outage_rca.md`). The shared `OkHttpClient` + 60s read timeout + no bulkhead is exactly the blast-radius mechanism the RCA called out. Design intent matches the RCA's "isolate ZATCA" recommendation. Reviewer: abhilashpareek08 (Abhilash, EM).

### 1. Correctness

- **Resilience chain order is `CircuitBreaker( Retry( Bulkhead( call ) ) )`** as documented [ResilienceHelper.java:108-118](common/src/main/java/in/cleartax/einvoice/common/configs/helper/ResilienceHelper.java:108). Innermost bulkhead means each retry attempt acquires its own permit. Single in-flight logical request still holds 1 permit at a time (retries are sequential), so this is fine — but worth flagging: with bulkhead **outermost** instead, the entire CB+Retry+call chain runs under one permit, which gives slightly better load isolation against transient downstream slowness (a slow call with retry=2 can't double-book a permit). Either is defensible; the PR has chosen and documented its choice. ✅
- **`BulkheadFullException` does not retry**: confirmed via `getRetryer()` whitelist in [ResilienceHelper.java:215-222](common/src/main/java/in/cleartax/einvoice/common/configs/helper/ResilienceHelper.java:215). `retryExceptions(...)` is a whitelist — `BulkheadFullException` is absent → no retry storm on saturation. ✅ Matches PR claim.
- **Null-safe bulkhead path**: `getBulkhead(null, identifier)` returns null → `Bulkhead.decorateCallable` skipped → existing 3-arg `callWithResiliency(CB, Retry, Callable)` callers (NicEInvoiceClient, NicEWayBillClient, DocumentClient, etc. — 34 call sites) are unaffected. ✅ Backwards-compat preserved.
- **Static `meterRegistry` field reuse**: `getBulkhead` uses the same static `meterRegistry` as `getCircuitBreaker` / `getRetryer` ([ResilienceHelper.java:45-50](common/src/main/java/in/cleartax/einvoice/common/configs/helper/ResilienceHelper.java:45)). Pattern is consistent — bulkhead metrics will publish via `TaggedBulkheadMetrics`. ✅
- **Dispatcher cap vs bulkhead cap on a single-host upstream**: `Dispatcher.maxRequestsPerHost=64` and `Bulkhead.maxConcurrentCalls=64` are equal. ZATCA is a single host (`gw-fatoora.zatca.gov.sa`), so `maxRequests=128` is dead capacity — the per-host limit will gate first. Bulkhead becomes the de-facto throttle. Functionally fine, but `maxRequests=128` is misleading config. Consider `maxRequests=64, maxRequestsPerHost=64` for clarity, or set Dispatcher above Bulkhead with intent (e.g., `maxRequestsPerHost=80, bulkhead=64` so dispatcher doesn't reject before bulkhead's `maxWaitDuration` kicks in).

### 2. Impact

- **Single ZatcaClient construction site**: only [ZatcaDependencyBeans.java:60-64](gcc-device-onboarding/src/main/java/in/cleartax/einvoice/ZatcaDependencyBeans.java:60). Constructor signature change is fully contained. No other module instantiates `ZatcaClient`. ✅
- **ZatcaClient consumers**: only `ZatcaInteractionServiceImpl` (gcc-device-onboarding). Bean update propagates transparently. ✅
- **Bean ambiguity check for `OkHttpClient`**: with two beans now (`okHttpClientWithAuditTrailInterceptor` + `zatcaOkHttpClient`), Spring resolves by parameter name where `@Qualifier` is absent. All 6 `EInvoicingApplication` consumers either use `@Qualifier(...)` or have parameter name `okHttpClientWithAuditTrailInterceptor` — name-based resolution will work. The duplicate `getEinvoiceClient(OkHttpClient okHttpClientWithAuditTrailInterceptor)` in `ZatcaDependencyBeans` also relies on name-match. ✅ verified — but brittle. Consider adding `@Primary` to `okHttpClientWithAuditTrailInterceptor` so future no-qualifier beans don't silently bind to the new ZATCA client.
- **kafka-worker-consumers/applications module isolation**: the `zatcaOkHttpClient` bean is defined in `EInvoicingApplication` (the `applications` module). `gcc-device-onboarding`'s `ZatcaDependencyBeans` is `@DependsOn("resilienceHelper")` and gets the bean via `@Qualifier("zatcaOkHttpClient")`. As long as the gcc module's @Configuration is component-scanned by `EInvoicingApplication`, this wires up. It is — the `@ComponentScan` covers `in.cleartax.einvoice`. ✅
- **kafka-worker-consumers app context**: that module has its own `DependencyBeans.okHttpClientWithAuditTrailInterceptor` bean (separate Spring context). It does NOT use `ZatcaClient`, so no impact there. Verified — `ZatcaClient` is not imported in `kafka-worker-consumers`. ✅
- **Connection-pool tradeoff acknowledged**: PR body flags the extra socket count from a dedicated `ConnectionPool`. Reasonable cost for the isolation benefit.

### 3. Test quality

- **Zero unit-test coverage added**. No tests for:
  - `ResilienceHelper.getBulkhead(...)` — new factory method.
  - `callWithResiliency(... Bulkhead ...)` — new overloads with bulkhead decoration.
  - `ZatcaClient` 4-arg constructor wiring.
  - `BulkheadConfiguration` deserialization.
- The repo has **no existing tests** for `ResilienceHelper` or `ZatcaClient` (verified via `find` — no `ResilienceHelperTest*` or `ZatcaClientTest*` anywhere). So this is a continuation of a prior gap, not a regression. But for a resilience-pattern change born from a Sev1 outage, at minimum I'd expect:
  - One unit test per new ResilienceHelper overload that exercises `Bulkhead.decorateCallable` (mock bulkhead, verify decoration).
  - One ApplicationContext smoke test that boots the test profile and asserts the `zatcaOkHttpClient` bean is present and the `ZatcaClient` constructor wires it.
- **`application-test.yml` is not updated** with a `bulkhead` block ([applications/src/test/resources/application-test.yml](applications/src/test/resources/application-test.yml:592)). Tests therefore exercise only the null-bulkhead path. The new bulkhead/`BulkheadFullException` behavior is **never executed in CI**. Add a bulkhead block to the test profile (small concurrency, e.g. `maxConcurrentCalls: 4`, `maxWaitDurationMillis: 100`) so at least the wiring is exercised on every CI run.
- **Test plan in PR body is integration/manual-only** — load test, smoke test, Prometheus metrics check. Fine as a rollout plan, but does not protect against regressions on subsequent refactors.

### 4. Concerns / nits

- **🔴 CI red — must be green before merge:**
  - **`Jira Story/Task Key Checker / publish` FAILED** — `Jira Issue Key missing in PR title or description.` PR body has no JIRA ticket reference. Add the ticket (likely the KSA-outage follow-up ticket from the RCA action items).
  - **`AnalyzePR / Analyze and Test` FAILED** at the "Compile & Test" step. All test runs in the visible log show 0 failures/errors — failure is likely in a post-test phase (jacoco coverage threshold = 50, or sonar). The PR body's honest disclaimer "Local `mvn compile` was not run … relying on CI to validate" is the right call, but the CI signal now says investigate. Pull `gh run view 25154341773` and find the failed surefire/jacoco target.
  - `ai-review` StatusContext is ERROR — usually environmental, less critical, but worth a glance.
- **🟡 Silent no-op risk on misconfigured envs**: `getBulkhead(null, identifier)` returns null and the bulkhead is silently disabled. For an env where the `bulkhead:` block is accidentally omitted (e.g., a future new region/profile), ZATCA loses its bulkhead protection without any warning. Suggest: `log.warn("No bulkhead configuration for {} — bulkhead disabled", identifier)` in the null branch, OR fail-fast with a config-validation exception for production profiles. Same applies to test config — silent disable in tests is acceptable but should be deliberate.
- **🟡 Two new files missing newline at EOF**: [BulkheadConfiguration.java](common/src/main/java/in/cleartax/einvoice/common/configs/BulkheadConfiguration.java:13) and [ZatcaClient.java](gcc-device-onboarding/src/main/java/in/cleartax/einvoice/clients/ZatcaClient.java:88). Workflow has `check-formatting: false` so it won't fail CI, but spotless will flag this on the next format pass.
- **🟡 PR body claims `BulkheadFullException` "propagates as a 5xx for sync `/generate`"** — verified the exception is not in the retry whitelist, but I haven't traced what `/generate`'s exception handler maps `BulkheadFullException` to. For a saturated state, the user-facing response code matters (5xx vs 503-with-Retry-After is a meaningful difference for the caller's retry behavior — consider 503 + `Retry-After: 1` if not already). Worth confirming with a quick smoke test.
- **🟡 No design doc / Confluence link in PR body**. For a Sev1-driven resilience change, an LLD or RCA-action-item reference would help reviewers and future archaeology. The PR body is otherwise excellent — Why/What/How/Defaults/Risks/Test plan all present.
- **🟢 AI tag present**: `Co-Authored-By: Claude Opus 4.7 (1M context)` in commit message — ✅.
- **🟢 Branch fresh**: tip is from today; main last touched 2 days ago. No stale-base issue.
- **🟢 Defaults conservative and env-overridable**: `maxConcurrentCalls=64, maxWaitDurationMillis=1000` is a sensible starting point. PR explicitly asks reviewers to tune against observed peak — correct framing.
- **🟢 Mergeable**: branch is mergeable; no conflicts.

### 5. Pre-flight (own mode only)
N/A — others' PR.

### 6. TL;DR
Design and implementation are sound and correctly address the KSA-Apr-27 RCA's "shared OkHttpClient blast radius" finding. Two CI failures are merge-blockers: (a) **add a JIRA ticket reference** to PR body to unblock the JIRA key checker, and (b) **diagnose the `Compile & Test` failure** — tests pass, so it's likely jacoco coverage or sonar. Strongly recommend adding at least a smoke unit test for `getBulkhead` + an ApplicationContext test that boots and asserts `zatcaOkHttpClient` wires up; current PR adds zero unit-test coverage to a Sev1-driven resilience change. Minor: silent no-op when `bulkhead` block is missing from yaml is a future foot-gun — log a warning or fail-fast. Once CI is green and JIRA is linked, this is good to merge.
