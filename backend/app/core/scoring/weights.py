"""
ToxScore Scoring Weight Constants

All weights are defined here as the single source of truth.
Weights within each tier must sum to 1.0.
Tier weights must sum to 1.0.
"""

# Tier weights (must sum to 1.0)
HAZARD_WEIGHT = 0.60
EXPOSURE_WEIGHT = 0.25
TRANSPARENCY_WEIGHT = 0.15

# Hazard sub-weights (must sum to 1.0)
REGULATORY_BAN_WEIGHT = 0.30
CARCINOGENICITY_WEIGHT = 0.25
ENDOCRINE_DISRUPTION_WEIGHT = 0.20
SENSITIZATION_WEIGHT = 0.15
ACUTE_TOXICITY_WEIGHT = 0.10

# Exposure sub-weights (must sum to 1.0)
POSITION_WEIGHT = 0.40
PRODUCT_TYPE_WEIGHT = 0.30
FREQUENCY_WEIGHT = 0.30

# Product type exposure multipliers (0-1 scale)
# Higher = more exposure concern
PRODUCT_TYPE_EXPOSURE: dict[str, float] = {
    "toothpaste": 0.70,
    "lip_balm": 0.80,
    "sunscreen": 0.90,
    "lotion": 0.85,
    "moisturizer": 0.85,
    "deodorant": 0.75,
    "shampoo": 0.50,
    "conditioner": 0.55,
    "face_wash": 0.45,
    "body_wash": 0.40,
}

# Default for unknown product types
DEFAULT_PRODUCT_TYPE_EXPOSURE = 0.60

# Usage frequency multipliers
FREQUENCY_MULTIPLIERS: dict[str, float] = {
    "multiple_daily": 1.0,
    "twice_daily": 0.85,
    "daily": 0.70,
    "several_weekly": 0.50,
    "weekly": 0.30,
}

# Category to frequency mapping
CATEGORY_FREQUENCY: dict[str, str] = {
    "toothpaste": "twice_daily",
    "lip_balm": "multiple_daily",
    "sunscreen": "daily",
    "lotion": "daily",
    "moisturizer": "twice_daily",
    "deodorant": "daily",
    "shampoo": "several_weekly",
    "conditioner": "several_weekly",
    "face_wash": "twice_daily",
    "body_wash": "daily",
}

# Grade thresholds
GRADE_THRESHOLDS: dict[str, tuple[float, float]] = {
    "A": (0.0, 20.0),
    "B": (20.0, 40.0),
    "C": (40.0, 60.0),
    "D": (60.0, 80.0),
    "F": (80.0, 100.0),
}

# IARC group hazard scores (0-100)
IARC_GROUP_SCORES: dict[str, float] = {
    "1": 95.0,    # Carcinogenic to humans
    "2A": 75.0,   # Probably carcinogenic
    "2B": 55.0,   # Possibly carcinogenic
    "3": 15.0,    # Not classifiable
}

# Vague ingredient terms that reduce transparency
VAGUE_INGREDIENT_TERMS: set[str] = {
    "fragrance",
    "parfum",
    "flavor",
    "aroma",
    "natural flavor",
    "natural fragrance",
    "proprietary blend",
}
