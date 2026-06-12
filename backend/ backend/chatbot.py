"""
chatbot.py — Логика обработки сообщений и генерации ответов.

Определяет намерение пользователя (intent) и формирует
структурированный ответ на основе данных из БД.
"""

import re
from backend.db_connector import DatabaseConnector


# Ключевые слова для определения намерений
INTENT_PATTERNS = {
    "search_title": [
        r"найди?\s+книгу?\s+(.+)",
        r"поищи?\s+(.+)",
        r"есть\s+ли\s+книга\s+(.+)",
        r"книга\s+[«\"']?(.+?)[»\"']?\s*$",
        r"название\s+[«\"']?(.+?)[»\"']?",
        r"поиск\s+по\s+названию\s+(.+)",
        r"ищу\s+книгу?\s+(.+)",
    ],
    "search_author": [
        r"автор\s+(.+)",
        r"книги\s+(.+)",
        r"произведения\s+(.+)",
        r"поиск\s+по\s+автору\s+(.+)",
        r"работы\s+(.+)",
        r"написал\s+(.+)",
    ],
    "book_info": [
        r"информация\s+(?:о\s+книге\s+)?(?:об?\s+)?#?(\d+)",
        r"подробнее\s+(?:о\s+)?#?(\d+)",
        r"книга\s+#?(\d+)",
        r"id\s*[=:]?\s*(\d+)",
    ],
    "faq": [
        r"когда",
        r"как\s+(?:получить|взять|оформить|записаться)",
        r"сколько",
        r"можно\s+ли",
        r"есть\s+ли\s+(?:wifi|wi-fi|интернет|электронн|принтер|ксерокс)",
        r"штраф",
        r"правила",
        r"режим",
        r"часы\s+работы",
    ],
    "greeting": [
        r"^привет",
        r"^здравствуй",
        r"^добрый\s+(?:день|вечер|утро)",
        r"^салам",
        r"^hello",
        r"^hi\b",
    ],
    "help": [
        r"помоги",
        r"что\s+(?:ты\s+)?умеешь",
        r"команды",
        r"что\s+можно\s+(?:спросить|делать)",
        r"справка",
        r"помощь",
    ],
    "clear": [
        r"^(?:очисти|сбрось|удали)\s+(?:историю|чат)",
    ],
}

GREETING_RESPONSE = (
    "👋 Привет! Я чат-бот библиотеки университета.\n\n"
    "Я могу помочь вам:\n"
    "• 🔍 **Найти книгу** — просто напишите её название\n"
    "• ✍️ **Найти по автору** — например: *автор Булгаков*\n"
    "• 📖 **Узнать подробности** — напишите *книга #5*\n"
    "• ❓ **Ответить на вопросы** о библиотеке\n\n"
    "Чем могу помочь?"
)

HELP_RESPONSE = (
    "📚 **Что я умею:**\n\n"
    "**Поиск книг:**\n"
    "• *Мастер и Маргарита* — поиск по названию\n"
    "• *автор Достоевский* — все книги автора\n"
    "• *книга #3* — подробная информация по ID\n\n"
    "**Вопросы о библиотеке:**\n"
    "• *Когда работает библиотека?*\n"
    "• *Как получить читательский билет?*\n"
    "• *Можно ли распечатать?*\n"
    "• *Есть ли электронные книги?*\n\n"
    "**Управление:**\n"
    "• *очистить историю* — стереть переписку"
)

NOT_FOUND_RESPONSE = (
    "😕 Я не совсем понял ваш запрос.\n\n"
    "Попробуйте:\n"
    "• Написать название книги: *Война и мир*\n"
    "• Поиск по автору: *автор Толстой*\n"
    "• Написать *помощь* для списка команд"
)


