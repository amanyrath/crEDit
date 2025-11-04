import { createContext, useContext } from 'react'
import type { ReactNode } from 'react'
import { useAuth, type UseAuthReturn, type AuthUser } from '../hooks/useAuth'

type AuthContextType = UseAuthReturn

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

/**
 * AuthProvider component that wraps the application
 * Provides authentication state and methods to all child components
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const auth = useAuth()

  return <AuthContext.Provider value={auth}>{children}</AuthContext.Provider>
}

/**
 * Hook to access authentication context
 * Must be used within an AuthProvider
 */
export function useAuthContext(): AuthContextType {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }

  return context
}

// Re-export types for convenience
export type { AuthUser }
