import { SignUpForm } from '@/components/SignUpForm'
import { useAuthContext } from '@/contexts/AuthContext'
import { Navigate, useLocation } from 'react-router-dom'

/**
 * Sign up page component
 * Redirects to dashboard if user is already authenticated
 */
export function SignUpPage() {
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
          <p className="text-muted-foreground">Create your account</p>
        </div>
        <SignUpForm />
      </div>
    </div>
  )
}


