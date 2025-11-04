import { Amplify } from '@aws-amplify/core'

/**
 * Configure AWS Amplify with Cognito settings
 * This must be called before using any Amplify services
 */
export function configureAmplify() {
  const userPoolId = import.meta.env.VITE_COGNITO_USER_POOL_ID
  const clientId = import.meta.env.VITE_COGNITO_CLIENT_ID

  if (!userPoolId || !clientId) {
    throw new Error(
      'Missing required Cognito configuration. Please set VITE_COGNITO_USER_POOL_ID and VITE_COGNITO_CLIENT_ID in your .env.local file.'
    )
  }

  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId,
        userPoolClientId: clientId,
        loginWith: {
          email: true,
        },
      },
    },
  })
}

// Auto-configure on module load
configureAmplify()
