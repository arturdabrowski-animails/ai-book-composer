import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useBookStore } from '../stores/bookStore'
import ChaptersPanel from '../components/ChaptersPanel'
import EditorPane from '../components/EditorPane'
import PreviewPane from '../components/PreviewPane'
import ExportDialog from '../components/ExportDialog'
import { ArrowLeft, Eye, EyeOff, Download } from 'lucide-react'

export default function EditorPage() {
  const { bookId } = useParams()
  const navigate = useNavigate()

  const {
    currentBook,
    selectedChapter,
    loadBook,
    selectChapter,
    loading,
  } = useBookStore()

  const [showPreview, setShowPreview] = useState(false)
  const [showExportDialog, setShowExportDialog] = useState(false)

  useEffect(() => {
    if (bookId) {
      loadBook(bookId)
    }
  }, [bookId])

  const handleChapterSelect = (chapter) => {
    selectChapter(chapter)
  }

  if (loading && !currentBook) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
          <p className="text-gray-600 mt-4">Loading book...</p>
        </div>
      </div>
    )
  }

  if (!currentBook) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Book not found</p>
          <button
            onClick={() => navigate('/books')}
            className="text-primary-500 hover:text-primary-600"
          >
            Back to books
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* Top Bar */}
      <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
        <button
          onClick={() => navigate('/books')}
          className="flex items-center gap-2 text-gray-700 hover:text-gray-900 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Books</span>
        </button>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowExportDialog(true)}
            className="flex items-center gap-2 px-3 py-1.5 bg-primary-500 text-white rounded-md hover:bg-primary-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
          <button
            onClick={() => setShowPreview(!showPreview)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md transition-colors ${
              showPreview
                ? 'bg-primary-100 text-primary-700'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {showPreview ? (
              <>
                <EyeOff className="w-4 h-4" />
                Hide Preview
              </>
            ) : (
              <>
                <Eye className="w-4 h-4" />
                Show Preview
              </>
            )}
          </button>
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chapters Panel (Left) */}
        <div className="w-80 flex-shrink-0">
          <ChaptersPanel book={currentBook} onChapterSelect={handleChapterSelect} />
        </div>

        {/* Editor (Center) */}
        <div className={showPreview ? 'flex-1 border-r border-gray-200' : 'flex-1'}>
          <EditorPane chapter={selectedChapter} />
        </div>

        {/* Preview (Right) - Optional */}
        {showPreview && (
          <div className="w-1/2 flex-shrink-0">
            <PreviewPane content={selectedChapter?.content || ''} />
          </div>
        )}
      </div>

      {/* Export Dialog */}
      <ExportDialog
        book={currentBook}
        isOpen={showExportDialog}
        onClose={() => setShowExportDialog(false)}
      />
    </div>
  )
}
