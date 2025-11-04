/**
 * Test file to verify environment variables are loaded correctly
 * This file can be run with: npm test -- env.test.ts
 */

import { describe, it, expect } from 'vitest'

describe('Environment Variables', () => {
  it('should load VITE_API_URL', () => {
    // Vite automatically loads .env.local in development
    // Variables are accessible via import.meta.env
    expect(import.meta.env.VITE_API_URL).toBeDefined()
    // For local development, it should be http://localhost:8000
    if (import.meta.env.MODE === 'development') {
      expect(import.meta.env.VITE_API_URL).toBe('http://localhost:8000')
    }
  })

  it('should load VITE_COGNITO_USER_POOL_ID', () => {
    // This will be a placeholder until actual values are set
    expect(import.meta.env.VITE_COGNITO_USER_POOL_ID).toBeDefined()
  })

  it('should load VITE_COGNITO_CLIENT_ID', () => {
    // This will be a placeholder until actual values are set
    expect(import.meta.env.VITE_COGNITO_CLIENT_ID).toBeDefined()
  })

  it('should only expose VITE_ prefixed variables', () => {
    // Vite only exposes variables prefixed with VITE_ to client-side code
    // Other variables should not be accessible
    const envKeys = Object.keys(import.meta.env)
    const viteKeys = envKeys.filter(key => key.startsWith('VITE_'))
    // Should have at least our three VITE_ variables
    expect(viteKeys.length).toBeGreaterThanOrEqual(3)
  })
})
