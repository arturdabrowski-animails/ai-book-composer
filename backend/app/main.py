from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import logging

from .core.config import settings
from .routes import auth_router, books_router
from .routes import import_export

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)


@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup"""
    logger.info("🚀 Starting Book Composer API...")
    logger.info("📊 Running database migrations...")

    try:
        # Run alembic migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info("✅ Database migrations completed successfully!")
        if result.stdout:
            logger.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Migration failed: {e}")
        if e.stdout:
            logger.error(f"STDOUT: {e.stdout}")
        if e.stderr:
            logger.error(f"STDERR: {e.stderr}")
        # Don't crash the app, just log the error
        logger.warning("⚠️  Continuing without migrations - database may not be initialized")
    except Exception as e:
        logger.error(f"❌ Unexpected error during migration: {e}")
        logger.warning("⚠️  Continuing without migrations - database may not be initialized")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(books_router)
app.include_router(import_export.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Book Composer API",
        "version": "2.0.1",
        "build_date": "2025-11-07T11:30:00Z",
        "phase": "Phase 2: Import/Export (PDF temporarily disabled)",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/version")
async def version():
    """Version endpoint for frontend to check"""
    return {
        "version": "2.0.1",
        "build_date": "2025-11-07T11:30:00Z",
        "features": {
            "epub_import": True,
            "epub_export": True,
            "pdf_export": False  # Temporarily disabled
        }
    }
