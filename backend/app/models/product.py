from pydantic import BaseModel

from app.models.chemical import Chemical, RegulatoryStatus


class Product(BaseModel):
    id: str
    name: str
    brand: str | None = None
    category: str | None = None
    raw_ingredients: str | None = None


class IngredientWithChemical(BaseModel):
    raw_name: str
    resolved_name: str | None = None
    position: int
    confidence: float = 1.0
    chemical: Chemical | None = None
    regulatory_statuses: list[RegulatoryStatus] = []
