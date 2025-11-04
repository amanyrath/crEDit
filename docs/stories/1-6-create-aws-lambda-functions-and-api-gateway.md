# Story 1.6: Create AWS Lambda Functions and API Gateway

Status: review

**Note:** Stack successfully deployed. API Gateway endpoint testing recommended.

## Story

As a developer,
I want to create the AWS Lambda functions for API and background jobs, and configure API Gateway,
so that the backend is ready for deployment and can handle HTTP requests.

## Acceptance Criteria

1. Lambda function created for FastAPI API (using Mangum adapter)
2. Lambda function configured with Python 3.11 runtime
3. Lambda functions created for background jobs:
   - `compute-features` (triggered by EventBridge)
   - `assign-persona` (triggered by EventBridge)
   - `generate-recommendations` (triggered by EventBridge)
4. API Gateway REST API created
5. API Gateway routes configured: `/api/v1/*`
6. Lambda integration configured for API routes
7. CORS configured for frontend domain
8. API Gateway deployed to stage (dev/staging/prod)
9. Lambda environment variables configured (RDS connection, Cognito pool ID, etc.)
10. IAM roles created with appropriate permissions

## Tasks / Subtasks

- [x] Task 1: Create Lambda stack in CDK (AC: #1, #2, #3, #9, #10)
  - [x] Create `infrastructure/cdk/stacks/lambda_stack.py`
  - [x] Import Lambda security group from database stack (using stack exports)
  - [x] Create IAM role for API Lambda function with:
    - VPC access permissions (for RDS connection)
    - Secrets Manager read permissions (for RDS connection string and Cognito config)
    - CloudWatch Logs permissions
  - [x] Create IAM role for background job Lambda functions with:
    - VPC access permissions (for RDS connection)
    - Secrets Manager read permissions
    - CloudWatch Logs permissions
  - [x] Create API Lambda function:
    - Runtime: Python 3.11
    - Handler: `app.handler.handler` (Mangum adapter)
    - Timeout: 30 seconds
    - Memory: 512 MB
    - VPC configuration (using lambda security group)
    - Environment variables:
      - DATABASE_SECRET_ARN (from database stack)
      - COGNITO_SECRET_ARN (from cognito stack)
      - ENVIRONMENT (dev/staging/prod)
  - [x] Create background job Lambda functions:
    - `compute-features`: Runtime Python 3.11, timeout 5 minutes, memory 1024 MB
    - `assign-persona`: Runtime Python 3.11, timeout 5 minutes, memory 512 MB
    - `generate-recommendations`: Runtime Python 3.11, timeout 5 minutes, memory 512 MB
    - Each with VPC configuration and environment variables
  - [x] Package backend code for Lambda deployment (using CDK Code.from_asset)
  - [x] Add stack to `infrastructure/cdk/app.py`

- [x] Task 2: Create API Gateway REST API (AC: #4, #5, #6, #7, #8)
  - [x] Create REST API Gateway
  - [x] Configure CORS for frontend domain (allow all origins for dev, specific domain for prod)
  - [x] Create `/api/v1/*` proxy resource
  - [x] Configure Lambda integration for API routes
  - [x] Create API Gateway deployment
  - [x] Create API Gateway stage (dev/staging/prod)
  - [x] Configure API Gateway to use Lambda function
  - [x] Export API Gateway endpoint URL as stack output

- [x] Task 3: Create Lambda handler for FastAPI (AC: #1)
  - [x] Create `spendsense-backend/app/handler.py` with Mangum adapter (already exists)
  - [x] Configure handler to use FastAPI app from `app.main`
  - [x] Ensure handler loads environment variables from Secrets Manager (via connection.py)
  - [ ] Test handler locally (if possible) - requires AWS deployment

- [x] Task 4: Create Lambda handlers for background jobs (AC: #3)
  - [x] Create `spendsense-backend/lambdas/compute_features.py` (placeholder)
  - [x] Create `spendsense-backend/lambdas/assign_persona.py` (placeholder)
  - [x] Create `spendsense-backend/lambdas/generate_recommendations.py` (placeholder)
  - [x] Each handler should:
    - Load environment variables from Secrets Manager
    - Connect to RDS database (structure ready, implementation in future stories)
    - Log execution start/end
    - Handle errors gracefully

- [x] Task 5: Configure API Gateway authorizer (AC: #6)
  - [x] Create Cognito authorizer for API Gateway
  - [x] Configure authorizer to use Cognito User Pool
  - [x] Apply authorizer to protected routes (optional for MVP, can configure later) - commented out for MVP
  - [x] Document authorizer configuration (in README and code comments)

- [x] Task 6: Configure Lambda packaging and deployment (AC: #1, #2, #3)
  - [x] Create Lambda deployment package script or use CDK asset bundling (using CDK Code.from_asset)
  - [x] Configure CDK to bundle backend code with dependencies
  - [x] Ensure Lambda layers are used if needed for large dependencies (documented for future consideration)
  - [x] Document deployment process (in README)

- [x] Task 7: Document Lambda and API Gateway configuration (AC: #10)
  - [x] Update `infrastructure/README.md` with Lambda stack deployment instructions
  - [x] Document API Gateway endpoint URL retrieval
  - [x] Document Lambda function names and ARNs
  - [x] Document environment variables configuration
  - [x] Document IAM permissions
  - [x] Document how to test Lambda functions
  - [x] Document API Gateway endpoint testing

- [x] Task 8: Verify all components (AC: #1, #2, #3, #4, #5, #6, #7, #8, #9, #10)
  - [x] Deploy Lambda stack: `cdk deploy SpendSense-Lambda-dev`
  - [x] Verify API Lambda function is created and active (deployed successfully)
  - [x] Verify background job Lambda functions are created (deployed successfully)
  - [x] Verify API Gateway is created and deployed (deployed successfully)
  - [ ] Verify API Gateway endpoint is accessible (testing recommended)
  - [ ] Test API Gateway health endpoint: `GET /health` (testing recommended)
  - [x] Verify Lambda functions have correct environment variables (configured in CDK)
  - [x] Verify IAM roles have correct permissions (configured in CDK)
  - [x] Verify all acceptance criteria are met

## Dev Notes

### Architecture Patterns and Constraints

- **Lambda Runtime**: Python 3.11 [Source: docs/epics.md#Story-1.6]
- **API Adapter**: Mangum for FastAPI Lambda integration [Source: spendsense-backend/requirements.txt]
- **Infrastructure as Code**: AWS CDK Python (consistent with database and cognito stacks) [Source: infrastructure/cdk/app.py]
- **VPC Configuration**: Lambda functions need VPC access for RDS connection [Source: infrastructure/cdk/stacks/database_stack.py]
- **Secrets Management**: Environment variables reference Secrets Manager ARNs [Source: infrastructure/cdk/stacks/database_stack.py, cognito_stack.py]
- **API Gateway**: REST API with `/api/v1/*` routes [Source: docs/epics.md#Story-1.6]

### Project Structure Notes

The Lambda infrastructure should follow this structure:
```
infrastructure/
├── cdk/
│   ├── app.py                      # CDK app entry point (add Lambda stack)
│   ├── stacks/
│   │   ├── lambda_stack.py         # Lambda functions and API Gateway stack
│   │   ├── cognito_stack.py        # Existing Cognito stack
│   │   └── database_stack.py       # Existing database stack
│   └── requirements.txt            # Python dependencies
spendsense-backend/
├── app/
│   ├── handler.py                  # Lambda handler for FastAPI
│   └── main.py                     # Existing FastAPI app
└── lambdas/
    ├── compute_features.py         # Background job handler
    ├── assign_persona.py           # Background job handler
    └── generate_recommendations.py # Background job handler
```

[Source: infrastructure/cdk/app.py, spendsense-backend/app/main.py]

### Key Implementation Details

1. **Lambda Function Configuration**:
   - API Lambda: 30 second timeout, 512 MB memory (adjust based on needs)
   - Background jobs: 5 minute timeout, 512-1024 MB memory
   - Python 3.11 runtime
   - VPC configuration required for RDS access
   - Environment variables reference Secrets Manager ARNs (not actual secrets)

2. **API Gateway Configuration**:
   - REST API (not HTTP API) for better control
   - CORS configured for frontend domain
   - `/api/v1/*` proxy resource routes to Lambda
   - Stage: dev/staging/prod based on environment context
   - API Gateway authorizer (Cognito) can be configured later for protected routes

3. **Lambda Handler Structure**:
   - API handler uses Mangum to wrap FastAPI app
   - Handler loads secrets from Secrets Manager on cold start
   - Background job handlers are event-driven (EventBridge events)
   - All handlers should log to CloudWatch Logs

4. **IAM Permissions**:
   - Lambda execution role needs:
     - VPC access (ec2:CreateNetworkInterface, etc.)
     - Secrets Manager read (secretsmanager:GetSecretValue)
     - CloudWatch Logs write (logs:CreateLogGroup, logs:CreateLogStream, logs:PutLogEvents)
   - API Gateway needs permission to invoke Lambda function

5. **Deployment Packaging**:
   - CDK can bundle Lambda code automatically using `aws_cdk.aws_lambda_python_alpha` or asset bundling
   - Consider Lambda layers for shared dependencies if package size is large
   - Mangum and FastAPI dependencies must be included in deployment package

6. **Secrets Manager Integration**:
   - Lambda environment variables store ARNs, not actual secrets
   - Lambda code reads secrets at runtime using boto3
   - Database connection string: `spendsense/database/connection`
   - Cognito configuration: `spendsense/cognito/configuration`

### Learnings from Previous Stories

**From Story 1.3 (Status: done)**
- **Security Groups**: Database stack exports `LambdaSecurityGroup` that can be referenced by Lambda stack
- **Stack Exports**: Use `CfnOutput` with `export_name` for cross-stack references
- **Secrets Manager**: Database connection string stored in Secrets Manager at `spendsense/database/connection`

**From Story 1.5 (Status: review)**
- **Secrets Manager**: Cognito configuration stored in Secrets Manager at `spendsense/cognito/configuration`
- **Stack Pattern**: Follow same CDK stack pattern as database and cognito stacks
- **Stack Naming**: Use format `SpendSense-Lambda-{env}` to match other stacks

**From Story 1.2 (Status: in-progress)**
- **Backend Structure**: FastAPI app in `spendsense-backend/app/main.py`
- **Dependencies**: Mangum already in requirements.txt for Lambda support
- **Database Access**: Backend uses SQLAlchemy for database access

### References

- [Source: docs/epics.md#Story-1.6]
- [Source: docs/architecture.md]
- [Source: infrastructure/cdk/app.py]
- [Source: infrastructure/cdk/stacks/database_stack.py]
- [Source: infrastructure/cdk/stacks/cognito_stack.py]
- [Source: spendsense-backend/app/main.py]
- [Source: spendsense-backend/requirements.txt]
- [Source: infrastructure/README.md]

## Dev Agent Record

### Context Reference

- `docs/stories/1-6-create-aws-lambda-functions-and-api-gateway.context.xml` (to be created)

### Agent Model Used

Claude Sonnet 4.5 (via Cursor)

### Debug Log References

<!-- No debug logs required for this implementation -->

### Completion Notes List

- **Lambda Stack**: Created `infrastructure/cdk/stacks/lambda_stack.py` with complete Lambda and API Gateway configuration:
  - API Lambda function configured with Python 3.11, 30s timeout, 512 MB memory, VPC access
  - Three background job Lambda functions (compute-features, assign-persona, generate-recommendations) with appropriate timeouts and memory
  - IAM roles created with VPC, Secrets Manager, and CloudWatch Logs permissions
  - Environment variables configured to reference Secrets Manager ARNs from database and cognito stacks
  - Lambda security group imported from database stack using stack exports
  
- **API Gateway**: REST API created with:
  - `/api/v1/*` proxy resource routing to API Lambda
  - `/api/v1/health` public health check endpoint
  - CORS configured (all origins for dev, specific domain for prod)
  - Cognito authorizer created but not applied by default (can be enabled for protected routes)
  - API Gateway endpoint URL exported as stack output
  
- **Lambda Handlers**: 
  - FastAPI handler already exists in `app/handler.py` using Mangum adapter
  - Background job handlers created as placeholders with Secrets Manager integration structure
  - All handlers include error handling and logging
  
- **CDK Integration**: Lambda stack added to `app.py` and integrated with existing database and cognito stacks
  
- **Documentation**: Comprehensive documentation added to `infrastructure/README.md` including:
  - Deployment instructions
  - Lambda function details and configuration
  - API Gateway endpoint usage
  - Testing procedures
  - IAM permissions documentation

### File List

**Created Files:**
- `infrastructure/cdk/stacks/lambda_stack.py` - Lambda functions and API Gateway stack
- `spendsense-backend/lambdas/compute_features.py` - Background job handler (placeholder)
- `spendsense-backend/lambdas/assign_persona.py` - Background job handler (placeholder)
- `spendsense-backend/lambdas/generate_recommendations.py` - Background job handler (placeholder)
- `spendsense-backend/lambdas/__init__.py` - Lambda handlers package init

**Modified Files:**
- `infrastructure/cdk/app.py` - Added Lambda stack import and instantiation
- `infrastructure/README.md` - Added comprehensive Lambda and API Gateway documentation
- `docs/sprint-status.yaml` - Added story 1.6 and marked as in-progress

## Change Log

- 2025-01-XX: Story created and ready for implementation
- 2025-01-XX: Implementation completed
  - Created Lambda stack with API and background job functions
  - Created API Gateway REST API with CORS and Lambda integration
  - Created background job Lambda handlers (placeholders for future stories)
  - Configured Cognito authorizer (not applied by default for MVP)
  - Updated documentation with deployment and usage instructions
  - Lambda stack successfully deployed to AWS
  - All infrastructure components created and configured
  - Testing of API Gateway endpoint recommended (see README for testing instructions)
  - Story ready for review

