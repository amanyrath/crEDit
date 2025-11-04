# SpendSense Infrastructure

Infrastructure as Code for SpendSense using AWS CDK (Python).

## Prerequisites

See [DEPLOYMENT_SETUP.md](./DEPLOYMENT_SETUP.md) for complete setup instructions.

**Quick Checklist:**
1. ✅ AWS CLI configured (`aws configure`)
2. ✅ AWS CDK CLI installed (`npm install -g aws-cdk`)
3. ✅ Python 3.11+ and dependencies installed
4. ✅ CDK bootstrapped (`cdk bootstrap`)

**Required Environment Variables:**
- `AWS_REGION` (optional, defaults to `us-east-1`)
- `CDK_DEFAULT_ACCOUNT` (auto-detected from AWS CLI, optional)

**No `.env` file needed** - CDK reads from AWS CLI configuration automatically.

## Setup

1. **Navigate to CDK directory**
   ```bash
   cd infrastructure/cdk
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Deployment

### Deploy Database Stack

```bash
# Deploy to default environment (dev)
cdk deploy SpendSense-Database-dev

# Deploy to specific environment
cdk deploy SpendSense-Database-dev --context environment=dev --context region=us-east-1
```

### View Stack Outputs

After deployment, stack outputs will show:
- Database endpoint
- Database port
- Database name
- Credentials secret ARN
- Connection string secret ARN
- Lambda security group ID

## Post-Deployment Steps

### 1. Update Connection String Secret

After the database is created, you need to update the connection string secret with the actual database endpoint and credentials.

The connection string format is:
```
postgresql://username:password@host:5432/database_name
```

**Option A: Using AWS CLI**

1. Get the database endpoint from stack outputs:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Database-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`DatabaseEndpoint`].OutputValue' \
     --output text
   ```

2. Get the database credentials from Secrets Manager:
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id spendsense/database/credentials \
     --query SecretString \
     --output text | jq
   ```

3. Update the connection string secret:
   ```bash
   aws secretsmanager put-secret-value \
     --secret-id spendsense/database/connection \
     --secret-string '{"host":"<endpoint>","port":"5432","database":"spendsense","username":"spendsense_admin","password":"<password>","connection_string":"postgresql://spendsense_admin:<password>@<endpoint>:5432/spendsense"}'
   ```

**Option B: Using Python Script**

A helper script will be created in `infrastructure/scripts/` to automate this.

### 2. Configure Local Development Access

For local development, you'll need to configure security group rules to allow your IP address:

```bash
# Get your public IP
MY_IP=$(curl -s https://checkip.amazonaws.com)

# Add security group rule (replace SECURITY_GROUP_ID with the database security group ID)
aws ec2 authorize-security-group-ingress \
  --group-id <SECURITY_GROUP_ID> \
  --protocol tcp \
  --port 5432 \
  --cidr $MY_IP/32 \
  --description "Temporary access for local development"
```

**Important:** Remove this rule when not developing locally for security.

## Testing Connection

### From Local Environment

1. **Install PostgreSQL client**
   ```bash
   # macOS
   brew install postgresql
   
   # Linux
   sudo apt-get install postgresql-client
   ```

2. **Get connection details from Secrets Manager**
   ```bash
   aws secretsmanager get-secret-value \
     --secret-id spendsense/database/connection \
     --query SecretString \
     --output text | jq -r '.connection_string'
   ```

3. **Test connection**
   ```bash
   psql "<connection_string>"
   ```

### Using Python Script

A test script will be created in `infrastructure/scripts/test_connection.py`.

## Security Considerations

1. **Never commit secrets** - All credentials are in AWS Secrets Manager
2. **Remove local development access** when not needed
3. **Enable deletion protection** in production (change `deletion_protection=False` to `True`)
4. **Enable Multi-AZ** in production (change `multi_az=False` to `True`)
5. **Use least privilege IAM policies** for Lambda functions accessing the database

## Connection Pooling

Lambda functions should use connection pooling to manage database connections efficiently. Consider:

- Using SQLAlchemy with connection pooling
- Configuring appropriate pool sizes based on Lambda concurrency
- Using RDS Proxy for better connection management (future enhancement)

## Troubleshooting

### CDK Bootstrap Issues

If you get errors about CDK not being bootstrapped:
```bash
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### VPC Issues

If you get errors about VPC not found:
- The stack uses the default VPC
- Ensure your AWS account has a default VPC
- Or modify the stack to use a specific VPC ID

### Security Group Rules

If you can't connect:
- Check security group rules allow your IP/security group
- Verify VPC routing is correct
- Check network ACLs

## Stack Structure

```
infrastructure/
├── cdk/
│   ├── app.py                    # CDK app entry point
│   ├── cdk.json                  # CDK configuration
│   ├── requirements.txt          # Python dependencies
│   └── stacks/
│       ├── __init__.py
│       └── database_stack.py     # RDS PostgreSQL stack
└── scripts/                      # Helper scripts
    └── (to be created)
```

## Cost Considerations

- **db.t3.micro**: ~$15/month (eligible for free tier in first year)
- **Storage**: $0.115/GB/month for gp2
- **Backups**: Included in storage cost (7-day retention)
- **Secrets Manager**: $0.40/month per secret
- **KMS**: $1/month per key + $0.03 per 10,000 requests

## Next Steps

After deploying the database stack:
1. Update connection string secret (see Post-Deployment Steps)
2. Test connection from local environment
3. Proceed to Story 1.4: Create Database Schema

