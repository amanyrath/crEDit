# Story 2.3: Implement JWT Token Validation (Backend)

Status: ready-for-dev

## Story

As a developer,
I want to validate JWT tokens from Cognito on the backend,
so that only authenticated users can access protected API endpoints.

## Acceptance Criteria

1. FastAPI dependency created for JWT validation
2. JWT token extracted from `Authorization: Bearer <token>` header
3. Token signature verified using Cognito public keys (JWKS)
4. Token expiration checked
5. User ID and role extracted from token claims
6. Invalid tokens return 401 Unauthorized
7. Expired tokens return 401 with appropriate error message
8. Validated user info available in route handlers
9. Middleware or dependency injection pattern used

## Tasks / Subtasks

- [ ] Task 1: Install JWT validation dependencies (AC: #3, #4, #5)
  - [ ] Install python-jose: `pip install python-jose[cryptography]`
  - [ ] Install requests for JWKS fetching: `pip install requests`
  - [ ] Verify all packages installed correctly
  - [ ] Update requirements.txt with new dependencies

- [ ] Task 2: Create JWT utilities module (AC: #3, #4, #5)
  - [ ] Create `app/utils/jwt.py` module
  - [ ] Implement function to fetch Cognito JWKS keys
  - [ ] Implement JWKS caching mechanism (in-memory cache with TTL)
  - [ ] Implement function to get signing key from JWKS based on token header
  - [ ] Implement function to decode and verify JWT token
  - [ ] Extract user ID (`sub` claim) from token
  - [ ] Extract role from token custom claims (if present)
  - [ ] Handle token expiration validation
  - [ ] Handle invalid token signature errors

- [ ] Task 3: Create FastAPI dependency for JWT validation (AC: #1, #2, #6, #7, #8, #9)
  - [ ] Create `get_current_user()` dependency in `app/dependencies.py`
  - [ ] Extract `Authorization` header from request
  - [ ] Parse `Bearer <token>` format
  - [ ] Validate token using JWT utilities
  - [ ] Return user info (user_id, role) if token is valid
  - [ ] Raise HTTPException with 401 status for invalid tokens
  - [ ] Raise HTTPException with 401 status and appropriate message for expired tokens
  - [ ] Raise HTTPException with 401 status for missing/invalid Authorization header

- [ ] Task 4: Configure Cognito settings (AC: #3)
  - [ ] Add Cognito User Pool ID to environment variables
  - [ ] Add Cognito region to environment variables
  - [ ] Update `.env.example` with Cognito configuration
  - [ ] Update `app/config.py` to include Cognito settings
  - [ ] Construct Cognito JWKS URL (format: `https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json`)

- [ ] Task 5: Create user info model (AC: #8)
  - [ ] Create Pydantic model for user info (e.g., `UserInfo` or `CurrentUser`)
  - [ ] Include fields: `user_id` (from `sub` claim), `role` (from custom claims, optional)
  - [ ] Add type hints for better IDE support

- [ ] Task 6: Create protected route example (AC: #8, #9)
  - [ ] Create example protected endpoint in `app/api/v1/` (e.g., `auth.py` or `consumer.py`)
  - [ ] Use `get_current_user()` dependency in route handler
  - [ ] Demonstrate accessing user info in route handler
  - [ ] Verify dependency injection pattern works correctly

- [ ] Task 7: Add error handling and logging (AC: #6, #7)
  - [ ] Add logging for JWT validation failures (invalid signature, expired token, etc.)
  - [ ] Ensure error messages are clear and don't leak sensitive information
  - [ ] Log token validation attempts for debugging (without logging token itself)
  - [ ] Handle JWKS fetch failures gracefully

- [ ] Task 8: Create unit tests for JWT validation (AC: #1, #2, #3, #4, #5, #6, #7)
  - [ ] Create test file: `tests/test_jwt.py`
  - [ ] Test JWKS fetching and caching
  - [ ] Test token signature verification with valid token
  - [ ] Test token signature verification with invalid token
  - [ ] Test token expiration validation
  - [ ] Test user ID and role extraction from token claims
  - [ ] Test `get_current_user()` dependency with valid token
  - [ ] Test `get_current_user()` dependency with missing Authorization header
  - [ ] Test `get_current_user()` dependency with invalid token format
  - [ ] Test `get_current_user()` dependency with expired token
  - [ ] Mock Cognito JWKS endpoint for testing

- [ ] Task 9: Create integration test for protected endpoint (AC: #8, #9)
  - [ ] Create test that generates valid JWT token (or use test token)
  - [ ] Test protected endpoint with valid token
  - [ ] Test protected endpoint with invalid token (should return 401)
  - [ ] Test protected endpoint with expired token (should return 401)
  - [ ] Verify user info is accessible in route handler

- [ ] Task 10: Update documentation (AC: #9)
  - [ ] Document JWT validation dependency usage in README
  - [ ] Add example of how to use `get_current_user()` in route handlers
  - [ ] Document environment variables required for Cognito JWKS
  - [ ] Update architecture documentation if needed

## Dev Notes

### Architecture Patterns and Constraints

- **Backend Framework**: FastAPI with dependency injection pattern [Source: docs/architecture.md#Decision-Summary]
- **JWT Library**: python-jose for JWT validation [Source: docs/epics.md#Story-2.3]
- **Authentication Provider**: AWS Cognito [Source: docs/architecture.md#Decision-Summary]
- **Dependency Injection**: FastAPI dependencies for authentication [Source: docs/epics.md#Story-2.3]
- **Error Handling**: HTTPException with appropriate status codes (401 Unauthorized) [Source: docs/epics.md#Story-2.3]
- **Caching**: In-memory cache for JWKS keys (performance optimization) [Source: docs/epics.md#Story-2.3]

### Project Structure Notes

The JWT validation should be organized as follows:
```
spendsense-backend/
├── app/
│   ├── dependencies.py          # FastAPI dependency: get_current_user()
│   ├── utils/
│   │   └── jwt.py               # JWT validation utilities (JWKS fetching, token verification)
│   ├── config.py                # Cognito configuration (User Pool ID, region)
│   ├── api/
│   │   └── v1/
│   │       └── auth.py          # Example protected endpoint
│   └── ...
├── tests/
│   ├── test_jwt.py              # Unit tests for JWT validation
│   └── test_auth.py             # Integration tests for protected endpoints
└── ...
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **JWT Token Format**:
   - Token received in `Authorization: Bearer <token>` header
   - Token is a JWT from AWS Cognito
   - Token contains standard claims: `sub` (user ID), `exp` (expiration), `iat` (issued at), etc.
   - Custom claims may include role information

2. **JWKS (JSON Web Key Set)**:
   - Cognito exposes JWKS at: `https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json`
   - JWKS contains public keys for verifying token signatures
   - Should cache JWKS keys in memory to avoid repeated HTTP requests
   - Cache TTL should be reasonable (e.g., 1 hour) or implement cache invalidation

3. **Token Validation Flow**:
   ```
   1. Extract Authorization header
   2. Parse "Bearer <token>" format
   3. Decode token header to get key ID (kid)
   4. Fetch JWKS (or use cached)
   5. Find matching key by kid
   6. Verify token signature
   7. Check token expiration
   8. Extract claims (sub, role, etc.)
   9. Return user info or raise HTTPException
   ```

4. **FastAPI Dependency Pattern**:
   ```python
   from fastapi import Depends, HTTPException, Header
   from app.dependencies import get_current_user
   
   @app.get("/protected")
   async def protected_route(current_user: UserInfo = Depends(get_current_user)):
       # current_user.user_id and current_user.role available
       return {"message": "Access granted"}
   ```

5. **Error Handling**:
   - Missing Authorization header: 401 with message "Authorization header missing"
   - Invalid token format: 401 with message "Invalid token format"
   - Invalid signature: 401 with message "Invalid token"
   - Expired token: 401 with message "Token has expired"
   - JWKS fetch failure: 500 or 401 with appropriate error message

6. **Security Considerations**:
   - Never log the actual token value (security risk)
   - Validate token signature before trusting any claims
   - Always check expiration, even if token is valid
   - Use HTTPS for JWKS fetching (Cognito provides HTTPS)
   - Consider rate limiting for token validation attempts

7. **Performance Optimization**:
   - Cache JWKS keys in memory (avoid repeated HTTP requests)
   - Consider caching validated token info (with short TTL) if needed
   - Use async HTTP client (httpx) if fetching JWKS synchronously becomes a bottleneck

### Learnings from Previous Stories

**From Story 1.2 (Status: in-progress)**
- **Project Structure**: Backend project structure established at `spendsense-backend/` with FastAPI
- **Dependencies**: `app/dependencies.py` exists for dependency injection - use this file for `get_current_user()`
- **Configuration**: `app/config.py` exists with Settings class - add Cognito configuration here
- **Testing**: pytest with pytest-asyncio configured for async endpoint testing
- **Environment Variables**: `.env.example` pattern established - add Cognito settings

**From Story 1.5 (Status: pending)**
- **Cognito User Pool**: AWS Cognito User Pool will be created with User Pool ID
- **Cognito Region**: Cognito User Pool will be in a specific AWS region
- **Token Format**: Cognito issues JWT tokens with standard claims and optional custom claims

### References

- [Source: docs/epics.md#Story-2.3]
- [Source: docs/architecture.md#Decision-Summary]
- [Source: docs/architecture.md#Project-Structure]
- [Source: Story 1.2 implementation]
- [Source: AWS Cognito JWT Documentation]
- [Source: python-jose Documentation]
- [Source: FastAPI Dependencies Documentation]

## Dev Agent Record

### Context Reference

- `docs/stories/2-3-implement-jwt-token-validation.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

<!-- To be filled during implementation -->

### File List

<!-- To be filled during implementation -->

## Change Log

- 2025-01-XX: Story created and drafted

