---
name: v-customer
description: Given a customer ID from data/customers.yaml (top-10 curated MAF/Tabby/Mitsuba/Swiggy/Eicher + 5 placeholders), surface all JIRA tickets, Slack threads, PRs, and RCAs related to that customer. Counts toward SE-II "Customer Understanding" rubric line (≥4 customer-named investigations per half).
---

You are aggregating Vashistha's work touching a specific customer. Output is a consolidated briefing across JIRA / Slack / PRs / RCAs.

## Input

A customer ID (e.g. `tabby`, `mitsuba`, `swiggy`, `eicher`, `maf`) OR a customer name string for fuzzy match.

## Step 1 — Resolve customer

1. Read `~/dev/personal-skills/data/customers.yaml`.
2. Match by `id` exact, then by `name` substring (case-insensitive).
3. If not found:
   - Suggest closest matches from the 5 named customers.
   - If user-provided string isn't in customers.yaml at all, ask: "This customer isn't in `data/customers.yaml`. Want me to add as `customer-N` placeholder?"

## Step 2 — Aggregate (last 180 days, parallel queries)

### JIRA tickets
- JQL: `(assignee = currentUser() OR reporter = currentUser()) AND text ~ "<customer name>" AND updated >= -180d ORDER BY updated DESC`
- cloudId: `e435c3a3-1fe3-4dd6-9ccb-16a3ce431f86`
- Capture: `key`, `status`, `summary`, `updated`, `priority`, `link`

### Slack threads
- Search Slack workspace for `<customer name>` in messages where user `U087T0SHNCC` participated, last 90 days.
- Slack MCP caps at 20 msgs/query — paginate if needed.
- Group by thread (parent message). Limit 10 threads.
- Capture: `channel`, `permalink`, `top_message_text`, `reply_count`, `last_activity`.

### GitHub PRs
- `gh search prs --author=VashisthaCT body-contains "<customer name>" --created ">=$(date -v-180d +%Y-%m-%d)"` (sandbox-disabled).
- Also try title-contains via separate query.
- Capture: `repo`, `pr_number`, `title`, `state` (open/merged/closed), `link`.

### RCAs
- Drive search: `owner = 'vashistha.garg@clear.in' AND fullText contains '<customer name>' AND (title contains 'RCA' OR title contains 'RCF') AND modifiedTime >= '2025-10-28T00:00:00Z'`.
- Skip auto-Meet-Transcripts (`parentId == 1i0Msm1KKgwpCdsWtfjfcoT_21zuxMcuF`).
- Capture: `title`, `last_modified`, `link`.

## Step 3 — Compose

Markdown output:
```
## <Customer name> (<country code>)
*Status:* <from customers.yaml>
*Notes:* <from customers.yaml>

### JIRA (<count>)
- [KEY-NN](url) `<status>` `<priority>` — <summary> (updated <date>)
- ...

### Slack threads (<count>)
- [<channel>](permalink) — <top_message> — <N> replies (last <date>)
- ...

### PRs (<count>)
- [<repo>#<PR>](url) `<state>` — <title>
- ...

### RCAs (<count>)
- [<title>](url) — <date>
- ...

### Suggested next actions
1. <if any open JIRA in this customer's pile is >14d stale, surface it>
2. <if RCAs exist, link to runbook section: `runbooks/countries/<cc>/runbook.md` if any>
3. <if customer status in customers.yaml is "onboarding", link relevant runbook>
```

## Step 4 — Output

Print to chat by default. With `--draft` flag: post to self-DM `D088362AS65`.

## Constraints

- Drafts only — no auto-Slack-post to customer channels or external email.
- Real customer names OK per privacy decision. Never include real TINs / API secrets / credentials.
- Don't fabricate counts — if a section returns nothing, say "(none in last 180 days)".
- Cross-reference `runbooks/countries/<country-of-customer>/runbook.md` if customer is country-anchored.

## Verifiable success

- Output covers 4 sections (JIRA, Slack, PRs, RCAs).
- Every claim has an inline link or "(none)".
- Customer ID resolves to a real `data/customers.yaml` entry.
- "Suggested next actions" only references real items found above (no fabricated suggestions).

## Failure modes

- If JIRA MCP fails: skip JIRA section, mark "(JIRA unavailable)".
- If `gh` rate-limits: paginate or note "(GH rate-limited; rerun later)".
- If customer is a placeholder (`customer-6` through `customer-10` with `name: TBD`): prompt user to fill in `customers.yaml` first.

## Don't

- Don't aggregate across all customers in one call (one customer per invocation).
- Don't expose data from customers NOT in customers.yaml — that's an authorization signal.
- Don't run for a customer not in your work-history without a 180-day search confirming relevance.
