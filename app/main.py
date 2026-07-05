from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from typing import Optional, List
import time
import os

from database import engine, get_db, Base
from models import Category, Snippet
from schemas import (
    CategoryCreate, CategoryResponse,
    SnippetCreate, SnippetUpdate, SnippetResponse
)
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Create tables on startup (if they don't already exist)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="DevOps Knowledge Base",
    description="IEEE Young Protégé 2026 — DevOps Domain · Hirusha Sipsara",
    version="1.0.0"
)

# Allow the frontend (served separately or same-origin) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Prometheus Metrics ────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "app_request_count_total",
    "Total number of requests",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)


# ── System Routes ──────────────────────────────────────────────────────

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check — verifies app and database are both healthy."""
    start = time.time()
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    latency = round((time.time() - start) * 1000, 2)
    REQUEST_COUNT.labels(method="GET", endpoint="/health", status="200").inc()

    return {
        "status": "healthy",
        "database": db_status,
        "latency_ms": latency,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/metrics", tags=["System"])
def metrics():
    """Prometheus metrics scrape endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# ── Category Routes ────────────────────────────────────────────────────

@app.get("/categories", response_model=List[CategoryResponse], tags=["Categories"])
def list_categories(db: Session = Depends(get_db)):
    """List all categories."""
    REQUEST_COUNT.labels(method="GET", endpoint="/categories", status="200").inc()
    return db.query(Category).all()


@app.post("/categories", response_model=CategoryResponse, status_code=201, tags=["Categories"])
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category."""
    existing = db.query(Category).filter(Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    db_category = Category(name=category.name, description=category.description)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    REQUEST_COUNT.labels(method="POST", endpoint="/categories", status="201").inc()
    return db_category


@app.delete("/categories/{category_id}", tags=["Categories"])
def delete_category(category_id: int, db: Session = Depends(get_db)):
    """Delete a category (and its snippets, via cascade)."""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    REQUEST_COUNT.labels(method="DELETE", endpoint="/categories/{id}", status="200").inc()
    return {"message": f"Category '{category.name}' deleted successfully"}


# ── Snippet Routes ─────────────────────────────────────────────────────

def _to_snippet_response(snippet: Snippet) -> dict:
    """Helper — attaches category_name to the snippet response."""
    return {
        "id": snippet.id,
        "category_id": snippet.category_id,
        "category_name": snippet.category.name if snippet.category else None,
        "title": snippet.title,
        "command": snippet.command,
        "description": snippet.description,
        "tags": snippet.tags or [],
        "created_at": snippet.created_at,
        "updated_at": snippet.updated_at,
    }


@app.get("/snippets", response_model=List[SnippetResponse], tags=["Snippets"])
def list_snippets(
    category: Optional[str] = Query(None, description="Filter by category name"),
    db: Session = Depends(get_db)
):
    """List all snippets. Optionally filter by category name."""
    start = time.time()
    query = db.query(Snippet)

    if category:
        query = query.join(Category).filter(Category.name.ilike(category))

    snippets = query.all()
    latency = round((time.time() - start) * 1000, 2)
    REQUEST_COUNT.labels(method="GET", endpoint="/snippets", status="200").inc()
    REQUEST_LATENCY.labels(endpoint="/snippets").observe(latency / 1000)

    return [_to_snippet_response(s) for s in snippets]


@app.get("/snippets/search", response_model=List[SnippetResponse], tags=["Snippets"])
def search_snippets(
    q: str = Query(..., min_length=1, description="Search term"),
    db: Session = Depends(get_db)
):
    """Search snippets by title, command, description, or tag."""
    results = db.query(Snippet).filter(
        or_(
            Snippet.title.ilike(f"%{q}%"),
            Snippet.command.ilike(f"%{q}%"),
            Snippet.description.ilike(f"%{q}%"),
        )
    ).all()

    # Also match tags (array contains search term, case-insensitive best-effort)
    tag_matches = db.query(Snippet).filter(Snippet.tags.any(q.lower())).all()
    for s in tag_matches:
        if s not in results:
            results.append(s)

    REQUEST_COUNT.labels(method="GET", endpoint="/snippets/search", status="200").inc()
    return [_to_snippet_response(s) for s in results]


@app.post("/snippets", response_model=SnippetResponse, status_code=201, tags=["Snippets"])
def create_snippet(snippet: SnippetCreate, db: Session = Depends(get_db)):
    """Create a new snippet."""
    category = db.query(Category).filter(Category.id == snippet.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_snippet = Snippet(
        category_id=snippet.category_id,
        title=snippet.title,
        command=snippet.command,
        description=snippet.description,
        tags=snippet.tags or []
    )
    db.add(db_snippet)
    db.commit()
    db.refresh(db_snippet)

    REQUEST_COUNT.labels(method="POST", endpoint="/snippets", status="201").inc()
    return _to_snippet_response(db_snippet)


@app.get("/snippets/{snippet_id}", response_model=SnippetResponse, tags=["Snippets"])
def get_snippet(snippet_id: int, db: Session = Depends(get_db)):
    """Get a single snippet by ID."""
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
    REQUEST_COUNT.labels(method="GET", endpoint="/snippets/{id}", status="200").inc()
    return _to_snippet_response(snippet)


@app.put("/snippets/{snippet_id}", response_model=SnippetResponse, tags=["Snippets"])
def update_snippet(snippet_id: int, updates: SnippetUpdate, db: Session = Depends(get_db)):
    """Update an existing snippet."""
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    update_data = updates.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(snippet, field, value)

    db.commit()
    db.refresh(snippet)

    REQUEST_COUNT.labels(method="PUT", endpoint="/snippets/{id}", status="200").inc()
    return _to_snippet_response(snippet)


@app.delete("/snippets/{snippet_id}", tags=["Snippets"])
def delete_snippet(snippet_id: int, db: Session = Depends(get_db)):
    """Delete a snippet."""
    snippet = db.query(Snippet).filter(Snippet.id == snippet_id).first()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")

    db.delete(snippet)
    db.commit()
    REQUEST_COUNT.labels(method="DELETE", endpoint="/snippets/{id}", status="200").inc()
    return {"message": f"Snippet '{snippet.title}' deleted successfully"}


# ── Frontend — Serve static HTML UI ────────────────────────────────────
# Mount static files (CSS/JS if separated) and serve index.html at root
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["Frontend"])
def serve_frontend():
    """Serves the frontend dashboard UI."""
    return FileResponse(os.path.join(static_dir, "index.html"))
