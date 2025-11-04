import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useState, useEffect } from 'react'
import { useAuthContext } from '@/contexts/AuthContext'
import { useNavigate, Link } from 'react-router-dom'

const signUpSchema = z
  .object({
    email: z.string().email('Invalid email address'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .regex(/[A-Z]/, 'Password must contain an uppercase letter')
      .regex(/[a-z]/, 'Password must contain a lowercase letter')
      .regex(/[0-9]/, 'Password must contain a digit')
      .regex(/[^A-Za-z0-9]/, 'Password must contain a special character'),
    confirmPassword: z.string(),
  })
  .refine(data => data.password === data.confirmPassword, {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  })

type SignUpFormData = z.infer<typeof signUpSchema>

interface SignUpFormProps {
  onSubmit?: (data: SignUpFormData) => Promise<void> | void
}

type PasswordStrength = 'weak' | 'medium' | 'strong' | 'none'

interface PasswordRequirements {
  length: boolean
  uppercase: boolean
  lowercase: boolean
  digit: boolean
  symbol: boolean
}

function getPasswordStrength(password: string): PasswordStrength {
  if (!password) return 'none'

  const requirements: PasswordRequirements = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    digit: /[0-9]/.test(password),
    symbol: /[^A-Za-z0-9]/.test(password),
  }

  const metCount = Object.values(requirements).filter(Boolean).length

  if (metCount < 3) return 'weak'
  if (metCount < 5) return 'medium'
  return 'strong'
}

function getPasswordRequirements(password: string): PasswordRequirements {
  return {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    digit: /[0-9]/.test(password),
    symbol: /[^A-Za-z0-9]/.test(password),
  }
}

