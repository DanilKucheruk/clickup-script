import requests

CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'  # Замените на свой API ключ

def process_checklist_item(checklist_id, item, parent_item_id=None, item_number="1", numbering_map=None, depth=0):
    if depth > 10:  # Защита от бесконечной рекурсии
        print(f"Предупреждение: Достигнута максимальная глубина вложенности для элемента {item['fields']['title']}")
        return

    # Добавляем текущий элемент
    current_item_id = add_checklist_item(checklist_id, item['fields'], parent_item_id)

    if current_item_id:
        print(f"Элемент '{item['fields']['title']}' добавлен в ClickUp с ID: {current_item_id} (глубина: {depth})")
    
        if numbering_map is not None:
            numbering_map[item_number] = current_item_id

        # Обрабатываем потомков, если они есть
        if 'descendants' in item and item['descendants']:
            for index, sub_item in enumerate(item['descendants'], start=1):
                sub_item_number = f"{item_number}.{index}"
                print(f"Обрабатываем подзадачу '{sub_item['fields']['title']}' с номером {sub_item_number}. Родитель: {current_item_id} (глубина: {depth + 1})")
                # Рекурсивно обрабатываем подэлемент с увеличением глубины
                process_checklist_item(
                    checklist_id,
                    sub_item,
                    parent_item_id=current_item_id,
                    item_number=sub_item_number,
                    numbering_map=numbering_map,
                    depth=depth + 1
                )

def add_checklist_item(checklist_id, fields, parent_item_id=None):
    """Добавляет элемент в чеклист в ClickUp."""
    url = f'https://api.clickup.com/api/v2/checklist/{checklist_id}/checklist_item'
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }

    # Получаем название без нумерации
    title = fields.get('title', 'Без названия')
    if ' ' in title:
        # Убираем номер из начала названия
        parts = title.split(' ', 1)
        if parts[0].isdigit():
            title = parts[1]

    checklist_item_data = {
        'name': title,
        'resolved': fields.get('isComplete', False),
    }

    # Логируем перед отправкой запроса
    print(f"Отправка запроса для элемента: {checklist_item_data}")
    
    if parent_item_id:
        checklist_item_data['parent'] = parent_item_id
        print(f"Элемент '{checklist_item_data['name']}' имеет родительский ID: {parent_item_id}")
    else:
        print(f"Элемент '{checklist_item_data['name']}' является корневым элементом (без родителя).")
    
    response = requests.post(url, headers=headers, json=checklist_item_data)

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Ответ от API при добавлении элемента: {data}")  # Печатаем ответ
            items = data.get('checklist', {}).get('items', [])
            if items:
                def find_item_in_tree(items, target_name, parent_id=None):
                    for item in items:
                        if item.get('name') == target_name and item.get('parent') == parent_id:
                            return item.get('id')
                        children = item.get('children', [])
                        if children:
                            result = find_item_in_tree(children, target_name, item.get('id'))
                            if result:
                                return result
                    return None

                item_id = find_item_in_tree(items, checklist_item_data['name'], parent_item_id)
                if item_id:
                    print(f"Элемент добавлен с ID: {item_id}")
                    return item_id
                print(f"Ошибка: Не удалось найти добавленный элемент с именем {checklist_item_data['name']}")
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

def add_checklist_to_task(task_id, checklists):
    """Добавляет чеклисты с их элементами в задачу ClickUp."""
    if not checklists:
        print("Ошибка: пустой чеклист.")
        return

    def create_checklist(task_id, title):
        """Создает чеклист с заданным названием и возвращает его ID."""
        url = f'https://api.clickup.com/api/v2/task/{task_id}/checklist'
        headers = {
            'Authorization': CLICKUP_API_KEY,
            'Content-Type': 'application/json'
        }
        checklist_data = {'name': title}
        response = requests.post(url, headers=headers, json=checklist_data)
        
        if response.status_code == 200:
            return response.json().get('checklist', {}).get('id')
        print(f"Ошибка при создании чеклиста '{title}': {response.status_code} - {response.text}")
        return None

    def process_item(item):
        """Обрабатывает один элемент чеклиста."""
        # Получаем название чеклиста
        title = item['fields'].get('title', '')
        if ' ' in title:
            # Убираем номер из начала названия
            parts = title.split(' ', 1)
            if parts[0].isdigit():
                title = parts[1]
        print(f"Создаем чеклист '{title}'...")

        # Создаем новый чеклист
        checklist_id = create_checklist(task_id, title)
        if checklist_id:
            print(f"Чеклист '{title}' успешно создан. ID: {checklist_id}")

            # Обрабатываем подэлементы этого чеклиста
            if 'descendants' in item:
                for sub_index, sub_item in enumerate(item['descendants'], start=1):
                    print(f"Начинаем обработку элемента {sub_index} '{sub_item['fields'].get('title', 'Без названия')}'")
                    process_checklist_item(
                        checklist_id,
                        sub_item,
                        parent_item_id=None,
                        item_number=str(sub_index),
                        numbering_map={},
                        depth=0
                    )
        else:
            print(f"Ошибка: не удалось создать чеклист '{title}'.")

    # Обрабатываем все элементы чеклиста
    for checklist in checklists:
        if 'descendants' in checklist:
            for item in checklist['descendants']:
                process_item(item)
