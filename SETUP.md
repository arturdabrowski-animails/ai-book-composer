# Book Composer - Setup Guide

Complete setup guide for Phase 1 (Core Editor).

## Prerequisites

- **Python 3.11+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **PostgreSQL 14+** - Database
- **pip** - Python package manager
- **npm** - Node package manager

## Step-by-Step Setup

### 1. Clone Repository

```bash
git clone https://github.com/arturdabrowski-animails/ai-book-composer.git
cd ai-book-composer
```

### 2. Database Setup

#### Install PostgreSQL

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

#### Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database (inside psql)
CREATE DATABASE bookcomposer;
CREATE USER bookuser WITH PASSWORD 'bookpass123';
GRANT ALL PRIVILEGES ON DATABASE bookcomposer TO bookuser;
\q
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file with your settings:
# DATABASE_URL=postgresql+asyncpg://bookuser:bookpass123@localhost/bookcomposer
# SECRET_KEY=your-secret-key-here-change-in-production

# Run migrations
alembic upgrade head

# Start backend server
python -m uvicorn app.main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### 4. Frontend Setup

Open a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at: http://localhost:5173

### 5. First Steps

1. Open http://localhost:5173 in your browser
2. Click "Sign up" to create an account
3. Create your first book
4. Add chapters and start writing!

## Troubleshooting

### Database Connection Issues

**Error:** `could not connect to server`

**Solution:**
```bash
# Check if PostgreSQL is running
# macOS:
brew services list
# Linux:
sudo systemctl status postgresql

# Restart if needed:
brew services restart postgresql  # macOS
sudo systemctl restart postgresql  # Linux
```

### Backend Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>

# Or use a different port:
python -m uvicorn app.main:app --reload --port 8001
```

### Frontend Build Issues

**Error:** `Cannot find module`

**Solution:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Alembic Migration Issues

**Error:** `Target database is not up to date`

**Solution:**
```bash
cd backend
# Check current migration status
alembic current

# Reset and rerun migrations
alembic downgrade base
alembic upgrade head
```

## Development Tips

### Backend Development

```bash
# Create a new migration (after model changes)
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Database Management

```bash
# Connect to database
psql -U bookuser -d bookcomposer

# Useful commands:
\dt                  # List tables
\d users            # Describe users table
SELECT * FROM books; # Query books
\q                  # Quit
```

## Next Steps

Once Phase 1 is working:

- [ ] **Phase 2: Import/Export** - Add EPUB import and enhanced export
- [ ] **Phase 3: Preview & Polish** - Full-screen preview and export dialog

## Support

For issues, please check:
- Backend logs in terminal running uvicorn
- Frontend console in browser DevTools (F12)
- PostgreSQL logs: `/var/log/postgresql/` (Linux) or check with `brew services`

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (React)                  │
│  ┌──────────┬──────────────┬─────────────────────┐ │
│  │ Chapters │    Editor    │  Preview (Optional)  │ │
│  │   Tree   │   (Monaco)   │    (Markdown)       │ │
│  └──────────┴──────────────┴─────────────────────┘ │
└───────────────────┬─────────────────────────────────┘
                    │ REST API (JSON)
┌───────────────────┴─────────────────────────────────┐
│              Backend (FastAPI)                       │
│  ┌─────────────┬──────────────┬─────────────────┐  │
│  │   Routes    │   Services   │     Models      │  │
│  │  (API)      │  (Business)  │  (Database)     │  │
│  └─────────────┴──────────────┴─────────────────┘  │
└───────────────────┬─────────────────────────────────┘
                    │ SQLAlchemy (async)
┌───────────────────┴─────────────────────────────────┐
│              PostgreSQL Database                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ users │ books │ parts │ chapters            │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Phase 1 Features

- [x] User authentication (JWT)
- [x] Multi-book management
- [x] Chapter CRUD operations
- [x] Part grouping (optional)
- [x] Monaco Markdown editor
- [x] Auto-save (2-second debounce)
- [x] Chapter tree with drag & drop
- [x] Live Markdown preview (toggle)
- [x] PostgreSQL persistence

Happy writing! 📖✍️
