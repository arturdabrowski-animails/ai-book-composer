from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..core import get_db, get_current_user_dev
from ..models import User
from ..services import BookService
from ..schemas import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookListResponse,
    ChapterCreate,
    ChapterUpdate,
    ChapterResponse,
    ChapterMove,
    PartCreate,
    PartUpdate,
    PartResponse,
    PartMove
)

router = APIRouter(prefix="/api/books", tags=["books"])


# ====== Book Routes ======

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Create a new book"""
    service = BookService(db)
    book = await service.create_book(current_user.id, book_data)

    # Reload with relationships
    book = await service.get_book(book.id, current_user.id)
    return book


@router.get("", response_model=List[BookListResponse])
async def list_books(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """List all user's books"""
    service = BookService(db)
    books = await service.list_books(current_user.id)
    return books


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Get a single book with all chapters and parts"""
    service = BookService(db)
    book = await service.get_book(book_id, current_user.id)

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    return book


@router.put("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Update book metadata"""
    service = BookService(db)
    book = await service.update_book(book_id, current_user.id, book_data)

    # Reload with relationships
    book = await service.get_book(book.id, current_user.id)
    return book


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Delete a book"""
    service = BookService(db)
    await service.delete_book(book_id, current_user.id)


# ====== Chapter Routes ======

@router.post("/{book_id}/chapters", response_model=ChapterResponse, status_code=status.HTTP_201_CREATED)
async def create_chapter(
    book_id: UUID,
    chapter_data: ChapterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Create a new chapter"""
    service = BookService(db)
    chapter = await service.create_chapter(book_id, current_user.id, chapter_data)
    return chapter


@router.get("/{book_id}/chapters", response_model=List[ChapterResponse])
async def list_chapters(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """List all chapters for a book"""
    service = BookService(db)
    chapters = await service.list_chapters(book_id, current_user.id)
    return chapters


@router.get("/chapters/{chapter_id}", response_model=ChapterResponse)
async def get_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Get a single chapter"""
    service = BookService(db)
    chapter = await service.get_chapter(chapter_id)

    if not chapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chapter not found"
        )

    # Verify ownership
    await service.get_book(chapter.book_id, current_user.id)

    return chapter


@router.put("/chapters/{chapter_id}", response_model=ChapterResponse)
async def update_chapter(
    chapter_id: UUID,
    chapter_data: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Update chapter content"""
    service = BookService(db)
    chapter = await service.update_chapter(chapter_id, current_user.id, chapter_data)
    return chapter


@router.delete("/chapters/{chapter_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chapter(
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Delete a chapter"""
    service = BookService(db)
    await service.delete_chapter(chapter_id, current_user.id)


@router.put("/chapters/{chapter_id}/move", response_model=ChapterResponse)
async def move_chapter(
    chapter_id: UUID,
    move_data: ChapterMove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Reorder a chapter"""
    service = BookService(db)
    chapter = await service.move_chapter(chapter_id, current_user.id, move_data.position)
    return chapter


# ====== Part Routes ======

@router.post("/{book_id}/parts", response_model=PartResponse, status_code=status.HTTP_201_CREATED)
async def create_part(
    book_id: UUID,
    part_data: PartCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Create a new part"""
    service = BookService(db)
    part = await service.create_part(book_id, current_user.id, part_data)

    # Reload with chapters
    part = await service.get_part(part.id)
    return part


@router.get("/{book_id}/parts", response_model=List[PartResponse])
async def list_parts(
    book_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """List all parts for a book"""
    service = BookService(db)
    parts = await service.list_parts(book_id, current_user.id)
    return parts


@router.put("/parts/{part_id}", response_model=PartResponse)
async def update_part(
    part_id: UUID,
    part_data: PartUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Update a part"""
    service = BookService(db)
    part = await service.update_part(part_id, current_user.id, part_data)

    # Reload with chapters
    part = await service.get_part(part.id)
    return part


@router.delete("/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_part(
    part_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Delete a part"""
    service = BookService(db)
    await service.delete_part(part_id, current_user.id)


@router.put("/parts/{part_id}/move", response_model=PartResponse)
async def move_part(
    part_id: UUID,
    move_data: PartMove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user_dev)
):
    """Reorder a part"""
    service = BookService(db)
    part = await service.move_part(part_id, current_user.id, move_data.position)

    # Reload with chapters
    part = await service.get_part(part.id)
    return part
