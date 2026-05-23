# ISA: Live Pulse Infrastructure Monitoring (Ideal State Artifact)

## 1. Контекст (Context)
Reaper OS v11.3.1 (Frontier) зависит от нескольких внешних сервисов (MLX Inference на 8080, Neural Embedder на 5001). Текущий мониторинг в `reaper-brain.py` слишком базовый и не дает полной картины здоровья системы.

## 2. Проблема (Problem)
Отсутствие детальной видимости состояния инфры: не проверяются специфические порты, нет точных метрик потребления ресурсов движком MLX, а ошибки в логах сложно отследить без ручного вмешательства.

## 3. Цель (Goal)
Создать единую панель управления `PulseDashboard`, обеспечивающую 100% прозрачность состояния инфраструктуры и ресурсов в реальном времени.

## 4. Аудитория (Audience)
Principal (User), DA (Swarm Agents).

## 5. Критерии успеха (Success Criteria - ISC)
- [x] Проверка доступности портов 8080 (MLX) и 5001 (Embedder) через сокеты.
- [x] Вывод потребления RAM конкретно для процесса `rapid-mlx`.
- [x] Интеграция `status` (🟢 OPTIMAL / 🟡 DEGRADED / 🔴 CRITICAL) на основе здоровья всех сервисов.
- [x] Команда `reaper pulse` (через `reaper-brain.py pulse`) выводит структурированный JSON с метриками.
- [x] Добавление проверки времени отклика (latency) для Neural Store.

## 6. Что НЕ является целью (Non-Goals)
- Настройка внешних алертов (Slack/Email).
- Автоматический перезапуск упавших сервисов (только мониторинг).

## 7. Предположения (Assumptions)
Библиотека `psutil` установлена и доступна в окружении `.reaper_venv`.

## 8. Ограничения (Constraints)
Проверка портов должна иметь таймаут < 0.3с, чтобы не тормозить основной цикл.

## 9. Риски (Risks)
- Высокая нагрузка на CPU при частом сканировании процессов. Решение: оптимизация через поиск по имени.

## 10. Результаты (Deliverables)
- Обновленный класс `PulseDashboard` в `reaper-brain.py`.
- Расширенный вывод команды `pulse`.

## 11. Genesis Memory Sync
- **Semantic Contribution**: Real-time Infrastructure Observability pattern.
- **Procedural Discovery**: Latency-aware socket checks in Python.
- **Resonance Rule**: Monitor latency, not just uptime.

## 12. Definition of Done (DoD)
- [x] Task logic implemented and verified.
- [x] Cognitive Distillation performed.
- [ ] Memoir Git commit completed via `reaper-autonome finish`.
