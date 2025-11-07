import { useState } from 'react'
import { Download, X, AlertCircle } from 'lucide-react'

export default function ExportDialog({ book, isOpen, onClose }) {
  const [format, setFormat] = useState('epub')
  const [options, setOptions] = useState({
    include_title_page: true,
    include_copyright_page: true,
    include_toc: true,
    number_chapters: true,
    chapter_prefix: 'Chapter'
  })
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState(null)

  if (!isOpen) return null

  const handleExport = async () => {
    setIsExporting(true)
    setError(null)

    try {
      const response = await fetch(`/api/books/${book.id}/export/${format}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(options)
      })

      if (!response.ok) {
        // Try to parse JSON error, fallback to text
        let errorMessage = 'Export failed'
        try {
          const data = await response.json()
          errorMessage = data.detail || errorMessage
        } catch {
          const text = await response.text()
          errorMessage = text || `Server error (${response.status})`
        }
        throw new Error(errorMessage)
      }

      // Download file
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${book.title.replace(/[^a-z0-9]/gi, '_')}.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)

      onClose()
    } catch (err) {
      console.error('Export error:', err)
      setError(err.message)
    } finally {
      setIsExporting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Export Book</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4">
          {/* Format selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Format
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="radio"
                  value="epub"
                  checked={format === 'epub'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm">EPUB (E-readers)</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  value="pdf"
                  checked={format === 'pdf'}
                  onChange={(e) => setFormat(e.target.value)}
                  className="mr-2"
                />
                <span className="text-sm">PDF (Print)</span>
              </label>
            </div>
          </div>

          {/* Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Options
            </label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.include_toc}
                  onChange={(e) =>
                    setOptions({ ...options, include_toc: e.target.checked })
                  }
                  className="mr-2"
                />
                <span className="text-sm">Include table of contents</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.number_chapters}
                  onChange={(e) =>
                    setOptions({ ...options, number_chapters: e.target.checked })
                  }
                  className="mr-2"
                />
                <span className="text-sm">Number chapters</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.include_title_page}
                  onChange={(e) =>
                    setOptions({ ...options, include_title_page: e.target.checked })
                  }
                  className="mr-2"
                />
                <span className="text-sm">Include title page</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={options.include_copyright_page}
                  onChange={(e) =>
                    setOptions({
                      ...options,
                      include_copyright_page: e.target.checked
                    })
                  }
                  className="mr-2"
                />
                <span className="text-sm">Include copyright page</span>
              </label>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              disabled={isExporting}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleExport}
              disabled={isExporting}
              className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
              {isExporting ? 'Exporting...' : 'Export'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
