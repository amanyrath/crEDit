#!/bin/bash
# Quick script to set environment variables for seeding script

# Set AWS region (change if different)
export AWS_REGION=${AWS_REGION:-us-east-1}

echo "🔍 Retrieving configuration from AWS Secrets Manager..."

# Get Cognito User Pool ID
COGNITO_USER_POOL_ID=$(aws secretsmanager get-secret-value \
  --secret-id spendsense/cognito/configuration \
  --region $AWS_REGION \
  --query SecretString \
  --output text 2>/dev/null | jq -r '.user_pool_id' 2>/dev/null)

if [ -z "$COGNITO_USER_POOL_ID" ] || [ "$COGNITO_USER_POOL_ID" == "null" ]; then
  echo "⚠️  Could not retrieve COGNITO_USER_POOL_ID from Secrets Manager"
  echo "   Trying CloudFormation stack outputs..."
  COGNITO_USER_POOL_ID=$(aws cloudformation describe-stacks \
    --stack-name SpendSense-Cognito-dev \
    --region $AWS_REGION \
    --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
    --output text 2>/dev/null)
fi

if [ -z "$COGNITO_USER_POOL_ID" ] || [ "$COGNITO_USER_POOL_ID" == "null" ]; then
  echo "❌ Failed to get COGNITO_USER_POOL_ID"
  echo "   Please set it manually: export COGNITO_USER_POOL_ID=your-pool-id"
else
  export COGNITO_USER_POOL_ID
  echo "✅ COGNITO_USER_POOL_ID=$COGNITO_USER_POOL_ID"
fi

# Get Database URL
DATABASE_URL=$(aws secretsmanager get-secret-value \
  --secret-id spendsense/database/connection \
  --region $AWS_REGION \
  --query SecretString \
  --output text 2>/dev/null | jq -r '.connection_string' 2>/dev/null)

if [ -z "$DATABASE_URL" ] || [ "$DATABASE_URL" == "null" ]; then
  echo "⚠️  Could not retrieve DATABASE_URL from Secrets Manager"
  echo "   You may need to run: infrastructure/scripts/update_connection_string.py"
  echo "   Or set it manually: export DATABASE_URL=postgresql://user:pass@host:5432/dbname"
else
  export DATABASE_URL
  echo "✅ DATABASE_URL configured (hidden for security)"
fi

echo ""
echo "📋 Configuration complete!"
echo ""
echo "To run the seeding script:"
echo "  cd spendsense-backend"
echo "  python scripts/seed_demo_data.py"
echo ""


