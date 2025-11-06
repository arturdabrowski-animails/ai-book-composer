# Book Composer

A professional book editor and typesetter combining the best of Notion, Scrivener, and InDesign.

## Features

- **Multi-chapter editor** with Monaco-based Markdown editing
- **Visual chapter tree** with drag & drop reordering
- **Auto-save** functionality (2-second debounce)
- **Professional typography** for Polish and English text
- **Import/Export** EPUB, PDF, and DOCX formats
- **Live preview** of final book layout

## Tech Stack

**Backend:**
- FastAPI (Python 3.11+)
- PostgreSQL
- SQLAlchemy 2.0 (async)
- JWT authentication

**Frontend:**
- React 18
- Vite
- Monaco Editor
- Zustand (state management)
- Tailwind CSS
- DND Kit (drag & drop)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create database
createdb bookcomposer

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Run migrations
alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload --port 8000
```

Backend will run at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend will run at http://localhost:5173

## Project Structure

```
ai-book-composer/
├── backend/
│   ├── app/
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routes/        # API endpoints
│   │   ├── services/      # Business logic
│   │   └── main.py        # FastAPI app
│   ├── alembic/           # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page layouts
│   │   ├── stores/        # Zustand stores
│   │   ├── api/           # API client
│   │   └── styles/        # CSS files
│   └── package.json
└── docs/                  # Documentation
```

## Development Phases

### Phase 1: Core Editor ✅ COMPLETE
- ✅ PostgreSQL database setup
- ✅ User authentication (JWT)
- ✅ Multi-book management
- ✅ Multi-chapter editing
- ✅ Auto-save functionality (2s debounce)
- ✅ Chapter tree with parts grouping
- ✅ Monaco Markdown editor
- ✅ Optional live preview
- ✅ RESTful API with full CRUD

### Phase 2: Import/Export (Planned)
- EPUB import from existing books
- Enhanced EPUB export with typography
- PDF generation (print-ready)
- DOCX export (editable)

### Phase 3: Preview & Polish (Planned)
- Full-screen professional preview
- Export dialog with options
- Chapter-by-chapter navigation
- Professional typography rendering

## Documentation

- **Setup Guide:** [SETUP.md](./SETUP.md) - Detailed installation and configuration
- **API Reference:** [docs/API.md](./docs/API.md) - Complete API documentation

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT
