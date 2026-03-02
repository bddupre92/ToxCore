from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title="ToxScore API",
        description="Chemical safety scoring for consumer products",
        version="1.0.0",
        docs_url="/api/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/api/redoc" if settings.ENVIRONMENT != "production" else None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_app()
