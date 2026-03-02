"""Search API endpoint."""

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(tags=["search"])


class SearchResult(BaseModel):
    id: str
    name: str
    brand: str | None = None
    category: str | None = None
    image_url: str | None = None
    overall_score: float | None = None
    grade: str | None = None
    rank: float = 0.0


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    page: int
    limit: int


@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=1, max_length=200, description="Search query"),
    category: str | None = Query(None, description="Filter by category"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
) -> SearchResponse:
    """
    Full-text search for products.

    Uses PostgreSQL tsvector for relevance ranking.
    """
    # TODO: Replace with actual database query using search_products() function
    return SearchResponse(results=[], total=0, page=page, limit=limit)