class ChatBot:
    """Основной класс чат-бота. Принимает текст, возвращает ответ."""

    def __init__(self):
        self.db = DatabaseConnector()

    def process(self, user_message: str, session_id: str) -> dict:
        """
        Обрабатывает сообщение пользователя.
        Возвращает словарь с полями:
          - type: "text" | "books" | "book_detail" | "error"
          - text: текст ответа
          - books: список книг (если type == "books")
          - book: детали книги (если type == "book_detail")
          - clear: True если нужно очистить экран чата
        """
        # Сохраняем вопрос пользователя
        self.db.save_message(session_id, "user", user_message)

        msg = user_message.strip().lower()
        response = self._route(msg, user_message, session_id)

        # Сохраняем ответ бота
        self.db.save_message(session_id, "bot", response.get("text", ""))
        return response

    def _route(self, msg: str, original: str, session_id: str) -> dict:
        """Определяет намерение и вызывает нужный обработчик."""

        # ── Приветствие ───────────────────────────────────────────────────────
        if self._match_any(msg, INTENT_PATTERNS["greeting"]):
            return {"type": "text", "text": GREETING_RESPONSE}

        # ── Помощь ────────────────────────────────────────────────────────────
        if self._match_any(msg, INTENT_PATTERNS["help"]):
            return {"type": "text", "text": HELP_RESPONSE}

        # ── Очистить историю ──────────────────────────────────────────────────
        if self._match_any(msg, INTENT_PATTERNS["clear"]):
            self.db.clear_history(session_id)
            return {"type": "text", "text": "🗑️ История чата очищена.", "clear": True}

        # ── Информация о книге по ID ──────────────────────────────────────────
        for pattern in INTENT_PATTERNS["book_info"]:
            m = re.search(pattern, msg)
            if m:
                book_id = int(m.group(1))
                book = self.db.get_book_by_id(book_id)
                if book:
                    return {
                        "type": "book_detail",
                        "text": f"📖 Книга #{book_id}",
                        "book": book
                    }
                return {"type": "text", "text": f"❌ Книга с ID #{book_id} не найдена."}

        # ── FAQ ───────────────────────────────────────────────────────────────
        if self._match_any(msg, INTENT_PATTERNS["faq"]):
            faq = self.db.search_faq(msg)
            if faq:
                return {"type": "text", "text": f"**{faq['question']}**\n\n{faq['answer']}"}

        # ── Поиск по автору ───────────────────────────────────────────────────
        for pattern in INTENT_PATTERNS["search_author"]:
            m = re.search(pattern, msg)
            if m:
                author_query = m.group(1).strip()
                if len(author_query) >= 2:
                    books = self.db.search_by_author(author_query)
                    return self._books_response(books, f"автора «{author_query}»")

        # ── Поиск по названию (явный запрос) ─────────────────────────────────
        for pattern in INTENT_PATTERNS["search_title"]:
            m = re.search(pattern, msg)
            if m:
                title_query = m.group(1).strip()
                if len(title_query) >= 2:
                    books = self.db.search_by_title(title_query)
                    return self._books_response(books, f"«{title_query}»")

        # ── FAQ (второй проход — любые ключевые слова) ────────────────────────
        faq = self.db.search_faq(msg)
        if faq:
            return {"type": "text", "text": f"**{faq['question']}**\n\n{faq['answer']}"}

        # ── Неявный поиск: просто текст ───────────────────────────────────────
        clean = re.sub(r"[^\w\s]", "", original).strip()
        if len(clean) >= 3:
            books = self.db.search_by_title(clean)
            if not books:
                books = self.db.search_by_author(clean)
            if books:
                return self._books_response(books, f"«{clean}»")

        # ── Ничего не найдено ─────────────────────────────────────────────────
        return {"type": "text", "text": NOT_FOUND_RESPONSE}

    # ── Вспомогательные методы ────────────────────────────────────────────────

    @staticmethod
    def _match_any(text: str, patterns: list[str]) -> bool:
        """Проверяет, совпадает ли текст с любым из паттернов."""
        return any(re.search(p, text) for p in patterns)

    @staticmethod
    def _books_response(books: list[dict], query_label: str) -> dict:
        """Формирует ответ со списком найденных книг."""
        if not books:
            return {
                "type": "text",
                "text": f"📭 По запросу {query_label} ничего не найдено.\n\n"
                        "Попробуйте другое название или имя автора."
            }
        count = len(books)
        word = "книга" if count == 1 else ("книги" if count < 5 else "книг")
        return {
            "type": "books",
            "text": f"📚 По запросу {query_label} найдено {count} {word}:",
            "books": books
        }
