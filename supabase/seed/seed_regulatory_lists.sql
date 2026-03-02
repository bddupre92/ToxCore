-- Seed regulatory lists
INSERT INTO regulatory_lists (name, full_name, authority, url) VALUES
    ('ca_prop65', 'California Proposition 65', 'California OEHHA', 'https://oehha.ca.gov/proposition-65/proposition-65-list'),
    ('iarc', 'IARC Monographs on Carcinogens', 'International Agency for Research on Cancer', 'https://monographs.iarc.who.int/agents-classified-by-the-iarc/'),
    ('eu_cosing', 'EU CosIng Database', 'European Commission', 'https://single-market-economy.ec.europa.eu/sectors/cosmetics/cosmetic-ingredient-database_en'),
    ('ifra', 'IFRA Standards', 'International Fragrance Association', 'https://ifrafragrance.org/safe-use/library'),
    ('cir', 'CIR Safety Assessments', 'Cosmetic Ingredient Review', 'https://www.cir-safety.org/ingredients'),
    ('eu_annex_ii', 'EU Cosmetics Regulation Annex II (Prohibited)', 'European Commission', 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32009R1223'),
    ('eu_annex_iii', 'EU Cosmetics Regulation Annex III (Restricted)', 'European Commission', 'https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32009R1223'),
    ('epa_comptox', 'EPA CompTox Chemicals Dashboard', 'US Environmental Protection Agency', 'https://comptox.epa.gov/dashboard/')
ON CONFLICT (name) DO NOTHING;
