#!/usr/bin/env python3
import os
import sys
import time
import socket
import subprocess
import urllib.request
from knowledge_brain import update_process_status, add_telemetry

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_PORT = 5001
API_URL = f"http://localhost:{API_PORT}/health"

# Счетчики перезапусков
restarts = {
    "embedder_server": 0,
    "trinity_daemon": 0
}

def is_port_open(port):
    """Проверяет, открыт ли порт локально."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect(('127.0.0.1', port))
        s.close()
        return True
    except:
        return False

def check_flask_api():
    """Проверяет работоспособность Flask API через эндпоинт health."""
    if not is_port_open(API_PORT):
        return False
    try:
        with urllib.request.urlopen(API_URL, timeout=2.0) as response:
            return response.status == 200
    except:
        return False

def start_flask_api():
    """Запускает Flask API сервер в фоновом режиме."""
    print("Watchdog: перезапуск Flask API сервера...")
    log_file = os.path.join(PROJECT_DIR, "logs/embedder.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Запускаем в фоновом режиме
    cmd = [sys.executable, "tools/embedder_server.py"]
    with open(log_file, "a") as out:
        subprocess.Popen(cmd, cwd=PROJECT_DIR, stdout=out, stderr=out, start_new_session=True)
    
    restarts["embedder_server"] += 1
    add_telemetry("watchdog_restart", 1.0, "embedder_server restarted")

def is_trinity_running():
    """Проверяет, запущен ли демон Trinity (по сокету или процессу)."""
    # Будем искать процессы python3 с trinity в аргументах или запущенный trinity-start
    try:
        output = subprocess.check_output(["pgrep", "-f", "trinity-start.sh|conductor"], text=True)
        return len(output.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def main():
    print("Watchdog демон запущен.")
    add_telemetry("watchdog_status", 1.0, "Watchdog started")
    
    while True:
        try:
            # 1. Проверка Flask API
            api_alive = check_flask_api()
            if not api_alive:
                print("Watchdog: Flask API сервер недоступен!")
                start_flask_api()
                # Ждем 3 секунды, пока запустится
                time.sleep(3)
                api_alive = check_flask_api()
            
            update_process_status("embedder_server", api_alive, restarts["embedder_server"])
            
            # 2. Проверка Trinity демонов
            trinity_alive = is_trinity_running()
            update_process_status("trinity_core", trinity_alive, restarts["trinity_daemon"])
            
            # Пишем общую телеметрию здоровья
            add_telemetry("watchdog_ping", 1.0, f"API: {api_alive}, Trinity: {trinity_alive}")
            
        except Exception as e:
            print(f"Ошибка в цикле watchdog: {e}")
            
        time.sleep(10)

if __name__ == "__main__":
    # Разрешаем запускать напрямую
    try:
        main()
    except KeyboardInterrupt:
        print("Watchdog остановлен.")
