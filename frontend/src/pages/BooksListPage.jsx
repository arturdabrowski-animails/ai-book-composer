import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { useBookStore } from '../stores/bookStore'
import { BookOpen, Plus, LogOut, Trash2 } from 'lucide-react'

export default function BooksListPage() {
  const navigate = useNavigate()
  const { logout, user } = useAuthStore()
  const { books, loadBooks, createBook, deleteBook, loading } = useBookStore()

  const [showNewBookModal, setShowNewBookModal] = useState(false)
  const [newBookData, setNewBookData] = useState({
    title: '',
    author: '',
    language: 'en',
  })

  useEffect(() => {
    loadBooks()
  }, [])

  const handleCreateBook = async (e) => {
    e.preventDefault()

    try {
      const book = await createBook(newBookData)
      setShowNewBookModal(false)
      setNewBookData({ title: '', author: '', language: 'en' })
      navigate(`/books/${book.id}`)
    } catch (error) {
      console.error('Failed to create book:', error)
    }
  }

  const handleDeleteBook = async (bookId, e) => {
    e.stopPropagation()

    if (!confirm('Are you sure you want to delete this book?')) {
      return
    }

    try {
      await deleteBook(bookId)
    } catch (error) {
      console.error('Failed to delete book:', error)
    }
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Book Composer</h1>
            <p className="text-sm text-gray-600 mt-1">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="flex items-center gap-2 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign out
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900">My Books</h2>
          <button
            onClick={() => setShowNewBookModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Book
          </button>
        </div>

        {/* Books Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            <p className="text-gray-600 mt-4">Loading books...</p>
          </div>
        ) : books.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <p className="text-gray-600 mb-4">No books yet</p>
            <button
              onClick={() => setShowNewBookModal(true)}
              className="text-primary-500 hover:text-primary-600 font-medium"
            >
              Create your first book
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {books.map((book) => (
              <div
                key={book.id}
                onClick={() => navigate(`/books/${book.id}`)}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer group"
              >
                <div className="flex justify-between items-start mb-4">
                  <BookOpen className="w-8 h-8 text-primary-500" />
                  <button
                    onClick={(e) => handleDeleteBook(book.id, e)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-red-500 hover:text-red-600 p-1"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                  {book.title}
                </h3>

                {book.subtitle && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-1">
                    {book.subtitle}
                  </p>
                )}

                <p className="text-sm text-gray-500 mb-4">by {book.author}</p>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span>{book.language.toUpperCase()}</span>
                  <span>Updated {formatDate(book.updated_at)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* New Book Modal */}
      {showNewBookModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-semibold mb-4">Create New Book</h3>

            <form onSubmit={handleCreateBook} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  value={newBookData.title}
                  onChange={(e) =>
                    setNewBookData({ ...newBookData, title: e.target.value })
                  }
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="My Awesome Book"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Author *
                </label>
                <input
                  type="text"
                  value={newBookData.author}
                  onChange={(e) =>
                    setNewBookData({ ...newBookData, author: e.target.value })
                  }
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="John Doe"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Language
                </label>
                <select
                  value={newBookData.language}
                  onChange={(e) =>
                    setNewBookData({ ...newBookData, language: e.target.value })
                  }
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="en">English</option>
                  <option value="pl">Polish</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowNewBookModal(false)
                    setNewBookData({ title: '', author: '', language: 'en' })
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 transition-colors"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
