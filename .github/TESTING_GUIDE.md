# Testing Guide for CI/CD Workflows

This guide helps you test the CI/CD workflows after Stories 1.6 and 1.7 are complete.

## Prerequisites

1. ✅ Stories 1.6 and 1.7 are complete (Lambda stack and S3/CloudFront deployed)
2. ✅ AWS credentials configured locally (`aws configure`)
3. ✅ GitHub repository configured
4. ✅ GitHub Secrets configured (see `.github/GITHUB_SECRETS_SETUP.md`)

## Step 1: Get AWS Resource Values

Run the helper script to get values needed for GitHub Secrets:

```bash
.github/scripts/get_github_secrets_values.sh dev
```

Or manually retrieve values:

```bash
# Get S3 bucket name
aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
  --output text

# Get CloudFront Distribution ID
aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text
```

## Step 2: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

| Secret Name | Value | Source |
|------------|-------|--------|
| `AWS_ACCESS_KEY_ID` | Your AWS access key | Create IAM user (see `.github/GITHUB_SECRETS_SETUP.md`) |
| `AWS_SECRET_ACCESS_KEY` | Your AWS secret key | Create IAM user |
| `AWS_REGION` | `us-east-1` (or your region) | AWS region |
| `S3_BUCKET_NAME` | `spendsense-frontend-dev` | From Step 1 |
| `CLOUDFRONT_DISTRIBUTION_ID` | Distribution ID | From Step 1 |
| `ENVIRONMENT` | `dev` | Environment name |

## Step 3: Test CI Workflow

The CI workflow runs automatically on every push and pull request.

### Test on Pull Request

1. Create a feature branch:
   ```bash
   git checkout -b test-ci-workflow
   ```

2. Make a small change (e.g., update a comment):
   ```bash
   # Edit any file
   git add .
   git commit -m "test: trigger CI workflow"
   git push origin test-ci-workflow
   ```

3. Create a Pull Request to `main`

4. Check GitHub Actions:
   - Go to **Actions** tab
   - You should see "CI" workflow running
   - Both frontend and backend jobs should run in parallel

5. Verify results:
   - ✅ Frontend job: Lint, type check, and tests pass
   - ✅ Backend job: Lint (if Ruff installed), type check (if mypy configured), and tests pass

### Test on Push to Main

1. Merge your PR or push directly to main:
   ```bash
   git checkout main
   git merge test-ci-workflow
   git push origin main
   ```

2. Verify CI workflow runs successfully

## Step 4: Test Frontend Deployment Workflow

### Manual Trigger (Recommended for First Test)

1. Go to **Actions** tab → **Deploy Frontend** workflow
2. Click **Run workflow**
3. Select branch: `main`
4. Click **Run workflow** button

### Automatic Trigger

1. Make a change to frontend code:
   ```bash
   # Edit a file in spendsense-frontend/
   git add spendsense-frontend/
   git commit -m "test: trigger frontend deployment"
   git push origin main
   ```

2. Verify deployment:
   - Check GitHub Actions for workflow execution
   - Verify steps complete successfully:
     - ✅ Install dependencies
     - ✅ Build application
     - ✅ Deploy to S3
     - ✅ Invalidate CloudFront

3. Verify frontend is deployed:
   ```bash
   # Get CloudFront URL
   aws cloudformation describe-stacks \
     --stack-name SpendSense-S3-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionUrl`].OutputValue' \
     --output text
   
   # Open URL in browser
   ```

4. Check S3 bucket contents:
   ```bash
   aws s3 ls s3://spendsense-frontend-dev/
   ```

## Step 5: Test Backend Deployment Workflow

### Prerequisites

Ensure CDK bootstrap is complete:
```bash
cd infrastructure/cdk
cdk bootstrap aws://YOUR_ACCOUNT_ID/us-east-1
```

### Manual Trigger (Recommended for First Test)

1. Go to **Actions** tab → **Deploy Backend** workflow
2. Click **Run workflow**
3. Select branch: `main`
4. Click **Run workflow** button

### Automatic Trigger

1. Make a change to backend or infrastructure code:
   ```bash
   # Edit a file in spendsense-backend/ or infrastructure/
   git add spendsense-backend/ infrastructure/
   git commit -m "test: trigger backend deployment"
   git push origin main
   ```

2. Verify deployment:
   - Check GitHub Actions for workflow execution
   - Verify steps complete successfully:
     - ✅ Install CDK dependencies
     - ✅ Install CDK CLI
     - ✅ Deploy Lambda stack
     - ✅ Verify deployment

3. Verify Lambda functions are deployed:
   ```bash
   # List Lambda functions
   aws lambda list-functions \
     --query 'Functions[?starts_with(FunctionName, `SpendSense`)].FunctionName' \
     --output table
   
   # Check API Gateway endpoint
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Lambda-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
     --output text
   ```

## Troubleshooting

### CI Workflow Fails

**Issue**: Tests fail
- **Solution**: Check test logs, fix failing tests locally first

**Issue**: Linting fails
- **Solution**: Run `npm run lint` locally and fix issues

**Issue**: Type checking fails
- **Solution**: Run `tsc --noEmit` locally and fix type errors

### Frontend Deployment Fails

**Issue**: `S3_BUCKET_NAME secret is not set`
- **Solution**: Add `S3_BUCKET_NAME` secret in GitHub Settings

**Issue**: Access Denied when syncing to S3
- **Solution**: Verify IAM user has `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket` permissions

**Issue**: CloudFront invalidation fails
- **Solution**: Verify `CLOUDFRONT_DISTRIBUTION_ID` secret is set correctly
- **Solution**: Verify IAM user has `cloudfront:CreateInvalidation` permission

### Backend Deployment Fails

**Issue**: CDK bootstrap not complete
- **Solution**: Run `cdk bootstrap aws://ACCOUNT_ID/REGION` manually

**Issue**: CloudFormation stack errors
- **Solution**: Check CloudFormation console for detailed error messages
- **Solution**: Verify all dependencies (Database, Cognito) are deployed

**Issue**: IAM permissions insufficient
- **Solution**: Verify IAM user has CloudFormation, Lambda, and API Gateway permissions

## Verification Checklist

After testing, verify:

- [ ] CI workflow runs on pull requests
- [ ] CI workflow runs on push to main
- [ ] Frontend tests pass
- [ ] Backend tests pass
- [ ] Linting passes (frontend and backend)
- [ ] Type checking passes (frontend and backend)
- [ ] Frontend deployment workflow completes successfully
- [ ] Frontend is accessible via CloudFront URL
- [ ] Backend deployment workflow completes successfully
- [ ] Lambda functions are deployed and accessible
- [ ] API Gateway endpoint is accessible

## Next Steps

Once all workflows are tested and working:

1. ✅ Mark Task 5 as complete in story file
2. ✅ Update story status to "review"
3. ✅ Document any issues encountered and resolutions
4. ✅ Set up branch protection (optional but recommended)
5. ✅ Configure deployment notifications (optional)

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- `.github/GITHUB_SECRETS_SETUP.md` - Secrets configuration guide
- `.github/DEPLOYMENT.md` - Deployment and rollback procedures



