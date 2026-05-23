# ISA: gstack-fusion (Ideal State Artifact)

## 1. Контекст (Context)
Reaper OS v11.5.0 (Graph-Core) успешно стабилизирован на локальном инференсе. Однако текущий Pantheon Swarm (агенты) имеет упрощенную структуру принятия решений. Появилась возможность интегрировать лучшие практики из `garrytan/gstack` для усиления автономности и качества ревью.

## 2. Проблема (Problem)
Агенты `architect`, `builder` и `sentry` в `reaper-auto.py` действуют линейно. Отсутствует стадия глубокого бизнес-анализа (CEO) и архитектурного ревью (Tech Lead), а также нет встроенной проверки фронтенда через браузер.

## 3. Цель (Goal)
Интегрировать ролевые модели и браузерный QA из gstack в ядро Reaper OS.

## 4. Аудитория (Audience)
Principal (User).

## 5. Критерии успеха (Success Criteria - ISC)
1. **Multi-Role Thinking**: Скрипт `reaper-auto.py` поддерживает стадии `CEO_PLAN` и `LEAD_REVIEW`.
2. **Browser QA Node**: В LangGraph добавлен узел `BROWSER_QA` с использованием Playwright/Chromium.
3. **Safety Guard**: Реализована команда `/freeze` для временной блокировки файлов от записи.
4. **Local Execution**: Все новые функции работают на локальном инференсе Rapid-MLX (Qwen1.5B).

## 6. Что НЕ является целью (Non-Goals)
- Полная установка gstack (через Bun).
- Миграция памяти с Neural SQLite на GBrain (наша память мощнее).

## 7. Предположения (Assumptions)
- Локальная модель Qwen1.5B справится с ролевыми промптами.
- Chromium установлен в системе.

## 8. Ограничения (Constraints)
- RAM limit (8GB): нельзя раздувать контекст агентов.
- Только локальный запуск.

## 9. Риски (Risks)
- Галлюцинации 1.5B модели при сложных ролевых играх.
- Зависание браузерных процессов.

## 10. Результаты (Deliverables)
- Обновленный `.agents/lib/reaper-auto.py`.
- Новый скилл `.agents/skills/browser-qa/SKILL.md`.
- Интеграция в `GEMINI.md`.

## 11. Genesis Memory Sync
- **Semantic Contribution**: Понятие "Role-Play Swarm" как стандарт планирования в Reaper OS.
- **Procedural Discovery**: Алгоритм браузерной верификации фронтенда.
- **Resonance Rule**: "Think like a Team, execute like a Machine".

## 12. Definition of Done (DoD)
- [x] ISA утвержден.
- [ ] Логика ролей внедрена.
- [ ] Браузерный узел протестирован.
- [ ] Cognitive Distillation выполнена.
- [ ] `reaper-autonome finish` запущен.
