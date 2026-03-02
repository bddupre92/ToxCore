"""Tests for the Hazard scoring tier."""

import pytest

from app.core.scoring.hazard import HazardScorer
from app.models.chemical import Chemical, RegulatoryStatus


@pytest.fixture
def scorer():
    return HazardScorer()


def make_chemical(hazard_data: dict | None = None) -> Chemical:
    return Chemical(
        id="test",
        preferred_name="Test",
        hazard_data=hazard_data or {},
    )


class TestChemicalHazardScoring:
    def test_clean_chemical_scores_low(self, scorer):
        """Chemical with no hazard flags should score near zero."""
        chem = make_chemical()
        score = scorer.score_chemical(chem, [])
        assert score.total < 10

    def test_iarc_group_1_scores_high(self, scorer):
        """IARC Group 1 carcinogen should score very high."""
        chem = make_chemical({"iarc_group": "1", "carcinogen": True})
        statuses = [
            RegulatoryStatus(list_name="iarc", status="listed", classification="1"),
        ]
        score = scorer.score_chemical(chem, statuses)
        assert score.carcinogenicity >= 90

    def test_iarc_group_2b_scores_moderate(self, scorer):
        """IARC Group 2B should score moderately."""
        chem = make_chemical({"iarc_group": "2B"})
        statuses = [
            RegulatoryStatus(list_name="iarc", status="listed", classification="2B"),
        ]
        score = scorer.score_chemical(chem, statuses)
        assert 40 <= score.carcinogenicity <= 70

    def test_banned_chemical_max_regulatory(self, scorer):
        """Banned chemical should get max regulatory ban score."""
        chem = make_chemical()
        statuses = [
            RegulatoryStatus(list_name="eu_annex_ii", status="banned"),
        ]
        score = scorer.score_chemical(chem, statuses)
        assert score.regulatory_ban == 100.0

    def test_endocrine_disruptor(self, scorer):
        """Known endocrine disruptor should score high."""
        chem = make_chemical({
            "endocrine_disruptor": True,
            "reproductive_toxicant": True,
        })
        score = scorer.score_chemical(chem, [])
        assert score.endocrine_disruption >= 75

    def test_sensitizer(self, scorer):
        """Known sensitizer should have elevated score."""
        chem = make_chemical({"sensitizer": True})
        score = scorer.score_chemical(chem, [])
        assert score.sensitization >= 60

    def test_irritant_less_than_sensitizer(self, scorer):
        """Irritant should score lower than sensitizer."""
        irritant = scorer.score_chemical(make_chemical({"irritant": True}), [])
        sensitizer = scorer.score_chemical(make_chemical({"sensitizer": True}), [])
        assert irritant.sensitization < sensitizer.sensitization

    def test_acute_toxicity_ld50_categories(self, scorer):
        """LD50 values should map to GHS categories."""
        # Category 1: Fatal (LD50 <= 5)
        score = scorer.score_chemical(make_chemical({"ld50_oral_mg_kg": 3}), [])
        assert score.acute_toxicity == 100.0

        # Category 3: Toxic (LD50 <= 300)
        score = scorer.score_chemical(make_chemical({"ld50_oral_mg_kg": 200}), [])
        assert score.acute_toxicity == 65.0

        # Very low toxicity (LD50 > 5000)
        score = scorer.score_chemical(make_chemical({"ld50_oral_mg_kg": 10000}), [])
        assert score.acute_toxicity == 5.0

    def test_no_ld50_data_scores_zero(self, scorer):
        """Missing LD50 data should not contribute to score."""
        score = scorer.score_chemical(make_chemical(), [])
        assert score.acute_toxicity == 0.0


class TestProductHazardScoring:
    def test_position_weighting(self, scorer):
        """First ingredient should contribute more than last."""
        from app.models.product import IngredientWithChemical

        bad_chem = make_chemical({"carcinogen": True, "iarc_group": "1"})

        # Bad chemical first
        ingredients_first = [
            IngredientWithChemical(
                raw_name="BAD", position=1, chemical=bad_chem,
                regulatory_statuses=[
                    RegulatoryStatus(list_name="iarc", classification="1"),
                ],
            ),
            IngredientWithChemical(
                raw_name="AQUA", position=2, chemical=make_chemical(),
            ),
        ]

        # Bad chemical last
        ingredients_last = [
            IngredientWithChemical(
                raw_name="AQUA", position=1, chemical=make_chemical(),
            ),
            IngredientWithChemical(
                raw_name="BAD", position=2, chemical=bad_chem,
                regulatory_statuses=[
                    RegulatoryStatus(list_name="iarc", classification="1"),
                ],
            ),
        ]

        score_first, _ = scorer.score_product_hazard(ingredients_first)
        score_last, _ = scorer.score_product_hazard(ingredients_last)

        assert score_first > score_last

    def test_empty_ingredients_default(self, scorer):
        """Empty ingredient list should return moderate default."""
        score, details = scorer.score_product_hazard([])
        assert score == 50.0
        assert details == []
