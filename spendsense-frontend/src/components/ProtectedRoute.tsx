import { Navigate, useLocation } from 'react-router-dom'
import { useAuthContext } from '@/contexts/AuthContext'
import type { ReactNode } from 'react'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: 'consumer' | 'operator'
}

/**
 * ProtectedRoute component that checks authentication and optionally role before rendering children
 * Redirects to login page if user is not authenticated
 * Redirects to dashboard if user lacks required role
 * Preserves the intended destination for redirect after login
 */
export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, user } = useAuthContext()
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

  // Redirect to login if not authenticated
  // Preserve the location they were trying to access
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Check role if required
  if (requiredRole && user?.role !== requiredRole) {
    // Redirect to dashboard if user doesn't have required role
    return (
      <Navigate
        to="/dashboard"
        state={{
          error: `You don't have permission to access this page. Required role: ${requiredRole}`,
        }}
        replace
      />
    )
  }

  return <>{children}</>
}
