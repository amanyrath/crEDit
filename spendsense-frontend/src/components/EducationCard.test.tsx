import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { EducationCard } from './EducationCard'

const mockEducationCard = {
  id: 'test-1',
  title: 'Understanding Credit Utilization',
  description: 'Credit utilization is the percentage of your credit limit that you are using.',
  fullContent: 'Full content about credit utilization goes here. This is a longer explanation.',
  rationale: 'Your Visa ending in 4523 is at 65% utilization ($3,400 of $5,000 limit)',
  category: 'credit' as const,
  tags: ['Credit', 'DebtManagement'],
}

describe('EducationCard', () => {
  it('renders with all required props', () => {
    render(<EducationCard {...mockEducationCard} />)
    expect(screen.getByText(mockEducationCard.title)).toBeInTheDocument()
    expect(screen.getByText(mockEducationCard.description)).toBeInTheDocument()
    expect(screen.getByText(mockEducationCard.rationale)).toBeInTheDocument()
  })

  it('displays icon correctly', () => {
    render(<EducationCard {...mockEducationCard} />)
    const icon = screen.getByRole('article').querySelector('svg')
    expect(icon).toBeInTheDocument()
  })

  it('displays RationaleBox component', () => {
    render(<EducationCard {...mockEducationCard} />)
    expect(screen.getByText("Why we're showing this")).toBeInTheDocument()
    expect(screen.getByText(mockEducationCard.rationale)).toBeInTheDocument()
  })

  it('displays tags correctly', () => {
    render(<EducationCard {...mockEducationCard} />)
    expect(screen.getByText('#Credit')).toBeInTheDocument()
    expect(screen.getByText('#DebtManagement')).toBeInTheDocument()
  })

  it('displays "Learn More" button', () => {
    render(<EducationCard {...mockEducationCard} />)
    expect(screen.getByRole('button', { name: /learn more/i })).toBeInTheDocument()
  })

  it('opens modal when "Learn More" button is clicked', async () => {
    const user = userEvent.setup()
    render(<EducationCard {...mockEducationCard} />)
    
    const learnMoreButton = screen.getByRole('button', { name: /learn more/i })
    await user.click(learnMoreButton)

    expect(screen.getByRole('dialog')).toBeInTheDocument()
    expect(screen.getByText(mockEducationCard.fullContent)).toBeInTheDocument()
  })

  it('displays loading state correctly', () => {
    render(<EducationCard {...mockEducationCard} loading={true} />)
    const card = screen.getByRole('article')
    expect(card).toHaveClass('animate-pulse')
    expect(screen.queryByText(mockEducationCard.title)).not.toBeInTheDocument()
  })

  it('applies correct category colors', () => {
    const { container } = render(<EducationCard {...mockEducationCard} category="credit" />)
    const title = container.querySelector('[id^="education-title"]')
    expect(title).toHaveClass('border-blue-500')
  })

  it('handles different categories correctly', () => {
    const { container: savingsContainer } = render(
      <EducationCard {...mockEducationCard} category="savings" />
    )
    const savingsTitle = savingsContainer.querySelector('[id^="education-title"]')
    expect(savingsTitle).toHaveClass('border-green-500')

    const { container: budgetingContainer } = render(
      <EducationCard {...mockEducationCard} category="budgeting" />
    )
    const budgetingTitle = budgetingContainer.querySelector('[id^="education-title"]')
    expect(budgetingTitle).toHaveClass('border-purple-500')
  })

  it('has correct accessibility attributes', () => {
    render(<EducationCard {...mockEducationCard} />)
    const card = screen.getByRole('article')
    expect(card).toHaveAttribute('aria-labelledby', `education-title-${mockEducationCard.id}`)
    expect(card).toHaveAttribute('aria-describedby', `education-description-${mockEducationCard.id}`)
  })

  it('handles empty tags array', () => {
    render(<EducationCard {...mockEducationCard} tags={[]} />)
    expect(screen.queryByText('#')).not.toBeInTheDocument()
  })

  it('closes modal when dialog is closed', async () => {
    const user = userEvent.setup()
    render(<EducationCard {...mockEducationCard} />)
    
    const learnMoreButton = screen.getByRole('button', { name: /learn more/i })
    await user.click(learnMoreButton)

    expect(screen.getByRole('dialog')).toBeInTheDocument()

    const closeButton = screen.getByRole('button', { name: /close/i })
    await user.click(closeButton)

    expect(screen.queryByRole('dialog')).not.toBeInTheDocument()
  })

  it('accepts custom className', () => {
    const { container } = render(
      <EducationCard {...mockEducationCard} className="custom-class" />
    )
    const card = container.querySelector('[role="article"]')
    expect(card).toHaveClass('custom-class')
  })

  it('renders with different category icons', () => {
    const { container: creditContainer } = render(
      <EducationCard {...mockEducationCard} category="credit" />
    )
    expect(creditContainer.querySelector('svg')).toBeInTheDocument()

    const { container: savingsContainer } = render(
      <EducationCard {...mockEducationCard} category="savings" />
    )
    expect(savingsContainer.querySelector('svg')).toBeInTheDocument()
  })
})

