
import asyncio
import sys
import os
import subprocess
import time

async def stress_test():
    processes = []
    print('Starting concurrent load...')
    
    # Calculate main.py location dynamically relative to this script
    test_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(test_dir)
    main_path = os.path.join(project_root, 'engine', 'main.py')
    
    # Запуск 5 параллельных запросов инференса
    for i in range(5):
        processes.append(subprocess.Popen([sys.executable, main_path, 'encode', f'test message {i}'], stdout=subprocess.DEVNULL))
    
    await asyncio.sleep(5)
    # Проверка выживаемости heartbeat
    print('Load complete.')

if __name__ == '__main__':
    asyncio.run(stress_test())

