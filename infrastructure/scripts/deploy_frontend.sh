#!/bin/bash
# Deploy Frontend to S3 and CloudFront
# Usage: ./deploy_frontend.sh [environment]
# Example: ./deploy_frontend.sh dev

set -e  # Exit on error

# Get environment from argument or default to dev
ENVIRONMENT=${1:-dev}

# Get the script directory and project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
FRONTEND_DIR="$PROJECT_ROOT/spendsense-frontend"
BUCKET_NAME="spendsense-frontend-${ENVIRONMENT}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Deploying frontend to ${ENVIRONMENT} environment...${NC}"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Error: Frontend directory not found at $FRONTEND_DIR${NC}"
    echo "Expected frontend directory at: $FRONTEND_DIR"
    exit 1
fi

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Change to frontend directory
cd "$FRONTEND_DIR"

# Build frontend
echo -e "${YELLOW}Building frontend...${NC}"
npm run build

if [ ! -d "dist" ]; then
    echo -e "${RED}Error: Build output directory 'dist' not found${NC}"
    exit 1
fi

# Get CloudFront distribution ID from stack outputs
echo -e "${YELLOW}Retrieving CloudFront distribution ID...${NC}"
STACK_NAME="SpendSense-S3-${ENVIRONMENT}"
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionId'].OutputValue" \
    --output text \
    2>/dev/null || echo "")

if [ -z "$DISTRIBUTION_ID" ]; then
    echo -e "${YELLOW}Warning: Could not retrieve CloudFront distribution ID from stack${NC}"
    echo "You may need to manually invalidate CloudFront cache after deployment"
    DISTRIBUTION_ID=""
fi

# Sync build output to S3
echo -e "${YELLOW}Syncing files to S3 bucket: ${BUCKET_NAME}...${NC}"
aws s3 sync dist/ "s3://${BUCKET_NAME}" --delete

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to sync files to S3${NC}"
    exit 1
fi

echo -e "${GREEN}Files uploaded to S3 successfully${NC}"

# Invalidate CloudFront cache if distribution ID is available
if [ -n "$DISTRIBUTION_ID" ]; then
    echo -e "${YELLOW}Invalidating CloudFront cache...${NC}"
    INVALIDATION_ID=$(aws cloudfront create-invalidation \
        --distribution-id "$DISTRIBUTION_ID" \
        --paths "/*" \
        --query "Invalidation.Id" \
        --output text)
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}CloudFront cache invalidation created: ${INVALIDATION_ID}${NC}"
        echo "Cache invalidation may take a few minutes to complete"
    else
        echo -e "${YELLOW}Warning: Failed to create CloudFront invalidation${NC}"
    fi
else
    echo -e "${YELLOW}Skipping CloudFront cache invalidation (distribution ID not found)${NC}"
fi

# Get CloudFront URL from stack outputs
if [ -n "$DISTRIBUTION_ID" ]; then
    CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --query "Stacks[0].Outputs[?OutputKey=='CloudFrontDistributionUrl'].OutputValue" \
        --output text \
        2>/dev/null || echo "")
    
    if [ -n "$CLOUDFRONT_URL" ]; then
        echo -e "${GREEN}Deployment complete!${NC}"
        echo -e "${GREEN}Frontend URL: ${CLOUDFRONT_URL}${NC}"
    else
        echo -e "${GREEN}Deployment complete!${NC}"
        echo "Retrieve the CloudFront URL from the stack outputs:"
        echo "  aws cloudformation describe-stacks --stack-name $STACK_NAME --query 'Stacks[0].Outputs'"
    fi
else
    echo -e "${GREEN}Deployment complete!${NC}"
fi

