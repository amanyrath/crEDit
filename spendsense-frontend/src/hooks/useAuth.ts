import { useState, useEffect, useCallback, useRef } from 'react'
import { signIn, signOut, signUp, getCurrentUser, fetchAuthSession } from '@aws-amplify/auth'
import type { SignInOutput, SignUpOutput } from '@aws-amplify/auth'
import { useNavigate } from 'react-router-dom'

export interface AuthUser {
  username: string
  email?: string
  sub: string
  role?: string
}

export interface UseAuthReturn {
  user: AuthUser | null
  isAuthenticated: boolean
  isLoading: boolean
  error: Error | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string) => Promise<void>
  signOut: () => Promise<void>
  getCurrentSession: () => Promise<{ tokens: { accessToken: { toString: () => string } } } | null>
  refreshSession: () => Promise<void>
}

/**
 * Custom hook for authentication state and operations
 * Manages user authentication state, sign in, sign out, and token management
 */
// Storage event keys for cross-tab synchronization
const AUTH_STORAGE_KEY = 'spendsense_auth_state'
const AUTH_LOGOUT_EVENT = 'spendsense_auth_logout'
const AUTH_LOGIN_EVENT = 'spendsense_auth_login'

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<AuthUser | null>(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)
  const refreshTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const navigate = useNavigate()

  /**
   * Get token expiration time in milliseconds
   */
  const getTokenExpirationTime = useCallback((token: { payload?: { exp?: number } }): number | null => {
    if (!token.payload?.exp) return null
    // exp is in seconds, convert to milliseconds
    return token.payload.exp * 1000
  }, [])

  /**
   * Check if token needs refresh (within 5 minutes of expiration)
   */
  const shouldRefreshToken = useCallback((expirationTime: number | null): boolean => {
    if (!expirationTime) return false
    const now = Date.now()
    const fiveMinutes = 5 * 60 * 1000 // 5 minutes in milliseconds
    return expirationTime - now < fiveMinutes
  }, [])

  /**
   * Extract role from token claims
   * Priority: cognito:groups claim (operators > consumers) > custom:role > default "consumer"
   */
  const extractRoleFromClaims = (claims: Record<string, unknown>): string => {
    // Check cognito:groups claim (primary method)
    const groups = claims['cognito:groups'] as string[] | undefined
    if (Array.isArray(groups)) {
      if (groups.includes('operators')) {
        return 'operator'
      }
      if (groups.includes('consumers')) {
        return 'consumer'
      }
    }
    
    // Fallback to custom:role claim
    const customRole = claims['custom:role'] as string | undefined
    if (customRole && (customRole === 'consumer' || customRole === 'operator')) {
      return customRole
    }
    
    // Default to consumer
    return 'consumer'
  }

  /**
   * Get current session and update user state
   */
  const getCurrentSession = useCallback(async () => {
    try {
      // Get current user to check if authenticated
      const currentUser = await getCurrentUser()
      
      // Fetch auth session to get tokens (without force refresh to check expiration)
      const session = await fetchAuthSession({ forceRefresh: false })
      
      if (session.tokens && session.tokens.idToken && session.tokens.accessToken) {
        const payload = session.tokens.idToken.payload as unknown as { 
          email?: string
          sub: string
          'cognito:groups'?: string[]
          'custom:role'?: string
          [key: string]: unknown 
        }
        
        // Extract role from access token (access token has groups claim)
        let role = 'consumer'
        if (session.tokens.accessToken) {
          try {
            // Decode access token to get groups claim
            const accessTokenPayload = session.tokens.accessToken.payload as Record<string, unknown>
            role = extractRoleFromClaims(accessTokenPayload)
          } catch {
            // If access token parsing fails, try ID token
            role = extractRoleFromClaims(payload)
          }
        } else {
          // Fallback to ID token
          role = extractRoleFromClaims(payload)
        }
        
        const authUser: AuthUser = {
          username: currentUser.username || payload.email || payload.sub,
          email: payload.email,
          sub: payload.sub,
          role,
        }
        setUser(authUser)
        setIsAuthenticated(true)
        setError(null)
        
        // Notify other tabs of login
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ authenticated: true, timestamp: Date.now() }))
        window.dispatchEvent(new CustomEvent(AUTH_LOGIN_EVENT))
        
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
   * Refresh the current session using refresh token
   * This is called automatically before token expiration
   */
  const refreshSession = useCallback(async () => {
    try {
      // Force refresh to use refresh token
      const session = await fetchAuthSession({ forceRefresh: true })
      
      if (session.tokens && session.tokens.idToken) {
        const currentUser = await getCurrentUser()
        const payload = session.tokens.idToken.payload as unknown as { 
          email?: string
          sub: string
          'cognito:groups'?: string[]
          'custom:role'?: string
          [key: string]: unknown 
        }
        
        // Extract role from tokens
        let role = 'consumer'
        if (session.tokens.accessToken) {
          try {
            const accessTokenPayload = session.tokens.accessToken.payload as Record<string, unknown>
            role = extractRoleFromClaims(accessTokenPayload)
          } catch {
            role = extractRoleFromClaims(payload)
          }
        } else {
          role = extractRoleFromClaims(payload)
        }
        
        const authUser: AuthUser = {
          username: currentUser.username || payload.email || payload.sub,
          email: payload.email,
          sub: payload.sub,
          role,
        }
        setUser(authUser)
        setIsAuthenticated(true)
        setError(null)
        
        // Notify other tabs of refreshed session
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify({ authenticated: true, timestamp: Date.now() }))
        
        return true
      }
      
      // Session refresh failed - might be expired refresh token
      throw new Error('Failed to refresh session')
    } catch (err) {
      // Check if it's a refresh token expiration error
      const error = err instanceof Error ? err : new Error('Failed to refresh session')
      
      // Common Amplify errors for expired refresh token
      if (error.message.includes('refresh') || error.message.includes('expired') || error.message.includes('NotAuthorizedException')) {
        // Refresh token expired - clear session and redirect to login
        setUser(null)
        setIsAuthenticated(false)
        setError(null)
        localStorage.removeItem(AUTH_STORAGE_KEY)
        window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT))
        
        // Redirect to login if we're not already there
        if (window.location.pathname !== '/login') {
          navigate('/login', { replace: true })
        }
        
        return false
      }
      
      setError(error)
      setUser(null)
      setIsAuthenticated(false)
      return false
    }
  }, [navigate])

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
   * Sign up with email and password
   * After successful sign-up, automatically signs in the user
   */
  const signUpUser = useCallback(async (email: string, password: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const output: SignUpOutput = await signUp({
        username: email,
        password,
        options: {
          userAttributes: {
            email,
          },
        },
      })

      // If sign-up is successful and email verification is disabled,
      // automatically sign in the user
      if (output.isSignUpComplete) {
        // Sign in the user automatically
        await signInUser(email, password)
      } else {
        // User needs to complete sign-up flow (e.g., email verification)
        throw new Error('Sign up requires additional steps')
      }
    } catch (err: unknown) {
      const error = err instanceof Error ? err : new Error('Sign up failed')
      
      // Map Amplify errors to user-friendly messages
      if (err && typeof err === 'object' && 'name' in err) {
        if (err.name === 'UsernameExistsException') {
          error.message = 'An account with this email already exists'
        } else if (err.name === 'InvalidPasswordException') {
          error.message = 'Password does not meet requirements'
        } else if (err.name === 'InvalidParameterException') {
          error.message = 'Invalid email address'
        } else if (err.name === 'TooManyRequestsException') {
          error.message = 'Too many sign-up attempts. Please try again later'
        }
      }
      
      setError(error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [signInUser])

  /**
   * Sign out current user and clear session
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
      
      // Clear auth state and notify other tabs
      localStorage.removeItem(AUTH_STORAGE_KEY)
      window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT))
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Sign out failed')
      setError(error)
      // Still clear local state even if sign out fails
      setUser(null)
      setIsAuthenticated(false)
      
      // Still notify other tabs
      localStorage.removeItem(AUTH_STORAGE_KEY)
      window.dispatchEvent(new CustomEvent(AUTH_LOGOUT_EVENT))
      
      throw error
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Schedule token refresh based on actual expiration time
   */
  const scheduleTokenRefresh = useCallback(async () => {
    // Clear any existing timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current)
      refreshTimeoutRef.current = null
    }

    if (!isAuthenticated) return

    try {
      // Get current session to check expiration
      const session = await fetchAuthSession({ forceRefresh: false })
      
      if (session.tokens?.accessToken) {
        const expirationTime = getTokenExpirationTime(session.tokens.accessToken as { payload?: { exp?: number } })
        
        if (expirationTime) {
          if (shouldRefreshToken(expirationTime)) {
            // Token needs refresh now
            const refreshed = await refreshSession()
            if (refreshed) {
              // Schedule next refresh check recursively
              setTimeout(() => scheduleTokenRefresh(), 1000)
            }
          } else {
            // Calculate time until refresh is needed (5 minutes before expiration)
            const now = Date.now()
            const fiveMinutes = 5 * 60 * 1000
            const refreshTime = expirationTime - now - fiveMinutes
            
            if (refreshTime > 0) {
              refreshTimeoutRef.current = setTimeout(async () => {
                const refreshed = await refreshSession()
                if (refreshed) {
                  // Schedule next refresh check recursively
                  setTimeout(() => scheduleTokenRefresh(), 1000)
                }
              }, refreshTime)
            } else {
              // Token expires very soon, refresh immediately
              const refreshed = await refreshSession()
              if (refreshed) {
                setTimeout(() => scheduleTokenRefresh(), 1000)
              }
            }
          }
        }
      }
    } catch (err) {
      // Session check failed, might be expired
      console.error('Failed to schedule token refresh:', err)
    }
  }, [isAuthenticated, getTokenExpirationTime, shouldRefreshToken, refreshSession])

  // Initialize: Check for existing session on mount
  useEffect(() => {
    let mounted = true
    
    const initAuth = async () => {
      try {
        await getCurrentSession()
        if (mounted) {
          await scheduleTokenRefresh()
        }
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
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current)
      }
    }
  }, [getCurrentSession, scheduleTokenRefresh])

  // Schedule token refresh when authentication state changes
  useEffect(() => {
    if (isAuthenticated) {
      scheduleTokenRefresh()
    } else {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current)
        refreshTimeoutRef.current = null
      }
    }
  }, [isAuthenticated, scheduleTokenRefresh])

  // Cross-tab synchronization: Listen for storage events
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      // Handle localStorage changes from other tabs
      if (e.key === AUTH_STORAGE_KEY) {
        if (e.newValue === null) {
          // Auth state cleared in another tab (logout)
          setUser(null)
          setIsAuthenticated(false)
        } else {
          // Auth state updated in another tab (login)
          // Re-check session to sync state
          getCurrentSession().catch(() => {
            // Ignore errors during sync
          })
        }
      }
    }

    const handleCustomLogout = () => {
      // Handle custom logout event from other tabs
      setUser(null)
      setIsAuthenticated(false)
    }

    const handleCustomLogin = () => {
      // Handle custom login event from other tabs
      getCurrentSession().catch(() => {
        // Ignore errors during sync
      })
    }

    window.addEventListener('storage', handleStorageChange)
    window.addEventListener(AUTH_LOGOUT_EVENT, handleCustomLogout)
    window.addEventListener(AUTH_LOGIN_EVENT, handleCustomLogin)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener(AUTH_LOGOUT_EVENT, handleCustomLogout)
      window.removeEventListener(AUTH_LOGIN_EVENT, handleCustomLogin)
    }
  }, [getCurrentSession])

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    signIn: signInUser,
    signUp: signUpUser,
    signOut: signOutUser,
    getCurrentSession,
    refreshSession,
  }
}

