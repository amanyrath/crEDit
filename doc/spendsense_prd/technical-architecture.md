# Technical Architecture

## Stack Overview

**Frontend:**
- React 18 with Vite
- Tailwind CSS for styling
- Recharts for data visualization
- AWS Amplify (or AWS SDK) for authentication
- React Router for navigation

**Backend:**
- FastAPI (Python 3.11+)
- boto3 (AWS SDK for Python) for AWS service integration
- Pandas for feature computation
- OpenAI API for chat (or Claude)
- Pydantic for data validation

**Database:**
- AWS RDS PostgreSQL
- Application-layer security (data access enforced in application code)
- Automated backups

**Deployment:**
- Frontend: Amazon S3 + CloudFront
- Backend: AWS Lambda + API Gateway (serverless)
- Background Jobs: AWS Lambda + EventBridge
- Database: AWS RDS PostgreSQL (managed)

**File Storage:**
- Amazon S3 (for partner logos and static content)

---

## Database Schema

See detailed schema in "Database Schema" section above. Key tables:
- `profiles` - User roles and metadata
- `consent_records` - Consent audit trail
- `accounts` - Synthetic bank accounts
- `transactions` - Transaction history
- `computed_features` - Cached feature computations
- `persona_assignments` - Persona tracking
- `recommendations` - Generated recommendations
- `decision_traces` - Auditability logs
- `chat_logs` - Chat history with guardrails status
- `operator_actions` - Operator audit log

---

## API Endpoints

**Authentication:**
- Handled by AWS Cognito User Pools (signup, login, logout, token refresh)

**Consumer Endpoints:**
```
GET  /api/users/me/profile          # User profile + consent status
GET  /api/users/me/accounts         # List of accounts
GET  /api/users/me/transactions     # Transaction list with filters
GET  /api/users/me/insights         # Computed charts data
GET  /api/users/me/recommendations  # Education + offers
POST /api/users/me/consent          # Grant/revoke consent
POST /api/chat                      # Chat with AI agent
```

**Operator Endpoints:**
```
GET  /api/operator/users                    # User list
GET  /api/operator/users/{user_id}          # User detail
GET  /api/operator/users/{user_id}/signals  # Behavioral signals
GET  /api/operator/users/{user_id}/traces   # Decision traces
POST /api/operator/users/{user_id}/override # Override recommendation
```

**Health Check:**
```
GET  /health  # API health status
```

---

## Data Flow

**User Login → Dashboard Load:**
1. User logs in via AWS Cognito
2. Frontend retrieves JWT token from Cognito
3. Check consent status (from RDS database)
4. If no consent → show modal → on accept, record in DB
5. If consent granted → fetch pre-computed features
6. Render dashboard with transactions, insights, education, offers

**Recommendation Generation (Background Job):**
1. Trigger: New user signup or daily refresh
2. Fetch user transactions from DB
3. Run feature detection (subscriptions, credit, savings, income)
4. Store computed features in `computed_features` table
5. Run persona assignment logic
6. Store persona in `persona_assignments` table
7. Generate recommendations from content catalog
8. Apply eligibility filters and tone guardrails
9. Store recommendations + decision traces
10. Mark as ready for user

**Operator Audit:**
1. Operator logs in
2. Views user list
3. Clicks user → fetch all data for that user
4. Views behavioral signals (from `computed_features`)
5. Views recommendations (from `recommendations`)
6. Clicks "Decision Trace" → fetch from `decision_traces`
7. Reviews JSON of how recommendation was generated
8. Can override or flag for review (logged in `operator_actions`)

---
