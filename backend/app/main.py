from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .routes import auth_router, books_router
from .routes import import_export

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc"
)

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
