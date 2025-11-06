import { useState, useEffect, useMemo, useRef } from 'react'
import Editor from '@monaco-editor/react'
import debounce from 'lodash.debounce'
import { useBookStore } from '../stores/bookStore'
import { Save, Clock } from 'lucide-react'

export default function EditorPane({ chapter }) {
  const { updateChapter } = useBookStore()

  const [content, setContent] = useState(chapter?.content || '')
  const [title, setTitle] = useState(chapter?.title || '')
  const [lastSaved, setLastSaved] = useState(null)
  const [isSaving, setIsSaving] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const contentRef = useRef(content)
  const titleRef = useRef(title)

  // Update local state when chapter changes
  useEffect(() => {
    if (chapter) {
      setContent(chapter.content || '')
      setTitle(chapter.title || '')
      contentRef.current = chapter.content || ''
      titleRef.current = chapter.title || ''
      setHasUnsavedChanges(false)
    }
  }, [chapter?.id])

  // Auto-save function
  const saveChapter = async (chapterId, newTitle, newContent) => {
    if (!chapterId) return

    setIsSaving(true)
    try {
      await updateChapter(chapterId, {
        title: newTitle,
        content: newContent,
      })
      setLastSaved(new Date())
      setHasUnsavedChanges(false)
    } catch (error) {
      console.error('Failed to save chapter:', error)
    } finally {
      setIsSaving(false)
    }
  }

  // Debounced save (2 seconds)
  const debouncedSave = useMemo(
    () =>
      debounce((chapterId, newTitle, newContent) => {
        saveChapter(chapterId, newTitle, newContent)
      }, 2000),
    []
  )

  // Handle content change
  const handleContentChange = (value) => {
    setContent(value || '')
    contentRef.current = value || ''
    setHasUnsavedChanges(true)

    if (chapter?.id) {
      debouncedSave(chapter.id, titleRef.current, value || '')
    }
  }

  // Handle title change
  const handleTitleChange = (e) => {
    const newTitle = e.target.value
    setTitle(newTitle)
    titleRef.current = newTitle
    setHasUnsavedChanges(true)

    if (chapter?.id) {
      debouncedSave(chapter.id, newTitle, contentRef.current)
    }
  }

  // Manual save
  const handleManualSave = () => {
    if (chapter?.id) {
      saveChapter(chapter.id, title, content)
    }
  }

  // Format time ago
  const formatTimeAgo = (date) => {
    if (!date) return ''

    const seconds = Math.floor((new Date() - date) / 1000)

    if (seconds < 60) return 'just now'
    if (seconds < 120) return '1 minute ago'
    if (seconds < 3600) return `${Math.floor(seconds / 60)} minutes ago`
    if (seconds < 7200) return '1 hour ago'
    return `${Math.floor(seconds / 3600)} hours ago`
  }

  // Re-render time ago every 10 seconds
  const [, setTick] = useState(0)
  useEffect(() => {
    const interval = setInterval(() => setTick((t) => t + 1), 10000)
    return () => clearInterval(interval)
  }, [])

  if (!chapter) {
    return (
      <div className="h-full flex items-center justify-center bg-white text-gray-500">
        <div className="text-center">
          <p className="text-lg mb-2">No chapter selected</p>
          <p className="text-sm">
            Select a chapter from the left panel or create a new one
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex-1 mr-4">
          <input
            type="text"
            value={title}
            onChange={handleTitleChange}
            className="w-full text-xl font-semibold text-gray-900 border-none focus:outline-none focus:ring-0 px-0"
            placeholder="Chapter Title"
          />
        </div>

        <div className="flex items-center gap-4">
          {/* Save Status */}
          <div className="flex items-center gap-2 text-sm text-gray-600">
            {isSaving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                <span>Saving...</span>
              </>
            ) : hasUnsavedChanges ? (
              <>
                <Clock className="w-4 h-4" />
                <span>Unsaved changes</span>
              </>
            ) : lastSaved ? (
              <>
                <span className="text-green-600">Saved {formatTimeAgo(lastSaved)}</span>
              </>
            ) : null}
          </div>

          {/* Manual Save Button */}
          <button
            onClick={handleManualSave}
            disabled={isSaving || !hasUnsavedChanges}
            className="flex items-center gap-2 px-3 py-1.5 text-sm border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Save className="w-4 h-4" />
            Save
          </button>
        </div>
      </div>

      {/* Editor */}
      <div className="flex-1 overflow-hidden">
        <Editor
          height="100%"
          defaultLanguage="markdown"
          value={content}
          onChange={handleContentChange}
          theme="vs-light"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineHeight: 24,
            wordWrap: 'on',
            wrappingIndent: 'indent',
            padding: { top: 20, bottom: 20 },
            scrollBeyondLastLine: false,
            automaticLayout: true,
            suggest: {
              showWords: false,
            },
            quickSuggestions: false,
          }}
        />
      </div>
    </div>
  )
}
