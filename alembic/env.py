import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlmodel import SQLModel
from app.logging_config.logger import logger
import sys

# Add the project root to the sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db import sync_engine
from app.config import get_settings
from app.models import *

# Disable default logging and configure Loguru
logger.remove()
logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")

# Alembic config
config = context.config
settings = get_settings()

# Ensure Alembic config URL matches settings
if config.get_main_option("sqlalchemy.url") != settings.sync_database_url:
    logger.warning("Alembic config URL does not match settings! Using settings URL")
    config.set_main_option("sqlalchemy.url", settings.sync_database_url)

# Add migration-specific logging
logger.add(
    "logs/migrations.log",
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    level="INFO"
)
    
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    logger.info("Running migrations in 'offline' mode")
    url = settings.sync_database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    logger.info("Running migrations in 'online' mode")
    with sync_engine.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
