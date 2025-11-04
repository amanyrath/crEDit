#!/bin/bash
# Script to retrieve AWS resource values for GitHub Secrets configuration
# Usage: ./get_github_secrets_values.sh [environment]
# Example: ./get_github_secrets_values.sh dev

set -e

ENVIRONMENT=${1:-dev}
REGION=${AWS_REGION:-us-east-1}

echo "=========================================="
echo "GitHub Secrets Configuration Values"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "=========================================="
echo ""

# Get S3 bucket name
echo "📦 S3 Bucket Name:"
S3_BUCKET_NAME=$(aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-$ENVIRONMENT \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
  --output text 2>/dev/null || echo "")

if [ -n "$S3_BUCKET_NAME" ]; then
  echo "  S3_BUCKET_NAME: $S3_BUCKET_NAME"
else
  echo "  ⚠️  S3 stack not found or not deployed"
fi

echo ""

# Get CloudFront Distribution ID
echo "🌐 CloudFront Distribution ID:"
CLOUDFRONT_DIST_ID=$(aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-$ENVIRONMENT \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text 2>/dev/null || echo "")

if [ -n "$CLOUDFRONT_DIST_ID" ]; then
  echo "  CLOUDFRONT_DISTRIBUTION_ID: $CLOUDFRONT_DIST_ID"
else
  echo "  ⚠️  CloudFront distribution not found"
fi

echo ""

# Get CloudFront URL
echo "🔗 CloudFront Distribution URL:"
CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-$ENVIRONMENT \
  --region $REGION \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionUrl`].OutputValue' \
  --output text 2>/dev/null || echo "")

if [ -n "$CLOUDFRONT_URL" ]; then
  echo "  URL: $CLOUDFRONT_URL"
fi

echo ""

# Verify Lambda stack exists
echo "⚡ Lambda Stack Status:"
LAMBDA_STACK_STATUS=$(aws cloudformation describe-stacks \
  --stack-name SpendSense-Lambda-$ENVIRONMENT \
  --region $REGION \
  --query 'Stacks[0].StackStatus' \
  --output text 2>/dev/null || echo "NOT_FOUND")

if [ "$LAMBDA_STACK_STATUS" != "NOT_FOUND" ]; then
  echo "  Stack Status: $LAMBDA_STACK_STATUS"
  echo "  Stack Name: SpendSense-Lambda-$ENVIRONMENT"
else
  echo "  ⚠️  Lambda stack not found or not deployed"
fi

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Copy these values to GitHub Secrets:"
echo "   - Go to: Settings → Secrets and variables → Actions"
echo "   - Add secrets as described in .github/GITHUB_SECRETS_SETUP.md"
echo ""
echo "2. Required Secrets:"
echo "   - AWS_ACCESS_KEY_ID (create IAM user first)"
echo "   - AWS_SECRET_ACCESS_KEY (create IAM user first)"
echo "   - AWS_REGION: $REGION"
if [ -n "$S3_BUCKET_NAME" ]; then
  echo "   - S3_BUCKET_NAME: $S3_BUCKET_NAME"
fi
if [ -n "$CLOUDFRONT_DIST_ID" ]; then
  echo "   - CLOUDFRONT_DISTRIBUTION_ID: $CLOUDFRONT_DIST_ID"
fi
echo "   - ENVIRONMENT: $ENVIRONMENT (optional, defaults to 'dev')"
echo ""
echo "3. Test workflows:"
echo "   - Push changes to trigger CI workflow"
echo "   - Use 'Run workflow' button to test deployments manually"
echo ""



