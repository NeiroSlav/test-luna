import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers.activity import activity_router
from api.routers.building import building_router
from api.routers.org import org_router
from infra.sql import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Миграция alembic при старте"""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_migrations)

    yield


def create_app() -> FastAPI:
    """Инициализация FastApi приложения"""

    app = FastAPI(
        title="Organization App",
        lifespan=lifespan,
    )

    # Подключение роутеров
    app.include_router(org_router)
    app.include_router(building_router)
    app.include_router(activity_router)

    return app
