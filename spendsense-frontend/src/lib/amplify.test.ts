import { describe, it, expect, beforeEach, vi } from 'vitest'
import { Amplify } from '@aws-amplify/core'

// Mock environment variables
const mockEnv = {
  VITE_COGNITO_USER_POOL_ID: 'us-east-1_test123',
  VITE_COGNITO_CLIENT_ID: 'test-client-id',
}

describe('Amplify Configuration', () => {
  beforeEach(() => {
    // Reset Amplify configuration
    vi.clearAllMocks()
    // Mock import.meta.env
    vi.stubGlobal('import', {
      meta: {
        env: mockEnv,
      },
    })
  })

  it('should configure Amplify with Cognito settings', async () => {
    // Dynamically import to trigger configuration
    const { configureAmplify } = await import('./amplify')
    
    // Verify configuration was called
    expect(configureAmplify).toBeDefined()
    
    // Verify Amplify is configured
    const config = Amplify.getConfig()
    expect(config.Auth?.Cognito?.userPoolId).toBe(mockEnv.VITE_COGNITO_USER_POOL_ID)
    expect(config.Auth?.Cognito?.userPoolClientId).toBe(mockEnv.VITE_COGNITO_CLIENT_ID)
  })

  it('should throw error if Cognito User Pool ID is missing', async () => {
    const originalEnv = { ...mockEnv }
    delete (mockEnv as any).VITE_COGNITO_USER_POOL_ID

    await expect(async () => {
      await import('./amplify')
    }).rejects.toThrow('Missing required Cognito configuration')
    
    // Restore
    Object.assign(mockEnv, originalEnv)
  })

  it('should throw error if Cognito Client ID is missing', async () => {
    const originalEnv = { ...mockEnv }
    delete (mockEnv as any).VITE_COGNITO_CLIENT_ID

    await expect(async () => {
      await import('./amplify')
    }).rejects.toThrow('Missing required Cognito configuration')
    
    // Restore
    Object.assign(mockEnv, originalEnv)
  })
})



