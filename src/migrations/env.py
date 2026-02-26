import asyncio

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from infra.sql import Base
from settings import get_settings

target_metadata = Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)


async def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section) or {},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
                include_schemas=True,
            )
        )
        await connection.run_sync(lambda conn: context.run_migrations())
        await connection.commit()


asyncio.run(run_migrations_online())
