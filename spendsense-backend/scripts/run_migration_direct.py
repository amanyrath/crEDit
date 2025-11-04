#!/usr/bin/env python3
"""
Direct database migration script - runs SQL directly without Alembic
Use this in AWS CloudShell when you can't use Alembic easily
"""

import os
import json
import boto3
from sqlalchemy import create_engine, text
from botocore.exceptions import ClientError

def get_db_url():
    """Get database URL from Secrets Manager"""
    try:
        secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
        response = secrets_client.get_secret_value(SecretId="spendsense/database/connection")
        secret_value = json.loads(response["SecretString"])
        
        if "connection_string" in secret_value:
            return secret_value["connection_string"]
        elif "host" in secret_value:
            # Construct from individual fields
            host = secret_value["host"]
            port = secret_value.get("port", "5432")
            database = secret_value.get("database", "spendsense")
            username = secret_value["username"]
            password = secret_value["password"]
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    except ClientError as e:
        print(f"Error retrieving secret: {e}")
        return None
    
    # Fallback to environment variable
    return os.getenv("DATABASE_URL")

def run_migration():
    """Run the database migration"""
    db_url = get_db_url()
    if not db_url:
        print("❌ Error: Could not get database URL")
        return False
    
    print("🔌 Connecting to database...")
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # Test connection
        result = conn.execute(text("SELECT 1"))
        print("✅ Database connection successful!")
        
        # Start transaction
        trans = conn.begin()
        try:
            print("\n🔄 Running migration...")
            
            # Enable UUID extension
            print("   - Enabling UUID extension...")
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            
            # Create profiles table
            print("   - Creating profiles table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id UUID PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    role VARCHAR(20) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE UNIQUE INDEX IF NOT EXISTS ix_profiles_email ON profiles(email);
            """))
            
            # Create consent_records table
            print("   - Creating consent_records table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS consent_records (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    granted_at TIMESTAMPTZ,
                    revoked_at TIMESTAMPTZ,
                    version VARCHAR(10) NOT NULL DEFAULT '1.0',
                    ip_address VARCHAR(45),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_consent_records_user_id ON consent_records(user_id);
            """))
            
            # Create accounts table
            print("   - Creating accounts table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    account_type VARCHAR(30) NOT NULL,
                    account_number_last4 VARCHAR(4),
                    balance NUMERIC(10,2),
                    "limit" NUMERIC(10,2),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_accounts_user_id ON accounts(user_id);
            """))
            
            # Create transactions table
            print("   - Creating transactions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
                    date DATE NOT NULL,
                    merchant VARCHAR(255) NOT NULL,
                    amount NUMERIC(10,2) NOT NULL,
                    category VARCHAR(100),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_transactions_user_id ON transactions(user_id);
                CREATE INDEX IF NOT EXISTS ix_transactions_account_id ON transactions(account_id);
                CREATE INDEX IF NOT EXISTS ix_transactions_date ON transactions(date);
                CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, date DESC);
            """))
            
            # Create computed_features table
            print("   - Creating computed_features table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS computed_features (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    time_window VARCHAR(10) NOT NULL,
                    signal_type VARCHAR(100) NOT NULL,
                    signal_value JSONB NOT NULL,
                    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_computed_features_user_id ON computed_features(user_id);
                CREATE INDEX IF NOT EXISTS ix_computed_features_signal_type ON computed_features(signal_type);
                CREATE INDEX IF NOT EXISTS idx_computed_features_user_window ON computed_features(user_id, time_window);
            """))
            
            # Create persona_assignments table
            print("   - Creating persona_assignments table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS persona_assignments (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    time_window VARCHAR(10) NOT NULL,
                    persona VARCHAR(50) NOT NULL,
                    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_persona_assignments_user_id ON persona_assignments(user_id);
                CREATE INDEX IF NOT EXISTS idx_persona_assignments_user_window ON persona_assignments(user_id, time_window);
            """))
            
            # Create recommendations table
            print("   - Creating recommendations table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS recommendations (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    type VARCHAR(20) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    rationale TEXT NOT NULL,
                    shown_at TIMESTAMPTZ,
                    clicked BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_recommendations_user_id ON recommendations(user_id);
                CREATE INDEX IF NOT EXISTS ix_recommendations_shown_at ON recommendations(shown_at);
            """))
            
            # Create decision_traces table
            print("   - Creating decision_traces table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS decision_traces (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    recommendation_id UUID NOT NULL UNIQUE REFERENCES recommendations(id) ON DELETE CASCADE,
                    trace_data JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE UNIQUE INDEX IF NOT EXISTS uq_decision_traces_recommendation_id ON decision_traces(recommendation_id);
            """))
            
            # Create chat_logs table
            print("   - Creating chat_logs table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS chat_logs (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    message TEXT NOT NULL,
                    response TEXT NOT NULL,
                    guardrails_passed BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_chat_logs_user_id ON chat_logs(user_id);
            """))
            
            # Create operator_actions table
            print("   - Creating operator_actions table...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS operator_actions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    operator_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    user_id UUID NOT NULL REFERENCES profiles(user_id) ON DELETE CASCADE,
                    action_type VARCHAR(20) NOT NULL,
                    reason TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                CREATE INDEX IF NOT EXISTS ix_operator_actions_operator_id ON operator_actions(operator_id);
                CREATE INDEX IF NOT EXISTS ix_operator_actions_user_id ON operator_actions(user_id);
            """))
            
            # Commit transaction
            trans.commit()
            print("\n✅ Migration completed successfully!")
            
            # Verify tables
            print("\n📊 Verifying schema...")
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            
            print(f"\n✅ Tables created: {len(tables)}")
            for table in sorted(tables):
                print(f"   - {table}")
            
            expected_tables = [
                'accounts', 'chat_logs', 'computed_features', 'consent_records',
                'decision_traces', 'operator_actions', 'persona_assignments',
                'profiles', 'recommendations', 'transactions'
            ]
            
            missing = set(expected_tables) - set(tables)
            if missing:
                print(f"\n⚠️  Warning: Missing tables: {missing}")
                return False
            
            print("\n🎉 All tables created successfully!")
            return True
            
        except Exception as e:
            trans.rollback()
            print(f"\n❌ Error during migration: {e}")
            raise

if __name__ == "__main__":
    print("🚀 Starting database migration...")
    print("=" * 50)
    success = run_migration()
    if success:
        print("\n✅ Migration completed successfully!")
        exit(0)
    else:
        print("\n❌ Migration failed!")
        exit(1)

