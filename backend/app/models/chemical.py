from pydantic import BaseModel


class Chemical(BaseModel):
    id: str
    dtxsid: str | None = None
    cas_number: str | None = None
    preferred_name: str
    inci_name: str | None = None
    molecular_formula: str | None = None
    molecular_weight: float | None = None
    description: str | None = None
    hazard_data: dict = {}


class RegulatoryStatus(BaseModel):
    list_name: str
    status: str | None = None
    classification: str | None = None
    details: dict = {}
