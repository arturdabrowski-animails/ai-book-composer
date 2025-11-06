import ReactMarkdown from 'react-markdown'

export default function PreviewPane({ content }) {
  return (
    <div className="h-full overflow-y-auto bg-white p-8">
      <div className="max-w-3xl mx-auto prose prose-sm sm:prose lg:prose-lg">
        <ReactMarkdown>{content || '*No content to preview*'}</ReactMarkdown>
      </div>
    </div>
  )
}
