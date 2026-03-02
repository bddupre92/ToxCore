"""
Tier 2: Exposure Scoring (25% of overall score)

Scores based on how much contact a consumer has with a product's ingredients.
Considers product type (leave-on vs rinse-off), ingredient position
(proxy for concentration), and typical usage frequency.
"""

from app.core.scoring.weights import (
    CATEGORY_FREQUENCY,
    DEFAULT_PRODUCT_TYPE_EXPOSURE,
    FREQUENCY_MULTIPLIERS,
    FREQUENCY_WEIGHT,
    POSITION_WEIGHT,
    PRODUCT_TYPE_EXPOSURE,
    PRODUCT_TYPE_WEIGHT,
)


class ExposureScorer:
    """Compute exposure scores based on product type and usage patterns."""

    def score(
        self,
        product_category: str | None,
        ingredient_positions: list[int],
        total_ingredients: int,
    ) -> float:
        """
        Compute exposure score (0-100) for a product.

        Higher score = more exposure concern.

        Combines:
        - Product type multiplier (leave-on > rinse-off)
        - Average ingredient position (high-concentration ingredients = more concern)
        - Usage frequency (daily > weekly)
        """
        category = (product_category or "").lower().strip()

        product_type_score = self._score_product_type(category)
        position_score = self._score_positions(ingredient_positions, total_ingredients)
        frequency_score = self._score_frequency(category)

        total = (
            position_score * POSITION_WEIGHT
            + product_type_score * PRODUCT_TYPE_WEIGHT
            + frequency_score * FREQUENCY_WEIGHT
        )

        return round(min(100.0, max(0.0, total)), 1)

    def score_for_ingredient(
        self,
        product_category: str | None,
        position: int,
        total_ingredients: int,
    ) -> float:
        """Compute exposure score for a single ingredient in context."""
        category = (product_category or "").lower().strip()

        product_type_multiplier = PRODUCT_TYPE_EXPOSURE.get(
            category, DEFAULT_PRODUCT_TYPE_EXPOSURE
        )
        frequency = CATEGORY_FREQUENCY.get(category, "daily")
        frequency_multiplier = FREQUENCY_MULTIPLIERS.get(frequency, 0.70)

        # Position factor: first ingredients have higher concentration
        position_factor = self._single_position_factor(position, total_ingredients)

        # Combine: higher product exposure * higher position * higher frequency
        raw_score = product_type_multiplier * position_factor * frequency_multiplier * 100

        return round(min(100.0, max(0.0, raw_score)), 1)

    def _score_product_type(self, category: str) -> float:
        """Score based on product type (0-100). Leave-on scores higher."""
        multiplier = PRODUCT_TYPE_EXPOSURE.get(category, DEFAULT_PRODUCT_TYPE_EXPOSURE)
        return multiplier * 100

    def _score_positions(
        self, positions: list[int], total_ingredients: int
    ) -> float:
        """
        Score based on how many concerning ingredients are in high positions.

        For exposure scoring, we care about the average position of all
        ingredients — products with many high-concentration ingredients
        score higher.
        """
        if not positions or total_ingredients == 0:
            return 50.0

        # Average normalized position (0 = last, 1 = first)
        normalized = [
            1.0 - (pos - 1) / max(total_ingredients - 1, 1)
            for pos in positions
        ]
        avg_normalized = sum(normalized) / len(normalized)

        return avg_normalized * 100

    def _score_frequency(self, category: str) -> float:
        """Score based on how often the product is used (0-100)."""
        frequency = CATEGORY_FREQUENCY.get(category, "daily")
        multiplier = FREQUENCY_MULTIPLIERS.get(frequency, 0.70)
        return multiplier * 100

    def _single_position_factor(
        self, position: int, total_ingredients: int
    ) -> float:
        """Position factor for a single ingredient (0-1). First = 1.0."""
        if total_ingredients <= 1:
            return 1.0
        return 1.0 - (position - 1) / max(total_ingredients - 1, 1)
