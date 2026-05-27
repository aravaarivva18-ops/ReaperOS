#!/usr/bin/env python3
import os
import re
import sys

# Регулярные выражения для поиска секретов
PATTERNS = {
    "GitHub Token": r"(?:ghp|gho|ghu|ghs|ghr)_[a-zA-Z0-9]{36,255}",
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
    "Hugging Face Token": r"hf_[a-zA-Z0-9]{34}",
    "Google Gemini API Key": r"AIzaSy[a-zA-Z0-9_-]{33}",
    "Generic Private Key": r"-----BEGIN [A-Z ]+ PRIVATE KEY-----"
}

EXCLUDED_DIRS = {
    ".git", ".reaper_venv", ".pytest_cache", "__pycache__", "node_modules", "logs", "scratch"
}

def scan_file(filepath):
    findings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for name, pattern in PATTERNS.items():
                    matches = re.findall(pattern, line)
                    if matches:
                        # Не предупреждаем о тестовых строках или фиктивных ключах
                        if "example" in line or "dummy" in line or "placeholder" in line:
                            continue
                        findings.append((line_num, name, matches))
    except Exception as e:
        # Игнорируем бинарные или недоступные файлы
        pass
    return findings

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    has_leaks = False
    
    print("AgentShield: сканирование секретов...")
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Исключаем системные папки
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        
        for filename in filenames:
            # Не сканируем сам анализатор или логи
            if filename in ["secrets_analyzer.py", ".DS_Store", "db.sqlite"]:
                continue
                
            filepath = os.path.join(dirpath, filename)
            findings = scan_file(filepath)
            
            if findings:
                rel_path = os.path.relpath(filepath, root_dir)
                for line_num, name, matches in findings:
                    print(f"⚠️ [КРИТИЧЕСКИ] {rel_path}:{line_num} - Обнаружен {name} ({len(matches)} шт.)")
                has_leaks = True
                
    if has_leaks:
        print("\n❌ Блокировка: обнаружены секреты в открытом виде!")
        sys.exit(1)
    else:
        print("✅ Секреты не обнаружены. Проверка пройдена.")
        sys.exit(0)

if __name__ == "__main__":
    main()
