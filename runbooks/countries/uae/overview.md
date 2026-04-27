# UAE (AE) — FTA E-Invoicing

**Code:** AE | **Region:** MEA | **Status:** Live (Tabby B2B/B2C live Dec 16 2025; MEA re-routing live Mar 26 2026)
**Regulator:** FTA (UAE Federal Tax Authority)
**Repos:** `einvoicing-core/einvoice-ae`, `clear-routing/clear-ae-fta`, `einvoicing-integrations`, `pdfgenerator`, `clear-peppol-ap`

## What UAE is

UAE operates an FTA-mandated e-invoicing scheme, integrated via Peppol-style 4-corner architecture. ClearTax handles both B2B and B2C flows (B2C added with the Tabby launch Dec 2025). The regulator is the UAE FTA; routing goes through `clear-ae-fta` vendor module.

## Architecture footprint

- **`einvoicing-core/einvoice-ae`** — country module. Validation rules: BuyerValidationRules, SellerValidationRules, TaxTotalsValidationRules, DocumentTotalsValidationRules, LineItemValidationRules, HeaderValidationRules, AllowanceChargeValidationRules, PaymentValidationRules, CreditNoteValidationRules. ValidationContext + ValidationError + ValidationRule interface.
- **`clear-routing/clear-ae-fta`** — vendor module. Dual OAuth2 (Redis-cached). Actions: `GET_TAXPAYER_DETAILS`, `SUBMIT_TAXPAYER_DETAILS`.
- **`einvoicing-integrations`** — UAE integration upload endpoint (PR #493).
- **`pdfgenerator`** — Arabic translation service handles MEA-wide Arabic strings; UAE templates 5/6/8/9 routed through Kramer.

## Key recent work (FY26 H2)

- **Tabby UAE B2B/B2C — new product line** (no JIRA — feature track; einvoicing-core#888, clear-sales#342) — 49 files, 9 validation rule classes, 92.77% coverage, **live Dec 16, 2025**.
- **NV-173 MEA Re-routing** (P0) + 11-PR post-launch sweep — einvoicing-core#1167, cloud-init#6662, ct-app-config#8098, clear-peppol-ap#165, plus #1258/#1254/#1072/#1099/#1069/#1026/#1033/#1003/#1047, e-invoicing-be#3716/#3714. **Live Mar 26, 2026**.
- **Arabic translation service for UAE** (einvoicing-core#941) — 25 review comments. Cross-service design Jan 12, deploy Jan 19. pdfgenerator#461 + Kramer templates 5/6/8/9 + MEA QA.
- **AE UBL TaxCategory ordering fix + 18-test regression guard** (einvoicing-core#1282).
- **UAE integration upload endpoint** (einvoicing-integrations#493).

## Slack & people

- **L3 channel:** `#einvoice_mea_l3_support` (`C0AB8EAH9A6`).
- **Global platform:** `#einvoicing_global_platform` (`C08MX0F3F17`).
- **Global PR:** `#einvoicing_global_pr` (`C09TU9UMJJ2`).
- **Tech internal:** `#e-invoice-tech-internal` (`C09AC9XKTC5`).
- **Cross MEA:** `#einvoice_india_mea` (`C0ADWHJ2V9S`).

## Status today (Apr 2026)

- Live; mature.
- Tabby B2B/B2C in production Dec 16 2025.
- MEA re-routing live Mar 26 2026 (Vashistha-owned P0 cross-country shift).
- Translation service for Arabic strings live cross-service.
- Validation rules pattern (9 classes in `einvoice-ae`) is the reference for new MEA modules. Jordan currently has zero validation rule classes — pattern to replicate.

## Reference notes

- **Customer:** Tabby — first major B2C customer in UAE; kickoff Dec 2 2025 questions-before-code thread: https://cleartaxtech.slack.com/archives/C08MX0F3F17/p1764661242981169
- **Tax authority country mapping** (used by Peppol TDD, see `regions/peppol/specs.md`): UAE = `AE`.

Sources: `project_perf_review_fy26.md` §4 H2 picks 1-2, 7, 10; `platform_architecture.md` §1, §3.
