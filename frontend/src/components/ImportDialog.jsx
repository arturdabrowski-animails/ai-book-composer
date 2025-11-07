import { useState } from 'react'
import { Upload, X, AlertCircle } from 'lucide-react'

export default function ImportDialog({ isOpen, onClose, onImport }) {
  const [file, setFile] = useState(null)
  const [isImporting, setIsImporting] = useState(false)
  const [error, setError] = useState(null)

  if (!isOpen) return null

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.name.endsWith('.epub')) {
      setFile(selectedFile)
      setError(null)
    } else {
      setFile(null)
      setError('Please select an EPUB file')
    }
  }

  const handleImport = async () => {
    if (!file) return

    setIsImporting(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/import/epub', {
        method: 'POST',
        body: formData
      })

      if (!response.ok) {
        // Try to parse JSON error, fallback to text
        let errorMessage = 'Import failed'
        try {
          const data = await response.json()
          errorMessage = data.detail || errorMessage
        } catch {
          const text = await response.text()
          errorMessage = text || `Server error (${response.status})`
        }
        throw new Error(errorMessage)
      }

      const book = await response.json()
      onImport(book)
      onClose()
    } catch (err) {
      console.error('Import error:', err)
      setError(err.message)
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Import EPUB</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="space-y-4">
          <div>
            <label
              htmlFor="file-upload"
              className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer hover:bg-gray-50 transition-colors"
            >
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <Upload className="w-10 h-10 mb-2 text-gray-400" />
                <p className="text-sm text-gray-600">
                  {file ? file.name : 'Click to upload or drag EPUB file'}
                </p>
              </div>
              <input
                id="file-upload"
                type="file"
                className="hidden"
                accept=".epub"
                onChange={handleFileChange}
              />
            </label>
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
              disabled={isImporting}
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleImport}
              disabled={!file || isImporting}
              className="flex-1 px-4 py-2 bg-primary-500 text-white rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isImporting ? 'Importing...' : 'Import'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
