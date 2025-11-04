# Story 3.2: Create Transactions API Endpoint

Status: review

## Story

As a consumer,
I want to view my transaction history,
so that I can understand my spending patterns.

## Acceptance Criteria

1. Backend endpoint created: `GET /api/v1/users/me/transactions`
2. Query parameters supported:
   - `start_date` (ISO 8601, optional)
   - `end_date` (ISO 8601, optional)
   - `category` (optional filter)
   - `merchant` (optional search)
   - `page` (default: 1)
   - `limit` (default: 50, max: 100)
3. Response format:
   ```json
   {
     "data": {
       "transactions": [...],
       "pagination": {
         "page": 1,
         "limit": 50,
         "total": 200,
         "total_pages": 4
       }
     },
     "meta": {
       "timestamp": "2025-11-03T10:30:00Z"
     }
   }
   ```
4. Transactions filtered by authenticated user (application-layer security)
5. Default sort: date descending (newest first)
6. Pagination works correctly
7. Empty result handled (empty array)
8. Error handling for invalid dates or parameters

## Tasks / Subtasks

- [x] Task 1: Create Pydantic models for query parameters and response (AC: #2, #3)
  - [x] Create `TransactionQueryParams` model for query parameters
  - [x] Add validation for date formats (ISO 8601)
  - [x] Add validation for pagination (page >= 1, limit 1-100)
  - [x] Create `TransactionResponse` model matching response format
  - [x] Create `PaginationInfo` model for pagination metadata
  - [x] Add transaction serialization model

- [x] Task 2: Implement transaction query logic (AC: #1, #4, #5, #6, #7)
  - [x] Create function to query transactions filtered by user_id
  - [x] Apply date filters (start_date, end_date) if provided
  - [x] Apply category filter if provided
  - [x] Apply merchant search (case-insensitive partial match) if provided
  - [x] Apply default sort: date descending (newest first)
  - [x] Implement pagination with LIMIT/OFFSET
  - [x] Return empty array if no transactions found
  - [x] Get total count for pagination metadata

- [x] Task 3: Create FastAPI endpoint (AC: #1, #2, #3, #8)
  - [x] Add GET endpoint `/api/v1/users/me/transactions` to consumer router
  - [x] Use `require_consumer` dependency for authentication
  - [x] Accept query parameters via Pydantic model
  - [x] Validate ISO 8601 date formats
  - [x] Handle invalid date format errors
  - [x] Handle invalid pagination parameter errors
  - [x] Return properly formatted response with data and meta sections
  - [x] Include timestamp in meta section

- [x] Task 4: Add unit tests for transaction query logic (AC: #1, #4, #5, #6, #7)
  - [x] Test query with no filters (returns all user transactions)
  - [x] Test date filtering (start_date only)
  - [x] Test date filtering (end_date only)
  - [x] Test date filtering (both start_date and end_date)
  - [x] Test category filtering
  - [x] Test merchant search (case-insensitive partial match)
  - [x] Test pagination (page and limit)
  - [x] Test empty result handling
  - [x] Test default sort (date descending)
  - [x] Test that transactions are filtered by user_id (security)

- [x] Task 5: Add integration tests for endpoint (AC: #1, #2, #3, #8)
  - [x] Test endpoint with valid authentication
  - [x] Test endpoint without authentication (401)
  - [x] Test with valid query parameters
  - [x] Test with invalid date format (400)
  - [x] Test with invalid pagination (negative page, limit > 100)
  - [x] Test response format matches specification
  - [x] Test pagination metadata is correct
  - [x] Test empty result response format

- [x] Task 6: Update main.py to include transactions endpoint (AC: #1)
  - [x] Verify consumer router is included in main app
  - [x] Ensure endpoint is accessible at `/api/v1/users/me/transactions`

## Dev Notes

### Prerequisites

- Stories 1.4, 2.3, 3.1 must be complete (database, auth, and seed data exist)
- Transaction model exists in `app/models/transaction.py`
- Consumer router exists in `app/api/v1/consumer.py`
- Authentication dependencies exist in `app/dependencies.py`

### Technical Notes

- Use FastAPI query parameters with Pydantic models
- Use SQLAlchemy for database queries with parameterized queries
- Apply user_id filter from JWT token (from `require_consumer` dependency)
- Implement efficient pagination with LIMIT/OFFSET
- Use SQLAlchemy's `desc()` for date descending sort
- Merchant search should use SQLAlchemy's `ilike()` for case-insensitive partial match
- Date validation should use Python's `datetime.date.fromisoformat()` or Pydantic's date validation

### Architecture Patterns

- **Database Access**: Use SQLAlchemy models and session management from `app.database`
- **Authentication**: Use `require_consumer` dependency from `app.dependencies`
- **Query Parameters**: Use Pydantic models for validation
- **Response Format**: Follow standard API response format with `data` and `meta` sections
- **Security**: Application-layer security - filter by user_id from JWT token

### Project Structure

The transactions endpoint should be added to:
```
spendsense-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── consumer.py          # Add transactions endpoint here
│   ├── models/
│   │   └── transaction.py          # Transaction model (already exists)
│   ├── schemas/
│   │   └── transaction.py          # Create Pydantic models here (if needed)
│   └── database/
│       └── session.py               # Database session management
├── tests/
│   └── test_transactions.py        # Create test file
└── ...
```

### Response Format Details

Transaction objects should include:
- `id`: UUID
- `user_id`: UUID (from authenticated user)
- `account_id`: UUID
- `date`: ISO 8601 date string
- `merchant`: string
- `amount`: decimal number (negative for debits, positive for credits)
- `category`: string (nullable)

## Dev Agent Record

### Context Reference

- `docs/stories/3-2-create-transactions-api-endpoint.context.xml` (to be created)

### Agent Model Used

AI Assistant (Claude Sonnet 4.5)

### Debug Log References

- Created Pydantic models for query parameters and response format
- Implemented transaction query logic with filters (date, category, merchant) and pagination
- Created FastAPI endpoint with proper authentication and error handling
- Added comprehensive unit and integration tests

### Completion Notes List

- **Endpoint Implementation**: Created `GET /api/v1/users/me/transactions` endpoint in `app/api/v1/consumer.py` that:
  - Supports query parameters: start_date, end_date, category, merchant, page, limit
  - Filters transactions by authenticated user (application-layer security)
  - Implements pagination with LIMIT/OFFSET
  - Returns transactions sorted by date descending (newest first)
  - Returns properly formatted response with data and meta sections
  
- **Query Logic**: Implemented `get_user_transactions()` function that:
  - Filters by user_id from JWT token
  - Applies optional date filters (start_date, end_date)
  - Applies optional category filter
  - Applies optional merchant search (case-insensitive partial match using SQLAlchemy's `ilike()`)
  - Implements efficient pagination
  - Returns empty array when no transactions found
  
- **Pydantic Models**: Created models for:
  - `TransactionQueryParams` - Query parameter validation
  - `TransactionResponse` - Transaction serialization
  - `PaginationInfo` - Pagination metadata
  - `TransactionsResponse` - Response structure
  
- **Tests**: Created comprehensive test suite (`tests/test_transactions.py`) covering:
  - Unit tests for query logic with various filters
  - Integration tests for endpoint with authentication
  - Tests for pagination, empty results, error handling
  - Tests for response format validation

### File List

**Created Files:**
- `spendsense-backend/tests/test_transactions.py` - Test suite for transactions endpoint

**Modified Files:**
- `spendsense-backend/app/api/v1/consumer.py` - Added transactions endpoint and query logic
- `docs/stories/3-2-create-transactions-api-endpoint.md` - Story file with implementation details

## Change Log

- 2025-11-03: Story created and marked ready-for-dev
- 2025-11-03: Implementation completed - all tasks done
  - Created transactions API endpoint with filters and pagination
  - Implemented query logic with user filtering
  - Added comprehensive test suite
  - Story marked ready for review

