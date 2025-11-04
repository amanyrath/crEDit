# IAM Setup Guide for GitHub Actions

This guide explains how to set up IAM permissions for GitHub Actions CI/CD workflows.

## Overview

The IAM policy in `.github/github-actions-policy.json` includes permissions for:

- **S3 Frontend Deployment**: Deploy frontend assets to S3
- **CDK Bootstrap**: Access CDK bootstrap bucket
- **CloudFront**: Create invalidations for cache clearing
- **CloudFormation**: Deploy and manage CDK stacks
- **Lambda**: Deploy and manage Lambda functions
- **API Gateway**: Manage API Gateway resources
- **IAM Roles**: Create and manage IAM roles for Lambda functions
- **CloudWatch Logs**: Create log groups for Lambda functions
- **EC2/VPC**: Describe VPC resources for Lambda VPC configuration
- **Secrets Manager**: Read secrets (database, Cognito config)
- **SSM Parameters**: Read/write CDK parameters
- **STS**: Assume roles and verify identity
- **EventBridge**: Manage EventBridge rules for Lambda triggers

## Step-by-Step Setup

### 1. Create IAM User

```bash
aws iam create-user --user-name github-actions-deploy
```

### 2. Create Access Key

```bash
aws iam create-access-key --user-name github-actions-deploy
```

**Important**: Save the `AccessKeyId` and `SecretAccessKey` immediately - you won't be able to see the secret key again!

### 3. Create IAM Policy

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create the policy
aws iam create-policy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://.github/github-actions-policy.json \
  --description "Permissions for GitHub Actions CI/CD deployment"
```

This will output a Policy ARN like:
```
arn:aws:iam::123456789012:policy/GitHubActionsDeployPolicy
```

### 4. Attach Policy to User

```bash
# Replace ACCOUNT_ID with your actual AWS account ID
aws iam attach-user-policy \
  --user-name github-actions-deploy \
  --policy-arn arn:aws:iam::ACCOUNT_ID:policy/GitHubActionsDeployPolicy
```

### 5. Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add these secrets:

| Secret Name | Value | Source |
|------------|-------|--------|
| `AWS_ACCESS_KEY_ID` | Access key ID from step 2 | `AccessKeyId` |
| `AWS_SECRET_ACCESS_KEY` | Secret access key from step 2 | `SecretAccessKey` |
| `AWS_REGION` | Your AWS region | e.g., `us-east-1` |
| `ENVIRONMENT` | Deployment environment | `dev`, `staging`, `prod` |
| `S3_BUCKET_NAME` | S3 bucket name | From S3 stack deployment |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID | From S3 stack deployment |

### 6. Verify Permissions

Test that the credentials work:

```bash
# Set credentials
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-east-1"

# Verify identity
aws sts get-caller-identity

# Test S3 access (if bucket exists)
aws s3 ls s3://spendsense-frontend-dev/

# Test CloudFormation access
aws cloudformation list-stacks --max-items 5
```

## Permission Breakdown

### S3 Permissions

**Frontend Deployment** (`s3:PutObject`, `s3:GetObject`, `s3:DeleteObject`, `s3:ListBucket`)
- Required for: Deploying frontend assets to S3
- Resources: `arn:aws:s3:::spendsense-frontend-*` and `arn:aws:s3:::spendsense-frontend-*/*`

**CDK Bootstrap** (`s3:GetObject`, `s3:PutObject`, `s3:ListBucket`)
- Required for: CDK bootstrap bucket access
- Resources: `arn:aws:s3:::cdk-*` and `arn:aws:s3:::cdk-*/*`

### CloudFront Permissions

**Invalidation** (`cloudfront:CreateInvalidation`, `cloudfront:GetInvalidation`, `cloudfront:ListInvalidations`)
- Required for: Clearing CloudFront cache after frontend deployment
- Resources: `*` (all distributions)

### CloudFormation Permissions

**CDK Stack Management**
- `cloudformation:CreateStack`, `cloudformation:UpdateStack`, `cloudformation:DeleteStack`
- `cloudformation:DescribeStacks`, `cloudformation:DescribeStackEvents`
- `cloudformation:DescribeChangeSet`, `cloudformation:CreateChangeSet`, `cloudformation:ExecuteChangeSet`
- Required for: Deploying and managing CDK stacks
- Resources: `*` (all stacks)

### Lambda Permissions

**Function Management**
- `lambda:CreateFunction`, `lambda:UpdateFunctionCode`, `lambda:UpdateFunctionConfiguration`
- `lambda:DeleteFunction`, `lambda:GetFunction`, `lambda:ListFunctions`
- `lambda:AddPermission`, `lambda:RemovePermission`
- Required for: Deploying and managing Lambda functions
- Resources: `*` (all Lambda functions)

### API Gateway Permissions

**Full Access** (`apigateway:*`)
- Required for: Creating and managing API Gateway REST APIs
- Resources: `*` (all API Gateway resources)

### IAM Permissions

**Role Management**
- `iam:CreateRole`, `iam:UpdateRole`, `iam:DeleteRole`
- `iam:AttachRolePolicy`, `iam:PutRolePolicy`, `iam:GetRole`
- `iam:PassRole` (critical for Lambda execution roles)
- Required for: Creating IAM roles for Lambda functions
- Resources: `*` (all IAM roles)

### CloudWatch Logs Permissions

**Log Group Management**
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`
- `logs:DescribeLogGroups`, `logs:DeleteLogGroup`
- Required for: Creating log groups for Lambda functions
- Resources: `*` (all log groups)

