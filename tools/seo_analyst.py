#!/usr/bin/env python3
import json
import os
import re
from collections import Counter, defaultdict

# Dynamic scratch path calculation
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH_DIR = os.getenv("SCRATCH_DIR")
if not SCRATCH_DIR:
    SCRATCH_DIR = os.path.join(project_root, "scratch")

CARDS_FILE = os.path.join(SCRATCH_DIR, "cards.json")
SEO_REPORT_FILE = os.path.join(SCRATCH_DIR, "seo_report.json")

STOP_WORDS = {
    'и', 'в', 'во', 'на', 'с', 'со', 'для', 'по', 'а', 'но', 'как', 'из', 'к', 'ко', 
    'у', 'о', 'об', 'за', 'от', 'при', 'это', 'что', 'чтобы', 'же', 'бы', 'ли', 
    'то', 'так', 'же', 'его', 'ее', 'их', 'все', 'всех', 'всеми', 'для', 'этот',
    'эта', 'эти', 'этого', 'этой', 'этих', 'тем', 'теми', 'ней', 'нем', 'ними'
}

def analyze_keywords(text):
    if not text:
        return {}, []
    
    words = re.findall(r'[а-яа-кёa-z0-9\-]+', text.lower())
    filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    
    counter = Counter(filtered_words)
    total_words = len(filtered_words)
    
    stuffing_warnings = []
    word_densities = {}
    
    for word, count in counter.items():
        density = (count / total_words) * 100 if total_words > 0 else 0
        word_densities[word] = {
            "count": count,
            "density": round(density, 2)
        }
        
        # WB criteria: if keyword density > 4% or count > 5, it can be flagged as spam
        if density > 4.5 and count > 3:
            stuffing_warnings.append({
                "word": word,
                "count": count,
                "density": round(density, 2),
                "reason": f"Переспам ключевого слова (плотность {density:.1f}%)"
            })
            
    return word_densities, stuffing_warnings

def analyze_card(card):
    nm_id = card.get('nmID')
    vendor_code = card.get('vendorCode', 'N/A')
    subject = card.get('subjectName', 'N/A')
    title = card.get('title', 'N/A')
    description = card.get('description', '')
    brand = card.get('brand', 'N/A')
    
    characteristics = card.get('characteristics', [])
    char_names = {c.get('name') for c in characteristics if c.get('name')}
    
    # Critical fields by category or general
    critical_fields = ['Состав', 'Цвет', 'Бренд', 'Страна производства', 'Комплектация']
    if subject == 'Рюкзаки':
        critical_fields += ['Назначение', 'Материал подкладки', 'Карманы']
    elif subject == 'Хлебницы':
        critical_fields += ['Материал', 'Особенности']
    elif 'садовые' in subject.lower() or 'клумбы' in subject.lower():
        critical_fields += ['Материал', 'Высота']
        
    missing_critical = [f for f in critical_fields if f not in char_names]
    
    # Word stuffing check
    densities, stuffing = analyze_keywords(description)
    
    # Calculate score (1-10)
    score = 10
    
    # Deductions
    if not description:
        score -= 5
    elif len(description) < 150:
        score -= 2
    
    score -= min(3, len(stuffing))
    
    char_count = len(characteristics)
    if char_count < 5:
        score -= 3
    elif char_count < 10:
        score -= 1
        
    score -= len(missing_critical)
    score = max(1, min(10, score))
    
    errors = []
    if not description:
        errors.append("Отсутствует SEO-описание.")
    elif len(description) < 150:
        errors.append("Слишком короткое описание (мало ключевых слов).")
        
    for item in stuffing:
        errors.append(f"Переспам слова '{item['word']}' ({item['count']} раз, {item['density']}%).")
        
    if missing_critical:
        errors.append(f"Пропущены важные фильтры: {', '.join(missing_critical)}")
        
    return {
        "nmID": nm_id,
        "vendorCode": vendor_code,
        "subject": subject,
        "title": title,
        "brand": brand,
        "seo_score": score,
        "char_count": char_count,
        "missing_critical": missing_critical,
        "stuffing_warnings": stuffing,
        "errors": errors
    }

def main():
    print("SEO Sub-agent: Starting expert audit of cards...")
    if not os.path.exists(CARDS_FILE):
        print(f"Error: {CARDS_FILE} not found.")
        return
        
    with open(CARDS_FILE, "r", encoding="utf-8") as f:
        cards = json.load(f)
        
    results = []
    category_chars = defaultdict(list)
    category_keywords = defaultdict(Counter)
    
    for card in cards:
        audit = analyze_card(card)
        results.append(audit)
        
        # Track category statistics
        subject = card.get('subjectName', 'N/A')
        characteristics = card.get('characteristics', [])
        for c in characteristics:
            name = c.get('name')
            if name:
                category_chars[subject].append(name)
                
        # Collect top words for keywords template
        desc = card.get('description', '')
        if desc:
            words = re.findall(r'[а-яа-кёa-z0-9\-]+', desc.lower())
            filtered = [w for w in words if w not in STOP_WORDS and len(w) > 2]
            category_keywords[subject].update(filtered)
            
    # Build category profiles
    category_profiles = {}
    for subject, chars in category_chars.items():
        total_cards_in_sub = sum(1 for c in cards if c.get('subjectName') == subject)
        char_counts = Counter(chars)
        # Keep features appearing in at least 40% of cards in this category
        frequent_chars = [name for name, count in char_counts.items() if count / total_cards_in_sub >= 0.4]
        
        # Base critical fields
        base_critical = ['Состав', 'Цвет', 'Бренд', 'Страна производства', 'Комплектация']
        # Category specific criticals based on high frequency
        extra_critical = [c for c in frequent_chars if c not in base_critical and c not in ['Описание', 'Наименование', 'Артикул']]
        
        top_kws = [w for w, _ in category_keywords[subject].most_common(10)]
        
        category_profiles[subject] = {
            "critical_fields": list(set(base_critical + extra_critical[:5])),
            "common_keywords": top_kws,
            "avg_char_count": round(len(chars) / total_cards_in_sub, 1) if total_cards_in_sub > 0 else 0
        }
        
    report = {
        "categories": category_profiles,
        "cards": results
    }
        
    with open(SEO_REPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    print(f"SEO Sub-agent: Audited {len(results)} cards and saved results to {SEO_REPORT_FILE}")

if __name__ == "__main__":
    main()
