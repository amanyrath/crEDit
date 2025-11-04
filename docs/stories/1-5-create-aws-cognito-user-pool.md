# Story 1.5: Create AWS Cognito User Pool

Status: drafted

## Story

As a developer,
I want to create the AWS Cognito User Pool with consumer and operator user groups,
so that authentication and authorization are ready for user management.

## Acceptance Criteria

1. AWS Cognito User Pool created
2. User groups created: "consumers" and "operators"
3. Email/password authentication enabled
4. JWT token configuration set (access token, ID token, refresh token)
5. User pool attributes configured (email, role)
6. Pre-seeded demo accounts created:
   - `hannah@demo.com` / `demo123` (Consumer)
   - `sam@demo.com` / `demo123` (Consumer)
   - `operator@demo.com` / `demo123` (Operator)
7. User pool ID and client ID stored in AWS Secrets Manager
8. Cognito configuration documented

## Tasks / Subtasks

- [ ] Task 1: Create Cognito User Pool stack in CDK (AC: #1, #3, #4, #5)
  - [ ] Create `infrastructure/cdk/stacks/cognito_stack.py`
  - [ ] Define Cognito User Pool with email/password authentication
  - [ ] Configure email as username (email sign-in)
  - [ ] Configure required attributes: email
  - [ ] Configure optional attributes: custom:role (for user role assignment, if using custom attributes)
  - [ ] Note: User groups are the primary mechanism for roles; custom:role is optional metadata
  - [ ] Configure password policy (minimum length, complexity requirements)
  - [ ] Configure email verification (skip for demo accounts initially)
  - [ ] Configure token expiration:
    - Access token: 1 hour
    - ID token: 1 hour
    - Refresh token: 30 days
  - [ ] Add stack to `infrastructure/cdk/app.py`

- [ ] Task 2: Create user groups (AC: #2)
  - [ ] Create "consumers" user group
  - [ ] Create "operators" user group
  - [ ] Configure group descriptions
  - [ ] Set up IAM roles for groups (if needed for future use)

- [ ] Task 3: Create Cognito User Pool Client (AC: #1, #4)
  - [ ] Create user pool client (app client)
  - [ ] Configure authentication flows:
    - ALLOW_USER_PASSWORD_AUTH (for direct sign-in)
    - ALLOW_REFRESH_TOKEN_AUTH (for token refresh)
  - [ ] Configure token validity:
    - Access token: 1 hour
    - ID token: 1 hour
    - Refresh token: 30 days
  - [ ] Configure OAuth flows (if needed for hosted UI)
  - [ ] Configure callback URLs (for hosted UI, if enabled)

- [ ] Task 4: Store Cognito configuration in Secrets Manager (AC: #7)
  - [ ] Create Secrets Manager secret for Cognito configuration
  - [ ] Store user pool ID
  - [ ] Store user pool ARN
  - [ ] Store client ID
  - [ ] Store client secret (if generated)
  - [ ] Store region
  - [ ] Configure IAM permissions for Lambda functions to access secret
  - [ ] Export secret ARN as stack output

- [ ] Task 5: Create user pool domain (optional, AC: #8)
  - [ ] Create Cognito user pool domain (for hosted UI)
  - [ ] Configure domain prefix (e.g., `spendsense-dev`)
  - [ ] Document hosted UI URLs (if enabled)
  - [ ] Note: This is optional for MVP, can be added later

- [ ] Task 6: Create pre-seeded demo accounts (AC: #6)
  - [ ] Create script to add demo users: `infrastructure/scripts/create_demo_users.py`
  - [ ] Create user: `hannah@demo.com` with permanent password (use `Demo123!` or admin-create-user with permanent password)
  - [ ] Add `hannah@demo.com` to "consumers" group
  - [ ] Create user: `sam@demo.com` with permanent password (use `Demo123!` or admin-create-user with permanent password)
  - [ ] Add `sam@demo.com` to "consumers" group
  - [ ] Create user: `operator@demo.com` with permanent password (use `Demo123!` or admin-create-user with permanent password)
  - [ ] Add `operator@demo.com` to "operators" group
  - [ ] Set custom:role attribute for each user (consumer or operator) - only if custom attribute is defined in Task 1
  - [ ] Mark users as email verified (skip email verification for demo)
  - [ ] Verify users can sign in with provided credentials
  - [ ] Document script usage and credentials in README

- [ ] Task 7: Document Cognito configuration (AC: #8)
  - [ ] Update `infrastructure/README.md` with Cognito stack deployment instructions
  - [ ] Document user pool ID retrieval
  - [ ] Document client ID retrieval
  - [ ] Document how to add users to groups
  - [ ] Document how to authenticate users
  - [ ] Document token validation process
  - [ ] Document custom attributes (email, role)
  - [ ] Document demo accounts credentials

- [ ] Task 8: Verify all components (AC: #1, #2, #3, #4, #5, #6, #7, #8)
  - [ ] Deploy Cognito stack: `cdk deploy SpendSense-Cognito-dev`
  - [ ] Verify user pool is created and active
  - [ ] Verify user groups are created
  - [ ] Verify user pool client is created
  - [ ] Verify Secrets Manager secret exists with correct values
  - [ ] Run demo user creation script
  - [ ] Verify demo users are created and in correct groups
  - [ ] Test authentication with demo account (optional, can be done in Story 2.2)
  - [ ] Verify all acceptance criteria are met

## Dev Notes

### Architecture Patterns and Constraints

- **Authentication Service**: AWS Cognito User Pool [Source: docs/architecture.md#Decision-Summary]
- **User Groups**: "consumers" and "operators" for role-based access [Source: docs/epics.md#Story-1.5]
- **Token Configuration**: 1 hour access/ID tokens, 30 days refresh token [Source: docs/epics.md#Story-1.5]
- **Secrets Management**: AWS Secrets Manager for Cognito configuration [Source: docs/architecture.md#Security-Architecture]
- **Infrastructure as Code**: AWS CDK Python (consistent with database stack) [Source: infrastructure/cdk/app.py]
- **User Attributes**: Email (required), custom:role (optional, for user role) [Source: docs/epics.md#Story-1.5]

### Project Structure Notes

The Cognito infrastructure should follow this structure:
```
infrastructure/
├── cdk/
│   ├── app.py                      # CDK app entry point (add Cognito stack)
│   ├── stacks/
│   │   ├── cognito_stack.py        # Cognito User Pool stack
│   │   └── database_stack.py       # Existing database stack
│   └── requirements.txt            # Python dependencies (add cognito dependencies if needed)
└── scripts/
    └── create_demo_users.py        # Script to create demo users
```

[Source: infrastructure/cdk/app.py, infrastructure/cdk/stacks/database_stack.py]

### Key Implementation Details

1. **Cognito User Pool Configuration**:
   - Sign-in method: Email (email as username)
   - Password policy: Minimum 8 characters, at least one uppercase, one lowercase, one number, one special character
   - Note: Demo accounts use temporary passwords with forced password change disabled, or use a stronger password that meets policy (e.g., `Demo123!`)
   - Email verification: Disabled for demo accounts (can be enabled later)
   - Multi-factor authentication: Disabled for MVP (can be added later)
   - Account recovery: Email-based (forgot password)

2. **User Attributes**:
   - Required: `email`
   - Optional: `custom:role` (for storing user role: "consumer" or "operator")
   - Note: Custom attributes must be defined in user pool schema before use (must be done in Task 1 before Task 6)
   - Alternative: Use user groups for role assignment (primary method), custom:role attribute can be used as additional metadata
   - Groups are the primary mechanism for role-based access control (see Story 2.4)

3. **Token Configuration**:
   - Access token: 1 hour (3600 seconds)
   - ID token: 1 hour (3600 seconds)
   - Refresh token: 30 days (2592000 seconds)
   - Token format: JWT (JSON Web Token)

4. **User Groups**:
   - "consumers": Regular users who use the application
   - "operators": Admin/operator users who can perform administrative actions
   - Groups can be used for IAM role mapping (future enhancement)
   - Groups are used for authorization in application code

5. **Secrets Manager**:
   - Secret name: `spendsense/cognito/configuration` (or similar)
   - Store: user_pool_id, user_pool_arn, client_id, client_secret (if generated), region
   - Format: JSON object with all Cognito configuration values
   - IAM permissions: Lambda execution role needs `secretsmanager:GetSecretValue` permission

6. **Demo Users**:
   - Use AWS SDK (boto3) to create users programmatically
   - Password options:
     - Option A: Use stronger password that meets policy (e.g., `Demo123!` instead of `demo123`)
     - Option B: Create users with temporary password and set `permanent=True` to avoid forced password change
     - Option C: Use admin-create-user with message_action=SUPPRESS to create users with permanent passwords
   - For demo purposes, skip email verification (mark as verified programmatically)
   - Add users to appropriate groups after creation (primary role mechanism)
   - Optionally set custom:role attribute to match group membership (if using custom attribute)
   - Ensure users can sign in immediately with provided credentials

7. **User Pool Domain** (Optional):
   - Domain prefix: `spendsense-dev` (or environment-specific)
   - Hosted UI URL: `https://spendsense-dev.auth.us-east-1.amazoncognito.com`
   - Can be used for hosted sign-in/sign-up pages (optional for MVP)

8. **Authentication Flows**:
   - USER_PASSWORD_AUTH: Direct sign-in with username/password
   - REFRESH_TOKEN_AUTH: Refresh access token using refresh token
   - Can add SRP (Secure Remote Password) flow later if needed

### Learnings from Previous Stories

**From Story 1.3 (Status: done)**
- **Infrastructure Pattern**: AWS CDK with Python - Cognito stack should follow same pattern as database stack
- **Stack Naming**: Use format `SpendSense-Cognito-{env}` to match database stack naming
- **Secrets Manager**: Store configuration in Secrets Manager (similar to database connection string)
- **Stack Outputs**: Export Cognito IDs and ARNs as stack outputs for easy reference
- **Documentation**: Document deployment and configuration in infrastructure/README.md

**From Story 1.2 (Status: in-progress)**
- **Backend Integration**: Backend will use boto3 to access Secrets Manager for Cognito configuration
- **Environment Variables**: Backend uses `.env` for local development - Cognito config can be documented for local testing
- **AWS SDK**: Backend already uses boto3 - will use for Cognito operations in future stories

**From Story 1.4 (Status: in-progress)**
- **User Management**: Database schema has `profiles` table with `user_id` (UUID from Cognito) - Cognito user IDs will be stored in database
- **Role Management**: Database has `role` field in profiles table - Cognito groups and custom:role attribute align with database role field

### References

- [Source: docs/epics.md#Story-1.5]
- [Source: docs/architecture.md#Decision-Summary]
- [Source: docs/architecture.md#Security-Architecture]
- [Source: infrastructure/cdk/app.py]
- [Source: infrastructure/cdk/stacks/database_stack.py]
- [Source: infrastructure/README.md]

## Dev Agent Record

### Context Reference

- `docs/stories/1-5-create-aws-cognito-user-pool.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

<!-- To be filled during implementation -->

### File List

<!-- To be filled during implementation -->

## Change Log

- 2025-11-03: Story created and drafted

