"""
Claude API integration for generating product/chemical explanations.

The AI never generates scores — it only explains pre-computed data
in consumer-friendly language with mandatory source citations.
"""

import logging

from app.core.ai.guardrails import AIGuardrails
from app.core.ai.prompts import (
    CHEMICAL_EXPLANATION_PROMPT,
    PRODUCT_EXPLANATION_PROMPT,
    PROMPT_VERSION,
)

logger = logging.getLogger(__name__)


class AIExplainer:
    """Generate explanations using Claude API."""

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 1024

    def __init__(self, api_key: str) -> None:
        import anthropic

        self.client = anthropic.Anthropic(api_key=api_key)
        self.guardrails = AIGuardrails()

    def explain_product(
        self,
        product_data: dict,
        score_data: dict,
        ingredient_analysis: list[dict],
    ) -> dict:
        """
        Generate a product safety explanation.

        Args:
            product_data: Product name, brand, category, etc.
            score_data: Pre-computed scores (overall, hazard, exposure, transparency, grade)
            ingredient_analysis: Per-ingredient hazard details

        Returns:
            Dict with explanation text, model version, and validation status.
        """
        prompt = PRODUCT_EXPLANATION_PROMPT.format(
            product_data=self._format_product(product_data),
            score_breakdown=self._format_scores(score_data),
            ingredient_analysis=self._format_ingredients(ingredient_analysis),
        )

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        explanation = response.content[0].text

        # Validate with guardrails
        known_chemicals = {
            i.get("raw_name", "") for i in ingredient_analysis
        }
        is_valid, issues = self.guardrails.validate(
            explanation,
            known_chemicals=known_chemicals,
            actual_score=score_data.get("overall_score"),
            actual_grade=score_data.get("grade"),
        )

        if not is_valid:
            logger.warning("AI guardrail issues: %s", issues)

        return {
            "explanation": explanation,
            "model_version": self.MODEL,
            "prompt_version": PROMPT_VERSION,
            "valid": is_valid,
            "issues": issues,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    def explain_chemical(
        self,
        chemical_data: dict,
        regulatory_status: list[dict],
    ) -> dict:
        """Generate a chemical safety explanation."""
        prompt = CHEMICAL_EXPLANATION_PROMPT.format(
            chemical_data=self._format_chemical(chemical_data),
            regulatory_status=self._format_regulatory(regulatory_status),
        )

        response = self.client.messages.create(
            model=self.MODEL,
            max_tokens=self.MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

        explanation = response.content[0].text

        is_valid, issues = self.guardrails.validate(explanation)

        if not is_valid:
            logger.warning("AI guardrail issues for chemical: %s", issues)

        return {
            "explanation": explanation,
            "model_version": self.MODEL,
            "prompt_version": PROMPT_VERSION,
            "valid": is_valid,
            "issues": issues,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }

    def _format_product(self, data: dict) -> str:
        lines = []
        for key in ["name", "brand", "category"]:
            if data.get(key):
                lines.append(f"{key}: {data[key]}")
        return "\n".join(lines) if lines else "No product data available"

    def _format_scores(self, data: dict) -> str:
        lines = [
            f"Overall Score: {data.get('overall_score', 'N/A')}/100",
            f"Grade: {data.get('grade', 'N/A')}",
            f"Hazard Score: {data.get('hazard_score', 'N/A')}/100 (60% weight)",
            f"Exposure Score: {data.get('exposure_score', 'N/A')}/100 (25% weight)",
            f"Transparency Score: {data.get('transparency_score', 'N/A')}/100 (15% weight)",
        ]
        return "\n".join(lines)

    def _format_ingredients(self, ingredients: list[dict]) -> str:
        lines = []
        for i in ingredients:
            name = i.get("raw_name", "Unknown")
            hazard = i.get("hazard_score", "N/A")
            factors = i.get("contributing_factors", [])
            resolved = "Identified" if i.get("resolved") else "Unidentified"
            line = f"- {name} (Position {i.get('position', '?')}, {resolved}, Hazard: {hazard})"
            if factors:
                line += f" [{', '.join(factors)}]"
            lines.append(line)
        return "\n".join(lines) if lines else "No ingredient analysis available"

    def _format_chemical(self, data: dict) -> str:
        lines = []
        for key in [
            "preferred_name", "cas_number", "inci_name",
            "molecular_formula", "description",
        ]:
            if data.get(key):
                lines.append(f"{key}: {data[key]}")
        return "\n".join(lines) if lines else "No chemical data available"

    def _format_regulatory(self, statuses: list[dict]) -> str:
        if not statuses:
            return "No regulatory data available for this chemical."
        lines = []
        for s in statuses:
            line = f"- {s.get('list_name', 'Unknown')}: {s.get('status', 'N/A')}"
            if s.get("classification"):
                line += f" (Classification: {s['classification']})"
            lines.append(line)
        return "\n".join(lines)