### EC2/VPC Permissions

**Network Resource Discovery**
- `ec2:DescribeVpcs`, `ec2:DescribeSubnets`, `ec2:DescribeSecurityGroups`
- `ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`, `ec2:DeleteNetworkInterface`
- Required for: Lambda VPC configuration
- Resources: `*` (all VPC resources)

### Secrets Manager Permissions

**Read Secrets**
- `secretsmanager:GetSecretValue`, `secretsmanager:DescribeSecret`
- Required for: Reading database connection strings and Cognito configuration
- Resources: `arn:aws:secretsmanager:*:*:secret:spendsense/*`

### SSM Parameter Store Permissions

**CDK Parameter Management**
- `ssm:GetParameter`, `ssm:GetParameters`, `ssm:PutParameter`, `ssm:DeleteParameter`
- Required for: CDK context and parameter storage
- Resources: `arn:aws:ssm:*:*:parameter/cdk/*`

### STS Permissions

**Identity Verification**
- `sts:GetCallerIdentity`, `sts:AssumeRole`
- Required for: Verifying credentials and assuming roles
- Resources: `*`

### EventBridge Permissions

**Rule Management**
- `events:PutRule`, `events:DeleteRule`, `events:DescribeRule`
- `events:PutTargets`, `events:RemoveTargets`, `events:ListTargetsByRule`
- Required for: Creating EventBridge rules for Lambda triggers
- Resources: `*` (all EventBridge rules)

## Security Best Practices

### 1. Least Privilege

The policy is scoped to specific resources where possible:
- S3 buckets: `spendsense-frontend-*`
- Secrets: `spendsense/*`
- SSM Parameters: `cdk/*`

### 2. Resource Naming Convention

Ensure your AWS resources follow naming conventions:
- S3 buckets: `spendsense-frontend-{environment}`
- Secrets: `spendsense/*`
- CDK stacks: `SpendSense-*-{environment}`

### 3. Rotate Credentials Regularly

- Rotate access keys every 90 days
- Use separate keys for different environments if possible
- Monitor access key usage in CloudTrail

### 4. Consider OIDC for Production

For production environments, consider using IAM roles with OIDC instead of access keys:
- No long-lived credentials
- Temporary credentials automatically rotated
- Better security posture

See `.github/GITHUB_SECRETS_SETUP.md` for OIDC setup instructions.

## Troubleshooting

### "Access Denied" Errors

1. **Verify policy is attached**:
   ```bash
   aws iam list-attached-user-policies --user-name github-actions-deploy
   ```

2. **Check policy permissions**:
   ```bash
   aws iam get-policy-version \
     --policy-arn arn:aws:iam::ACCOUNT_ID:policy/GitHubActionsDeployPolicy \
     --version-id v1
   ```

3. **Test specific permissions**:
   ```bash
   aws iam simulate-principal-policy \
     --policy-source-arn arn:aws:iam::ACCOUNT_ID:user/github-actions-deploy \
     --action-names s3:PutObject \
     --resource-arns arn:aws:s3:::spendsense-frontend-dev/test.txt
   ```

### CDK Bootstrap Issues

If CDK deployment fails with bootstrap errors:

```bash
# Bootstrap CDK (requires admin permissions)
cdk bootstrap aws://ACCOUNT_ID/REGION
```

The IAM user needs `s3:PutObject` and `s3:GetObject` on the CDK bootstrap bucket.

### S3 Deployment Fails

1. Verify bucket exists: `aws s3 ls s3://spendsense-frontend-dev`
2. Check bucket policy allows the IAM user
3. Verify `S3_BUCKET_NAME` secret matches actual bucket name

### CloudFormation Stack Creation Fails

1. Check IAM permissions: `iam:PassRole` is critical
2. Verify CDK bootstrap is complete
3. Check CloudFormation stack limits
4. Review CloudFormation events: `aws cloudformation describe-stack-events --stack-name SpendSense-Lambda-dev`

## References

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS CDK Security](https://docs.aws.amazon.com/cdk/v2/guide/security.html)
- [IAM Policy Simulator](https://policysim.aws.amazon.com/)

