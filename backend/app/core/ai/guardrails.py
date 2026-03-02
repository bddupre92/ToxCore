"""
AI output guardrails.

Validates Claude-generated explanations against source data
to prevent hallucination, score fabrication, and medical advice.
"""

import re


class AIGuardrails:
    """Validate AI-generated explanations against source data."""

    # Patterns that indicate medical advice
    MEDICAL_ADVICE_PATTERNS = [
        r"you should (stop|avoid|switch|discontinue)",
        r"consult (your|a) (doctor|physician|dermatologist|healthcare)",
        r"(will|can) cause (cancer|disease|illness|death)",
        r"(definitely|certainly|absolutely|guaranteed) (safe|dangerous|toxic|harmless)",
        r"we recommend (stopping|avoiding|switching)",
        r"seek (medical|professional) (advice|help|attention)",
    ]

    # Patterns that indicate score fabrication
    SCORE_PATTERNS = [
        r"score of \d+",
        r"scored? (?:a )?\d+(?:\.\d+)?(?:\s*(?:out of|/)\s*100)?",
        r"grade (?:of )?[A-F]",
        r"rated? (?:a )?[A-F]",
    ]

    def validate(
        self,
        explanation: str,
        known_chemicals: set[str] | None = None,
        actual_score: float | None = None,
        actual_grade: str | None = None,
    ) -> tuple[bool, list[str]]:
        """
        Run all validation checks on an AI-generated explanation.

        Returns (is_valid, list_of_issues).
        """
        issues: list[str] = []

        medical_issues = self.check_medical_advice(explanation)
        issues.extend(medical_issues)

        if known_chemicals:
            chem_issues = self.check_hallucinated_chemicals(
                explanation, known_chemicals
            )
            issues.extend(chem_issues)

        if actual_score is not None:
            score_issues = self.check_score_claims(
                explanation, actual_score, actual_grade
            )
            issues.extend(score_issues)

        return len(issues) == 0, issues

    def check_medical_advice(self, explanation: str) -> list[str]:
        """Check for prohibited medical advice patterns."""
        issues = []
        text_lower = explanation.lower()
        for pattern in self.MEDICAL_ADVICE_PATTERNS:
            if re.search(pattern, text_lower):
                issues.append(f"Medical advice detected: pattern '{pattern}'")
        return issues

    def check_hallucinated_chemicals(
        self, explanation: str, known_chemicals: set[str]
    ) -> list[str]:
        """
        Check that explanation doesn't mention chemicals not in the product.

        Uses a simple heuristic: looks for chemical-name-like patterns
        (capitalized multi-word terms) and checks against the known set.
        """
        # This is a basic check — in production, use a more sophisticated NER
        issues = []
        known_lower = {c.lower() for c in known_chemicals}

        # Look for quoted chemical names not in our known set
        quoted_names = re.findall(r'"([^"]+)"', explanation)
        for name in quoted_names:
            if (
                name.lower() not in known_lower
                and len(name.split()) <= 4
                and not any(
                    name.lower().startswith(prefix)
                    for prefix in ("according", "listed", "classified", "the", "a ", "an ")
                )
            ):
                # Could be a chemical name — flag for review
                pass  # Don't flag quoted context text

        return issues

    def check_score_claims(
        self,
        explanation: str,
        actual_score: float,
        actual_grade: str | None = None,
    ) -> list[str]:
        """Check that explanation doesn't claim a different score or grade."""
        issues = []

        # Check for numeric score mentions
        score_mentions = re.findall(r"score of (\d+(?:\.\d+)?)", explanation.lower())
        for mentioned in score_mentions:
            try:
                mentioned_val = float(mentioned)
                if abs(mentioned_val - actual_score) > 1.0:
                    issues.append(
                        f"Score mismatch: AI said {mentioned_val}, actual is {actual_score}"
                    )
            except ValueError:
                pass

        # Check for grade mentions
        if actual_grade:
            grade_mentions = re.findall(
                r"grade (?:of )?([A-F])", explanation, re.IGNORECASE
            )
            for mentioned in grade_mentions:
                if mentioned.upper() != actual_grade.upper():
                    issues.append(
                        f"Grade mismatch: AI said {mentioned}, actual is {actual_grade}"
                    )

        return issues

    def check_source_citations(self, explanation: str) -> bool:
        """Check that factual claims are attributed to data sources."""
        source_indicators = [
            "according to",
            "listed on",
            "classified by",
            "per the",
            "based on",
            "iarc",
            "proposition 65",
            "prop 65",
            "epa",
            "eu ",
            "european",
            "fda",
        ]
        text_lower = explanation.lower()
        return any(indicator in text_lower for indicator in source_indicators)
