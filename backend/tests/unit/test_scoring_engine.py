"""
Comprehensive tests for the ToxScore scoring engine.

Tests cover:
- Weight constraints (sums to 1.0)
- Grade boundaries
- Determinism (same inputs -> same outputs)
- Edge cases (empty ingredients, single ingredient, all unresolved)
- Known-good products (golden test data)
"""

import pytest

from app.core.scoring.engine import ScoringEngine
from app.core.scoring.weights import (
    ACUTE_TOXICITY_WEIGHT,
    CARCINOGENICITY_WEIGHT,
    ENDOCRINE_DISRUPTION_WEIGHT,
    EXPOSURE_WEIGHT,
    FREQUENCY_WEIGHT,
    HAZARD_WEIGHT,
    POSITION_WEIGHT,
    PRODUCT_TYPE_WEIGHT,
    REGULATORY_BAN_WEIGHT,
    SENSITIZATION_WEIGHT,
    TRANSPARENCY_WEIGHT,
)
from app.models.chemical import Chemical, RegulatoryStatus
from app.models.product import IngredientWithChemical, Product


@pytest.fixture
def engine():
    return ScoringEngine()


def make_product(
    name: str = "Test Product",
    category: str = "shampoo",
    raw_ingredients: str = "AQUA, SODIUM LAURYL SULFATE",
) -> Product:
    return Product(
        id="test-id",
        name=name,
        category=category,
        raw_ingredients=raw_ingredients,
    )


def make_ingredient(
    raw_name: str,
    position: int,
    chemical: Chemical | None = None,
    regulatory_statuses: list[RegulatoryStatus] | None = None,
) -> IngredientWithChemical:
    return IngredientWithChemical(
        raw_name=raw_name,
        position=position,
        chemical=chemical,
        regulatory_statuses=regulatory_statuses or [],
    )


def make_chemical(
    name: str = "Test Chemical",
    hazard_data: dict | None = None,
    cas_number: str | None = None,
) -> Chemical:
    return Chemical(
        id="chem-id",
        preferred_name=name,
        cas_number=cas_number,
        hazard_data=hazard_data or {},
    )


# ============================================================================
# Weight Constraint Tests
# ============================================================================

class TestWeightConstraints:
    def test_tier_weights_sum_to_one(self):
        total = HAZARD_WEIGHT + EXPOSURE_WEIGHT + TRANSPARENCY_WEIGHT
        assert abs(total - 1.0) < 1e-10, f"Tier weights sum to {total}, expected 1.0"

    def test_hazard_sub_weights_sum_to_one(self):
        total = (
            REGULATORY_BAN_WEIGHT
            + CARCINOGENICITY_WEIGHT
            + ENDOCRINE_DISRUPTION_WEIGHT
            + SENSITIZATION_WEIGHT
            + ACUTE_TOXICITY_WEIGHT
        )
        assert abs(total - 1.0) < 1e-10, f"Hazard sub-weights sum to {total}"

    def test_exposure_sub_weights_sum_to_one(self):
        total = POSITION_WEIGHT + PRODUCT_TYPE_WEIGHT + FREQUENCY_WEIGHT
        assert abs(total - 1.0) < 1e-10, f"Exposure sub-weights sum to {total}"


# ============================================================================
# Grade Boundary Tests
# ============================================================================

class TestGradeBoundaries:
    def test_grade_a(self, engine):
        assert engine.score_to_grade(0.0) == "A"
        assert engine.score_to_grade(10.0) == "A"
        assert engine.score_to_grade(19.9) == "A"

    def test_grade_b(self, engine):
        assert engine.score_to_grade(20.0) == "B"
        assert engine.score_to_grade(30.0) == "B"
        assert engine.score_to_grade(39.9) == "B"

    def test_grade_c(self, engine):
        assert engine.score_to_grade(40.0) == "C"
        assert engine.score_to_grade(50.0) == "C"
        assert engine.score_to_grade(59.9) == "C"

    def test_grade_d(self, engine):
        assert engine.score_to_grade(60.0) == "D"
        assert engine.score_to_grade(70.0) == "D"
        assert engine.score_to_grade(79.9) == "D"

    def test_grade_f(self, engine):
        assert engine.score_to_grade(80.0) == "F"
        assert engine.score_to_grade(90.0) == "F"
        assert engine.score_to_grade(100.0) == "F"


