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

### Deploy Cognito Stack

```bash
# Deploy to default environment (dev)
cdk deploy SpendSense-Cognito-dev

# Deploy to specific environment
cdk deploy SpendSense-Cognito-dev --context environment=dev --context region=us-east-1
```

### Deploy Lambda Stack

**Prerequisites:** Database and Cognito stacks must be deployed first.

```bash
# Deploy to default environment (dev)
cdk deploy SpendSense-Lambda-dev

# Deploy to specific environment
cdk deploy SpendSense-Lambda-dev --context environment=dev --context region=us-east-1
```

### Deploy S3 Stack

**Prerequisites:** None (independent stack).

```bash
# Deploy to default environment (dev)
cdk deploy SpendSense-S3-dev

# Deploy to specific environment
cdk deploy SpendSense-S3-dev --context environment=dev --context region=us-east-1
```

### View Stack Outputs

After deployment, stack outputs will show:

**Database Stack:**
- Database endpoint
- Database port
- Database name
- Credentials secret ARN
- Connection string secret ARN
- Lambda security group ID

**Cognito Stack:**
- User Pool ID
- User Pool ARN
- User Pool Client ID
- Cognito configuration secret ARN

**Lambda Stack:**
- API Gateway endpoint URL
- API Gateway REST API ID
- API Lambda function ARN
- Compute Features Lambda function ARN
- Assign Persona Lambda function ARN
- Generate Recommendations Lambda function ARN

**S3 Stack:**
- Frontend bucket name
- Frontend bucket ARN
- Assets bucket name
- Assets bucket ARN
- CloudFront distribution ID
- CloudFront distribution URL
- CloudFront distribution domain name

## Post-Deployment Steps

### 1. Deploy Prerequisites

Before deploying the Lambda stack, ensure the following stacks are deployed:
1. Database Stack (`SpendSense-Database-dev`)
2. Cognito Stack (`SpendSense-Cognito-dev`)

The Lambda stack depends on outputs from these stacks (security groups, secret ARNs, User Pool ID).

### 2. Update Connection String Secret

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

Use the helper script to automate this:
```bash
cd infrastructure/scripts
python3 update_connection_string.py --stack-name SpendSense-Database-dev
```

### 3. Update Cognito Configuration Secret

After the Cognito stack is deployed, update the Cognito configuration secret with actual values:

**Option A: Using Python Script (Recommended)**

```bash
cd infrastructure/scripts
python3 update_cognito_config.py --stack-name SpendSense-Cognito-dev
```

**Option B: Using AWS CLI**

1. Get the Cognito configuration from stack outputs:
   ```bash
   aws cloudformation describe-stacks \
     --stack-name SpendSense-Cognito-dev \
     --query 'Stacks[0].Outputs' \
     --output json
   ```

2. Update the secret with the values:
   ```bash
   aws secretsmanager put-secret-value \
     --secret-id spendsense/cognito/configuration \
     --secret-string '{"user_pool_id":"<user_pool_id>","user_pool_arn":"<user_pool_arn>","client_id":"<client_id>","region":"us-east-1"}'
   ```

### 4. Create Demo Users

After updating the Cognito configuration secret, create demo users:

```bash
cd infrastructure/scripts
python3 create_demo_users.py
```

**Demo Account Credentials:**
- `hannah@demo.com` / `Demo123!` (Consumer)
- `sam@demo.com` / `Demo123!` (Consumer)
- `operator@demo.com` / `Demo123!` (Operator)

⚠️  **SECURITY WARNING:** These are demo accounts with intentionally weak passwords for testing purposes only. 
    These credentials should NEVER be used in production environments. Change all demo passwords immediately 
    in any production deployment.

**Note:** The password `Demo123!` meets Cognito password policy requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### 4. Configure Local Development Access

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

## Retrieving Cognito Configuration

### User Pool ID and Client ID

**Option A: From Stack Outputs**
```bash
aws cloudformation describe-stacks \
  --stack-name SpendSense-Cognito-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolId`].OutputValue' \
  --output text

aws cloudformation describe-stacks \
  --stack-name SpendSense-Cognito-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`UserPoolClientId`].OutputValue' \
  --output text
```

**Option B: From Secrets Manager**
```bash
aws secretsmanager get-secret-value \
  --secret-id spendsense/cognito/configuration \
  --query SecretString \
  --output text | jq
```

### Adding Users to Groups

To add a user to a group (consumers or operators):
```bash
aws cognito-idp admin-add-user-to-group \
  --user-pool-id <USER_POOL_ID> \
  --username <USERNAME> \
  --group-name consumers  # or "operators"
