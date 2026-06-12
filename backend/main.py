"""
main.py — FastAPI-приложение.

Запуск:
    uvicorn backend.main:app --reload --port 8000

Маршруты:
    GET  /              → Главная страница (HTML)
    POST /api/chat      → Отправить сообщение, получить ответ
    GET  /api/history   → История чата сессии
    POST /api/clear     → Очистить историю
    GET  /api/books     → Поиск книг (query params: title / author)
    GET  /api/books/{id}→ Карточка книги
"""

import uuid
import sys
import os

from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Добавляем корень проекта в sys.path, чтобы импорты работали
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.chatbot import ChatBot
from backend.db_connector import DatabaseConnector
from database.init_db import init_database

# ── Инициализация ─────────────────────────────────────────────────────────────
init_database()  # Создаёт таблицы и заполняет БД при первом запуске

app = FastAPI(
    title="Библиотечный чат-бот",
    description="API для чат-бота электронной библиотеки университета",
    version="1.0.0",
)

# CORS — разрешает встраивание виджета на сторонние сайты (например lib.dulaty.kz)
# В продакшене замените "*" на конкретный домен сайта для безопасности:
#   allow_origins=["https://lib.dulaty.kz"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы (CSS, JS)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "static")),
    name="static",
)

# Шаблоны Jinja2
templates = Jinja2Templates(
    directory=os.path.join(os.path.dirname(__file__), "..", "frontend", "templates")
)

bot = ChatBot()
db  = DatabaseConnector()


# ── Модели запросов ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None  # Если None — создаётся автоматически


class ClearRequest(BaseModel):
    session_id: str


# ── Маршруты ─────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Главная страница с чат-интерфейсом."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/widget-demo", response_class=HTMLResponse)
async def widget_demo(request: Request):
    """
    Демо-страница, показывающая, как виджет выглядит на обычном сайте.
    Имитирует страницу lib.dulaty.kz с встроенным виджетом в углу.
    """
    return templates.TemplateResponse("widget_demo.html", {"request": request})


@app.post("/api/chat")
async def chat(body: ChatRequest):
    """
    Принимает сообщение пользователя, возвращает ответ бота.
    Если session_id не передан — генерирует новый.
    """
    session_id = body.session_id or str(uuid.uuid4())
    if not body.message.strip():
        raise HTTPException(status_code=400, detail="Сообщение не может быть пустым")

    response = bot.process(body.message, session_id)
    response["session_id"] = session_id
    return JSONResponse(content=response)


@app.get("/api/history")
async def history(
    session_id: str = Query(..., description="ID сессии"),
    limit: int = Query(50, ge=1, le=200)
):
    """Возвращает историю переписки для данной сессии."""
    messages = db.get_history(session_id, limit)
    return {"session_id": session_id, "messages": messages}


@app.post("/api/clear")
async def clear_history(body: ClearRequest):
    """Очищает историю чата для данной сессии."""
    db.clear_history(body.session_id)
    return {"ok": True, "session_id": body.session_id}


@app.get("/api/books")
async def search_books(
    title:  str | None = Query(None, description="Поиск по названию"),
    author: str | None = Query(None, description="Поиск по автору"),
):
    """
    Поиск книг через REST API.
    Примеры:
      GET /api/books?title=булгаков
      GET /api/books?author=толстой
    """
    if title:
        books = db.search_by_title(title)
    elif author:
        books = db.search_by_author(author)
    else:
        raise HTTPException(status_code=400, detail="Укажите параметр title или author")
    return {"books": books, "count": len(books)}


@app.get("/api/books/{book_id}")
async def get_book(book_id: int):
    """Возвращает полную карточку книги по ID."""
    book = db.get_book_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail=f"Книга #{book_id} не найдена")
    return book
