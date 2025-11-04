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
   - Database connection string
   - AWS Cognito settings
   - AWS region
   - LLM API keys (OpenAI or Anthropic)

4. **Run the development server:**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`

5. **Run tests:**

   ```bash
   pytest
   ```

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

