import { useAuthContext } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'

/**
 * Dashboard page component (protected route)
 * Displays user information and logout functionality
 */
export function DashboardPage() {
  const { user, signOut, isLoading } = useAuthContext()
  const navigate = useNavigate()

  const handleLogout = async () => {
    try {
      await signOut()
      navigate('/login', { replace: true })
    } catch (error) {
      console.error('Logout error:', error)
    }
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

  return (
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
  )
}

