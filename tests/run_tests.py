#!/usr/bin/env python3
"""Простой запускатель тестов fpx.

Как использовать:
    python run_tests.py           # запустить все тесты
    python run_tests.py -v        # подробный вывод (дефолт)
    python run_tests.py -k chat   # только тесты с "chat" в названии
    python run_tests.py --tb=long # полный traceback

Требования:
    pip install pytest pytest-asyncio beautifulsoup4 fpx-engine
"""
import sys
import subprocess


def main():
    args = [sys.executable, "-m", "pytest", ".", "-v", "--tb=short"] + sys.argv[1:]
    print("=" * 60)
    print("Запуск тестов fpx")
    print("=" * 60)
    print(f"Команда: {' '.join(args)}")
    print()
    result = subprocess.run(args)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
