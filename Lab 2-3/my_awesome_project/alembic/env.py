from logging.config import fileConfig
import os

from alembic import context
from app.models.base import Base
from sqlalchemy import engine_from_config, pool

config = context.config

# Allow overriding the URL via environment variable. If the project uses
# async driver (postgresql+asyncpg) in `DATABASE_URL`, Alembic (sync engine)
# cannot use the async driver string, so strip the `+asyncpg` part for
# migrations.
env_db_url = os.environ.get("ALEMBIC_DATABASE_URL") or os.environ.get("DATABASE_URL")
if env_db_url:
    # If using async driver, convert to sync driver for alembic
    if env_db_url.startswith("postgresql+asyncpg://"):
        sync_url = env_db_url.replace("+asyncpg", "")
    else:
        sync_url = env_db_url
    config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
