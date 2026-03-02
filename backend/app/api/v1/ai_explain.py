"""AI explanation API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/explain", tags=["ai-explain"])


class ExplanationResponse(BaseModel):
    entity_type: str
    entity_id: str
    explanation: str
    model_version: str | None = None
    cached: bool = False


@router.post("/product/{product_id}")
async def explain_product(product_id: str) -> ExplanationResponse:
    """
    Generate AI explanation for a product's safety profile.

    Uses Claude to translate pre-computed scores into consumer-friendly language.
    Rate-limited per user. Returns cached explanation if available.
    """
    # TODO: Implement with Claude integration in Phase 6
    raise HTTPException(status_code=503, detail="AI explanations not yet available")


@router.post("/chemical/{chemical_id}")
async def explain_chemical(chemical_id: str) -> ExplanationResponse:
    """
    Generate AI explanation for a chemical's safety profile.

    Uses Claude to explain regulatory data in plain language.
    Rate-limited per user. Returns cached explanation if available.
    """
    # TODO: Implement with Claude integration in Phase 6
    raise HTTPException(status_code=503, detail="AI explanations not yet available")
