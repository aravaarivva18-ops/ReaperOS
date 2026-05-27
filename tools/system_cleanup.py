#!/usr/bin/env python3
import os
import sys
import shutil
import logging
import time
import subprocess
import argparse
import gzip
from datetime import datetime, timedelta

# Настройка путей
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "cleanup.log")

# Создаем папку логов, если ее нет
os.makedirs(LOGS_DIR, exist_ok=True)

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

def rotate_logs(max_size_mb=5, keep_days=14, dry_run=False):
    """Выполняет ротацию и сжатие логов."""
    logging.info("=== Запуск ротации логов ===")
    if not os.path.exists(LOGS_DIR):
        return
        
    now = datetime.now()
    retention_cutoff = now - timedelta(days=keep_days)
    
    for filename in os.listdir(LOGS_DIR):
        filepath = os.path.join(LOGS_DIR, filename)
        if not os.path.isfile(filepath):
            continue
            
        # Удаление старых архивов логов
        if filename.endswith(".gz"):
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < retention_cutoff:
                if dry_run:
                    logging.info(f"[DRY-RUN] Будет удален старый архив лога: {filename}")
                else:
                    try:
                        os.remove(filepath)
                        logging.info(f"Удален старый архив лога: {filename}")
                    except Exception as e:
                        logging.error(f"Не удалось удалить архив лога {filename}: {e}")
            continue
            
        # Исключаем текущий файл очистки во время его записи (чтобы избежать коллизий)
        if filename == "cleanup.log":
            continue
            
        # Проверка размера и ротация обычных логов
        try:
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if size_mb > max_size_mb:
                timestamp = now.strftime("%Y%m%d_%H%M%S")
                archive_name = f"{filename}.{timestamp}.gz"
                archive_path = os.path.join(LOGS_DIR, archive_name)
                
                if dry_run:
                    logging.info(f"[DRY-RUN] Будет сжат лог: {filename} -> {archive_name}")
                else:
                    logging.info(f"Сжатие лога: {filename} ({format_size(os.path.getsize(filepath))}) -> {archive_name}")
                    with open(filepath, 'rb') as f_in:
                        with gzip.open(archive_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    # Очищаем исходный файл лога
                    open(filepath, 'w').close()
        except Exception as e:
            logging.error(f"Ошибка при обработке лога {filename}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Автоматическая фоновая очистка системы Reaper OS")
    parser.add_argument("--dry-run", action="store_true", help="Запуск в режиме симуляции")
    args = parser.parse_args()

    start_time = time.time()
    logging.info("=== Запуск очистки системы ===")
    if args.dry_run:
        logging.info("Режим симуляции (dry-run) активен.")

    total_freed = 0

    # Список путей для полной очистки caches
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

    # Запуск ротации и сжатия логов проекта
    rotate_logs(dry_run=args.dry_run)

    # Системная очистка brew
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
