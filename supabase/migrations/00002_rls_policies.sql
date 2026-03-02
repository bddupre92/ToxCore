-- Row-Level Security Policies
-- Public reads, service-role writes for all tables

-- ============================================================================
-- CHEMICALS
-- ============================================================================
ALTER TABLE chemicals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "chemicals_public_read"
    ON chemicals FOR SELECT
    USING (true);

CREATE POLICY "chemicals_service_write"
    ON chemicals FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

CREATE POLICY "chemicals_service_update"
    ON chemicals FOR UPDATE
    USING (current_setting('role') = 'service_role');

-- ============================================================================
-- CHEMICAL SYNONYMS
-- ============================================================================
ALTER TABLE chemical_synonyms ENABLE ROW LEVEL SECURITY;

CREATE POLICY "synonyms_public_read"
    ON chemical_synonyms FOR SELECT
    USING (true);

CREATE POLICY "synonyms_service_write"
    ON chemical_synonyms FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

-- ============================================================================
-- REGULATORY LISTS
-- ============================================================================
ALTER TABLE regulatory_lists ENABLE ROW LEVEL SECURITY;

CREATE POLICY "reg_lists_public_read"
    ON regulatory_lists FOR SELECT
    USING (true);

CREATE POLICY "reg_lists_service_write"
    ON regulatory_lists FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

-- ============================================================================
-- CHEMICAL REGULATORY STATUS
-- ============================================================================
ALTER TABLE chemical_regulatory_status ENABLE ROW LEVEL SECURITY;

CREATE POLICY "crs_public_read"
    ON chemical_regulatory_status FOR SELECT
    USING (true);

CREATE POLICY "crs_service_write"
    ON chemical_regulatory_status FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

-- ============================================================================
-- PRODUCTS
-- ============================================================================
ALTER TABLE products ENABLE ROW LEVEL SECURITY;

CREATE POLICY "products_public_read"
    ON products FOR SELECT
    USING (true);

CREATE POLICY "products_service_write"
    ON products FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

CREATE POLICY "products_service_update"
    ON products FOR UPDATE
    USING (current_setting('role') = 'service_role');

-- ============================================================================
-- PRODUCT INGREDIENTS
-- ============================================================================
ALTER TABLE product_ingredients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "pi_public_read"
    ON product_ingredients FOR SELECT
    USING (true);

CREATE POLICY "pi_service_write"
    ON product_ingredients FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

-- ============================================================================
-- PRODUCT SCORES
-- ============================================================================
ALTER TABLE product_scores ENABLE ROW LEVEL SECURITY;

CREATE POLICY "scores_public_read"
    ON product_scores FOR SELECT
    USING (true);

CREATE POLICY "scores_service_write"
    ON product_scores FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

CREATE POLICY "scores_service_update"
    ON product_scores FOR UPDATE
    USING (current_setting('role') = 'service_role');

-- ============================================================================
-- NAME MAPPINGS
-- ============================================================================
ALTER TABLE name_mappings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "nm_public_read"
    ON name_mappings FOR SELECT
    USING (true);

CREATE POLICY "nm_service_write"
    ON name_mappings FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');

-- ============================================================================
-- AI EXPLANATIONS
-- ============================================================================
ALTER TABLE ai_explanations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ae_public_read"
    ON ai_explanations FOR SELECT
    USING (true);

CREATE POLICY "ae_service_write"
    ON ai_explanations FOR INSERT
    WITH CHECK (current_setting('role') = 'service_role');
