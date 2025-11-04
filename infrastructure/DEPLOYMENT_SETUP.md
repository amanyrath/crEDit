# Deployment Setup Guide

Complete guide for setting up and deploying the SpendSense database infrastructure.

## Prerequisites Checklist

### 1. AWS Account Setup

**AWS Console:**
- ✅ AWS account with appropriate permissions
- ✅ IAM user or role with permissions to create:
  - RDS instances
  - Secrets Manager secrets
  - KMS keys
  - VPC resources (security groups, subnets)
  - CloudFormation stacks
  - IAM roles and policies

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "rds:*",
        "secretsmanager:*",
        "kms:*",
        "ec2:*",
        "cloudformation:*",
        "iam:*",
        "s3:*",
        "ssm:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### 2. AWS CLI Configuration

**Install AWS CLI** (if not already installed):
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

**Configure AWS Credentials:**
```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Your IAM user access key
- **AWS Secret Access Key**: Your IAM user secret key
- **Default region name**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

**Verify Configuration:**
```bash
aws sts get-caller-identity
```

This should return your AWS account ID, user ARN, and user ID.

**Alternative: Environment Variables** (if not using `aws configure`):
```bash
export AWS_ACCESS_KEY_ID=your-access-key-id
export AWS_SECRET_ACCESS_KEY=your-secret-access-key
export AWS_DEFAULT_REGION=us-east-1
```

### 3. AWS CDK Setup

**Install Node.js** (required for CDK CLI):
```bash
# macOS
brew install node

# Verify
node --version  # Should be v18.x or later
npm --version
```

**Install AWS CDK CLI:**
```bash
npm install -g aws-cdk

# Verify installation
cdk --version
```

**Install Python Dependencies:**
```bash
cd infrastructure/cdk
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Environment Variables

**Option A: Export in your shell** (recommended for deployment):
```bash
export AWS_REGION=us-east-1
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

**Option B: Create `.env` file** (for local development):
```bash
# infrastructure/cdk/.env (optional, CDK reads from AWS CLI config)
AWS_REGION=us-east-1
CDK_DEFAULT_ACCOUNT=your-aws-account-id
```

**Option C: Use CDK context** (no .env needed):
The CDK app will automatically detect your account from AWS CLI config, and region defaults to `us-east-1` or can be passed via context.

### 5. CDK Bootstrap (First Time Only)

CDK needs to bootstrap your AWS account/region to set up S3 buckets and IAM roles for deployments.

**Bootstrap your account:**
```bash
cd infrastructure/cdk
source venv/bin/activate  # If not already activated

# Bootstrap in your default region
cdk bootstrap

# Or bootstrap in a specific region
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

**Verify Bootstrap:**
```bash
aws cloudformation describe-stacks --stack-name CDKToolkit --region us-east-1
```

## CDK Configuration

### cdk.json

The `cdk.json` file is already configured correctly:
- ✅ App command: `python3 app.py`
- ✅ CDK feature flags configured
- ✅ No changes needed

### app.py Configuration

The `app.py` reads configuration in this order:
1. **Environment name**: From CDK context `--context environment=dev` or defaults to `dev`
2. **Region**: From CDK context `--context region=us-east-1` or environment variable `AWS_REGION` or defaults to `us-east-1`
3. **Account ID**: From environment variable `CDK_DEFAULT_ACCOUNT` (auto-detected from AWS CLI if not set)

**You don't need to modify `app.py`** - it will auto-detect your account from AWS CLI.

## Deployment Steps

### Step 1: Verify Prerequisites

```bash
# Check AWS credentials
aws sts get-caller-identity

# Check CDK
cdk --version

# Check Python and dependencies
cd infrastructure/cdk
source venv/bin/activate
python3 --version
pip list | grep aws-cdk
```

### Step 2: Synthesize Stack (Preview)

```bash
cd infrastructure/cdk
source venv/bin/activate

# Generate CloudFormation template (dry run)
cdk synth SpendSense-Database-dev
```

This will show you what will be created without actually deploying.

### Step 3: Deploy

**Basic deployment (uses defaults):**
```bash
cdk deploy SpendSense-Database-dev
```

**With explicit region:**
```bash
cdk deploy SpendSense-Database-dev --context region=us-east-1
```

**With custom environment name:**
```bash
cdk deploy SpendSense-Database-dev --context environment=dev --context region=us-east-1
```

**CDK will:**
1. Ask for confirmation (type `y`)
2. Show changes to be made
3. Create/update the CloudFormation stack
4. Take 10-15 minutes (RDS instance creation)

### Step 4: Get Stack Outputs