export function SignUpForm({ onSubmit }: SignUpFormProps) {
  const [authError, setAuthError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const { signUp, isLoading: authLoading } = useAuthContext()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setFocus,
    watch,
  } = useForm<SignUpFormData>({
    resolver: zodResolver(signUpSchema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
  })

  const password = watch('password')
  const passwordStrength = password ? getPasswordStrength(password) : 'none'
  const passwordRequirements = password
    ? getPasswordRequirements(password)
    : {
        length: false,
        uppercase: false,
        lowercase: false,
        digit: false,
        symbol: false,
      }

  const isLoading = onSubmit ? isSubmitting : authLoading

  const onSubmitHandler = async (data: SignUpFormData) => {
    setAuthError(null)
    setSuccessMessage(null)
    setIsSubmitting(true)
    try {
      if (onSubmit) {
        await onSubmit(data)
      } else {
        // Use Cognito authentication
        await signUp(data.email, data.password)
        setSuccessMessage('Account created successfully! Redirecting...')
        // Navigate to dashboard on successful sign-up
        setTimeout(() => {
          navigate('/dashboard', { replace: true })
        }, 1000)
      }
    } catch (error) {
      console.error('Sign up error:', error)
      const errorMessage =
        error instanceof Error ? error.message : 'Sign up failed. Please try again.'
      setAuthError(errorMessage)
      // Focus on first error field after submission error
      const firstErrorField = errors.email
        ? 'email'
        : errors.password
          ? 'password'
          : errors.confirmPassword
            ? 'confirmPassword'
            : null
      if (firstErrorField) {
        setFocus(firstErrorField as keyof SignUpFormData)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  // Clear success message after showing
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => {
        setSuccessMessage(null)
      }, 3000)
      return () => clearTimeout(timer)
    }
  }, [successMessage])

  return (
    <form onSubmit={handleSubmit(onSubmitHandler)} noValidate className="space-y-4 w-full max-w-md">
      <div className="space-y-2">
        <label
          htmlFor="email"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Email
        </label>
        <Input
          id="email"
          type="email"
          placeholder="Enter your email"
          {...register('email')}
          disabled={isLoading}
          aria-label="Email address"
          aria-describedby={errors.email ? 'email-error' : undefined}
          aria-invalid={!!errors.email}
          className={errors.email ? 'border-destructive focus-visible:ring-destructive' : ''}
        />
        {errors.email && (
          <p id="email-error" role="alert" className="text-sm text-destructive" aria-live="polite">
            {errors.email.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label
          htmlFor="password"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Password
        </label>
        <Input
          id="password"
          type="password"
          placeholder="Enter your password"
          {...register('password')}
          disabled={isLoading}
          aria-label="Password"
          aria-describedby={errors.password ? 'password-error' : undefined}
          aria-invalid={!!errors.password}
          className={errors.password ? 'border-destructive focus-visible:ring-destructive' : ''}
        />
        {errors.password && (
          <p
            id="password-error"
            role="alert"
            className="text-sm text-destructive"
            aria-live="polite"
          >
            {errors.password.message}
          </p>
        )}

        {/* Password Strength Indicator */}
        {password && passwordStrength !== 'none' && (
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={`h-full transition-all duration-300 ${
                    passwordStrength === 'weak'
                      ? 'bg-destructive w-1/3'
                      : passwordStrength === 'medium'
                        ? 'bg-yellow-500 w-2/3'
                        : 'bg-green-500 w-full'
                  }`}
                  role="progressbar"
                  aria-valuenow={
                    passwordStrength === 'weak' ? 33 : passwordStrength === 'medium' ? 66 : 100
                  }
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`Password strength: ${passwordStrength}`}
                />
              </div>
              <span className="text-xs text-muted-foreground capitalize">{passwordStrength}</span>
            </div>

            {/* Password Requirements */}
            <div className="text-xs text-muted-foreground space-y-0.5">
              <div className={passwordRequirements.length ? 'text-green-600' : ''}>
                {passwordRequirements.length ? '✓' : '○'} At least 8 characters
              </div>
              <div className={passwordRequirements.uppercase ? 'text-green-600' : ''}>
                {passwordRequirements.uppercase ? '✓' : '○'} One uppercase letter
              </div>
              <div className={passwordRequirements.lowercase ? 'text-green-600' : ''}>
                {passwordRequirements.lowercase ? '✓' : '○'} One lowercase letter
              </div>
              <div className={passwordRequirements.digit ? 'text-green-600' : ''}>
                {passwordRequirements.digit ? '✓' : '○'} One digit
              </div>
              <div className={passwordRequirements.symbol ? 'text-green-600' : ''}>
                {passwordRequirements.symbol ? '✓' : '○'} One special character
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-2">
        <label
          htmlFor="confirmPassword"
          className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
        >
          Confirm Password
        </label>
        <Input
          id="confirmPassword"
          type="password"
          placeholder="Confirm your password"
          {...register('confirmPassword')}
          disabled={isLoading}
          aria-label="Confirm password"
          aria-describedby={errors.confirmPassword ? 'confirmPassword-error' : undefined}
          aria-invalid={!!errors.confirmPassword}
          className={
            errors.confirmPassword ? 'border-destructive focus-visible:ring-destructive' : ''
          }
        />
        {errors.confirmPassword && (
          <p
            id="confirmPassword-error"
            role="alert"
            className="text-sm text-destructive"
            aria-live="polite"
          >
            {errors.confirmPassword.message}
          </p>
        )}
      </div>

      {authError && (
        <div
          role="alert"
          className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-md p-3"
          aria-live="polite"
        >
          {authError}
        </div>
      )}

      {successMessage && (
        <div
          role="alert"
          className="text-sm text-green-600 bg-green-50 border border-green-200 rounded-md p-3"
          aria-live="polite"
        >
          {successMessage}
        </div>
      )}

      <Button
        type="submit"
        disabled={isLoading}
        className="w-full"
        aria-label={isLoading ? 'Creating account...' : 'Sign up'}
      >
        {isLoading ? 'Creating account...' : 'Sign up'}
      </Button>

      <div className="text-center text-sm text-muted-foreground">
        Already have an account?{' '}
        <Link
          to="/login"
          className="text-primary hover:underline font-medium"
          aria-label="Sign in to your account"
        >
          Sign in
        </Link>
      </div>
    </form>
  )
}
