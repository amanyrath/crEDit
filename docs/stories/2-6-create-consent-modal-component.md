# Story 2.6: Create Consent Modal Component

Status: review

## Story

As a consumer,
I want to understand what data will be used before granting consent,
so that I can make an informed decision about data sharing.

## Acceptance Criteria

1. Consent modal component created (`ConsentModal.tsx`)
2. Modal displays:
   - Welcome message
   - Explanation of data usage
   - List of data accessed (transactions, account balances, payment patterns)
   - List of what is NOT done (no sharing, no financial advice, no credential access)
   - Checkbox: "I consent to SpendSense analyzing my financial data"
   - Accept and Decline buttons
3. Modal appears on first login (if consent not granted)
4. Modal cannot be dismissed without accepting or declining
5. Modal uses shadcn/ui Dialog component
6. Modal is accessible (keyboard navigation, focus management)
7. Modal styled with Tailwind CSS

## Tasks / Subtasks

- [x] Task 1: Create ConsentModal component structure (AC: #1, #2)
  - [x] Create `src/components/ConsentModal.tsx` component
  - [x] Set up component with shadcn/ui Dialog component
  - [x] Add welcome message section
  - [x] Add explanation of data usage section
  - [x] Add list of data accessed (transactions, account balances, payment patterns)
  - [x] Add list of what is NOT done (no sharing, no financial advice, no credential access)
  - [x] Add consent checkbox with label
  - [x] Add Accept and Decline buttons

- [x] Task 2: Implement modal behavior (AC: #3, #4)
  - [x] Create logic to check consent status (placeholder for now, will use API in next story)
  - [x] Show modal if consent not granted (after login)
  - [x] Prevent modal dismissal without accepting or declining
  - [x] Handle Accept button click (placeholder for now)
  - [x] Handle Decline button click (placeholder for now)
  - [x] Close modal after consent action is taken

- [x] Task 3: Integrate ConsentModal with authentication flow (AC: #3)
  - [x] Add ConsentModal to DashboardPage or App component
  - [x] Show modal after successful login if consent not granted
  - [x] Check consent status from auth context (placeholder for now)
  - [x] Ensure modal appears before dashboard content is shown

- [x] Task 4: Implement accessibility features (AC: #6)
  - [x] Ensure keyboard navigation works (Tab, Enter, Escape)
  - [x] Add proper ARIA attributes (aria-label, aria-describedby, role)
  - [x] Implement focus management (focus trap within modal)
  - [x] Ensure screen reader support
  - [x] Add proper heading structure

- [x] Task 5: Style modal with Tailwind CSS (AC: #7)
  - [x] Style modal container and overlay
  - [x] Style modal content sections
  - [x] Style lists (data accessed and what is NOT done)
  - [x] Style checkbox and label
  - [x] Style Accept and Decline buttons
  - [x] Ensure responsive design (mobile-friendly)
  - [x] Match design system / theme from other components

- [x] Task 6: Create tests for ConsentModal component (AC: #1, #2, #3, #4, #5, #6)
  - [x] Test modal rendering
  - [x] Test all content sections are displayed
  - [x] Test modal appears when consent not granted
  - [x] Test modal cannot be dismissed without accepting or declining
  - [x] Test Accept button functionality
  - [x] Test Decline button functionality
  - [x] Test checkbox interaction
  - [x] Test accessibility features (keyboard navigation, ARIA attributes)
  - [x] Test focus management

## Dev Notes

### Architecture Patterns and Constraints

- **Frontend Framework**: React + TypeScript + Vite [Source: Story 1.1]
- **UI Components**: shadcn/ui Dialog component [Source: Story 2.1]
- **Styling**: Tailwind CSS [Source: Story 2.1]
- **Authentication**: AWS Amplify Auth with Cognito [Source: Story 2.2]
- **Testing**: Vitest (frontend testing framework) [Source: Story 1.1]
- **Accessibility**: WCAG 2.1 AA compliance [Source: Story 2.1]

### Project Structure Notes

The consent modal component should be organized as:
```
spendsense-frontend/
├── src/
│   ├── components/
│   │   ├── ConsentModal.tsx         # To be created
│   │   ├── LoginForm.tsx            # Already exists
│   │   └── SignUpForm.tsx           # Already exists
│   ├── pages/
│   │   └── DashboardPage.tsx        # Already exists - may need integration
│   └── ...
```

[Source: docs/architecture.md#Project-Structure]

### Key Implementation Details

1. **Component Structure**:
   - Component name: `ConsentModal`
   - File location: `src/components/ConsentModal.tsx`
   - Export: Named export

2. **Modal Content**:
   - Welcome message: Brief introduction to SpendSense
   - Data usage explanation: Clear explanation of how data is used
   - Data accessed list:
     - Transactions
     - Account balances
     - Payment patterns
   - What is NOT done list:
     - No data sharing with third parties
     - No financial advice provided
     - No credential access required
   - Consent checkbox: Required before Accept button is enabled
   - Accept button: Enabled only when checkbox is checked
   - Decline button: Always enabled

3. **shadcn/ui Dialog Component**:
   - Use Dialog component from shadcn/ui
   - Configure with `open` prop to control visibility
   - Set `onOpenChange` to prevent dismissal (when needed)
   - Use DialogContent, DialogHeader, DialogTitle, DialogDescription
   - Ensure proper modal structure

4. **Modal Behavior**:
   - Modal should appear automatically after login if consent not granted
   - Modal cannot be closed by clicking overlay or pressing Escape (until Accept/Decline is clicked)
   - Accept button should be disabled until checkbox is checked
   - After Accept/Decline, modal should close (will integrate with API in next story)

5. **Accessibility Requirements**:
   - Proper ARIA labels and roles
   - Focus trap within modal
   - Keyboard navigation support
   - Screen reader announcements
   - Proper heading hierarchy

6. **Integration Points**:
   - Will need to check consent status from auth context (placeholder for now)
   - Will need to call consent API after Accept/Decline (to be implemented in next story)
   - Should integrate with DashboardPage or App component

### Learnings from Previous Stories

**From Story 2.1 (Status: review)**
- Component structure and patterns
- shadcn/ui component usage
- Accessibility features implementation
- Tailwind CSS styling patterns

**From Story 2.2 (Status: review)**
- `useAuth` hook structure and authentication patterns
- React Router setup and navigation patterns
- Protected routes implementation

**From Story 2.4 (Status: review)**
- Form component patterns
- Checkbox usage
- Button styling and states

### References

- [Source: docs/epics.md#Epic-2]
- [Source: docs/architecture.md#Project-Structure]
- [Source: Story 2.1 implementation]
- [Source: Story 2.2 implementation]
- [Source: Story 2.4 implementation]
- [Source: shadcn/ui Dialog Documentation]
- [Source: WCAG 2.1 Guidelines]

## Dev Agent Record

### Context Reference

- `docs/stories/2-6-create-consent-modal-component.context.xml` (to be created)

### Agent Model Used

AI Assistant (Claude Sonnet 4.5)

### Debug Log References

- Added shadcn/ui Dialog and Checkbox components
- Created ConsentModal component with all required content sections
- Integrated modal with DashboardPage component
- Implemented consent status check using localStorage (placeholder for API integration)
- Added comprehensive test suite with 23 passing tests
- All accessibility features implemented (ARIA attributes, keyboard navigation, focus management)

### Completion Notes List

- Created ConsentModal component with full modal structure, content sections, and accessibility features
- Integrated ConsentModal with DashboardPage to show modal after login if consent not granted
- Implemented consent status check using localStorage (will be replaced with API call in next story)
- Added comprehensive test suite covering all acceptance criteria and accessibility requirements
- All 23 tests passing successfully
- Modal prevents dismissal without accepting or declining (uses onEscapeKeyDown and onInteractOutside handlers)
- Accept button disabled until checkbox is checked
- Responsive design implemented with Tailwind CSS

### File List

- Created: `spendsense-frontend/src/components/ConsentModal.tsx`
- Created: `spendsense-frontend/src/components/ConsentModal.test.tsx`
- Created: `spendsense-frontend/src/components/ui/dialog.tsx`
- Created: `spendsense-frontend/src/components/ui/checkbox.tsx`
- Modified: `spendsense-frontend/src/pages/DashboardPage.tsx` (integrated ConsentModal)
- Modified: `spendsense-frontend/package.json` (added lucide-react dependency)

## Change Log

- 2025-11-03: Story created and marked ready-for-dev
- 2025-11-03: Story implementation completed, all tasks done, all tests passing (23/23)

