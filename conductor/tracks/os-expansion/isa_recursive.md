# ISA: Recursive Memory - GraphRAG v2 (Ideal State Artifact)

## 1. Контекст (Context)
Reaper OS v11.3.1 (Frontier) использует векторный поиск для извлечения контекста. Однако плоские векторы часто упускают важные связи между файлами и символами (классы, функции, зависимости).

## 2. Проблема (Problem)
Текущий поиск в `NeuralStore` ограничен косинусным сходством. Если информация разнесена по разным файлам, агент получает неполную картину, что ведет к галлюцинациям или ошибкам в планировании.

## 3. Цель (Goal)
Внедрить алгоритм рекурсивного поиска (GraphRAG v2), который автоматически "прыгает" по символическим ссылкам (`link:symbol`) и объединяет контекст связанных узлов.

## 4. Аудитория (Audience)
Principal (User), DA (Swarm Agents).

## 5. Критерии успеха (Success Criteria - ISC)
- [x] Реализация метода `recursive_expand` в `NeuralStore`.
- [x] Автоматическое извлечение тегов `link:` из метаданных найденных узлов.
- [x] Вторичный поиск (по символам) для каждого извлеченного тега.
- [x] Объединение результатов с учетом пенальти за глубину прыжка (decay factor).
- [x] Тест: Поиск по запросу "PrivacyLayer" должен возвращать не только `reaper-brain.py`, но и связанные скрипты автоматизации через теги.

## 6. Что НЕ является целью (Non-Goals)
- Полноценная графовая БД (Neo4j). Используем существующий SQLite substrate.
- Бесконечная рекурсия (лимит глубины = 1-2 прыжка).

## 7. Предположения (Assumptions)
Метаданные (теги) корректно заполняются при индексации или через `SkillGrapher`.

## 8. Ограничения (Constraints)
Максимальное количество результирующих узлов после расширения — 10, чтобы не перегружать контекстное окно LLM.

## 9. Риски (Risks)
- Зацикливание ссылок (A -> B -> A). Решение: `seen_ids` set.
- Снижение релевантности (Noise). Решение: строгий decay score.

## 10. Результаты (Deliverables)
- Обновленный `NeuralStore` в `reaper-brain.py`.
- Логика рекурсивного расширения в `search()`.

## 11. Genesis Memory Sync
- **Semantic Contribution**: Relational Knowledge Retrieval (GraphRAG v2).
- **Procedural Discovery**: Symbol-based context merging with tag priority.
- **Resonance Rule**: Context is a graph, not a list.

## 12. Definition of Done (DoD)
- [x] Task logic implemented and verified.
- [x] Cognitive Distillation performed.
- [ ] Memoir Git commit completed via `reaper-autonome finish`.
