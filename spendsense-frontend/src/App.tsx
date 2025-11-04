import { TailwindTest } from './components/TailwindTest'
import './App.css'

function App() {
  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-4">SpendSense Frontend</h1>
        <p className="mb-6">Frontend project initialized successfully!</p>
        <TailwindTest />
      </div>
    </div>
  )
}

export default App
