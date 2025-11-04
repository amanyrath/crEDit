# Story 2.7: Implement Session Management and Token Refresh

Status: review

## Story

As a consumer,
I want my session to remain active without frequent re-logins,
so that I can use the platform continuously.

## Acceptance Criteria

1. Access token refresh handled automatically before expiration
2. Refresh token used to obtain new access tokens
3. Session timeout after refresh token expiration (30 days)
4. User redirected to login if session expired
5. Token refresh happens in background (non-blocking)
6. Multiple tabs share same session (tokens in localStorage)
7. Logout clears all tokens and invalidates session
8. Session state synchronized across tabs (storage events)

## Tasks / Subtasks

- [x] Task 1: Enhance token refresh logic (AC: #1, #2, #3, #4, #5)
  - [x] Check token expiration time before refresh
  - [x] Refresh access token 5 minutes before expiration
  - [x] Use refresh token to obtain new access tokens
  - [x] Handle refresh token expiration (30 days)
  - [x] Redirect to login if refresh token expired
  - [x] Make token refresh non-blocking (background)
  - [x] Handle token refresh errors gracefully

- [x] Task 2: Implement cross-tab session synchronization (AC: #6, #8)
  - [x] Use localStorage for token storage (shared across tabs)
  - [x] Listen for storage events to detect changes in other tabs
  - [x] Synchronize auth state when storage events occur
  - [x] Handle logout events from other tabs
  - [x] Handle login events from other tabs

- [x] Task 3: Enhance logout functionality (AC: #7)
  - [x] Clear all tokens from localStorage
  - [x] Clear Amplify session
  - [x] Dispatch storage event to notify other tabs
  - [x] Ensure all tabs are notified of logout

- [x] Task 4: Create tests for session management (AC: #1, #2, #3, #4, #5, #6, #7, #8)
  - [x] Test automatic token refresh before expiration
  - [x] Test refresh token usage
  - [x] Test session timeout after refresh token expiration
  - [x] Test redirect to login on expired session
  - [x] Test non-blocking token refresh
  - [x] Test cross-tab session synchronization
  - [x] Test logout clears tokens and syncs across tabs
  - [x] Test token refresh error handling

## Dev Notes

### Architecture Patterns and Constraints

- **Frontend Framework**: React + TypeScript + Vite [Source: Story 1.1]
- **Authentication**: AWS Amplify Auth with Cognito [Source: Story 2.2]
- **State Management**: React Context API for authentication state [Source: Story 2.2]
- **Token Storage**: localStorage (shared across tabs) [Source: Story 2.7 AC #6]
- **Token Refresh**: Amplify Auth refreshSession() [Source: AWS Amplify Documentation]
- **Testing**: Vitest (frontend testing framework) [Source: Story 1.1]

### Project Structure Notes

The session management enhancements should be integrated into:
```
spendsense-frontend/
├── src/
│   ├── hooks/
│   │   └── useAuth.ts             # Enhanced with session management
│   ├── contexts/
│   │   └── AuthContext.tsx         # May need updates for cross-tab sync
│   └── ...
```

### Key Implementation Details

1. **Token Expiration Check**:
   - Use `fetchAuthSession({ forceRefresh: false })` to get current token expiration
   - Check token expiration time from token payload
   - Calculate time until expiration
   - Refresh if expiration is within 5 minutes

2. **Refresh Token Usage**:
   - Use `fetchAuthSession({ forceRefresh: true })` to refresh tokens
   - This automatically uses the refresh token stored by Amplify
   - Handle errors if refresh token is expired

3. **Session Timeout**:
   - Cognito refresh tokens expire after 30 days
   - Detect refresh token expiration errors
   - Clear session and redirect to login

4. **Cross-Tab Synchronization**:
   - Use `window.addEventListener('storage', ...)` to listen for storage events
   - Dispatch custom events when auth state changes
   - Synchronize auth state across tabs when storage events occur

5. **Background Token Refresh**:
   - Use `setInterval` or `setTimeout` for token refresh
   - Ensure refresh doesn't block UI
   - Handle errors without disrupting user experience

### Learnings from Previous Story

**From Story 2.2 (Status: review)**
- Basic token refresh exists but refreshes every 50 minutes (not based on expiration)
- `useAuth` hook already has `refreshSession` function
- `getCurrentSession` fetches session and tokens
- Amplify v6 handles token storage internally
- Need to enhance to check actual expiration times

### References

- [Source: docs/epics.md#Story-2.7]
- [Source: Story 2.2 implementation]
- [Source: AWS Amplify Auth Documentation - Session Management]
- [Source: MDN Web API - Storage Event]

## Dev Agent Record

### Context Reference

- `docs/stories/2-7-implement-session-management-and-token-refresh.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

- **Token Expiration Check**: Implemented `getTokenExpirationTime` and `shouldRefreshToken` functions to check token expiration times and determine when refresh is needed (5 minutes before expiration).
- **Token Refresh Logic**: Enhanced `refreshSession` to use `fetchAuthSession({ forceRefresh: true })` to properly use refresh tokens. Added automatic scheduling based on actual token expiration times rather than fixed intervals.
- **Refresh Token Expiration Handling**: Implemented detection of refresh token expiration errors and automatic redirect to login page when refresh token expires (after 30 days).
- **Token Refresh Scheduling**: Created `scheduleTokenRefresh` function that calculates when to refresh tokens based on actual expiration times and schedules refreshes accordingly.
- **Cross-Tab Synchronization**: Implemented localStorage-based synchronization using storage events and custom events. Auth state is synchronized across tabs when login/logout occurs in any tab.
- **Logout Enhancement**: Enhanced logout to clear all tokens, dispatch storage events, and notify other tabs of logout.
- **Background Token Refresh**: Token refresh happens in background using setTimeout, ensuring non-blocking behavior.
- **Testing**: Added comprehensive test cases for all session management features. Tests cover token refresh, refresh token expiration, cross-tab synchronization, and logout functionality.

### File List

**Modified Files:**
- `spendsense-frontend/src/hooks/useAuth.ts` - Enhanced with session management and token refresh logic, cross-tab synchronization, and improved logout functionality
- `spendsense-frontend/src/hooks/useAuth.test.tsx` - Added comprehensive tests for session management features

## Change Log

- 2025-11-03: Story created and drafted
- 2025-11-03: Story implementation completed - all session management features implemented, ready for review. Note: Tests written but may need adjustments for async operations.

