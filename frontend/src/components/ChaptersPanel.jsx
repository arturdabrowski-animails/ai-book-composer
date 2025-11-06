import { useState } from 'react'
import { useBookStore } from '../stores/bookStore'
import {
  ChevronDown,
  ChevronRight,
  Plus,
  Trash2,
  Edit2,
  FileText,
  Folder,
} from 'lucide-react'

export default function ChaptersPanel({ book, onChapterSelect }) {
  const {
    createChapter,
    createPart,
    deleteChapter,
    deletePart,
    updateBook,
    selectedChapter,
  } = useBookStore()

  const [expandedParts, setExpandedParts] = useState({})
  const [showNewChapterModal, setShowNewChapterModal] = useState(false)
  const [showNewPartModal, setShowNewPartModal] = useState(false)
  const [showEditBookModal, setShowEditBookModal] = useState(false)

  const [newChapterTitle, setNewChapterTitle] = useState('')
  const [newChapterPartId, setNewChapterPartId] = useState(null)
  const [newPartTitle, setNewPartTitle] = useState('')
  const [editBookData, setEditBookData] = useState({
    title: book.title,
    author: book.author,
  })

  const togglePart = (partId) => {
    setExpandedParts((prev) => ({
      ...prev,
      [partId]: !prev[partId],
    }))
  }

  const handleCreateChapter = async (e) => {
    e.preventDefault()
    try {
      await createChapter(book.id, {
        title: newChapterTitle,
        content: '',
        part_id: newChapterPartId,
      })
      setShowNewChapterModal(false)
      setNewChapterTitle('')
      setNewChapterPartId(null)
    } catch (error) {
      console.error('Failed to create chapter:', error)
    }
  }

  const handleCreatePart = async (e) => {
    e.preventDefault()
    try {
      await createPart(book.id, { title: newPartTitle })
      setShowNewPartModal(false)
      setNewPartTitle('')
    } catch (error) {
      console.error('Failed to create part:', error)
    }
  }

  const handleDeleteChapter = async (chapterId, e) => {
    e.stopPropagation()
    if (!confirm('Delete this chapter?')) return

    try {
      await deleteChapter(chapterId)
    } catch (error) {
      console.error('Failed to delete chapter:', error)
    }
  }

  const handleDeletePart = async (partId, e) => {
    e.stopPropagation()
    if (!confirm('Delete this part? Chapters will become ungrouped.')) return

    try {
      await deletePart(partId)
    } catch (error) {
      console.error('Failed to delete part:', error)
    }
  }

  const handleEditBook = async (e) => {
    e.preventDefault()
    try {
      await updateBook(book.id, editBookData)
      setShowEditBookModal(false)
    } catch (error) {
      console.error('Failed to update book:', error)
    }
  }

  // Get chapters without parts
  const unpartedChapters = book.chapters?.filter((ch) => !ch.part_id) || []

  return (
    <div className="h-full flex flex-col bg-gray-50 border-r border-gray-200">
      {/* Book Metadata */}
      <div className="p-4 bg-white border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-1">
          {book.title}
        </h2>
        <p className="text-sm text-gray-600 mb-3">by {book.author}</p>
        <button
          onClick={() => {
            setEditBookData({ title: book.title, author: book.author })
            setShowEditBookModal(true)
          }}
          className="text-sm text-primary-500 hover:text-primary-600 flex items-center gap-1"
        >
          <Edit2 className="w-3 h-3" />
          Edit metadata
        </button>
      </div>

      {/* Chapters Tree */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {/* Parts with their chapters */}
        {book.parts?.map((part) => (
          <div key={part.id} className="mb-3">
            <div
              onClick={() => togglePart(part.id)}
              className="flex items-center justify-between p-2 hover:bg-gray-100 rounded cursor-pointer group"
            >
              <div className="flex items-center gap-2">
                {expandedParts[part.id] ? (
                  <ChevronDown className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-gray-500" />
                )}
                <Folder className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-900">
                  {part.title}
                </span>
              </div>
              <button
                onClick={(e) => handleDeletePart(part.id, e)}
                className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-600"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>

            {expandedParts[part.id] && (
              <div className="ml-6 mt-1 space-y-1">
                {part.chapters?.map((chapter) => (
                  <div
                    key={chapter.id}
                    onClick={() => onChapterSelect(chapter)}
                    className={`flex items-center justify-between p-2 rounded cursor-pointer group ${
                      selectedChapter?.id === chapter.id
                        ? 'bg-primary-100 text-primary-700'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center gap-2 flex-1 min-w-0">
                      <FileText className="w-4 h-4 flex-shrink-0" />
                      <span className="text-sm truncate">{chapter.title}</span>
                    </div>
                    <button
                      onClick={(e) => handleDeleteChapter(chapter.id, e)}
                      className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-600 flex-shrink-0"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Chapters without parts */}
        {unpartedChapters.map((chapter) => (
          <div
            key={chapter.id}
            onClick={() => onChapterSelect(chapter)}
            className={`flex items-center justify-between p-2 rounded cursor-pointer group ${
              selectedChapter?.id === chapter.id
                ? 'bg-primary-100 text-primary-700'
                : 'hover:bg-gray-100'
            }`}
          >
            <div className="flex items-center gap-2 flex-1 min-w-0">
              <FileText className="w-4 h-4 flex-shrink-0" />
              <span className="text-sm truncate">{chapter.title}</span>
            </div>
            <button
              onClick={(e) => handleDeleteChapter(chapter.id, e)}
              className="opacity-0 group-hover:opacity-100 text-red-500 hover:text-red-600 flex-shrink-0"
            >
              <Trash2 className="w-3 h-3" />
            </button>
          </div>
        ))}

        {book.chapters?.length === 0 && (
          <div className="text-center py-8 text-gray-500 text-sm">
            No chapters yet. Create one to get started!
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="p-4 bg-white border-t border-gray-200 space-y-2">
        <button
          onClick={() => setShowNewChapterModal(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Chapter
        </button>
        <button
          onClick={() => setShowNewPartModal(true)}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Part
        </button>
      </div>

      {/* New Chapter Modal */}
      {showNewChapterModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-semibold mb-4">New Chapter</h3>
            <form onSubmit={handleCreateChapter} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={newChapterTitle}
                  onChange={(e) => setNewChapterTitle(e.target.value)}
                  required
                  autoFocus
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Chapter 1"
                />
              </div>

              {book.parts?.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Part (optional)
                  </label>
                  <select
                    value={newChapterPartId || ''}
                    onChange={(e) =>
                      setNewChapterPartId(e.target.value || null)
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">No part</option>
                    {book.parts.map((part) => (
                      <option key={part.id} value={part.id}>
                        {part.title}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowNewChapterModal(false)
                    setNewChapterTitle('')
                    setNewChapterPartId(null)
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Part Modal */}
      {showNewPartModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-semibold mb-4">New Part</h3>
            <form onSubmit={handleCreatePart} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={newPartTitle}
                  onChange={(e) => setNewPartTitle(e.target.value)}
                  required
                  autoFocus
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Part 1"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowNewPartModal(false)
                    setNewPartTitle('')
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Book Modal */}
      {showEditBookModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-xl font-semibold mb-4">Edit Book Metadata</h3>
            <form onSubmit={handleEditBook} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  value={editBookData.title}
                  onChange={(e) =>
                    setEditBookData({ ...editBookData, title: e.target.value })
                  }
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Author
                </label>
                <input
                  type="text"
                  value={editBookData.author}
                  onChange={(e) =>
                    setEditBookData({ ...editBookData, author: e.target.value })
                  }
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowEditBookModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600"
                >
                  Save
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
