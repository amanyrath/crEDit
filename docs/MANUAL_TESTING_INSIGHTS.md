# Manual Testing Guide: Insights API Endpoint

This guide provides instructions for manually testing the `/api/v1/users/me/insights` endpoint.

## Prerequisites

1. **Backend server running**: 
   ```bash
   cd spendsense-backend
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   uvicorn app.main:app --reload
   ```
   Server should be available at `http://localhost:8000`

2. **Database seeded**: Run the seeding script to create demo data:
   ```bash
   python scripts/seed_demo_data.py
   ```

3. **Authentication token**: You'll need a valid JWT token from Cognito for testing. 
   For testing purposes, you can use the test script approach below.

## Testing Approaches

### Option 1: Using FastAPI's Interactive Documentation (Swagger UI)

1. Start the server: `uvicorn app.main:app --reload`
2. Open browser: `http://localhost:8000/docs`
3. Find the `/api/v1/users/me/insights` endpoint
4. Click "Try it out"
5. Enter period parameter: `30d` or `90d`
6. Click "Authorize" and enter your Bearer token
7. Click "Execute"
8. Review the response

### Option 2: Using curl (Requires Authentication Token)

Replace `YOUR_JWT_TOKEN` with an actual token from Cognito.

#### Test 1: Default Period (30d)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me/insights" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" | jq .
```

#### Test 2: 90 Day Period
```bash
curl -X GET "http://localhost:8000/api/v1/users/me/insights?period=90d" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" | jq .
```

#### Test 3: Invalid Period (Should return 400)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me/insights?period=invalid" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" | jq .
```

#### Test 4: Without Authentication (Should return 401)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me/insights" \
  -H "Content-Type: application/json" | jq .
```

### Option 3: Using Python Test Script

Run the test script with the virtual environment activated:

```bash
cd spendsense-backend
source venv/bin/activate
python test_insights_manual.py
```

## Expected Response Format

### Successful Response (200 OK)
```json
{
  "data": {
    "summary": {
      "total_spending": 1234.56,
      "average_daily_spend": 41.15,
      "top_category": "Food & Drink",
      "savings_rate": null
    },
    "charts": {
      "spending_by_category": [
        {
          "category": "Food & Drink",
          "amount": 450.00
        },
        {
          "category": "Shopping",
          "amount": 320.50
        }
      ],
      "credit_utilization": [
        {
          "date": "2025-11-03",
          "utilization": 68.0,
          "balance": 3400.00,
          "limit": 5000.00
        }
      ],
      "subscriptions": {
        "total_monthly": 203.00,
        "subscriptions": [
          {
            "merchant": "Netflix",
            "amount": 15.99
          },
          {
            "merchant": "Spotify",
            "amount": 10.00
          }
        ]
      }
    }
  },
  "meta": {
    "timestamp": "2025-11-03T10:30:00Z",
    "period": "30d",
    "start_date": "2025-10-04",
    "end_date": "2025-11-03"
  }
}
```

### Error Response: Invalid Period (400 Bad Request)
```json
{
  "detail": "Period must be '30d' or '90d'"
}
```

### Error Response: Unauthorized (401)
```json
{
  "detail": "Not authenticated"
}
```

## Test Cases to Verify

### ✅ Test Case 1: Default Period
- **Request**: `GET /api/v1/users/me/insights`
- **Expected**: Status 200, period in meta should be "30d"
- **Verify**: 
  - Summary contains total_spending, average_daily_spend, top_category
  - Charts contain spending_by_category array
  - Charts contain credit_utilization array (empty if no credit accounts)
  - Charts contain subscriptions object

### ✅ Test Case 2: 90 Day Period
- **Request**: `GET /api/v1/users/me/insights?period=90d`
- **Expected**: Status 200, period in meta should be "90d"
- **Verify**: 
  - start_date and end_date span 90 days
  - Data aggregated over 90 days instead of 30

### ✅ Test Case 3: Invalid Period
- **Request**: `GET /api/v1/users/me/insights?period=invalid`
- **Expected**: Status 400
- **Verify**: Error message indicates period must be '30d' or '90d'

### ✅ Test Case 4: Missing Authentication
- **Request**: `GET /api/v1/users/me/insights` (no Authorization header)
- **Expected**: Status 401
- **Verify**: Error indicates authentication required

### ✅ Test Case 5: Empty Data
- **Request**: `GET /api/v1/users/me/insights` (user with no transactions)
- **Expected**: Status 200
- **Verify**: 
  - total_spending is 0.0
  - average_daily_spend is 0.0
  - top_category is null
  - spending_by_category is empty array
  - credit_utilization is empty array (if no credit accounts)
  - subscriptions.total_monthly is 0.0
  - subscriptions.subscriptions is empty array

### ✅ Test Case 6: User with Credit Accounts
- **Request**: `GET /api/v1/users/me/insights` (user with credit card accounts)
- **Expected**: Status 200
- **Verify**: 
  - credit_utilization array contains data points
  - Each data point has date, utilization, balance, limit
  - Utilization is calculated as (balance / limit) * 100

### ✅ Test Case 7: Subscription Detection
- **Request**: `GET /api/v1/users/me/insights` (user with recurring transactions)
- **Expected**: Status 200
- **Verify**: 
  - subscriptions.subscriptions array contains detected subscriptions
  - Each subscription has merchant name and amount
  - total_monthly is sum of all subscription amounts

## Performance Testing

### Response Time
- **Target**: < 500ms for typical user data
- **Test**: Measure response time with `time curl ...`

### Database Query Efficiency
- **Verify**: Check database logs to ensure queries use indexes
- **Expected**: Single query per aggregation (not N+1 queries)

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution**: Activate virtual environment and install dependencies:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "401 Unauthorized"
**Solution**: Ensure you have a valid JWT token from Cognito. Token should be in format:
```
Authorization: Bearer eyJraWQiOiJ...
```

### Issue: "500 Internal Server Error"
**Solution**: 
- Check server logs for detailed error
- Verify database connection is working
- Verify database has been seeded with demo data
- Check that user_id exists in database

### Issue: Empty Data in Response
**Solution**: 
- Verify demo data seeding script ran successfully
- Check that transactions exist for the authenticated user
- Verify date range is correct (transactions should be within last 30/90 days)

## Quick Validation Checklist

- [ ] Endpoint responds with 200 OK for valid requests
- [ ] Period parameter validation works (30d, 90d accepted, others rejected)
- [ ] Authentication required (401 without token)
- [ ] Response structure matches specification
- [ ] Summary cards contain expected fields
- [ ] Charts contain expected data structures
- [ ] Empty states handled gracefully
- [ ] Credit utilization calculated correctly (if credit accounts exist)
- [ ] Subscriptions detected correctly (if recurring transactions exist)
- [ ] Meta information includes timestamp, period, date range

