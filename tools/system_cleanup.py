#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import time
import subprocess
import argparse
from datetime import datetime

# Настройка путей
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(PROJECT_DIR, "logs/cleanup.log")

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def get_dir_size(path):
    """Возвращает размер директории в байтах."""
    total_size = 0
    if not os.path.exists(path):
        return 0
    if os.path.isfile(path) or os.path.islink(path):
        return os.path.getsize(path)
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try:
                    total_size += os.path.getsize(fp)
                except OSError:
                    pass
    return total_size

def format_size(size_bytes):
    """Форматирует байты в удобочитаемый вид."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def safe_remove(path, dry_run=False):
    """Безопасно удаляет файл или папку."""
    if not os.path.exists(path):
        return 0
    
    size = get_dir_size(path)
    if dry_run:
        logging.info(f"[DRY-RUN] Будет удалено: {path} ({format_size(size)})")
        return size
    
    try:
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        logging.info(f"Успешно удалено: {path} ({format_size(size)})")
        return size
    except Exception as e:
        logging.error(f"Ошибка при удалении {path}: {e}")
        return 0

def run_cmd(cmd, dry_run=False):
    """Запускает системную команду."""
    if dry_run:
        logging.info(f"[DRY-RUN] Будет запущена команда: {' '.join(cmd)}")
        return
    
    start_time = time.time()
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        latency = (time.time() - start_time) * 1000
        logging.info(f"Команда {' '.join(cmd)} выполнена за {latency:.1f}ms")
        if latency > 10000: # предупреждение если выполняется дольше 10 секунд
            logging.warning(f"Высокая задержка команды {' '.join(cmd)}: {latency:.1f}ms")
    except subprocess.CalledProcessError as e:
        logging.error(f"Ошибка выполнения команды {' '.join(cmd)}: {e.stderr}")
    except Exception as e:
        logging.error(f"Ошибка при запуске {' '.join(cmd)}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Автоматическая фоновая очистка системы Reaper OS")
    parser.add_argument("--dry-run", action="store_true", help="Запуск в режиме симуляции")
    args = parser.parse_args()

    start_time = time.time()
    logging.info("=== Запуск очистки системы ===")
    if args.dry_run:
        logging.info("Режим симуляции (dry-run) активен.")

    total_freed = 0

    # Список путей для полной очистки
    home_dir = os.path.expanduser("~")
    username = os.getenv("USER") or os.getenv("USERNAME") or "rus"
    targets = [
        os.path.join(home_dir, "Library/Caches/Google"),
        os.path.join(home_dir, "Library/Caches/node-gyp"),
        os.path.join(home_dir, "Library/Caches/ms-playwright"),
        os.path.join(home_dir, "Library/Caches/ms-playwright-go"),
        os.path.join(home_dir, "Library/Caches/org.swift.swiftpm"),
        os.path.join(home_dir, "Library/Caches/pip"),
        os.path.join(home_dir, "Library/Caches/pnpm"),
        os.path.join(home_dir, f".gemini/tmp/{username}/chats"),
        os.path.join(home_dir, f".gemini/tmp/{username}/tool-outputs")
    ]

    for target in targets:
        total_freed += safe_remove(target, dry_run=args.dry_run)

    # Системная очистка
    run_cmd(["brew", "cleanup", "--prune=all"], dry_run=args.dry_run)

    end_time = time.time()
    duration = (end_time - start_time) * 1000
    
    logging.info(f"=== Очистка завершена за {duration:.1f}ms ===")
    if args.dry_run:
        logging.info(f"Всего будет освобождено: {format_size(total_freed)}")
    else:
        logging.info(f"Всего освобождено: {format_size(total_freed)}")
        
    if duration > 15000:
        logging.warning(f"Высокая задержка всего процесса очистки: {duration:.1f}ms")

if __name__ == "__main__":
    main()
