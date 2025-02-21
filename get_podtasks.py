import requests
import json
from typing import List, Dict, Optional

BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/xd11bddxxpimt63p/'

def get_subtasks(parent_id: int) -> List[Dict]:
    """Получение подзадач по ID родительской задачи

    Args:
        parent_id (int): ID родительской задачи

    Returns:
        List[Dict]: Список подзадач с их данными
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
        if 'result' not in response_data:
            print(f"Неожиданный формат ответа: {response_data}")
            return []
            
        tasks = response_data.get('result', {}).get('tasks', [])
        if not tasks:
            print(f"Подзадачи для задачи {parent_id} не найдены")
        return tasks

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении подзадач (ID {parent_id}): {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON ответа: {e}")
        return []

def print_tasks(tasks: List[Dict]) -> None:
    """Вывод информации о задачах в консоль

    Args:
        tasks (List[Dict]): Список задач для вывода
    """
    if not tasks:
        print("Задачи не найдены")
        return

    for task in tasks:
        print(f"ID: {task['id']}")
        print(f"Название: {task['title']}")
        print(f"Ответственный: {task['responsibleId']} ({task['responsible']['name']})")
        print(f"Статус: {task['status']}")
        if task.get('deadline'):
            print(f"Дедлайн: {task['deadline']}")
        print(f"Дата создания: {task['createdDate']}")
        print("-" * 50)

def get_task_ids(tasks: List[Dict]) -> List[str]:
    """Получение списка ID задач

    Args:
        tasks (List[Dict]): Список задач

    Returns:
        List[str]: Список ID задач
    """
    return [task['id'] for task in tasks]

if __name__ == "__main__":
    parent_task_id = 62147
    tasks = get_subtasks(parent_task_id)
    task_ids = get_task_ids(tasks)
    print(task_ids)
