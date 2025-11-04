# Story 1.4: Create Database Schema

Status: drafted

## Story

As a developer,
I want to create the complete database schema with all required tables,
so that the application has a proper data structure for storing user data, transactions, and recommendations.

## Acceptance Criteria

1. All tables created per PRD schema:
   - `profiles` (user_id, email, role, created_at, updated_at)
   - `consent_records` (id, user_id, granted_at, revoked_at, version, ip_address)
   - `accounts` (id, user_id, account_type, account_number_last4, balance, limit, created_at)
   - `transactions` (id, user_id, account_id, date, merchant, amount, category, created_at)
   - `computed_features` (id, user_id, time_window, signal_type, signal_value, computed_at)
   - `persona_assignments` (id, user_id, time_window, persona, assigned_at)
   - `recommendations` (id, user_id, type, title, rationale, shown_at, clicked)
   - `decision_traces` (id, recommendation_id, trace_data, created_at)
   - `chat_logs` (id, user_id, message, response, guardrails_passed, created_at)
   - `operator_actions` (id, operator_id, user_id, action_type, reason, created_at)
2. Appropriate indexes created (user_id, date ranges, foreign keys)
3. Foreign key constraints defined
4. Migration script created (Alembic or similar)
5. Schema can be applied to RDS instance
6. Schema matches architecture document

## Tasks / Subtasks

