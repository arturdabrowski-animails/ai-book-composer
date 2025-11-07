from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


# ====== Chapter Schemas ======

class ChapterCreate(BaseModel):
    """Schema for creating a chapter"""
    title: str
    content: str = ""
    part_id: Optional[UUID] = None
    position: Optional[int] = None


class ChapterUpdate(BaseModel):
    """Schema for updating a chapter"""
    title: Optional[str] = None
    content: Optional[str] = None
    part_id: Optional[UUID] = None


class ChapterMove(BaseModel):
    """Schema for moving a chapter"""
    position: int


class ChapterResponse(BaseModel):
    """Schema for chapter response"""
    id: UUID
    book_id: UUID
    part_id: Optional[UUID]
    title: str
    content: str
    position: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ====== Part Schemas ======

class PartCreate(BaseModel):
    """Schema for creating a part"""
    title: str
    position: Optional[int] = None


class PartUpdate(BaseModel):
    """Schema for updating a part"""
    title: Optional[str] = None


class PartMove(BaseModel):
    """Schema for moving a part"""
    position: int


class PartResponse(BaseModel):
    """Schema for part response"""
    id: UUID
    book_id: UUID
    title: str
    position: int
    created_at: datetime
    chapters: List[ChapterResponse] = []

    class Config:
        from_attributes = True


# ====== Book Schemas ======

class BookCreate(BaseModel):
    """Schema for creating a book"""
    title: str
    subtitle: Optional[str] = None
    author: str
    language: str = "pl"
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None


class BookUpdate(BaseModel):
    """Schema for updating a book"""
    title: Optional[str] = None
    subtitle: Optional[str] = None
    author: Optional[str] = None
    language: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    genre: Optional[str] = None


class BookListResponse(BaseModel):
    """Schema for book list response (minimal info)"""
    id: UUID
    title: str
    subtitle: Optional[str]
    author: str
    language: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookResponse(BaseModel):
    """Schema for full book response with parts and chapters"""
    id: UUID
    user_id: UUID
    title: str
    subtitle: Optional[str]
    author: str
    language: str
    publisher: Optional[str]
    isbn: Optional[str]
    genre: Optional[str]
    book_metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    parts: List[PartResponse] = []
    chapters: List[ChapterResponse] = []

    class Config:
        from_attributes = True
