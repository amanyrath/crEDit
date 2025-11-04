# Deployment Documentation

This document describes the deployment process, rollback procedures, and operational guidelines for the SpendSense CI/CD pipeline.

## Overview

The project uses GitHub Actions for continuous integration and deployment:

- **CI Workflow**: Runs on every push and pull request to `main`
- **Frontend Deployment**: Automatically deploys to S3 + CloudFront on push to `main`
- **Backend Deployment**: Automatically deploys Lambda functions via CDK on push to `main`

## Workflows

### CI Workflow (`.github/workflows/ci.yml`)

**Trigger**: Push or pull request to `main` branch

**Actions**:
1. Frontend CI:
   - Lint code with ESLint
   - Type check with TypeScript
   - Run tests with Vitest

2. Backend CI:
   - Lint code with Ruff (if available)
   - Type check with mypy (if configured)
   - Run tests with pytest

**Status**: Both jobs must pass for CI to succeed

### Frontend Deployment (`.github/workflows/deploy-frontend.yml`)

**Trigger**: 
- Push to `main` branch with changes in `spendsense-frontend/`
- Manual trigger via GitHub Actions UI

**Prerequisites**:
- Story 1.7 must be completed (S3 bucket and CloudFront distribution)
- GitHub Secrets configured (see `GITHUB_SECRETS_SETUP.md`)

**Process**:
1. Install dependencies (`npm ci`)
2. Build application (`npm run build`)
3. Sync build output to S3 bucket
4. Invalidate CloudFront cache

**Manual Deployment**:
```bash
# From GitHub Actions UI:
# 1. Go to Actions tab
# 2. Select "Deploy Frontend" workflow
# 3. Click "Run workflow"
# 4. Select branch and click "Run workflow"
```

### Backend Deployment (`.github/workflows/deploy-backend.yml`)

**Trigger**:
- Push to `main` branch with changes in `spendsense-backend/` or `infrastructure/`
- Manual trigger via GitHub Actions UI

**Prerequisites**:
- Story 1.6 must be completed (Lambda stack)
- CDK bootstrap completed: `cdk bootstrap aws://ACCOUNT_ID/REGION`
- GitHub Secrets configured

**Process**:
1. Install CDK dependencies
2. Install CDK CLI
3. Deploy Lambda stack: `cdk deploy SpendSense-Lambda-{env}`
4. Verify deployment status

**Manual Deployment**:
```bash
# From GitHub Actions UI:
# 1. Go to Actions tab
# 2. Select "Deploy Backend" workflow
# 3. Click "Run workflow"
# 4. Select branch and click "Run workflow"
```

## Rollback Procedures

### Frontend Rollback

#### Option 1: Redeploy Previous Version (Recommended)

1. Checkout previous commit:
   ```bash
   git checkout <previous-commit-hash>
   ```

2. Trigger manual deployment:
   - Go to GitHub Actions → Deploy Frontend → Run workflow

#### Option 2: S3 Versioning (If Enabled)

1. List S3 object versions:
   ```bash
   aws s3api list-object-versions \
     --bucket spendsense-frontend-dev \
     --prefix index.html
   ```

2. Restore previous version:
   ```bash
   aws s3api restore-object \
     --bucket spendsense-frontend-dev \
     --key index.html \
     --version-id <version-id>
   ```

3. Invalidate CloudFront:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <distribution-id> \
     --paths "/*"
   ```

#### Option 3: CloudFront Invalidation with Previous S3 Content

1. Upload previous build to S3:
   ```bash
   aws s3 sync <previous-build-directory> s3://spendsense-frontend-dev/ --delete
   ```

2. Invalidate CloudFront:
   ```bash
   aws cloudfront create-invalidation \
     --distribution-id <distribution-id> \
     --paths "/*"
   ```

### Backend Rollback

#### Option 1: CDK Rollback (Recommended)

1. Identify previous CloudFormation stack state:
   ```bash
   aws cloudformation list-stack-events \
     --stack-name SpendSense-Lambda-dev \
     --max-items 50
   ```

2. Revert CDK code to previous commit:
   ```bash
   git checkout <previous-commit-hash>
   ```

3. Deploy previous version:
   ```bash
   cd infrastructure/cdk
   cdk deploy SpendSense-Lambda-dev
   ```

#### Option 2: Lambda Function Version Rollback

1. List Lambda function versions:
   ```bash
   aws lambda list-versions-by-function \
     --function-name <function-name>
   ```

2. Update alias to previous version:
   ```bash
   aws lambda update-alias \
     --function-name <function-name> \
     --name <alias-name> \
     --function-version <previous-version>
   ```

#### Option 3: CloudFormation Stack Rollback

1. Check stack status:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Lambda-dev
   ```

