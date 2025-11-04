# Running Migration in AWS CloudShell

## Quick Start

1. **Open AWS CloudShell**
   - Go to AWS Console
   - Click the CloudShell icon in the top navigation bar
   - Wait for CloudShell to initialize

2. **Clone the repository**
   ```bash
   cd ~
   git clone https://github.com/YOUR_USERNAME/crEDit.git
   # OR if you haven't pushed to GitHub yet, you can upload the migration file
   ```

3. **Navigate to backend directory**
   ```bash
   cd crEDit/spendsense-backend
   ```

4. **Set up Python environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Get database connection string**
   ```bash
   export DATABASE_URL=$(aws secretsmanager get-secret-value \
       --secret-id spendsense/database/connection \
       --query SecretString \
       --output text | jq -r '.connection_string')
   ```

6. **Test connection**
   ```bash
   python3 -c "from app.database.connection import get_engine; engine = get_engine(); conn = engine.connect(); print('✅ Connection successful!'); conn.close()"
   ```

7. **Apply migration**
   ```bash
   alembic upgrade head
   ```

8. **Verify tables**
   ```bash
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
   ```

## Alternative: Upload Migration File Manually

If you can't clone the repo, you can upload just the migration file:

1. **Upload migration file to CloudShell**
   - In CloudShell, click the Actions menu (three dots)
   - Select "Upload file"
   - Upload: `alembic/versions/84631dd483c_initial_schema.py`

2. **Create minimal setup**
   ```bash
   mkdir -p ~/migration
   cd ~/migration
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install only what's needed
   pip install sqlalchemy psycopg2-binary alembic boto3 python-dotenv
   ```

3. **Create minimal alembic setup**
   ```bash
   mkdir -p alembic/versions
   # Copy your migration file here
   ```

4. **Get connection string and run migration**
   ```bash
   export DATABASE_URL=$(aws secretsmanager get-secret-value \
       --secret-id spendsense/database/connection \
       --query SecretString \
       --output text | jq -r '.connection_string')
   
   alembic upgrade head
   ```

## Troubleshooting

- **If jq is not installed**: CloudShell usually has it, but if not: `sudo yum install jq -y`
- **If connection fails**: Check that the security group allows CloudShell IPs (CloudShell IPs are dynamic)
- **If migration file not found**: Make sure you're in the correct directory with `alembic/versions/` folder

