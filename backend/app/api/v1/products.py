"""Product API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/products", tags=["products"])


class ProductResponse(BaseModel):
    id: str
    name: str
    brand: str | None = None
    category: str | None = None
    image_url: str | None = None
    raw_ingredients: str | None = None
    barcode: str | None = None
    score: dict | None = None
    ingredients: list[dict] = []


class ProductScoreResponse(BaseModel):
    product_id: str
    overall_score: float
    hazard_score: float
    exposure_score: float
    transparency_score: float
    grade: str
    scoring_version: str
    score_details: dict = {}


@router.get("/{product_id}")
async def get_product(product_id: str) -> ProductResponse:
    """Get product detail with score and ingredients."""
    # TODO: Replace with actual database query in Phase 5 integration
    raise HTTPException(status_code=404, detail="Product not found")


@router.get("/{product_id}/score")
async def get_product_score(product_id: str) -> ProductScoreResponse:
    """Get detailed score breakdown for a product."""
    raise HTTPException(status_code=404, detail="Product score not found")


@router.get("/{product_id}/ingredients")
async def get_product_ingredients(product_id: str) -> list[dict]:
    """Get resolved ingredients with chemical data."""
    raise HTTPException(status_code=404, detail="Product not found")
