import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './stores/authStore'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import BooksListPage from './pages/BooksListPage'
import EditorPage from './pages/EditorPage'

function App() {
  const { token } = useAuthStore()

  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes */}
        <Route
          path="/books"
          element={token ? <BooksListPage /> : <Navigate to="/login" />}
        />
        <Route
          path="/books/:bookId"
          element={token ? <EditorPage /> : <Navigate to="/login" />}
        />

        {/* Default redirect */}
        <Route
          path="/"
          element={<Navigate to={token ? "/books" : "/login"} />}
        />
      </Routes>
    </div>
  )
}

export default App
