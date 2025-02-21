import requests

BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/qlhdwbxoy6zj10gy/'

def get_selected_fields_for_task(task_id):
    """Получение выбранных значений для пользовательских полей задачи."""
    url = f"{BITRIX24_WEBHOOK_URL}task.item.userfield.getlist.json"
    
    params = {
        'TASK_ID': task_id
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        # Получаем данные
        data = response.json()
        
        if 'result' in data:
            user_fields = data['result']
            print("Полные данные о полях:")
            print(data)  # Выведем полный ответ для диагностики
            
            selected_values = {}
            for field in user_fields:
                field_name = field['FIELD_NAME']
                # Выведем информацию о поле для диагностики
                print(f"\nДанные для поля {field_name}:")
                print(field)
                
                # Проверим наличие значений
                if 'LIST' in field and len(field['LIST']) > 0:
                    for item in field['LIST']:
                        print(f"  Значение: {item['VALUE']}, по умолчанию: {item.get('DEF', 'N')}")
                        if item.get('DEF') == 'Y':  # Значение по умолчанию
                            selected_values[field_name] = item['VALUE']
                            break
                    else:
                        selected_values[field_name] = None
                else:
                    selected_values[field_name] = None

            return selected_values
        
        else:
            print(f"Нет данных для задачи с ID {task_id}")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных о задаче: {e}")
        return None

# Пример вызова функции
task_id = 63062  # Замените на ID вашей задачи
selected_fields = get_selected_fields_for_task(task_id)

if selected_fields:
    print("\nВыбранные значения для задачи:")
    for field_name, value in selected_fields.items():
        print(f"{field_name}: {value}")
else:
    print("Не удалось получить выбранные значения.")
