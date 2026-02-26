from typing import AsyncGenerator

from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from settings import get_settings

Base = declarative_base()


# Глобальный engine для всего приложения
engine = create_async_engine(get_settings().database_url)
PostgresSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession]:
    """
    Генератор асинхронной сессии.
    Коммитит сессию после выполнения процедур, или откатывает при ошибках.
    Гарантирует закрытие сессии по завершении.
    """
    async with PostgresSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def run_migrations():
    """Запуск миграции alembic"""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", get_settings().database_url)
    command.upgrade(alembic_cfg, "head")
