import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { signIn, signOut, getCurrentUser, fetchAuthSession } from '@aws-amplify/auth'
import { useAuth } from './useAuth'
import { BrowserRouter } from 'react-router-dom'

// Mock Amplify Auth functions
vi.mock('@aws-amplify/auth', () => ({
  signIn: vi.fn(),
  signOut: vi.fn(),
  getCurrentUser: vi.fn(),
  fetchAuthSession: vi.fn(),
}))

// Mock react-router-dom
const mockNavigate = vi.fn()
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

// Helper to wrap hook with Router
const wrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>{children}</BrowserRouter>
)

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Clear localStorage manually
    try {
      localStorage.removeItem('spendsense_auth_state')
      localStorage.removeItem('cognito_access_token')
      localStorage.removeItem('cognito_id_token')
      localStorage.removeItem('cognito_refresh_token')
    } catch (e) {
      // Ignore if localStorage is not available
    }
    mockNavigate.mockClear()
  })

  it('should initialize with no authenticated user', async () => {
    vi.mocked(getCurrentUser).mockRejectedValue(new Error('Not authenticated'))
    vi.mocked(fetchAuthSession).mockResolvedValue({
      tokens: null,
    } as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })

  it('should sign in user successfully', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600, // 1 hour from now
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)
    vi.mocked(signIn).mockResolvedValue({
      isSignedIn: true,
      nextStep: { signInStep: 'DONE' },
    } as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.signIn('test@example.com', 'password123')
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    expect(result.current.user).toBeDefined()
    expect(result.current.user?.email).toBe('test@example.com')
    expect(signIn).toHaveBeenCalledWith({
      username: 'test@example.com',
      password: 'password123',
    })
    expect(localStorage.getItem('spendsense_auth_state')).toBeTruthy()
  })

  it('should handle sign in error - wrong password', async () => {
    const error = new Error('NotAuthorizedException')
    ;(error as any).name = 'NotAuthorizedException'
    vi.mocked(signIn).mockRejectedValue(error)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await expect(
        result.current.signIn('test@example.com', 'wrongpassword')
      ).rejects.toThrow('Incorrect email or password')
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.error?.message).toBe('Incorrect email or password')
  })

  it('should handle sign in error - user not found', async () => {
    const error = new Error('UserNotFoundException')
    ;(error as any).name = 'UserNotFoundException'
    vi.mocked(signIn).mockRejectedValue(error)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await expect(
        result.current.signIn('notfound@example.com', 'password123')
      ).rejects.toThrow('User not found')
    })

    expect(result.current.error?.message).toBe('User not found')
  })

  it('should sign out user successfully and clear tokens', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)
    vi.mocked(signOut).mockResolvedValue({} as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    // First sign in
    vi.mocked(signIn).mockResolvedValue({
      isSignedIn: true,
      nextStep: { signInStep: 'DONE' },
    } as any)

    await act(async () => {
      await result.current.signIn('test@example.com', 'password123')
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    // Then sign out
    await act(async () => {
      await result.current.signOut()
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(false)
    })

    expect(result.current.user).toBeNull()
    expect(signOut).toHaveBeenCalled()
    expect(localStorage.getItem('spendsense_auth_state')).toBeNull()
  })

  it('should get current session when authenticated', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const session = await act(async () => {
      return await result.current.getCurrentSession()
    })

    expect(session).not.toBeNull()
    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user?.email).toBe('test@example.com')
  })

  it('should return null session when not authenticated', async () => {
    vi.mocked(getCurrentUser).mockRejectedValue(new Error('Not authenticated'))
    vi.mocked(fetchAuthSession).mockResolvedValue({
      tokens: null,
    } as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const session = await act(async () => {
      return await result.current.getCurrentSession()
    })

    expect(session).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })

  it('should refresh session using refresh token', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    const refreshedSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'new-mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValueOnce(mockSession as any)
    vi.mocked(fetchAuthSession).mockResolvedValueOnce(refreshedSession as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    // Refresh session
    await act(async () => {
      await result.current.refreshSession()
    })

    expect(fetchAuthSession).toHaveBeenCalledWith({ forceRefresh: true })
  })

  it('should handle refresh token expiration and redirect to login', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValueOnce(mockSession as any)
    
    // Mock refresh failure due to expired refresh token
    const refreshError = new Error('Refresh token expired')
    refreshError.message = 'refresh expired'
    vi.mocked(fetchAuthSession).mockRejectedValueOnce(refreshError)

    Object.defineProperty(window, 'location', {
      value: { pathname: '/dashboard' },
      writable: true,
    })

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    // Try to refresh session
    await act(async () => {
      await result.current.refreshSession()
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(false)
    })

    expect(mockNavigate).toHaveBeenCalledWith('/login', { replace: true })
  })

  it('should synchronize auth state across tabs on logout', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)
    vi.mocked(signIn).mockResolvedValue({
      isSignedIn: true,
      nextStep: { signInStep: 'DONE' },
    } as any)
    vi.mocked(signOut).mockResolvedValue({} as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await act(async () => {
      await result.current.signIn('test@example.com', 'password123')
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })

    // Simulate logout event from another tab
    const logoutEvent = new StorageEvent('storage', {
      key: 'spendsense_auth_state',
      newValue: null,
      oldValue: JSON.stringify({ authenticated: true }),
    })

    act(() => {
      window.dispatchEvent(logoutEvent)
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(false)
    })
  })

  it('should synchronize auth state across tabs on login', async () => {
    const mockUser = {
      username: 'test@example.com',
      userId: 'user-123',
    }

    const mockSession = {
      tokens: {
        idToken: {
          payload: {
            sub: 'user-123',
            email: 'test@example.com',
          },
        },
        accessToken: {
          toString: () => 'mock-access-token',
          payload: {
            exp: Math.floor(Date.now() / 1000) + 3600,
          },
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)

    const { result } = renderHook(() => useAuth(), { wrapper })

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(false)

    // Simulate login event from another tab
    const loginEvent = new StorageEvent('storage', {
      key: 'spendsense_auth_state',
      newValue: JSON.stringify({ authenticated: true, timestamp: Date.now() }),
      oldValue: null,
    })

    act(() => {
      window.dispatchEvent(loginEvent)
    })

    await waitFor(() => {
      expect(result.current.isAuthenticated).toBe(true)
    })
  })
})



