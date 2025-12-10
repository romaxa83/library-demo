#!/bin/bash

echo "🔍 Проверка кода с помощью pylint..."
pylint src/ --fail-under=8.0 || true

echo ""
echo "📋 Проверка стиля с помощью flake8..."
flake8 src/

echo ""
echo "🎨 Проверка форматирования с помощью black..."
black --check src/ || true

echo ""
echo "📦 Проверка импортов с помощью isort..."
isort --check-only src/ || true

echo ""
echo "📝 Проверка типов с помощью mypy..."
mypy src/ || true

echo ""
echo "✅ Анализ завершён!"