#!/bin/bash
# Скрипт настройки Git pre-commit хуков в ReaperOS

HOOK_DIR="$(git rev-parse --git-dir)/hooks"
PRE_COMMIT="$HOOK_DIR/pre-commit"

echo "Настройка Git pre-commit хуков..."

cat << 'EOF' > "$PRE_COMMIT"
#!/bin/bash
# ReaperOS Git Quality Gate

PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# 1. Запуск сканера секретов
python3 tools/secrets_analyzer.py
if [ $? -ne 0 ]; then
    echo "❌ Коммит заблокирован: Нарушение требований безопасности (AgentShield)."
    exit 1
fi

# 2. Запуск тестов
echo "Запуск тестов (pytest)..."
.reaper_venv/bin/pytest
if [ $? -ne 0 ]; then
    echo "❌ Коммит заблокирован: Некоторые тесты упали."
    exit 1
fi

echo "✅ Все Quality Gates пройдены. Коммит разрешен."
exit 0
EOF

chmod +x "$PRE_COMMIT"
echo "Git pre-commit хук успешно установлен в $PRE_COMMIT"
