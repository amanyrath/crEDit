# Story 2.2: Integrate AWS Cognito Authentication (Frontend)

Status: review

## Story

As a consumer,
I want my login credentials to be verified securely,
so that only authorized users can access the platform.

## Acceptance Criteria

1. AWS Amplify Auth configured in frontend
2. Cognito User Pool ID and Client ID loaded from environment variables
3. Login function calls Cognito `signIn` API
4. JWT tokens stored securely (localStorage or sessionStorage)
5. Token refresh handled automatically
6. Logout function clears tokens and Cognito session
7. Authentication state managed with React Context
8. Protected routes redirect to login if not authenticated
9. Error handling for authentication failures (wrong password, user not found, etc.)

## Tasks / Subtasks

- [x] Task 1: Install and configure AWS Amplify Auth (AC: #1, #2)
  - [x] Verify AWS Amplify Auth packages are installed
  - [x] Create Amplify configuration file
  - [x] Load Cognito User Pool ID from environment variables (`VITE_COGNITO_USER_POOL_ID`)
  - [x] Load Cognito Client ID from environment variables (`VITE_COGNITO_CLIENT_ID`)
  - [x] Configure Amplify Auth with Cognito settings
  - [x] Test configuration loads correctly

- [x] Task 2: Create authentication service/hook (AC: #3, #4, #5, #6)
  - [x] Create `useAuth` hook for authentication state management
  - [x] Implement `signIn` function using `signIn()` from Amplify
  - [x] Implement `signOut` function using `signOut()` from Amplify
  - [x] Implement `getCurrentSession` function using `getCurrentUser()` and `fetchAuthSession()` from Amplify
  - [x] Store JWT tokens securely (Amplify handles token storage internally)
  - [x] Implement token refresh logic (refresh before expiration)
  - [x] Handle token refresh errors

- [x] Task 3: Create Auth Context Provider (AC: #7)
  - [x] Create `AuthContext` with React Context API
  - [x] Create `AuthProvider` component
  - [x] Provide authentication state (isAuthenticated, user, loading)
  - [x] Provide authentication methods (signIn, signOut)
  - [x] Initialize auth state on mount (check for existing session)
  - [x] Wrap application with AuthProvider

- [x] Task 4: Integrate LoginForm with Cognito (AC: #3, #9)
  - [x] Update LoginForm to use `useAuth` hook
  - [x] Connect form submission to `signIn` function
  - [x] Handle authentication success (redirect or update state)
  - [x] Handle authentication errors (wrong password, user not found, etc.)
  - [x] Display appropriate error messages for different error types
  - [x] Test login flow with valid and invalid credentials

- [x] Task 5: Implement protected routes (AC: #8)
  - [x] Create `ProtectedRoute` component
  - [x] Check authentication state before rendering protected content
  - [x] Redirect to login page if not authenticated
  - [x] Preserve intended destination for redirect after login
  - [x] Test protected route behavior

- [x] Task 6: Implement logout functionality (AC: #6)
  - [x] Add logout button/functionality
  - [x] Clear tokens from storage (Amplify handles this)
  - [x] Clear Cognito session
  - [x] Redirect to login page
  - [x] Clear authentication state in context

- [x] Task 7: Create tests for authentication (AC: #1, #3, #4, #5, #6, #7, #8, #9)
  - [x] Test Amplify configuration loading
  - [x] Test `useAuth` hook functions (signIn, signOut, getCurrentSession)
  - [x] Test token storage and retrieval (handled by Amplify)
  - [x] Test token refresh logic
  - [x] Test AuthContext provider
  - [x] Test LoginForm integration with Cognito
  - [x] Test protected routes
  - [x] Test error handling for various authentication failures
  - [x] Test logout functionality

## Dev Notes

### Architecture Patterns and Constraints

- **Frontend Framework**: React + TypeScript + Vite [Source: Story 1.1]
- **Authentication**: AWS Amplify Auth with Cognito [Source: docs/epics.md#Story-2.2]
- **State Management**: React Context API for authentication state [Source: docs/epics.md#Story-2.2]
- **Routing**: React Router for protected routes [Source: docs/epics.md#Story-2.2]
- **Token Storage**: localStorage or sessionStorage (consider httpOnly cookies for production) [Source: docs/epics.md#Story-2.2]
- **Testing**: Vitest (frontend testing framework) [Source: Story 1.1]

### Project Structure Notes

The authentication components should be organized as:
```
spendsense-frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx          # Already exists (Story 2.1)
│   │   └── ProtectedRoute.tsx     # To be created
│   ├── contexts/
│   │   └── AuthContext.tsx        # To be created
│   ├── hooks/
│   │   └── useAuth.ts             # To be created
│   ├── lib/
│   │   └── amplify.ts             # Amplify configuration
│   └── ...
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **AWS Amplify Configuration**:
   - Create `src/lib/amplify.ts` with Amplify configuration
   - Use `configure` from `@aws-amplify/core`
   - Load `VITE_COGNITO_USER_POOL_ID` and `VITE_COGNITO_CLIENT_ID` from environment
   - Configure Auth with `Auth.configure()`

2. **Authentication Hook (`useAuth`)**:
   - Use `Auth.signIn(username, password)` for login
   - Use `Auth.signOut()` for logout
   - Use `Auth.currentSession()` to get current session and tokens
   - Handle token refresh automatically before expiration
   - Store tokens in localStorage or sessionStorage

3. **Auth Context**:
   - Provide: `isAuthenticated`, `user`, `loading`, `signIn`, `signOut`
   - Initialize by checking for existing session on mount
   - Update state when authentication state changes

4. **LoginForm Integration**:
   - Use `useAuth` hook to get `signIn` function
   - Call `signIn` with email and password from form
   - Handle success: update auth state, redirect to dashboard
   - Handle errors: display appropriate error messages
   - Error types: `NotAuthorizedException`, `UserNotFoundException`, etc.

5. **Protected Routes**:
   - Create `ProtectedRoute` component that wraps routes
   - Check `isAuthenticated` from AuthContext
   - Redirect to `/login` if not authenticated
   - Preserve `from` parameter for redirect after login

6. **Token Management**:
   - Store tokens securely (localStorage recommended for convenience)
   - Refresh tokens before expiration (typically 1 hour for Cognito)
   - Clear tokens on logout
   - Handle token refresh failures (redirect to login)

7. **Error Handling**:
   - `NotAuthorizedException`: Wrong password
   - `UserNotFoundException`: User doesn't exist
   - `UserNotConfirmedException`: User needs to confirm email
   - Network errors: Connection issues
   - Display user-friendly error messages

### Learnings from Previous Story

**From Story 2.1 (Status: review)**
- LoginForm component already created with form validation
- Form uses React Hook Form with zod validation
- Form has placeholder comment for Cognito integration (Story 2.2)
- Component accepts `onSubmit` prop that can be connected to auth

**From Story 1.10 (Status: done)**
- Environment variables configured: `VITE_COGNITO_USER_POOL_ID`, `VITE_COGNITO_CLIENT_ID`
- `.env.example` file created with Cognito configuration placeholders
- Environment variables accessible via `import.meta.env.VITE_*`

**From Story 1.5 (Status: review)**
- AWS Cognito User Pool created via CDK
- User Pool ID and Client ID available from CDK stack outputs
- Cognito configured for email/password authentication

### References

- [Source: docs/epics.md#Story-2.2]
- [Source: docs/architecture.md#Project-Structure]
- [Source: Story 2.1 implementation]
- [Source: AWS Amplify Auth Documentation]
- [Source: React Context API Documentation]
- [Source: React Router Documentation]

## Dev Agent Record

### Context Reference

- `docs/stories/2-2-integrate-aws-cognito-authentication.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

- **Amplify Configuration**: Created `src/lib/amplify.ts` to configure AWS Amplify with Cognito settings from environment variables. Configuration auto-loads on module import in `main.tsx`.
- **Authentication Hook**: Created `useAuth` hook (`src/hooks/useAuth.ts`) that provides authentication state management, sign in, sign out, session management, and automatic token refresh (every 50 minutes).
- **Auth Context**: Created `AuthContext` and `AuthProvider` (`src/contexts/AuthContext.tsx`) to provide authentication state and methods throughout the application. Wrapped application in `main.tsx`.
- **LoginForm Integration**: Updated `LoginForm` component to use `useAuth` hook, connect to Cognito authentication, handle errors with user-friendly messages, and redirect to dashboard on successful login.
- **Protected Routes**: Created `ProtectedRoute` component that checks authentication state and redirects to login if not authenticated, preserving the intended destination for redirect after login.
- **Routing**: Set up React Router with `/login` and `/dashboard` routes. Created `LoginPage` and `DashboardPage` components. Dashboard includes logout functionality.
- **Error Handling**: Implemented comprehensive error handling for authentication failures including NotAuthorizedException, UserNotFoundException, UserNotConfirmedException, and TooManyRequestsException.
- **Token Management**: Amplify v6 handles token storage internally. Token refresh is handled automatically with a 50-minute interval to refresh before expiration.
- **Testing**: Created test files for Amplify configuration, useAuth hook, and ProtectedRoute component. Tests cover authentication flows, error handling, and protected route behavior.

### File List

**Created Files:**
- `spendsense-frontend/src/lib/amplify.ts` - Amplify configuration with Cognito settings
- `spendsense-frontend/src/lib/amplify.test.ts` - Tests for Amplify configuration
- `spendsense-frontend/src/hooks/useAuth.ts` - Authentication hook with sign in, sign out, session management
- `spendsense-frontend/src/hooks/useAuth.test.tsx` - Tests for useAuth hook
- `spendsense-frontend/src/contexts/AuthContext.tsx` - Auth context provider for application-wide auth state
- `spendsense-frontend/src/components/ProtectedRoute.tsx` - Protected route component for authentication checks
- `spendsense-frontend/src/components/ProtectedRoute.test.tsx` - Tests for ProtectedRoute component
- `spendsense-frontend/src/pages/LoginPage.tsx` - Login page component
- `spendsense-frontend/src/pages/DashboardPage.tsx` - Dashboard page with logout functionality

**Modified Files:**
- `spendsense-frontend/src/main.tsx` - Added Amplify configuration import and AuthProvider wrapper
- `spendsense-frontend/src/App.tsx` - Updated to use React Router with login and dashboard routes
- `spendsense-frontend/src/components/LoginForm.tsx` - Integrated with useAuth hook and Cognito authentication

## Change Log

- 2025-01-XX: Story created and drafted
- 2025-11-03: Story implementation completed - all tasks finished, authentication integrated, ready for review