2. If stack is in `UPDATE_ROLLBACK_*` state, wait for automatic rollback

3. If needed, manually rollback:
   ```bash
   aws cloudformation cancel-update-stack \
     --stack-name SpendSense-Lambda-dev
   ```

## Environment-Specific Deployment

### Development (`dev`)

- **Trigger**: Automatic on push to `main`
- **Environment Secret**: `ENVIRONMENT=dev`
- **Stack Name**: `SpendSense-Lambda-dev`
- **S3 Bucket**: `spendsense-frontend-dev`

### Staging (Future)

- **Trigger**: Manual or tag-based
- **Environment Secret**: `ENVIRONMENT=staging`
- **Stack Name**: `SpendSense-Lambda-staging`
- **S3 Bucket**: `spendsense-frontend-staging`

### Production (Future)

- **Trigger**: Manual or release tag
- **Environment Secret**: `ENVIRONMENT=prod`
- **Stack Name**: `SpendSense-Lambda-prod`
- **S3 Bucket**: `spendsense-frontend-prod`

## Branch Protection

### Recommended Settings

1. **Require status checks**:
   - Require `Frontend CI` to pass
   - Require `Backend CI` to pass

2. **Require pull request reviews**:
   - Require at least 1 approval
   - Dismiss stale reviews when new commits are pushed

3. **Require branches to be up to date**:
   - Require branches to be up to date before merging

4. **Restrict force pushes**:
   - Do not allow force pushes to `main`

### Setting Up Branch Protection

1. Go to repository **Settings** → **Branches**
2. Click **Add rule** or edit existing rule for `main`
3. Configure protection rules as above
4. Click **Save changes**

## Monitoring Deployments

### GitHub Actions

- View workflow runs: **Actions** tab in GitHub repository
- Check workflow logs for errors
- Monitor deployment status

### AWS CloudWatch

- Lambda function logs: CloudWatch Logs
- API Gateway logs: API Gateway console → Logs
- CloudFront logs: CloudWatch Logs (if enabled)

### Health Checks

After deployment, verify:

1. **Frontend**:
   - Visit CloudFront distribution URL
   - Verify application loads correctly
   - Check browser console for errors

2. **Backend**:
   - Test API endpoints
   - Check Lambda function logs
   - Verify API Gateway responses

## Troubleshooting

### CI Workflow Fails

- Check workflow logs in GitHub Actions
- Verify all dependencies are installed
- Check for linting or test failures
- Ensure all required files are committed

### Frontend Deployment Fails

- Verify S3 bucket exists and is accessible
- Check IAM permissions for S3 operations
- Verify `S3_BUCKET_NAME` secret is set correctly
- Check CloudFront distribution ID is correct

### Backend Deployment Fails

- Verify CDK bootstrap is complete
- Check IAM permissions for CloudFormation
- Verify Lambda stack dependencies (Database, Cognito) are deployed
- Check CloudFormation stack events for errors

### Deployment Stuck

- Check CloudFormation stack status
- Review stack events for errors
- Cancel and retry if needed
- Contact AWS support if persistent issues

## Emergency Procedures

### Immediate Rollback

1. **Frontend**: Redeploy previous commit via GitHub Actions
2. **Backend**: Use CDK rollback or CloudFormation console
3. **Notify**: Alert team of rollback and reason

### Disable Automatic Deployments

1. Temporarily disable workflow:
   - Go to workflow file
   - Comment out `push` trigger
   - Commit and push

2. Or use branch protection to prevent merges

## Best Practices

1. **Always test locally** before pushing
2. **Review CI results** before merging PRs
3. **Monitor deployments** after pushing to main
4. **Keep deployment documentation** up to date
5. **Use feature branches** for development
6. **Tag releases** for production deployments
7. **Document rollback procedures** for each environment
8. **Regularly rotate** AWS credentials
9. **Use OIDC** for production (instead of access keys)
10. **Enable CloudWatch alarms** for critical functions

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [AWS CDK Documentation](https://docs.aws.amazon.com/cdk/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [CloudFront Best Practices](https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/best-practices.html)



