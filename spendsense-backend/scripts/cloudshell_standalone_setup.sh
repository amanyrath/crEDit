#!/bin/bash
# Standalone CloudShell setup - doesn't require Git
# Just upload the migration file and this script to CloudShell

set -e

echo "🚀 Standalone CloudShell Migration Setup"
echo "=========================================="
echo ""

# Create working directory
WORK_DIR="$HOME/migration"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

echo "📁 Created working directory: $WORK_DIR"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip -q
pip install sqlalchemy psycopg2-binary alembic boto3 python-dotenv -q

echo "✅ Dependencies installed"
echo ""

# Set AWS region
export AWS_REGION=${AWS_REGION:-us-east-1}

# Get database connection string
echo "🔑 Retrieving database connection string from Secrets Manager..."
export DATABASE_URL=$(aws secretsmanager get-secret-value \
    --secret-id spendsense/database/connection \
    --query SecretString \
    --output text | jq -r '.connection_string')

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: Could not retrieve DATABASE_URL from Secrets Manager"
    exit 1
fi

echo "✅ Connection string retrieved"
echo ""

# Create minimal alembic structure
echo "📂 Setting up Alembic structure..."
mkdir -p alembic/versions

# Create alembic.ini
cat > alembic.ini << 'EOF'
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
EOF

# Create alembic/env.py that uses DATABASE_URL from environment
cat > alembic/env.py << 'ENVEOF'
"""Alembic environment configuration"""
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable not set")

config.set_main_option("sqlalchemy.url", database_url)

# No models needed for standalone migration
target_metadata = None

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
ENVEOF

# Create script.py.mako
mkdir -p alembic
cat > alembic/script.py.mako << 'EOF'
"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}

def upgrade() -> None:
    ${upgrades if upgrades else "pass"}

def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
EOF

echo "✅ Alembic structure created"
echo ""
echo "📋 Next steps:"
echo "   1. Upload the migration file to: $WORK_DIR/alembic/versions/"
echo "      File name: 84631dd483c_initial_schema.py"
echo "   2. Or paste the migration file content directly"
echo ""
echo "   Once the migration file is in place, run:"
echo "   cd $WORK_DIR"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""

