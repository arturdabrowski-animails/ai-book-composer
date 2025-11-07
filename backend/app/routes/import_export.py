from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
import tempfile
import os
import logging
import traceback
from ebooklib import epub

from ..core import get_db, get_current_user_dev
from ..models import User
from ..services.epub_importer import EPUBImporter
from ..services.epub_builder import EPUBBuilder
from ..services.pdf_exporter import PDFExporter
from ..services.book_service import BookService
from ..schemas import BookCreate, ChapterCreate, ExportOptions

router = APIRouter(prefix="/api", tags=["import-export"])
logger = logging.getLogger(__name__)


@router.post("/import/epub")
async def import_epub(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """
    Import EPUB file and create book with chapters.

    Returns the created book with all chapters.
    """
    try:
        # Validate file
        if not file.filename.endswith('.epub'):
            raise HTTPException(400, "File must be .epub format")

        logger.info(f"Importing EPUB file: {file.filename}")

        # Read file
        content = await file.read()
        logger.info(f"File size: {len(content)} bytes")

        # Import EPUB
        importer = EPUBImporter()
        try:
            data = importer.import_file(content)
            logger.info(f"Parsed EPUB: {data['metadata'].get('title', 'Unknown')}")
        except Exception as e:
            logger.error(f"Failed to parse EPUB: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(400, f"Failed to parse EPUB: {str(e)}")

        # Create book
        book_service = BookService(db)

        book_data = BookCreate(**data['metadata'])
        book = await book_service.create_book(current_user.id, book_data)
        logger.info(f"Created book: {book.id}")

        # Create chapters
        for idx, chapter_data in enumerate(data['chapters']):
            chapter = ChapterCreate(**chapter_data)
            await book_service.create_chapter(book.id, current_user.id, chapter)
            logger.debug(f"Created chapter {idx + 1}/{len(data['chapters'])}")

        # Return complete book
        result = await book_service.get_book(book.id, current_user.id)
        logger.info(f"Import completed successfully: {book.id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during import: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(500, f"Import failed: {str(e)}")


@router.post("/books/{book_id}/export/epub")
async def export_epub(
    book_id: UUID,
    options: ExportOptions = ExportOptions(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Export book as EPUB"""
    try:
        logger.info(f"Exporting book {book_id} as EPUB")

        # Get book with chapters
        book_service = BookService(db)
        book = await book_service.get_book(book_id, current_user.id)

        if not book:
            raise HTTPException(404, "Book not found")

        # Build EPUB
        builder = EPUBBuilder()
        epub_book = builder.build_from_book(book, options)

        # Write to temp file
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as tmp:
            epub.write_epub(tmp.name, epub_book)
            tmp_path = tmp.name

        # Schedule cleanup
        background_tasks.add_task(os.unlink, tmp_path)

        # Return file
        filename = f"{book.title.replace(' ', '_')}.epub"
        logger.info(f"EPUB export successful: {filename}")

        return FileResponse(
            path=tmp_path,
            media_type='application/epub+zip',
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export EPUB: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(500, f"Export failed: {str(e)}")


@router.post("/books/{book_id}/export/pdf")
async def export_pdf(
    book_id: UUID,
    options: ExportOptions = ExportOptions(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Export book as PDF"""
    try:
        logger.info(f"Exporting book {book_id} as PDF")

        book_service = BookService(db)
        book = await book_service.get_book(book_id, current_user.id)

        if not book:
            raise HTTPException(404, "Book not found")

        # Generate PDF
        exporter = PDFExporter()
        pdf_bytes = exporter.export(book, options)

        # Save to temp file and return
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        # Schedule cleanup
        background_tasks.add_task(os.unlink, tmp_path)

        filename = f"{book.title.replace(' ', '_')}.pdf"
        logger.info(f"PDF export successful: {filename}")

        return FileResponse(
            path=tmp_path,
            media_type='application/pdf',
            filename=filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export PDF: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(500, f"Export failed: {str(e)}")
