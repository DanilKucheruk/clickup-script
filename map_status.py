import requests

CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'  # Замените на свой API ключ

def add_checklist_item(checklist_id, fields, parent_item_id=None, item_number=None):
    """Добавляет элемент в чеклист в ClickUp с учетом нумерации и правильной привязкой подзадач."""
    url = f'https://api.clickup.com/api/v2/checklist/{checklist_id}/checklist_item'
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }
    
    checklist_item_data = {
        'name': f"{item_number} {fields.get('title', 'Без названия')}",  # Нумерация перед названием
        'completed': fields.get('isComplete', False),
    }
    
    if parent_item_id:  # Указываем родительский элемент, если он есть
        checklist_item_data['parent'] = parent_item_id
    
    response = requests.post(url, headers=headers, json=checklist_item_data)
    
    print(f"Ответ API: {response.status_code} - {response.text}")  # Выводим полный ответ API для диагностики
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Ответ от API при добавлении элемента: {data}")  # Печатаем весь ответ
            items = data.get('checklist', {}).get('items', [])
            if items:
                # Получаем последний элемент и его ID
                item_id = items[-1].get('id')
                if item_id:
                    return item_id  # Возвращаем ID добавленного элемента
                else:
                    print(f"Ошибка: Не удалось найти ID элемента в ответе API.")
                    return None
            else:
                print(f"Ошибка: В ответе API отсутствуют элементы чеклиста.")
                return None
        except Exception as e:
            print(f"Ошибка при обработке ответа: {e}")
            return None
    else:
        print(f"Ошибка API при добавлении элемента: {response.status_code} - {response.text}")
        return None


def process_checklist_item(checklist_id, item, parent_item_id=None, item_number="1", numbering_map=None):
    """Обрабатывает каждый элемент чеклиста и добавляет его в ClickUp с нумерацией и правильной привязкой подзадач."""
    
    # Добавляем текущий элемент в ClickUp
    item_id = add_checklist_item(checklist_id, item['fields'], parent_item_id, item_number)
    
    if item_id:
        print(f"Элемент '{item['fields']['title']}' добавлен в ClickUp с ID: {item_id}")
        
        # Печатаем информацию о родителе, к которому привязан элемент
        if parent_item_id:
            print(f"Элемент '{item['fields']['title']}' привязан к родителю с ID: {parent_item_id}")
        else:
            print(f"Элемент '{item['fields']['title']}' не имеет родителя (корневой элемент).")
        
        # Сохраняем ID элемента в словарь для будущих привязок
        if numbering_map is not None:
            numbering_map[item_number] = item_id
        
        # Если у элемента есть подзадачи (descendants), обрабатываем их
        if 'descendants' in item:
            for index, sub_item in enumerate(item['descendants'], start=1):
                sub_item_number = f"{item_number}.{index}"  # Формируем номер подзадачи
                # Передаем текущий item_id как родитель для подзадачи
                process_checklist_item(checklist_id, sub_item, parent_item_id=item_id, item_number=sub_item_number, numbering_map=numbering_map)


def add_checklist_tree_to_task(task_id, checklist_tree):
    """Добавляет чеклист с его элементами (дерево) в задачу ClickUp."""
    if not checklist_tree.get('descendants'):
        print("Ошибка: в чеклисте отсутствуют элементы.")
        return
    
    checklist_root = checklist_tree['descendants'][0]
    checklist_name = checklist_root['fields'].get('title', 'Чеклист из Битрикса')
    
    url = f'https://api.clickup.com/api/v2/task/{task_id}/checklist'
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }
    checklist_data = {'name': checklist_name}
    
    response = requests.post(url, headers=headers, json=checklist_data)
    
    if response.status_code == 200:
        checklist_id = response.json().get('checklist', {}).get('id')
        if checklist_id:
            print(f"Чеклист '{checklist_name}' успешно создан. ID: {checklist_id}")
            
            # Словарь для хранения соответствий нумерации и ID
            numbering_map = {}
            
            # Обрабатываем все элементы чеклиста (включая подзадачи) с нумерацией начиная с 1
            for index, item in enumerate(checklist_root.get('descendants', []), start=1):
                item_number = str(index)  # Начинаем с 1 для первого элемента
                process_checklist_item(checklist_id, item, parent_item_id=None, item_number=item_number, numbering_map=numbering_map)
        else:
            print("Ошибка: не удалось извлечь ID чеклиста.")
    else:
        print(f"Ошибка при добавлении чеклиста: {response.status_code} - {response.text}")

