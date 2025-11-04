import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { LoginForm } from './LoginForm'

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Form Rendering', () => {
    it('renders email and password input fields', () => {
      render(<LoginForm />)
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument()
    })

    it('renders with proper labels', () => {
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(passwordInput).toHaveAttribute('type', 'password')
    })

    it('renders with placeholder text', () => {
      render(<LoginForm />)
      
      expect(screen.getByPlaceholderText(/enter your email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
    })
  })

  describe('Email Validation', () => {
    it('displays error for invalid email format', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'invalid-email')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      }, { timeout: 3000 })
    })

    it('displays error for empty email', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const submitButton = screen.getByRole('button', { name: /log in/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      })
    })

    it('accepts valid email format', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      render(<LoginForm onSubmit={onSubmit} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
        })
      })
      
      expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument()
    })
  })

  describe('Password Validation', () => {
    it('displays error for empty password', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/password is required/i)).toBeInTheDocument()
      })
    })

    it('accepts non-empty password', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      render(<LoginForm onSubmit={onSubmit} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'p')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })
      
      expect(screen.queryByText(/password is required/i)).not.toBeInTheDocument()
    })
  })

  describe('Error Message Display', () => {
    it('displays error messages with proper ARIA attributes', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'invalid')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        const errorMessage = screen.getByText(/invalid email address/i)
        expect(errorMessage).toBeInTheDocument()
        expect(errorMessage).toHaveAttribute('role', 'alert')
        expect(errorMessage).toHaveAttribute('id', 'email-error')
      }, { timeout: 3000 })
      
      const emailInputAfterError = screen.getByLabelText(/email/i)
      expect(emailInputAfterError).toHaveAttribute('aria-describedby', 'email-error')
      expect(emailInputAfterError).toHaveAttribute('aria-invalid', 'true')
    })

    it('clears errors when user starts typing', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'invalid')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      }, { timeout: 3000 })
      
      await user.clear(emailInput)
      await user.type(emailInput, 'test@example.com')
      
      await waitFor(() => {
        expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument()
      }, { timeout: 3000 })
    })
  })

  describe('Loading State', () => {
    it('shows loading state during form submission', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn(async () => {
        await new Promise<void>((resolve) => setTimeout(resolve, 100))
      })
      render(<LoginForm onSubmit={onSubmit} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      expect(screen.getByRole('button', { name: /logging in/i })).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
      expect(emailInput).toBeDisabled()
      expect(passwordInput).toBeDisabled()
      
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument()
      }, { timeout: 200 })
    })

    it('prevents multiple submissions while loading', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn(async () => {
        await new Promise<void>((resolve) => setTimeout(resolve, 100))
      })
      render(<LoginForm onSubmit={onSubmit} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      await user.click(submitButton) // Try to submit again
      await user.click(submitButton) // Try again
      
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledTimes(1)
      })
    })
  })

  describe('Form Submission', () => {
    it('calls onSubmit with form data when valid', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      render(<LoginForm onSubmit={onSubmit} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
        })
      })
    })

    it('handles submission without onSubmit prop', async () => {
      const user = userEvent.setup()
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Login attempt:', {
          email: 'test@example.com',
          password: 'password123',
        })
      })
      
      consoleSpy.mockRestore()
    })
  })

  describe('Accessibility Features', () => {
    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      emailInput.focus()
      expect(emailInput).toHaveFocus()
      
      await user.tab()
      expect(passwordInput).toHaveFocus()
      
      await user.tab()
      expect(submitButton).toHaveFocus()
    })

    it('submits form on Enter key press', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      render(<LoginForm onSubmit={onSubmit} />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.keyboard('{Enter}')
      
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })
    })

    it('has proper ARIA labels for screen readers', () => {
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      expect(emailInput).toHaveAttribute('aria-label', 'Email address')
      expect(passwordInput).toHaveAttribute('aria-label', 'Password')
      expect(submitButton).toHaveAttribute('aria-label', 'Log in')
    })

    it('has proper ARIA attributes for error states', async () => {
      const user = userEvent.setup()
      render(<LoginForm />)
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'invalid')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      }, { timeout: 3000 })
      
      const emailInputAfterError = screen.getByLabelText(/email/i)
      expect(emailInputAfterError).toHaveAttribute('aria-invalid', 'true')
      expect(emailInputAfterError).toHaveAttribute('aria-describedby', 'email-error')
      const errorMessage = screen.getByText(/invalid email address/i)
      expect(errorMessage).toHaveAttribute('aria-live', 'polite')
    })
  })

  describe('Responsive Design', () => {
    it('has responsive width classes', () => {
      const { container } = render(<LoginForm />)
      const form = container.querySelector('form')
      
      expect(form).toHaveClass('w-full', 'max-w-md')
    })
  })
})

