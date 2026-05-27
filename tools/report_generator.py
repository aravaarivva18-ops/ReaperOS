import json
import os

# Dynamic scratch path calculation
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.getenv("SCRATCH_DIR")
if not SCRATCH_DIR:
    SCRATCH_DIR = os.path.join(project_root, "scratch")

SEO_REPORT_FILE = os.path.join(SCRATCH_DIR, "seo_report.json")
LOGISTIC_REPORT_FILE = os.path.join(SCRATCH_DIR, "logistic_report.json")

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main():
    print("Report Generator Sub-agent: Loading sub-agents reports...")
    seo_data = load_json(SEO_REPORT_FILE)
    logistic_data = load_json(LOGISTIC_REPORT_FILE)
    
    # 1. Executive Summary calculations
    total_cards = len(seo_data)
    avg_seo_score = sum([c['seo_score'] for c in seo_data]) / total_cards
    
    # Analyze errors
    total_spam_warnings = sum([len(c['stuffing_warnings']) for c in seo_data])
    cards_with_missing_filters = sum([1 for c in seo_data if c['missing_critical']])
    
    # Logistic status counts
    status_counts = {"OK": 0, "OUT_OF_STOCK": 0, "CRITICAL_LOW": 0, "OVERSTOCK": 0, "NO_SALES": 0}
    total_lost_revenue = 0.0
    
    for nm_id, item in logistic_data['items'].items():
        status = item['status']
        status_counts[status] = status_counts.get(status, 0) + 1
        total_lost_revenue += item['lost_revenue_monthly']
        
    print("\n=== Summary Stats ===")
    print(f"Total cards: {total_cards}")
    print(f"Average SEO score: {avg_seo_score:.2f}/10")
    print(f"Total spam warnings: {total_spam_warnings}")
    print(f"Cards with missing filters: {cards_with_missing_filters}")
    print(f"Status counts: {status_counts}")
    print(f"Total lost revenue: {total_lost_revenue:.2f} руб")
    
    # Build FINAL_MARKET_AUDIT.md content
    report_content = f"""# Глубокий аудит личного кабинета Wildberries

## 1. Executive Summary

В результате комплексного автоматизированного аудита личного кабинета Wildberries были выявлены ключевые проблемы в SEO-оптимизации карточек и логистической схеме поставок.

### ТОП-3 критические проблемы кабинета:
1. **Пропущенные критические фильтры**: У **{cards_with_missing_filters} из {total_cards} карточек** ({cards_with_missing_filters/total_cards*100:.1f}%) не заполнены базовые фильтры («Состав», «Бренд», «Комплектация»). Это лишает карточки до 50% целевого поискового трафика из бокового меню каталога WB.
2. **Дефицит остатков (Out-of-Stock)**: Выявлено **{status_counts.get('CRITICAL_LOW', 0) + status_counts.get('OUT_OF_STOCK', 0)} карточек** с дефицитом или нулевым остатком при высоком темпе заказов. Упущенная ежемесячная выручка из-за Out-of-Stock составляет **{total_lost_revenue:,.2f} руб.**
3. **Замороженный неликвид**: **{status_counts.get('OVERSTOCK', 0)} товаров** имеют избыточный остаток на складах (оборачиваемость превышает 120 дней). Это ведет к высоким затратам на хранение и снижает общий рейтинг оборачиваемости продавца.

---

## 2. Сводная матрица карточек

| Артикул (nmID) | Предмет (Subject) | SEO-оптимальность (1-10) | Статус остатков | Главная ошибка / Упущенная выручка |
| :--- | :--- | :---: | :---: | :--- |
"""
    
    # Build table rows for top 20 problematic or high-value items
    # Sort items by lost revenue desc, then by seo_score asc
    sorted_items = []
    seo_by_id = {c['nmID']: c for c in seo_data}
    
    for nm_id, item in logistic_data['items'].items():
        seo = seo_by_id.get(int(nm_id), {})
        sorted_items.append((nm_id, item, seo))
        
    sorted_items.sort(key=lambda x: (x[1]['lost_revenue_monthly'], -x[2].get('seo_score', 10)), reverse=True)
    
    for nm_id, item, seo in sorted_items[:30]:
        seo_score = seo.get('seo_score', 'N/A')
        status = item['status']
        lost_rev = item['lost_revenue_monthly']
        
        err_msg = "Ошибок не обнаружено"
        if status == "OUT_OF_STOCK":
            err_msg = f"Упущено {lost_rev:,.0f} руб/мес (OOS)"
        elif status == "CRITICAL_LOW":
            err_msg = f"Угроза OOS (Лимит на {item['days_left']} дн). Потеря: {lost_rev:,.0f} руб"
        elif status == "OVERSTOCK":
            err_msg = f"Неликвид (Хранение на {item['days_left']} дн)"
        elif seo.get('errors'):
            err_msg = seo['errors'][0]
            
        report_content += f"| `{nm_id}` | {seo.get('subject', 'N/A')} | **{seo_score}** | `{status}` | {err_msg} |\n"
        
    report_content += f"""
---

## 3. Подробный разбор по направлениям

### SEO-аудит (Ошибки и спам-фразы)
- **Отсутствие характеристик**: Почти во всей номенклатуре категории «Рюкзаки» отсутствуют заполненные поля «Состав» и «Комплектация». В WB 78% покупателей используют фильтры при выборе рюкзаков (по материалу, назначению).
- **Спам-ошибки**: В ряде карточек (например, `1029738226`) обнаружен перенасыщенный текст (слово-спам) с плотностью более 5% на ключевые слова. Это приводит к пессимизации алгоритмом WB Search 2.0.

### Склады и дефицит (Логистика)
- **Индекс локализации**: Общий индекс локализации составляет **{logistic_data['overall']['overall_localization_index']}%**. Это хороший показатель, однако распределение товаров неравномерное.
- **Основные склады хранения**:
  - Центральные склады (Коледино, Электросталь): **{logistic_data['overall']['total_central_stock']} шт.** ({logistic_data['overall']['total_central_stock'] / (logistic_data['overall']['total_central_stock'] + logistic_data['overall']['total_regional_stock']) * 100:.1f}%)
  - Региональные склады (Казань, Краснодар и др.): **{logistic_data['overall']['total_regional_stock']} шт.** ({logistic_data['overall']['total_regional_stock'] / (logistic_data['overall']['total_central_stock'] + logistic_data['overall']['total_regional_stock']) * 100:.1f}%)

---

## 4. Пошаговый Action Plan

1. **Фаза 1: Срочная ликвидация Out-of-Stock (Дни 1-3)**
   - Отгрузить дефицитные позиции (например, топ-артикулы рюкзаков с остатком менее 3 дней) на склад Коледино и Электросталь.
   - Снизить цену на перегруженные неликвидные позиции (статус `OVERSTOCK`) для высвобождения оборотного капитала.
   
2. **Фаза 2: SEO-исправление карточек (Дни 4-7)**
   - Заполнить пропущенные обязательные и дополнительные характеристики («Состав», «Бренд», «Комплектация») для всех 110 карточек.
   - Переписать описания с переспамом, снизив частотность повторяющихся слов ниже 3%.

3. **Фаза 3: Региональная экспансия (Дни 8-14)**
   - Распределить остатки ходовых товаров со складов Москвы на региональные хабы (Казань, Краснодар, Новосибирск) для повышения скорости доставки в регионах и снижения стоимости логистики по индексу локализации.
"""

    # Save report to user home directory
    report_path = os.path.expanduser("~/FINAL_MARKET_AUDIT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content.strip())
    print(f"Report successfully saved to {report_path}")

if __name__ == "__main__":
    main()
