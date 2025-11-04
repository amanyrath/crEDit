# Architecture

## Executive Summary

SpendSense uses a modern AWS-based serverless architecture with React frontend and FastAPI backend. The system delivers personalized financial education through behavioral signal detection, persona assignment, and explainable recommendation generation. Architecture prioritizes scalability, security, and full decision traceability for operator oversight.

## Project Initialization

First implementation story should execute:

**Frontend:**
```bash
npm create vite@latest spendsense-frontend -- --template react-ts
cd spendsense-frontend
npm install
npm install @tanstack/react-query react-router-dom date-fns
npm install -D tailwindcss postcss autoprefixer
npm install recharts
npm install @aws-amplify/auth @aws-amplify/core
npx tailwindcss init -p
```

**Backend:**
```bash
mkdir spendsense-backend
cd spendsense-backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fastapi uvicorn[standard] mangum
pip install boto3 pydantic python-dotenv
pip install pandas pytz
pip install openai  # or anthropic for Claude
pip install pytest pytest-asyncio
```

This establishes the base architecture with these decisions:
- Frontend: React 18 + Vite + TypeScript + Tailwind CSS
- State Management: React Query + Context API
- Backend: FastAPI with AWS Lambda deployment
- Database: AWS RDS PostgreSQL (to be configured)
- Authentication: AWS Cognito (to be configured)

## Decision Summary

| Category | Decision | Version | Affects Epics | Rationale |
| -------- | -------- | ------- | ------------- | --------- |
| Frontend Framework | React | 18.x | All frontend epics | Industry standard, large ecosystem |
| Build Tool | Vite | Latest | All frontend epics | Fast development, optimized builds |
| Language | TypeScript | 5.x | All frontend epics | Type safety, better DX |
| Styling | Tailwind CSS | 3.x | All frontend epics | Utility-first, rapid development |
| Design System | shadcn/ui | Latest | Consumer Dashboard, Operator Dashboard | Accessible, customizable components |
| State Management | React Query | Latest | All frontend epics | Server state management, caching |
| Data Visualization | Recharts | Latest | Consumer Dashboard (Insights) | React-native charting library |
| Routing | React Router | 6.x | All frontend epics | Standard React routing |
| Backend Framework | FastAPI | Latest | All backend epics | Fast, async, auto-docs |
| Language | Python | 3.11+ | All backend epics | FastAPI requirement, data processing |
| Database | AWS RDS PostgreSQL | 15.x | All epics | Managed PostgreSQL, reliable |
| Authentication | AWS Cognito | Latest | Authentication & Authorization | Managed auth, JWT tokens |
| File Storage | Amazon S3 | Latest | Offers (partner logos) | Scalable object storage |
| API Deployment | AWS Lambda + API Gateway | Latest | All backend epics | Serverless, auto-scaling |
| Background Jobs | AWS Lambda + EventBridge | Latest | Signal Detection, Persona Assignment, Recommendation Engine | Serverless async processing |
| Frontend Hosting | S3 + CloudFront | Latest | All frontend epics | Global CDN, fast delivery |
| Logging | CloudWatch Logs | Latest | All epics | Centralized logging |
| Secrets Management | AWS Secrets Manager | Latest | All backend epics | Secure secret storage |
| Testing (Frontend) | Vitest + Playwright | Latest | All frontend epics | Fast unit tests, E2E testing |
| Testing (Backend) | pytest | Latest | All backend epics | Standard Python testing |
| Linting (Frontend) | ESLint + Prettier | Latest | All frontend epics | Code quality, formatting |
| Linting (Backend) | Ruff + Black + mypy | Latest | All backend epics | Fast linting, formatting, type checking |
| CI/CD | GitHub Actions | Latest | All epics | Automated testing and deployment |
| Monitoring | CloudWatch | Latest | All epics | Metrics, alarms, dashboards |

## Project Structure

