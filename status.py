import requests

BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'
task_id = '63427'  # Замените на нужный ID задачи

# Формируем запрос
url = f"{BITRIX24_WEBHOOK_URL}tasks.task.get"

try:
    response = requests.get(url, params={"taskId": task_id})
    response.raise_for_status()  # Если ошибка, выбрасывает исключение
    
    # Извлекаем данные из ответа
    task_data = response.json().get('result', {}).get('task', {})
    
    # Получаем статус задачи
    status = task_data.get('priority')
    
    if status is not None:
        print(f"Статус задачи: {status}")
    else:
        print("Статус не найден.")
        
except requests.exceptions.RequestException as e:
    print(f"Ошибка при получении данных о задаче: {e}")
