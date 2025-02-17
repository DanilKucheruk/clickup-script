import re

def trancfer_descriprion(bitrix_task):
    """
    Конвертирует описание задачи из Bitrix BB-кодов в формат ClickUp
    """
    task_id = bitrix_task.get('id', '')
    task_description = f'Задача в Bitrix: https://bit.paypoint.pro/company/personal/user/334/tasks/task/view/{task_id}/\n\n'
    description = bitrix_task.get('description', '')
    
    # Преобразование BB-кодов в формат ClickUp
    
    # Сохраняем переносы строк
    description = description.replace('\n', '\n')
    
    # Жирный текст
    description = re.sub(r'\[B\](.*?)\[/B\]', r'<b>\1</b>', description)
    
    # Курсив
    description = re.sub(r'\[I\](.*?)\[/I\]', r'<i>\1</i>', description)
    
    # Подчеркнутый текст
    description = re.sub(r'\[U\](.*?)\[/U\]', r'<u>\1</u>', description)
    
    # Списки
    description = re.sub(r'\[LIST\]\s*([\s\S]*?)\[/LIST\]', lambda m: '\n'.join([f'• {line.strip()}' for line in m.group(1).split('[*]') if line.strip()]), description)
    
    # Ссылки
    description = re.sub(r'\[URL=(.*?)\](.*?)\[/URL\]', r'<a href="\1">\2</a>', description)
    
    # Упоминания пользователей
    description = re.sub(r'\[USER=(\d+)\](.*?)\[/USER\]', r'@\2', description)
    
    # Цитаты
    description = re.sub(r'\[QUOTE\](.*?)\[/QUOTE\]', r'<blockquote>\1</blockquote>', description)
    
    # Код
    description = re.sub(r'\[CODE\](.*?)\[/CODE\]', r'<code>\1</code>', description)
    
    # Обрабатываем специальные случаи с параметрами
    lines = []
    for line in description.split('\n'):
        # Обрабатываем строки с параметрами
        if '•' in line or '*' in line:
            # Убираем маркеры списка
            line = line.replace('•', '').replace('*', '').strip()
            
            # Ищем параметр и его описание
            if ' - ' in line:
                param, desc = line.split(' - ', 1)
                # Убираем лишние пробелы и форматирование
                param = param.strip().replace('<b>', '').replace('</b>', '')
                desc = desc.strip().replace('<b>', '').replace('</b>', '')
                # Добавляем форматирование в стиле ClickUp
                line = f"• <b>{param}</b> - {desc}"
            else:
                line = f"• {line}"
        
        lines.append(line)
    
    # Удаляем оставшиеся BB-коды
    description = re.sub(r'\[.*?\]', '', '\n'.join(lines))
    
    # Убираем множественные пустые строки
    description = re.sub(r'\n{3,}', '\n\n', description)
    
    task_description += description
    return task_description

# def process_checklist(checklist_data):
#     """Обработка чеклиста в формате Bitrix в строку для описания задачи в ClickUp."""
#     checklist_str = ''
    
#     # Проверка наличия чеклиста
#     if checklist_data:
#         for item in checklist_data.values():
#             title = item.get('title', '')
#             is_complete = item.get('isComplete', 'N') == 'Y'  # Если завершен, то True
#             # Формируем строку чеклиста для ClickUp
#             checklist_str += f"- [{'x' if is_complete else ' '}] {title}\n"
    
#     return checklist_str

