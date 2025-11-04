# Story 1.9: Set Up CI/CD Pipeline with GitHub Actions

Status: in-progress

## Story

As a developer,
I want to create GitHub Actions workflows for automated testing and deployment,
so that code changes are automatically tested and deployed to AWS.

## Acceptance Criteria

1. GitHub Actions workflow created for CI:
   - Runs on pull requests and pushes to main
   - Runs frontend tests (Vitest)
   - Runs backend tests (pytest)
   - Runs linting (ESLint, Ruff)
   - Runs type checking (TypeScript, mypy)
2. GitHub Actions workflow created for frontend deployment:
   - Builds React app with Vite
   - Uploads to S3 bucket
   - Invalidates CloudFront distribution
3. GitHub Actions workflow created for backend deployment:
   - Builds Lambda deployment packages
   - Deploys Lambda functions via SAM or CDK
   - Updates API Gateway if needed
4. AWS credentials configured in GitHub Secrets
5. Workflows run successfully on test commits

**Prerequisites:** GitHub repository, AWS credentials

**Technical Notes:**
- Use AWS SAM CLI or CDK for Lambda deployment
- Configure GitHub Secrets for AWS access keys
- Set up branch protection if needed
- Document deployment process and rollback procedure

## Tasks / Subtasks

- [x] Task 1: Create CI workflow for continuous integration (AC: #1)
  - [x] Create `.github/workflows/ci.yml`
  - [x] Configure workflow to run on pull requests and pushes to main
  - [x] Set up separate jobs for frontend and backend testing (parallel execution)
  - [x] Configure Node.js environment for frontend (use Node.js 20.x LTS)
  - [x] Configure Python environment for backend (use Python 3.11+)
  - [x] Add frontend test step: Run `npm test` (Vitest)
  - [x] Add backend test step: Run `pytest` in backend directory
  - [x] Add frontend linting step: Run `npm run lint` (ESLint)
  - [x] Add backend linting step: Run `ruff check` (if available) or configure Ruff
  - [x] Add frontend type checking step: Run `tsc --noEmit` (TypeScript)
  - [x] Add backend type checking step: Run `mypy` (if configured)
  - [x] Configure workflow to fail if any step fails
  - [ ] Add workflow status badges to README (optional)

- [x] Task 2: Create frontend deployment workflow (AC: #2)
  - [x] Create `.github/workflows/deploy-frontend.yml`
  - [x] Configure workflow to run on push to main branch (or manual trigger)
  - [x] Set up Node.js environment
  - [x] Configure AWS credentials using GitHub Secrets
  - [x] Add step to install frontend dependencies: `npm ci`
  - [x] Add step to build frontend: `npm run build`
  - [x] Add step to configure AWS CLI
  - [x] Add step to sync build output to S3 bucket (use `aws s3 sync`)
  - [x] Add step to invalidate CloudFront distribution (use `aws cloudfront create-invalidation`)
  - [x] Configure S3 bucket name from GitHub Secrets or environment variable
  - [x] Configure CloudFront distribution ID from GitHub Secrets or environment variable
  - [x] Add error handling and rollback documentation
  - [x] Document S3 bucket and CloudFront distribution setup requirements

- [x] Task 3: Create backend deployment workflow (AC: #3)
  - [x] Create `.github/workflows/deploy-backend.yml`
  - [x] Configure workflow to run on push to main branch (or manual trigger)
  - [x] Set up Python environment
  - [x] Configure AWS credentials using GitHub Secrets
  - [x] Add step to install CDK dependencies: `pip install -r requirements.txt` in infrastructure/cdk
  - [x] Add step to install CDK CLI: `npm install -g aws-cdk` (or use CDK Docker image)
  - [x] Add step to configure AWS CLI
  - [x] Add step to deploy Lambda stack: `cdk deploy SpendSense-Lambda-dev` (or use CDK synth + deploy)
  - [x] Add step to verify deployment success
  - [x] Configure environment variables (dev/staging/prod) from GitHub Secrets
  - [x] Add error handling and rollback documentation
  - [x] Document CDK deployment prerequisites (bootstrap, etc.)

- [x] Task 4: Configure GitHub Secrets for AWS credentials (AC: #4)
  - [x] Document required GitHub Secrets:
    - `AWS_ACCESS_KEY_ID`: AWS access key for GitHub Actions
    - `AWS_SECRET_ACCESS_KEY`: AWS secret access key
    - `AWS_REGION`: AWS region (e.g., `us-east-1`)
    - `S3_BUCKET_NAME`: S3 bucket name for frontend deployment (optional, can be in workflow)
    - `CLOUDFRONT_DISTRIBUTION_ID`: CloudFront distribution ID (optional, can be in workflow)
  - [x] Create documentation for setting up GitHub Secrets
  - [x] Document IAM policy requirements for GitHub Actions user/role
  - [x] Document how to create IAM user with minimal required permissions
  - [x] Add security best practices (use IAM roles with OIDC if possible)

- [ ] Task 5: Test workflows with test commits (AC: #5)
  - [ ] Create test commit to trigger CI workflow
  - [ ] Verify CI workflow runs successfully on pull request
  - [ ] Verify CI workflow runs successfully on push to main
  - [ ] Verify all test steps pass (frontend tests, backend tests)
  - [ ] Verify all linting steps pass
  - [ ] Verify all type checking steps pass
  - [ ] Create test commit to trigger frontend deployment (if applicable)
  - [ ] Verify frontend deployment workflow runs successfully
  - [ ] Verify frontend assets are uploaded to S3
  - [ ] Verify CloudFront invalidation completes
  - [ ] Create test commit to trigger backend deployment (if applicable)
  - [ ] Verify backend deployment workflow runs successfully
  - [ ] Verify Lambda functions are deployed
  - [ ] Document any issues encountered and resolutions

- [x] Task 6: Document deployment process and rollback procedure (AC: #3, #4)
  - [x] Create deployment documentation in `.github/` or `docs/` directory
  - [x] Document manual deployment process (if needed)
  - [x] Document rollback procedure for frontend (S3 versioning, CloudFront invalidation)
  - [x] Document rollback procedure for backend (CDK rollback, previous Lambda version)
  - [x] Document branch protection setup (if applicable)
  - [x] Document how to trigger workflows manually (if needed)
  - [x] Document environment-specific deployment (dev/staging/prod)

## Dev Notes

### Architecture Patterns and Constraints

- **CI/CD Platform**: GitHub Actions [Source: docs/architecture.md#Decision-Summary]
- **Frontend Testing**: Vitest [Source: docs/architecture.md#Decision-Summary]
- **Backend Testing**: pytest [Source: docs/architecture.md#Decision-Summary]
- **Frontend Linting**: ESLint [Source: docs/architecture.md#Decision-Summary]
- **Backend Linting**: Ruff [Source: docs/architecture.md#Decision-Summary]
- **Frontend Type Checking**: TypeScript [Source: docs/architecture.md#Decision-Summary]
- **Backend Type Checking**: mypy [Source: docs/architecture.md#Decision-Summary]
- **Frontend Deployment**: S3 + CloudFront [Source: docs/architecture.md#Decision-Summary]
- **Backend Deployment**: AWS CDK for Lambda functions [Source: infrastructure/cdk/app.py]
- **Infrastructure as Code**: AWS CDK (Python) [Source: infrastructure/README.md]

### Project Structure Notes

The CI/CD workflows should follow this structure:
```
.github/
├── workflows/
│   ├── ci.yml                    # Continuous integration workflow
│   ├── deploy-frontend.yml       # Frontend deployment workflow
│   └── deploy-backend.yml        # Backend deployment workflow
└── README.md                     # CI/CD documentation (optional)
```

[Source: Standard GitHub Actions structure]

### Key Implementation Details

1. **CI Workflow Configuration**:
   - Trigger: `on: [push, pull_request]` with branches: `main`
   - Use matrix strategy to run frontend and backend tests in parallel
   - Cache dependencies (npm packages, pip packages) for faster builds
   - Use `npm ci` for frontend (faster, more reliable than `npm install`)
   - Use separate jobs for frontend and backend to allow parallel execution

2. **Frontend Deployment**:
   - S3 bucket should be configured with static website hosting (or use CloudFront)
   - CloudFront distribution should be created (Story 1.7) before deployment
   - Use `aws s3 sync` with `--delete` flag to remove old files
   - Use `aws cloudfront create-invalidation` to invalidate cache
   - Consider using environment-specific buckets/distributions (dev/staging/prod)

3. **Backend Deployment**:
   - Use AWS CDK for deployment (consistent with infrastructure setup)
   - CDK requires `cdk bootstrap` to be run once per account/region
   - Deploy Lambda stack: `cdk deploy SpendSense-Lambda-dev`
   - CDK automatically handles API Gateway updates
   - Consider using CDK context for environment-specific configurations

4. **AWS Credentials**:
   - Use GitHub Secrets for sensitive credentials
   - Create IAM user with minimal required permissions:
     - S3: `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket`
     - CloudFront: `cloudfront:CreateInvalidation`
     - CloudFormation/CDK: `cloudformation:*`, `lambda:*`, `apigateway:*`, `iam:*`, `logs:*`
     - Secrets Manager: `secretsmanager:GetSecretValue` (if needed)
   - Consider using IAM roles with OIDC (more secure, no long-lived credentials)

5. **Workflow Optimization**:
   - Use caching for dependencies (npm, pip)
   - Use `actions/cache` for node_modules and pip packages
   - Use `actions/setup-node` with cache option
   - Use `actions/setup-python` with cache option
   - Run tests and linting in parallel when possible

6. **Error Handling**:
   - Configure workflow to fail fast on errors
   - Add notifications for failed deployments (optional)
   - Document manual rollback procedures
   - Consider using deployment status checks

7. **Branch Protection** (Optional):
   - Require status checks to pass before merging
   - Require pull request reviews
   - Prevent force pushes to main branch
   - Document setup in deployment documentation

### Learnings from Previous Stories

**From Story 1.1 (Status: done)**
- **Frontend Setup**: Frontend project uses Vitest for testing (`npm test`), ESLint for linting (`npm run lint`), TypeScript for type checking
- **Build Command**: Frontend builds with `npm run build` (Vite)
- **Project Location**: Frontend project at `spendsense-frontend/`

**From Story 1.2 (Status: in-progress)**
- **Backend Setup**: Backend project uses pytest for testing, requires Python 3.11+
- **Project Location**: Backend project at `spendsense-backend/`
- **Dependencies**: Backend uses `requirements.txt` for dependencies

**From Story 1.3 (Status: done)**
- **Infrastructure**: AWS CDK is used for infrastructure as code
- **CDK Location**: Infrastructure code at `infrastructure/cdk/`
- **Deployment**: CDK requires `cdk bootstrap` and uses `cdk deploy` command

**From Story 1.6 (Status: in-progress)**
- **Lambda Stack**: Lambda functions are deployed via CDK stack `SpendSense-Lambda-dev`
- **API Gateway**: API Gateway is configured in Lambda stack

**From Story 1.7 (Status: not started, but referenced)**
- **S3 and CloudFront**: Frontend deployment requires S3 bucket and CloudFront distribution
- **Note**: Story 1.7 may need to be completed before frontend deployment workflow can be fully tested

### References

- [Source: docs/epics.md#Story-1.9]
- [Source: docs/architecture.md#Decision-Summary]
- [Source: infrastructure/README.md]
- [Source: infrastructure/cdk/app.py]
- [Source: spendsense-frontend/package.json]
- [Source: spendsense-backend/requirements.txt]

## Dev Agent Record

### Context Reference

- `docs/stories/1-9-set-up-cicd-pipeline-with-github-actions.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

- **CI Workflow**: Created `.github/workflows/ci.yml` with separate jobs for frontend and backend:
  - Frontend job: Runs ESLint, TypeScript type checking, and Vitest tests
  - Backend job: Runs Ruff linting (if available), mypy type checking (if configured), and pytest tests
  - Both jobs run in parallel on push and pull requests to main branch
  - Uses caching for npm and pip dependencies to speed up workflow execution

- **Frontend Deployment Workflow**: Created `.github/workflows/deploy-frontend.yml`:
  - Triggers on push to main (with frontend changes) or manual trigger
  - Builds React app with Vite
  - Syncs build output to S3 bucket (configured via GitHub Secrets)
  - Invalidates CloudFront distribution cache
  - Includes error handling for missing secrets

- **Backend Deployment Workflow**: Created `.github/workflows/deploy-backend.yml`:
  - Triggers on push to main (with backend/infrastructure changes) or manual trigger
  - Installs CDK dependencies and CLI
  - Deploys Lambda stack via CDK: `cdk deploy SpendSense-Lambda-{env}`
  - Verifies deployment success
  - Supports environment-specific deployment (dev/staging/prod)

- **Documentation**: Created comprehensive documentation:
  - `.github/GITHUB_SECRETS_SETUP.md`: Complete guide for setting up GitHub Secrets, IAM user creation, and security best practices
  - `.github/DEPLOYMENT.md`: Deployment procedures, rollback guides, troubleshooting, and operational best practices

- **Note**: Task 5 (Test workflows) requires actual GitHub repository and AWS infrastructure (Stories 1.6 and 1.7) to fully test. CI workflow can be tested immediately, but deployment workflows need infrastructure in place.

### File List

**Created Files:**
- `.github/workflows/ci.yml` - CI workflow for frontend and backend testing, linting, and type checking
- `.github/workflows/deploy-frontend.yml` - Frontend deployment workflow (S3 + CloudFront)
- `.github/workflows/deploy-backend.yml` - Backend deployment workflow (CDK Lambda stack)
- `.github/GITHUB_SECRETS_SETUP.md` - GitHub Secrets configuration guide
- `.github/DEPLOYMENT.md` - Deployment and rollback procedures documentation

## Change Log

- 2025-11-03: Story created and drafted
- 2025-11-03: Story context generated and marked ready-for-dev
- 2025-11-03: Implementation completed
  - Created CI workflow (`.github/workflows/ci.yml`) with frontend and backend jobs
  - Created frontend deployment workflow (`.github/workflows/deploy-frontend.yml`)
  - Created backend deployment workflow (`.github/workflows/deploy-backend.yml`)
  - Created GitHub Secrets setup documentation (`.github/GITHUB_SECRETS_SETUP.md`)
  - Created deployment documentation (`.github/DEPLOYMENT.md`)
  - Tasks 1-4 and 6 completed; Task 5 (testing) pending infrastructure setup (Stories 1.6, 1.7)

