from fastapi import FastAPI

from .config import get_settings
from .routers import account, banking, kyc, onboarding, support


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.include_router(account.router)
    app.include_router(kyc.router)
    app.include_router(banking.router)
    app.include_router(onboarding.router)
    app.include_router(support.router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
