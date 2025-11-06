from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status

from ..models import Book, Chapter, Part
from ..schemas.book import (
    BookCreate,
    BookUpdate,
    ChapterCreate,
    ChapterUpdate,
    PartCreate,
    PartUpdate
)


class BookService:
    """Service for book operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ====== Book Operations ======

    async def create_book(self, user_id: UUID, data: BookCreate) -> Book:
        """Create a new book"""
        book = Book(
            user_id=user_id,
            title=data.title,
            subtitle=data.subtitle,
            author=data.author,
            language=data.language,
            publisher=data.publisher,
            isbn=data.isbn,
            genre=data.genre,
        )

        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def get_book(self, book_id: UUID, user_id: UUID) -> Optional[Book]:
        """Get a book with all chapters and parts"""
        result = await self.db.execute(
            select(Book)
            .where(and_(Book.id == book_id, Book.user_id == user_id))
            .options(
                selectinload(Book.parts).selectinload(Part.chapters),
                selectinload(Book.chapters)
            )
        )
        return result.scalar_one_or_none()

    async def list_books(self, user_id: UUID) -> List[Book]:
        """List all user's books"""
        result = await self.db.execute(
            select(Book)
            .where(Book.user_id == user_id)
            .order_by(Book.updated_at.desc())
        )
        return result.scalars().all()

    async def update_book(self, book_id: UUID, user_id: UUID, data: BookUpdate) -> Book:
        """Update book metadata"""
        book = await self.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(book, field, value)

        await self.db.commit()
        await self.db.refresh(book)
        return book

    async def delete_book(self, book_id: UUID, user_id: UUID) -> bool:
        """Delete a book and all its chapters"""
        book = await self.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        await self.db.delete(book)
        await self.db.commit()
        return True

    # ====== Chapter Operations ======

    async def create_chapter(self, book_id: UUID, user_id: UUID, data: ChapterCreate) -> Chapter:
        """Create a new chapter"""
        # Verify book ownership
        book = await self.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Determine position
        if data.position is None:
            # Add at the end
            result = await self.db.execute(
                select(func.max(Chapter.position))
                .where(Chapter.book_id == book_id)
            )
            max_position = result.scalar()
            position = (max_position or 0) + 1
        else:
            position = data.position

        chapter = Chapter(
            book_id=book_id,
            part_id=data.part_id,
            title=data.title,
            content=data.content,
            position=position
        )

        self.db.add(chapter)
        await self.db.commit()
        await self.db.refresh(chapter)
        return chapter

    async def get_chapter(self, chapter_id: UUID) -> Optional[Chapter]:
        """Get a single chapter"""
        result = await self.db.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        return result.scalar_one_or_none()

    async def list_chapters(self, book_id: UUID, user_id: UUID) -> List[Chapter]:
        """List all chapters for a book"""
        # Verify book ownership
        book = await self.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        result = await self.db.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id)
            .order_by(Chapter.position)
        )
        return result.scalars().all()

    async def update_chapter(self, chapter_id: UUID, user_id: UUID, data: ChapterUpdate) -> Chapter:
        """Update chapter content"""
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )

        # Verify book ownership
        book = await self.get_book(chapter.book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(chapter, field, value)

        await self.db.commit()
        await self.db.refresh(chapter)
        return chapter

    async def delete_chapter(self, chapter_id: UUID, user_id: UUID) -> bool:
        """Delete a chapter"""
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )

        # Verify book ownership
        book = await self.get_book(chapter.book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        await self.db.delete(chapter)
        await self.db.commit()
        return True

    async def move_chapter(self, chapter_id: UUID, user_id: UUID, new_position: int) -> Chapter:
        """Move chapter to a new position"""
        chapter = await self.get_chapter(chapter_id)
        if not chapter:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chapter not found"
            )

        # Verify book ownership
        book = await self.get_book(chapter.book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        old_position = chapter.position

        if new_position == old_position:
            return chapter

        # Reorder chapters
        if new_position > old_position:
            # Moving down: shift chapters up
            await self.db.execute(
                update(Chapter)
                .where(
                    and_(
                        Chapter.book_id == chapter.book_id,
                        Chapter.position > old_position,
                        Chapter.position <= new_position
                    )
                )
                .values(position=Chapter.position - 1)
            )
        else:
            # Moving up: shift chapters down
            await self.db.execute(
                update(Chapter)
                .where(
                    and_(
                        Chapter.book_id == chapter.book_id,
                        Chapter.position >= new_position,
                        Chapter.position < old_position
                    )
                )
                .values(position=Chapter.position + 1)
            )

        # Update chapter position
        chapter.position = new_position
        await self.db.commit()
        await self.db.refresh(chapter)
        return chapter

    # ====== Part Operations ======

    async def create_part(self, book_id: UUID, user_id: UUID, data: PartCreate) -> Part:
        """Create a new part"""
        # Verify book ownership
        book = await self.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        # Determine position
        if data.position is None:
            result = await self.db.execute(
                select(func.max(Part.position))
                .where(Part.book_id == book_id)
            )
            max_position = result.scalar()
            position = (max_position or 0) + 1
        else:
            position = data.position

        part = Part(
            book_id=book_id,
            title=data.title,
            position=position
        )

        self.db.add(part)
        await self.db.commit()
        await self.db.refresh(part)
        return part

    async def get_part(self, part_id: UUID) -> Optional[Part]:
        """Get a single part"""
        result = await self.db.execute(
            select(Part)
            .where(Part.id == part_id)
            .options(selectinload(Part.chapters))
        )
        return result.scalar_one_or_none()

    async def list_parts(self, book_id: UUID, user_id: UUID) -> List[Part]:
        """List all parts for a book"""
        # Verify book ownership
        book = await self.get_book(book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Book not found"
            )

        result = await self.db.execute(
            select(Part)
            .where(Part.book_id == book_id)
            .order_by(Part.position)
            .options(selectinload(Part.chapters))
        )
        return result.scalars().all()

    async def update_part(self, part_id: UUID, user_id: UUID, data: PartUpdate) -> Part:
        """Update part"""
        part = await self.get_part(part_id)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        # Verify book ownership
        book = await self.get_book(part.book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(part, field, value)

        await self.db.commit()
        await self.db.refresh(part)
        return part

    async def delete_part(self, part_id: UUID, user_id: UUID) -> bool:
        """Delete a part (chapters become ungrouped)"""
        part = await self.get_part(part_id)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        # Verify book ownership
        book = await self.get_book(part.book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        # Chapters will have part_id set to NULL (due to ON DELETE SET NULL)
        await self.db.delete(part)
        await self.db.commit()
        return True

    async def move_part(self, part_id: UUID, user_id: UUID, new_position: int) -> Part:
        """Move part to a new position"""
        part = await self.get_part(part_id)
        if not part:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Part not found"
            )

        # Verify book ownership
        book = await self.get_book(part.book_id, user_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )

        old_position = part.position

        if new_position == old_position:
            return part

        # Reorder parts
        if new_position > old_position:
            await self.db.execute(
                update(Part)
                .where(
                    and_(
                        Part.book_id == part.book_id,
                        Part.position > old_position,
                        Part.position <= new_position
                    )
                )
                .values(position=Part.position - 1)
            )
        else:
            await self.db.execute(
                update(Part)
                .where(
                    and_(
                        Part.book_id == part.book_id,
                        Part.position >= new_position,
                        Part.position < old_position
                    )
                )
                .values(position=Part.position + 1)
            )

        # Update part position
        part.position = new_position
        await self.db.commit()
        await self.db.refresh(part)
        return part
