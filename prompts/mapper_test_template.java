/*
 * TEMPLATE — Mapper-layer test skeleton for a new e-invoicing country.
 *
 * Substitute placeholders before saving into einvoicing-core:
 *   {{COUNTRY_CODE_2}}        -> lowercase, e.g. "jo"
 *   {{COUNTRY_CODE_2_UPPER}}  -> uppercase, e.g. "JO"
 *   {{COUNTRY_NAME_PASCAL}}   -> e.g. "Jordan"
 *   {{PROVIDER_NAME}}         -> e.g. "JoFotara"
 *   {{PACKAGE}}               -> e.g. "com.clear.einvoicing.jo.mapper"
 *
 * Reference: ~/dev/personal-skills/prompts/country_onboarding_playbook.md Section C.
 *
 * Target test count: ~50 across these dimensions
 *   - 1 per sub-type code (Jordan: 8) → header / sub-type rendering
 *   - 1 per buyer ID scheme (TN/NIN/PN/None) → 4
 *   - 1 per tax category (S/Z/O[/E]) → 3-4
 *   - Doc-level + line-level discount combos → 4
 *   - Single-line + multi-line → 2
 *   - Credit note BillingReference + PaymentMeans → 4
 *   - Edge cases (empty notes, foreign currency, exports, etc.) → 10-15
 *   - Negative / null-leak guards (`="null"` and `>null<` absent) → 5-10
 *
 * The 5 representative test methods below cover header, supplier, customer,
 * totals, lines, edge case. Extend incrementally — every fixture/test pair
 * caught a real production bug during Jordan onboarding.
 */
package {{PACKAGE}};

import com.clear.einvoicing.{{COUNTRY_CODE_2}}.mapper.testsupport.LocalDateTimeSchemaMapping;
import com.clear.schema.registry.services.SchemaConverterService;
import com.clear.schema.registry.repositories.SchemaMappingRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Mapper-layer tests for {{COUNTRY_NAME_PASCAL}} ({{COUNTRY_CODE_2_UPPER}}) → {{PROVIDER_NAME}} XML schema mapping.
 * Asserts the schema-mapping JSON correctly transforms DB-shape JSON into the
 * UBL-shape JsonNode that the production XML renderer consumes.
 *
 * Pairs with {@link SalesTo{{PROVIDER_NAME}}EndToEndXmlTest} which runs the full
 * pipeline through the XML renderer (slower; this class is for fast feedback).
 */
class SalesTo{{PROVIDER_NAME}}MapperTest {

    private static final String SOURCE_SCHEMA = "EINVOICE_DB_TEMPLATE_SCHEMA_MY";
    private static final String DEST_SCHEMA = "EINVOICE_SALES_GOVT_SCHEMA";
    private static final String FIXTURES = "src/test/resources/{{COUNTRY_CODE_2}}/inputs/";

    private static SchemaConverterService converter;
    private static ObjectMapper objectMapper;

    @BeforeAll
    static void setUp() throws Exception {
        // Load mapping JSON via SchemaMappingRepository (production-shaped).
        // {{COUNTRY_CODE_2_UPPER}} mapping file lives at src/main/resources/SchemaMapping/{{COUNTRY_CODE_2_UPPER}}/SalesEinvoiceTo{{PROVIDER_NAME}}Xml.json
        // Tests load it via classpath; production loads via schema-registry hardcoded whitelist.
        SchemaMappingRepository repo = new SchemaMappingRepository();
        // TODO: wire mapping load — pattern from einvoice-ae's MapperTest
        converter = new SchemaConverterService(repo);
        objectMapper = new ObjectMapper();
    }

    @BeforeEach
    void registerCallableHelpers() {
        // CallableClass stub — production has copies in einvoicing-workflow-consumer + einvoice-my.
        // einvoice-{{COUNTRY_CODE_2}} test classpath needs its own at testsupport/.
        LocalDateTimeSchemaMapping.register();
    }

