#!/bin/bash
# Script to run database migration in AWS CloudShell
# This script sets up the environment and runs Alembic migration

set -e

echo "🚀 Setting up database migration in AWS CloudShell..."

# Check if we're in CloudShell (optional check)
if [ -z "$AWS_EXECUTION_ENV" ]; then
    echo "⚠️  Warning: This script is designed for AWS CloudShell"
    echo "   You can still run it, but make sure AWS credentials are configured"
fi

# Get repository URL (adjust if needed)
REPO_URL="https://github.com/YOUR_USERNAME/crEDit.git"  # Update this with your repo URL
WORK_DIR="$HOME/crEDit"

# Clone or update repository
if [ -d "$WORK_DIR" ]; then
    echo "📦 Updating existing repository..."
    cd "$WORK_DIR"
    git pull
else
    echo "📦 Cloning repository..."
    git clone "$REPO_URL" "$WORK_DIR"
    cd "$WORK_DIR"
fi

# Navigate to backend directory
cd "$WORK_DIR/spendsense-backend"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Set AWS region (CloudShell usually has this, but just in case)
export AWS_REGION=${AWS_REGION:-us-east-1}

# Get database connection string from Secrets Manager
echo "🔑 Retrieving database connection string from Secrets Manager..."
export DATABASE_URL=$(aws secretsmanager get-secret-value \
    --secret-id spendsense/database/connection \
    --query SecretString \
    --output text | jq -r '.connection_string')

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: Could not retrieve DATABASE_URL from Secrets Manager"
    exit 1
fi

echo "✅ Database connection string retrieved"
echo ""

# Test connection
echo "🧪 Testing database connection..."
python3 -c "
from app.database.connection import get_engine
engine = get_engine()
conn = engine.connect()
print('✅ Database connection successful!')
conn.close()
" || {
    echo "❌ Database connection failed!"
    exit 1
}

# Check current migration status
echo ""
echo "📊 Current migration status:"
alembic current || echo "No migrations applied yet"

# Apply migrations
echo ""
echo "🔄 Applying migrations..."
alembic upgrade head

# Verify tables were created
echo ""
echo "✅ Verifying schema..."
python3 -c "
from app.database.connection import get_engine
from sqlalchemy import inspect
engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'✅ Tables created: {len(tables)}')
for table in sorted(tables):
    print(f'   - {table}')
"

echo ""
echo "🎉 Migration completed successfully!"