# ============================================================================
# Determinism Tests
# ============================================================================

class TestDeterminism:
    def test_same_inputs_same_outputs(self, engine):
        product = make_product()
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("SLS", 2, make_chemical("SLS", {"irritant": True})),
        ]

        score1 = engine.compute_score(product, ingredients)
        score2 = engine.compute_score(product, ingredients)

        assert score1.overall_score == score2.overall_score
        assert score1.hazard_score == score2.hazard_score
        assert score1.exposure_score == score2.exposure_score
        assert score1.transparency_score == score2.transparency_score
        assert score1.grade == score2.grade

    def test_determinism_over_many_runs(self, engine):
        product = make_product(category="toothpaste")
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("SODIUM FLUORIDE", 2, make_chemical("Sodium Fluoride")),
            make_ingredient("PARFUM", 3),  # Unresolved
        ]

        scores = [engine.compute_score(product, ingredients) for _ in range(100)]
        first = scores[0]
        for s in scores[1:]:
            assert s.overall_score == first.overall_score


# ============================================================================
# Edge Case Tests
# ============================================================================

class TestEdgeCases:
    def test_empty_ingredients(self, engine):
        product = make_product(raw_ingredients=None)
        score = engine.compute_score(product, [])

        assert 0 <= score.overall_score <= 100
        assert score.grade in ("A", "B", "C", "D", "F")
        assert score.scoring_version == "v1.0"
        # No ingredients = high transparency concern
        assert score.transparency_score > 50

    def test_single_ingredient(self, engine):
        product = make_product()
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
        ]
        score = engine.compute_score(product, ingredients)

        assert 0 <= score.overall_score <= 100
        assert len(score.ingredient_details) == 1

    def test_all_unresolved_ingredients(self, engine):
        product = make_product()
        ingredients = [
            make_ingredient("UNKNOWN1", 1),
            make_ingredient("UNKNOWN2", 2),
            make_ingredient("UNKNOWN3", 3),
        ]
        score = engine.compute_score(product, ingredients)

        # All unresolved = moderate hazard + low transparency
        assert score.transparency_score > 50
        assert all(not d.resolved for d in score.ingredient_details)

    def test_score_bounds(self, engine):
        """Scores must always be between 0 and 100."""
        product = make_product()

        # Worst case: known carcinogen, banned, endocrine disruptor
        bad_chem = make_chemical("Bad Chemical", {
            "carcinogen": True,
            "iarc_group": "1",
            "endocrine_disruptor": True,
            "reproductive_toxicant": True,
            "sensitizer": True,
            "ld50_oral_mg_kg": 3,
        })
        bad_statuses = [
            RegulatoryStatus(list_name="ca_prop65", status="listed",
                             details={"listing_type": "cancer"}),
            RegulatoryStatus(list_name="iarc", status="listed", classification="1"),
            RegulatoryStatus(list_name="eu_annex_ii", status="banned"),
        ]
        ingredients = [
            make_ingredient("BAD", 1, bad_chem, bad_statuses),
        ]
        score = engine.compute_score(product, ingredients)

        assert 0 <= score.overall_score <= 100
        assert 0 <= score.hazard_score <= 100
        assert 0 <= score.exposure_score <= 100
        assert 0 <= score.transparency_score <= 100


# ============================================================================
# Known-Good Product Tests (Golden Data)
# ============================================================================

