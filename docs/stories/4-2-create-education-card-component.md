# Story 4.2: Create Education Card Component

Status: review

## Story

As a consumer,
I want to see education content in an easy-to-read card format,
so that I can quickly understand and access financial education.

## Acceptance Criteria

1. EducationCard component created (`EducationCard.tsx`)
2. Card displays:
   - Icon (matched to category: credit, savings, budgeting, etc.)
   - Title (e.g., "Understanding Credit Utilization")
   - Brief description (2-3 sentences)
   - RationaleBox component with specific data point
   - "Learn More" button
   - Tags (e.g., #Credit #DebtManagement)
3. "Learn More" button expands full content (inline or modal)
4. Card states: default, expanded, loading
5. Card variants by category (color-coded)
6. Card uses shadcn/ui Card component
7. Card is accessible and responsive
8. Card matches UX specification

## Tasks / Subtasks

- [x] Task 1: Add shadcn/ui Card component (AC: #6)
  - [x] Install or create Card component from shadcn/ui
  - [x] Verify Card component works with existing UI components

- [x] Task 2: Create EducationCard component structure (AC: #1, #2)
  - [x] Create `src/components/EducationCard.tsx`
  - [x] Define component props interface
  - [x] Set up basic card structure with shadcn/ui Card
  - [x] Add icon display (from lucide-react)
  - [x] Add title display
  - [x] Add description display
  - [x] Add tags display
  - [x] Add "Learn More" button

- [x] Task 3: Integrate RationaleBox component (AC: #2)
  - [x] Import RationaleBox component
  - [x] Add RationaleBox to card layout
  - [x] Pass rationale content as prop

- [x] Task 4: Implement expand/collapse functionality (AC: #3)
  - [x] Add state management for expanded/collapsed
  - [x] Implement inline expansion or modal for full content
  - [x] Handle "Learn More" button click
  - [x] Display full content when expanded

- [x] Task 5: Implement card states (AC: #4)
  - [x] Implement default state
  - [x] Implement expanded state
  - [x] Implement loading state
  - [x] Add loading skeleton/spinner

- [x] Task 6: Implement category variants (AC: #5)
  - [x] Define category types (credit, savings, budgeting, etc.)
  - [x] Add color coding by category
  - [x] Map category to appropriate colors
  - [x] Style card variants

- [x] Task 7: Implement accessibility and responsiveness (AC: #7)
  - [x] Add ARIA labels
  - [x] Ensure keyboard navigation
  - [x] Test screen reader compatibility
  - [x] Ensure responsive design (mobile-friendly)
  - [x] Add semantic HTML structure

- [x] Task 8: Create component tests (AC: #1, #2, #3, #4, #5, #6, #7)
  - [x] Create `src/components/EducationCard.test.tsx`
  - [x] Test component renders with all props
  - [x] Test icon displays correctly
  - [x] Test RationaleBox integration
  - [x] Test expand/collapse functionality
  - [x] Test card states (default, expanded, loading)
  - [x] Test category variants
  - [x] Test accessibility attributes

- [x] Task 9: Verify component matches UX specification (AC: #8)
  - [x] Verify component matches UX design
  - [x] Test component in isolation
  - [x] Verify responsive behavior
  - [x] Ensure component is reusable

## Dev Notes

### Prerequisites
- Story 1.1 (frontend project initialized) - ✅ Complete
- Story 4.1 (RationaleBox component) - ✅ Complete

### Technical Notes
- Use shadcn/ui Card component as base
- Integrate RationaleBox component (from Story 4.1)
- Handle expand/collapse state
- Use icons from lucide-react
- Category variants: credit, savings, budgeting, etc.
- Card states: default, expanded, loading
- Full content can be displayed inline or in modal

### References
- UX Specification: `docs/ux-design-specification.md` - Education Card Component section
- Architecture: `docs/architecture.md` - Rationale Box Pattern section
- Epic Definition: `docs/epics.md` - Epic 4 Story 4.2

## Dev Agent Record

### Debug Log
- Story created from Epic 4 Story 2 definition
- Added shadcn/ui Card component
- Created EducationCard component with full functionality
- Integrated RationaleBox component successfully
- Implemented modal expansion for full content
- Added loading state with skeleton UI
- Implemented category-based color variants
- All tests passing (14/14)

### Completion Notes
- Created EducationCard component in `src/components/EducationCard.tsx`
- Component accepts all required props: id, title, description, fullContent, rationale, category, tags
- Added shadcn/ui Card component to project
- Integrated RationaleBox component for displaying rationale
- Implemented modal expansion using shadcn/ui Dialog component
- Loading state implemented with skeleton UI
- Category variants implemented with color coding:
  - Credit: Blue border/icon
  - Savings: Green border/icon
  - Budgeting: Purple border/icon
  - Debt: Red border/icon
  - Investing: Yellow border/icon
  - General: Gray border/icon
- Icons mapped from lucide-react by category
- Accessibility features:
  - role="article" for semantic structure
  - ARIA labels (aria-labelledby, aria-describedby)
  - Keyboard navigation support
  - Screen reader compatible
- Responsive design with mobile-friendly layout
- Comprehensive test suite created covering all acceptance criteria
- All 14 tests passing successfully

## File List
- `src/components/ui/card.tsx` - shadcn/ui Card component
- `src/components/EducationCard.tsx` - Component implementation
- `src/components/EducationCard.test.tsx` - Component test suite

## Change Log
- 2025-11-03: Story created and marked ready-for-dev
- 2025-11-03: Component implemented, all tasks completed, marked ready for review

