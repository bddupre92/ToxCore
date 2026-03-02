from fastapi import APIRouter

from app.api.v1.ai_explain import router as ai_explain_router
from app.api.v1.chemicals import router as chemicals_router
from app.api.v1.compare import router as compare_router
from app.api.v1.health import router as health_router
from app.api.v1.products import router as products_router
from app.api.v1.search import router as search_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(products_router)
api_router.include_router(search_router)
api_router.include_router(chemicals_router)
api_router.include_router(compare_router)
api_router.include_router(ai_explain_router)
