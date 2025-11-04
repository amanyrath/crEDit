import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { LoginForm } from './LoginForm'
import { AuthProvider } from '@/contexts/AuthContext'
import { signIn, getCurrentUser, fetchAuthSession } from '@aws-amplify/auth'

// Mock Amplify Auth
vi.mock('@aws-amplify/auth', () => ({
  signIn: vi.fn(),
  signOut: vi.fn(),
  getCurrentUser: vi.fn(),
  fetchAuthSession: vi.fn(),
}))

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      <AuthProvider>
        {children}
      </AuthProvider>
    </BrowserRouter>
  )
}

// Helper to render and wait for form to be ready
const renderLoginForm = async (props?: { onSubmit?: (data: { email: string; password: string }) => Promise<void> | void }) => {
  const result = render(<LoginForm {...props} />, { wrapper: TestWrapper })
  await waitFor(() => {
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
  }, { timeout: 2000 })
  return result
}

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock getCurrentUser to return "not authenticated" by default
    vi.mocked(getCurrentUser).mockRejectedValue(new Error('Not authenticated'))
    vi.mocked(fetchAuthSession).mockResolvedValue({ tokens: null } as any)
  })

  describe('Form Rendering', () => {
    it('renders email and password input fields', async () => {
      await renderLoginForm()
      
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /log in/i })).toBeInTheDocument()
    })

    it('renders with proper labels', async () => {
      await renderLoginForm()
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      expect(emailInput).toHaveAttribute('type', 'email')
      expect(passwordInput).toHaveAttribute('type', 'password')
    })

    it('renders with placeholder text', async () => {
      await renderLoginForm()
      
      expect(screen.getByPlaceholderText(/enter your email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
    })
  })

  describe('Email Validation', () => {
    it('displays error for invalid email format', async () => {
      const user = userEvent.setup()
      await renderLoginForm()
      
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
      await renderLoginForm()
      
      const submitButton = screen.getByRole('button', { name: /log in/i })
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      })
    })

    it('accepts valid email format', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      await renderLoginForm({ onSubmit })
      
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
      await renderLoginForm()
      
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
      await renderLoginForm({ onSubmit })
      
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
      await renderLoginForm()
      
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
      await renderLoginForm()
      
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
      await renderLoginForm({ onSubmit })
      
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
      await renderLoginForm({ onSubmit })
      
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
      await renderLoginForm({ onSubmit })
      
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
      
      // Mock successful sign in
      vi.mocked(signIn).mockResolvedValue({
        isSignedIn: true,
        nextStep: { signInStep: 'DONE' },
      } as any)
      
      vi.mocked(getCurrentUser).mockResolvedValue({
        username: 'test@example.com',
        userId: 'user-123',
      } as any)
      vi.mocked(fetchAuthSession).mockResolvedValue({
        tokens: {
          idToken: {
            payload: {
              sub: 'user-123',
              email: 'test@example.com',
            },
          },
        },
      } as any)
      
      await renderLoginForm()
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.click(submitButton)
      
      await waitFor(() => {
        expect(signIn).toHaveBeenCalledWith({
          username: 'test@example.com',
          password: 'password123',
        })
      }, { timeout: 3000 })
    })
  })

  describe('Accessibility Features', () => {
    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      await renderLoginForm()
      
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
      await renderLoginForm({ onSubmit })
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      
      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123')
      await user.keyboard('{Enter}')
      
      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })
    })

    it('has proper ARIA labels for screen readers', async () => {
      await renderLoginForm()
      
      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByLabelText(/password/i)
      const submitButton = screen.getByRole('button', { name: /log in/i })
      
      expect(emailInput).toHaveAttribute('aria-label', 'Email address')
      expect(passwordInput).toHaveAttribute('aria-label', 'Password')
      expect(submitButton).toHaveAttribute('aria-label', 'Log in')
    })

    it('has proper ARIA attributes for error states', async () => {
      const user = userEvent.setup()
      await renderLoginForm()
      
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
    it('has responsive width classes', async () => {
      const { container } = await renderLoginForm()
      const form = container.querySelector('form')
      
      expect(form).toHaveClass('w-full', 'max-w-md')
    })
  })
})
