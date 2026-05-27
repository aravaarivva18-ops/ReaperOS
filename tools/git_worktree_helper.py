#!/usr/bin/env python3
import os
import subprocess
import shutil

def create_worktree(worktree_path):
    """
    Создает изолированное git-дерево (worktree) в режиме detached HEAD на базе текущего коммита.
    """
    if os.path.exists(worktree_path):
        print(f"Путь {worktree_path} уже существует. Пытаемся принудительно удалить...")
        remove_worktree(worktree_path)
        
    print(f"Git Worktree: создание дерева в {worktree_path}...")
    try:
        # Добавляем worktree в режиме detached HEAD на основе текущего коммита HEAD
        subprocess.run(
            ["git", "worktree", "add", "--detach", worktree_path, "HEAD"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Git Worktree успешно создан.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании Git Worktree: {e.stderr.decode().strip()}")
        return False

def remove_worktree(worktree_path):
    """
    Удаляет изолированное git-дерево и очищает метаданные git.
    """
    print(f"Git Worktree: удаление дерева {worktree_path}...")
    try:
        # Принудительно удаляем worktree из git
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Предупреждение при удалении из реестра Git: {e.stderr.decode().strip()}")
        # Если git не может удалить, пробуем удалить папку физически
        if os.path.exists(worktree_path):
            try:
                shutil.rmtree(worktree_path)
            except Exception as ex:
                print(f"❌ Не удалось физически удалить папку {worktree_path}: {ex}")
                
    # Очищаем устаревшие метаданные
    try:
        subprocess.run(
            ["git", "worktree", "prune"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("✅ Git Worktree успешно удален и реестр очищен.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении git worktree prune: {e.stderr.decode().strip()}")
        return False

if __name__ == "__main__":
    # Тестовый запуск
    test_path = os.path.expanduser("~/reaper_test_worktree")
    if create_worktree(test_path):
        remove_worktree(test_path)
