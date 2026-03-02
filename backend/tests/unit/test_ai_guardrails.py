"""Tests for AI output guardrails."""

import pytest

from app.core.ai.guardrails import AIGuardrails


@pytest.fixture
def guardrails():
    return AIGuardrails()


class TestMedicalAdvice:
    def test_detects_stop_using(self, guardrails):
        text = "You should stop using this product immediately."
        issues = guardrails.check_medical_advice(text)
        assert len(issues) > 0

    def test_detects_consult_doctor(self, guardrails):
        text = "We recommend that you consult your doctor about this ingredient."
        issues = guardrails.check_medical_advice(text)
        assert len(issues) > 0

    def test_detects_will_cause_cancer(self, guardrails):
        text = "This chemical will cause cancer if used regularly."
        issues = guardrails.check_medical_advice(text)
        assert len(issues) > 0

    def test_detects_definitely_safe(self, guardrails):
        text = "This product is definitely safe for daily use."
        issues = guardrails.check_medical_advice(text)
        assert len(issues) > 0

    def test_allows_balanced_language(self, guardrails):
        text = (
            "According to IARC, this chemical is classified as Group 2B "
            "(possibly carcinogenic). However, the concentration in this "
            "product is typical for cosmetic formulations. Limited data is "
            "available on long-term effects at these exposure levels."
        )
        issues = guardrails.check_medical_advice(text)
        assert len(issues) == 0

    def test_allows_factual_statements(self, guardrails):
        text = (
            "Sodium Lauryl Sulfate is listed as an irritant. "
            "It is commonly used in shampoos as a surfactant."
        )
        issues = guardrails.check_medical_advice(text)
        assert len(issues) == 0


class TestScoreClaims:
    def test_detects_wrong_score(self, guardrails):
        text = "This product received a score of 75 out of 100."
        issues = guardrails.check_score_claims(text, actual_score=30.0)
        assert len(issues) > 0

    def test_allows_correct_score(self, guardrails):
        text = "This product received a score of 30 out of 100."
        issues = guardrails.check_score_claims(text, actual_score=30.0)
        assert len(issues) == 0

    def test_detects_wrong_grade(self, guardrails):
        text = "The product earned a grade of A."
        issues = guardrails.check_score_claims(
            text, actual_score=75.0, actual_grade="D"
        )
        assert len(issues) > 0

    def test_allows_correct_grade(self, guardrails):
        text = "The product earned a grade of B."
        issues = guardrails.check_score_claims(
            text, actual_score=30.0, actual_grade="B"
        )
        assert len(issues) == 0


class TestSourceCitations:
    def test_detects_citations(self, guardrails):
        text = (
            "According to IARC, this chemical is classified as Group 1. "
            "It is also listed on California Proposition 65."
        )
        assert guardrails.check_source_citations(text) is True

    def test_no_citations(self, guardrails):
        text = "This chemical is dangerous and should be avoided."
        assert guardrails.check_source_citations(text) is False


class TestFullValidation:
    def test_valid_explanation_passes(self, guardrails):
        text = (
            "Based on EPA data, this product contains well-studied ingredients. "
            "According to IARC classifications, none of the identified ingredients "
            "are classified as carcinogenic to humans. The overall safety profile "
            "suggests low concern for typical use."
        )
        is_valid, issues = guardrails.validate(
            text,
            known_chemicals={"Water", "Glycerin"},
            actual_score=15.0,
            actual_grade="A",
        )
        assert is_valid
        assert len(issues) == 0

    def test_medical_advice_fails_validation(self, guardrails):
        text = "You should stop using this product and consult your doctor."
        is_valid, issues = guardrails.validate(text)
        assert not is_valid
        assert len(issues) > 0
