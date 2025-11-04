/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { BrowserRouter } from 'react-router-dom'
import { SignUpForm } from './SignUpForm'
import { AuthProvider } from '@/contexts/AuthContext'
import { signUp, signIn, getCurrentUser, fetchAuthSession } from '@aws-amplify/auth'

// Mock Amplify Auth
vi.mock('@aws-amplify/auth', () => ({
  signUp: vi.fn(),
  signIn: vi.fn(),
  signOut: vi.fn(),
  getCurrentUser: vi.fn(),
  fetchAuthSession: vi.fn(),
}))

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      <AuthProvider>{children}</AuthProvider>
    </BrowserRouter>
  )
}

// Helper to render and wait for form to be ready
const renderSignUpForm = async (props?: {
  onSubmit?: (data: {
    email: string
    password: string
    confirmPassword: string
  }) => Promise<void> | void
}) => {
  const result = render(<SignUpForm {...props} />, { wrapper: TestWrapper })
  await waitFor(
    () => {
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    },
    { timeout: 2000 }
  )
  return result
}

describe('SignUpForm', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Mock getCurrentUser to return "not authenticated" by default
    vi.mocked(getCurrentUser).mockRejectedValue(new Error('Not authenticated'))
    vi.mocked(fetchAuthSession).mockResolvedValue({ tokens: null } as any)
  })

  describe('Form Rendering', () => {
    it('renders email, password, and confirm password input fields', async () => {
      await renderSignUpForm()

      expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/confirm your password/i)).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument()
    })

    it('renders with proper labels', async () => {
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)

      expect(emailInput).toHaveAttribute('type', 'email')
      expect(passwordInput).toHaveAttribute('type', 'password')
      expect(confirmPasswordInput).toHaveAttribute('type', 'password')
    })

    it('renders with placeholder text', async () => {
      await renderSignUpForm()

      expect(screen.getByPlaceholderText(/enter your email/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/enter your password/i)).toBeInTheDocument()
      expect(screen.getByPlaceholderText(/confirm your password/i)).toBeInTheDocument()
    })

    it('renders link to login page', async () => {
      await renderSignUpForm()

      const signInLink = screen.getByRole('link', { name: /sign in/i })
      expect(signInLink).toBeInTheDocument()
      expect(signInLink).toHaveAttribute('href', '/login')
    })
  })

  describe('Email Validation', () => {
    it('displays error for invalid email format', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'invalid-email')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
        },
        { timeout: 3000 }
      )
    })

    it('displays error for empty email', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const submitButton = screen.getByRole('button', { name: /sign up/i })
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
      })
    })

    it('accepts valid email format', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'Password123!',
          confirmPassword: 'Password123!',
        })
      })

      expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument()
    })
  })

  describe('Password Validation', () => {
    it('displays error for empty password', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
      })
    })

    it('displays error for password too short', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Short1!')
      await user.type(confirmPasswordInput, 'Short1!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
      })
    })

    it('displays error for password missing uppercase', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'password123!')
      await user.type(confirmPasswordInput, 'password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must contain an uppercase letter/i)).toBeInTheDocument()
      })
    })

    it('displays error for password missing lowercase', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'PASSWORD123!')
      await user.type(confirmPasswordInput, 'PASSWORD123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must contain a lowercase letter/i)).toBeInTheDocument()
      })
    })

    it('displays error for password missing digit', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password!')
      await user.type(confirmPasswordInput, 'Password!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must contain a digit/i)).toBeInTheDocument()
      })
    })

    it('displays error for password missing special character', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123')
      await user.type(confirmPasswordInput, 'Password123')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/password must contain a special character/i)).toBeInTheDocument()
      })
    })

    it('accepts password meeting all requirements', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })

      expect(screen.queryByText(/password must/i)).not.toBeInTheDocument()
    })
  })

  describe('Confirm Password Validation', () => {
    it('displays error when passwords do not match', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Different123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument()
      })
    })

    it('accepts matching passwords', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })

      expect(screen.queryByText(/passwords do not match/i)).not.toBeInTheDocument()
    })
  })

  describe('Password Strength Indicator', () => {
    it('shows password strength indicator when password is entered', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const passwordInput = screen.getByPlaceholderText(/enter your password/i)

      await user.type(passwordInput, 'P')

      await waitFor(() => {
        expect(screen.getByText(/weak/i)).toBeInTheDocument()
      })
    })

    it('shows weak strength for passwords with less than 3 requirements', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const passwordInput = screen.getByPlaceholderText(/enter your password/i)

      await user.type(passwordInput, 'Short')

      await waitFor(() => {
        expect(screen.getByText(/weak/i)).toBeInTheDocument()
      })
    })

    it('shows medium strength for passwords with 3-4 requirements', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const passwordInput = screen.getByPlaceholderText(/enter your password/i)

      await user.type(passwordInput, 'Password1')

      await waitFor(() => {
        expect(screen.getByText(/medium/i)).toBeInTheDocument()
      })
    })

    it('shows strong strength for passwords meeting all requirements', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const passwordInput = screen.getByPlaceholderText(/enter your password/i)

      await user.type(passwordInput, 'Password123!')

      await waitFor(() => {
        expect(screen.getByText(/strong/i)).toBeInTheDocument()
      })
    })

    it('displays password requirements checklist', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const passwordInput = screen.getByPlaceholderText(/enter your password/i)

      await user.type(passwordInput, 'Password123!')

      await waitFor(() => {
        expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument()
        expect(screen.getByText(/one uppercase letter/i)).toBeInTheDocument()
        expect(screen.getByText(/one lowercase letter/i)).toBeInTheDocument()
        expect(screen.getByText(/one digit/i)).toBeInTheDocument()
        expect(screen.getByText(/one special character/i)).toBeInTheDocument()
      })
    })

    it('updates requirements checklist in real-time', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const passwordInput = screen.getByPlaceholderText(/enter your password/i)

      await user.type(passwordInput, 'P')

      await waitFor(() => {
        // Should show requirements with mostly unchecked
        expect(screen.getByText(/at least 8 characters/i)).toBeInTheDocument()
      })

      await user.type(passwordInput, 'assword123!')

      await waitFor(() => {
        // Should show strong password with all requirements met
        expect(screen.getByText(/strong/i)).toBeInTheDocument()
      })
    })
  })

  describe('Error Message Display', () => {
    it('displays error messages with proper ARIA attributes', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'invalid')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          const errorMessage = screen.getByText(/invalid email address/i)
          expect(errorMessage).toBeInTheDocument()
          expect(errorMessage).toHaveAttribute('role', 'alert')
          expect(errorMessage).toHaveAttribute('id', 'email-error')
        },
        { timeout: 3000 }
      )

      const emailInputAfterError = screen.getByLabelText(/email/i)
      expect(emailInputAfterError).toHaveAttribute('aria-describedby', 'email-error')
      expect(emailInputAfterError).toHaveAttribute('aria-invalid', 'true')
    })

    it('clears errors when user starts typing', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'invalid')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
        },
        { timeout: 3000 }
      )

      await user.clear(emailInput)
      await user.type(emailInput, 'test@example.com')

      await waitFor(
        () => {
          expect(screen.queryByText(/invalid email address/i)).not.toBeInTheDocument()
        },
        { timeout: 3000 }
      )
    })
  })

  describe('Loading State', () => {
    it('shows loading state during form submission', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn(async () => {
        await new Promise<void>(resolve => setTimeout(resolve, 100))
      })
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      expect(screen.getByRole('button', { name: /creating account/i })).toBeInTheDocument()
      expect(submitButton).toBeDisabled()
      expect(emailInput).toBeDisabled()
      expect(passwordInput).toBeDisabled()
      expect(confirmPasswordInput).toBeDisabled()

      await waitFor(
        () => {
          expect(screen.getByRole('button', { name: /sign up/i })).toBeInTheDocument()
        },
        { timeout: 200 }
      )
    })

    it('prevents multiple submissions while loading', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn(async () => {
        await new Promise<void>(resolve => setTimeout(resolve, 100))
      })
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
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
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'Password123!',
          confirmPassword: 'Password123!',
        })
      })
    })

    it('handles submission without onSubmit prop', async () => {
      const user = userEvent.setup()

      // Mock successful sign up and sign in
      vi.mocked(signUp).mockResolvedValue({
        isSignUpComplete: true,
        nextStep: { signUpStep: 'DONE' },
      } as any)

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

      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          expect(signUp).toHaveBeenCalledWith({
            username: 'test@example.com',
            password: 'Password123!',
            options: {
              userAttributes: {
                email: 'test@example.com',
              },
            },
          })
        },
        { timeout: 3000 }
      )
    })

    it('displays success message after successful sign-up', async () => {
      const user = userEvent.setup()

      // Mock successful sign up and sign in
      vi.mocked(signUp).mockResolvedValue({
        isSignUpComplete: true,
        nextStep: { signUpStep: 'DONE' },
      } as any)

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

      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          expect(screen.getByText(/account created successfully/i)).toBeInTheDocument()
        },
        { timeout: 3000 }
      )
    })

    it('handles sign-up errors and displays error messages', async () => {
      const user = userEvent.setup()

      // Mock sign up error
      const error = new Error('Username exists')
      error.name = 'UsernameExistsException'
      vi.mocked(signUp).mockRejectedValue(error)

      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          expect(screen.getByText(/account with this email already exists/i)).toBeInTheDocument()
        },
        { timeout: 3000 }
      )
    })
  })

  describe('Accessibility Features', () => {
    it('supports keyboard navigation', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      emailInput.focus()
      expect(emailInput).toHaveFocus()

      await user.tab()
      expect(passwordInput).toHaveFocus()

      await user.tab()
      expect(confirmPasswordInput).toHaveFocus()

      await user.tab()
      expect(submitButton).toHaveFocus()
    })

    it('submits form on Enter key press', async () => {
      const user = userEvent.setup()
      const onSubmit = vi.fn()
      await renderSignUpForm({ onSubmit })

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)

      await user.type(emailInput, 'test@example.com')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.keyboard('{Enter}')

      await waitFor(() => {
        expect(onSubmit).toHaveBeenCalled()
      })
    })

    it('has proper ARIA labels for screen readers', async () => {
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      expect(emailInput).toHaveAttribute('aria-label', 'Email address')
      expect(passwordInput).toHaveAttribute('aria-label', 'Password')
      expect(confirmPasswordInput).toHaveAttribute('aria-label', 'Confirm password')
      expect(submitButton).toHaveAttribute('aria-label', 'Sign up')
    })

    it('has proper ARIA attributes for error states', async () => {
      const user = userEvent.setup()
      await renderSignUpForm()

      const emailInput = screen.getByLabelText(/email/i)
      const passwordInput = screen.getByPlaceholderText(/enter your password/i)
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm your password/i)
      const submitButton = screen.getByRole('button', { name: /sign up/i })

      await user.type(emailInput, 'invalid')
      await user.type(passwordInput, 'Password123!')
      await user.type(confirmPasswordInput, 'Password123!')
      await user.click(submitButton)

      await waitFor(
        () => {
          expect(screen.getByText(/invalid email address/i)).toBeInTheDocument()
        },
        { timeout: 3000 }
      )

      const emailInputAfterError = screen.getByLabelText(/email/i)
      expect(emailInputAfterError).toHaveAttribute('aria-invalid', 'true')
      expect(emailInputAfterError).toHaveAttribute('aria-describedby', 'email-error')
      const errorMessage = screen.getByText(/invalid email address/i)
      expect(errorMessage).toHaveAttribute('aria-live', 'polite')
    })
  })

  describe('Responsive Design', () => {
    it('has responsive width classes', async () => {
      const { container } = await renderSignUpForm()
      const form = container.querySelector('form')

      expect(form).toHaveClass('w-full', 'max-w-md')
    })
  })
})
