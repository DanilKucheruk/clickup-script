import requests

# Замените на ваш API ключ для ClickUp
CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'

def create_clickup_checklist(task_id, checklist_data):
    """Создание чеклиста в задаче ClickUp."""
    url = f'https://api.clickup.com/api/v2/task/{task_id}/checklist'
    
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Перебираем все элементы чеклиста из Bitrix и готовим для отправки в ClickUp
    items = []
    for item in checklist_data.values():
        title = item.get('title', '')
        is_complete = item.get('isComplete', 'N') == 'Y'  # Если завершено, то True
        # Добавляем чеклист-элемент в список
        items.append({
            'name': title,
            'checked': is_complete
        })
    
    # Данные для запроса в ClickUp
    data = {
        'checklist': items
    }

    try:
        # Отправка POST-запроса на создание чеклиста в ClickUp
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"Чеклист успешно добавлен в задачу ClickUp: {task_id}")
        else:
            print(f"Ошибка при добавлении чеклиста в ClickUp: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")

def transfer_description_with_checklist(bitrix_task, clickup_task_id):
    """Переносим описание задачи и чеклист в ClickUp."""
    task_id = bitrix_task.get('id', '')
    task_description = f'Задача в Bitrix: https://bit.paypoint.pro/company/personal/user/334/tasks/task/view/{task_id}/' + "\n"
    task_description = task_description + bitrix_task.get('description', '')
    
    # Обработка ссылок и пользователей
    task_description = re.sub(r'\[URL=(.*?)\](.*?)\[/URL\]', r'\1', task_description)
    task_description = re.sub(r'\[USER=(\d+)\](.*?)\[/USER\]', r'@ \1 \2', task_description)

    # Отправка описание задачи в ClickUp (если нужно)
    # Убедитесь, что в ClickUp есть поле для описания
    # Здесь пример просто добавления описания
    description_data = {
        "description": task_description
    }
    
    # Вызываем функцию для создания чеклиста в ClickUp
    create_clickup_checklist(clickup_task_id, bitrix_task.get('checklist', {}))

# Пример использования
bitrix_task = {
    'id': '61945',
    'description': 'Описание задачи с [USER=293]Пользователь[/USER] и [URL=http://example.com]ссылкой[/URL].',
    'checklist': {
        '35205': {'title': 'Pinger', 'isComplete': 'N'},
        '35203': {'title': 'Процессинг', 'isComplete': 'N'},
        '35200': {'title': 'Aml', 'isComplete': 'N'},
        '35198': {'title': 'Ротор', 'isComplete': 'Y'},
        '35193': {'title': 'Кабинет', 'isComplete': 'N'},
        '35192': {'title': 'Web', 'isComplete': 'Y'},
        '35191': {'title': 'Чек-лист 1', 'isComplete': 'N'}
    }
}

clickup_task_id = 'YOUR_CLICKUP_TASK_ID'  # ID задачи в ClickUp
# Переносим описание и чеклист из Bitrix в ClickUp
transfer_description_with_checklist(bitrix_task, clickup_task_id)
