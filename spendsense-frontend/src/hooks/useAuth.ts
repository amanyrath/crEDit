import { useState, useEffect, useCallback } from 'react'
import { signIn, signOut, getCurrentUser, fetchAuthSession } from '@aws-amplify/auth'
import type { SignInOutput } from '@aws-amplify/auth'

export interface AuthUser {
  username: string
  email?: string
  sub: string
}

export interface UseAuthReturn {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: Error | null
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  getCurrentSession: () => Promise<{ tokens: { accessToken: { toString: () => string } } } | null>
  refreshSession: () => Promise<void>
}

/**
 * Custom hook for authentication state and operations
 * Manages user authentication state, sign in, sign out, and token management
 */
export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  /**
   * Get current session and update user state
   */
  const getCurrentSession = useCallback(async () => {
    try {
      // Get current user to check if authenticated
      const currentUser = await getCurrentUser()
      
      // Fetch auth session to get tokens
      const session = await fetchAuthSession()
      
      if (session.tokens && session.tokens.idToken) {
        const payload = session.tokens.idToken.payload as unknown as { email?: string; sub: string; [key: string]: unknown }
        const authUser: AuthUser = {
          username: currentUser.username || payload.email || payload.sub,
          email: payload.email,
          sub: payload.sub,
        }
        setUser(authUser)
        setIsAuthenticated(true)
        setError(null)
        return { tokens: { accessToken: { toString: () => session.tokens?.accessToken?.toString() || '' } } }
      }
      
      setUser(null)
      setIsAuthenticated(false)
      return null
    } catch (err) {
      // No active session
      setUser(null)
      setIsAuthenticated(false)
      return null
    }
  }, [])

  /**
   * Refresh the current session
   */
  const refreshSession = useCallback(async () => {
    try {
      await getCurrentSession()
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to refresh session')
      setError(error)
      setUser(null)
      setIsAuthenticated(false)
    }
  }, [getCurrentSession])

  /**
   * Sign in with email and password
   */
  const signInUser = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const output: SignInOutput = await signIn({
        username: email,
        password,
      })

      // Check if user needs to complete sign in (e.g., MFA, new password)
      if (output.isSignedIn) {
        await getCurrentSession()
      } else {
        // User needs to complete sign in flow
        throw new Error('Sign in requires additional steps')
      }
    } catch (err: unknown) {
      const error = err instanceof Error ? err : new Error('Authentication failed')
      
      // Map Amplify errors to user-friendly messages
      if (err && typeof err === 'object' && 'name' in err) {
        if (err.name === 'NotAuthorizedException') {
          error.message = 'Incorrect email or password'
        } else if (err.name === 'UserNotFoundException') {
          error.message = 'User not found'
        } else if (err.name === 'UserNotConfirmedException') {
          error.message = 'Please confirm your email address'
        } else if (err.name === 'TooManyRequestsException') {
          error.message = 'Too many login attempts. Please try again later'
        }
      }
      
      setError(error)
      setUser(null)
      setIsAuthenticated(false)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [getCurrentSession])

  /**
   * Sign out current user
   */
  const signOutUser = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      await signOut()
      setUser(null)
      setIsAuthenticated(false)
      
      // Clear any stored tokens
      localStorage.removeItem('cognito_access_token')
      localStorage.removeItem('cognito_id_token')
      localStorage.removeItem('cognito_refresh_token')
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Sign out failed')
      setError(error)
      // Still clear local state even if sign out fails
      setUser(null)
      setIsAuthenticated(false)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Initialize: Check for existing session on mount
  useEffect(() => {
    let mounted = true
    
    const initAuth = async () => {
      try {
        await getCurrentSession()
      } catch (err) {
        // No active session is not an error
        if (mounted) {
          setUser(null)
          setIsAuthenticated(false)
        }
      } finally {
        if (mounted) {
          setIsLoading(false)
        }
      }
    }
    
    initAuth()
    
    return () => {
      mounted = false
    }
  }, [getCurrentSession])

  // Set up token refresh interval (refresh 5 minutes before expiration)
  useEffect(() => {
    if (!isAuthenticated) return

    const refreshInterval = setInterval(async () => {
      try {
        await refreshSession()
      } catch (err) {
        console.error('Failed to refresh session:', err)
      }
    }, 50 * 60 * 1000) // Refresh every 50 minutes (tokens typically expire in 1 hour)

    return () => clearInterval(refreshInterval)
  }, [isAuthenticated, refreshSession])

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    signIn: signInUser,
    signOut: signOutUser,
    getCurrentSession,
    refreshSession,
  }
}

