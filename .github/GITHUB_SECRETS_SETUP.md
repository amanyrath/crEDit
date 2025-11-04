# GitHub Secrets Setup Guide

This document describes how to configure GitHub Secrets for CI/CD workflows.

## Required Secrets

### Core AWS Credentials

| Secret Name | Description | Example |
|------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key for GitHub Actions | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region for deployments | `us-east-1` |

### Frontend Deployment (Optional - Required for deploy-frontend.yml)

| Secret Name | Description | Example |
|------------|-------------|---------|
| `S3_BUCKET_NAME` | S3 bucket name for frontend hosting | `spendsense-frontend-dev` |
| `CLOUDFRONT_DISTRIBUTION_ID` | CloudFront distribution ID | `E1234567890ABC` |

### Backend Deployment (Optional - Required for deploy-backend.yml)

| Secret Name | Description | Example |
|------------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `dev`, `staging`, `prod` |

## Setting Up GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

## Creating IAM User for GitHub Actions

### Step 1: Create IAM User

```bash
aws iam create-user --user-name github-actions-deploy
```

### Step 2: Create Access Key

```bash
aws iam create-access-key --user-name github-actions-deploy
```

Save the `AccessKeyId` and `SecretAccessKey` - these will be used as GitHub Secrets.

### Step 3: Create IAM Policy

Create a policy file `github-actions-policy.json`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::spendsense-frontend-*",
        "arn:aws:s3:::spendsense-frontend-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:DescribeStacks",
        "cloudformation:DescribeStackEvents",
        "cloudformation:DescribeStackResource",
        "cloudformation:DescribeStackResources",
        "cloudformation:CreateStack",
        "cloudformation:UpdateStack",
        "cloudformation:DeleteStack",
        "cloudformation:GetTemplate",
        "cloudformation:ValidateTemplate"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "apigateway:*",
        "iam:PassRole",
        "iam:GetRole",
        "iam:CreateRole",
        "iam:AttachRolePolicy",
        "iam:PutRolePolicy",
        "iam:UpdateRole",
        "iam:DeleteRole",
        "iam:ListAttachedRolePolicies",
        "iam:ListRolePolicies",
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:DescribeLogGroups",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "ec2:CreateNetworkInterface",
        "ec2:DescribeNetworkInterfaces",
        "ec2:DeleteNetworkInterface"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:*:*:secret:spendsense/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "ssm:GetParameter",
        "ssm:GetParameters"
      ],
      "Resource": "arn:aws:ssm:*:*:parameter/cdk/*"
    }
  ]
}
```

### Step 4: Attach Policy to User

```bash
aws iam create-policy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://github-actions-policy.json

aws iam attach-user-policy \
  --user-name github-actions-deploy \
  --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/GitHubActionsDeployPolicy
```

Replace `YOUR_ACCOUNT_ID` with your AWS account ID.

## Security Best Practices

### Option 1: IAM User with Access Keys (Current Approach)

- **Pros**: Simple to set up, works immediately
- **Cons**: Long-lived credentials, need to rotate manually
- **Best for**: MVP, development environments

### Option 2: IAM Roles with OIDC (Recommended for Production)

For production, consider using IAM roles with OIDC (OpenID Connect) to avoid storing long-lived credentials:

1. Create an OIDC provider in AWS IAM
2. Create an IAM role that trusts GitHub
3. Update workflows to use `role-to-assume` instead of access keys

Example workflow change:
```yaml
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::ACCOUNT_ID:role/github-actions-role
    aws-region: us-east-1
```

See [AWS documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) for detailed setup.

## Verifying Secrets

After setting up secrets, verify they are configured:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Verify all required secrets are listed
3. Secrets are masked in workflow logs (they appear as `***`)

## Troubleshooting

### Workflow fails with "Access Denied"

- Verify IAM user has correct permissions
- Check that policy is attached to the user
- Verify secret values are correct (no extra spaces)

### S3 deployment fails

- Verify `S3_BUCKET_NAME` secret is set
- Verify bucket exists and IAM user has access
- Check bucket policy allows actions from IAM user

### CloudFront invalidation fails

- Verify `CLOUDFRONT_DISTRIBUTION_ID` secret is set
- Verify distribution ID is correct
- Check IAM user has `cloudfront:CreateInvalidation` permission

### CDK deployment fails

- Verify CDK bootstrap is complete: `cdk bootstrap aws://ACCOUNT_ID/REGION`
- Check IAM user has CloudFormation permissions
- Verify Lambda stack name matches (`SpendSense-Lambda-dev`)

## Rotating Credentials

To rotate AWS access keys:

1. Create new access key for IAM user
2. Update GitHub Secrets with new values
3. Test workflow with new credentials
4. Delete old access key from AWS

## References

- [GitHub Actions Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)

