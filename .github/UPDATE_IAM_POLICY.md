# How to Update Existing IAM Policy

Since the policy `GitHubActionsDeployPolicy` already exists, you need to update it with a new version.

## Option 1: Update Existing Policy (Recommended)

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create a new policy version with the updated permissions
aws iam create-policy-version \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy \
  --policy-document file://.github/github-actions-policy.json \
  --set-as-default
```

This will:
1. Create a new version of the existing policy with updated permissions
2. Set it as the default version (automatically replaces the old version)

## Option 2: Delete and Recreate (If Option 1 Fails)

If you need to delete and recreate:

```bash
# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# 1. Detach policy from user first
aws iam detach-user-policy \
  --user-name github-actions-deploy \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy

# 2. List all policy versions and delete non-default versions
aws iam list-policy-versions \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy \
  --query 'Versions[?IsDefaultVersion==`false`].VersionId' \
  --output text | xargs -I {} aws iam delete-policy-version \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy \
    --version-id {}

# 3. Delete the default version (requires deleting non-default versions first)
aws iam delete-policy-version \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy \
  --version-id v1

# 4. Delete the policy
aws iam delete-policy \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy

# 5. Recreate the policy
aws iam create-policy \
  --policy-name GitHubActionsDeployPolicy \
  --policy-document file://.github/github-actions-policy.json \
  --description "Permissions for GitHub Actions CI/CD deployment"

# 6. Reattach to user
aws iam attach-user-policy \
  --user-name github-actions-deploy \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy
```

## Verify Policy Update

After updating, verify the policy has the correct permissions:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# List policy versions
aws iam list-policy-versions \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy

# Get the default policy version
aws iam get-policy-version \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy \
  --version-id v2
```

## Quick Update Command

Run this single command to update the policy:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text) && \
aws iam create-policy-version \
  --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy \
  --policy-document file://.github/github-actions-policy.json \
  --set-as-default
```

This will update the existing policy with the new permissions without requiring deletion.

