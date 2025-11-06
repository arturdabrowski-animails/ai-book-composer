# Book Composer API Documentation

Base URL: `http://localhost:8000`

## Authentication

All endpoints except `/api/auth/register` and `/api/auth/login` require authentication via JWT Bearer token.

### Headers

```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2025-01-06T00:00:00Z"
}
```

#### Login
```http
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "created_at": "2025-01-06T00:00:00Z"
}
```

### Books

#### Create Book
```http
POST /api/books
```

**Request Body:**
```json
{
  "title": "My Book",
  "subtitle": "A great story",
  "author": "John Doe",
  "language": "en",
  "publisher": "Self-published",
  "isbn": "978-0-123456-78-9",
  "genre": "Fiction"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "My Book",
  "subtitle": "A great story",
  "author": "John Doe",
  "language": "en",
  "publisher": "Self-published",
  "isbn": "978-0-123456-78-9",
  "genre": "Fiction",
  "metadata": {},
  "created_at": "2025-01-06T00:00:00Z",
  "updated_at": "2025-01-06T00:00:00Z",
  "parts": [],
  "chapters": []
}
```

#### List Books
```http
GET /api/books
```

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "title": "My Book",
    "subtitle": "A great story",
    "author": "John Doe",
    "language": "en",
    "created_at": "2025-01-06T00:00:00Z",
    "updated_at": "2025-01-06T00:00:00Z"
  }
]
```

#### Get Book
```http
GET /api/books/{book_id}
```

**Response:** `200 OK` - Returns full book with parts and chapters

#### Update Book
```http
PUT /api/books/{book_id}
```

**Request Body:** (all fields optional)
```json
{
  "title": "Updated Title",
  "author": "Updated Author"
}
```

#### Delete Book
```http
DELETE /api/books/{book_id}
```

**Response:** `204 No Content`

### Chapters

#### Create Chapter
```http
POST /api/books/{book_id}/chapters
```

**Request Body:**
```json
{
  "title": "Chapter 1",
  "content": "# Chapter 1\n\nContent goes here...",
  "part_id": "uuid or null",
  "position": 1
}
```

#### List Chapters
```http
GET /api/books/{book_id}/chapters
```

#### Get Chapter
```http
GET /api/books/chapters/{chapter_id}
```

#### Update Chapter
```http
PUT /api/books/chapters/{chapter_id}
```

**Request Body:** (all fields optional)
```json
{
  "title": "Updated Chapter Title",
  "content": "Updated content...",
  "part_id": "uuid or null"
}
```

#### Delete Chapter
```http
DELETE /api/books/chapters/{chapter_id}
```

**Response:** `204 No Content`

#### Move Chapter
```http
PUT /api/books/chapters/{chapter_id}/move
```

**Request Body:**
```json
{
  "position": 3
}
```

### Parts

#### Create Part
```http
POST /api/books/{book_id}/parts
```

**Request Body:**
```json
{
  "title": "Part 1: The Beginning",
  "position": 1
}
```

#### List Parts
```http
GET /api/books/{book_id}/parts
```

#### Update Part
```http
PUT /api/books/parts/{part_id}
```

#### Delete Part
```http
DELETE /api/books/parts/{part_id}
```

**Note:** Chapters in this part will have `part_id` set to NULL

#### Move Part
```http
PUT /api/books/parts/{part_id}/move
```

**Request Body:**
```json
{
  "position": 2
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Book not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## Interactive Documentation

Visit these URLs when the backend is running:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
