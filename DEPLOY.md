# 🚀 Как опубликовать бота в интернете (бесплатно, для отчёта руководителю)

Эта инструкция поможет получить **постоянную ссылку** вида
`https://library-chatbot-xxxx.onrender.com`, которую можно отправить
руководителю практики. По этой ссылке бот будет работать в браузере
у любого человека — без VS Code, без установки Python.

Используем бесплатные сервисы: **GitHub** (хранение кода) +
**Render.com** (хостинг).

---

## Шаг 1. Создайте аккаунт на GitHub

1. Перейдите на https://github.com
2. Нажмите **Sign up**, зарегистрируйтесь (email + пароль)

---

## Шаг 2. Загрузите проект на GitHub

### Вариант А — через браузер (проще, без команд)

1. На github.com нажмите **+** (в правом верхнем углу) → **New repository**
2. Назовите репозиторий, например `library-chatbot`
3. Сделайте его **Public**
4. Нажмите **Create repository**
5. На открывшейся странице нажмите **uploading an existing file**
6. Перетащите туда **ВСЕ файлы и папки** из распакованной папки `library_chatbot`
   (включая `backend`, `frontend`, `database`, `run.py`, `requirements.txt`, `render.yaml`)
7. Нажмите **Commit changes**

> ⚠️ Важно: загружайте содержимое папки `library_chatbot`, а НЕ саму папку
> как один файл. То есть `backend/`, `frontend/` и т.д. должны быть видны
> сразу в корне репозитория на GitHub.

### Вариант Б — через терминал VS Code (для тех, кто умеет в git)

```powershell
cd library_chatbot
git init
git add .
git commit -m "Первая версия библиотечного чат-бота"
git branch -M main
git remote add origin https://github.com/ВАШ_ЛОГИН/library-chatbot.git
git push -u origin main
```

---

## Шаг 3. Разверните на Render.com

1. Перейдите на https://render.com
2. Нажмите **Get Started** → войдите через **GitHub** (это свяжет аккаунты)
3. На главной панели нажмите **New +** → **Web Service**
4. Выберите репозиторий `library-chatbot`, который вы загрузили
5. Render автоматически найдёт файл `render.yaml` и заполнит настройки.
   Если не найдёт — заполните вручную:
   - **Name**: `library-chatbot` (или любое другое)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free`
6. Нажмите **Create Web Service**

---

## Шаг 4. Подождите 2-5 минут

Render будет собирать и запускать проект. Вы увидите логи —
дождитесь строки:

```
Application startup complete.
```

---

## Шаг 5. Откройте вашу ссылку!

Наверху страницы Render будет ссылка вида:

```
https://library-chatbot-xxxx.onrender.com
```

Откройте её — увидите чат-бот на весь экран.

Чтобы увидеть **виджет** (как у "AI GUL"), откройте:

```
https://library-chatbot-xxxx.onrender.com/widget-demo
```

---

## ⚠️ О бесплатном плане Render

- Сервис "засыпает" после 15 минут без посещений
- Первое открытие после "сна" может занять **30-60 секунд** — это нормально,
  просто подождите, страница загрузится
- Для постоянной работы (без "сна") нужен платный план — но для демонстрации
  руководителю бесплатного плана достаточно

---

## Что отправить руководителю практики

Отправьте две ссылки:

1. **Чат-бот (полный экран):**
   `https://library-chatbot-xxxx.onrender.com`

2. **Демо виджета (как будет выглядеть на сайте библиотеки):**
   `https://library-chatbot-xxxx.onrender.com/widget-demo`

Также можно приложить исходный код — ссылку на ваш репозиторий GitHub:
`https://github.com/ВАШ_ЛОГИН/library-chatbot`

---

## Если хотите встроить на настоящий сайт lib.dulaty.kz позже

Когда появится доступ к админке Joomla:

1. Откройте файл `frontend/widget.html`
2. Найдите строку:
   ```javascript
   const API_BASE = "";
   ```
3. Замените на адрес вашего Render-сервиса:
   ```javascript
   const API_BASE = "https://library-chatbot-xxxx.onrender.com";
   ```
4. Скопируйте весь код файла и вставьте в Joomla:
   **Content → Site Modules → New → Custom HTML**
