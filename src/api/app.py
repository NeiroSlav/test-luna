import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.exceptions import setup_error_handlers
from api.routers.activity import activity_router
from api.routers.building import building_router
from api.routers.org import org_router
from infra.sql import fill_db, run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Миграция alembic при старте"""
    loop = asyncio.get_event_loop()
    loop.run_in_executor(None, run_migrations)
    await fill_db()

    yield


def create_app() -> FastAPI:
    """Инициализация FastApi приложения"""

    app = FastAPI(
        title="Organization App",
        lifespan=lifespan,
    )

    # Подключение обработки ошибок
    setup_error_handlers(app)

    # Подключение роутеров
    app.include_router(org_router)
    app.include_router(building_router)
    app.include_router(activity_router)

    return app
