# SpendSense Backend

FastAPI backend application for the SpendSense financial education platform.

## Prerequisites

- Python 3.11 or later
- pip

## Setup

1. **Create and activate virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure environment variables:**

   Copy `.env.example` to `.env` and update with your values:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   - `DATABASE_URL`: PostgreSQL connection string
   - `COGNITO_USER_POOL_ID`: AWS Cognito User Pool ID
   - `COGNITO_CLIENT_ID`: AWS Cognito Client ID
   - `AWS_REGION`: AWS region (default: `us-east-1`)
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY`: LLM API key

   **Getting AWS Resource Values:**

   **Database Connection String:**
   ```bash
   # Get from AWS Secrets Manager
   aws secretsmanager get-secret-value \
     --secret-id spendsense/database/connection \
     --query SecretString \
     --output text
   ```

   **Database Endpoint (for manual connection string construction):**
   ```bash
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Database-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
     --output text
   ```

   **Cognito Values:**
   ```bash
   # User Pool ID
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Cognito-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
     --output text

   # Client ID
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Cognito-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
     --output text
   ```

   Or from AWS Secrets Manager:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id spendsense/cognito/configuration \
     --query SecretString \
     --output text | jq -r '.user_pool_id'
   ```

   **LLM API Keys:**
   - OpenAI: Get from https://platform.openai.com/api-keys
   - Anthropic: Get from https://console.anthropic.com/

   **Local Database Access:**
   
   For local development, you may need to set up port forwarding to access the RDS database:
   ```bash
   # Get database endpoint
   DB_ENDPOINT=$(aws cloudformation describe-stacks \
     --stack-name SpendSense-Database-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
     --output text)

   # Set up port forwarding (requires AWS CLI Session Manager Plugin)
   aws rds start-db-instance --db-instance-identifier your-db-instance-id
   # Then use port forwarding or VPN to connect
   ```
   
   Alternatively, you can use a local PostgreSQL database for development:
   ```bash
   # Install PostgreSQL locally
   # Update DATABASE_URL to: postgresql://username:password@localhost:5432/spendsense
   ```

4. **Run the development server:**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

5. **Run tests:**

   ```bash
   pytest
   ```

   To test environment variable loading:
   ```bash
   pytest tests/test_env.py
   ```

## Environment Variables

The backend uses `python-dotenv` to automatically load environment variables from `.env` file.

**Accessing Environment Variables in Code:**

```python
from app.config import settings

# Access via settings object
database_url = settings.database_url
cognito_user_pool_id = settings.cognito_user_pool_id
aws_region = settings.aws_region
```

Or directly:
```python
import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv("DATABASE_URL")
```

**Important Notes:**
- `.env` file is gitignored - never commit actual secrets
- Environment variables are loaded on application startup
- Settings are defined in `app/config.py`
- For production, set environment variables in your deployment environment (Lambda, ECS, etc.)

## AWS Credentials

For local development, you need AWS credentials configured. Options:

1. **AWS CLI credentials file** (recommended):
   ```bash
   aws configure
   ```
   This creates `~/.aws/credentials` and `~/.aws/config`

2. **Environment variables**:
   ```bash
   export AWS_ACCESS_KEY_ID=your-access-key
   export AWS_SECRET_ACCESS_KEY=your-secret-key
   export AWS_REGION=us-east-1
   ```

3. **AWS SSO/Profiles**:
   ```bash
   aws configure sso
   aws sso login --profile your-profile
   ```

4. **IAM Roles** (for Lambda/ECS deployments):
   - Credentials are automatically provided via IAM roles
   - No manual credential configuration needed

## Project Structure

```
spendsense-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── handler.py           # Lambda handler (Mangum)
│   ├── config.py            # Configuration management
│   ├── dependencies.py      # Dependency injection
│   ├── api/                 # API routes
│   │   └── v1/
│   ├── services/            # Business logic (future)
│   ├── models/              # Database models (future)
│   └── utils/               # Utilities (future)
├── lambdas/                 # Lambda function handlers (future)
├── tests/                   # Test files
├── requirements.txt         # Production dependencies
├── requirements-dev.txt     # Development dependencies
└── .env.example            # Environment variables template
```

## API Documentation

Once the server is running, interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

- **Formatting**: Black (to be configured)
- **Linting**: Ruff (to be configured)
- **Type Checking**: mypy (to be configured)
- **Testing**: pytest with pytest-asyncio

