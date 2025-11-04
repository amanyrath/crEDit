# Story 1.8: Set Up EventBridge Rules for Background Jobs

Status: ready-for-dev

## Story

As a developer,
I want to create EventBridge rules to trigger background job Lambda functions,
so that feature computation, persona assignment, and recommendation generation run automatically.

## Acceptance Criteria

1. EventBridge rule created for `compute-features` Lambda:
   - Trigger: New user signup event OR daily schedule (1 AM UTC)
   - Target: `compute-features` Lambda function
2. EventBridge rule created for `assign-persona` Lambda:
   - Trigger: After `compute-features` completes (or daily schedule)
   - Target: `assign-persona` Lambda function
3. EventBridge rule created for `generate-recommendations` Lambda:
   - Trigger: After `assign-persona` completes (or daily schedule)
   - Target: `generate-recommendations` Lambda function
4. EventBridge event bus configured (default or custom)
5. Lambda function permissions configured for EventBridge invocation
6. Test events can trigger Lambda functions successfully

## Tasks / Subtasks

- [x] Task 1: Create EventBridge rules in Lambda stack (AC: #1, #2, #3, #4, #5)
  - [x] Import Lambda function references from Lambda stack
  - [x] Create EventBridge rule for `compute-features`:
    - Scheduled rule: Daily at 1 AM UTC (cron: `cron(0 1 * * ? *)`)
    - Event pattern rule: Custom event for user signup (event pattern matching `user.signup`)
    - Target: `compute-features` Lambda function
    - Event payload format: `{event_type: "user.signup" | "scheduled", user_id: "...", timestamp: "..."}`
  - [x] Create EventBridge rule for `assign-persona`:
    - Scheduled rule: Daily at 1:05 AM UTC (5 minutes after compute-features)
    - Event pattern rule: Custom event after compute-features completes (event pattern matching `features.computed`)
    - Target: `assign-persona` Lambda function
    - Event payload format: `{event_type: "features.computed" | "scheduled", user_id: "...", timestamp: "..."}`
  - [x] Create EventBridge rule for `generate-recommendations`:
    - Scheduled rule: Daily at 1:10 AM UTC (10 minutes after compute-features)
    - Event pattern rule: Custom event after assign-persona completes (event pattern matching `persona.assigned`)
    - Target: `generate-recommendations` Lambda function
    - Event payload format: `{event_type: "persona.assigned" | "scheduled", user_id: "...", timestamp: "..."}`
  - [x] Configure EventBridge event bus (use default bus for MVP)
  - [x] Grant EventBridge permission to invoke Lambda functions (automatic via CDK LambdaFunction target)
  - [x] Add EventBridge rule ARNs as stack outputs

- [x] Task 2: Update Lambda handlers to emit custom events (AC: #1, #2, #3)
  - [x] Update `compute-features` Lambda handler to emit `features.computed` event when complete
  - [x] Update `assign-persona` Lambda handler to emit `persona.assigned` event when complete
  - [x] Use EventBridge SDK (boto3) to put custom events
  - [x] Event payload format consistent with EventBridge rules
  - [x] Handle errors gracefully (log errors but don't fail Lambda execution)
  - [x] Add EventBridge PutEvents permission to background job Lambda role

- [x] Task 3: Document EventBridge configuration (AC: #4, #5, #6)
  - [x] Update `infrastructure/README.md` with EventBridge rules documentation
  - [x] Document event structure and payload format
  - [x] Document how to test EventBridge rules (manual event publishing)
  - [x] Document scheduled rule times and timezone
  - [x] Document event flow: user signup → compute-features → assign-persona → generate-recommendations
  - [x] Document how to manually trigger Lambda functions via EventBridge

- [x] Task 4: Create test script for EventBridge events (AC: #6)
  - [x] Create script to publish test events: `infrastructure/scripts/test_eventbridge.py`
  - [x] Script should:
    - Publish `user.signup` event with test user_id
    - Publish `features.computed` event with test user_id
    - Publish `persona.assigned` event with test user_id
    - Publish scheduled-style events (for testing daily schedule)
  - [x] Script should verify events are received by Lambda functions
  - [x] Document script usage in README

- [ ] Task 5: Verify all components (AC: #1, #2, #3, #4, #5, #6)
  - [ ] Deploy Lambda stack with EventBridge rules: `cdk deploy SpendSense-Lambda-dev`
  - [ ] Verify EventBridge rules are created (check AWS Console or CDK outputs)
  - [ ] Verify Lambda functions have EventBridge invoke permissions
  - [ ] Test scheduled rules (wait for scheduled time or use test script)
  - [ ] Test custom events using test script
  - [ ] Verify Lambda functions receive events and execute
  - [ ] Verify event payload format matches expected structure
  - [ ] Verify all acceptance criteria are met

## Dev Notes

### Architecture Patterns and Constraints

- **EventBridge**: Use default event bus for MVP [Source: docs/epics.md#Story-1.8]
- **Event Patterns**: Use custom event patterns for user signup and Lambda completion events [Source: docs/epics.md#Story-1.8]
- **Scheduled Rules**: Use cron expressions for daily schedule (1 AM UTC) [Source: docs/epics.md#Story-1.8]
- **Event Payload**: `{event_type: "...", user_id: "...", timestamp: "..."}` [Source: docs/epics.md#Story-1.8]
- **Lambda Integration**: EventBridge rules target Lambda functions directly [Source: infrastructure/cdk/stacks/lambda_stack.py]

### Project Structure Notes

The EventBridge rules should be added to the Lambda stack:
```
infrastructure/
├── cdk/
│   ├── app.py                      # CDK app entry point (Lambda stack already included)
│   ├── stacks/
│   │   └── lambda_stack.py         # Lambda functions, API Gateway, and EventBridge rules
│   └── requirements.txt            # Python dependencies
spendsense-backend/
└── lambdas/
    ├── compute_features.py         # Background job handler (emit events)
    ├── assign_persona.py           # Background job handler (emit events)
    └── generate_recommendations.py # Background job handler
infrastructure/
└── scripts/
    └── test_eventbridge.py         # Test script for EventBridge events
```

[Source: infrastructure/cdk/app.py, infrastructure/cdk/stacks/lambda_stack.py]

### Key Implementation Details

1. **EventBridge Rules**:
   - Scheduled rules: Use `aws_events.Rule` with `schedule` property
   - Event pattern rules: Use `aws_events.Rule` with `event_pattern` property
   - Default event bus: Use `aws_events.EventBus.from_event_bus_name` for default bus
   - Lambda targets: Use `aws_events_targets.LambdaFunction` for Lambda integration
   - Event payload: EventBridge will wrap custom events, Lambda receives full EventBridge event structure

2. **Lambda Permissions**:
   - EventBridge needs permission to invoke Lambda functions
   - CDK automatically adds permissions when using `LambdaFunction` target
   - Verify permissions are correct in IAM console

3. **Event Flow**:
   - User signup → `user.signup` event → `compute-features` Lambda
   - `compute-features` completes → `features.computed` event → `assign-persona` Lambda
   - `assign-persona` completes → `persona.assigned` event → `generate-recommendations` Lambda
   - Daily schedule → All three Lambdas run independently (for full refresh)

4. **Event Payload Structure**:
   - EventBridge wraps events, Lambda receives:
     ```json
     {
       "version": "0",
       "id": "...",
       "detail-type": "EventBridge custom event",
       "source": "spendsense",
       "account": "...",
       "time": "...",
       "region": "...",
       "detail": {
         "event_type": "user.signup" | "features.computed" | "persona.assigned" | "scheduled",
         "user_id": "...",
         "timestamp": "..."
       }
     }
     ```

5. **Scheduled Rules**:
   - Use cron expressions: `cron(0 1 * * ? *)` for 1 AM UTC daily
   - Stagger scheduled times: 1:00 AM, 1:05 AM, 1:10 AM to avoid conflicts
   - For scheduled events, `user_id` can be null or "all" (process all users)

6. **Lambda Event Emission**:
   - Use `boto3.client('events')` to put custom events
   - Event source: `spendsense` (custom source name)
   - Event detail-type: Descriptive name (e.g., "Features Computed")
   - Event detail: JSON with `event_type`, `user_id`, `timestamp`

### Learnings from Previous Stories

**From Story 1.6 (Status: review)**
- **Lambda Functions**: Three background job Lambda functions already created (compute-features, assign-persona, generate-recommendations)
- **Lambda Stack**: Lambda stack exists and exports Lambda function references
- **CDK Pattern**: Follow same CDK stack pattern as other stacks
- **Stack Naming**: Use format `SpendSense-Lambda-{env}` to match other stacks
- **Lambda Handlers**: Background job handlers are placeholders, need to emit events when complete

### References

- [Source: docs/epics.md#Story-1.8]
- [Source: infrastructure/cdk/stacks/lambda_stack.py]
- [Source: infrastructure/cdk/app.py]
- [Source: docs/architecture.md]
- [Source: infrastructure/README.md]

## Dev Agent Record

### Context Reference

- `docs/stories/1-8-set-up-eventbridge-rules-for-background-jobs.context.xml` (to be created)

### Agent Model Used

Claude Sonnet 4.5 (via Cursor)

### Debug Log References

<!-- Debug logs will be added during implementation -->

### Completion Notes List

- **EventBridge Rules**: Created all 6 EventBridge rules in Lambda stack:
  - 3 scheduled rules (daily at 1:00 AM, 1:05 AM, 1:10 AM UTC)
  - 3 event pattern rules (user.signup, features.computed, persona.assigned)
  - All rules use default event bus and target Lambda functions directly
  - EventBridge permissions to invoke Lambda functions are automatically granted by CDK
  
- **Lambda Handlers**: Updated all three background job Lambda handlers to emit custom events:
  - `compute-features` emits `features.computed` event when complete
  - `assign-persona` emits `persona.assigned` event when complete
  - Event emission uses boto3 EventBridge client with proper error handling
  - Events only emitted for user-specific processing (not scheduled batch jobs)
  
- **IAM Permissions**: Added EventBridge PutEvents permission to background job Lambda role:
  - Allows Lambda functions to emit custom events to EventBridge
  - Permission configured with wildcard resource (required by EventBridge PutEvents API)
  
- **Documentation**: Comprehensive EventBridge documentation added to infrastructure/README.md:
  - EventBridge rules configuration and schedule
  - Event structure and payload format
  - Event flow documentation (scheduled and event-based)
  - Testing instructions (manual and script-based)
  - CloudWatch Logs verification steps
  
- **Test Script**: Created `infrastructure/scripts/test_eventbridge.py`:
  - Supports individual test events (signup, features, persona)
  - Supports complete event chain testing
  - Includes clear output and CloudWatch Logs verification instructions
  - Can be run interactively or with command-line arguments

### File List

**Modified Files:**
- `infrastructure/cdk/stacks/lambda_stack.py` - Added EventBridge rules for all three background job Lambda functions
- `spendsense-backend/lambdas/compute_features.py` - Added event emission function and call on completion
- `spendsense-backend/lambdas/assign_persona.py` - Added event emission function and call on completion
- `infrastructure/README.md` - Added comprehensive EventBridge documentation section

**Created Files:**
- `infrastructure/scripts/test_eventbridge.py` - Test script for EventBridge events and Lambda triggers

## Change Log

- 2025-01-XX: Story created and ready for implementation
- 2025-01-XX: Implementation completed
  - Created EventBridge rules for all three background job Lambda functions (scheduled and event-based)
  - Updated Lambda handlers to emit custom events when jobs complete
  - Added EventBridge PutEvents permission to background job Lambda role
  - Added comprehensive EventBridge documentation to infrastructure/README.md
  - Created test script for EventBridge events
  - All tasks completed except verification (requires deployment)
  - Story ready for deployment and testing

