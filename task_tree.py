import requests
from typing import List, Dict, Optional
import sys
from pathlib import Path

# Добавляем путь к release в PYTHONPATH
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from release.script import transfer_task
import time

BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/xd11bddxxpimt63p/'
GROUP_ID = 279

def get_task_details(task_id: str) -> Optional[Dict]:
    """Получение детальной информации о задаче

    Args:
        task_id (str): ID задачи

    Returns:
        Optional[Dict]: Информация о задаче или None в случае ошибки
    """
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.get.json"
    params = {'taskId': task_id}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get('result', {}).get('task')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении информации о задаче {task_id}: {e}")
        return None

def get_subtasks(parent_id: str) -> List[Dict]:
    """Получение подзадач по ID родительской задачи

    Args:
        parent_id (str): ID родительской задачи

    Returns:
        List[Dict]: Список подзадач
    """
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.list.json"
    params = {
        'filter[PARENT_ID]': parent_id,
        'select[]': ['ID', 'TITLE', 'RESPONSIBLE_ID', 'STATUS', 'CREATED_DATE', 'DEADLINE']
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        response_data = response.json()
        return response_data.get('result', {}).get('tasks', [])
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении подзадач (ID {parent_id}): {e}")
        return []

def get_root_tasks(group_id: int) -> List[str]:
    """Получение корневых задач группы (PARENT_ID = 0)

    Args:
        group_id (int): ID группы

    Returns:
        List[str]: Список ID корневых задач
    """
    url = f"{BITRIX24_WEBHOOK_URL}task.ctasks.getlist.json"
    params = {'filter[GROUP_ID]': group_id}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        response_data = response.json()
        tasks = response_data.get('result', [])

        return [
            task['ID'] for task in tasks 
            if int(task.get('PARENT_ID', 0)) == 0 and int(task.get('GROUP_ID', 0)) == group_id
        ]
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задач: {e}")
        return []

def process_task_tree(task_id: str, level: int = 0) -> List[str]:
    """Рекурсивный обход дерева задач с сохранением порядка

    Args:
        task_id (str): ID задачи
        level (int): Уровень вложенности

    Returns:
        List[str]: Список ID задач в порядке обхода
    """
    task = get_task_details(task_id)
    if not task:
        return []

    indent = "  " * level
    print(f"{indent}└─ {task_id}")
    
    # Сначала добавляем текущую задачу
    tasks_order = [task_id]
    
    # Затем обрабатываем все подзадачи
    subtasks = get_subtasks(task_id)
    for subtask in subtasks:
        tasks_order.extend(process_task_tree(subtask['id'], level + 1))
    
    return tasks_order

def main():
    print("Получение дерева задач...")
    root_tasks = get_root_tasks(GROUP_ID)
    
    if not root_tasks:
        print("Корневые задачи не найдены")
        return
    
    all_tasks = []
    print("Структура задач:")
    for task_id in root_tasks:
        tasks_in_tree = process_task_tree(task_id)
        all_tasks.extend(tasks_in_tree)
        print()
    
    print(f"\nОбщее количество задач: {len(all_tasks)}")
    
    print("\nНачинаем перенос задач в ClickUp...")
    
    # Переносим задачи в порядке их иерархии
    batch_size = 5  # Количество задач в одной партии
    for i in range(0, len(all_tasks), batch_size):
        batch = all_tasks[i:i + batch_size]
        print(f"\nПеренос задач {i+1}-{min(i+batch_size, len(all_tasks))} из {len(all_tasks)}")
        transfer_task(batch)
        
        # Небольшая пауза между партиями
        if i + batch_size < len(all_tasks):
            print("Пауза 0.5 секунд перед следующей партией...")
    
    print("\n✅ Перенос задач завершен!")

if __name__ == "__main__":
    main()
