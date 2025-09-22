from fastapi import FastAPI

from .config import get_settings
from .routers import alerts, compliance, ocr, onboarding, ops, risk


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.include_router(ocr.router)
    app.include_router(risk.router)
    app.include_router(compliance.router)
    app.include_router(onboarding.router)
    app.include_router(alerts.router)
    app.include_router(ops.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
