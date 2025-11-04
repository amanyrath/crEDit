import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { useState } from "react"
import { useAuthContext } from "@/contexts/AuthContext"
import { useNavigate } from "react-router-dom"

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})

type LoginFormData = z.infer<typeof loginSchema>

interface LoginFormProps {
  onSubmit?: (data: LoginFormData) => Promise<void> | void
}

export function LoginForm({ onSubmit }: LoginFormProps) {
  const [authError, setAuthError] = useState<string | null>(null)
  const { signIn, isLoading: authLoading } = useAuthContext()
  const navigate = useNavigate()

  const {
    register,
    handleSubmit,
    formState: { errors },
    setFocus,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    mode: 'onSubmit',
    reValidateMode: 'onChange',
  })

  const isLoading = authLoading

  const onSubmitHandler = async (data: LoginFormData) => {
    setAuthError(null)
    try {
      if (onSubmit) {
        await onSubmit(data)
      } else {
        // Use Cognito authentication
        await signIn(data.email, data.password)
        // Navigate to dashboard on successful login
        navigate('/dashboard', { replace: true })
      }
    } catch (error) {
      console.error("Login error:", error)
      const errorMessage = error instanceof Error ? error.message : "Login failed. Please try again."
      setAuthError(errorMessage)
      // Focus on first error field after submission error
      const firstErrorField = errors.email ? "email" : errors.password ? "password" : null
      if (firstErrorField) {
        setFocus(firstErrorField as keyof LoginFormData)
      }
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmitHandler)} noValidate className="space-y-4 w-full max-w-md">
      <div className="space-y-2">
        <label htmlFor="email" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Email
        </label>
        <Input
          id="email"
          type="email"
          placeholder="Enter your email"
          {...register("email")}
          disabled={isLoading}
          aria-label="Email address"
          aria-describedby={errors.email ? "email-error" : undefined}
          aria-invalid={!!errors.email}
          className={errors.email ? "border-destructive focus-visible:ring-destructive" : ""}
        />
        {errors.email && (
          <p
            id="email-error"
            role="alert"
            className="text-sm text-destructive"
            aria-live="polite"
          >
            {errors.email.message}
          </p>
        )}
      </div>

      <div className="space-y-2">
        <label htmlFor="password" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
          Password
        </label>
        <Input
          id="password"
          type="password"
          placeholder="Enter your password"
          {...register("password")}
          disabled={isLoading}
          aria-label="Password"
          aria-describedby={errors.password ? "password-error" : undefined}
          aria-invalid={!!errors.password}
          className={errors.password ? "border-destructive focus-visible:ring-destructive" : ""}
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
      <Button
        type="submit"
        disabled={isLoading}
        className="w-full"
        aria-label={isLoading ? "Logging in..." : "Log in"}
      >
        {isLoading ? "Logging in..." : "Log in"}
      </Button>
    </form>
  )
}

