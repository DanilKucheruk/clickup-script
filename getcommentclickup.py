import requests

CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'

def get_clickup_task_with_watchers(task_id):
    """Получение информации о задаче ClickUp по ID задачи, включая наблюдателей (watchers)."""
    url = f"https://api.clickup.com/api/v2/task/{task_id}"
    headers = {'Authorization': CLICKUP_API_KEY}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        task_data = response.json().get('task', {})
        if task_data:
            # Основные данные задачи
            task_name = task_data.get('name', 'Неизвестно')
            task_status = task_data.get('status', {}).get('status', 'Неизвестно')
            task_assignees = [assignee['username'] for assignee in task_data.get('assignees', [])]
            task_priority = task_data.get('priority', {}).get('priority', 'Не установлен')
            task_due_date = task_data.get('due_date', 'Не установлена')

            # Наблюдатели
            task_watchers = [watcher['username'] for watcher in task_data.get('watchers', [])]
            
            print(f"Задача: {task_name}")
            print(f"Статус: {task_status}")
            print(f"Ответственные: {', '.join(task_assignees)}")
            print(f"Приоритет: {task_priority}")
            print(f"Дата выполнения: {task_due_date}")
            print(f"Наблюдатели: {', '.join(task_watchers) if task_watchers else 'Нет наблюдателей'}")
        
        return task_data
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задачи ClickUp для задачи {task_id}: {e}")
        return {}

# Пример вызова
clickup_task_id = "8697ykcbg"
get_clickup_task_with_watchers(clickup_task_id)
