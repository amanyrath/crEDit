import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, waitFor, act } from '@testing-library/react'
import { signIn, signOut, getCurrentUser, fetchAuthSession } from '@aws-amplify/auth'
import { useAuth } from './useAuth'

// Mock Amplify Auth functions
vi.mock('@aws-amplify/auth', () => ({
  signIn: vi.fn(),
  signOut: vi.fn(),
  getCurrentUser: vi.fn(),
  fetchAuthSession: vi.fn(),
}))

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with no authenticated user', async () => {
    vi.mocked(getCurrentUser).mockRejectedValue(new Error('Not authenticated'))
    vi.mocked(fetchAuthSession).mockResolvedValue({
      tokens: null,
    } as any)

    const { result } = renderHook(() => useAuth())

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
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)
    vi.mocked(signIn).mockResolvedValue({
      isSignedIn: true,
      nextStep: { signInStep: 'DONE' },
    } as any)

    const { result } = renderHook(() => useAuth())

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
  })

  it('should handle sign in error - wrong password', async () => {
    const error = new Error('NotAuthorizedException')
    ;(error as any).name = 'NotAuthorizedException'
    vi.mocked(signIn).mockRejectedValue(error)

    const { result } = renderHook(() => useAuth())

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

    const { result } = renderHook(() => useAuth())

    await act(async () => {
      await expect(
        result.current.signIn('notfound@example.com', 'password123')
      ).rejects.toThrow('User not found')
    })

    expect(result.current.error?.message).toBe('User not found')
  })

  it('should sign out user successfully', async () => {
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
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)
    vi.mocked(signOut).mockResolvedValue({} as any)

    const { result } = renderHook(() => useAuth())

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
        },
      },
    }

    vi.mocked(getCurrentUser).mockResolvedValue(mockUser as any)
    vi.mocked(fetchAuthSession).mockResolvedValue(mockSession as any)

    const { result } = renderHook(() => useAuth())

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

    const { result } = renderHook(() => useAuth())

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    const session = await act(async () => {
      return await result.current.getCurrentSession()
    })

    expect(session).toBeNull()
    expect(result.current.isAuthenticated).toBe(false)
  })
})

