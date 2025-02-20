import sys
import requests

# Конфигурация: замените на ваш домен Bitrix24 и токен вебхука
BITRIX24_DOMAIN = 'bit.paypoint.pro'
WEBHOOK_TOKEN = '334/ns8ufic41u9h1nla'


def get_task_custom_fields(task_id):
    """
    Получает информацию о задаче из Bitrix24 и извлекает кастомные поля.
    """
    url = f"https://{BITRIX24_DOMAIN}/rest/{WEBHOOK_TOKEN}/tasks.task.get"
    params = {
        'taskId': task_id
    }
    response = requests.get(url, params=params)
    if response.ok:
        data = response.json()
        task = data.get('result', {}).get('task', {})
        custom_fields = {}
        for key, value in task.items():
            if key.startswith('UF_'):
                custom_fields[key] = value
        return custom_fields
    else:
        print(f"Ошибка: {response.status_code} - {response.text}")
        return None


if __name__ == '__main__':
    task_id = 62421
    fields = get_task_custom_fields(task_id)
    if fields:
        print("Кастомные поля задачи:")
        for key, value in fields.items():
            print(f"{key}: {value}")
    else:
        print("Не удалось получить кастомные поля.")
