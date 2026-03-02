from pydantic import BaseModel, Field


class HazardScore(BaseModel):
    """Hazard score for a single chemical."""

    total: float = Field(ge=0, le=100)
    regulatory_ban: float = Field(ge=0, le=100)
    carcinogenicity: float = Field(ge=0, le=100)
    endocrine_disruption: float = Field(ge=0, le=100)
    sensitization: float = Field(ge=0, le=100)
    acute_toxicity: float = Field(ge=0, le=100)


class IngredientScoreDetail(BaseModel):
    """Score breakdown for a single ingredient."""

    raw_name: str
    position: int
    resolved: bool
    hazard_score: float
    position_weight: float
    contributing_factors: list[str] = []


class ProductScore(BaseModel):
    """Complete product score with breakdown."""

    overall_score: float = Field(ge=0, le=100)
    hazard_score: float = Field(ge=0, le=100)
    exposure_score: float = Field(ge=0, le=100)
    transparency_score: float = Field(ge=0, le=100)
    grade: str
    scoring_version: str
    ingredient_details: list[IngredientScoreDetail] = []
