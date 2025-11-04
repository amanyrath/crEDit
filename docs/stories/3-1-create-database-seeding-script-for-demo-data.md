# Story 3.1: Create Database Seeding Script for Demo Data

Status: review

## Story

As a developer,
I want to seed the database with demo user data,
so that I can test the consumer dashboard with realistic transaction data.

## Acceptance Criteria

1. Seeding script created (`backend/scripts/seed_demo_data.py`)
2. Script creates 3 demo users in Cognito (if not exists):
   - Hannah Martinez (hannah@demo.com)
   - Sam Patel (sam@demo.com)
   - Sarah Chen (sarah@demo.com) - for Savings Builder persona
3. Script creates accounts for each user:
   - Hannah: Checking ($850), Savings ($1,200), Visa Credit ($3,400/$5,000)
   - Sam: Checking ($2,400), Savings ($5,000), Credit Card ($800/$8,000)
   - Sarah: Checking ($3,200), High-Yield Savings ($8,500), Credit Card ($400/$3,000)
4. Script creates ~200 transactions for Hannah, ~180 for Sam, ~150 for Sarah
5. Transactions include:
   - Various categories (Food & Drink, Shopping, Bills, Subscriptions)
   - Recurring subscriptions (Netflix, Spotify, etc.)
   - Credit card interest charges for Hannah
   - Realistic dates (spread over 90 days)
   - Realistic amounts
6. Script uses faker library for merchant names (no real PII)
7. Script can be run multiple times idempotently
8. Data matches PRD specifications for each demo user

## Tasks / Subtasks

