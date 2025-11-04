"""Alembic environment configuration"""

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import all models to ensure they are registered with Base
from app.models import Base  # noqa: F401
from app.models.account import Account  # noqa: F401
from app.models.chat_log import ChatLog  # noqa: F401
from app.models.computed_feature import ComputedFeature  # noqa: F401
from app.models.consent import ConsentRecord  # noqa: F401
from app.models.decision_trace import DecisionTrace  # noqa: F401
from app.models.operator_action import OperatorAction  # noqa: F401
from app.models.persona import PersonaAssignment  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.recommendation import Recommendation  # noqa: F401
from app.models.transaction import Transaction  # noqa: F401
from app.database.connection import get_db_url

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url from environment variable
# Use set_main_option with raw=False to avoid interpolation issues with special characters
database_url = get_db_url()
# Set directly on the config object to avoid ConfigParser interpolation issues
config.attributes['sqlalchemy.url'] = database_url

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Use the database URL directly instead of from config
    url = get_db_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Use the database URL directly instead of from config to avoid interpolation issues
    database_url = get_db_url()
    connectable = engine_from_config(
        {"sqlalchemy.url": database_url},
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

