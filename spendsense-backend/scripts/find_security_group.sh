#!/bin/bash
# Script to find the RDS database security group ID

set -e

STACK_NAME="SpendSense-Database-dev"
REGION="us-east-1"

echo "🔍 Finding security groups in stack: $STACK_NAME"
echo ""

# Method 1: Try to find by logical resource ID
echo "Method 1: Looking for DatabaseSecurityGroup..."
SG_ID=$(aws cloudformation describe-stack-resources \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "StackResources[?LogicalResourceId=='DatabaseSecurityGroup'].PhysicalResourceId" \
    --output text 2>/dev/null || echo "")

if [ -n "$SG_ID" ] && [ "$SG_ID" != "None" ] && [ "$SG_ID" != "null" ]; then
    echo "✅ Found: $SG_ID"
    echo ""
    echo "📋 Security Group Details:"
    aws ec2 describe-security-groups --group-ids "$SG_ID" --region "$REGION" --query 'SecurityGroups[0].{GroupId:GroupId,GroupName:GroupName,Description:Description,VpcId:VpcId}' --output table
    exit 0
fi

# Method 2: List all security groups in the stack
echo "Method 2: Listing all security groups in stack..."
echo ""
aws cloudformation describe-stack-resources \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "StackResources[?ResourceType=='AWS::EC2::SecurityGroup'].{LogicalId:LogicalResourceId,PhysicalId:PhysicalResourceId}" \
    --output table

echo ""
echo "Method 3: Finding by description..."
aws ec2 describe-security-groups \
    --region "$REGION" \
    --filters "Name=description,Values=*Database*" \
    --query 'SecurityGroups[*].{GroupId:GroupId,GroupName:GroupName,Description:Description}' \
    --output table

echo ""
echo "💡 Use one of the GroupIds above for the security group rule"

