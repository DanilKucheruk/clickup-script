import requests
import json

# 🔹 Ваши API ключи
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'

def get_all_task_tags():
    """Получение всех задач и их тегов и сохранение в файл."""
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.list.json"
    try:
        # Отправка GET-запроса для получения списка задач
        response = requests.get(url)
        response.raise_for_status()  # Проверка на успешность запроса
        tasks = response.json().get('result', [])
        
        # Сохранение данных в файл JSON
        with open('tasks_with_tags.json', 'w', encoding='utf-8') as f:
            json.dump(tasks, f, ensure_ascii=False, indent=4)
        
        print("Данные успешно сохранены в tasks_with_tags.json.")
        
    except requests.exceptions.RequestException as e:
        # Обработка ошибок при запросе
        print(f"Ошибка при получении задач из Bitrix: {e}")

if __name__ == "__main__":
    get_all_task_tags()
