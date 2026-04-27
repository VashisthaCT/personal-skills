---
name: v-law-watch
description: Monthly best-effort scrape of country regulator portals + invoicenavigator newsletter for e-invoicing regulatory changes. Diffs against the last entry timestamp in each `runbooks/.../law_changes.md`, appends new dated items, and drafts a per-scope summary to self-DM `D088362AS65`. Triggered by `/v-law-watch <scope>` where `<scope>` is `all`, a country key (`jordan`, `india`, `ksa`, `uae`, `malaysia`, `belgium`, `france`, `poland`), or `peppol`. Optional `--since YYYY-MM-DD` overrides the last-entry watermark.
---

You are running a monthly law-watch for Vashistha's e-invoicing portfolio. Output is **drafts only** — appends to `law_changes.md` and a self-DM draft. The user reviews and triages the `Impact` field manually.

## Inputs

- `<scope>` — `all` OR a country/region key (e.g. `jordan`, `india`, `peppol`).
- `--since YYYY-MM-DD` — optional. If omitted, use the top-most `## YYYY-MM-DD` heading in each entry's `law_changes.md` as the watermark. If the file has no dated entry, use 60 days ago.

## Step 1 — Resolve scope

1. Read `~/dev/personal-skills/data/countries.yaml` and `~/dev/personal-skills/data/law_feeds.yaml`.
2. If `<scope> == all`: every entry under `countries:` with `seed: rich` (currently jordan, india, uae) plus `peppol` from `regions:`. **Always include the global `invoicenavigator` feed** as a single extra fetch — it covers EU + ROW.
3. Else: just the one entry. If unknown, list valid keys and stop.

## Step 2 — Per-entry fetch and diff

For each entry in scope:

a. **Find the last-entry timestamp.** Read its `runbooks/countries/<cc>/law_changes.md` (or `runbooks/regions/<name>/spec_changes.md` for peppol). Top-most `## YYYY-MM-DD` heading is the watermark. If `--since` was passed, that overrides.

b. **Resolve feeds.** Look up the entry in `~/dev/personal-skills/data/law_feeds.yaml` under `feeds.<key>`. Each entry has 1-3 named URLs.

c. **Fetch each feed.** Use `WebFetch` with a prompt like *"List items, news, or circulars on this page with their date and title; ignore navigation and footer."* Most regulator portals are in the user's sandbox-allowedHosts list (zatca.gov.sa, jofotara.gov.jo, ewaybillgst.gov.in, docs.peppol.eu, www.invoicenavigator.eu, etc.) so it should work without `dangerouslyDisableSandbox`. If a feed 404s, times out, or returns "Operation not permitted", **skip it and log the error — do NOT crash**. If the failure looks sandbox-related, retry once with `dangerouslyDisableSandbox: true`.

d. **Extract candidate items.** For each item the page returns: title, date (best-effort parse), URL, 1-3 line summary. Drop anything older than the watermark. Drop items without a parseable date (we re-find them on the next run).

e. **Apply the e-invoicing keyword filter** (case-insensitive, ANY match keeps the item):
   - e-invoicing, e-invoice, einvoice, einvoicing
   - invoice, facture, fatura, fatoora, فاتورة
   - VAT, GST, tax invoice
   - regulator names: ZATCA, FTA, ETA, ISTD, NIC, GSTN, LHDN, KSeF, PPF, JoFotara, MyInvois, Peppol
   - compliance, mandate, phase, go-live, rollout
   - credit note, debit note
   - UBL, PINT, SBDH, clearance
   
   Skip generic press releases, anniversaries, leadership changes, and unrelated tax-policy news. When in doubt, **include** — user prefers false positives over false negatives.

f. **Append each kept item** to the law_changes file using append-only format. Insert at the top (newest first), above any existing `---` divider. If the same date already has an entry with the same title, skip to avoid dupes.

   ```markdown
   ## YYYY-MM-DD — <Title>

   **Source:** <URL>
   **Summary:** <1-3 lines from the page>
   **Impact:** TBD — to be triaged by user
   ```

g. **Best-effort update** of `data/countries.yaml`: if the entry has a `last_law_check:` field, update it to today's date (`YYYY-MM-DD`). If absent, **do not add it** — leave the file's shape alone.

## Step 3 — Global feed (invoicenavigator)

Fetch `https://www.invoicenavigator.eu/` (or the value of `feeds.global.invoicenavigator` from the YAML). Apply the same keyword filter. For each kept item, decide which entry's `law_changes.md` it belongs in by matching country tags in the title/summary (e.g. "Belgium VAT 2026" → `runbooks/countries/belgium/law_changes.md`). If no clear country match, append to `runbooks/regions/peppol/spec_changes.md` with a `**Cross-reference:** <country>` note. If still ambiguous, drop it (user picks up the next run with more context).

This step is part of every `<scope> == all` run and is **skipped** for scoped runs (e.g. `/v-law-watch jordan` does NOT fetch invoicenavigator — it stays focused).

## Step 4 — Compose summary draft

Use `slack_send_message_draft` to channel `D088362AS65` (self-DM). Format:

```
Law watch — <scope> — <today YYYY-MM-DD>

<N> new entries across <K> countries:
- [<cc>] <count> updates — top: <title> — <link>
- ...

Sources polled: <comma-separated list of feed URLs successfully fetched>
Errors: <count> (skipped feeds: <list with 1-line reason>)
```

If `N == 0`, draft anyway with "No new entries since <watermark>" — the user wants confirmation the cron ran.

## Sandbox notes

- `WebFetch` is sandboxed by default. The user's allowedHosts already includes zatca.gov.sa, jofotara.gov.jo, ewaybillgst.gov.in, docs.peppol.eu, www.invoicenavigator.eu, datypic.com, www.galaxygw.com — these work without elevation.
- For other hosts in `law_feeds.yaml` (tax.gov.ae, hasil.gov.my, finance.belgium.be, podatki.gov.pl, peppol.org, gst.gov.in, taxinformation.cbic.gov.in, economie.gouv.fr): try sandboxed first; on "Operation not permitted" or DNS failure, retry once with `dangerouslyDisableSandbox: true`.
- Never elevate the sandbox preemptively — try the safe path first per `/sandbox` policy.

## Verifiable success criteria

- For `/v-law-watch <single>`: at least one feed fetched (or every feed errored with logged reason); zero or more append blocks added to its single `law_changes.md`; one draft to `D088362AS65`.
- For `/v-law-watch all`: every `seed: rich` entry attempted + invoicenavigator + peppol; per-entry append blocks; one summary draft.
- `data/countries.yaml` not corrupted (only `last_law_check` field touched if present).
- Every appended block has all 4 fields (heading, Source, Summary, Impact).
- Impact is always literal `TBD — to be triaged by user`. Never fabricate compliance interpretation.

## Don't

- Don't claim regulatory expertise. Every new entry's Impact line is `TBD — to be triaged by user`.
- Don't auto-send the Slack message. `slack_send_message_draft` only.
- Don't rewrite or edit existing entries in `law_changes.md`. Append-only.
- Don't crash on a single feed failure. Log it, continue.
- Don't fetch the same feed twice in one run.
- Don't add new fields to `countries.yaml` schema. Only update `last_law_check` if the field already exists.
- Don't run for entries with `seed: stub` under `<scope> == all` — they don't have a runbook to append to.