```

### Authenticating Users

Users can authenticate using:
- Direct sign-in with email/password (USER_PASSWORD_AUTH flow)
- Refresh token authentication (REFRESH_TOKEN_AUTH flow)

See Story 2.2 and 2.3 for backend integration details.

## S3 and CloudFront Configuration

### Retrieving CloudFront Distribution URL

**Option A: From Stack Outputs**
```bash
aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionUrl`].OutputValue' \
  --output text
```

**Option B: Get All S3 Stack Outputs**
```bash
aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-dev \
  --query 'Stacks[0].Outputs' \
  --output json
```

### S3 Bucket Names

- **Frontend Bucket:** `spendsense-frontend-{env}` (e.g., `spendsense-frontend-dev`)
- **Assets Bucket:** `spendsense-assets-{env}` (e.g., `spendsense-assets-dev`)

### Deploying Frontend to S3

**Option A: Using Deployment Script (Recommended)**

```bash
cd infrastructure/scripts
./deploy_frontend.sh dev
```

The script will:
1. Build the frontend (`npm run build`)
2. Sync files to S3 bucket
3. Invalidate CloudFront cache
4. Display the CloudFront URL

**Option B: Manual Deployment**

1. **Build the frontend:**
   ```bash
   cd spendsense-frontend
   npm run build
   ```

2. **Sync to S3:**
   ```bash
   aws s3 sync dist/ s3://spendsense-frontend-dev --delete
   ```

3. **Invalidate CloudFront cache:**
   ```bash
   # Get distribution ID
   DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
     --stack-name SpendSense-S3-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
     --output text)
   
   # Create invalidation
   aws cloudfront create-invalidation \
     --distribution-id $DISTRIBUTION_ID \
     --paths "/*"
   ```

### CloudFront Cache Invalidation

CloudFront caches content at edge locations. After deploying updates, you need to invalidate the cache:

```bash
# Get distribution ID
DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
  --stack-name SpendSense-S3-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
  --output text)

# Invalidate all paths
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/*"

# Or invalidate specific paths
aws cloudfront create-invalidation \
  --distribution-id $DISTRIBUTION_ID \
  --paths "/index.html" "/assets/*"
```

**Note:** Cache invalidation can take a few minutes to complete. You can check the status:
```bash
aws cloudfront list-invalidations \
  --distribution-id $DISTRIBUTION_ID
```

### CORS Configuration

CORS is configured on both S3 buckets to allow:
- All origins (for dev environment)
- Methods: GET, HEAD, OPTIONS
- Headers: All headers
- Exposed headers: ETag, Last-Modified

For production, restrict CORS to specific origins:
- Update CORS rules in `infrastructure/cdk/stacks/s3_stack.py`
- Redeploy the stack

### Bucket Policies

- **Public Access:** Blocked (all buckets)
- **CloudFront Access:** Enabled via Origin Access Identity (OAI)
- **Direct S3 Access:** Denied (only CloudFront can access)

### Testing Frontend Deployment

1. **Deploy the frontend** (see above)
2. **Get CloudFront URL:**
   ```bash
   CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
     --stack-name SpendSense-S3-dev \
     --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionUrl`].OutputValue' \
     --output text)
   
   echo "Frontend URL: $CLOUDFRONT_URL"
   ```

3. **Test in browser:**
   - Open the CloudFront URL in a browser
   - Verify the frontend loads correctly
   - Test SPA routing (navigate to different routes)
   - Verify 404 errors redirect to index.html

4. **Test SPA Routing:**
   - Navigate to a non-existent route (e.g., `/test-route`)
   - Should return index.html (not 404 error)
   - React Router should handle the route client-side

### CloudFront Configuration

- **Default Root Object:** `index.html`
- **Error Pages:** 404 and 403 errors redirect to `/index.html` (for SPA routing)
- **Viewer Protocol Policy:** Redirect HTTP to HTTPS
- **Allowed Methods:** GET, HEAD, OPTIONS
- **Cached Methods:** GET, HEAD
- **Query String Forwarding:** All query strings forwarded (for SPA routing)
- **Price Class:** PriceClass_100 (North America and Europe)
- **SSL Certificate:** CloudFront default certificate

### Environment-Specific Configuration

The S3 stack uses environment context:
- **Dev:** `spendsense-frontend-dev`, `spendsense-assets-dev`
- **Staging:** `spendsense-frontend-staging`, `spendsense-assets-staging`
- **Prod:** `spendsense-frontend-prod`, `spendsense-assets-prod`

Set environment when deploying:
```bash
cdk deploy SpendSense-S3-dev --context environment=dev
cdk deploy SpendSense-S3-staging --context environment=staging
cdk deploy SpendSense-S3-prod --context environment=prod
```

## Testing Connection

### Database Connection - From Local Environment

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

Test database connection using:
```bash
cd infrastructure/scripts
python3 test_connection.py
```

### Cognito Authentication Testing

Test Cognito authentication using AWS CLI:
```bash
# Get client ID
CLIENT_ID=$(aws secretsmanager get-secret-value \
  --secret-id spendsense/cognito/configuration \
  --query SecretString \
  --output text | jq -r '.client_id')

