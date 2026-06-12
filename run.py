#!/usr/bin/env python3
"""
run.py — Точка входа для запуска библиотечного чат-бота.

Использование:
    python run.py
    python run.py --port 8080
    python run.py --host 0.0.0.0 --port 8000
"""

import argparse
import sys
import os

# Убеждаемся, что корень проекта в sys.path
sys.path.insert(0, os.path.dirname(__file__))

import uvicorn


def main():
    parser = argparse.ArgumentParser(description="Запуск библиотечного чат-бота")
    parser.add_argument("--host",   default="127.0.0.1", help="Хост (default: 127.0.0.1)")
    parser.add_argument("--port",   default=8000, type=int, help="Порт (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Авторелоад при изменениях (режим разработки)")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print("  📚  Библиотечный чат-бот")
    print(f"{'='*50}")
    print(f"  🌐  Открыть: http://{args.host}:{args.port}")
    print(f"  📖  API docs: http://{args.host}:{args.port}/docs")
    print(f"  🛑  Остановить: Ctrl+C")
    print(f"{'='*50}\n")

    uvicorn.run(
        "backend.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