    private JsonNode convert(String fixtureName) throws IOException {
        Path fixture = Path.of(FIXTURES + fixtureName);
        JsonNode source = objectMapper.readTree(Files.readString(fixture));
        return converter.convertSchema(source, SOURCE_SCHEMA, DEST_SCHEMA);
    }

    // ===== Representative tests (5) =====

    @Test
    @DisplayName("Header — invoice 388 with sub-type carries ProfileID, ID, UUID, IssueDate, currency codes")
    void headerFields_minimalInvoice388() throws Exception {
        JsonNode result = convert("01_minimal-invoice-388.json");

        assertThat(result.at("/Invoice/ProfileID").asText()).isEqualTo("reporting:1.0");
        assertThat(result.at("/Invoice/ID").asText()).isNotBlank();
        assertThat(result.at("/Invoice/UUID").asText()).isNotBlank();
        assertThat(result.at("/Invoice/IssueDate").asText()).matches("\\d{4}-\\d{2}-\\d{2}");
        assertThat(result.at("/Invoice/InvoiceTypeCode/text").asText()).isEqualTo("388");
        assertThat(result.at("/Invoice/InvoiceTypeCode/_name").asText()).isNotBlank();
        assertThat(result.at("/Invoice/DocumentCurrencyCode").asText()).isNotBlank();
    }

    @Test
    @DisplayName("Supplier — country code converted from 3-letter DB enum to 2-letter UBL (B4)")
    void supplierCountryCode_3letterTo2letter() throws Exception {
        JsonNode result = convert("01_minimal-invoice-388.json");

        // B4: Even though DB has 3-letter (e.g. JOR), expression resolves to 2-letter (e.g. JO).
        String supplierCountry = result
                .at("/Invoice/AccountingSupplierParty/Party/PostalAddress/Country/IdentificationCode")
                .asText();
        assertThat(supplierCountry).hasSize(2);
    }

    @Test
    @DisplayName("Customer — PartyIdentification omitted when buyer is walk-in (skipIfEmpty cascade, B11)")
    void customerWalkin_partyIdentificationAbsent() throws Exception {
        JsonNode result = convert("03_customer-none-walkin.json");

        // B11: skipIfEmpty cascade. Walk-in fixture has no buyer ID — entire PartyIdentification block must be missing.
        assertThat(result.at("/Invoice/AccountingCustomerParty/Party/PartyIdentification/ID/text").isMissingNode())
                .isTrue();
        assertThat(result.at("/Invoice/AccountingCustomerParty/Party/PartyIdentification/ID/_schemeID").isMissingNode())
                .isTrue();
    }

    @Test
    @DisplayName("Totals — Money wrapper: TaxExclusive/TaxInclusive/Allowance/Payable read .value.value (B1)")
    void legalMonetaryTotals_moneyWrapper() throws Exception {
        JsonNode result = convert("02_credit-note-381-nin-buyer.json");

        // B1: amount.value.value (NOT amount.value).
        assertThat(result.at("/Invoice/LegalMonetaryTotal/TaxExclusiveAmount/text").asText()).isNotEmpty();
        assertThat(result.at("/Invoice/LegalMonetaryTotal/TaxExclusiveAmount/_currencyID").asText()).isNotEmpty();
        assertThat(result.at("/Invoice/LegalMonetaryTotal/TaxInclusiveAmount/text").asText()).isNotEmpty();
        assertThat(result.at("/Invoice/LegalMonetaryTotal/AllowanceTotalAmount/text").asText()).isNotEmpty();
        assertThat(result.at("/Invoice/LegalMonetaryTotal/PayableAmount/text").asText()).isNotEmpty();
    }

