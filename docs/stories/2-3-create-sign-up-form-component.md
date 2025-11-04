# Story 2.3: Create Sign-Up Form Component

Status: drafted

## Story

As a consumer,
I want to create a new account with my email and password,
so that I can access the SpendSense platform and start managing my finances.

## Acceptance Criteria

1. Sign-up form component created (`SignUpForm.tsx`)
2. Form has email, password, and confirm password input fields
3. Form validation:
   - Email: required, valid email format
   - Password: required, meets Cognito password policy (min 8 chars, uppercase, lowercase, digit, symbol)
   - Confirm password: required, matches password
4. Real-time password strength indicator
5. Error messages displayed for invalid inputs
6. Loading state shown during sign-up process
7. Form uses shadcn/ui Input and Button components
8. Form is accessible (keyboard navigation, screen reader support)
9. Form styled with Tailwind CSS
10. Link to login page ("Already have an account? Sign in")
11. Sign-up function calls Cognito `signUp()` API
12. Success message displayed after successful sign-up
13. Automatic sign-in after successful sign-up (since email verification is disabled)
14. Error handling for sign-up failures (email already exists, weak password, etc.)
15. Redirect to dashboard after successful sign-up and sign-in

## Tasks / Subtasks

- [ ] Task 1: Create SignUpForm component structure (AC: #1, #2)
  - [ ] Create `src/components/SignUpForm.tsx` component
  - [ ] Set up component with React Hook Form
  - [ ] Add email input field using shadcn/ui Input component
  - [ ] Add password input field using shadcn/ui Input component (type="password")
  - [ ] Add confirm password input field using shadcn/ui Input component (type="password")
  - [ ] Add form submission handler

- [ ] Task 2: Implement form validation (AC: #3)
  - [ ] Create zod schema for sign-up form:
    - Email: required, valid email format
    - Password: required, meets Cognito password policy
    - Confirm password: required, matches password
  - [ ] Integrate zod schema with React Hook Form using @hookform/resolvers
  - [ ] Display validation error messages for email field
  - [ ] Display validation error messages for password field
  - [ ] Display validation error messages for confirm password field
  - [ ] Test validation with invalid inputs

- [ ] Task 3: Add password strength indicator (AC: #4)
  - [ ] Create password strength validation function
  - [ ] Check for: length >= 8, uppercase, lowercase, digit, symbol
  - [ ] Display visual indicator (weak/medium/strong)
  - [ ] Update indicator in real-time as user types
  - [ ] Show missing requirements (if password doesn't meet policy)

- [ ] Task 4: Add loading state (AC: #6)
  - [ ] Add loading state to form submission
  - [ ] Disable form inputs during loading
  - [ ] Show loading indicator (spinner or disabled button state)
  - [ ] Prevent form submission while loading

- [ ] Task 5: Implement accessibility features (AC: #8)
  - [ ] Add proper labels to form inputs
  - [ ] Add ARIA attributes (aria-label, aria-describedby) for screen readers
  - [ ] Ensure keyboard navigation works (Tab order, Enter to submit)
  - [ ] Add focus management (focus on first error field after validation)
  - [ ] Test with screen reader (if possible) or verify ARIA attributes

- [ ] Task 6: Style form with Tailwind CSS (AC: #9)
  - [ ] Style form container with appropriate spacing and layout
  - [ ] Style input fields with consistent design
  - [ ] Style error messages with appropriate colors
  - [ ] Style submit button with proper states (default, hover, disabled, loading)
  - [ ] Ensure responsive design (mobile-friendly)
  - [ ] Match design system / theme from LoginForm

- [ ] Task 7: Add sign-up link to login page (AC: #10)
  - [ ] Add "Don't have an account? Sign up" link to LoginPage
  - [ ] Link navigates to sign-up page/route
  - [ ] Add "Already have an account? Sign in" link to sign-up page
  - [ ] Link navigates back to login page

- [ ] Task 8: Integrate SignUpForm with Cognito (AC: #11, #12, #13, #14, #15)
  - [ ] Add `signUp` function to `useAuth` hook
  - [ ] Implement `signUp` function using `signUp()` from Amplify Auth
  - [ ] Update SignUpForm to use `useAuth` hook
  - [ ] Connect form submission to `signUp` function
  - [ ] Handle sign-up success (show success message)
  - [ ] Automatically sign in user after successful sign-up
  - [ ] Redirect to dashboard after successful sign-up and sign-in
  - [ ] Handle sign-up errors (email already exists, weak password, etc.)
  - [ ] Display appropriate error messages for different error types
  - [ ] Handle case where email verification is required (if enabled in future)

- [ ] Task 9: Create sign-up page and route (AC: #1, #15)
  - [ ] Create `src/pages/SignUpPage.tsx` component
  - [ ] Add `/signup` route to App.tsx
  - [ ] Style sign-up page consistently with login page
  - [ ] Redirect authenticated users away from sign-up page (to dashboard)

- [ ] Task 10: Add user to default group (AC: #11)
  - [ ] After successful sign-up, assign user to "consumers" group
  - [ ] Note: This may require backend API call or Lambda trigger
  - [ ] If backend API needed, create endpoint for assigning user to group
  - [ ] Call API after successful sign-up to assign user to consumers group

- [ ] Task 11: Create tests for SignUpForm component (AC: #1, #2, #3, #4, #6, #8, #11, #14)
  - [ ] Create unit tests for form rendering
  - [ ] Test email validation (valid/invalid formats)
  - [ ] Test password validation (meets Cognito password policy)
  - [ ] Test confirm password validation (matches password)
  - [ ] Test password strength indicator
  - [ ] Test error message display
  - [ ] Test loading state behavior
  - [ ] Test form submission (mock signUp handler)
  - [ ] Test accessibility features (keyboard navigation, ARIA attributes)
  - [ ] Test error handling for various sign-up failures
  - [ ] Test automatic sign-in after sign-up

## Dev Notes

### Architecture Patterns and Constraints

- **Frontend Framework**: React + TypeScript + Vite [Source: Story 1.1]
- **UI Components**: shadcn/ui components (Input, Button) [Source: Story 2.1]
- **Form Management**: React Hook Form for form state management [Source: Story 2.1]
- **Validation**: zod for schema validation [Source: Story 2.1]
- **Authentication**: AWS Amplify Auth with Cognito [Source: Story 2.2]
- **Styling**: Tailwind CSS [Source: Story 2.1]
- **Testing**: Vitest (frontend testing framework) [Source: Story 1.1]
- **Accessibility**: WCAG 2.1 AA compliance [Source: Story 2.1]

### Project Structure Notes

The sign-up components should be organized as:
```
spendsense-frontend/
├── src/
│   ├── components/
│   │   ├── LoginForm.tsx          # Already exists (Story 2.1)
│   │   └── SignUpForm.tsx         # To be created
│   ├── pages/
│   │   ├── LoginPage.tsx          # Already exists (Story 2.2)
│   │   └── SignUpPage.tsx         # To be created
│   ├── hooks/
│   │   └── useAuth.ts             # Already exists (Story 2.2) - needs signUp function
│   └── ...
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **Component Structure**:
   - Component name: `SignUpForm`
   - File location: `src/components/SignUpForm.tsx`
   - Export: Named export (matching LoginForm pattern)

2. **Form Fields**:
   - Email: Text input with email type validation
   - Password: Password input with Cognito password policy validation
   - Confirm Password: Password input with match validation

3. **Password Policy** (from Cognito configuration):
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one digit
   - At least one special character

4. **Validation Schema** (zod):
   ```typescript
   const signUpSchema = z.object({
     email: z.string().email("Invalid email address"),
     password: z.string()
       .min(8, "Password must be at least 8 characters")
       .regex(/[A-Z]/, "Password must contain an uppercase letter")
       .regex(/[a-z]/, "Password must contain a lowercase letter")
       .regex(/[0-9]/, "Password must contain a digit")
       .regex(/[^A-Za-z0-9]/, "Password must contain a special character"),
     confirmPassword: z.string()
   }).refine((data) => data.password === data.confirmPassword, {
     message: "Passwords do not match",
     path: ["confirmPassword"]
   })
   ```

5. **Password Strength Indicator**:
   - Weak: Less than 3 requirements met
   - Medium: 3-4 requirements met
   - Strong: All 5 requirements met
   - Visual indicator: Color-coded bar or text
   - Show missing requirements below password field

6. **React Hook Form Setup**:
   - Use `useForm` hook with zod resolver
   - Handle form submission with `onSubmit`
   - Access form errors via `formState.errors`
   - Access loading state via custom state or form submission state

7. **shadcn/ui Components**:
   - Input component: For email and password fields
   - Button component: For submit button
   - Ensure components are properly imported and configured

8. **Accessibility Requirements**:
   - Label each input with proper `<label>` elements
   - Associate error messages with inputs using `aria-describedby`
   - Ensure keyboard navigation (Tab, Enter, Escape)
   - Focus management on errors and form submission

9. **Loading State**:
   - Disable form during submission
   - Show loading indicator (spinner, disabled button, or loading text)
   - Prevent multiple submissions

10. **Error Handling**:
    - Display validation errors inline with each field
    - Clear errors when user starts typing
    - Handle Cognito errors:
      - `UsernameExistsException`: Email already exists
      - `InvalidPasswordException`: Password doesn't meet policy
      - `InvalidParameterException`: Invalid email format
      - Network errors: Connection issues

11. **Sign-Up Flow**:
    - Call `signUp()` from Amplify Auth with email and password
    - On success, automatically sign in user (since email verification is disabled)
    - Assign user to "consumers" group (may require backend API call)
    - Redirect to dashboard after successful sign-in
    - Show success message briefly before redirect

12. **useAuth Hook Integration**:
    - Add `signUp(email: string, password: string)` function to `useAuth` hook
    - Function should:
      - Call `signUp()` from `@aws-amplify/auth`
      - Handle success/error cases
      - Optionally auto-sign-in after successful sign-up
      - Return user info or error

### Learnings from Previous Stories

**From Story 2.1 (Status: review)**
- LoginForm component structure and patterns
- Form validation with zod and React Hook Form
- shadcn/ui component usage
- Accessibility features implementation
- Tailwind CSS styling patterns

**From Story 2.2 (Status: review)**
- `useAuth` hook structure and authentication patterns
- Cognito integration with Amplify Auth
- Error handling for authentication failures
- React Router setup and navigation patterns
- Protected routes implementation

**From Story 1.5 (Status: review)**
- Cognito User Pool configuration
- Password policy requirements
- Email verification is disabled for demo (users can sign in immediately)
- User groups: "consumers" and "operators"
- Default role assignment for new users

### References

- [Source: docs/epics.md#Epic-2]
- [Source: docs/architecture.md#Project-Structure]
- [Source: Story 2.1 implementation]
- [Source: Story 2.2 implementation]
- [Source: Story 1.5 implementation]
- [Source: AWS Amplify Auth Documentation - signUp]
- [Source: React Hook Form Documentation]
- [Source: zod Documentation]
- [Source: shadcn/ui Documentation]

## Dev Agent Record

### Context Reference

- `docs/stories/2-3-create-sign-up-form-component.context.xml` (to be created)

### Agent Model Used

<!-- To be filled during implementation -->

### Debug Log References

<!-- To be filled during implementation -->

### Completion Notes List

<!-- To be filled during implementation -->

### File List

<!-- To be filled during implementation -->

## Change Log

- 2025-11-03: Story created and drafted