# Get user pool ID
USER_POOL_ID=$(aws secretsmanager get-secret-value \
  --secret-id spendsense/cognito/configuration \
  --query SecretString \
  --output text | jq -r '.user_pool_id')

# Authenticate demo user (⚠️ uses demo password - for testing only)
aws cognito-idp initiate-auth \
  --auth-flow USER_PASSWORD_AUTH \
  --client-id $CLIENT_ID \
  --auth-parameters USERNAME=hannah@demo.com,PASSWORD=Demo123!
```

Or use the demo users created by the `create_demo_users.py` script.

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
│       ├── database_stack.py     # RDS PostgreSQL stack
│       └── cognito_stack.py      # Cognito User Pool stack
└── scripts/                      # Helper scripts
    ├── update_connection_string.py  # Update database connection secret
    ├── update_cognito_config.py     # Update Cognito configuration secret
    ├── create_demo_users.py         # Create demo users in Cognito
    └── test_connection.py           # Test database connection
```

## Cost Considerations

**Database Stack:**
- **db.t3.micro**: ~$15/month (eligible for free tier in first year)
- **Storage**: $0.115/GB/month for gp2
- **Backups**: Included in storage cost (7-day retention)
- **Secrets Manager**: $0.40/month per secret
- **KMS**: $1/month per key + $0.03 per 10,000 requests

**Cognito Stack:**
- **Cognito User Pool**: Free tier includes 50,000 MAUs (Monthly Active Users)
- **Beyond free tier**: $0.0055 per MAU
- **Secrets Manager**: $0.40/month per secret

## Lambda Functions and API Gateway

### API Gateway Endpoint

After deploying the Lambda stack, retrieve the API Gateway endpoint URL:

```bash
aws cloudformation describe-stacks \
  --stack-name SpendSense-Lambda-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text
```

The API is available at: `{ApiGatewayUrl}/api/v1/*`

**Example endpoints:**
- Health check: `GET {ApiGatewayUrl}/api/v1/health`
- API routes: `GET|POST|PUT|DELETE {ApiGatewayUrl}/api/v1/{resource}`

### Lambda Functions

**API Lambda Function:**
- **Purpose**: FastAPI application using Mangum adapter
- **Runtime**: Python 3.11
- **Timeout**: 30 seconds
- **Memory**: 512 MB
- **Handler**: `app.handler.handler`
- **VPC**: Yes (for RDS access)
- **Environment Variables**:
  - `DATABASE_SECRET_ARN`: ARN of database connection string secret
  - `DATABASE_SECRET_NAME`: Name of database secret (`spendsense/database/connection`)
  - `COGNITO_SECRET_ARN`: ARN of Cognito configuration secret
  - `COGNITO_SECRET_NAME`: Name of Cognito secret (`spendsense/cognito/configuration`)
  - `ENVIRONMENT`: Environment name (dev/staging/prod)
  - `AWS_REGION`: AWS region

**Background Job Lambda Functions:**

1. **Compute Features** (`compute-features`)
   - Runtime: Python 3.11
   - Timeout: 5 minutes
   - Memory: 1024 MB
   - Handler: `lambdas.compute_features.handler`
   - Triggered by: EventBridge (to be configured in Story 1.8)

2. **Assign Persona** (`assign-persona`)
   - Runtime: Python 3.11
   - Timeout: 5 minutes
   - Memory: 512 MB
   - Handler: `lambdas.assign_persona.handler`
   - Triggered by: EventBridge (scheduled and event-based)

3. **Generate Recommendations** (`generate-recommendations`)
   - Runtime: Python 3.11
   - Timeout: 5 minutes
   - Memory: 512 MB
   - Handler: `lambdas.generate_recommendations.handler`
   - Triggered by: EventBridge (scheduled and event-based)

### IAM Permissions

**API Lambda Role:**
- VPC access (for RDS connection)
- Secrets Manager read access (database and Cognito secrets)
- CloudWatch Logs write access

**Background Job Lambda Role:**
- VPC access (for RDS connection)
- Secrets Manager read access (database and Cognito secrets)
- CloudWatch Logs write access
- EventBridge PutEvents permission (for emitting custom events)

