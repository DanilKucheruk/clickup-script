import re

def trancfer_descriprion(bitrix_task):
    task_id = bitrix_task.get('id', '')
    task_description = f'Задача в Bitrix: https://bit.paypoint.pro/company/personal/user/334/tasks/task/view/{task_id}/' + "\n"
    task_description = task_description + bitrix_task.get('description', '')
    
    # Обработка ссылок
    task_description = re.sub(r'\[URL=(.*?)\](.*?)\[/URL\]', r'\1', task_description)
    task_description = re.sub(r'\[USER=(\d+)\](.*?)\[/USER\]', r'@ \1 \2', task_description)
    task_description = re.sub(r'\[.*?\]', '', task_description)

    print(task_description)
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

