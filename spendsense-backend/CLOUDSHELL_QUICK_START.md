# Quick Start: Run Migration in CloudShell

## Easiest Method: Direct Python Script

### Step 1: Open AWS CloudShell
- Go to: https://console.aws.amazon.com
- Click the CloudShell icon (top navigation bar)
- Wait for it to initialize (~30 seconds)

### Step 2: Upload and Run Script

**Option A: Upload the script file**
1. Click Actions menu (three dots) → "Upload file"
2. Upload: `spendsense-backend/scripts/run_migration_direct.py`
3. Run:
```bash
pip install sqlalchemy psycopg2-binary boto3
python3 run_migration_direct.py
```

**Option B: Copy-paste the script content**
1. Open `spendsense-backend/scripts/run_migration_direct.py` in your editor
2. Copy the entire file
3. In CloudShell, run:
```bash
cat > run_migration.py << 'SCRIPTEOF'
# Paste the entire script content here
SCRIPTEOF

# Install dependencies
pip install sqlalchemy psycopg2-binary boto3

# Run the script
python3 run_migration.py
```

## Alternative: Using Alembic (Full Setup)

If you want to use Alembic instead, follow these steps:

### Step 1: Open CloudShell

### Step 2: Copy and Paste These Commands

```bash
# Get the migration file content (you'll paste this into a file)
cat > ~/migration_file.py << 'MIGRATIONEOF'
```

Then paste the entire content of `alembic/versions/84631dd483c_initial_schema.py` here, followed by:

```bash
MIGRATIONEOF

# Create working directory
mkdir -p ~/migration/alembic/versions
cd ~/migration

# Move migration file to correct location
mv ~/migration_file.py alembic/versions/84631dd483c_initial_schema.py

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install sqlalchemy psycopg2-binary alembic boto3 python-dotenv

# Create minimal alembic.ini
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

# Create alembic/env.py
cat > alembic/env.py << 'ENVEOF'
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL not set")
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = None

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
ENVEOF

# Create alembic/script.py.mako
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

# Get database connection string
export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id spendsense/database/connection --query SecretString --output text | jq -r '.connection_string')

# Test connection
python3 -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); conn = engine.connect(); print('✅ Connection successful!'); conn.close()"

# Run migration
alembic upgrade head

# Verify tables
python3 -c "from sqlalchemy import create_engine, inspect; engine = create_engine('$DATABASE_URL'); inspector = inspect(engine); tables = inspector.get_table_names(); print(f'\n✅ Tables created: {len(tables)}'); [print(f'   - {t}') for t in sorted(tables)]"
```

## What This Does

1. Creates the migration file
2. Sets up Alembic configuration
3. Installs dependencies
4. Gets database connection from Secrets Manager
5. Applies the migration
6. Verifies all 10 tables were created

## Expected Result

You should see:
```
✅ Connection successful!
INFO  [alembic.runtime.migration] Running upgrade  -> 84631dd483c, Initial schema

✅ Tables created: 10
   - accounts
   - alembic_version
   - chat_logs
   - computed_features
   - consent_records
   - decision_traces
   - operator_actions
   - persona_assignments
   - profiles
   - recommendations
   - transactions
```

