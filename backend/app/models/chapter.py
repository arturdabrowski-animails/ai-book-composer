from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from ..core.database import Base


class Chapter(Base):
    """Chapter model"""

    __tablename__ = "chapters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    book_id = Column(UUID(as_uuid=True), ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    part_id = Column(UUID(as_uuid=True), ForeignKey("parts.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(500), nullable=False)
    content = Column(Text, default="")
    position = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    book = relationship("Book", back_populates="chapters")
    part = relationship("Part", back_populates="chapters")

    def __repr__(self):
        return f"<Chapter {self.title}>"
