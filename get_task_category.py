import requests
from typing import Optional, Dict, Union

BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/xd11bddxxpimt63p/'

def get_task_custom_fields(task_id: str) -> Dict[str, Optional[str]]:
    """Получение значений кастомных полей для задачи

    Args:
        task_id (str): ID задачи в Битрикс24

    Returns:
        Dict[str, Optional[str]]: Словарь с значениями кастомных полей
    """
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.list.json"
    params = {
        'filter[ID]': task_id,
        'select[]': ['*', 'UF_*', 'UF_CATEGORY', 'UF_IMPORTANCE', 'UF_SIZE']
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        tasks = response.json().get('result', {}).get('tasks', [])
        if not tasks:
            return {'category': None, 'importance': None, 'size': None}
            
        task = tasks[0]
        return {
            'category': task.get('ufCategory'),
            'importance': task.get('ufImportance'),
            'size': task.get('ufSize')
        }

    except Exception as e:
        print(f"Error getting task custom fields: {e}")
        return {'category': None, 'importance': None, 'size': None}

def get_task_category(task_id: str) -> Optional[str]:
    """Получение значения кастомного поля UF_CATEGORY для задачи

    Args:
        task_id (str): ID задачи в Битрикс24

    Returns:
        Optional[str]: Значение поля UF_CATEGORY или None, если поле не найдено
    """
    return get_task_custom_fields(task_id)['category']

def get_task_size(task_id: str) -> Optional[str]:
    """Получение значения кастомного поля UF_SIZE для задачи

    Args:
        task_id (str): ID задачи в Битрикс24

    Returns:
        Optional[str]: Значение поля UF_SIZE или None, если поле не найдено
    """
    return get_task_custom_fields(task_id)['size']

def get_task_importance(task_id: str) -> Optional[str]:
    """Получение значения кастомного поля UF_IMPORTANCE для задачи

    Args:
        task_id (str): ID задачи в Битрикс24

    Returns:
        Optional[str]: Значение поля UF_IMPORTANCE или None, если поле не найдено
    """
    return get_task_custom_fields(task_id)['importance']

