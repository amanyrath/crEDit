import { useAuthContext } from '@/contexts/AuthContext'

/**
 * Operator Dashboard Page
 * Displays operator-specific features and user management tools
 */
export function OperatorDashboardPage() {
  const { user } = useAuthContext()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Operator Dashboard</h1>
          <p className="mt-2 text-gray-600">Welcome, {user?.email || user?.username}</p>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Dashboard Overview</h2>
          <p className="text-gray-600">
            Operator dashboard features will be implemented in future stories.
          </p>
          <p className="mt-4 text-sm text-gray-500">Role: {user?.role || 'Unknown'}</p>
        </div>
      </div>
    </div>
  )
}
