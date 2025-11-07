import BookPreview from './BookPreview'
import { useBookStore } from '../stores/bookStore'

export default function PreviewPane({ content }) {
  const { currentBook } = useBookStore()

  return (
    <BookPreview
      content={content}
      bookTitle={currentBook?.title || 'Untitled'}
    />
  )
}
