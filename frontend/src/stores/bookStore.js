import { create } from 'zustand'
import { booksAPI } from '../api'

export const useBookStore = create((set, get) => ({
  books: [],
  currentBook: null,
  selectedChapter: null,
  loading: false,
  error: null,

  // Books
  loadBooks: async () => {
    set({ loading: true, error: null })
    try {
      const books = await booksAPI.listBooks()
      set({ books, loading: false })
    } catch (error) {
      set({ error: error.message, loading: false })
    }
  },

  loadBook: async (bookId) => {
    set({ loading: true, error: null })
    try {
      const book = await booksAPI.getBook(bookId)
      set({ currentBook: book, loading: false })
      return book
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  createBook: async (data) => {
    set({ loading: true, error: null })
    try {
      const book = await booksAPI.createBook(data)
      set((state) => ({
        books: [book, ...state.books],
        loading: false,
      }))
      return book
    } catch (error) {
      set({ error: error.message, loading: false })
      throw error
    }
  },

  updateBook: async (bookId, data) => {
    try {
      const updatedBook = await booksAPI.updateBook(bookId, data)
      set((state) => ({
        currentBook:
          state.currentBook?.id === bookId ? updatedBook : state.currentBook,
        books: state.books.map((b) =>
          b.id === bookId ? { ...b, ...data } : b
        ),
      }))
      return updatedBook
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  deleteBook: async (bookId) => {
    try {
      await booksAPI.deleteBook(bookId)
      set((state) => ({
        books: state.books.filter((b) => b.id !== bookId),
        currentBook:
          state.currentBook?.id === bookId ? null : state.currentBook,
      }))
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  // Chapters
  createChapter: async (bookId, data) => {
    try {
      const chapter = await booksAPI.createChapter(bookId, data)

      // Refresh book to get updated chapters
      await get().loadBook(bookId)

      return chapter
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  updateChapter: async (chapterId, data) => {
    try {
      const updatedChapter = await booksAPI.updateChapter(chapterId, data)

      // Update in current book
      set((state) => {
        if (!state.currentBook) return state

        return {
          currentBook: {
            ...state.currentBook,
            chapters: state.currentBook.chapters.map((ch) =>
              ch.id === chapterId ? { ...ch, ...updatedChapter } : ch
            ),
          },
          selectedChapter:
            state.selectedChapter?.id === chapterId
              ? updatedChapter
              : state.selectedChapter,
        }
      })

      return updatedChapter
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  deleteChapter: async (chapterId) => {
    try {
      await booksAPI.deleteChapter(chapterId)

      // Remove from current book
      set((state) => {
        if (!state.currentBook) return state

        return {
          currentBook: {
            ...state.currentBook,
            chapters: state.currentBook.chapters.filter(
              (ch) => ch.id !== chapterId
            ),
          },
          selectedChapter:
            state.selectedChapter?.id === chapterId
              ? null
              : state.selectedChapter,
        }
      })
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  moveChapter: async (chapterId, newPosition) => {
    try {
      await booksAPI.moveChapter(chapterId, newPosition)

      // Refresh book to get updated positions
      const { currentBook } = get()
      if (currentBook) {
        await get().loadBook(currentBook.id)
      }
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  // Parts
  createPart: async (bookId, data) => {
    try {
      const part = await booksAPI.createPart(bookId, data)

      // Refresh book to get updated parts
      await get().loadBook(bookId)

      return part
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  updatePart: async (partId, data) => {
    try {
      const updatedPart = await booksAPI.updatePart(partId, data)

      // Update in current book
      set((state) => {
        if (!state.currentBook) return state

        return {
          currentBook: {
            ...state.currentBook,
            parts: state.currentBook.parts.map((p) =>
              p.id === partId ? { ...p, ...updatedPart } : p
            ),
          },
        }
      })

      return updatedPart
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  deletePart: async (partId) => {
    try {
      await booksAPI.deletePart(partId)

      // Refresh book to handle chapters that were in this part
      const { currentBook } = get()
      if (currentBook) {
        await get().loadBook(currentBook.id)
      }
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  movePart: async (partId, newPosition) => {
    try {
      await booksAPI.movePart(partId, newPosition)

      // Refresh book to get updated positions
      const { currentBook } = get()
      if (currentBook) {
        await get().loadBook(currentBook.id)
      }
    } catch (error) {
      set({ error: error.message })
      throw error
    }
  },

  // UI State
  selectChapter: (chapter) => {
    set({ selectedChapter: chapter })
  },

  clearError: () => {
    set({ error: null })
  },
}))
