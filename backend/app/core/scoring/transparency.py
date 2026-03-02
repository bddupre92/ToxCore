"""
Tier 3: Transparency Scoring (15% of overall score)

Scores based on how much is known about the product and its ingredients.
Lower score (better) for products with fully resolved, well-studied ingredients.
Higher score (worse) for products with vague terms, unresolved ingredients,
or incomplete data.
"""

from app.core.scoring.weights import VAGUE_INGREDIENT_TERMS
from app.models.product import IngredientWithChemical, Product


class TransparencyScorer:
    """Score product transparency based on data completeness."""

    def score(
        self,
        product: Product,
        ingredients: list[IngredientWithChemical],
    ) -> float:
        """
        Compute transparency score (0-100). Lower = more transparent.

        Factors:
        - Ingredient resolution rate (what % resolved to known chemicals)
        - Presence of vague terms ("fragrance", "parfum", "flavor")
        - Data completeness (do resolved chemicals have regulatory data)
        - Ingredient list completeness
        """
        if not ingredients:
            # No ingredients at all = very low transparency
            return 90.0

        resolution_penalty = self._score_resolution_rate(ingredients)
        vague_penalty = self._score_vague_terms(ingredients)
        data_completeness_penalty = self._score_data_completeness(ingredients)
        list_completeness_penalty = self._score_list_completeness(product, ingredients)

        # Weight the factors
        total = (
            resolution_penalty * 0.40
            + vague_penalty * 0.25
            + data_completeness_penalty * 0.20
            + list_completeness_penalty * 0.15
        )

        return round(min(100.0, max(0.0, total)), 1)

    def _score_resolution_rate(
        self, ingredients: list[IngredientWithChemical]
    ) -> float:
        """
        Score based on % of ingredients resolved to known chemicals.
        100% resolved = 0 (best). 0% resolved = 100 (worst).
        """
        if not ingredients:
            return 100.0

        resolved = sum(1 for i in ingredients if i.chemical is not None)
        resolution_rate = resolved / len(ingredients)

        # Invert: higher resolution = lower score (better)
        return (1.0 - resolution_rate) * 100

    def _score_vague_terms(
        self, ingredients: list[IngredientWithChemical]
    ) -> float:
        """
        Penalize products with vague umbrella terms.

        "Fragrance" / "Parfum" can hide hundreds of undisclosed chemicals.
        Each vague term adds to the score.
        """
        if not ingredients:
            return 0.0

        vague_count = 0
        for ingredient in ingredients:
            name_lower = ingredient.raw_name.lower().strip()
            if name_lower in VAGUE_INGREDIENT_TERMS:
                vague_count += 1

        # Each vague term adds 30 points, capped at 100
        return min(100.0, vague_count * 30.0)

    def _score_data_completeness(
        self, ingredients: list[IngredientWithChemical]
    ) -> float:
        """
        Score based on data quality for resolved chemicals.

        Chemicals with regulatory review data (CIR, SCCS) are better
        than chemicals with no data at all.
        """
        if not ingredients:
            return 100.0

        resolved = [i for i in ingredients if i.chemical is not None]
        if not resolved:
            return 100.0

        chemicals_with_data = 0
        for ingredient in resolved:
            chem = ingredient.chemical
            assert chem is not None
            has_hazard_data = bool(chem.hazard_data)
            has_regulatory = len(ingredient.regulatory_statuses) > 0
            if has_hazard_data or has_regulatory:
                chemicals_with_data += 1

        data_rate = chemicals_with_data / len(resolved)
        return (1.0 - data_rate) * 100

    def _score_list_completeness(
        self,
        product: Product,
        ingredients: list[IngredientWithChemical],
    ) -> float:
        """
        Check if the ingredient list appears complete.

        Heuristics:
        - Very short lists (< 3 ingredients) may be truncated
        - Missing raw_ingredients on the product suggests no INCI list
        """
        if not product.raw_ingredients:
            return 80.0

        if len(ingredients) < 3:
            return 60.0

        if len(ingredients) < 5:
            return 30.0

        return 0.0