### API Gateway Configuration

**CORS:**
- **Dev environment**: All origins allowed (`*`)
- **Production**: Configure specific frontend domain

**Routes:**
- `/api/v1/health` - Public health check endpoint
- `/api/v1/*` - Proxy resource routing to API Lambda

**Authorization:**
- Cognito authorizer is configured but not applied to routes by default
- To enable authentication for protected routes, uncomment the `default_method_options` in `lambda_stack.py`
- Health endpoint is always public (no authentication required)

### Testing Lambda Functions

**Test API Gateway Endpoint:**
```bash
# Get API Gateway URL
API_URL=$(aws cloudformation describe-stacks \
  --stack-name SpendSense-Lambda-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiGatewayUrl`].OutputValue' \
  --output text)

# Test health endpoint
curl $API_URL/api/v1/health
```

**Test Lambda Functions Directly:**
```bash
# Get Lambda function name
LAMBDA_NAME=$(aws cloudformation describe-stack-resources \
  --stack-name SpendSense-Lambda-dev \
  --query 'StackResources[?ResourceType==`AWS::Lambda::Function` && LogicalResourceId==`ApiLambda`].PhysicalResourceId' \
  --output text)

# Invoke Lambda function
aws lambda invoke \
  --function-name $LAMBDA_NAME \
  --payload '{"httpMethod":"GET","path":"/health"}' \
  response.json

