"""Tests for the Exposure scoring tier."""

import pytest

from app.core.scoring.exposure import ExposureScorer


@pytest.fixture
def scorer():
    return ExposureScorer()


class TestProductTypeScoring:
    def test_leave_on_higher_than_rinse_off(self, scorer):
        """Leave-on products should score higher exposure."""
        positions = [1, 2, 3]
        lotion = scorer.score("lotion", positions, 3)
        shampoo = scorer.score("shampoo", positions, 3)
        assert lotion > shampoo

    def test_sunscreen_highest_exposure(self, scorer):
        """Sunscreen (leave-on, large area) should be among highest."""
        positions = [1, 2, 3]
        sunscreen = scorer.score("sunscreen", positions, 3)
        body_wash = scorer.score("body_wash", positions, 3)
        assert sunscreen > body_wash

    def test_unknown_category_uses_default(self, scorer):
        """Unknown category should use default multiplier."""
        positions = [1, 2, 3]
        score = scorer.score("unknown_category", positions, 3)
        assert 0 <= score <= 100


class TestPositionScoring:
    def test_score_bounds(self, scorer):
        """Exposure score must be 0-100."""
        for category in ["shampoo", "lotion", "sunscreen", "toothpaste"]:
            for positions in [[], [1], [1, 2, 3], list(range(1, 21))]:
                total = max(len(positions), 1)
                score = scorer.score(category, positions, total)
                assert 0 <= score <= 100, f"Score {score} out of bounds"


class TestIngredientExposure:
    def test_first_ingredient_higher(self, scorer):
        """First ingredient should have higher exposure than last."""
        first = scorer.score_for_ingredient("lotion", 1, 10)
        last = scorer.score_for_ingredient("lotion", 10, 10)
        assert first > last

    def test_single_ingredient_max_position(self, scorer):
        """Single ingredient should get max position factor."""
        score = scorer.score_for_ingredient("lotion", 1, 1)
        assert score > 0
