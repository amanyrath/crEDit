import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import App from './App'

describe('App', () => {
  it('renders the SpendSense frontend title', () => {
    render(<App />)
    expect(screen.getByText('SpendSense Frontend')).toBeInTheDocument()
  })

  it('renders the TailwindTest component', () => {
    render(<App />)
    expect(screen.getByText('Tailwind CSS is working!')).toBeInTheDocument()
  })
})
