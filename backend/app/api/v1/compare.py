"""Product comparison API endpoint."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(tags=["compare"])


class CompareRequest(BaseModel):
    product_ids: list[str] = Field(
        ..., min_length=2, max_length=3, description="2-3 product IDs to compare"
    )


class ComparedProduct(BaseModel):
    id: str
    name: str
    brand: str | None = None
    category: str | None = None
    image_url: str | None = None
    overall_score: float | None = None
    hazard_score: float | None = None
    exposure_score: float | None = None
    transparency_score: float | None = None
    grade: str | None = None
    flagged_ingredients: list[dict] = []


class CompareResponse(BaseModel):
    products: list[ComparedProduct]


@router.post("/compare")
async def compare_products(request: CompareRequest) -> CompareResponse:
    """
    Compare 2-3 products side-by-side.

    Returns scores and flagged ingredients for each product.
    """
    if len(request.product_ids) != len(set(request.product_ids)):
        raise HTTPException(status_code=400, detail="Duplicate product IDs")

    # TODO: Replace with actual database query
    raise HTTPException(status_code=404, detail="Products not found")
