# Database Seeding Script

## Overview

The `seed_demo_data.py` script populates the SpendSense database with demo user data for development and testing purposes. It creates Cognito users, database profiles, accounts, and realistic transaction history.

## Security Notes

⚠️ **IMPORTANT**: This script is for **development and testing only**. Never use in production.

### Secrets Management

- **No hardcoded secrets**: All sensitive data is retrieved from environment variables or AWS Secrets Manager
- **Database credentials**: Retrieved from AWS Secrets Manager (`spendsense/database/connection`)
- **Cognito configuration**: Retrieved from AWS Secrets Manager (`spendsense/cognito/configuration`) or environment variables
- **Demo passwords**: Uses `DEMO_PASSWORD` environment variable (defaults to `Demo123!` for demo users only)

### Data Privacy

- **No real PII**: Uses Faker library to generate fake merchant names
- **Demo users only**: Creates specific test users (`hannah@demo.com`, `sam@demo.com`, `sarah@demo.com`)
- **Isolated test data**: All data is clearly marked as demo/test data

## Prerequisites

1. **AWS Credentials**: Configured via AWS CLI (`aws configure`) or environment variables
2. **Database**: PostgreSQL database accessible via `DATABASE_URL`
3. **Cognito**: User Pool deployed and accessible
4. **Python Dependencies**: Installed via `pip install -r requirements.txt -c .pip-constraints.txt`

## Usage

### Quick Start

```bash
# Set up environment variables
source scripts/setup_seed_env.sh

# Run the seeding script
python scripts/seed_demo_data.py
```

### Manual Setup

```bash
# Export required environment variables
export DATABASE_URL=$(aws secretsmanager get-secret-value \
  --secret-id spendsense/database/connection \
  --query SecretString \
  --output text | jq -r '.connection_string')

export COGNITO_USER_POOL_ID=$(aws secretsmanager get-secret-value \
  --secret-id spendsense/cognito/configuration \
  --query SecretString \
  --output text | jq -r '.user_pool_id')

export AWS_REGION=us-east-1  # Optional, defaults to us-east-1

# Optional: Set custom demo password
export DEMO_PASSWORD=YourSecurePassword123!

# Run the script
python scripts/seed_demo_data.py
```

## What Gets Created

### Users (3 total)

1. **Hannah Martinez** (`hannah@demo.com`)
   - Role: consumer
   - Persona: High Utilization
   - Accounts: Checking ($850), Savings ($1,200), Credit Card ($3,400/$5,000)
   - Transactions: ~200 over 90 days
   - Features: Subscription charges, credit card interest ($87/month)

2. **Sam Patel** (`sam@demo.com`)
   - Role: consumer
   - Persona: Subscription-Heavy
   - Accounts: Checking ($2,400), Savings ($5,000), Credit Card ($800/$8,000)
   - Transactions: ~180 over 90 days
   - Features: 8 active subscriptions

3. **Sarah Chen** (`sarah@demo.com`)
   - Role: consumer
   - Persona: Savings Builder
   - Accounts: Checking ($3,200), High-Yield Savings ($8,500), Credit Card ($400/$3,000)
   - Transactions: ~150 over 90 days
   - Features: Automatic savings transfers ($500/month)

### Accounts (9 total)

- 3 accounts per user (checking, savings/high-yield-savings, credit_card)
- Realistic balances matching PRD specifications
- Credit card limits set appropriately

### Transactions (~530 total)

- Realistic distribution over 90 days
- Multiple transactions per day allowed
- Categories: Food & Drink, Shopping, Bills, Subscriptions, Transportation, Entertainment
- Recurring subscriptions with consistent merchant names
- Credit card interest charges (Hannah)
- Automatic savings transfers (Sarah)

## Idempotency

The script is **idempotent** - it can be run multiple times safely:

- **Cognito users**: Checks if user exists before creating
- **Profiles**: Checks if profile exists before creating
- **Accounts**: Checks if account type exists before creating
- **Transactions**: Checks if transactions exist and regenerates if incomplete

If partial data exists (e.g., only 106 transactions when 200 expected), the script will:
1. Detect partial data
2. Clear existing transactions for that user
3. Regenerate complete transaction set

## Environment Variables

| Variable | Required | Default | Source |
|----------|----------|---------|--------|
| `DATABASE_URL` | Yes | None | AWS Secrets Manager or env var |
| `COGNITO_USER_POOL_ID` | Yes | None | AWS Secrets Manager or env var |
| `AWS_REGION` | No | `us-east-1` | Environment variable |
| `DEMO_PASSWORD` | No | `Demo123!` | Environment variable |
| `COGNITO_CONFIG_SECRET_ID` | No | `spendsense/cognito/configuration` | Environment variable |

## Troubleshooting

### "User pool does not exist"

**Error**: `ResourceNotFoundException: User pool X does not exist`

**Solution**: 
- Verify `COGNITO_USER_POOL_ID` is set correctly
- Check AWS region matches your deployment
- Verify Cognito User Pool is deployed

### "Connection refused" or "Connection timeout"

**Error**: `psycopg2.OperationalError: connection to server failed`

**Solution**:
- Verify `DATABASE_URL` is set correctly
- Check database is accessible from your network
- For RDS: Ensure security groups allow your IP
- Verify database is running

### Partial transaction generation

**Symptom**: Only ~106 transactions created instead of 200

**Solution**: 
- This was fixed in the script - run again to regenerate complete set
- Script now allows multiple transactions per day

### AWS credentials not found

**Error**: `NoCredentialsError`

**Solution**:
- Run `aws configure` to set up credentials
- Or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables
- Or use AWS SSO: `aws sso login --profile your-profile`

## Verification

After running the script, verify data was created:

```bash
python scripts/verify_seeding.py
```

This will show:
- Profiles: 3/3 demo users
- Accounts: 9 total
- Transactions: ~530 total

## Related Files

- `scripts/seed_demo_data.py` - Main seeding script
- `scripts/setup_seed_env.sh` - Environment setup helper
- `scripts/verify_seeding.py` - Verification script
- `tests/test_seed_demo_data.py` - Unit tests

## See Also

- [Backend README](../README.md) - General setup instructions
- [Story 3.1 Documentation](../../docs/stories/3-1-create-database-seeding-script-for-demo-data.md) - Story details