bitrix_checklist_tree = {
        "nodeId": 0,
        "fields": {
            "id": None,
            "copiedId": None,
            "entityId": None,
            "userId": 334,
            "createdBy": None,
            "parentId": None,
            "title": "",
            "sortIndex": None,
            "displaySortIndex": "",
            "isComplete": False,
            "isImportant": False,
            "completedCount": 0,
            "members": [],
            "attachments": []
        },
        "action": [],
        "descendants": [
            {
                "nodeId": 1,
                "fields": {
                    "id": 35191,
                    "copiedId": None,
                    "entityId": 61945,
                    "userId": 334,
                    "createdBy": 293,
                    "parentId": 0,
                    "title": "Чек-лист 1",
                    "sortIndex": 0,
                    "displaySortIndex": "",
                    "isComplete": False,
                    "isImportant": False,
                    "completedCount": 0,
                    "members": [],
                    "attachments": []
                },
                "action": {
                    "modify": True,
                    "remove": True,
                    "toggle": True,
                    "add": True,
                    "addAccomplice": True
                },
                "descendants": [
                    {
                        "nodeId": 2,
                        "fields": {
                            "id": 35192,
                            "copiedId": None,
                            "entityId": 61945,
                            "userId": 334,
                            "createdBy": 293,
                            "parentId": 35191,
                            "title": "Web",
                            "sortIndex": 0,
                            "displaySortIndex": "1",
                            "isComplete": False,
                            "isImportant": False,
                            "completedCount": 0,
                            "members": [],
                            "attachments": []
                        },
                        "action": {
                            "modify": True,
                            "remove": True,
                            "toggle": True,
                            "add": True,
                            "addAccomplice": True
                        },
                        "descendants": [
                            {
                                "nodeId": 3,
                                "fields": {
                                    "id": 35193,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35192,
                                    "title": "Кабинет",
                                    "sortIndex": 0,
                                    "displaySortIndex": "1.1",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            },
                            {
                                "nodeId": 4,
                                "fields": {
                                    "id": 35194,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35192,
                                    "title": "Сервис авторизации",
                                    "sortIndex": 1,
                                    "displaySortIndex": "1.2",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            },
                            {
                                "nodeId": 5,
                                "fields": {
                                    "id": 35195,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35192,
                                    "title": "Мерчант",
                                    "sortIndex": 2,
                                    "displaySortIndex": "1.3",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            },
                            {
                                "nodeId": 6,
                                "fields": {
                                    "id": 35196,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35192,
                                    "title": "Сокет",
                                    "sortIndex": 3,
                                    "displaySortIndex": "1.4",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            }
                        ]
                    },
                    {
                        "nodeId": 3,
                        "fields": {
                            "id": 35197,
                            "copiedId": None,
                            "entityId": 61945,
                            "userId": 334,
                            "createdBy": 293,
                            "parentId": 35191,
                            "title": "Gates",
                            "sortIndex": 1,
                            "displaySortIndex": "2",
                            "isComplete": False,
                            "isImportant": False,
                            "completedCount": 1,
                            "members": [],
                            "attachments": []
                        },
                        "action": {
                            "modify": True,
                            "remove": True,
                            "toggle": True,
                            "add": True,
                            "addAccomplice": True
                        },
                        "descendants": [
                            {
                                "nodeId": 4,
                                "fields": {
                                    "id": 35198,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35197,
                                    "title": "Ротор",
                                    "sortIndex": 0,
                                    "displaySortIndex": "2.1",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            },
                            {
                                "nodeId": 5,
                                "fields": {
                                    "id": 35210,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35197,
                                    "title": "Мульти-Генератор",
                                    "sortIndex": 1,
                                    "displaySortIndex": "2.2",
                                    "isComplete": True,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            },
                            {
                                "nodeId": 6,
                                "fields": {
                                    "id": 35199,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35197,
                                    "title": "Микросервисы",
                                    "sortIndex": 2,
                                    "displaySortIndex": "2.3",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": [
                                    {
                                        "nodeId": 7,
                                        "fields": {
                                            "id": 35200,
                                            "copiedId": None,
                                            "entityId": 61945,
                                            "userId": 334,
                                            "createdBy": 293,
                                            "parentId": 35199,
                                            "title": "Aml",
                                            "sortIndex": 0,
                                            "displaySortIndex": "2.3.1",
                                            "isComplete": False,
                                            "isImportant": False,
                                            "completedCount": 0,
                                            "members": [],
                                            "attachments": []
                                        },
                                        "action": {
                                            "modify": True,
                                            "remove": True,
                                            "toggle": True,
                                            "add": True,
                                            "addAccomplice": True
                                        },
                                        "descendants": []
                                    },
                                    {
                                        "nodeId": 8,
                                        "fields": {
                                            "id": 35201,
                                            "copiedId": None,
                                            "entityId": 61945,
                                            "userId": 334,
                                            "createdBy": 293,
                                            "parentId": 35199,
                                            "title": "Loki",
                                            "sortIndex": 1,
                                            "displaySortIndex": "2.3.2",
                                            "isComplete": False,
                                            "isImportant": False,
                                            "completedCount": 0,
                                            "members": [],
                                            "attachments": []
                                        },
                                        "action": {
                                            "modify": True,
                                            "remove": True,
                                            "toggle": True,
                                            "add": True,
                                            "addAccomplice": True
                                        },
                                        "descendants": []
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "nodeId": 4,
                        "fields": {
                            "id": 35202,
                            "copiedId": None,
                            "entityId": 61945,
                            "userId": 334,
                            "createdBy": 293,
                            "parentId": 35191,
                            "title": "Processing",
                            "sortIndex": 2,
                            "displaySortIndex": "3",
                            "isComplete": False,
                            "isImportant": False,
                            "completedCount": 0,
                            "members": [],
                            "attachments": []
                        },
                        "action": {
                            "modify": True,
                            "remove": True,
                            "toggle": True,
                            "add": True,
                            "addAccomplice": True
                        },
                        "descendants": [
                            {
                                "nodeId": 5,
                                "fields": {
                                    "id": 35203,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35202,
                                    "title": "Процессинг",
                                    "sortIndex": 0,
                                    "displaySortIndex": "3.1",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            }
                        ]
                    },
                    {
                        "nodeId": 5,
                        "fields": {
                            "id": 35204,
                            "copiedId": None,
                            "entityId": 61945,
                            "userId": 334,
                            "createdBy": 293,
                            "parentId": 35191,
                            "title": "Dev-Ops",
                            "sortIndex": 3,
                            "displaySortIndex": "4",
                            "isComplete": False,
                            "isImportant": False,
                            "completedCount": 0,
                            "members": [],
                            "attachments": []
                        },
                        "action": {
                            "modify": True,
                            "remove": True,
                            "toggle": True,
                            "add": True,
                            "addAccomplice": True
                        },
                        "descendants": [
                            {
                                "nodeId": 6,
                                "fields": {
                                    "id": 35205,
                                    "copiedId": None,
                                    "entityId": 61945,
                                    "userId": 334,
                                    "createdBy": 293,
                                    "parentId": 35204,
                                    "title": "Pinger",
                                    "sortIndex": 0,
                                    "displaySortIndex": "4.1",
                                    "isComplete": False,
                                    "isImportant": False,
                                    "completedCount": 0,
                                    "members": [],
                                    "attachments": []
                                },
                                "action": {
                                    "modify": True,
                                    "remove": True,
                                    "toggle": True,
                                    "add": True,
                                    "addAccomplice": True
                                },
                                "descendants": []
                            }
                        ]
                    }
                ]
            }
        ]
    }

if __name__ == "__main__":
    TASK_ID = "8697yvhgm"
    add_checklist_tree_to_task(TASK_ID, bitrix_checklist_tree)
