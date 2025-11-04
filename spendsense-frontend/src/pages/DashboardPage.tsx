import { useAuthContext } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'
import { ConsentModal } from '@/components/ConsentModal'
import { useState, useEffect } from 'react'

/**
 * Dashboard page component (protected route)
 * Displays user information and logout functionality
 */
export function DashboardPage() {
  const { user, signOut, isLoading } = useAuthContext()
  const navigate = useNavigate()

  // Consent status placeholder - will be replaced with API call in next story
  const [consentGranted, setConsentGranted] = useState<boolean | null>(null)
  const [showConsentModal, setShowConsentModal] = useState(false)

  // Check consent status after user is loaded
  useEffect(() => {
    if (!isLoading && user) {
      // Placeholder: Check localStorage for consent status
      // In next story, this will check API
      const storedConsent = localStorage.getItem('spendsense_consent_granted')
      if (storedConsent === 'true') {
        setConsentGranted(true)
        setShowConsentModal(false)
      } else {
        setConsentGranted(false)
        setShowConsentModal(true)
      }
    }
  }, [isLoading, user])

  const handleLogout = async () => {
    try {
      await signOut()
      navigate('/login', { replace: true })
    } catch (error) {
      console.error('Logout error:', error)
    }
  }

  const handleConsentAccept = () => {
    // Placeholder: Store consent in localStorage
    // In next story, this will call API
    localStorage.setItem('spendsense_consent_granted', 'true')
    setConsentGranted(true)
    setShowConsentModal(false)
  }

  const handleConsentDecline = () => {
    // Placeholder: Handle decline
    // In next story, this will call API and redirect user
    setConsentGranted(false)
    setShowConsentModal(false)
    // For now, we'll just close the modal
    // In production, this might redirect to a different page or show a message
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="text-lg">Loading...</div>
        </div>
      </div>
    )
  }

  // Show consent modal if consent not granted
  if (showConsentModal && consentGranted === false) {
    return (
      <>
        <ConsentModal
          open={showConsentModal}
          onAccept={handleConsentAccept}
          onDecline={handleConsentDecline}
        />
        {/* Show loading state behind modal while consent is pending */}
        <div className="min-h-screen flex items-center justify-center bg-background/50">
          <div className="text-center">
            <div className="text-lg">Loading...</div>
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <ConsentModal
        open={showConsentModal}
        onAccept={handleConsentAccept}
        onDecline={handleConsentDecline}
      />
      <div className="min-h-screen bg-background p-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
              <p className="text-muted-foreground">Welcome to SpendSense</p>
            </div>
            <Button onClick={handleLogout} variant="outline">
              Logout
            </Button>
          </div>

          <div className="bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">User Information</h2>
            <div className="space-y-2">
              <div>
                <span className="font-medium">Email: </span>
                <span>{user?.email || user?.username || 'N/A'}</span>
              </div>
              <div>
                <span className="font-medium">User ID: </span>
                <span className="font-mono text-sm">{user?.sub || 'N/A'}</span>
              </div>
            </div>
          </div>

          <div className="mt-8 bg-card border rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <p className="text-muted-foreground">
              Dashboard content will be implemented in future stories.
            </p>
          </div>
        </div>
      </div>
    </>
  )
}
