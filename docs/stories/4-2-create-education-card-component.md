# Story 4.2: Create Education Card Component

Status: ready-for-dev

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

- [ ] Task 1: Add shadcn/ui Card component (AC: #6)
  - [ ] Install or create Card component from shadcn/ui
  - [ ] Verify Card component works with existing UI components

- [ ] Task 2: Create EducationCard component structure (AC: #1, #2)
  - [ ] Create `src/components/EducationCard.tsx`
  - [ ] Define component props interface
  - [ ] Set up basic card structure with shadcn/ui Card
  - [ ] Add icon display (from lucide-react)
  - [ ] Add title display
  - [ ] Add description display
  - [ ] Add tags display
  - [ ] Add "Learn More" button

- [ ] Task 3: Integrate RationaleBox component (AC: #2)
  - [ ] Import RationaleBox component
  - [ ] Add RationaleBox to card layout
  - [ ] Pass rationale content as prop

- [ ] Task 4: Implement expand/collapse functionality (AC: #3)
  - [ ] Add state management for expanded/collapsed
  - [ ] Implement inline expansion or modal for full content
  - [ ] Handle "Learn More" button click
  - [ ] Display full content when expanded

- [ ] Task 5: Implement card states (AC: #4)
  - [ ] Implement default state
  - [ ] Implement expanded state
  - [ ] Implement loading state
  - [ ] Add loading skeleton/spinner

- [ ] Task 6: Implement category variants (AC: #5)
  - [ ] Define category types (credit, savings, budgeting, etc.)
  - [ ] Add color coding by category
  - [ ] Map category to appropriate colors
  - [ ] Style card variants

- [ ] Task 7: Implement accessibility and responsiveness (AC: #7)
  - [ ] Add ARIA labels
  - [ ] Ensure keyboard navigation
  - [ ] Test screen reader compatibility
  - [ ] Ensure responsive design (mobile-friendly)
  - [ ] Add semantic HTML structure

- [ ] Task 8: Create component tests (AC: #1, #2, #3, #4, #5, #6, #7)
  - [ ] Create `src/components/EducationCard.test.tsx`
  - [ ] Test component renders with all props
  - [ ] Test icon displays correctly
  - [ ] Test RationaleBox integration
  - [ ] Test expand/collapse functionality
  - [ ] Test card states (default, expanded, loading)
  - [ ] Test category variants
  - [ ] Test accessibility attributes

- [ ] Task 9: Verify component matches UX specification (AC: #8)
  - [ ] Verify component matches UX design
  - [ ] Test component in isolation
  - [ ] Verify responsive behavior
  - [ ] Ensure component is reusable

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
- Ready to begin implementation

### Completion Notes
_(To be completed after implementation)_

## File List
_(To be updated during implementation)_

## Change Log
- 2025-11-03: Story created and marked ready-for-dev

