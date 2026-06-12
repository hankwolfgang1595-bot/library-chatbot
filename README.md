# 📚 Библиотечный Чат-Бот

Прототип чат-бота для университетской электронной библиотеки.  
Тёмный интерфейс в стиле ChatGPT, FastAPI на бэкенде, SQLite для хранения данных.

---

## Структура проекта

```
library_chatbot/
│
├── run.py                        # Точка входа — запуск сервера
├── requirements.txt              # Зависимости Python
│
├── backend/
│   ├── __init__.py
│   ├── main.py                   # FastAPI-приложение, маршруты
│   ├── chatbot.py                # Логика NLU и генерации ответов
│   ├── db_connector.py           # Слой доступа к данным (SQLite)
│   └── irbis_connector.py        # 🔌 Заглушка для интеграции ИРБИС 64
│
├── database/
│   ├── __init__.py
│   ├── init_db.py                # Создание таблиц и загрузка примеров
│   └── library.db                # SQLite-файл (создаётся автоматически)
│
└── frontend/
    ├── templates/
    │   └── index.html            # Jinja2-шаблон главной страницы
    └── static/
        ├── css/
        │   └── style.css         # Стили (тёмная академическая тема)
        └── js/
            └── app.js            # Логика чата, рендеринг ответов
```

---

## Быстрый старт

### 1. Клонируйте или скопируйте папку проекта

```bash
cd library_chatbot
```

### 2. Создайте виртуальное окружение

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Запустите сервер

```bash
python run.py
```

Откройте браузер: **http://127.0.0.1:8000**

> Для режима разработки с авторелоадом:
> ```bash
> python run.py --reload
> ```

---

## 🎈 Виджет для встраивания на сайт (как "AI GUL")

Помимо полноэкранной страницы, проект включает **компактный виджет-чат**
в виде плавающей кнопки в углу экрана — именно так выглядит большинство
чат-ботов на сайтах библиотек.

### Посмотреть демо

Запустите сервер (`python run.py`) и откройте:

```
http://127.0.0.1:8000/widget-demo
```

Это имитация страницы `lib.dulaty.kz` с виджетом LibBot в правом нижнем углу.
Нажмите на синюю круглую кнопку 💬, чтобы открыть чат.

### Встроить виджет на реальный сайт

1. Откройте файл `frontend/widget.html`
2. Скопируйте **весь его код** (стили + HTML + JavaScript)
3. Вставьте перед закрывающим тегом `</body>` на нужной странице сайта
4. В самом низу скрипта найдите строку:
   ```javascript
   const API_BASE = "http://127.0.0.1:8000";
   ```
   Замените на адрес вашего развёрнутого сервера, например:
   ```javascript
   const API_BASE = "https://library-api.dulaty.kz";
   ```

### Важно про CORS

Бэкенд уже настроен с `CORSMiddleware`, что позволяет виджету работать
на любом домене. В продакшене рекомендуется ограничить список разрешённых
доменов в `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://lib.dulaty.kz"],  # вместо "*"
    ...
)
```

---



| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/` | Главная страница (чат-интерфейс) |
| POST | `/api/chat` | Отправить сообщение, получить ответ |
| GET | `/api/history?session_id=...` | История чата сессии |
| POST | `/api/clear` | Очистить историю |
| GET | `/api/books?title=...` | Поиск книг по названию |
| GET | `/api/books?author=...` | Поиск книг по автору |
| GET | `/api/books/{id}` | Карточка книги по ID |
| GET | `/docs` | Интерактивная документация Swagger |

### Пример запроса к `/api/chat`

```json
POST /api/chat
{
  "message": "автор Достоевский",
  "session_id": "abc-123"    // необязательно, создастся автоматически
}
```

Ответ:
```json
{
  "type": "books",
  "text": "📚 По запросу «достоевский» найдено 2 книги:",
  "books": [ { "id": 2, "title": "Преступление и наказание", ... } ],
  "session_id": "abc-123"
}
```

---

## Что умеет бот

### Поиск книг
| Запрос | Действие |
|--------|----------|
| `Мастер и Маргарита` | Поиск по названию |
| `автор Булгаков` | Все книги автора |
| `книга #5` | Подробная карточка книги с ID 5 |

### FAQ — вопросы о библиотеке
- *Когда работает библиотека?*
- *Как получить читательский билет?*
- *На сколько дней выдают книги?*
- *Есть ли электронные книги?*
- *Можно ли распечатать?*
- *Есть ли Wi-Fi?*
- *Штрафы за просрочку?*
- *Правила поведения?*

### Управление
- `очистить историю` — удалить переписку текущей сессии
- `помощь` — список команд

---

## Описание файлов

### `backend/main.py`
FastAPI-приложение. Монтирует статику, регистрирует маршруты, запускает инициализацию БД при старте.

### `backend/chatbot.py`
NLU-движок на регулярных выражениях. Определяет намерение пользователя (поиск, FAQ, приветствие…) и возвращает структурированный ответ с полем `type`.

### `backend/db_connector.py`
Слой данных. Все SQL-запросы собраны здесь — замена на ИРБИС не затронет остальной код.

### `backend/irbis_connector.py`
Заглушка для ИРБИС 64. Содержит полные комментарии о том, как подключить реальный сервер и какие поля RUSMARC использовать. Интерфейс идентичен `DatabaseConnector`.

### `database/init_db.py`
Создаёт три таблицы (`books`, `faq`, `chat_history`) и заполняет их 20 книгами и 8 FAQ-записями.

### `frontend/templates/index.html`
Jinja2-шаблон. Сайдбар с быстрыми ссылками, шапка, окно чата, поле ввода. Все динамические данные передаются через JavaScript.

### `frontend/static/css/style.css`
Тёмная академическая тема: фон `#0f0e0c`, золотые акценты `#c9a84c`, шрифты Crimson Pro + Inter. CSS-переменные для лёгкой смены темы.

### `frontend/static/js/app.js`
Управляет отправкой сообщений, рендерингом трёх типов ответов (`text`, `books`, `book_detail`), хранит `session_id` в `sessionStorage`, восстанавливает историю при перезагрузке.

---

## Интеграция ИРБИС 64 (в будущем)

1. Откройте `backend/irbis_connector.py`
2. Реализуйте методы `search_by_title`, `search_by_author`, `get_book_by_id`
3. В `backend/main.py` замените строку:
   ```python
   from backend.db_connector import DatabaseConnector
   ```
   на:
   ```python
   from backend.irbis_connector import IrbisConnector as DatabaseConnector
   ```
4. Всё остальное работает без изменений.

Полезные ресурсы:
- Официальный сайт: https://irbis.elnit.org
- Python-клиент: https://github.com/amironov73/PlusIrbis
- Протокол: TCP/IP, порт 6666, кодировка CP1251

---

## База данных

SQLite-файл `database/library.db` создаётся автоматически при первом запуске.

### Таблицы

**books** — каталог книг  
`id, title, author, year, genre, description, isbn, available, location`

**faq** — часто задаваемые вопросы  
`id, keywords, question, answer`

**chat_history** — история переписки  
`id, session_id, role, message, timestamp`

### Добавить книгу вручную

```bash
sqlite3 database/library.db \
  "INSERT INTO books (title, author, year, genre, description, available, location)
   VALUES ('Название', 'Автор', 2024, 'Жанр', 'Описание', 1, 'Зал 1');"
```

---

## Требования

- Python 3.10+
- Зависимости: fastapi, uvicorn, jinja2, python-multipart
- Браузер: Chrome, Firefox, Edge (современные версии)
