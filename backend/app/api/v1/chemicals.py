"""Chemical/ingredient API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/chemicals", tags=["chemicals"])


class ChemicalResponse(BaseModel):
    id: str
    dtxsid: str | None = None
    cas_number: str | None = None
    preferred_name: str
    inci_name: str | None = None
    molecular_formula: str | None = None
    molecular_weight: float | None = None
    description: str | None = None
    hazard_data: dict = {}
    regulatory_statuses: list[dict] = []


class ChemicalProductsResponse(BaseModel):
    chemical_id: str
    chemical_name: str
    products: list[dict]
    total: int


@router.get("/{chemical_id}")
async def get_chemical(chemical_id: str) -> ChemicalResponse:
    """Get chemical profile with all regulatory data."""
    raise HTTPException(status_code=404, detail="Chemical not found")


@router.get("/{chemical_id}/products")
async def get_chemical_products(chemical_id: str) -> ChemicalProductsResponse:
    """Get products containing this chemical."""
    raise HTTPException(status_code=404, detail="Chemical not found")


@router.get("/{chemical_id}/regulatory")
async def get_chemical_regulatory(chemical_id: str) -> list[dict]:
    """Get regulatory status across all lists."""
    raise HTTPException(status_code=404, detail="Chemical not found")
