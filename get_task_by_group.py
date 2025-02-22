import requests

# Ваш webhook URL для Bitrix24
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'

# ID группы (прим. - используйте нужный ID группы)
GROUP_ID = 279  # Замените на ID вашей группы

def get_tasks_by_group(group_id):
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.getList"
    params = {
        'filter': {
            'GROUP_ID': group_id,  # Фильтруем по ID группы
        },
        'select[]': ['ID'],  # Указываем нужные поля для задачи
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        tasks = response.json().get('result', [])
        return tasks
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задач: {e}")
        return []

# Получаем все задачи для группы с ID = 1
tasks = get_tasks_by_group(GROUP_ID)

for task in tasks:
    print(f"Задача ID: {task['ID']}")
