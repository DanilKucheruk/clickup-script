import requests
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'

def get_bitrix_task_category_and_priority(task_id):
    """
    Получает категорию и важность задачи из Bitrix24
    
    Args:
        task_id (int): ID задачи в Bitrix24
        
    Returns:
        tuple: (category, priority) или (None, None) в случае ошибки
    """
    # Получаем данные задачи
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.get.json"
    params = {
        "taskId": task_id,
        "select[]": ["PRIORITY", "TAGS"]  # Добавляем поля PRIORITY и TAGS
    }

    try:
        # Получаем данные задачи
        response = requests.get(url, params=params)
        response.raise_for_status()
        task_data = response.json()
        
        if not task_data.get('result'):
            print(f"Ошибка: Не удалось получить данные задачи {task_id}")
            return None, None
            
        task = task_data['result']['task']
        
        # Получаем теги задачи из основного ответа API
        tags = task.get('tags', [])
        category = None
        for tag in tags:
            if tag.startswith('П'):
                category = "Dev / ⚛️ Новый функционал"
                break
        
        # Определяем важность
        priority_map = {
            0: "⨳⨳⨳⨳⨳ Экстренная",
            1: "⨳⨳⨳⨳ Высокая",
            2: "⨳⨳⨳ Обычная",
            3: "⨳⨳ Низкая",
            4: "⨳ Очень низкая"
        }
        priority = priority_map.get(int(task.get('priority', 2)), "⨳⨳⨳ Обычная")
        
        return category, priority
        
    except Exception as e:
        print(f"Ошибка при получении категории и важности: {str(e)}")
        return None, None

# Пример использования:
if __name__ == "__main__":
    task_id = input("Введите ID задачи: ")
    category, priority = get_bitrix_task_category_and_priority(task_id)
    if category and priority:
        print(f"Категория: {category}")
        print(f"Важность: {priority}")




if __name__ == "__main__":
    task_id = input("Введите ID задачи: ")
    get_bitrix_task_priority(task_id)