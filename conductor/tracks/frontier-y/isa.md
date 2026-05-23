# ISA: Frontier-Y Evolution (Ideal State Artifact)

## 1. Контекст (Context)
Текущая архитектура Reaper OS нуждается в переходе от ручного управления (manual planning/execution) к автоматизированному (dynamic spec synthesis, semantic search, distillation).

## 2. Проблема (Problem)
1. Conductor требует ручного планирования.
2. Context rot (засорение памяти) замедляет систему.
3. Отсутствие эффективного поиска по истории: поиск ведется по ключевым словам, теряются глубокие связи.

## 3. Цель (Goal)
Стандартизировать автоматизированную когнитивную архитектуру Trinity, обеспечивающую самообслуживание системы через динамическую спецификацию, Semantic Search и Distillation-циклы.

## 4. Аудитория (Audience)
Principal (User) / Reaper OS Orchestrator.

## 5. Критерии успеха (Success Criteria - ISC)
- [ ] `spec_synthesizer.py` генерирует `.task_tree.json` из `isa.md`.
- [ ] `reaper.py` реализовал интеграцию `sqlite-vec` для семантического поиска.
- [ ] Фаза `distill` (автоматическая дистилляция сессии) внедрена в `Phase 4` протокола.
- [ ] Система прошла полную верификацию Trinity Protocol.

## 6. Что НЕ является целью (Non-Goals)
- Улучшение UI или визуальных интерфейсов.
- Динамическое переключение моделей (routing). Мы сохраняем gpt-4o-mini как основную модель для Рипера.

## 7. Предположения (Assumptions)
- Доступ к OpenAI API стабилен.
- Python 3.12 доступен в окружении для всех процессов.

## 8. Ограничения (Constraints)
- RAM < 8GB (минимум нагрузки на фон).
- Отсутствие вечных демонов (Zero-Clutter Policy).

## 9. Риски (Risks)
- "Галлюцинации" синтезатора задач. *Митигация*: Валидация JSON через Pydantic.

## 10. Результаты (Deliverables)
- `tools/spec_synthesizer.py`
- `reaper.py` (updated with `sqlite-vec` integration)
- `PROCEDURAL_PATTERNS.md` update (distillation routine)

## 11. Genesis Memory Sync
- **Semantic Contribution**: Added Trinity v12.3 specs for Frontier-Y.
- **Procedural Discovery**: Protocol for auto-distillation.
- **Resonance Rule**: Always synthesize specs before action.

## 12. Definition of Done (DoD)
- [ ] Все компоненты Frontier-Y реализованы.
- [ ] Сквозное тестирование (GSD-T) успешно.
- [ ] Память дистиллирована в хронику.