```
spendsense/
├── frontend/                          # React + Vite application
│   ├── public/
│   ├── src/
│   │   ├── components/                # Reusable UI components
│   │   │   ├── ui/                    # shadcn/ui components
│   │   │   ├── RationaleBox.tsx       # Custom rationale box component
│   │   │   ├── EducationCard.tsx      # Education card with rationale
│   │   │   ├── DecisionTraceViewer.tsx # JSON viewer for operators
│   │   │   ├── ChatWidget.tsx         # Consumer chat widget
│   │   │   └── OperatorDataTable.tsx  # Operator data table
│   │   ├── features/                  # Feature-based organization
│   │   │   ├── auth/
│   │   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   ├── ConsentModal.tsx
│   │   │   │   └── hooks/
│   │   │   │       └── useAuth.ts
│   │   │   ├── consumer/
│   │   │   │   ├── dashboard/
│   │   │   │   │   ├── DashboardLayout.tsx
│   │   │   │   │   └── tabs/
│   │   │   │   │       ├── TransactionsTab.tsx
│   │   │   │   │       ├── InsightsTab.tsx
│   │   │   │   │       ├── EducationTab.tsx
│   │   │   │   │       └── OffersTab.tsx
│   │   │   │   └── chat/
│   │   │   │       └── ChatWidget.tsx
│   │   │   └── operator/
│   │   │       ├── UserList/
│   │   │       │   └── UserListPage.tsx
│   │   │       └── UserDetail/
│   │   │           └── UserDetailPage.tsx
│   │   ├── lib/                       # Utilities and configurations
│   │   │   ├── api/                   # API client
│   │   │   │   ├── client.ts
│   │   │   │   └── endpoints.ts
│   │   │   ├── auth/                  # Auth utilities
│   │   │   │   └── cognito.ts
│   │   │   ├── utils/
│   │   │   │   └── date.ts
│   │   │   └── queryClient.ts         # React Query configuration
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── vite-env.d.ts
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── .eslintrc.json
│   ├── .prettierrc
│   └── .env.local                     # Local environment variables
│
├── backend/                           # FastAPI application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── handler.py                 # Lambda handler (Mangum)
│   │   ├── config.py                  # Configuration management
│   │   ├── dependencies.py            # Dependency injection
│   │   │
│   │   ├── api/                       # API routes
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py            # Auth endpoints
│   │   │   │   ├── consumer.py        # Consumer endpoints
│   │   │   │   └── operator.py        # Operator endpoints
│   │   │
│   │   ├── services/                  # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py        # Cognito integration
│   │   │   ├── signal_detection.py    # Behavioral signal detection
│   │   │   ├── persona_assignment.py  # Persona assignment logic
│   │   │   ├── recommendation_engine.py # Recommendation generation
│   │   │   └── consent_service.py     # Consent management
│   │   │
│   │   ├── models/                    # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   ├── recommendation.py
│   │   │   └── decision_trace.py
│   │   │
│   │   ├── database/                  # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connection.py          # RDS connection
│   │   │   ├── models.py              # SQLAlchemy models
│   │   │   └── repositories.py        # Data access layer
│   │   │
│   │   ├── utils/                     # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── logging.py             # Logging configuration
│   │   │   ├── errors.py              # Error handling
│   │   │   └── date_utils.py          # Date/time utilities
│   │   │
│   │   └── middleware/                # Middleware
│   │       ├── __init__.py
│   │       ├── auth.py                # JWT validation
│   │       └── error_handler.py       # Global error handler
│   │
│   ├── lambdas/                       # Lambda functions for background jobs
│   │   ├── compute_features/
│   │   │   ├── handler.py
│   │   │   └── requirements.txt
│   │   ├── assign_persona/
│   │   │   ├── handler.py
│   │   │   └── requirements.txt
│   │   └── generate_recommendations/
│   │       ├── handler.py
│   │       └── requirements.txt
│   │
│   ├── tests/                         # Test files
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_api/
│   │   ├── test_services/
│   │   └── test_utils/
│   │
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pytest.ini
│   ├── pyproject.toml                 # Black, Ruff, mypy config
│   └── .env                           # Local environment variables
│
├── infrastructure/                    # Infrastructure as Code
│   ├── cdk/                           # AWS CDK (or CloudFormation/SAM)
│   │   ├── app.py
│   │   ├── stacks/
│   │   │   ├── database.py            # RDS PostgreSQL
│   │   │   ├── api.py                 # Lambda + API Gateway
│   │   │   ├── auth.py                # Cognito
│   │   │   ├── storage.py             # S3 buckets
│   │   │   └── events.py              # EventBridge rules
│   │   └── cdk.json
│   └── scripts/                       # Deployment scripts
│
├── docs/                              # Documentation
│   ├── architecture.md                # This file
│   ├── api.md                         # API documentation
│   └── deployment.md                  # Deployment guide
│
├── .github/
│   └── workflows/
│       ├── ci.yml                     # CI pipeline
│       └── deploy.yml                 # Deployment pipeline
│
└── README.md
```

