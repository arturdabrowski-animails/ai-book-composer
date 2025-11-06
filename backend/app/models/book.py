from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class Book(Base):
    """Book model"""

    __tablename__ = "books"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(500), nullable=False)
    subtitle = Column(String(500))
    author = Column(String(255), nullable=False)
    language = Column(String(10), default="pl")
    publisher = Column(String(255))
    isbn = Column(String(20))
    genre = Column(String(100))

    metadata = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="books")
    parts = relationship("Part", back_populates="book", cascade="all, delete-orphan", order_by="Part.position")
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan", order_by="Chapter.position")

    def __repr__(self):
        return f"<Book {self.title}>"
