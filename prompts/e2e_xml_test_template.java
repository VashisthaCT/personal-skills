/*
 * TEMPLATE — End-to-end XML test skeleton for a new e-invoicing country.
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
 * Target test count: ~93 across these dimensions
 *   - 9 fixtures × ~10 XPath assertions each = ~90 base tests
 *   - + absence-assertion guards (B10) for skipped blocks: ~5
 *   - + namespace correctness on prefixed elements (cac:/cbc:/ext:): ~3
 *
 * The 5 representative test methods below cover full pipeline + XPath.
 * Pattern is copy-paste-able across countries — same harness with no @SpringBootTest.
 */
package {{PACKAGE}};

import com.clear.einvoicing.{{COUNTRY_CODE_2}}.mapper.testsupport.LocalDateTimeSchemaMapping;
import com.clear.validation.services.processor.JsonValidationProcessor;
import com.clear.validation.utils.XmlNamespaceConfigRegistry;
import com.clear.schema.registry.services.SchemaConverterService;
import com.clear.schema.registry.repositories.SchemaMappingRepository;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.slf4j.MDC;
import org.xmlunit.assertj3.XmlAssert;

import java.io.IOException;
import java.lang.reflect.Field;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Map;
import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * End-to-end XML tests for {{COUNTRY_NAME_PASCAL}} ({{COUNTRY_CODE_2_UPPER}}).
 * Pipeline: JSON fixture → schema-mapping → JsonValidationProcessor.preProcessor → real UBL XML
 * → XPath assertions via XMLUnit assertj3.
 *
 * Pairs with {@link SalesTo{{PROVIDER_NAME}}MapperTest} which only asserts the intermediate JsonNode.
 *
 * Test harness notes:
 *   - No @SpringBootTest. We instantiate JsonValidationProcessor directly and reflection-inject
 *     XmlNamespaceConfigRegistry pointing at our local clean copy of xml-namespace-configs.json
 *     (the library-shipped copy has _comment fields its own Jackson rejects).
 *   - schemaRegistryService is left null (unused on the JSON-input path).
 *   - LocalDateTimeSchemaMapping CallableClass is registered manually since einvoice-{{COUNTRY_CODE_2}}
 *     doesn't depend on einvoicing-workflow-consumer or einvoice-my (which both ship copies).
 */
class SalesTo{{PROVIDER_NAME}}EndToEndXmlTest {

    private static final String SOURCE_SCHEMA = "EINVOICE_DB_TEMPLATE_SCHEMA_MY";
    private static final String DEST_SCHEMA = "EINVOICE_SALES_GOVT_SCHEMA";
    private static final String FIXTURES = "src/test/resources/{{COUNTRY_CODE_2}}/inputs/";
    private static final String NS_CONFIG_PATH = "{{COUNTRY_CODE_2}}/xml-namespace-configs.json";

    private static final Map<String, String> UBL_NAMESPACES = Map.of(
            "inv", "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
            "cbc", "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
            "cac", "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
            "ext", "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
    );

    private static SchemaConverterService converter;
    private static JsonValidationProcessor jsonValidationProcessor;
    private static ObjectMapper objectMapper;

    @BeforeAll
    static void setUp() throws Exception {
        SchemaMappingRepository repo = new SchemaMappingRepository();
        // TODO: wire mapping load — pattern from einvoice-ae's E2E test
        converter = new SchemaConverterService(repo);
        objectMapper = new ObjectMapper();

        // Real production JsonValidationProcessor with reflection-injected namespace registry.
        jsonValidationProcessor = new JsonValidationProcessor(/* schemaRegistryService */ null);
        Field nsField = JsonValidationProcessor.class.getDeclaredField("nsConfigRegistry");
        nsField.setAccessible(true);
        nsField.set(jsonValidationProcessor, new XmlNamespaceConfigRegistry(NS_CONFIG_PATH));
    }

    @BeforeEach
    void registerCallableHelpers() {
        LocalDateTimeSchemaMapping.register();
    }

    @AfterEach
    void clearMdc() {
        // B17: MDC is thread-local; tests can leak state.
        MDC.clear();
    }

    private String renderXml(String fixtureName) throws IOException {
        Path fixture = Path.of(FIXTURES + fixtureName);
        JsonNode source = objectMapper.readTree(Files.readString(fixture));
        JsonNode mapped = converter.convertSchema(source, SOURCE_SCHEMA, DEST_SCHEMA);
        // preProcessor returns Base64 of the rendered XML (production pattern).
        String base64 = jsonValidationProcessor.preProcessor(mapped);
        return new String(Base64.getDecoder().decode(base64));
    }

    // ===== Representative tests (5) =====

    @Test
    @DisplayName("E2E — minimal invoice 388 renders valid UBL with all mandatory header XPaths")
    void minimalInvoice388_xmlRendersAllHeaderXpaths() throws Exception {
        String xml = renderXml("01_minimal-invoice-388.json");

        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("/inv:Invoice/cbc:ProfileID")
                .isEqualTo("reporting:1.0");
        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("/inv:Invoice/cbc:InvoiceTypeCode/text()")
                .isEqualTo("388");
        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("/inv:Invoice/cbc:InvoiceTypeCode/@name")
                .isEqualTo("012");
    }

    @Test
    @DisplayName("E2E — country code emitted as 2-letter (B4): supplier + customer IdentificationCode")
    void countryCode_2letter_supplierAndCustomer() throws Exception {
        String xml = renderXml("01_minimal-invoice-388.json");

        // B4: even though DB has 3-letter (e.g. JOR), expression resolves to 2-letter.
        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("/inv:Invoice/cac:AccountingSupplierParty/cac:Party/cac:PostalAddress/cac:Country/cbc:IdentificationCode")
                .matches("[A-Z]{2}");
    }

