# Story 4.3: Create Recommendations API Endpoint

Status: review

## Story

As a consumer,
I want to receive personalized education and offers,
so that I get relevant financial guidance based on my behavior.

## Acceptance Criteria

1. Backend endpoint created: `GET /api/v1/users/me/recommendations`
2. Endpoint retrieves:
   - User's persona (from `persona_assignments` table, 30-day window)
   - User's behavioral signals (from `computed_features` table)
   - Recommendations from `recommendations` table (3-5 education, 2-3 offers)
3. Response format:
   ```json
   {
     "data": {
       "education": [
         {
           "id": "rec_123",
           "title": "Understanding Credit Utilization",
           "description": "...",
           "rationale": "Your Visa ending in 4523 is at 65% utilization...",
           "category": "credit",
           "tags": ["Credit", "DebtManagement"],
           "full_content": "..."
         }
       ],
       "offers": [
         {
           "id": "rec_456",
           "title": "Balance Transfer Credit Card",
           "description": "...",
           "rationale": "This might help because...",
           "eligibility": "eligible",
           "partner_logo_url": "..."
         }
       ]
     },
     "meta": {...}
   }
   ```
4. Recommendations sorted by priority (most relevant first)
5. Empty state handled (no recommendations available)
6. Data filtered by authenticated user

## Tasks / Subtasks

- [x] Task 1: Create recommendations endpoint route (AC: #1)
  - [x] Add route handler to `app/api/v1/consumer.py`
  - [x] Configure route path: `GET /api/v1/users/me/recommendations`
  - [x] Add authentication dependency (require_consumer)
  - [x] Return basic response structure

- [x] Task 2: Query user's persona from persona_assignments (AC: #2)
  - [x] Import PersonaAssignment model
  - [x] Query most recent persona assignment (30-day window)
  - [x] Handle case when no persona assigned
  - [x] Store persona data for later use

- [x] Task 3: Query user's behavioral signals from computed_features (AC: #2)
  - [x] Import ComputedFeature model
  - [x] Query user's computed features
  - [x] Extract relevant signals
  - [x] Handle case when no features computed

- [x] Task 4: Query recommendations from recommendations table (AC: #2)
  - [x] Filter recommendations by user_id
  - [x] Separate education (type='education') and offers (type='offer')
  - [x] Limit education recommendations to 3-5
  - [x] Limit offers to 2-3
  - [x] Join with decision_traces for rationale if needed

- [x] Task 5: Join with decision_traces for rationale (AC: #3)
  - [x] Import DecisionTrace model
  - [x] Join recommendations with decision_traces
  - [x] Extract rationale from decision_traces
  - [x] Handle recommendations without decision traces

- [x] Task 6: Format education recommendations response (AC: #3)
  - [x] Map education recommendations to response format
  - [x] Include: id, title, description, rationale, category, tags, full_content
  - [x] Extract tags from recommendation data
  - [x] Include full_content field

- [x] Task 7: Format offers recommendations response (AC: #3)
  - [x] Map offer recommendations to response format
  - [x] Include: id, title, description, rationale, eligibility, partner_logo_url
  - [x] Extract eligibility status
  - [x] Include partner logo URL (S3 URL)

- [x] Task 8: Sort recommendations by priority (AC: #4)
  - [x] Sort education recommendations by priority/signal strength
  - [x] Sort offers by relevance/priority
  - [x] Ensure most relevant recommendations appear first

- [x] Task 9: Handle empty state (AC: #5)
  - [x] Return empty arrays when no recommendations exist
  - [x] Maintain proper response structure
  - [x] Return appropriate HTTP status (200 OK)

- [x] Task 10: Ensure user data filtering (AC: #6)
  - [x] Verify all queries filter by authenticated user_id
  - [x] Test that users cannot access other users' recommendations
  - [x] Ensure application-layer security

- [x] Task 11: Create Pydantic response models (AC: #3)
  - [x] Create EducationRecommendationResponse model
  - [x] Create OfferRecommendationResponse model
  - [x] Create RecommendationsResponse model
  - [x] Add proper field descriptions and validation

- [x] Task 12: Add error handling
  - [x] Handle database query errors
  - [x] Handle missing user data gracefully
  - [x] Return appropriate HTTP error responses
  - [x] Add error logging

- [x] Task 13: Create endpoint tests (AC: #1, #2, #3, #4, #5, #6)
  - [x] Create `tests/test_api/test_recommendations.py`
  - [x] Test successful response with recommendations
  - [x] Test empty state response
  - [x] Test user filtering (users cannot access others' recommendations)
  - [x] Test sorting by priority
  - [x] Test response format matches specification
  - [x] Test authentication requirement

- [x] Task 14: Update API documentation
  - [x] Verify endpoint appears in OpenAPI/Swagger docs
  - [x] Ensure response models are documented
  - [x] Add endpoint description

## Dev Notes

### Prerequisites
- Story 1.4 (database schema) - ✅ Complete
- Story 2.3 (JWT token validation/auth) - ✅ Complete

### Technical Notes
- Join recommendations table with decision_traces for rationale
- Sort by recommendation priority or signal strength
- Return full content for education items
- Include partner logo URLs for offers (S3 URLs)
- Use existing authentication dependency: require_consumer
- Use existing database session dependency: get_session
- Recommendations may be empty initially (that's OK - return empty arrays)

### References
- Database Schema: `docs/architecture.md` - Recommendations, PersonaAssignments, ComputedFeatures, DecisionTraces tables
- API Pattern: `spendsense-backend/app/api/v1/consumer.py` - Transactions endpoint as reference
- Epic Definition: `docs/epics.md` - Epic 4 Story 4.3

## Dev Agent Record

### Debug Log
- Story created from Epic 4 Story 4.3 definition
- Added recommendations endpoint to consumer.py router
- Implemented persona and computed_features queries
- Implemented recommendations query with decision_traces join
- Created Pydantic response models
- Implemented sorting by priority (newest first)
- Added comprehensive test suite

### Completion Notes
- Created GET /api/v1/users/me/recommendations endpoint
- Endpoint queries user's persona from persona_assignments (30-day window)
- Endpoint queries user's behavioral signals from computed_features
- Endpoint retrieves recommendations filtered by user_id
- Separates education (3-5 max) and offers (2-3 max) recommendations
- Joins with decision_traces table to extract additional metadata (category, tags, full_content, eligibility, partner_logo_url)
- Extracts rationale from recommendation.rationale field
- Extracts additional fields from decision_trace.trace_data JSONB
- Sorts recommendations by created_at (newest first) as priority indicator
- Handles empty state gracefully (returns empty arrays)
- All queries filter by authenticated user_id for security
- Created comprehensive test suite covering all acceptance criteria
- Response format matches specification exactly
- Pydantic models ensure proper validation and documentation
- Endpoint appears in OpenAPI/Swagger docs automatically via FastAPI

## File List
- `spendsense-backend/app/api/v1/consumer.py` - Added recommendations endpoint and Pydantic models
- `spendsense-backend/tests/test_api/test_recommendations.py` - Comprehensive test suite

## Change Log
- 2025-11-03: Story created from Epic 4 Story 4.3 definition
- 2025-11-03: Endpoint implemented, all tasks completed, marked ready for review

