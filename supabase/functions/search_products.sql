-- Full-text search function for products with score data
CREATE OR REPLACE FUNCTION search_products(
    query TEXT,
    result_limit INTEGER DEFAULT 20,
    result_offset INTEGER DEFAULT 0,
    category_filter TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    brand TEXT,
    category VARCHAR(100),
    image_url TEXT,
    overall_score NUMERIC,
    grade CHAR(1),
    rank REAL
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id,
        p.name,
        p.brand,
        p.category,
        p.image_url,
        ps.overall_score,
        ps.grade,
        ts_rank(p.search_vector, websearch_to_tsquery('english', query)) AS rank
    FROM products p
    LEFT JOIN product_scores ps ON ps.product_id = p.id
    WHERE p.search_vector @@ websearch_to_tsquery('english', query)
        AND (category_filter IS NULL OR p.category = category_filter)
    ORDER BY rank DESC
    LIMIT result_limit
    OFFSET result_offset;
END;
$$ LANGUAGE plpgsql STABLE;

-- Search chemicals by name (with fuzzy matching fallback)
CREATE OR REPLACE FUNCTION search_chemicals(
    query TEXT,
    result_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    id UUID,
    preferred_name TEXT,
    inci_name TEXT,
    cas_number VARCHAR(20),
    rank REAL
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        c.id,
        c.preferred_name,
        c.inci_name,
        c.cas_number,
        ts_rank(c.search_vector, websearch_to_tsquery('english', query)) AS rank
    FROM chemicals c
    WHERE c.search_vector @@ websearch_to_tsquery('english', query)
    ORDER BY rank DESC
    LIMIT result_limit;
END;
$$ LANGUAGE plpgsql STABLE;