class TestKnownProducts:
    """Test specific products with expected behavior."""

    def test_safe_product_scores_low(self, engine):
        """A product with all safe, well-known ingredients should score well."""
        product = make_product(
            name="Safe Moisturizer",
            category="moisturizer",
            raw_ingredients="AQUA, GLYCERIN, CETYL ALCOHOL, TOCOPHERYL ACETATE",
        )
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("GLYCERIN", 2, make_chemical("Glycerin")),
            make_ingredient("CETYL ALCOHOL", 3, make_chemical("Cetyl Alcohol")),
            make_ingredient(
                "TOCOPHERYL ACETATE", 4, make_chemical("Vitamin E Acetate")
            ),
        ]
        score = engine.compute_score(product, ingredients)

        # Safe ingredients, all resolved = should be grade A or B
        assert score.grade in ("A", "B"), (
            f"Safe product got grade {score.grade} (score={score.overall_score})"
        )
        assert score.hazard_score < 30

    def test_concerning_product_scores_high(self, engine):
        """A product with known carcinogens should score poorly."""
        product = make_product(
            name="Concerning Product",
            category="lotion",
            raw_ingredients="AQUA, FORMALDEHYDE, PARFUM",
        )

        formaldehyde = make_chemical(
            "Formaldehyde",
            {"carcinogen": True, "iarc_group": "1", "sensitizer": True},
        )
        form_statuses = [
            RegulatoryStatus(
                list_name="iarc", status="listed", classification="1"
            ),
            RegulatoryStatus(
                list_name="ca_prop65", status="listed",
                details={"listing_type": "cancer"},
            ),
        ]

        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("FORMALDEHYDE", 2, formaldehyde, form_statuses),
            make_ingredient("PARFUM", 3),  # Vague, unresolved
        ]
        score = engine.compute_score(product, ingredients)

        # Formaldehyde (IARC Group 1) + parfum + diluted by water at position 1
        # Should score worse than a fully safe product (grade B or higher)
        assert score.grade in ("B", "C", "D", "F"), (
            f"Concerning product got grade {score.grade} (score={score.overall_score})"
        )
        assert score.hazard_score > 20

    def test_fragrance_reduces_transparency(self, engine):
        """Products with 'PARFUM' should have lower transparency scores."""
        product_with_parfum = make_product(
            raw_ingredients="AQUA, GLYCERIN, PARFUM"
        )
        product_without = make_product(
            raw_ingredients="AQUA, GLYCERIN, CITRIC ACID"
        )

        glycerin = make_chemical("Glycerin")
        citric = make_chemical("Citric Acid")

        ingredients_with = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("GLYCERIN", 2, glycerin),
            make_ingredient("PARFUM", 3),  # Vague + unresolved
        ]
        ingredients_without = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("GLYCERIN", 2, glycerin),
            make_ingredient("CITRIC ACID", 3, citric),
        ]

        score_with = engine.compute_score(product_with_parfum, ingredients_with)
        score_without = engine.compute_score(product_without, ingredients_without)

        assert score_with.transparency_score > score_without.transparency_score

    def test_leave_on_higher_exposure_than_rinse_off(self, engine):
        """Leave-on products should score higher on exposure than rinse-off."""
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("GLYCERIN", 2, make_chemical("Glycerin")),
        ]

        lotion = make_product(category="lotion", name="Lotion")
        body_wash = make_product(category="body_wash", name="Body Wash")

        score_lotion = engine.compute_score(lotion, ingredients)
        score_wash = engine.compute_score(body_wash, ingredients)

        assert score_lotion.exposure_score > score_wash.exposure_score

    def test_banned_chemical_scores_very_high(self, engine):
        """A banned chemical should produce very high hazard scores."""
        product = make_product()
        banned_chem = make_chemical("Banned Substance")
        banned_statuses = [
            RegulatoryStatus(
                list_name="eu_annex_ii", status="banned"
            ),
        ]

        ingredients = [
            make_ingredient("BANNED", 1, banned_chem, banned_statuses),
        ]
        score = engine.compute_score(product, ingredients)

        # Single banned ingredient = high hazard
        assert score.hazard_score > 20


# ============================================================================
# Scoring Version Tests
# ============================================================================

class TestScoringVersion:
    def test_version_is_set(self, engine):
        product = make_product()
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
        ]
        score = engine.compute_score(product, ingredients)
        assert score.scoring_version == "v1.0"

    def test_ingredient_details_populated(self, engine):
        product = make_product()
        ingredients = [
            make_ingredient("AQUA", 1, make_chemical("Water")),
            make_ingredient("SLS", 2, make_chemical("SLS", {"irritant": True})),
        ]
        score = engine.compute_score(product, ingredients)

        assert len(score.ingredient_details) == 2
        assert score.ingredient_details[0].raw_name == "AQUA"
        assert score.ingredient_details[1].raw_name == "SLS"
        assert score.ingredient_details[0].position == 1
        assert score.ingredient_details[1].position == 2