# View response
cat response.json
```

### Lambda Packaging

Lambda functions are automatically bundled by CDK using `Code.from_asset()`. The entire `spendsense-backend` directory is packaged, including:
- All Python code
- Dependencies from `requirements.txt` (installed during deployment)
- Lambda handlers in `app/` and `lambdas/` directories

**Note:** For production, consider using Lambda layers for shared dependencies to reduce package size and improve cold start times.

## EventBridge Rules for Background Jobs

EventBridge rules are configured to automatically trigger background job Lambda functions. The rules support both scheduled triggers (daily refresh) and event-based triggers (user signup, job completion).

### EventBridge Rules

**1. Compute Features Lambda Rules:**

- **Scheduled Rule:** Daily at 1:00 AM UTC
  - Rule name: `spendsense-compute-features-scheduled-{env}`
  - Triggers: `compute-features` Lambda function
  - Event payload: `{event_type: "scheduled", user_id: null}`

- **Event Pattern Rule:** User signup event
  - Rule name: `spendsense-compute-features-event-{env}`
  - Event pattern: `source: "spendsense", detail-type: "User Signup", detail.event_type: "user.signup"`
  - Triggers: `compute-features` Lambda function
  - Event payload: `{event_type: "user.signup", user_id: "...", timestamp: "..."}`

**2. Assign Persona Lambda Rules:**

- **Scheduled Rule:** Daily at 1:05 AM UTC (5 minutes after compute-features)
  - Rule name: `spendsense-assign-persona-scheduled-{env}`
  - Triggers: `assign-persona` Lambda function
  - Event payload: `{event_type: "scheduled", user_id: null}`

- **Event Pattern Rule:** Features computed event
  - Rule name: `spendsense-assign-persona-event-{env}`
  - Event pattern: `source: "spendsense", detail-type: "Features Computed", detail.event_type: "features.computed"`
  - Triggers: `assign-persona` Lambda function
  - Event payload: `{event_type: "features.computed", user_id: "...", timestamp: "..."}`

**3. Generate Recommendations Lambda Rules:**

- **Scheduled Rule:** Daily at 1:10 AM UTC (10 minutes after compute-features)
  - Rule name: `spendsense-generate-recommendations-scheduled-{env}`
  - Triggers: `generate-recommendations` Lambda function
  - Event payload: `{event_type: "scheduled", user_id: null}`

- **Event Pattern Rule:** Persona assigned event
  - Rule name: `spendsense-generate-recommendations-event-{env}`
  - Event pattern: `source: "spendsense", detail-type: "Persona Assigned", detail.event_type: "persona.assigned"`
  - Triggers: `generate-recommendations` Lambda function
  - Event payload: `{event_type: "persona.assigned", user_id: "...", timestamp: "..."}`

### Event Flow

**Scheduled Flow (Daily Refresh):**
1. 1:00 AM UTC: `compute-features` Lambda runs for all users
2. 1:05 AM UTC: `assign-persona` Lambda runs for all users
3. 1:10 AM UTC: `generate-recommendations` Lambda runs for all users

**Event-Based Flow (User Signup):**
1. User signs up → `user.signup` event published to EventBridge
2. EventBridge triggers `compute-features` Lambda
3. `compute-features` completes → emits `features.computed` event
4. EventBridge triggers `assign-persona` Lambda
5. `assign-persona` completes → emits `persona.assigned` event
6. EventBridge triggers `generate-recommendations` Lambda

### Event Structure

**EventBridge Event Format:**
```json
{
  "version": "0",
  "id": "...",
  "detail-type": "User Signup" | "Features Computed" | "Persona Assigned",
  "source": "spendsense",
  "account": "...",
  "time": "2025-01-XXT...",
  "region": "us-east-1",
  "detail": {
    "event_type": "user.signup" | "features.computed" | "persona.assigned" | "scheduled",
    "user_id": "..." | null,
    "timestamp": "2025-01-XXT...Z"
  }
}
```

**Lambda Handler Receives:**
The Lambda handler receives the full EventBridge event structure. Extract data from:
- `event.get("detail", {}).get("user_id")` - User ID
- `event.get("detail", {}).get("event_type")` - Event type
- `event.get("detail", {}).get("timestamp")` - Event timestamp

### Emitting Custom Events

Lambda handlers emit custom events to EventBridge when jobs complete:

**From `compute-features` Lambda:**
```python
emit_event("features.computed", user_id)
```

**From `assign-persona` Lambda:**
```python
emit_event("persona.assigned", user_id)
```

**Event Format:**
- Source: `spendsense`
- DetailType: `"Features Computed"` or `"Persona Assigned"`
- Detail: JSON with `event_type`, `user_id`, `timestamp`

### Testing EventBridge Rules

**Option A: Using Test Script (Recommended)**

```bash
cd infrastructure/scripts
python3 test_eventbridge.py
```

The script will:
- Publish test events to EventBridge
- Verify events are received by Lambda functions
- Check CloudWatch Logs for Lambda execution

**Option B: Manual Event Publishing**

1. **Publish user signup event:**
   ```bash
   aws events put-events \
     --entries '[{
       "Source": "spendsense",
       "DetailType": "User Signup",
       "Detail": "{\"event_type\": \"user.signup\", \"user_id\": \"test-user-123\", \"timestamp\": \"2025-01-XXT...Z\"}"
     }]'
   ```

2. **Check Lambda execution:**
   ```bash
   # View CloudWatch Logs for compute-features Lambda
   aws logs tail /aws/lambda/compute-features --follow
   ```

3. **Verify event chain:**
   - Check `compute-features` Lambda logs
   - Check `assign-persona` Lambda logs (should trigger automatically)
   - Check `generate-recommendations` Lambda logs (should trigger automatically)

**Option C: Test Scheduled Rules**

Scheduled rules run automatically at their configured times. To test without waiting:

1. **Manually invoke Lambda function:**
   ```bash
   aws lambda invoke \
     --function-name compute-features \
     --payload '{"event_type": "scheduled", "user_id": null, "timestamp": "2025-01-XXT...Z"}' \
     response.json
   ```

2. **Check execution result:**
   ```bash
   cat response.json
   ```

### Retrieving EventBridge Rule ARNs

Get EventBridge rule ARNs from stack outputs:

```bash
# Get all EventBridge rule ARNs
aws cloudformation describe-stacks \
  --stack-name SpendSense-Lambda-dev \
  --query 'Stacks[0].Outputs[?contains(OutputKey, `RuleArn`)].{Key:OutputKey,Value:OutputValue}' \
  --output table
```

Or get specific rule ARN:

```bash
# Compute Features Scheduled Rule
aws cloudformation describe-stacks \
  --stack-name SpendSense-Lambda-dev \
  --query 'Stacks[0].Outputs[?OutputKey==`ComputeFeaturesScheduledRuleArn`].OutputValue' \
  --output text
```

### EventBridge Permissions

EventBridge automatically gets permission to invoke Lambda functions when using `LambdaFunction` target in CDK. No manual permission configuration needed.

Lambda functions need `events:PutEvents` permission to emit custom events (already configured in background job Lambda role).

## Next Steps

After deploying the infrastructure stacks:
1. Update connection string secret (see Post-Deployment Steps)
2. Update Cognito configuration secret (see Post-Deployment Steps)
3. Create demo users (see Post-Deployment Steps)
4. Test connections from local environment
5. Deploy Lambda stack (see Deployment section)
6. Test API Gateway endpoint (see Lambda Functions and API Gateway section)
7. Proceed to Story 1.4: Create Database Schema (if not done)
8. Proceed to Story 1.8: Set Up EventBridge Rules for Background Jobs
9. Proceed to Story 2.2: Integrate AWS Cognito Authentication

