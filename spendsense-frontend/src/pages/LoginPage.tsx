import { LoginForm } from '@/components/LoginForm'
import { useAuthContext } from '@/contexts/AuthContext'
import { Navigate, useLocation, Link } from 'react-router-dom'

/**
 * Login page component
 * Redirects to dashboard if user is already authenticated
 */
export function LoginPage() {
  const { isAuthenticated, isLoading } = useAuthContext()
  const location = useLocation()

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    )
  }

  // Redirect to dashboard if already authenticated
  // Use the 'from' location if available (from protected route redirect)
  const from = (location.state as { from?: Location })?.from?.pathname || '/dashboard'
  if (isAuthenticated) {
    return <Navigate to={from} replace />
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-8">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">SpendSense</h1>
          <p className="text-muted-foreground">Sign in to your account</p>
        </div>
        <LoginForm />
        <div className="text-center mt-4 text-sm text-muted-foreground">
          Don't have an account?{' '}
          <Link
            to="/signup"
            className="text-primary hover:underline font-medium"
            aria-label="Create a new account"
          >
            Sign up
          </Link>
        </div>
      </div>
    </div>
  )
}
