-- ToxScore Initial Schema
-- Chemical Knowledge Graph + Products + Scores + Search

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- ============================================================================
-- CHEMICALS: Core of the Knowledge Graph
-- ============================================================================

CREATE TABLE chemicals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    dtxsid VARCHAR(20) UNIQUE,
    cas_number VARCHAR(20),
    preferred_name TEXT NOT NULL,
    inci_name TEXT,
    molecular_formula TEXT,
    molecular_weight NUMERIC(12, 4),
    smiles TEXT,
    description TEXT,
    hazard_data JSONB DEFAULT '{}',
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(preferred_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(inci_name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(cas_number, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'C')
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_chemicals_search ON chemicals USING GIN (search_vector);
CREATE INDEX idx_chemicals_cas ON chemicals (cas_number);
CREATE INDEX idx_chemicals_inci ON chemicals (inci_name);
CREATE INDEX idx_chemicals_dtxsid ON chemicals (dtxsid);
CREATE INDEX idx_chemicals_name_trgm ON chemicals USING GIN (preferred_name gin_trgm_ops);

-- ============================================================================
-- CHEMICAL SYNONYMS: Many names map to one chemical
-- ============================================================================

CREATE TABLE chemical_synonyms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chemical_id UUID REFERENCES chemicals (id) ON DELETE CASCADE,
    synonym TEXT NOT NULL,
    source VARCHAR(50),
    UNIQUE (chemical_id, synonym)
);

CREATE INDEX idx_synonyms_name ON chemical_synonyms (lower(synonym));
CREATE INDEX idx_synonyms_trgm ON chemical_synonyms USING GIN (synonym gin_trgm_ops);

-- ============================================================================
-- REGULATORY LISTS: Government and industry safety classifications
-- ============================================================================

CREATE TABLE regulatory_lists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    full_name TEXT,
    authority TEXT,
    url TEXT,
    last_updated DATE
);

CREATE TABLE chemical_regulatory_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chemical_id UUID REFERENCES chemicals (id) ON DELETE CASCADE,
    list_id UUID REFERENCES regulatory_lists (id) ON DELETE CASCADE,
    status VARCHAR(50),
    classification VARCHAR(100),
    details JSONB DEFAULT '{}',
    effective_date DATE,
    source_url TEXT,
    UNIQUE (chemical_id, list_id)
);

CREATE INDEX idx_crs_chemical ON chemical_regulatory_status (chemical_id);
CREATE INDEX idx_crs_list ON chemical_regulatory_status (list_id);

-- ============================================================================
-- PRODUCTS: Consumer products with ingredient lists
-- ============================================================================

CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    barcode VARCHAR(50) UNIQUE,
    name TEXT NOT NULL,
    brand TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    image_url TEXT,
    source VARCHAR(50) DEFAULT 'open_beauty_facts',
    source_id TEXT,
    raw_ingredients TEXT,
    metadata JSONB DEFAULT '{}',
    search_vector tsvector GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(name, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(brand, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(category, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(raw_ingredients, '')), 'C')
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_products_search ON products USING GIN (search_vector);
CREATE INDEX idx_products_barcode ON products (barcode);
CREATE INDEX idx_products_category ON products (category);
CREATE INDEX idx_products_brand ON products (brand);

-- ============================================================================
-- PRODUCT INGREDIENTS: Junction table linking products to chemicals
-- ============================================================================

CREATE TABLE product_ingredients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products (id) ON DELETE CASCADE,
    chemical_id UUID REFERENCES chemicals (id) ON DELETE SET NULL,
    raw_name TEXT NOT NULL,
    resolved_name TEXT,
    position INTEGER,
    confidence NUMERIC(3, 2) DEFAULT 1.0,
    UNIQUE (product_id, raw_name)
);

CREATE INDEX idx_pi_product ON product_ingredients (product_id);
CREATE INDEX idx_pi_chemical ON product_ingredients (chemical_id);

-- ============================================================================
-- PRODUCT SCORES: Pre-computed deterministic scores
-- ============================================================================

CREATE TABLE product_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products (id) ON DELETE CASCADE UNIQUE,
    overall_score NUMERIC(4, 1) NOT NULL,
    hazard_score NUMERIC(4, 1) NOT NULL,
    exposure_score NUMERIC(4, 1) NOT NULL,
    transparency_score NUMERIC(4, 1) NOT NULL,
    grade CHAR(1) NOT NULL,
    scoring_version VARCHAR(10) NOT NULL,
    score_details JSONB DEFAULT '{}',
    computed_at TIMESTAMPTZ DEFAULT now(),
    CONSTRAINT valid_grade CHECK (grade IN ('A', 'B', 'C', 'D', 'F')),
    CONSTRAINT valid_overall CHECK (overall_score >= 0 AND overall_score <= 100),
    CONSTRAINT valid_hazard CHECK (hazard_score >= 0 AND hazard_score <= 100),
    CONSTRAINT valid_exposure CHECK (exposure_score >= 0 AND exposure_score <= 100),
    CONSTRAINT valid_transparency CHECK (transparency_score >= 0 AND transparency_score <= 100)
);

CREATE INDEX idx_ps_grade ON product_scores (grade);
CREATE INDEX idx_ps_overall ON product_scores (overall_score);

-- ============================================================================
-- NAME MAPPINGS: INCI name resolution cache
-- ============================================================================

CREATE TABLE name_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    raw_name TEXT NOT NULL,
    normalized_name TEXT,
    chemical_id UUID REFERENCES chemicals (id),
    resolution_method VARCHAR(50),
    confidence NUMERIC(3, 2) DEFAULT 1.0,
    verified BOOLEAN DEFAULT false,
    UNIQUE (raw_name)
);

CREATE INDEX idx_nm_raw ON name_mappings (lower(raw_name));
CREATE INDEX idx_nm_normalized ON name_mappings (lower(normalized_name));

-- ============================================================================
-- AI EXPLANATIONS: Cached Claude-generated explanations
-- ============================================================================

CREATE TABLE ai_explanations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(20) NOT NULL,
    entity_id UUID NOT NULL,
    explanation_type VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    model_version VARCHAR(50),
    prompt_version VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE (entity_type, entity_id, explanation_type)
);

CREATE INDEX idx_ae_entity ON ai_explanations (entity_type, entity_id);

-- ============================================================================
-- UPDATED_AT TRIGGER: Auto-update timestamps
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chemicals_updated_at
    BEFORE UPDATE ON chemicals
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
