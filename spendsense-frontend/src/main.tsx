import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// Configure Amplify before importing App
import './lib/amplify'
import { AuthProvider } from './contexts/AuthContext'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>
)
