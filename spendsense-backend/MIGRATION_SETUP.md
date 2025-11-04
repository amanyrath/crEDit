# Database Migration Setup Guide

This guide explains how to set up and run database migrations for Story 1.4.

## Prerequisites

1. **Story 1.3 Complete**: RDS PostgreSQL database must be deployed and accessible
2. **AWS Credentials**: Configured locally for accessing Secrets Manager
3. **Python Environment**: Virtual environment activated with dependencies installed

## Step 1: Install Dependencies

Make sure all database dependencies are installed:

```bash
cd spendsense-backend
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

This will install:
- SQLAlchemy 2.0+
- psycopg2-binary (PostgreSQL driver)
- Alembic (migration tool)

## Step 2: Configure Database Connection

You have two options for connecting to the database:

### Option A: Environment Variable (Recommended for Local Development)

Set the `DATABASE_URL` environment variable:

```bash
# macOS/Linux
export DATABASE_URL="postgresql://username:password@host:5432/spendsense"

# Windows (PowerShell)
$env:DATABASE_URL="postgresql://username:password@host:5432/spendsense"
```

To get the connection string from Secrets Manager:

```bash
aws secretsmanager get-secret-value \
  --secret-id spendsense/database/connection \
  --query SecretString \
  --output text | jq -r '.connection_string'
```

### Option B: Secrets Manager (Automatic)

If `DATABASE_URL` is not set, the code will automatically retrieve it from AWS Secrets Manager.

Make sure:
1. AWS credentials are configured (`aws configure`)
2. You have permission to access the secret: `spendsense/database/connection`

## Step 3: Configure Local Development Access

If connecting from your local machine, you may need to add your IP to the database security group:

```bash
# Get your public IP
MY_IP=$(curl -s https://checkip.amazonaws.com)

# Get the security group ID from AWS Console or:
# aws ec2 describe-security-groups --filters "Name=group-name,Values=DatabaseSecurityGroup*"

# Add ingress rule (replace SECURITY_GROUP_ID)
aws ec2 authorize-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp \
  --port 5432 \
  --cidr $MY_IP/32 \
  --description "Temporary access for local development"
```

**Important:** Remove this rule when not developing locally for security.

## Step 4: Generate Initial Migration

Generate the migration script from your SQLAlchemy models:

```bash
cd spendsense-backend
alembic revision --autogenerate -m "Initial schema"
```

This will create a migration file in `alembic/versions/` with all table definitions, foreign keys, and indexes.

**Note:** Review the generated migration file to ensure it matches your requirements.

## Step 5: Apply Migration

Apply the migration to create all tables:

```bash
alembic upgrade head
```

This will:
- Create all 10 tables (profiles, consent_records, accounts, transactions, etc.)
- Create all foreign key constraints
- Create all indexes
- Set up the complete database schema

## Step 6: Verify Schema

Verify that all tables were created:

```bash
# Using psql
psql "$DATABASE_URL" -c "\dt"

# Or using Python
python -c "
from app.database.connection import get_engine
from sqlalchemy import inspect
engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()
print('Tables created:', tables)
print('Total tables:', len(tables))
"
```

Expected tables:
- profiles
- consent_records
- accounts
- transactions
- computed_features
- persona_assignments
- recommendations
- decision_traces
- chat_logs
- operator_actions

## Troubleshooting

### Connection Errors

**Error: "DATABASE_URL not found"**
- Make sure `DATABASE_URL` is set or AWS credentials are configured
- Verify the secret exists: `aws secretsmanager describe-secret --secret-id spendsense/database/connection`

**Error: "Connection refused" or "timeout"**
- Check that your IP is added to the security group
- Verify the database endpoint is correct
- Check that the database is in "available" state

### Migration Errors

**Error: "Target database is not up to date"**
- Check current migration status: `alembic current`
- Check migration history: `alembic history`
- If needed, downgrade and reapply: `alembic downgrade -1` then `alembic upgrade head`

**Error: "Table already exists"**
- The database may already have tables. Check: `alembic current`
- If migration wasn't tracked, you may need to stamp the database: `alembic stamp head`

## Migration Commands Reference

```bash
# Check current migration version
alembic current

# View migration history
alembic history

# Create a new migration (manual)
alembic revision -m "Description"

# Create a new migration (auto-generate from models)
alembic revision --autogenerate -m "Description"

# Apply all pending migrations
alembic upgrade head

# Apply next migration
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Stamp database with current version (without running migrations)
alembic stamp head
```

## Next Steps

After the schema is created:
1. Verify all acceptance criteria are met (Story 1.4)
2. Test database connections from application code
3. Proceed with Story 3.1 (Database Seeding Script) to add demo data