    @Test
    @DisplayName("E2E — TaxCategory + TaxScheme attribute split (B9): schemeAgencyID + schemeID")
    void taxCategoryAttributes_splitWithSchemeAgencyAndSchemeID() throws Exception {
        String xml = renderXml("02_credit-note-381-nin-buyer.json");

        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("(//cac:TaxCategory/cbc:ID)[1]/@schemeAgencyID")
                .isEqualTo("6");
        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("(//cac:TaxCategory/cbc:ID)[1]/@schemeID")
                .isEqualTo("UN/ECE 5305");
        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .valueByXPath("(//cac:TaxCategory/cac:TaxScheme/cbc:ID)[1]/@schemeID")
                .isEqualTo("UN/ECE 5153");
    }

    @Test
    @DisplayName("E2E — absence assertion: no PaymentMeans block on cash sub-type (3-flag pattern, B10)")
    void noPaymentMeansBlock_onCashIncomeBill() throws Exception {
        // B10 regression guard. Without skipIfSourceEmpty+RELATIVE, an empty <cbc:PaymentMeans/>
        // would emit and the regulator would reject. Caught only by absence assertion.
        String xml = renderXml("08_cash-invoice-388-subtype011-multiline.json");

        XmlAssert.assertThat(xml)
                .withNamespaceContext(UBL_NAMESPACES)
                .nodesByXPath("/inv:Invoice/cac:PaymentMeans")
                .doNotExist();
    }

    @Test
    @DisplayName("E2E — no-null-leaks sanity: every fixture renders without `=\"null\"` or `>null<`")
    void noNullLeaks_acrossAllFixtures() throws Exception {
        // Regression trap for missing skipIfEmpty (B11). Run all 9 fixtures; assert the rendered
        // XML never contains a null literal.
        for (int i = 1; i <= 9; i++) {
            String fixtureName = String.format("%02d_*.json", i);
            // Use Files.list + filter to find the fixture by prefix (each has a descriptive suffix).
            Path fixturesDir = Path.of(FIXTURES);
            Path fixture = Files.list(fixturesDir)
                    .filter(p -> p.getFileName().toString().startsWith(String.format("%02d_", i)))
                    .findFirst()
                    .orElseThrow();
            String xml = renderXml(fixture.getFileName().toString());

            assertThat(xml).as("Fixture %02d must not contain null literals", i)
                    .doesNotContain("=\"null\"")
                    .doesNotContain(">null<");
        }
    }

    /*
     * ===== Remaining ~88 tests to fill =====
     *
     * 9 fixtures × ~10 assertions each ≈ 90 tests.
     *
     * Per-fixture XPath checklist:
     *   - /inv:Invoice/cbc:ID
     *   - /inv:Invoice/cbc:UUID
     *   - /inv:Invoice/cbc:IssueDate (matches YYYY-MM-DD)
     *   - /inv:Invoice/cbc:InvoiceTypeCode + @name (sub-type)
     *   - /inv:Invoice/cbc:DocumentCurrencyCode (3-letter)
     *   - /inv:Invoice/cac:AdditionalDocumentReference[cbc:ID="ICV"]/cbc:UUID = invoice document number
     *   - Signature block presence (B7) — both URNs match expected literals
     *   - Supplier: PostalAddress/Country/IdentificationCode (2-letter), TIN, RegistrationName, ISS
     *   - Customer: depending on scenario — PartyIdentification @schemeID, RegistrationName presence/absence
     *   - LegalMonetaryTotal: 4 amounts non-empty, currencyID matches (2-letter on amount-element)
     *   - InvoiceLine: cbc:ID, cbc:InvoicedQuantity + @unitCode, cbc:LineExtensionAmount, Item/Name, Price/PriceAmount
     *
     * Per-scenario absence checklist (B10 regression guards):
     *   - Walk-in fixture: /cac:AccountingCustomerParty//cac:PartyIdentification doesNotExist
     *   - No-discount fixtures: /cac:AllowanceCharge doesNotExist
     *   - Cash sub-types (011, 111): /cac:PaymentMeans doesNotExist
     *   - Income Bill sub-types (011, 021, 111, 121): /cac:TaxTotal doesNotExist (doc + line)
     *   - Standard 388 (not credit note): /cac:BillingReference doesNotExist
     *
     * Negative tests for known-rejected XML (regulator validator rules, captured from mock):
     *   - PROFILE_ID_INVALID — wrong ProfileID rejected
     *   - INVOICE_TYPE_INVALID — type other than 388/381 rejected
     *   - INVOICE_LINE_MISSING — line without InvoicedQuantity/Price/PriceAmount rejected
     *   - CHARGE_INDICATOR_INVALID — ChargeIndicator other than "false" rejected
     *
     * Each follows:
     *   String xml = renderXml("XX_<scenario>.json");
     *   XmlAssert.assertThat(xml)
     *       .withNamespaceContext(UBL_NAMESPACES)
     *       .valueByXPath("/inv:Invoice/...")
     *       .isEqualTo("expected");
     *
     * For absence:
     *   XmlAssert.assertThat(xml)
     *       .withNamespaceContext(UBL_NAMESPACES)
     *       .nodesByXPath("/inv:Invoice/cac:...")
     *       .doNotExist();
     */
}
