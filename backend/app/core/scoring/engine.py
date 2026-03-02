"""
ToxScore Scoring Engine

Combines the three scoring tiers into an overall product score.
100% deterministic — no AI, no ML, no network calls.

Score range: 0-100 (lower = safer)
Grade: A (0-20), B (20-40), C (40-60), D (60-80), F (80-100)
"""

from app.core.scoring.exposure import ExposureScorer
from app.core.scoring.hazard import HazardScorer
from app.core.scoring.transparency import TransparencyScorer
from app.core.scoring.weights import (
    EXPOSURE_WEIGHT,
    GRADE_THRESHOLDS,
    HAZARD_WEIGHT,
    TRANSPARENCY_WEIGHT,
)
from app.models.product import IngredientWithChemical, Product
from app.models.score import IngredientScoreDetail, ProductScore


class ScoringEngine:
    """Main scoring engine that combines all three tiers."""

    VERSION = "v1.0"

    def __init__(self) -> None:
        self.hazard_scorer = HazardScorer()
        self.exposure_scorer = ExposureScorer()
        self.transparency_scorer = TransparencyScorer()

    def compute_score(
        self,
        product: Product,
        ingredients: list[IngredientWithChemical],
    ) -> ProductScore:
        """
        Compute the full ToxScore for a product.

        This is a pure function: same inputs always produce same outputs.
        No side effects, no network calls, no randomness.
        """
        # Tier 1: Hazard (60%)
        hazard_score, ingredient_details = self.hazard_scorer.score_product_hazard(
            ingredients
        )

        # Tier 2: Exposure (25%)
        positions = [i.position for i in ingredients]
        exposure_score = self.exposure_scorer.score(
            product.category,
            positions,
            len(ingredients),
        )

        # Tier 3: Transparency (15%)
        transparency_score = self.transparency_scorer.score(product, ingredients)

        # Weighted combination
        overall = (
            hazard_score * HAZARD_WEIGHT
            + exposure_score * EXPOSURE_WEIGHT
            + transparency_score * TRANSPARENCY_WEIGHT
        )
        overall = round(min(100.0, max(0.0, overall)), 1)

        # Convert ingredient details to model
        details = [
            IngredientScoreDetail(
                raw_name=d["raw_name"],
                position=d["position"],
                resolved=d["resolved"],
                hazard_score=d["hazard_score"],
                position_weight=d["position_weight"],
                contributing_factors=d["contributing_factors"],
            )
            for d in ingredient_details
        ]

        return ProductScore(
            overall_score=overall,
            hazard_score=round(hazard_score, 1),
            exposure_score=round(exposure_score, 1),
            transparency_score=round(transparency_score, 1),
            grade=self.score_to_grade(overall),
            scoring_version=self.VERSION,
            ingredient_details=details,
        )

    @staticmethod
    def score_to_grade(score: float) -> str:
        """Convert a numeric score (0-100) to a letter grade."""
        for grade, (low, high) in GRADE_THRESHOLDS.items():
            if low <= score < high:
                return grade
        return "F"  # 100.0 maps to F