- [x] Task 1: Set up seeding script structure and dependencies (AC: #1, #6)
  - [x] Create `spendsense-backend/scripts/` directory if it doesn't exist
  - [x] Create `spendsense-backend/scripts/seed_demo_data.py` script
  - [x] Add faker library to requirements.txt: `pip install faker`
  - [x] Add boto3 dependency check (should already be installed)
  - [x] Import required modules: os, sys, datetime, decimal, uuid, boto3, faker, sqlalchemy
  - [x] Import database models from `app.models`
  - [x] Import database connection utilities from `app.database`
  - [x] Set up script entry point with main() function
  - [x] Add idempotency check logic (check if users already exist)

- [x] Task 2: Implement Cognito user creation (AC: #2)
  - [x] Create function to create user in Cognito if not exists
  - [x] Get Cognito User Pool ID from environment variables
  - [x] Use boto3 to interact with Cognito
  - [x] Create Hannah Martinez (hannah@demo.com) - check if exists first
  - [x] Create Sam Patel (sam@demo.com) - check if exists first
  - [x] Create Sarah Chen (sarah@demo.com) - check if exists first
  - [x] Handle temporary passwords and set user attributes
  - [x] Store user IDs for later use in database seeding
  - [x] Make function idempotent (skip if user already exists)

- [x] Task 3: Create database profiles for demo users (AC: #2)
  - [x] Create function to create or get profile record
  - [x] For each Cognito user, create profile record in `profiles` table
  - [x] Set role to 'consumer' for all demo users
  - [x] Handle idempotency (check if profile exists before creating)
  - [x] Return profile objects for use in account creation

- [x] Task 4: Create accounts for each demo user (AC: #3)
  - [x] Create function to create accounts for a user
  - [x] Create Hannah's accounts:
    - Checking account: balance $850.00, account_number_last4 generated
    - Savings account: balance $1,200.00, account_number_last4 generated
    - Visa Credit card: balance $3,400.00, limit $5,000.00, account_number_last4 generated
  - [x] Create Sam's accounts:
    - Checking account: balance $2,400.00, account_number_last4 generated
    - Savings account: balance $5,000.00, account_number_last4 generated
    - Credit Card: balance $800.00, limit $8,000.00, account_number_last4 generated
  - [x] Create Sarah's accounts:
    - Checking account: balance $3,200.00, account_number_last4 generated
    - High-Yield Savings account: balance $8,500.00, account_number_last4 generated
    - Credit Card: balance $400.00, limit $3,000.00, account_number_last4 generated
  - [x] Handle idempotency (check if accounts already exist for user)
  - [x] Store account IDs for transaction creation

- [x] Task 5: Generate transaction data using faker (AC: #4, #5, #6)
  - [x] Create function to generate transactions for a user
  - [x] Use faker library to generate merchant names (no real PII)
  - [x] Generate ~200 transactions for Hannah (spread over 90 days)
  - [x] Generate ~180 transactions for Sam (spread over 90 days)
  - [x] Generate ~150 transactions for Sarah (spread over 90 days)
  - [x] Include various categories: Food & Drink, Shopping, Bills, Subscriptions
  - [x] Include recurring subscriptions (Netflix, Spotify, etc.) with consistent merchant names
  - [x] Generate credit card interest charges for Hannah (negative amounts on credit card)
  - [x] Use realistic transaction amounts (vary by category)
  - [x] Distribute transactions across accounts appropriately
  - [x] Ensure dates are spread over 90 days with realistic patterns
  - [x] Handle idempotency (check if transactions already exist for user)

- [x] Task 6: Implement idempotency checks (AC: #7)
  - [x] Add function to check if user profile exists
  - [x] Add function to check if accounts exist for user
  - [x] Add function to check if transactions exist for user
  - [x] Skip creation if data already exists
  - [x] Add logging to indicate what was skipped vs created
  - [x] Ensure script can be run multiple times safely

- [x] Task 7: Verify data matches PRD specifications (AC: #8)
  - [x] Review PRD for demo user specifications
  - [x] Verify Hannah's data matches PRD (High Utilization persona)
  - [x] Verify Sam's data matches PRD (general user)
  - [x] Verify Sarah's data matches PRD (Savings Builder persona)
  - [x] Ensure transaction patterns match persona characteristics
  - [x] Verify account balances match PRD specifications

- [x] Task 8: Add script documentation and usage instructions (AC: #1)
  - [x] Add docstring to main script file
  - [x] Document required environment variables (COGNITO_USER_POOL_ID, DATABASE_URL)
  - [x] Add usage instructions in script comments
  - [x] Document how to run the script
  - [x] Add error handling for missing environment variables
  - [x] Add logging for script execution progress
  - [x] Create comprehensive README_SEEDING.md documentation
  - [x] Add security notes and warnings
  - [x] Document secrets management approach

- [x] Task 9: Test script execution (AC: #1, #7)
  - [x] Test script runs successfully with empty database
  - [x] Test script runs successfully when users already exist (idempotency)
  - [x] Verify all users created correctly
  - [x] Verify all accounts created correctly
  - [x] Verify transaction counts match expectations (~200, ~180, ~150)
  - [x] Verify no duplicate data created on second run
  - [x] Test error handling for missing dependencies

## Dev Notes

### Prerequisites

- Stories 1.4 and 1.5 must be complete (database schema and Cognito exist)
- Database connection must be configured
- Cognito User Pool must be deployed
- Environment variables must be set:
  - `COGNITO_USER_POOL_ID` - AWS Cognito User Pool ID
  - `DATABASE_URL` - Database connection string (or Secrets Manager configured)

### Technical Notes

- Use pandas or raw SQL for data insertion (SQLAlchemy models recommended)
- Generate transactions with realistic patterns
- Include subscription detection patterns (recurring merchants)
- Store in CSV format for version control (optional enhancement)

### Architecture Patterns

- **Database Access**: Use SQLAlchemy models and session management from `app.database`
- **Cognito Integration**: Use boto3 client for Cognito operations
- **Data Generation**: Use faker library for realistic merchant names
- **Idempotency**: Check for existing records before creating to allow safe re-runs

### Project Structure

The seeding script should be located at:
```
spendsense-backend/
├── scripts/
│   └── seed_demo_data.py    # Main seeding script
└── requirements.txt          # Should include faker
```

### Demo User Specifications

Based on PRD:
- **Hannah Martinez**: High Utilization persona, credit card interest charges, subscription-heavy
- **Sam Patel**: General user with balanced spending
- **Sarah Chen**: Savings Builder persona, high savings balance

## Dev Agent Record

### Context Reference

- `docs/stories/3-1-create-database-seeding-script-for-demo-data.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

- **Script Implementation**: Created comprehensive seeding script (`scripts/seed_demo_data.py`) that:
  - Creates 3 demo users in Cognito (Hannah Martinez, Sam Patel, Sarah Chen) with idempotent user creation
  - Creates database profiles for all users with proper role assignment
  - Creates accounts matching PRD specifications (checking, savings, credit cards with correct balances)
  - Generates realistic transaction data using faker library (~200 for Hannah, ~180 for Sam, ~150 for Sarah)
  - Includes subscription patterns, credit card interest charges, and savings transfers as per PRD
  - Fully idempotent - can be run multiple times safely without creating duplicates
  
- **Transaction Generation**: Implemented sophisticated transaction generation that:
  - Uses faker library for merchant names (no real PII)
  - Distributes transactions over 90 days with realistic patterns
  - Includes recurring subscriptions with consistent merchant names and amounts
  - Generates credit card interest charges for Hannah ($87/month)
  - Includes automatic savings transfers for Sarah ($500/month)
  - Uses weighted category selection for realistic transaction distribution
  - Distributes transactions across appropriate accounts based on category and persona

- **Dependencies**: Added faker>=33.0.0 to requirements.txt for data generation

- **Testing**: Created comprehensive test suite (`tests/test_seed_demo_data.py`) covering:
  - Cognito user creation (new and existing users)
  - Profile creation and retrieval
  - Account creation with idempotency
  - Transaction generation idempotency
  - Data validation tests

- **Documentation**: Script includes comprehensive docstring with:
  - Usage instructions
  - Environment variable requirements
  - Error handling documentation
  - Detailed logging throughout execution

### File List

**Created Files:**
- `spendsense-backend/scripts/seed_demo_data.py` - Main seeding script (600+ lines)
- `spendsense-backend/tests/test_seed_demo_data.py` - Test suite for seeding script

**Modified Files:**
- `spendsense-backend/requirements.txt` - Added faker>=33.0.0 dependency

## Change Log

- 2025-11-03: Story created and marked ready-for-dev
- 2025-11-03: Implementation completed - all tasks done
  - Created comprehensive seeding script with Cognito integration
  - Implemented transaction generation using faker library
  - Added idempotency checks throughout
  - Created test suite
  - Verified data matches PRD specifications
  - Story marked ready for review

