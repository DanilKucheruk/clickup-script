import requests
import json

# 🔹 Ваши API ключи
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/gvjddzm83i5hmitz/disk.file.get.json?id='

def get_link_to_image(file_id):
    url = f"{BITRIX24_WEBHOOK_URL}{file_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Проверяем, что ключ 'result' есть в ответе
        if 'result' in data:
            # Возвращаем DETAIL_URL, так как это ссылка на файл
            return data['result'].get('DETAIL_URL')
        else:
            print("Ошибка: Неверный формат ответа или нет данных в 'result'")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return None