    @Test
    @DisplayName("Lines — line-level TaxTotal absent on no-VAT sub-type (3-flag pattern, B10)")
    void lines_noTaxTotalOnIncomeBill() throws Exception {
        // Fixture 07 = A/R Income Bill (sub-type 021) — no VAT, no TaxTotal expected.
        JsonNode result = convert("07_ar-invoice-388-subtype021.json");

        // B10: with skipIfSourceEmpty + pathResolutionMode RELATIVE, the line TaxTotal block must be absent.
        // If absent assertion fails, you forgot pathResolutionMode RELATIVE (default WITH_FALLBACK
        // walks up to root scope and silently injects doc-level taxTotal[0]).
        JsonNode firstLine = result.at("/Invoice/InvoiceLine/0");
        assertThat(firstLine.at("/TaxTotal").isMissingNode())
                .as("Line-level TaxTotal must be absent for no-VAT sub-types")
                .isTrue();
    }

    /*
     * ===== Remaining ~45 tests to fill =====
     *
     * Sub-type coverage (8):
     *   subType011_cashIncomeBill — no VAT, no PartyIdentification mandatory
     *   subType012_cashGeneralSales — VAT 16%, payment-means 10
     *   subType013_cashSpecialSales — VAT + OTH second subtotal, confirm consultant query
     *   subType021_arIncomeBill — payment-means 30, no VAT
     *   subType022_arGeneralSales — VAT, A/R buyer mandatory
     *   subType023_arSpecialSales — VAT + OTH, A/R
     *   subType111_exportCashIncomeBill — foreign customer country
     *   subType121_exportArIncomeBill — open: buyer name on exports?
     *
     * Buyer ID schemes (4):
     *   buyer_TN_taxNumber — emits @schemeID="TN" (UBL value), internal API enum is "TIN"
     *   buyer_NIN_nationalId — exactly 10 digits, emits @schemeID="NIN"
     *   buyer_PN_passport — alphanumeric >10 chars, emits @schemeID="PN"
     *   buyer_None_walkin — entire PartyIdentification missing (above)
     *
     * Tax category coverage (3-4):
     *   taxCategory_S_standard — Percent 16, TaxScheme VAT
     *   taxCategory_Z_zero — Percent 0, TaxScheme VAT
     *   taxCategory_O_exempt — no Percent, TaxScheme VAT
     *
     * Discount permutations (4):
     *   docLevelDiscount — AllowanceCharge ChargeIndicator=false at doc
     *   lineLevelDiscount — AllowanceCharge inside Price block
     *   bothDiscounts
     *   noDiscount — AllowanceCharge missing entirely
     *
     * Credit note flow (4):
     *   creditNote_BillingReference — InvoiceDocumentReference fields populated
     *   creditNote_PaymentMeansCode10 — listID="UN/ECE 4461"
     *   creditNote_InstructionNote — present and non-empty
     *   creditNote_AllAmountsMatchOriginal — DocumentDescription = original full amount
     *
     * TaxCategory attribute split (B9) — 4 assertions:
     *   taxCategory_id_text — value
     *   taxCategory_id_schemeAgencyID — "6"
     *   taxCategory_id_schemeID — "UN/ECE 5305"
     *   taxCategory_taxScheme_id_schemeID — "UN/ECE 5153"
     *
     * Signature stub (B7) — 2 assertions:
     *   signature_id_isInvoiceUrn
     *   signature_method_isXadesUrn
     *
     * ICV AdditionalDocumentReference (B5, B14):
     *   icv_id_isLiteralICV
     *   icv_uuid_fallsBackToInvoiceIdEn
     *
     * Null-leak guards (5+):
     *   noNullLeak_inSerializedJson — assert "null" not in resulting JsonNode toString
     *   noEmptyTagLeak_PaymentMeans — fixture without payment means: PaymentMeans block missing
     *   noEmptyTagLeak_TaxTotal — same for line-level TaxTotal in no-VAT scenarios (above)
     *   noEmptyTagLeak_AllowanceCharge — same for AllowanceCharge in no-discount scenarios
     *   noEmptyTagLeak_PartyIdentification — same for walk-in
     *
     * Each test follows the same shape:
     *   1. convert(fixtureName)
     *   2. assertThat(result.at("/Invoice/...")).hasFieldOrPropertyWithValue(...)
     *      OR assertThat(result.at("/Invoice/...").isMissingNode()).isTrue();
     */
}
