import requests

CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'  # Замените на свой API ключ

def process_checklist_item(checklist_id, item, parent_item_id=None, item_number="1", numbering_map=None, depth=0):
    if depth > 10:  # Защита от бесконечной рекурсии
        print(f"Предупреждение: Достигнута максимальная глубина вложенности для элемента {item.get('fields', {}).get('title', 'Без названия')}")
        return

    # Проверяем, что у элемента есть поле fields
    if 'fields' not in item:
        print(f"Предупреждение: Элемент не содержит поле 'fields': {item}")
        return

    # Добавляем текущий элемент
    current_item_id = add_checklist_item(checklist_id, item['fields'], parent_item_id)

    if current_item_id:
        print(f"Элемент '{item['fields'].get('title', 'Без названия')}' добавлен в ClickUp с ID: {current_item_id} (глубина: {depth})")
    
        if numbering_map is not None:
            numbering_map[item_number] = current_item_id

        # Обрабатываем потомков, если они есть
        descendants = item.get('descendants', [])
        if descendants:
            for index, sub_item in enumerate(descendants, start=1):
                sub_item_number = f"{item_number}.{index}"
                sub_title = sub_item.get('fields', {}).get('title', 'Без названия')
                print(f"Обрабатываем подзадачу '{sub_title}' с номером {sub_item_number}. Родитель: {current_item_id} (глубина: {depth + 1})")
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

    # Получаем название и описание
    title = fields.get('title', 'Без названия')
    description = fields.get('description', '')

    # Если есть описание, добавляем его к названию
    if description:
        title = f"{title}\n{description}"

    # Преобразуем HTML в markdown
    title = title.replace('<b>', '**').replace('</b>', '**')
    title = title.replace('<i>', '_').replace('</i>', '_')
    title = title.replace('<code>', '`').replace('</code>', '`')
    title = title.replace('<pre>', '```\n').replace('</pre>', '\n```')
    title = title.replace('<br>', '\n').replace('<br/>', '\n')
    title = title.replace('&nbsp;', ' ')

    # Если в начале есть цифры с точкой, убираем их
    if ' ' in title:
        parts = title.split(' ', 1)
        if parts[0].replace('.', '').isdigit():
            title = parts[1]

    checklist_item_data = {
        'name': title,
        'resolved': fields.get('isComplete', False),
    }

    # Логируем перед отправкой запроса
    
    if parent_item_id:
        checklist_item_data['parent'] = parent_item_id
    
    response = requests.post(url, headers=headers, json=checklist_item_data)

    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Ответ от API при добавлении элемента: {data}")
            
            # Получаем ID созданного элемента из ответа
            items = data.get('checklist', {}).get('items', [])
            if items:
                # Ищем последний добавленный элемент с нужным именем
                for item in reversed(items):
                    if item.get('name') == checklist_item_data['name']:
                        item_id = item.get('id')
                        if item_id:
                            print(f"Элемент добавлен с ID: {item_id}")
                            return item_id
            
            # print(f"Ошибка: В ответе API отсутствует ID элемента чеклиста")
            return None
                
        except Exception as e:
            # print(f"Ошибка при обработке ответа: {e}")
            return None
    else:
        # print(f"Ошибка API при добавлении элемента: {response.status_code} - {response.text}")
        return None

def add_checklist_to_task(task_id, checklists):
    """Добавляет чеклисты с их элементами в задачу ClickUp."""
    print("=== Начало обработки чеклистов ===")
    
    def process_checklist(checklist_data):
        """Обрабатывает отдельный чеклист"""
        if not isinstance(checklist_data, dict):
            return
            
        fields = checklist_data.get('fields', {})
        if not fields:
            print("Нет полей в чеклисте")
            return
            
        title = fields.get('title', 'Чеклист')
        print(f"Создаем чеклист '{title}'...")
        
        checklist_id = create_checklist(task_id, title)
        if not checklist_id:
            return
            
        descendants = checklist_data.get('descendants', [])
        if descendants:
            print(f"Обрабатываем {len(descendants)} элементов чеклиста...")
            process_checklist_items(checklist_id, descendants)

    try:
        if isinstance(checklists, list):
            for checklist in checklists:
                process_checklist(checklist)
        elif isinstance(checklists, dict):
            if 'descendants' in checklists:
                for checklist in checklists['descendants']:
                    process_checklist(checklist)
            else:
                process_checklist(checklists)
    except Exception as e:
        print(f"Критическая ошибка при обработке чеклистов: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("=== Конец обработки чеклистов ===")

def create_checklist(task_id, title):
    """Создает чеклист с заданным названием и возвращает его ID."""
    if not task_id:
        print(f"Ошибка: task_id не может быть пустым при создании чеклиста '{title}'")
        return None
        
    print(f"Создание чеклиста с названием '{title}' для задачи {task_id}")
    url = f'https://api.clickup.com/api/v2/task/{task_id}/checklist'
    headers = {
        'Authorization': f'{CLICKUP_API_KEY}',
        'Content-Type': 'application/json'
    }
    checklist_data = {'name': title}
    
    try:
        response = requests.post(url, headers=headers, json=checklist_data)
        # rint(f"Ответ API при создании чеклиста: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            checklist_id = response.json().get('checklist', {}).get('id')
            return checklist_id
        # print(f"Ошибка при создании чеклиста '{title}': {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Исключение при создании чеклиста '{title}': {str(e)}")
    return None

def process_checklist_items(checklist_id, items, parent_id=None, depth=0):
    """Обрабатывает элементы чеклиста."""
    if depth > 10:  # Защита от бесконечной рекурсии
        print(f"Предупреждение: Достигнута максимальная глубина вложенности")
        return

    # print(f"Тип данных items: {type(items)}")
    # print(f"Содержимое items: {items}")

    for sub_index, sub_item in enumerate(items, start=1):
        # print(f"Начинаем обработку элемента {sub_index} (глубина: {depth}):")
        # print(f"Содержимое sub_item: {sub_item}")
        
        # Создаем текущий элемент
        current_item_id = process_checklist_item(
            checklist_id,
            sub_item,
            parent_item_id=parent_id,
            item_number=str(sub_index),
            numbering_map={},
            depth=depth
        )
        
        # Обрабатываем вложенные элементы
        if current_item_id and 'descendants' in sub_item and sub_item['descendants']:
            process_checklist_items(
                checklist_id,
                sub_item['descendants'],
                parent_id=current_item_id,
                depth=depth + 1
            )
