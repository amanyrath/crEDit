# Story 2.5: Implement Role-Based Access Control

Status: ready-for-dev

## Story

As an operator,
I want to access operator-specific features,
so that I can audit recommendations and monitor users.

## Acceptance Criteria

1. FastAPI dependency created for role checking: `require_role(role: str)`
2. Consumer endpoints check for "consumer" role (or default authenticated user)
3. Operator endpoints check for "operator" role
4. 403 Forbidden returned if user doesn't have required role
5. Role extracted from JWT token custom claims
6. Role-based route protection implemented:
   - `/api/v1/users/me/*` - Consumer role
   - `/api/v1/operator/*` - Operator role only
7. Frontend routes protected based on user role
8. Operator dashboard only accessible to operators

## Tasks / Subtasks

- [x] Task 1: Understand JWT token structure and role claims (AC: #5)
  - [x] Review Cognito JWT token structure
  - [x] Identify where role information is stored in token (groups claim or custom:role claim)
  - [x] Understand how Cognito user groups map to JWT claims
  - [x] Document token claim structure for roles

- [x] Task 2: Create role extraction utility (AC: #5)
  - [x] Create function to extract role from JWT token claims
  - [x] Handle case where role is in `cognito:groups` claim (primary method)
  - [x] Handle fallback to `custom:role` claim if groups not present
  - [x] Default to "consumer" role if no role information found
  - [x] Add unit tests for role extraction logic

- [x] Task 3: Create FastAPI dependency for role checking (AC: #1, #2, #3, #4)
  - [x] Create `require_role(role: str)` dependency function in `app/dependencies.py`
  - [x] Dependency should depend on `get_current_user()` (from Story 2.3)
  - [x] Check if user's role matches required role
  - [x] Raise HTTPException with 403 status if role doesn't match
  - [x] Create convenience dependency `require_operator()` for operator-only endpoints
  - [x] Create convenience dependency `require_consumer()` for consumer endpoints (allows default authenticated users)

- [x] Task 4: Implement backend role-based route protection (AC: #6)
  - [x] Create `/api/v1/users/me/` endpoint with consumer role protection
  - [x] Create `/api/v1/operator/` endpoint group with operator role protection
  - [x] Add example consumer endpoint (e.g., `/api/v1/users/me/profile`)
  - [x] Add example operator endpoint (e.g., `/api/v1/operator/users`)
  - [x] Test that consumer endpoints reject operator-only access (if applicable)
  - [x] Test that operator endpoints reject consumer access

- [x] Task 5: Update frontend auth context with role (AC: #7, #8)
  - [x] Extract role from JWT token in frontend (from ID token or access token)
  - [x] Add `role` field to auth context/user state
  - [x] Update `useAuth` hook to include role information
  - [x] Ensure role is available after login and token refresh

- [x] Task 6: Create frontend role-based route protection (AC: #7, #8)
  - [x] Create `RequireRole` component or update `ProtectedRoute` to check roles
  - [x] Protect operator dashboard routes with operator role requirement
  - [x] Redirect to appropriate page if user lacks required role
  - [x] Show appropriate error message for unauthorized access attempts

- [x] Task 7: Create operator dashboard placeholder (AC: #8)
  - [x] Create basic operator dashboard page/route (`/operator/dashboard`)
  - [x] Add route to App.tsx with role protection
  - [x] Create placeholder content for operator dashboard
  - [x] Test that only operators can access the dashboard

- [x] Task 8: Create unit tests for role checking (AC: #1, #2, #3, #4)
  - [x] Test `require_role()` dependency with valid role
  - [x] Test `require_role()` dependency with invalid role (should return 403)
  - [x] Test `require_operator()` dependency
  - [x] Test `require_consumer()` dependency
  - [x] Test role extraction from token claims
  - [x] Mock JWT tokens with different role configurations

- [x] Task 9: Create integration tests for protected endpoints (AC: #6)
  - [x] Test consumer endpoint with consumer role (should succeed)
  - [x] Test consumer endpoint with operator role (should succeed if consumer endpoints allow all authenticated users)
  - [x] Test operator endpoint with consumer role (should return 403)
  - [x] Test operator endpoint with operator role (should succeed)
  - [x] Test endpoints without authentication (should return 401)

- [x] Task 10: Update documentation (AC: #1, #6, #7)
  - [x] Document role-based access control usage in README
  - [x] Add examples of how to use `require_role()` in route handlers
  - [x] Document frontend role-based route protection
  - [x] Update architecture documentation if needed

## Dev Notes

### Architecture Patterns and Constraints

- **Backend Framework**: FastAPI with dependency injection pattern [Source: docs/architecture.md#Decision-Summary]
- **Authentication**: AWS Cognito JWT tokens [Source: Story 2.3]
- **Role Source**: Cognito user groups (primary) or custom:role attribute (fallback) [Source: Story 1.5]
- **Dependency Injection**: FastAPI dependencies for authorization [Source: docs/epics.md#Story-2.5]
- **Error Handling**: HTTPException with 403 Forbidden for unauthorized access [Source: docs/epics.md#Story-2.5]
- **Frontend**: React with role-based route protection [Source: docs/epics.md#Story-2.5]

### Project Structure Notes

The role-based access control should be organized as follows:
```
spendsense-backend/
├── app/
│   ├── dependencies.py          # FastAPI dependencies: get_current_user(), require_role(), require_operator()
│   ├── utils/
│   │   └── jwt.py               # JWT utilities (includes role extraction, from Story 2.3)
│   ├── api/
│   │   └── v1/
│   │       ├── consumer.py      # Consumer endpoints (/api/v1/users/me/*)
│   │       └── operator.py      # Operator endpoints (/api/v1/operator/*)
│   └── ...
├── tests/
│   ├── test_rbac.py             # Unit tests for role checking
│   └── test_protected_endpoints.py  # Integration tests for protected endpoints
└── ...

spendsense-frontend/
├── src/
│   ├── components/
│   │   └── ProtectedRoute.tsx   # Updated to support role-based protection
│   ├── hooks/
│   │   └── useAuth.ts            # Updated to include role information
│   ├── pages/
│   │   └── OperatorDashboard.tsx # Operator dashboard page
│   └── ...
└── ...
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **JWT Token Role Claims**:
   - Cognito stores user groups in the `cognito:groups` claim in the access token
   - If user is in "consumers" group, claim will contain `["consumers"]`
   - If user is in "operators" group, claim will contain `["operators"]`
   - Users can be in multiple groups
   - Fallback: Check `custom:role` attribute if groups claim not present
   - Default: If no role information, default to "consumer" role

2. **Role Extraction Flow**:
   ```
   1. Decode JWT token (already done by get_current_user())
   2. Check `cognito:groups` claim in access token
   3. If "operators" group present → role = "operator"
   4. Else if "consumers" group present → role = "consumer"
   5. Else check `custom:role` claim → use that value
   6. Else default to "consumer"
   ```

3. **FastAPI Dependency Pattern**:
   ```python
   from fastapi import Depends, HTTPException
   from app.dependencies import get_current_user, require_role, require_operator
   
   @app.get("/api/v1/users/me/profile")
   async def get_profile(current_user: UserInfo = Depends(require_consumer)):
       # Consumer-only endpoint
       return {"user_id": current_user.user_id}
   
   @app.get("/api/v1/operator/users")
   async def list_users(current_user: UserInfo = Depends(require_operator)):
       # Operator-only endpoint
       return {"users": []}
   ```

4. **Error Handling**:
   - Missing authentication: 401 Unauthorized (handled by `get_current_user()`)
   - Insufficient role: 403 Forbidden (handled by `require_role()`)
   - Error message: "Insufficient permissions. Required role: {role}"

5. **Frontend Role Protection**:
   - Extract role from ID token or access token after login
   - Store role in auth context/state
   - Check role before rendering protected routes
   - Redirect to appropriate page (e.g., dashboard) if unauthorized
   - Show error message: "You don't have permission to access this page"

6. **Security Considerations**:
   - Always validate token signature and expiration before checking role
   - Never trust role information from unvalidated tokens
   - Role checks should happen after authentication checks
   - Log unauthorized access attempts for security monitoring

### Learnings from Previous Stories

**From Story 2.3 (Status: ready-for-dev)**
- JWT validation will be implemented with `get_current_user()` dependency
- Token structure and claim extraction patterns
- Error handling patterns for authentication failures

**From Story 1.5 (Status: review)**
- Cognito User Pool configuration with user groups
- User groups: "consumers" and "operators"
- Groups are primary mechanism for role assignment
- Custom:role attribute can be used as fallback

**From Story 2.2 (Status: review)**
- Frontend authentication patterns with Amplify Auth
- Token storage and refresh patterns
- Auth context structure

### References

- [Source: docs/epics.md#Story-2.5]
- [Source: docs/architecture.md#Decision-Summary]
- [Source: docs/architecture.md#Project-Structure]
- [Source: Story 2.3 implementation]
- [Source: Story 1.5 implementation]
- [Source: Story 2.2 implementation]
- [Source: AWS Cognito JWT Token Claims Documentation]
- [Source: FastAPI Dependencies Documentation]

## Dev Agent Record

### Context Reference

- `docs/stories/2-5-implement-role-based-access-control.context.xml` (to be created)

### Agent Model Used

AI Assistant (Claude Sonnet 4.5)

### Debug Log References

- Implemented JWT validation foundation as prerequisite for RBAC
- Created role extraction utility with priority: cognito:groups > custom:role > default consumer
- Implemented FastAPI dependencies for role-based access control
- Created protected endpoints for consumer and operator roles
- Updated frontend to extract and use role information from tokens
- Added role-based route protection in frontend ProtectedRoute component

### Completion Notes List

- Implemented complete role-based access control system for both backend and frontend
- Created JWT validation utilities (extended Story 2.3 scope) as prerequisite
- Backend: FastAPI dependencies (require_role, require_operator, require_consumer) with proper error handling
- Backend: Protected endpoints at /api/v1/users/me/* (consumer) and /api/v1/operator/* (operator)
- Frontend: Updated useAuth hook to extract role from Cognito tokens (access token groups claim)
- Frontend: Enhanced ProtectedRoute component with optional requiredRole prop
- Frontend: Created OperatorDashboardPage with role protection
- Tests: Comprehensive unit and integration tests for RBAC functionality
- Documentation: Added RBAC section to backend README with usage examples

### File List

Backend:
- Created: `spendsense-backend/app/utils/jwt.py`
- Created: `spendsense-backend/app/utils/models.py`
- Created: `spendsense-backend/app/utils/__init__.py`
- Created: `spendsense-backend/app/api/v1/consumer.py`
- Created: `spendsense-backend/app/api/v1/operator.py`
- Created: `spendsense-backend/tests/test_rbac.py`
- Modified: `spendsense-backend/app/dependencies.py`
- Modified: `spendsense-backend/app/main.py`
- Modified: `spendsense-backend/requirements.txt`
- Modified: `spendsense-backend/README.md`

Frontend:
- Created: `spendsense-frontend/src/pages/OperatorDashboardPage.tsx`
- Modified: `spendsense-frontend/src/hooks/useAuth.ts`
- Modified: `spendsense-frontend/src/components/ProtectedRoute.tsx`
- Modified: `spendsense-frontend/src/App.tsx`

Story:
- Created: `docs/stories/2-5-implement-role-based-access-control.md`

## Change Log

- 2025-11-03: Story created and drafted
- 2025-11-03: Story implementation completed, all tasks done, ready for review

