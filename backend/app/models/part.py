from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class Part(Base):
    """Part model - optional grouping for chapters (Part 1, Part 2, etc.)"""

    __tablename__ = "parts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)

    title = Column(String(500), nullable=False)
    position = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    book = relationship("Book", back_populates="parts")
    chapters = relationship("Chapter", back_populates="part", order_by="Chapter.position")

    def __repr__(self):
        return f"<Part {self.title}>"
