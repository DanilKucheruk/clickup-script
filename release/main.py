import requests

# Ваши API ключи и настройки
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'
CLICKUP_API_KEY = 'your_clickup_api_key'
CLICKUP_LIST_ID = 'your_clickup_list_id'


# Функция для переноса задачи из Bitrix в ClickUp
def create_clickup_task(bitrix_task):
    url = f"https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task"
    headers = {
        'Authorization': CLICKUP_API_KEY
    }
    data = {
        'name': bitrix_task['TITLE'],
        'description': bitrix_task['DESCRIPTION'],
        'assignees': [map_bitrix_user_to_clickup(bitrix_task['RESPONSIBLE_ID'])],
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        clickup_task = response.json()
        return clickup_task['id']  # Возвращаем ID задачи в ClickUp
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании задачи в ClickUp: {e}")
        return None

# Функция для получения подзадач для задачи Bitrix
def get_bitrix_subtasks(task_id):
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.getList"
    params = {
        'filter': {
            'PARENT_ID': task_id  # Фильтруем подзадачи по родительскому ID
        },
        'select[]': ['ID', 'TITLE', 'DESCRIPTION', 'RESPONSIBLE_ID', 'STATUS']
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        subtasks = response.json().get('result', [])
        return subtasks
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении подзадач для задачи {task_id}: {e}")
        return []

# Основная функция для запуска процесса
def main():
    # Получаем все задачи без родительских для группы (проект)
    group_id = 1  # Пример ID группы
    tasks = get_bitrix_tasks_without_parent(group_id)
    
    # Переносим каждую задачу и ее подзадачи
    for task in tasks:
        transfer_task_and_subtasks(task)

if __name__ == "__main__":
    main()
