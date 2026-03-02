-- Seed test chemicals for development/testing
INSERT INTO chemicals (preferred_name, cas_number, inci_name, dtxsid, hazard_data) VALUES
    ('Sodium Lauryl Sulfate', '151-21-3', 'SODIUM LAURYL SULFATE', 'DTXSID4026062', '{"irritant": true, "sensitizer": false}'),
    ('Sodium Fluoride', '7681-49-4', 'SODIUM FLUORIDE', 'DTXSID1020603', '{"acute_toxicity": "moderate"}'),
    ('Triclosan', '3380-34-5', 'TRICLOSAN', 'DTXSID7020875', '{"endocrine_disruptor": true, "bioaccumulative": true}'),
    ('Bisphenol A', '80-05-7', 'BISPHENOL A', 'DTXSID7020182', '{"endocrine_disruptor": true, "reproductive_toxicant": true}'),
    ('Titanium Dioxide', '13463-67-7', 'TITANIUM DIOXIDE', 'DTXSID3021344', '{"iarc_group": "2B"}'),
    ('Water', '7732-18-5', 'AQUA', 'DTXSID7021383', '{}'),
    ('Glycerin', '56-81-5', 'GLYCERIN', 'DTXSID0020662', '{}'),
    ('Cetyl Alcohol', '36653-82-4', 'CETYL ALCOHOL', 'DTXSID8025148', '{}'),
    ('Fragrance', NULL, 'PARFUM', NULL, '{"transparency_concern": true, "undisclosed_mixture": true}'),
    ('Formaldehyde', '50-00-0', 'FORMALDEHYDE', 'DTXSID7020637', '{"iarc_group": "1", "carcinogen": true}')
ON CONFLICT DO NOTHING;

-- Seed test products
INSERT INTO products (name, brand, category, raw_ingredients, barcode) VALUES
    ('Test Toothpaste', 'TestBrand', 'toothpaste',
     'AQUA, SORBITOL, HYDRATED SILICA, SODIUM LAURYL SULFATE, SODIUM FLUORIDE, AROMA, CELLULOSE GUM, SODIUM SACCHARIN, CI 77891',
     '0000000000001'),
    ('Test Shampoo', 'TestBrand', 'shampoo',
     'AQUA, SODIUM LAURYL SULFATE, COCAMIDOPROPYL BETAINE, GLYCERIN, SODIUM CHLORIDE, PARFUM, CITRIC ACID',
     '0000000000002'),
    ('Test Moisturizer', 'TestBrand', 'moisturizer',
     'AQUA, GLYCERIN, CETYL ALCOHOL, CAPRYLIC/CAPRIC TRIGLYCERIDE, DIMETHICONE, TOCOPHERYL ACETATE, PARFUM',
     '0000000000003')
ON CONFLICT DO NOTHING;