## Epic to Architecture Mapping

| Epic | Components | Location | Key Technologies |
|------|-----------|----------|------------------|
| Authentication & Authorization | Login, Consent Modal, JWT validation | `frontend/src/features/auth/`, `backend/app/api/v1/auth.py`, `backend/app/services/auth_service.py` | AWS Cognito, React Router |
| Consumer Dashboard - Transactions | Transaction table, filters, pagination | `frontend/src/features/consumer/dashboard/tabs/TransactionsTab.tsx` | React Query, shadcn/ui Table |
| Consumer Dashboard - Insights | Charts, summary cards | `frontend/src/features/consumer/dashboard/tabs/InsightsTab.tsx` | Recharts, React Query |
| Consumer Dashboard - Education | Education cards, rationale boxes | `frontend/src/features/consumer/dashboard/tabs/EducationTab.tsx` | Custom EducationCard component |
| Consumer Dashboard - Offers | Offer cards, eligibility logic | `frontend/src/features/consumer/dashboard/tabs/OffersTab.tsx` | Custom components |
| Consumer Dashboard - Chat | Chat widget, AI integration | `frontend/src/features/consumer/chat/` | OpenAI/Claude API, React Query |
| Operator Dashboard - User List | User table, filters, search | `frontend/src/features/operator/UserList/` | OperatorDataTable component |
| Operator Dashboard - User Detail | User overview, signals, recommendations, traces | `frontend/src/features/operator/UserDetail/` | DecisionTraceViewer component |
| Behavioral Signal Detection | Feature computation logic | `backend/app/services/signal_detection.py`, `backend/lambdas/compute_features/` | Pandas, AWS Lambda, EventBridge |
| Persona Assignment | Persona logic | `backend/app/services/persona_assignment.py`, `backend/lambdas/assign_persona/` | AWS Lambda, EventBridge |
| Recommendation Engine | Recommendation generation | `backend/app/services/recommendation_engine.py`, `backend/lambdas/generate_recommendations/` | OpenAI/Claude API, AWS Lambda |
| Consent Management | Consent tracking | `backend/app/services/consent_service.py`, `backend/app/api/v1/consumer.py` | RDS PostgreSQL, FastAPI |

## Technology Stack Details

### Core Technologies

**Frontend:**
- React 18.x - UI framework
- TypeScript 5.x - Type safety
- Vite - Build tool and dev server
- Tailwind CSS 3.x - Utility-first CSS
- shadcn/ui - Component library
- React Query (TanStack Query) - Server state management
- React Router 6.x - Client-side routing
- Recharts - Data visualization
- date-fns - Date manipulation

**Backend:**
- FastAPI - Web framework
- Python 3.11+ - Programming language
- Mangum - ASGI adapter for Lambda
- Pydantic - Data validation
- SQLAlchemy - ORM (optional, or use raw SQL)
- boto3 - AWS SDK
- pandas - Data processing
- OpenAI/Anthropic - LLM APIs

**Infrastructure:**
- AWS RDS PostgreSQL 15.x - Database
- AWS Cognito - Authentication
- AWS Lambda - Serverless compute
- API Gateway - API management
- S3 + CloudFront - Frontend hosting
- EventBridge - Event-driven architecture
- CloudWatch - Logging and monitoring
- Secrets Manager - Secret storage

### Integration Points

**Frontend ↔ Backend:**
- REST API via API Gateway
- JWT tokens in Authorization header
- React Query for data fetching and caching

**Backend ↔ Database:**
- Direct connection to RDS PostgreSQL
- Connection pooling for Lambda functions
- SQLAlchemy ORM or raw SQL queries

**Backend ↔ AWS Services:**
- Cognito for user authentication
- S3 for file storage
- EventBridge for triggering background jobs
- CloudWatch for logging
- Secrets Manager for configuration

