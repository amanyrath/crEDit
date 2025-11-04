import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { TailwindTest } from './TailwindTest'

describe('TailwindTest', () => {
  it('renders the component with correct text', () => {
    render(<TailwindTest />)
    expect(screen.getByText('Tailwind CSS is working!')).toBeInTheDocument()
    expect(
      screen.getByText(/If you see this styled component, Tailwind is configured correctly/)
    ).toBeInTheDocument()
  })
})
