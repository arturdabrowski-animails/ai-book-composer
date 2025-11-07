import { Routes, Route, Navigate } from 'react-router-dom'
import BooksListPage from './pages/BooksListPage'
import EditorPage from './pages/EditorPage'

function App() {
  // Authentication disabled for development
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        {/* Main routes - no auth required */}
        <Route path="/books" element={<BooksListPage />} />
        <Route path="/books/:bookId" element={<EditorPage />} />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/books" />} />
      </Routes>
    </div>
  )
}

export default App
