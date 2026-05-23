# ISA: Semantic Privacy Upgrade (Ideal State Artifact)

## 1. Контекст (Context)
Reaper OS v11.3.1 (Frontier) требует абсолютной чистоты логов. Текущий PrivacyLayer в `reaper-brain.py` покрывает только базовые токены и не защищает от современных форматов секретов.

## 2. Проблема (Problem)
Высокий риск утечки AWS Secret Access Keys, новых GitHub PAT, Google API Keys и приватных ключей (RSA/PGP) в публичные или локальные логи при работе `reaper-auto`.

## 3. Цель (Goal)
Создать непроницаемый Semantic Privacy Layer, маскирующий 100% критических секретов в любом текстовом потоке.

## 4. Аудитория (Audience)
Principal (User), DA (Swarm Agents).

## 5. Критерии успеха (Success Criteria - ISC)
- [x] Маскировка AWS Secret Access Key (40 символов).
- [x] Маскировка GitHub Fine-grained PAT (`github_pat_`).
- [x] Маскировка Google Cloud/Maps API Keys (`AIza`).
- [x] Маскировка блоков Private Keys (`-----BEGIN ...`).
- [x] Успешное прохождение `reaper-brain.py privacy-test` с новыми паттернами.
- [x] Подтвержденная работа маскировки в логах `reaper-auto`.

## 6. Что НЕ является целью (Non-Goals)
- Шифрование файлов на диске (только маскировка вывода/логов).
- Маскировка пользовательских имен (кроме путей).

## 7. Предположения (Assumptions)
Паттерны секретов соответствуют официальной документации вендоров.

## 8. Ограничения (Constraints)
Маскировка не должна ломать структуру JSON/структурированных данных, если они нужны для работы.

## 9. Риски (Risks)
- False Positives (маскировка полезных данных). Решается уточнением Regex.
- Пропуск новых форматов (регулярное обновление паттернов).

## 10. Результаты (Deliverables)
- Обновленный `reaper-brain.py` (PrivacyLayer class).
- Обновленный тест-кейс в `reaper-brain.py`.

## 11. Genesis Memory Sync
- **Semantic Contribution**: Privacy-First Logging architecture.
- **Procedural Discovery**: Regex optimization for high-speed log masking.
- **Resonance Rule**: Never leak credentials, even in errors.

## 12. Definition of Done (DoD)
- [x] Task logic implemented and verified.
- [x] Cognitive Distillation performed.
- [ ] Memoir Git commit completed via `reaper-autonome finish`.
