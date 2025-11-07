import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { ZoomIn, ZoomOut, Maximize2, BookOpen } from 'lucide-react'

export default function BookPreview({ content, bookTitle = 'Untitled' }) {
  const [zoom, setZoom] = useState(0.75) // Default 75% for better fit
  const [isFullscreen, setIsFullscreen] = useState(false)

  const handleZoomIn = () => {
    setZoom(prev => Math.min(1.5, prev + 0.1))
  }

  const handleZoomOut = () => {
    setZoom(prev => Math.max(0.4, prev - 0.1))
  }

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen)
  }

  return (
    <div className={`flex flex-col h-full bg-gray-100 ${isFullscreen ? 'fixed inset-0 z-50' : ''}`}>
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <BookOpen className="w-4 h-4" />
          <span>Print Preview - Professional Layout</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleZoomOut}
            disabled={zoom <= 0.4}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50"
            title="Zoom out"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm text-gray-700 min-w-[60px] text-center">
            {Math.round(zoom * 100)}%
          </span>
          <button
            onClick={handleZoomIn}
            disabled={zoom >= 1.5}
            className="p-2 rounded hover:bg-gray-100 disabled:opacity-50"
            title="Zoom in"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <div className="w-px h-6 bg-gray-300 mx-2" />
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded hover:bg-gray-100"
            title="Toggle fullscreen"
          >
            <Maximize2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Preview Area - Scrollable Pages */}
      <div className="flex-1 overflow-auto bg-gray-200 p-8">
        <div
          className="mx-auto shadow-2xl bg-white transition-all"
          style={{
            width: `${794 * zoom}px`, // A4 width in pixels (21cm at 96 DPI)
            minHeight: `${1122 * zoom}px`, // A4 height (29.7cm)
          }}
        >
          <style>{printCSS}</style>

          {/* Book Content with Professional Print CSS */}
          <div className="book-preview-content">
            {/* Content Page */}
            <article className="page chapter">
              <section className="chapter-content">
                <ReactMarkdown>{content || '*No content to preview*'}</ReactMarkdown>
              </section>
            </article>
          </div>
        </div>
      </div>

      {/* Info Bar */}
      <div className="bg-white border-t border-gray-200 px-4 py-2 text-xs text-gray-500 flex items-center justify-between">
        <span>Scroll to see more content • Professional book formatting with Polish typography</span>
        <span>A4 Format (21 × 29.7 cm)</span>
      </div>
    </div>
  )
}

// Professional print CSS (matching our PDF export)
const printCSS = `
  .book-preview-content {
    font-family: 'Georgia', 'Palatino', serif;
    font-size: 11pt;
    line-height: 1.7;
    color: #1a1a1a;
  }

  .page {
    width: 794px;
    min-height: 1122px;
    padding: 2.5cm 2cm;
    page-break-after: always;
    background: white;
  }

  .title-page {
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding-top: 35%;
  }

  .book-title {
    font-size: 36pt;
    font-weight: bold;
    letter-spacing: 0.03em;
    line-height: 1.2;
    color: #1a1a1a;
    text-transform: uppercase;
    font-variant: small-caps;
    margin: 0;
  }

  .chapter {
    padding: 2.5cm 2cm;
  }

  .chapter-content {
    text-align: justify;
    hyphens: auto;
  }

  /* Paragraphs */
  .chapter-content p {
    margin: 0;
    text-indent: 1.5em;
    line-height: 1.7;
  }

  .chapter-content > p:first-of-type {
    text-indent: 0;
  }

  /* Drop caps */
  .chapter-content > p:first-of-type::first-letter {
    font-size: 3.8em;
    line-height: 0.85;
    float: left;
    margin: 0.08em 0.12em 0 0;
    font-weight: bold;
    color: #2a2a2a;
  }

  /* Headings */
  .chapter-content h1,
  .chapter-content h2,
  .chapter-content h3,
  .chapter-content h4 {
    font-weight: bold;
    color: #1a1a1a;
    page-break-after: avoid;
  }

  .chapter-content h1 {
    font-size: 28pt;
    margin: 2em 0 1.5em 0;
    text-align: center;
    font-variant: small-caps;
    letter-spacing: 0.02em;
  }

  .chapter-content h2 {
    font-size: 18pt;
    margin-top: 2em;
    margin-bottom: 0.75em;
    letter-spacing: 0.02em;
    font-variant: small-caps;
  }

  .chapter-content h3 {
    font-size: 14pt;
    margin-top: 1.5em;
    margin-bottom: 0.6em;
  }

  .chapter-content h4 {
    font-size: 12pt;
    margin-top: 1.2em;
    margin-bottom: 0.5em;
  }

  /* No indent after headings */
  .chapter-content h1 + p,
  .chapter-content h2 + p,
  .chapter-content h3 + p,
  .chapter-content h4 + p {
    text-indent: 0;
  }

  /* Scene breaks */
  .chapter-content hr {
    border: none;
    text-align: center;
    margin: 2em 0;
    height: 1.5em;
  }

  .chapter-content hr::before {
    content: "* * *";
    font-size: 1.2em;
    letter-spacing: 1.5em;
    color: #888;
  }

  /* Blockquotes */
  .chapter-content blockquote {
    margin: 1.75em 2.5em;
    padding: 1em 1.25em;
    font-style: italic;
    border-left: 3px solid #c0c0c0;
    background: #f8f8f8;
    color: #2a2a2a;
  }

  .chapter-content blockquote p {
    text-indent: 0;
    margin-bottom: 0.5em;
  }

  /* Lists */
  .chapter-content ul,
  .chapter-content ol {
    margin: 1.2em 0;
    padding-left: 2.5em;
  }

  .chapter-content li {
    margin: 0.6em 0;
    line-height: 1.6;
  }

  .chapter-content li p {
    text-indent: 0;
    margin: 0.3em 0;
  }

  /* Code */
  .chapter-content code {
    font-family: 'Courier New', monospace;
    background: #f5f5f5;
    padding: 0.15em 0.4em;
    font-size: 9.5pt;
    border-radius: 2px;
    color: #c7254e;
  }

  .chapter-content pre {
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-left: 3px solid #999;
    padding: 1em 1.2em;
    margin: 1.5em 0;
    overflow-x: auto;
  }

  .chapter-content pre code {
    background: none;
    padding: 0;
    color: #333;
  }

  /* Tables */
  .chapter-content table {
    border-collapse: collapse;
    margin: 1.5em auto;
    width: 100%;
    font-size: 10pt;
  }

  .chapter-content th,
  .chapter-content td {
    border: 1px solid #d0d0d0;
    padding: 0.6em 0.8em;
    text-align: left;
  }

  .chapter-content th {
    background: #f0f0f0;
    font-weight: bold;
    font-variant: small-caps;
    letter-spacing: 0.05em;
  }

  /* Emphasis */
  .chapter-content em {
    font-style: italic;
  }

  .chapter-content strong {
    font-weight: bold;
  }
`
