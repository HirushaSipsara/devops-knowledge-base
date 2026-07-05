from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


# ── Category Schemas ─────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="Docker")
    description: Optional[str] = Field(None, example="Container-related commands and tools")


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Snippet Schemas ──────────────────────────────────────────────────

class SnippetCreate(BaseModel):
    category_id: int = Field(..., example=1)
    title: str = Field(..., min_length=1, max_length=150, example="Build a Docker image")
    command: str = Field(..., example="docker build -t myapp:latest .")
    description: Optional[str] = Field(None, example="Builds a Docker image from the current directory")
    tags: Optional[List[str]] = Field(default=[], example=["docker", "build"])


class SnippetUpdate(BaseModel):
    category_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    command: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class SnippetResponse(BaseModel):
    id: int
    category_id: int
    category_name: Optional[str] = None
    title: str
    command: str
    description: Optional[str]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}