**Background Jobs:**
- EventBridge triggers Lambda functions
- Lambda functions compute features, assign personas, generate recommendations
- Results stored in RDS PostgreSQL

## Novel Pattern Designs

### Rationale Box Pattern

**Purpose:** Display explainable AI rationales for recommendations

**Components:**
- `RationaleBox` component (frontend)
- Rationale generation in recommendation engine (backend)

**Data Flow:**
1. Recommendation engine generates rationale with data points
2. Rationale stored with recommendation in database
3. Frontend displays rationale in highlighted box
4. Format: "We're showing you this because [specific data point]"

**Implementation:**
- Visual: Light blue background (#eff6ff), left border accent
- Component: Reusable React component with consistent styling
- Content: Template-based with variable substitution

### Decision Trace Transparency Pattern

**Purpose:** Full auditability of recommendation generation for operators

**Components:**
- `DecisionTraceViewer` component (frontend)
- Decision trace storage in database (backend)
- JSON schema for trace format

**Data Flow:**
1. Recommendation generation creates decision trace
2. Trace stored as JSON in `decision_traces` table
3. Operator views trace in modal with syntax highlighting
4. Trace includes: persona match, signals used, template ID, guardrails passed

**Implementation:**
- JSON viewer component with collapsible sections
- Syntax highlighting for readability
- Copy-to-clipboard functionality

## Implementation Patterns

These patterns ensure consistent implementation across all AI agents:

### Naming Patterns

**API Routes:**
- REST endpoints: `/api/v1/{resource}/{id?}`
- Plural resource names: `/api/v1/users`, `/api/v1/transactions`
- Nested resources: `/api/v1/users/{user_id}/recommendations`

**Database Tables:**
- Snake_case: `user_profiles`, `consent_records`, `computed_features`
- Singular for lookup tables, plural for collections

**React Components:**
- PascalCase: `UserCard.tsx`, `EducationCard.tsx`
- Feature-based organization in `features/` directory

**Python Modules:**
- Snake_case: `auth_service.py`, `signal_detection.py`
- Service files end with `_service.py`

**Variables/Functions:**
- Frontend: camelCase (TypeScript/React conventions)
- Backend: snake_case (Python conventions)

### Structure Patterns

**Frontend:**
- Feature-based organization in `src/features/`
- Shared components in `src/components/`
- Utilities in `src/lib/`
- Tests co-located: `*.test.tsx` or `__tests__/` folders

**Backend:**
- API routes in `app/api/v1/`
- Business logic in `app/services/`
- Data models in `app/models/`
- Database layer in `app/database/`
- Tests in `tests/` directory mirroring structure

**Lambda Functions:**
- Each function in separate directory under `backend/lambdas/`
- Each has `handler.py` and `requirements.txt`

### Format Patterns

**API Requests:**
- Content-Type: `application/json`
- Authentication: Bearer token in `Authorization` header

**API Responses:**
- Success: `{data: {...}, meta: {timestamp: "ISO8601"}}`
- Error: `{error: {code: "ERROR_CODE", message: "...", details: {...}}}`

**Date Format:**
- Storage: ISO 8601 UTC timestamps in database
- API: ISO 8601 strings
- Display: User's local timezone formatted

**Error Codes:**
- Format: `SCREAMING_SNAKE_CASE`
- Examples: `VALIDATION_ERROR`, `AUTHENTICATION_FAILED`, `NOT_FOUND`

### Communication Patterns

**Frontend → Backend:**
- React Query mutations for POST/PUT/DELETE
- React Query queries for GET requests
- Automatic retry on failure (3 attempts)

**Backend → Database:**
- Connection pooling for Lambda functions
- Transaction management for multi-step operations

**Background Jobs:**
- EventBridge events trigger Lambda functions
- Event payload: `{event_type: "...", user_id: "...", timestamp: "..."}`

### Lifecycle Patterns

**Loading States:**
- React Query provides `isLoading` and `isFetching` states
- Skeleton screens for content loading
- Spinner for action buttons

**Error Recovery:**
- React Query automatic retry (3 attempts)
- User-friendly error messages
- Fallback UI for critical errors

**State Updates:**
- Optimistic updates for mutations where appropriate
- Cache invalidation after mutations
- Background refetch for stale data

### Location Patterns

**API Routes:**
- Base URL: `https://api.spendsense.com/api/v1`
- Environment-based: `VITE_API_URL` in frontend `.env`

**Static Assets:**
- Partner logos: S3 bucket `spendsense-assets/logos/`
- Frontend build: S3 bucket `spendsense-frontend/`

**Environment Variables:**
- Frontend: `.env.local` (gitignored)
- Backend: AWS Secrets Manager in production
- Local development: `.env` files

### Consistency Patterns

**Date Display:**
- Relative for recent: "2 hours ago", "3 days ago"
- Absolute for older: "Nov 3, 2025"
- Use `date-fns` `formatDistanceToNow` and `format`

**Logging Format:**
- Structured JSON: `{timestamp, level, service, message, context}`
- No PII in logs
- Context includes request_id, user_id (hashed)

**Error Messages:**
- User-facing: Clear, actionable, no technical jargon
- Logged: Detailed with stack traces and context

## Consistency Rules

### Naming Conventions

**Frontend:**
- Components: PascalCase (`UserCard.tsx`)
- Files: Match component name
- Hooks: `use` prefix (`useAuth.ts`, `useTransactions.ts`)
- Constants: SCREAMING_SNAKE_CASE (`API_BASE_URL`)

**Backend:**
- Modules: snake_case (`auth_service.py`)
- Classes: PascalCase (`UserService`)
- Functions: snake_case (`get_user_by_id`)
- Constants: SCREAMING_SNAKE_CASE (`DEFAULT_PAGE_SIZE`)

### Code Organization

**Frontend:**
- Feature-based structure in `src/features/`
- Shared components in `src/components/ui/`
- API client in `src/lib/api/`
- Types in `src/types/` or co-located with components

**Backend:**
- API routes grouped by domain in `app/api/v1/`
- Services contain business logic
- Models define data structures
- Repositories handle data access

**Tests:**
- Co-located with source files or in `__tests__/`
- Naming: `*.test.tsx` or `*.test.py`
- Test data in `__fixtures__/` or `tests/fixtures/`

### Error Handling

**Frontend:**
- React Error Boundaries for component errors
- React Query error handling for API errors
- User-friendly error messages displayed
- Technical errors logged to console (dev only)

**Backend:**
- FastAPI exception handlers for HTTP errors
- Structured error responses
- All errors logged to CloudWatch
- Validation errors return 400 with details

**Error Response Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  }
}
```

### Logging Strategy

**Frontend:**
- Development: Console logging
- Production: Structured logs to monitoring service (if added)

**Backend:**
- Structured JSON logs to CloudWatch
- Levels: DEBUG, INFO, WARN, ERROR
- Context: Request ID, user ID (hashed), timestamp
- No PII in logs

**Log Format:**
```json
{
  "timestamp": "2025-11-03T10:30:00Z",
  "level": "INFO",
  "service": "recommendation_engine",
  "message": "Generated recommendation",
  "context": {
    "request_id": "req_123",
    "user_id": "user_abc",
    "recommendation_id": "rec_xyz"
  }
}
```

## Data Architecture

### Database Schema Overview

**Core Tables:**
- `user_profiles` - User information and roles (consumer/operator)
- `consent_records` - Consent audit trail
- `accounts` - Synthetic bank accounts
- `transactions` - Transaction history
- `computed_features` - Cached behavioral signals
- `persona_assignments` - Persona tracking over time windows
- `recommendations` - Generated recommendations
- `decision_traces` - Full auditability logs
- `chat_logs` - Chat history with guardrails status
- `operator_actions` - Operator audit log

**Relationships:**
- `user_profiles` → `consent_records` (one-to-many)
- `user_profiles` → `accounts` (one-to-many)
- `accounts` → `transactions` (one-to-many)
- `user_profiles` → `computed_features` (one-to-many, time-windowed)
- `user_profiles` → `persona_assignments` (one-to-many, time-windowed)
- `user_profiles` → `recommendations` (one-to-many)
- `recommendations` → `decision_traces` (one-to-one)
- `user_profiles` → `chat_logs` (one-to-many)
- `user_profiles` → `operator_actions` (one-to-many, for operators)

**Indexes:**
- `user_profiles.email` - Unique index
- `transactions.user_id, date` - Composite index for queries
- `computed_features.user_id, time_window` - Composite index
- `persona_assignments.user_id, time_window` - Composite index

## API Contracts

### Authentication Endpoints

**POST /api/v1/auth/login**
- Request: `{email: string, password: string}`
- Response: `{data: {token: string, user: {...}}, meta: {...}}`
- Errors: 401 Unauthorized

**POST /api/v1/auth/logout**
- Request: `{token: string}`
- Response: `{data: {success: true}, meta: {...}}`

### Consumer Endpoints

**GET /api/v1/users/me/profile**
- Response: `{data: {user: {...}, consent_status: boolean}, meta: {...}}`
- Auth: Required

**GET /api/v1/users/me/accounts**
- Response: `{data: {accounts: [...]}, meta: {...}}`
- Auth: Required

**GET /api/v1/users/me/transactions**
- Query params: `?start_date=ISO8601&end_date=ISO8601&category=...&merchant=...&page=1&limit=50`
- Response: `{data: {transactions: [...], pagination: {...}}, meta: {...}}`
- Auth: Required

**GET /api/v1/users/me/insights**
- Query params: `?period=30d|90d`
- Response: `{data: {charts: {...}, summary: {...}}, meta: {...}}`
- Auth: Required

**GET /api/v1/users/me/recommendations**
- Response: `{data: {education: [...], offers: [...]}, meta: {...}}`
- Auth: Required

**POST /api/v1/users/me/consent**
- Request: `{granted: boolean, ip_address?: string}`
- Response: `{data: {consent_record: {...}}, meta: {...}}`
- Auth: Required

**POST /api/v1/chat**
- Request: `{message: string}`
- Response: `{data: {response: string, citations: [...]}, meta: {...}}`
- Auth: Required
- Rate limit: 10 messages per minute

### Operator Endpoints

**GET /api/v1/operator/users**
- Query params: `?search=...&persona=...&risk_flag=...&page=1&limit=50`
- Response: `{data: {users: [...], pagination: {...}}, meta: {...}}`
- Auth: Required (operator role)

**GET /api/v1/operator/users/{user_id}**
- Response: `{data: {user: {...}, signals: {...}, recommendations: [...]}, meta: {...}}`
- Auth: Required (operator role)

**GET /api/v1/operator/users/{user_id}/signals**
- Response: `{data: {signals: {...}}, meta: {...}}`
- Auth: Required (operator role)

**GET /api/v1/operator/users/{user_id}/traces/{recommendation_id}**
- Response: `{data: {trace: {...}}, meta: {...}}`
- Auth: Required (operator role)

**POST /api/v1/operator/users/{user_id}/override**
- Request: `{recommendation_id: string, reason: string}`
- Response: `{data: {action: {...}}, meta: {...}}`
- Auth: Required (operator role)

## Security Architecture

**Authentication:**
- AWS Cognito User Pools for user authentication
- JWT tokens for API authorization
- Token refresh mechanism
- Role-based access control (consumer vs operator)

**Authorization:**
- JWT token validation on all protected endpoints
- Role checking for operator endpoints
- User data isolation (users can only access their own data)

**Data Protection:**
- Encryption in transit: HTTPS/TLS
- Encryption at rest: RDS encryption, S3 encryption
- No PII in logs or decision traces
- IP address logging for consent audit trail

**API Security:**
- Rate limiting on all endpoints
- CORS configured for frontend domain only
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)

**Secrets Management:**
- AWS Secrets Manager for production secrets
- Environment variables for local development
- No secrets in code or version control

## Performance Considerations

**Frontend:**
- Code splitting with Vite
- Lazy loading for routes
- Image optimization
- React Query caching (5min stale time, 30min cache time)
- CDN delivery via CloudFront

**Backend:**
- Lambda cold start mitigation (provisioned concurrency if needed)
- Connection pooling for RDS
- Cached computed features (stored in database)
- Background job processing (async, non-blocking)

**Database:**
- Indexed queries
- Query optimization
- Connection pooling
- Read replicas if needed (future)

**API:**
- Response time target: <500ms (95th percentile)
- Lambda timeout: 30 seconds (API), 5 minutes (background jobs)
- API Gateway caching for static data

## Deployment Architecture

**Frontend:**
- Build: Vite production build
- Hosting: S3 bucket `spendsense-frontend`
- CDN: CloudFront distribution
- CI/CD: GitHub Actions → Build → Deploy to S3 → Invalidate CloudFront

**Backend API:**
- Runtime: AWS Lambda (Python 3.11)
- Gateway: API Gateway REST API
- CI/CD: GitHub Actions → Build → Deploy Lambda via SAM/Serverless Framework

**Background Jobs:**
- Runtime: AWS Lambda functions
- Trigger: EventBridge rules (scheduled or event-based)
- CI/CD: Same as API Lambda functions

**Database:**
- Service: AWS RDS PostgreSQL
- Instance: db.t3.micro (MVP), scale as needed
- Backups: Automated daily backups
- Multi-AZ: Not required for MVP

**Infrastructure as Code:**
- AWS CDK or CloudFormation/SAM
- Version controlled in `infrastructure/` directory
- Environment-specific stacks (dev, staging, prod)

## Development Environment

### Prerequisites

**Frontend:**
- Node.js 18.x or later
- npm or yarn

**Backend:**
- Python 3.11 or later
- pip
- AWS CLI (for deployment)
- AWS credentials configured

**Database:**
- AWS RDS PostgreSQL instance (or local PostgreSQL for development)

**Tools:**
- Git
- VS Code (recommended) or any IDE
- Docker (optional, for local development)

### Setup Commands

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev  # Start dev server
```

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
uvicorn app.main:app --reload  # Start dev server
```

**Database Setup:**
- Create RDS PostgreSQL instance via AWS Console or CDK
- Run migrations (to be created)
- Seed demo data (to be created)

**Environment Variables:**

Frontend `.env.local`:
```
VITE_API_URL=https://api.spendsense.com/api/v1
VITE_COGNITO_USER_POOL_ID=...
VITE_COGNITO_CLIENT_ID=...
```

Backend `.env`:
```
DATABASE_URL=postgresql://user:pass@host:5432/dbname
COGNITO_USER_POOL_ID=...
COGNITO_CLIENT_ID=...
AWS_REGION=us-east-1
OPENAI_API_KEY=...  # or ANTHROPIC_API_KEY
```

## Architecture Decision Records (ADRs)

### ADR-001: AWS over Supabase

**Decision:** Use AWS services (RDS, Cognito, S3, Lambda) instead of Supabase

**Rationale:** User has AWS access, more control and flexibility, enterprise-grade infrastructure

**Consequences:**
- More setup required (no all-in-one platform)
- More control over infrastructure
- Better scalability options
- More AWS-specific knowledge needed

### ADR-002: Serverless Backend (Lambda + API Gateway)

**Decision:** Deploy FastAPI backend as Lambda functions with API Gateway

**Rationale:** Auto-scaling, cost-effective for MVP, pay-per-use model

**Consequences:**
- Cold start latency (mitigated with provisioned concurrency if needed)
- 15-minute timeout limit (sufficient for API endpoints)
- Stateless design required

### ADR-003: React Query for State Management

**Decision:** Use React Query + Context API instead of Redux

**Rationale:** Simpler API, built-in caching, better for server state management

**Consequences:**
- Less boilerplate than Redux
- Excellent caching and refetching
- May need Context API for UI-only state

### ADR-004: Event-Driven Background Jobs

**Decision:** Use EventBridge + Lambda for background job processing

**Rationale:** Serverless, scalable, separates concerns from API

**Consequences:**
- Async processing (may have slight delay)
- Independent scaling
- Easier to monitor and debug

### ADR-005: S3 + CloudFront for Frontend Hosting

**Decision:** Host frontend on S3 with CloudFront CDN instead of Vercel

**Rationale:** Consistent AWS stack, cost-effective, global CDN

**Consequences:**
- Manual deployment setup (vs Vercel's automatic)
- More control over CDN configuration
- Slightly more complex CI/CD

---

_Generated by BMAD Decision Architecture Workflow v1.3.2_
_Date: 2025-11-03_
_For: Alexis_