After deployment, note the outputs:
```bash
aws cloudformation describe-stacks \
  --stack-name SpendSense-Database-dev \
  --query 'Stacks[0].Outputs' \
  --output table
```

Or view in AWS Console:
- Go to CloudFormation → Stacks → SpendSense-Database-dev → Outputs

### Step 5: Update Connection String Secret

After deployment, update the connection string secret:
```bash
cd infrastructure/scripts
python3 update_connection_string.py
```

Or with custom parameters:
```bash
python3 update_connection_string.py \
  --stack-name SpendSense-Database-dev \
  --region us-east-1
```

### Step 6: Test Connection (Optional)

```bash
# Install PostgreSQL client (if not already installed)
# macOS
brew install postgresql

# Install Python dependencies
pip install psycopg2-binary boto3

# Test connection
cd infrastructure/scripts
python3 test_connection.py
```

## AWS Console Verification

After deployment, verify in AWS Console:

### 1. RDS Database
- **Console**: RDS → Databases
- **Check**: Instance `SpendSense-Database-dev-PostgreSQLDatabase*` is `Available`
- **Check**: Engine version is PostgreSQL 15.4
- **Check**: Instance class is `db.t3.micro`
- **Check**: Encryption shows KMS key

### 2. Secrets Manager
- **Console**: Secrets Manager
- **Check**: Secret `spendsense/database/credentials` exists
- **Check**: Secret `spendsense/database/connection` exists (after running update script)

### 3. Security Groups
- **Console**: EC2 → Security Groups
- **Check**: `DatabaseSecurityGroup` allows inbound from `LambdaSecurityGroup` on port 5432
- **Check**: `LambdaSecurityGroup` exists

### 4. KMS Key
- **Console**: KMS → Customer managed keys
- **Check**: Key for database encryption exists

### 5. CloudFormation Stack
- **Console**: CloudFormation → Stacks
- **Check**: Stack `SpendSense-Database-dev` is `CREATE_COMPLETE`
- **Check**: All resources created successfully

## Troubleshooting

### Issue: "CDK_DEFAULT_ACCOUNT not set"

**Solution**: CDK auto-detects from AWS CLI. Verify:
```bash
aws sts get-caller-identity
```

If it works, CDK will auto-detect. If you need to set explicitly:
```bash
export CDK_DEFAULT_ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

### Issue: "No default VPC found"

**Solution**: The stack uses the default VPC. Create one or modify the stack:
```bash
# Check for default VPC
aws ec2 describe-vpcs --filters "Name=isDefault,Values=true"

# If none exists, create default VPC
aws ec2 create-default-vpc --region us-east-1
```

Or modify `database_stack.py` to use a specific VPC ID.

### Issue: "Insufficient permissions"

**Solution**: Check IAM permissions:
```bash
aws iam get-user
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

Ensure you have permissions for RDS, Secrets Manager, KMS, EC2, and CloudFormation.

### Issue: "Bootstrap not found"

**Solution**: Bootstrap your account:
```bash
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

### Issue: "Subnet group creation failed"

**Solution**: Ensure your default VPC has subnets in at least 2 availability zones. Check:
```bash
aws ec2 describe-subnets --filters "Name=vpc-id,Values=VPC_ID"
```

## Environment-Specific Configuration

### Development (dev)
```bash
cdk deploy SpendSense-Database-dev --context environment=dev --context region=us-east-1
```

### Production (prod)
Before deploying to production, update `database_stack.py`:
- Set `deletion_protection=True`
- Set `multi_az=True`
- Set `removal_policy=RemovalPolicy.RETAIN`

Then deploy:
```bash
cdk deploy SpendSense-Database-prod --context environment=prod --context region=us-east-1
```

## Cost Estimation

Before deploying, understand costs:
- **db.t3.micro**: ~$15/month (free tier eligible in first year)
- **Storage (20GB gp2)**: ~$2.30/month
- **Backups**: Included in storage
- **Secrets Manager**: $0.40/month per secret (2 secrets = $0.80/month)
- **KMS**: $1/month per key + $0.03 per 10,000 requests

**Estimated total**: ~$19/month (or free tier eligible)

## Next Steps

After successful deployment:
1. ✅ Update connection string secret (Step 5 above)
2. ✅ Test connection (Step 6 above)
3. ✅ Configure local development access (see README.md)
4. ✅ Proceed to Story 1.4: Create Database Schema

## Quick Reference

```bash
# Setup
cd infrastructure/cdk
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cdk bootstrap

# Deploy
cdk deploy SpendSense-Database-dev

# Update connection string
cd ../scripts
python3 update_connection_string.py

# Test
python3 test_connection.py
```

