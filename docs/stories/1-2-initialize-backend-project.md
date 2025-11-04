# Story 1.2: Initialize Backend Project

Status: in-progress

## Story

As a developer,
I want to set up the FastAPI backend project with Python virtual environment,
so that I have a working development environment for building the API and business logic.

## Acceptance Criteria

1. Backend directory created with `spendsense-backend/` structure
2. Python virtual environment created and activated
3. FastAPI, uvicorn, mangum installed for Lambda deployment
4. boto3, pydantic, python-dotenv installed for AWS integration
5. pandas, pytz installed for data processing
6. OpenAI package installed (or anthropic for Claude)
7. pytest and pytest-asyncio installed for testing
8. Project structure matches architecture document (app/, lambdas/, tests/)
9. Basic FastAPI app runs with `uvicorn app.main:app --reload`
10. Requirements.txt and requirements-dev.txt created

## Tasks / Subtasks

- [x] Task 1: Create backend directory structure (AC: #1, #8)
  - [x] Create `spendsense-backend/` directory at project root
  - [x] Create `app/` directory structure
  - [x] Create `lambdas/` directory structure
  - [x] Create `tests/` directory structure
  - [x] Verify directory structure matches architecture document

- [x] Task 2: Set up Python virtual environment (AC: #2)
  - [x] Verify Python 3.11+ is installed (Python 3.14.0 confirmed)
  - [x] Create virtual environment: `python -m venv venv`
  - [x] Document activation commands (Linux/Mac: `source venv/bin/activate`, Windows: `venv\Scripts\activate`)
  - [x] Add `venv/` to `.gitignore` (already in root .gitignore)

- [ ] Task 3: Install core FastAPI dependencies (AC: #3)
  - [ ] Install FastAPI: `pip install fastapi`
  - [ ] Install uvicorn with standard extras: `pip install uvicorn[standard]`
  - [ ] Install mangum for Lambda deployment: `pip install mangum`
  - [ ] Verify all packages installed correctly

- [ ] Task 4: Install AWS integration dependencies (AC: #4)
  - [ ] Install boto3: `pip install boto3`
  - [ ] Install pydantic: `pip install pydantic`
  - [ ] Install python-dotenv: `pip install python-dotenv`
  - [ ] Verify all packages installed correctly

- [ ] Task 5: Install data processing dependencies (AC: #5)
  - [ ] Install pandas: `pip install pandas`
  - [ ] Install pytz: `pip install pytz`
  - [ ] Verify all packages installed correctly

- [ ] Task 6: Install LLM integration package (AC: #6)
  - [ ] Install OpenAI package: `pip install openai`
  - [x] (Optional) Document alternative: `pip install anthropic` for Claude
  - [ ] Verify package installed correctly

- [ ] Task 7: Install testing dependencies (AC: #7)
  - [ ] Install pytest: `pip install pytest`
  - [ ] Install pytest-asyncio: `pip install pytest-asyncio`
  - [ ] Verify all packages installed correctly

- [x] Task 8: Create basic FastAPI application structure (AC: #8, #9)
  - [x] Create `app/__init__.py`
  - [x] Create `app/main.py` with basic FastAPI app
  - [x] Create `app/handler.py` for Lambda handler (Mangum)
  - [x] Create `app/config.py` for configuration management
  - [x] Create `app/dependencies.py` for dependency injection
  - [x] Create basic API structure: `app/api/v1/__init__.py`
  - [ ] Verify FastAPI app runs with `uvicorn app.main:app --reload` (requires dependencies installed)

- [x] Task 9: Create requirements files (AC: #10)
  - [x] Generate `requirements.txt` with production dependencies
  - [x] Generate `requirements-dev.txt` with development dependencies (pytest, pytest-asyncio, etc.)
  - [x] Verify both files include all installed packages with versions

- [x] Task 10: Configure development environment (AC: #2, #9)
  - [x] Create `.env.example` file with required environment variables
  - [x] Document environment variable setup in README
  - [ ] Verify FastAPI app can read configuration from environment variables (requires dependencies installed)

## Dev Notes

### Architecture Patterns and Constraints

- **Backend Framework**: FastAPI with AWS Lambda deployment [Source: docs/architecture.md#Decision-Summary]
- **Language**: Python 3.11+ as required by FastAPI [Source: docs/architecture.md#Decision-Summary]
- **Deployment**: Mangum adapter for ASGI applications on Lambda [Source: docs/architecture.md#Project-Initialization]
- **Testing**: pytest with pytest-asyncio for async endpoint testing [Source: docs/architecture.md#Decision-Summary]
- **Linting**: Ruff + Black + mypy (to be configured in future stories) [Source: docs/architecture.md#Decision-Summary]
- **Project Structure**: Feature-based organization with `app/`, `lambdas/`, and `tests/` directories [Source: docs/architecture.md#Project-Structure]

### Project Structure Notes

The backend project should follow this structure:
```
spendsense-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app entry point
│   ├── handler.py                 # Lambda handler (Mangum)
│   ├── config.py                  # Configuration management
│   ├── dependencies.py            # Dependency injection
│   ├── api/                       # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py            # Auth endpoints (future)
│   │       ├── consumer.py        # Consumer endpoints (future)
│   │       └── operator.py        # Operator endpoints (future)
│   ├── services/                  # Business logic (future)
│   ├── models/                    # Database models (future)
│   └── utils/                     # Utilities (future)
├── lambdas/                       # Lambda function handlers (future)
├── tests/                         # Test files
│   ├── __init__.py
│   ├── conftest.py                # pytest configuration
│   └── test_main.py               # Basic FastAPI tests
├── requirements.txt               # Production dependencies
├── requirements-dev.txt           # Development dependencies
├── .env.example                   # Environment variables template
└── README.md                      # Setup instructions
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **Python Version**: Use Python 3.11 or later as specified in architecture
2. **Virtual Environment**: Use `python -m venv venv` to create isolated environment
3. **FastAPI Setup**: Create basic FastAPI app in `app/main.py` with health check endpoint
4. **Lambda Handler**: Create `app/handler.py` using Mangum to wrap FastAPI app for Lambda deployment
5. **Environment Variables**: Use python-dotenv for local development, boto3 for AWS Secrets Manager in production
6. **Requirements Files**: Use `pip freeze > requirements.txt` to generate pinned versions, separate dev dependencies

### Learnings from Previous Story

**From Story 1.1 (Status: done)**

- **Project Structure**: Frontend project created at `spendsense-frontend/` - follow similar naming convention for backend at `spendsense-backend/`
- **Configuration Files**: Created comprehensive `.gitignore` at root level - ensure `venv/` and Python-specific ignores are covered (already in root .gitignore)
- **Testing Setup**: Frontend uses Vitest - backend should use pytest with pytest-asyncio for async endpoint testing
- **Documentation**: Created README.md files for frontend - should create similar setup documentation for backend
- **Environment Variables**: Frontend uses `.env.local` - backend should use `.env` with python-dotenv for local development
- **Linting/Formatting**: Frontend configured ESLint and Prettier - backend should use Ruff, Black, and mypy (to be configured in future stories)

[Source: docs/stories/1-1-initialize-frontend-project.md#Dev-Agent-Record]

### References

- [Source: docs/epics.md#Story-1.2]
- [Source: docs/architecture.md#Project-Initialization]
- [Source: docs/architecture.md#Decision-Summary]
- [Source: docs/architecture.md#Project-Structure]
- [Source: docs/architecture.md#Development-Environment]

## Dev Agent Record

### Context Reference

- `docs/stories/1-2-initialize-backend-project.context.xml`

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

- **Directory Structure**: Created complete backend project structure at `spendsense-backend/` matching architecture document
  - `app/` directory with main.py, handler.py, config.py, dependencies.py
  - `app/api/v1/` directory structure for future API routes
  - `lambdas/` directory for future Lambda handlers
  - `tests/` directory with conftest.py and test_main.py
- **Virtual Environment**: Created Python virtual environment (Python 3.14.0 confirmed, meets 3.11+ requirement)
- **FastAPI Application**: Created basic FastAPI app with health check endpoint (`/health`) and root endpoint
- **Lambda Handler**: Created Mangum adapter in `app/handler.py` for AWS Lambda deployment
- **Configuration**: Created `app/config.py` with Settings class using python-dotenv for environment variables
- **Requirements Files**: Created `requirements.txt` and `requirements-dev.txt` with all required dependencies
- **Environment Template**: Created `.env.example` with all required environment variables documented
- **Documentation**: Created comprehensive README.md with setup instructions
- **Testing Setup**: Created pytest configuration (conftest.py) and basic tests (test_main.py)
- **Dependencies Installation**: Note - Dependencies need to be installed manually using:
  ```bash
  source venv/bin/activate
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  ```
  After installation, verify with: `uvicorn app.main:app --reload` and `pytest`

### File List

**Created Files:**
- `app/__init__.py` - Application package initialization
- `app/main.py` - FastAPI application entry point with health check endpoint
- `app/handler.py` - Lambda handler using Mangum adapter
- `app/config.py` - Configuration management with Settings class
- `app/dependencies.py` - Dependency injection placeholder
- `app/api/__init__.py` - API package initialization
- `app/api/v1/__init__.py` - API v1 router setup
- `tests/__init__.py` - Tests package initialization
- `tests/conftest.py` - pytest configuration and fixtures
- `tests/test_main.py` - Basic FastAPI application tests
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `.env.example` - Environment variables template
- `README.md` - Setup and development documentation

**Directory Structure:**
- `spendsense-backend/` - Backend project root
- `app/` - Main application code
- `app/api/v1/` - API v1 routes (structure ready for future endpoints)
- `lambdas/` - Lambda function handlers (future)
- `tests/` - Test files
- `venv/` - Python virtual environment (excluded from git)

## Change Log

- 2025-11-03: Story created and drafted
- 2025-11-03: Story context generated and marked ready-for-dev
- 2025-11-03: Story implementation in progress - structure and files created, dependencies installation pending