- [ ] Task 1: Set up database migration framework (AC: #4)
  - [ ] Choose migration tool (Alembic recommended for SQLAlchemy)
  - [ ] Install Alembic: `pip install alembic`
  - [ ] Initialize Alembic: `alembic init alembic`
  - [ ] Configure Alembic to use database connection string from environment variables
  - [ ] Configure Alembic env.py to use SQLAlchemy models or raw SQL
  - [ ] Create initial migration directory structure

- [ ] Task 2: Create SQLAlchemy models or SQL schema definitions (AC: #1, #6)
  - [ ] Create `app/models/` directory structure
  - [ ] Create `app/models/__init__.py`
  - [ ] Create `app/models/base.py` with Base model and common fields
  - [ ] Create `app/models/profile.py` - Profiles model
  - [ ] Create `app/models/consent.py` - ConsentRecords model
  - [ ] Create `app/models/account.py` - Accounts model
  - [ ] Create `app/models/transaction.py` - Transactions model
  - [ ] Create `app/models/computed_feature.py` - ComputedFeatures model
  - [ ] Create `app/models/persona.py` - PersonaAssignments model
  - [ ] Create `app/models/recommendation.py` - Recommendations model
  - [ ] Create `app/models/decision_trace.py` - DecisionTraces model
  - [ ] Create `app/models/chat_log.py` - ChatLogs model
  - [ ] Create `app/models/operator_action.py` - OperatorActions model
  - [ ] Verify all models match PRD schema requirements

- [ ] Task 3: Define table schemas with proper data types (AC: #1)
  - [ ] Define `profiles` table:
    - `user_id` (UUID, primary key, from Cognito)
    - `email` (VARCHAR, unique, not null)
    - `role` (VARCHAR, enum: 'consumer' or 'operator', not null)
    - `created_at` (TIMESTAMPTZ, not null, default now())
    - `updated_at` (TIMESTAMPTZ, not null, default now(), on update now())
  - [ ] Define `consent_records` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `granted_at` (TIMESTAMPTZ, nullable)
    - `revoked_at` (TIMESTAMPTZ, nullable)
    - `version` (VARCHAR, default '1.0')
    - `ip_address` (VARCHAR, nullable)
  - [ ] Define `accounts` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `account_type` (VARCHAR, enum: 'checking', 'savings', 'high_yield_savings', 'credit_card', not null)
    - `account_number_last4` (VARCHAR(4), nullable)
    - `balance` (DECIMAL(10,2), nullable)
    - `limit` (DECIMAL(10,2), nullable, for credit cards)
    - `created_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `transactions` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `account_id` (UUID, foreign key to accounts.id, not null)
    - `date` (DATE, not null)
    - `merchant` (VARCHAR, not null)
    - `amount` (DECIMAL(10,2), not null, negative for debits, positive for credits)
    - `category` (VARCHAR, nullable)
    - `created_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `computed_features` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `time_window` (VARCHAR, enum: '30d', '90d', '180d', not null)
    - `signal_type` (VARCHAR, not null, e.g., 'subscription', 'credit_utilization_*', 'savings_behavior', 'income_stability')
    - `signal_value` (JSONB, not null, stores computed signal data)
    - `computed_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `persona_assignments` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `time_window` (VARCHAR, enum: '30d', '90d', '180d', not null)
    - `persona` (VARCHAR, enum: 'high_utilization', 'subscription_heavy', 'variable_income_budgeter', 'savings_builder', 'general_wellness', not null)
    - `assigned_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `recommendations` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `type` (VARCHAR, enum: 'education', 'offer', not null)
    - `title` (VARCHAR, not null)
    - `rationale` (TEXT, not null, explains why recommendation is shown)
    - `shown_at` (TIMESTAMPTZ, nullable, timestamp when shown to user)
    - `clicked` (BOOLEAN, default false)
    - `created_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `decision_traces` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `recommendation_id` (UUID, foreign key to recommendations.id, unique, not null)
    - `trace_data` (JSONB, not null, stores complete decision trace JSON)
    - `created_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `chat_logs` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `user_id` (UUID, foreign key to profiles.user_id, not null)
    - `message` (TEXT, not null, user's message)
    - `response` (TEXT, not null, AI response)
    - `guardrails_passed` (BOOLEAN, not null, default true)
    - `created_at` (TIMESTAMPTZ, not null, default now())
  - [ ] Define `operator_actions` table:
    - `id` (UUID, primary key, default gen_random_uuid())
    - `operator_id` (UUID, foreign key to profiles.user_id, not null, operator user)
    - `user_id` (UUID, foreign key to profiles.user_id, not null, target user)
    - `action_type` (VARCHAR, enum: 'override', 'flag', not null)
    - `reason` (TEXT, not null)
    - `created_at` (TIMESTAMPTZ, not null, default now())

- [ ] Task 4: Create foreign key constraints (AC: #3)
  - [ ] Add foreign key: `consent_records.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `accounts.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `transactions.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `transactions.account_id` → `accounts.id`
  - [ ] Add foreign key: `computed_features.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `persona_assignments.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `recommendations.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `decision_traces.recommendation_id` → `recommendations.id` (unique constraint)
  - [ ] Add foreign key: `chat_logs.user_id` → `profiles.user_id`
  - [ ] Add foreign key: `operator_actions.operator_id` → `profiles.user_id`
  - [ ] Add foreign key: `operator_actions.user_id` → `profiles.user_id`
  - [ ] Configure cascade behavior (ON DELETE CASCADE where appropriate)

- [ ] Task 5: Create indexes for performance (AC: #2)
  - [ ] Create unique index on `profiles.email`
  - [ ] Create composite index on `transactions(user_id, date DESC)` for transaction queries
  - [ ] Create index on `transactions.account_id` for account-based queries
  - [ ] Create index on `transactions.date` for date range queries
  - [ ] Create composite index on `computed_features(user_id, time_window)` for signal queries
  - [ ] Create index on `computed_features.signal_type` for signal type filtering
  - [ ] Create composite index on `persona_assignments(user_id, time_window)` for persona queries
  - [ ] Create index on `recommendations.user_id` for user recommendation queries
  - [ ] Create index on `recommendations.shown_at` for recommendation tracking
  - [ ] Create index on `chat_logs.user_id` for user chat history
  - [ ] Create index on `chat_logs.created_at` for chronological queries
  - [ ] Create index on `operator_actions.user_id` for user action queries
  - [ ] Create index on `operator_actions.operator_id` for operator audit queries

- [ ] Task 6: Create initial migration script (AC: #4, #5)
  - [ ] Create Alembic migration: `alembic revision -m "Initial schema"`
  - [ ] Add all table creation statements to migration
  - [ ] Add all foreign key constraints to migration
  - [ ] Add all indexes to migration
  - [ ] Verify migration script syntax is correct
  - [ ] Test migration can be applied to local database (if available)
  - [ ] Document migration rollback procedure

- [ ] Task 7: Configure database connection for migrations (AC: #5)
  - [ ] Update Alembic env.py to read DATABASE_URL from environment variables
  - [ ] Configure connection to use Secrets Manager for production (via boto3)
  - [ ] Configure connection to use .env file for local development
  - [ ] Test connection configuration works with local database
  - [ ] Document connection setup in README

- [ ] Task 8: Verify schema matches architecture document (AC: #6)
  - [ ] Verify all tables from architecture document are created
  - [ ] Verify all relationships match architecture document
  - [ ] Verify all indexes match architecture document specifications
  - [ ] Verify data types are appropriate for PostgreSQL
  - [ ] Verify schema supports all required queries from API endpoints

- [ ] Task 9: Create database utility functions (AC: #5)
  - [ ] Create `app/database/__init__.py`
  - [ ] Create `app/database/connection.py` for database connection management
  - [ ] Create `app/database/session.py` for SQLAlchemy session management
  - [ ] Create helper functions for connection pooling (for Lambda)
  - [ ] Document connection pooling configuration

- [ ] Task 10: Test schema creation on RDS instance (AC: #5)
  - [ ] Deploy RDS instance (from Story 1.3)
  - [ ] Retrieve connection string from Secrets Manager
  - [ ] Run migration: `alembic upgrade head`
  - [ ] Verify all tables created successfully
  - [ ] Verify all indexes created successfully
  - [ ] Verify foreign key constraints work correctly
  - [ ] Test connection from local environment
  - [ ] Document any connection issues or solutions

## Dev Notes

### Architecture Patterns and Constraints

- **Database**: AWS RDS PostgreSQL 15.x [Source: docs/architecture.md#Decision-Summary]
- **ORM/Migration**: SQLAlchemy with Alembic for migrations [Source: docs/epics.md#Story-1.4]
- **Connection Management**: Use connection pooling for Lambda functions [Source: docs/architecture.md#Performance-Considerations]
- **Schema Design**: Application-layer security (data access enforced in code, not database) [Source: docs/architecture.md#Security-Architecture]
- **Data Types**: Use UUID for primary keys, TIMESTAMPTZ for timestamps, JSONB for flexible data [Source: PostgreSQL best practices]
- **Indexes**: Composite indexes on (user_id, date) and (user_id, time_window) for efficient queries [Source: docs/epics.md#Story-1.4]

### Project Structure Notes

The database schema should be organized as follows:
```
spendsense-backend/
├── app/
│   ├── models/                       # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py                   # Base model class
│   │   ├── profile.py
│   │   ├── consent.py
│   │   ├── account.py
│   │   ├── transaction.py
│   │   ├── computed_feature.py
│   │   ├── persona.py
│   │   ├── recommendation.py
│   │   ├── decision_trace.py
│   │   ├── chat_log.py
│   │   └── operator_action.py
│   ├── database/                     # Database utilities
│   │   ├── __init__.py
│   │   ├── connection.py             # Connection management
│   │   └── session.py                # Session management
├── alembic/                          # Alembic migrations
│   ├── versions/                     # Migration scripts
│   ├── env.py                        # Alembic configuration
│   └── script.py.mako                # Migration template
└── alembic.ini                       # Alembic configuration file
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **Migration Tool Choice**: 
   - Alembic is recommended for SQLAlchemy-based projects
   - Provides version control for schema changes
   - Supports both upgrade and downgrade migrations
   - Can generate migrations from SQLAlchemy models

2. **SQLAlchemy Models**:
   - Use declarative base for model definitions
   - Define relationships using SQLAlchemy relationship() function
   - Use UUID type for primary keys (PostgreSQL UUID extension)
   - Use JSONB for flexible data storage (signal_value, trace_data)
   - Use ENUM types for constrained values (role, account_type, persona, etc.)

3. **Data Types**:
   - UUID: Use PostgreSQL UUID type with gen_random_uuid() for primary keys
   - TIMESTAMPTZ: Use for all timestamp fields (timezone-aware)
   - DECIMAL(10,2): Use for monetary amounts (balance, limit, amount)
   - VARCHAR: Use for text fields with appropriate length limits
   - JSONB: Use for flexible structured data (signal_value, trace_data)
   - BOOLEAN: Use for boolean flags

4. **Foreign Key Constraints**:
   - Define foreign keys with ON DELETE CASCADE where appropriate
   - Use ON DELETE RESTRICT for critical relationships (e.g., profiles)
   - Ensure referential integrity across all relationships

5. **Indexes**:
   - Composite indexes on (user_id, date) for transaction queries
   - Composite indexes on (user_id, time_window) for time-windowed data
   - Single column indexes for foreign keys and frequently filtered columns
   - Unique index on profiles.email for user lookups

6. **Connection Pooling**:
   - Configure SQLAlchemy connection pool for Lambda functions
   - Use connection pooling to manage RDS connections efficiently
   - Consider RDS Proxy for production (future enhancement)

7. **Environment Configuration**:
   - Use DATABASE_URL environment variable for connection string
   - Retrieve from Secrets Manager in production
   - Use .env file for local development
   - Document connection string format: `postgresql://user:pass@host:5432/dbname`

### Learnings from Previous Stories

**From Story 1.2 (Status: in-progress)**
- **Backend Structure**: Backend project created at `spendsense-backend/` with `app/` directory - database models should be created in `app/models/`
- **Python Environment**: Python 3.11+ virtual environment setup - Alembic should be installed in the same environment
- **Dependencies**: FastAPI and SQLAlchemy dependencies should be added to requirements.txt
- **Environment Variables**: Backend uses `.env` with python-dotenv - database connection string should be configured similarly

**From Story 1.3 (Status: in-progress)**
- **RDS Database**: RDS PostgreSQL instance will be created with database name "spendsense" - schema should be created in this database
- **Connection String**: Connection string stored in AWS Secrets Manager - migrations should support reading from Secrets Manager
- **Security Groups**: Security groups configured for Lambda access - local development may require temporary security group rule
- **VPC Configuration**: RDS is in VPC - Lambda functions need VPC configuration to access RDS

### References

- [Source: docs/epics.md#Story-1.4]
- [Source: docs/architecture.md#Data-Architecture]
- [Source: docs/architecture.md#Decision-Summary]
- [Source: docs/architecture.md#Performance-Considerations]
- [Source: docs/architecture.md#Security-Architecture]
- [Source: doc/spendsense_prd.md#Database-Schema]

## Dev Agent Record

### Context Reference

- `docs/stories/1-4-create-database-schema.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

<!-- To be filled during implementation -->

### File List

**Created Files:**
<!-- To be filled during implementation -->

**Modified Files:**
<!-- To be filled during implementation -->

## Change Log

- 2025-11-03: Story created and drafted

