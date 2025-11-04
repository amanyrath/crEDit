import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { RationaleBox } from './RationaleBox'

describe('RationaleBox', () => {
  const mockContent = "Your Visa ending in 4523 is at 65% utilization ($3,400 of $5,000 limit)"

  it('renders with content prop', () => {
    render(<RationaleBox content={mockContent} />)
    expect(screen.getByText(mockContent)).toBeInTheDocument()
  })

  it('displays label correctly', () => {
    render(<RationaleBox content={mockContent} />)
    expect(screen.getByText("Why we're showing this")).toBeInTheDocument()
  })

  it('displays content correctly', () => {
    render(<RationaleBox content={mockContent} />)
    const contentElement = screen.getByText(mockContent)
    expect(contentElement).toBeInTheDocument()
    expect(contentElement).toHaveAttribute('id', 'rationale-content')
  })

  it('applies correct styling classes', () => {
    const { container } = render(<RationaleBox content={mockContent} />)
    const rationaleBox = container.firstChild as HTMLElement
    
    expect(rationaleBox).toHaveClass('rounded-md')
    expect(rationaleBox).toHaveClass('p-4')
    expect(rationaleBox).toHaveClass('border-l-4')
    expect(rationaleBox).toHaveClass('shadow-sm')
    expect(rationaleBox).toHaveClass('bg-[#eff6ff]')
    expect(rationaleBox).toHaveClass('border-[#1e40af]')
  })

  it('has correct accessibility attributes', () => {
    render(<RationaleBox content={mockContent} />)
    const rationaleBox = screen.getByRole('region')
    
    expect(rationaleBox).toHaveAttribute('aria-label', "Why we're showing this")
    expect(rationaleBox).toHaveAttribute('aria-describedby', 'rationale-content')
  })

  it('accepts custom className', () => {
    const { container } = render(
      <RationaleBox content={mockContent} className="custom-class" />
    )
    const rationaleBox = container.firstChild as HTMLElement
    
    expect(rationaleBox).toHaveClass('custom-class')
  })

  it('renders with different content', () => {
    const differentContent = "You have 8 active subscriptions totaling $203/month"
    render(<RationaleBox content={differentContent} />)
    expect(screen.getByText(differentContent)).toBeInTheDocument()
  })
})

