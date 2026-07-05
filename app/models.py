from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Category(Base):
    __tablename__ = "categories"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime(timezone=True), server_default=func.now())

    snippets    = relationship("Snippet", back_populates="category", cascade="all, delete-orphan")


class Snippet(Base):
    __tablename__ = "snippets"

    id          = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    title       = Column(String(150), nullable=False)
    command     = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    tags        = Column(ARRAY(String), default=[])
    created_at  = Column(DateTime(timezone=True), server_default=func.now())
    updated_at  = Column(DateTime(timezone=True), onupdate=func.now())

    category    = relationship("Category", back_populates="snippets")
