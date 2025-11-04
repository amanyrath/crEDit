# Run Database Migration in AWS CloudShell

Since the RDS database is in a private subnet (not publicly accessible), we need to run the migration from within AWS. AWS CloudShell is the easiest option.

## Prerequisites

- AWS CloudShell access (available in AWS Console)
- Repository access (GitHub or upload files manually)

## Quick Start (Recommended)

### Step 1: Open AWS CloudShell
- Go to AWS Console (https://console.aws.amazon.com)
- Click the CloudShell icon in the top navigation bar
- Wait for CloudShell to initialize (takes ~30 seconds)

### Step 2: Upload Migration File
You have two options:

**Option A: If you have Git repository:**
```bash
cd ~
git clone <your-repo-url> crEDit
cd crEDit/spendsense-backend
```

**Option B: Upload files directly (no Git needed):**
1. In CloudShell, click the Actions menu (three dots) → "Upload file"
2. Upload: `alembic/versions/84631dd483c_initial_schema.py`
3. Upload: `requirements.txt`
4. Or run the standalone setup script first

### Step 3: Run Migration

**If you cloned the full repo:**
```bash
cd ~/crEDit/spendsense-backend
source venv/bin/activate  # if venv exists, otherwise create it
pip install -r requirements.txt
export DATABASE_URL=$(aws secretsmanager get-secret-value --secret-id spendsense/database/connection --query SecretString --output text | jq -r '.connection_string')
alembic upgrade head
```

**If you uploaded files manually:**
```bash
# First, run the standalone setup
bash <(curl -s https://raw.githubusercontent.com/YOUR_REPO/...)  # or upload the script
# Then upload the migration file and run:
alembic upgrade head
```

## Option 1: Full Repository Setup (Recommended)

### Step 1: Open CloudShell
- Go to AWS Console
- Click the CloudShell icon (top navigation bar)

### Step 2: Clone or Upload Code
```bash
# Option A: Clone from Git
cd ~
git clone <your-repo-url> crEDit
cd crEDit/spendsense-backend

# Option B: Upload files manually via CloudShell upload feature
```

### Step 3: Set Up Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Get Database Connection
```bash
# CloudShell automatically has AWS credentials configured
export DATABASE_URL=$(aws secretsmanager get-secret-value \
    --secret-id spendsense/database/connection \
    --query SecretString \
    --output text | jq -r '.connection_string')

echo "Connection string retrieved: ${DATABASE_URL:0:50}..."
```

### Step 5: Test Connection
```bash
python3 -c "
from app.database.connection import get_engine
engine = get_engine()
conn = engine.connect()
print('✅ Database connection successful!')
conn.close()
"
```

### Step 6: Apply Migration
```bash
alembic upgrade head
```

### Step 7: Verify Tables Created
```bash
python3 -c "
from app.database.connection import get_engine
from sqlalchemy import inspect
engine = get_engine()
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'\n✅ Schema created successfully!')
print(f'Total tables: {len(tables)}\n')
for table in sorted(tables):
    print(f'  - {table}')
"
```

## Expected Output

After running the migration, you should see:
- All 10 tables created:
  - accounts
  - chat_logs
  - computed_features
  - consent_records
  - decision_traces
  - operator_actions
  - persona_assignments
  - profiles
  - recommendations
  - transactions

## Troubleshooting

**Issue: "jq command not found"**
```bash
# CloudShell should have jq, but if not:
sudo yum install jq -y
```

**Issue: "Connection timeout"**
- CloudShell IPs are dynamic
- The security group already allows Lambda access
- CloudShell should be able to connect if it's in the same region

**Issue: "Module not found"**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

**Issue: "Migration file not found"**
```bash
# Check migration file exists
ls -la alembic/versions/
# Should see: 84631dd483c_initial_schema.py
```

## After Migration

Once the migration is complete:
1. Verify all tables exist
2. Check that indexes were created
3. Verify foreign key constraints
4. Update Story 1.4 status to "done"

## Clean Up

After migration, you can:
- Keep CloudShell session for future migrations
- Or close it (your work is saved in the repository)

