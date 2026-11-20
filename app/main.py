from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator
from sqlalchemy import func, or_, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .db import Base, engine
from .models import Engine
from .seed import SEED_ENGINES

BASE_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with Session(engine) as session:
        count = session.scalar(select(func.count()).select_from(Engine)) or 0
        if count == 0:
            session.add_all(Engine(**row) for row in SEED_ENGINES)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
    yield


app = FastAPI(
    title="Database Labs",
    description="A small live index for 26 hands-on database labs.",
    version="1.0.0",
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


class EngineIn(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    category: str = Field(min_length=2, max_length=80)
    runtime: Literal["docker", "cloud"] = "docker"
    repo_url: HttpUrl
    notes: str = Field(default="", max_length=500)

    @field_validator("name", "category", "notes")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()


class EngineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    runtime: str
    repo_url: str
    notes: str
    created_at: datetime


def db_session():
    from .db import get_db

    yield from get_db()


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/healthz")
def healthz(response: Response):
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001
        response.status_code = 503
        return JSONResponse(
            status_code=503,
            content={"status": "error", "detail": type(exc).__name__},
        )
    return {
        "status": "ok",
        "database": engine.dialect.name,
        "version": "1.0.0",
    }


@app.get("/api/stats")
def stats(db: Session = Depends(db_session)):
    total = db.scalar(select(func.count()).select_from(Engine)) or 0
    docker = (
        db.scalar(
            select(func.count()).select_from(Engine).where(Engine.runtime == "docker")
        )
        or 0
    )
    cloud = total - docker
    categories = db.scalar(select(func.count(func.distinct(Engine.category)))) or 0
    return {
        "total": total,
        "docker": docker,
        "cloud": cloud,
        "categories": categories,
    }


@app.get("/api/engines", response_model=list[EngineOut])
def list_engines(
    q: str | None = Query(default=None, max_length=80),
    category: str | None = Query(default=None, max_length=80),
    runtime: Literal["docker", "cloud"] | None = None,
    db: Session = Depends(db_session),
):
    statement = select(Engine)
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(
            or_(Engine.name.ilike(pattern), Engine.category.ilike(pattern))
        )
    if category:
        statement = statement.where(Engine.category == category)
    if runtime:
        statement = statement.where(Engine.runtime == runtime)
    statement = statement.order_by(Engine.category, Engine.name)
    return db.scalars(statement).all()


@app.get("/api/categories", response_model=list[str])
def list_categories(db: Session = Depends(db_session)):
    return list(db.scalars(select(Engine.category).distinct().order_by(Engine.category)))


@app.post("/api/engines", response_model=EngineOut, status_code=201)
def create_engine(payload: EngineIn, db: Session = Depends(db_session)):
    existing = db.scalar(
        select(Engine).where(func.lower(Engine.name) == payload.name.lower())
    )
    if existing:
        raise HTTPException(status_code=409, detail="An engine with that name already exists.")

    row = Engine(
        name=payload.name,
        category=payload.category,
        runtime=payload.runtime,
        repo_url=str(payload.repo_url),
        notes=payload.notes,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="An engine with that name already exists.") from exc
    db.refresh(row)
    return row


@app.delete("/api/engines/{engine_id}", status_code=204)
def delete_engine(engine_id: int, db: Session = Depends(db_session)):
    row = db.get(Engine, engine_id)
    if not row:
        raise HTTPException(status_code=404, detail="Engine not found.")
    db.delete(row)
    db.commit()
    return Response(status_code=204)
