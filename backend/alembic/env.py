import asyncio
from logging.config import fileConfig
from dotenv import load_dotenv

load_dotenv() # Force load .env before settings
import sys
import os

# Append backend directory to sys.path to allow imports from app
import sys
import os

# If running from backend directory, add Parent to path? No, 'app' is inside backend.
# We need 'backend' to be the root of import if we assume 'app' is top level package...
# Actually, the structure is:
# backend/
#   app/
#     main.py
# So if we run inside backend, we can import app.
# If we run from project root, we need to add backend.

current_dir = os.getcwd()
if current_dir.endswith("backend"):
    sys.path.append(current_dir)
else:
    sys.path.append(os.path.join(current_dir, 'backend'))

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.core.config import settings
from app.core.database import Base
from app.models import * # Import all models to ensure they are registered

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

# Override sqlalchemy.url with value from settings
config.set_main_option("sqlalchemy.url", str(settings.SQLALCHEMY_DATABASE_URI))

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
