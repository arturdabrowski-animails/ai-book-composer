import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import BooksListPage from './pages/BooksListPage'
import EditorPage from './pages/EditorPage'
import { getApiUrl } from './config'

function App() {
  // Authentication disabled for development
  const buildDate = new Date('2025-11-07T12:00:00Z').toLocaleString('pl-PL')
  const [apiVersion, setApiVersion] = useState('checking...')

  useEffect(() => {
    // Check API version on mount
    fetch(getApiUrl('/api/version'))
      .then(res => res.json())
      .then(data => setApiVersion(`API: ${data.version}`))
      .catch(() => setApiVersion('API: offline'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <div className="flex-1">
        <Routes>
          {/* Main routes - no auth required */}
          <Route path="/books" element={<BooksListPage />} />
          <Route path="/books/:bookId" element={<EditorPage />} />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/books" />} />
        </Routes>
      </div>

      {/* Version signature */}
      <footer className="py-2 px-4 text-xs text-gray-400 text-center border-t border-gray-200 bg-white">
        Frontend v2.0.1 | Build: {buildDate} | {apiVersion} | Phase 2: Import/Export
      </footer>
    </div>
  )
}

export default App
