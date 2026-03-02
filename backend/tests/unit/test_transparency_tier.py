"""Tests for the Transparency scoring tier."""

import pytest

from app.core.scoring.transparency import TransparencyScorer
from app.models.chemical import Chemical
from app.models.product import IngredientWithChemical, Product


@pytest.fixture
def scorer():
    return TransparencyScorer()


def make_product(raw_ingredients: str | None = "AQUA, GLYCERIN") -> Product:
    return Product(id="test", name="Test", raw_ingredients=raw_ingredients)


def make_resolved(name: str, position: int) -> IngredientWithChemical:
    return IngredientWithChemical(
        raw_name=name,
        position=position,
        chemical=Chemical(id="chem", preferred_name=name, hazard_data={"some": "data"}),
        regulatory_statuses=[],
    )


def make_unresolved(name: str, position: int) -> IngredientWithChemical:
    return IngredientWithChemical(
        raw_name=name,
        position=position,
        chemical=None,
    )


class TestResolutionRate:
    def test_all_resolved_low_score(self, scorer):
        """100% resolved ingredients should minimize resolution penalty."""
        product = make_product()
        ingredients = [
            make_resolved("AQUA", 1),
            make_resolved("GLYCERIN", 2),
            make_resolved("CETYL ALCOHOL", 3),
            make_resolved("DIMETHICONE", 4),
            make_resolved("TOCOPHEROL", 5),
        ]
        score = scorer.score(product, ingredients)
        assert score < 30

    def test_none_resolved_high_score(self, scorer):
        """0% resolved ingredients should maximize resolution penalty."""
        product = make_product()
        ingredients = [
            make_unresolved("UNKNOWN1", 1),
            make_unresolved("UNKNOWN2", 2),
            make_unresolved("UNKNOWN3", 3),
            make_unresolved("UNKNOWN4", 4),
            make_unresolved("UNKNOWN5", 5),
        ]
        score = scorer.score(product, ingredients)
        assert score >= 60

    def test_partial_resolution(self, scorer):
        """50% resolved should be between 0% and 100%."""
        product = make_product()
        all_resolved = [make_resolved(f"CHEM{i}", i) for i in range(1, 6)]
        none_resolved = [make_unresolved(f"UNK{i}", i) for i in range(1, 6)]
        half_resolved = [
            make_resolved("AQUA", 1),
            make_unresolved("UNK1", 2),
            make_resolved("GLYCERIN", 3),
            make_unresolved("UNK2", 4),
            make_resolved("DIMETHICONE", 5),
        ]

        score_all = scorer.score(product, all_resolved)
        score_none = scorer.score(product, none_resolved)
        score_half = scorer.score(product, half_resolved)

        assert score_all < score_half < score_none


class TestVagueTerms:
    def test_parfum_increases_score(self, scorer):
        """'PARFUM' should increase transparency score."""
        product = make_product()
        without = [
            make_resolved("AQUA", 1),
            make_resolved("GLYCERIN", 2),
            make_resolved("CITRIC ACID", 3),
            make_resolved("TOCOPHEROL", 4),
            make_resolved("DIMETHICONE", 5),
        ]
        with_parfum = [
            make_resolved("AQUA", 1),
            make_resolved("GLYCERIN", 2),
            make_unresolved("PARFUM", 3),
            make_resolved("TOCOPHEROL", 4),
            make_resolved("DIMETHICONE", 5),
        ]

        score_without = scorer.score(product, without)
        score_with = scorer.score(product, with_parfum)

        assert score_with > score_without

    def test_fragrance_detected(self, scorer):
        """'fragrance' (case-insensitive) should be detected as vague."""
        product = make_product()
        ingredients = [
            make_resolved("AQUA", 1),
            make_resolved("GLYCERIN", 2),
            make_unresolved("fragrance", 3),
            make_resolved("TOCOPHEROL", 4),
            make_resolved("DIMETHICONE", 5),
        ]
        score = scorer.score(product, ingredients)
        # Should be higher due to vague term
        assert score > 15


class TestListCompleteness:
    def test_no_ingredients_text_penalized(self, scorer):
        """Product with no raw_ingredients should be penalized."""
        product = make_product(raw_ingredients=None)
        score = scorer.score(product, [])
        assert score > 80

    def test_very_short_list_penalized(self, scorer):
        """Very short ingredient lists may be truncated."""
        product = make_product(raw_ingredients="AQUA, GLYCERIN")
        ingredients = [
            make_resolved("AQUA", 1),
            make_resolved("GLYCERIN", 2),
        ]
        score = scorer.score(product, ingredients)
        # Short list = some transparency concern (list completeness penalty)
        assert score >= 9
