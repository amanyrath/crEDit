# Verify IAM Policy - Fixed Commands

## Step 1: Get Your Account ID and Policy ARN

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy"
```

## Step 2: Get the Default Version ID

```bash
VERSION_ID=$(aws iam get-policy --policy-arn "$POLICY_ARN" --query 'Policy.DefaultVersionId' --output text)
echo "Default version: $VERSION_ID"
```

## Step 3: View the Policy (Using the Version ID)

```bash
aws iam get-policy-version \
  --policy-arn "$POLICY_ARN" \
  --version-id "$VERSION_ID"
```

## Complete One-Liner (Fixed)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text) && \
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy" && \
VERSION_ID=$(aws iam get-policy --policy-arn "$POLICY_ARN" --query 'Policy.DefaultVersionId' --output text) && \
aws iam get-policy-version --policy-arn "$POLICY_ARN" --version-id "$VERSION_ID"
```

## List All Policy Versions

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws iam list-policy-versions \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy"
```

## Update Policy (Simplified)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws iam create-policy-version \
  --policy-arn "arn:aws:iam::${ACCOUNT_ID}:policy/GitHubActionsDeployPolicy" \
  --policy-document file://.github/github-actions-policy.json \
  --set-as-default
```

