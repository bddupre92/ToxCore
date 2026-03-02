"""
Tier 1: Hazard Scoring (60% of overall score)

Scores chemicals based on regulatory status, carcinogenicity,
endocrine disruption potential, sensitization, and acute toxicity.
All scoring is deterministic from pre-loaded data.
"""

from app.core.scoring.weights import (
    ACUTE_TOXICITY_WEIGHT,
    CARCINOGENICITY_WEIGHT,
    ENDOCRINE_DISRUPTION_WEIGHT,
    IARC_GROUP_SCORES,
    REGULATORY_BAN_WEIGHT,
    SENSITIZATION_WEIGHT,
)
from app.models.chemical import Chemical, RegulatoryStatus
from app.models.product import IngredientWithChemical
from app.models.score import HazardScore


class HazardScorer:
    """Compute hazard scores for chemicals and products."""

    def score_chemical(
        self,
        chemical: Chemical,
        regulatory_statuses: list[RegulatoryStatus],
    ) -> HazardScore:
        """
        Compute hazard score (0-100) for a single chemical.

        Deterministic scoring based on:
        - Regulatory bans/restrictions
        - IARC carcinogenicity classification
        - Endocrine disruption evidence
        - Skin/respiratory sensitization
        - Acute toxicity data
        """
        regulatory_ban = self._score_regulatory_ban(regulatory_statuses)
        carcinogenicity = self._score_carcinogenicity(chemical, regulatory_statuses)
        endocrine = self._score_endocrine_disruption(chemical, regulatory_statuses)
        sensitization = self._score_sensitization(chemical)
        acute_toxicity = self._score_acute_toxicity(chemical)

        total = (
            regulatory_ban * REGULATORY_BAN_WEIGHT
            + carcinogenicity * CARCINOGENICITY_WEIGHT
            + endocrine * ENDOCRINE_DISRUPTION_WEIGHT
            + sensitization * SENSITIZATION_WEIGHT
            + acute_toxicity * ACUTE_TOXICITY_WEIGHT
        )

        return HazardScore(
            total=round(min(100.0, max(0.0, total)), 1),
            regulatory_ban=round(regulatory_ban, 1),
            carcinogenicity=round(carcinogenicity, 1),
            endocrine_disruption=round(endocrine, 1),
            sensitization=round(sensitization, 1),
            acute_toxicity=round(acute_toxicity, 1),
        )

    def score_product_hazard(
        self,
        ingredients: list[IngredientWithChemical],
    ) -> tuple[float, list[dict]]:
        """
        Aggregate hazard scores across all ingredients in a product.

        Ingredients are weighted by position (first listed = highest concentration).
        Returns the weighted average hazard score and per-ingredient details.
        """
        if not ingredients:
            return 50.0, []

        scored_ingredients: list[dict] = []
        total_weight = 0.0
        weighted_sum = 0.0

        for ingredient in ingredients:
            position_weight = self._position_weight(
                ingredient.position, len(ingredients)
            )

            if ingredient.chemical is not None:
                hazard = self.score_chemical(
                    ingredient.chemical,
                    ingredient.regulatory_statuses,
                )
                chem_score = hazard.total
                contributing = self._get_contributing_factors(
                    ingredient.chemical, ingredient.regulatory_statuses
                )
            else:
                # Unresolved ingredient: moderate default penalty
                chem_score = 40.0
                contributing = ["unresolved_ingredient"]

            weighted_sum += chem_score * position_weight
            total_weight += position_weight

            scored_ingredients.append({
                "raw_name": ingredient.raw_name,
                "position": ingredient.position,
                "resolved": ingredient.chemical is not None,
                "hazard_score": round(chem_score, 1),
                "position_weight": round(position_weight, 4),
                "contributing_factors": contributing,
            })

        if total_weight == 0:
            return 50.0, scored_ingredients

        avg_score = weighted_sum / total_weight
        return round(min(100.0, max(0.0, avg_score)), 1), scored_ingredients

    def _score_regulatory_ban(self, statuses: list[RegulatoryStatus]) -> float:
        """Score based on whether chemical is banned or restricted."""
        score = 0.0
        for status in statuses:
            if status.status in ("banned", "prohibited"):
                score = max(score, 100.0)
            elif status.status == "restricted":
                score = max(score, 70.0)
            elif status.status == "listed" and status.list_name == "ca_prop65":
                score = max(score, 60.0)
        return score

    def _score_carcinogenicity(
        self, chemical: Chemical, statuses: list[RegulatoryStatus]
    ) -> float:
        """Score based on IARC classification and Prop 65 cancer listing."""
        score = 0.0

        # Check IARC classification from regulatory status
        for status in statuses:
            if status.list_name == "iarc" and status.classification:
                iarc_score = IARC_GROUP_SCORES.get(status.classification, 0.0)
                score = max(score, iarc_score)

        # Check hazard_data for IARC group
        iarc_group = chemical.hazard_data.get("iarc_group")
        if iarc_group:
            iarc_score = IARC_GROUP_SCORES.get(str(iarc_group), 0.0)
            score = max(score, iarc_score)

        # Check for explicit carcinogen flag
        if chemical.hazard_data.get("carcinogen"):
            score = max(score, 90.0)

        # Prop 65 cancer listing
        for status in statuses:
            if status.list_name == "ca_prop65":
                details = status.details or {}
                if details.get("listing_type") == "cancer":
                    score = max(score, 70.0)

        return score

    def _score_endocrine_disruption(
        self, chemical: Chemical, statuses: list[RegulatoryStatus]
    ) -> float:
        """Score for endocrine disruption potential."""
        score = 0.0

        if chemical.hazard_data.get("endocrine_disruptor"):
            score = max(score, 80.0)

        if chemical.hazard_data.get("reproductive_toxicant"):
            score = max(score, 75.0)

        # Prop 65 reproductive toxicity
        for status in statuses:
            if status.list_name == "ca_prop65":
                details = status.details or {}
                if details.get("listing_type") == "reproductive":
                    score = max(score, 70.0)

        return score

    def _score_sensitization(self, chemical: Chemical) -> float:
        """Score for skin/respiratory sensitization."""
        score = 0.0

        if chemical.hazard_data.get("sensitizer"):
            score = max(score, 70.0)

        if chemical.hazard_data.get("irritant"):
            score = max(score, 40.0)

        if chemical.hazard_data.get("skin_sensitizer"):
            score = max(score, 65.0)

        if chemical.hazard_data.get("respiratory_sensitizer"):
            score = max(score, 75.0)

        return score

    def _score_acute_toxicity(self, chemical: Chemical) -> float:
        """Score based on LD50/LC50 acute toxicity data."""
        ld50 = chemical.hazard_data.get("ld50_oral_mg_kg")
        if ld50 is None:
            return 0.0

        try:
            ld50_val = float(ld50)
        except (ValueError, TypeError):
            return 0.0

        # GHS acute toxicity categories (oral)
        if ld50_val <= 5:
            return 100.0  # Category 1: Fatal
        elif ld50_val <= 50:
            return 85.0  # Category 2: Fatal
        elif ld50_val <= 300:
            return 65.0  # Category 3: Toxic
        elif ld50_val <= 2000:
            return 40.0  # Category 4: Harmful
        elif ld50_val <= 5000:
            return 20.0  # Category 5: May be harmful
        else:
            return 5.0  # Very low toxicity

    def _position_weight(self, position: int, total: int) -> float:
        """
        Calculate weight based on ingredient list position.

        First ingredient gets highest weight (proxy for concentration).
        Uses inverse-rank weighting: weight = 1 / (position ^ 0.5)
        """
        if position <= 0:
            position = 1
        return 1.0 / (position ** 0.5)

    def _get_contributing_factors(
        self, chemical: Chemical, statuses: list[RegulatoryStatus]
    ) -> list[str]:
        """Identify the key hazard factors for a chemical."""
        factors = []

        for status in statuses:
            if status.status in ("banned", "prohibited"):
                factors.append(f"banned_by_{status.list_name}")
            elif status.status == "restricted":
                factors.append(f"restricted_by_{status.list_name}")
            elif status.list_name == "iarc" and status.classification:
                factors.append(f"iarc_group_{status.classification}")
            elif status.list_name == "ca_prop65":
                factors.append("prop65_listed")

        if chemical.hazard_data.get("endocrine_disruptor"):
            factors.append("endocrine_disruptor")
        if chemical.hazard_data.get("carcinogen"):
            factors.append("carcinogen")
        if chemical.hazard_data.get("sensitizer") or chemical.hazard_data.get("irritant"):
            factors.append("sensitizer_or_irritant")

        return factors
