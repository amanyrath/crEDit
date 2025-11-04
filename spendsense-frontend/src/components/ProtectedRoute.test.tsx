/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { ProtectedRoute } from './ProtectedRoute'
import { AuthProvider } from '@/contexts/AuthContext'

// Mock useAuth hook
vi.mock('@/contexts/AuthContext', async () => {
  const actual = await vi.importActual('@/contexts/AuthContext')
  return {
    ...actual,
    useAuthContext: vi.fn(),
  }
})

const { useAuthContext } = await import('@/contexts/AuthContext')

describe('ProtectedRoute', () => {
  const renderProtectedRoute = (isAuthenticated: boolean, isLoading: boolean) => {
    vi.mocked(useAuthContext).mockReturnValue({
      isAuthenticated,
      isLoading,
      user: isAuthenticated ? { username: 'test@example.com', sub: 'user-123' } : null,
      error: null,
      signIn: vi.fn(),
      signOut: vi.fn(),
      getCurrentSession: vi.fn(),
      refreshSession: vi.fn(),
    } as any)

    return render(
      <BrowserRouter>
        <AuthProvider>
          <ProtectedRoute>
            <div>Protected Content</div>
          </ProtectedRoute>
        </AuthProvider>
      </BrowserRouter>
    )
  }

  it('should render protected content when authenticated', () => {
    renderProtectedRoute(true, false)
    expect(screen.getByText('Protected Content')).toBeInTheDocument()
  })

  it('should redirect to login when not authenticated', () => {
    renderProtectedRoute(false, false)
    // Should redirect, so protected content should not be visible
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })

  it('should show loading state while checking authentication', () => {
    renderProtectedRoute(false, true)
    expect(screen.getByText('Loading...')).toBeInTheDocument()
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument()
  })
})
