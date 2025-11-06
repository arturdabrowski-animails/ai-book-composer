import { api } from './client'

export const booksAPI = {
  // Books
  async createBook(data) {
    return api.post('/api/books', data)
  },

  async listBooks() {
    return api.get('/api/books')
  },

  async getBook(bookId) {
    return api.get(`/api/books/${bookId}`)
  },

  async updateBook(bookId, data) {
    return api.put(`/api/books/${bookId}`, data)
  },

  async deleteBook(bookId) {
    return api.delete(`/api/books/${bookId}`)
  },

  // Chapters
  async createChapter(bookId, data) {
    return api.post(`/api/books/${bookId}/chapters`, data)
  },

  async listChapters(bookId) {
    return api.get(`/api/books/${bookId}/chapters`)
  },

  async getChapter(chapterId) {
    return api.get(`/api/books/chapters/${chapterId}`)
  },

  async updateChapter(chapterId, data) {
    return api.put(`/api/books/chapters/${chapterId}`, data)
  },

  async deleteChapter(chapterId) {
    return api.delete(`/api/books/chapters/${chapterId}`)
  },

  async moveChapter(chapterId, position) {
    return api.put(`/api/books/chapters/${chapterId}/move`, { position })
  },

  // Parts
  async createPart(bookId, data) {
    return api.post(`/api/books/${bookId}/parts`, data)
  },

  async listParts(bookId) {
    return api.get(`/api/books/${bookId}/parts`)
  },

  async updatePart(partId, data) {
    return api.put(`/api/books/parts/${partId}`, data)
  },

  async deletePart(partId) {
    return api.delete(`/api/books/parts/${partId}`)
  },

  async movePart(partId, position) {
    return api.put(`/api/books/parts/${partId}/move`, { position })
  },
}
