import requests
import json
import re
from datetime import datetime
from checklist_transfer import add_checklist_to_task

from commets import add_comment_with_mentions
from description import trancfer_descriprion
from checklist_transfer import add_checklist_to_task

# 🔹 Ваши API ключи
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'
CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'
CLICKUP_LIST_ID = '901207995380'
FILTER_PATTERNS = [
    r'Необходимо указать крайний срок, иначе задача не будет выполнена вовремя\.',
    r'вы добавлены наблюдателем\.',
    r'задача почти просрочена\.',
    r'задача\s+просрочена',
    r'Крайний срок изменен на',


]
BITRIX_TO_CLICKUP_USERS = {
    # "Мария Новикова": 48467541,
    "Данил Кучерук": 87773460,
    # "Иван Жуков" : 152444606,
    # "Maria": 152420871,
    # "Ivan Zhukov": 152444606,
    # "Gena": 170510061
}

MAP_USER_ID_BITRIX_TO_CLICKUP = {
    334 : 87773460,
    6 : 48467541,
    1 : 152444606
}


def convert_bitrix_quotes(comment_text):
    """Преобразует цитаты из Bitrix ([QUOTE]...[/QUOTE])"""
    
    def quote_replacement(match):
        # Извлекаем имя пользователя и цитату
        user_text = match.group(1).strip()
        
        parts = user_text.split("\n", 1)
    
        if len(parts) == 2:
            user_line, quote_content = parts
        else:
            # Если разделить не удалось, просто возьмем все как одну часть
            user_line, quote_content = parts[0], ""
        
        # Форматируем цитату с нужным отступом, но избегаем лишних пустых строк
        formatted_quote = "\n".join([f"| {line}" for line in quote_content.split("\n") if line.strip()])
        
        # Возвращаем нужный формат: сначала имя пользователя, потом цитата
        return f"{user_line}\n{formatted_quote}"




    # Заменяем все цитаты
    comment_text = re.sub(r'\[QUOTE(?:=[^\]]+)?\](.*?)\[/QUOTE\]', quote_replacement, comment_text, flags=re.DOTALL)

    return comment_text.strip()

def format_comment_for_clickup(formatted_comment, comment_text):
    """Преобразует комментарий с упоминаниями в нужный формат для ClickUp."""
    
    if comment_text.strip():
        formatted_comment.append({
            "text": comment_text.strip(),
            "attributes": {}
        })

    return formatted_comment

def convert_bitrix_comment(comment_text):
    """Форматирует комментарий Bitrix для ClickUp, заменяя пользователей Bitrix на их ID ClickUp."""
    def replace_user(match):
        # Получаем имя пользователя из текста Bitrix
        user_name = match.group(2)
        # Получаем ID пользователя ClickUp по имени
        clickup_user_id = BITRIX_TO_CLICKUP_USERS.get(user_name)
        if clickup_user_id:
            return f"@{user_name}"  # Форматируем как упоминание пользователя
        else:
            return f"@{user_name}"  # Если не нашли в ClickUp, то так и указываем

    # Заменяем всех пользователей Bitrix на их идентификаторы в ClickUp
    comment_text = re.sub(r'\[USER=(\d+)\](.*?)\[/USER\]', replace_user, comment_text)
    comment_text = convert_bitrix_quotes(comment_text)
    comment_text = re.sub(r'\[URL=(.*?)\](.*?)\[/URL\]', r'\1', comment_text)
    # comment_text = re.sub(r'\[.*?\]', '', comment_text)  # Убираем BB-коды
    return comment_text.strip()

def filter_comment(comment_text):
    """Фильтрация комментариев по ключевым фразам."""
    for pattern in FILTER_PATTERNS:
        if re.search(pattern, comment_text, re.IGNORECASE):
            return None
    return comment_text

def get_bitrix_comments(task_id):
    """Получение всех комментариев из Bitrix24."""
    url = f"{BITRIX24_WEBHOOK_URL}task.commentitem.getList"
    try:
        response = requests.get(url, params={"taskId": task_id})
        response.raise_for_status()
        comments = []
        for c in response.json().get('result', []):
            author = c.get('AUTHOR_NAME', 'Неизвестный автор')
            post_date = c.get('POST_DATE', 'Неизвестная дата')
            text = convert_bitrix_comment(c.get('POST_MESSAGE', ''))
            text = filter_comment(text)
            date_obj = datetime.fromisoformat(post_date)
            readable_date = date_obj.strftime("%d %B %Y, %H:%M:%S")
            comment_header = f"{author}       {readable_date} \n"
            comment_header2 = "\n"
            formatted_comment = []
            comments.append(format_comment_for_clickup(formatted_comment, comment_header))
            comments.append(format_comment_for_clickup(formatted_comment, comment_header2))
            if text:
                formatted_comment = format_comment_for_clickup(formatted_comment,text)
                # Преобразуем список формата комментария в строку
                comment_str = ''.join([comment.get('text', '') for comment in formatted_comment])
                comment_str = comment_str.replace("@Мария Новикова", "@Maria Novikova")
                comment_str = comment_str.replace("@Данил Кучерук", "@Danil Kucheruk")
                comment_str = comment_str.replace("@Мария Новикова", "@Maria Novikova")
                # comment_str = comment_str.replace("@Иван Жуков", "@Ivan Zhukov")
                comments.append(comment_str)
        return comments  
        
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении комментариев Bitrix для задачи {task_id}: {e}")
        return []

def add_clickup_comment(task_id, comment):
    """Добавление одного объединенного комментария в ClickUp."""
    
    # Преобразуем комментарий в строку, удалим все лишние пробелы и невидимые символы
    cleaned_comment = '\n\n'.join([str(c).strip() for c in comment if isinstance(c, str)])
    add_comment_with_mentions(task_id, cleaned_comment)

# 🔹 Получение информации о задаче из Bitrix24
def get_bitrix_task(task_id):
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.get.json"
    try:
        response = requests.get(url, params={"taskId": task_id})
        response.raise_for_status()
        task = response.json().get('result', {}).get('task')
        if task:
            print(f"Задача {task_id} найдена")
        else:
            print(f"Задача {task_id} не найдена в Bitrix24.")
        return task
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении задачи {task_id} из Bitrix: {e}")
        return None


def get_bitrix_tags(task_id):
    """Получает список тегов задачи в виде массива строк."""
    url = f"{BITRIX24_WEBHOOK_URL}tasks.task.get.json"
    params = {
        "taskId": task_id,
        "select[]": ["TAGS"]
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        task = response.json().get('result', {}).get('task')

        if task and "tags" in task:
            tags_dict = task["tags"]  # {'1380': {'id': 1380, 'title': 'П1'}}
            tags_list = [tag_data["title"] for tag_data in tags_dict.values()]
            
            print(f"Теги задачи {task_id}: {tags_list}")
            return tags_list
        else:
            print(f"Задача {task_id} не содержит тегов.")
            return []
    
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении тегов для задачи {task_id}: {e}")
        return []

# 🔹 Маппинг ответственного из Bitrix24 на ClickUp

MAP_USER_ID_BITRIX_TO_CLICKUP = {
        334: 87773460,
        6: 48467541,
        1: 152444606
    }
    
def map_assignees(bitrix_task):
    clickupid = []
    
    # Получаем ID ответственного из Bitrix
    responsible = bitrix_task.get('responsible')
    if responsible:
        # Проверяем тип данных и извлекаем ID соответственно
        if isinstance(responsible, dict):
            bitrix_user_id = int(responsible.get('id', 0))
        elif isinstance(responsible, list) and responsible:
            bitrix_user_id = int(responsible[0])
        else:
            bitrix_user_id = int(responsible) if str(responsible).isdigit() else 0
        
        # Проверяем, если bitrix_user_id есть в словаре
        if bitrix_user_id in MAP_USER_ID_BITRIX_TO_CLICKUP:
            # Добавляем соответствующий clickup_id в список
            clickupid.append(MAP_USER_ID_BITRIX_TO_CLICKUP[bitrix_user_id])
    
    # Печатаем результат
    print("Mapped Assignees (ClickUp IDs):")
    print(clickupid)
    
    return clickupid


def map_watchers(bitrix_task):
    clickup_auditor_ids = set()  # Используем set для уникальных ID
    
    print("DEBUG: auditorsData type:", type(bitrix_task.get('auditorsData')))
    print("DEBUG: auditorsData value:", bitrix_task.get('auditorsData'))
    print("DEBUG: auditors type:", type(bitrix_task.get('auditors')))
    print("DEBUG: auditors value:", bitrix_task.get('auditors'))

    # Проверяем наличие auditorsData (словарь с данными аудиторов)
    auditorsData = bitrix_task.get('auditorsData')
    if auditorsData and isinstance(auditorsData, dict):
        print("DEBUG: Processing auditorsData as dict")
        for auditor_id_str in auditorsData:
            auditor_id = int(auditor_id_str)  # Используем ID из ключа словаря
            print(f"DEBUG: Processing auditor_id {auditor_id} from auditorsData")
            if auditor_id in MAP_USER_ID_BITRIX_TO_CLICKUP:
                clickup_auditor_ids.add(MAP_USER_ID_BITRIX_TO_CLICKUP[auditor_id])
    
    # Проверяем наличие auditors (список ID аудиторов)
    auditors = bitrix_task.get('auditors')
    if auditors and isinstance(auditors, list):
        print("DEBUG: Processing auditors as list")
        for auditor_id_str in auditors:
            auditor_id = int(auditor_id_str)
            print(f"DEBUG: Processing auditor_id {auditor_id} from auditors list")
            if auditor_id in MAP_USER_ID_BITRIX_TO_CLICKUP:
                clickup_auditor_ids.add(MAP_USER_ID_BITRIX_TO_CLICKUP[auditor_id])
    
    # Печатаем результат
    print("Mapped Watchers (ClickUp IDs):")
    result = list(clickup_auditor_ids)  # Преобразуем обратно в список
    print(result)
    
    return result


# 🔹 Приоритеты задач: Преобразуем из Bitrix в ClickUp
def get_bitrix_priority(priority):
    # Убедимся, что приоритет из Bitrix24 корректно отображается в ClickUp
    priority_map = {
        "1": 4,  # Lowest
        "2": 3,  # Low
        "3": 2,  # Normal
        "4": 1,
    }
    return priority_map.get(str(priority), 2)  # Default to Normal if the priority is unknown



def map_status(bitrix_task,tags):
    # 1 — вывалить ошибку? проверить в бд запросом наличие таких?
    # 2 — Создана => "Не начата"
    # 3 — (этот статус появиться в json, если нажата кнопка "Начать выполнение") => "В работе"
    # 4 — Ждёт контроля => если есть тег "Ожидает тестирования", то "На тестировании", а если тега нет, то "Ждет контроля"
    # 5 — Завершена => "Завершена"

    

    MAP_STATUS_BITRIX_TO_CLICKUP = {
        3 : "IN PROGRESS",
        2:  "PLANNING",
        4: "READY FOR REVIEW",
        5: "DONE"
    }


    bitrix_status = int(bitrix_task['status'])

    return MAP_STATUS_BITRIX_TO_CLICKUP[bitrix_status]


def update_task_add_watchers(task_id, watchers):
    """Обновление задачи в ClickUp и добавление наблюдателей."""
    
    # Формирование URL для запроса
    url = f'https://api.clickup.com/api/v2/task/{task_id}'
    
    # Заголовки для запроса
    headers = {
        'Authorization': CLICKUP_API_KEY,  # Ваш API ключ
        'accept': 'application/json',       # Указание на формат ответа
        'content-type': 'application/json'  # Указание на тип отправляемых данных
    }
    
    # Данные для запроса (добавление наблюдателей)
    data = {
        "watchers": {
            "add" : watchers
        }  
    }

    print(data, task_id)

    try:
        # Отправка PUT запроса
        response = requests.put(url, headers=headers, json=data)
        
        # Проверка успешности запроса
        if response.status_code == 200:
            print(f"Задача {task_id} обновлена в ClickUp.")
        else:
            # Вывод ошибки в случае, если код ответа не 200
            print(f"Ошибка при обновлении задачи: {response.status_code} - {response.text}")

    except requests.exceptions.RequestException as e:
        # Обработка ошибок при запросе
        print(f"Ошибка при запросе: {e}")

    
# 🔹 Создание задачи в ClickUp
def create_clickup_task(name, description, assignees, priority,status, date_created, deadline, bitrix_tags):
    url = f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task'
    headers = {'Authorization': CLICKUP_API_KEY, 'Content-Type': 'application/json'}
    data = {
        "name": name, 
        "description": description, 
        "assignees": assignees, 
        "priority": priority,
        "status" : status,
        "start_date": date_created,
        "due_date": deadline,
        "tags": bitrix_tags
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        clickup_task_id = response.json().get('id')
        print(f"Задача создана в ClickUp: {clickup_task_id}")
        return response.json().get('id')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании задачи в ClickUp: {e}")
        return None

# 🔹 Создание подзадачи в ClickUp
def create_clickup_subtask(parent_task_id, task_name, task_description, clickup_assign_ids, bitrix_priority,status, date_created, deadline,bitrix_tags):
    url = f'https://api.clickup.com/api/v2/task/{parent_task_id}/subtask'
    headers = {'Authorization': CLICKUP_API_KEY, 'Content-Type': 'application/json'}
    data = {
        "name": task_name, 
        "description": task_description, 
        "assignees": clickup_assign_ids, 
        "priority": bitrix_priority,
        "status" : status,
        "start_date": date_created,
        "due_date": deadline,
        "tags": bitrix_tags
    }
    try:
        # Здесь мы передаем родительский ID в запрос
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"✅ Подзадача создана в ClickUp: {response.json().get('id')}")
        return response.json().get('id')
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании подзадачи в ClickUp: {e}")
        return None

# 🔹 Хеш-карта для хранения ID задач
task_id_map = {}

# 🔹 Функция для добавления задачи в хеш-карту
def add_task_to_map(bitrix_task_id, clickup_task_id):
    task_id_map[bitrix_task_id] = clickup_task_id


def convert_to_timestamp(date_str):
    if date_str:
        # Преобразуем строку в объект datetime
        dt = datetime.fromisoformat(date_str)
        # Получаем timestamp в секундах и умножаем на 1000 для миллисекунд
        return int(dt.timestamp() * 1000)
    else:
        return None

def transfer_task():
    # Получаем список всех задач Bitrix24
    task_ids = [59662] 
    for task_id in task_ids:
        try:
            print(f"\n=== Начинаем обработку задачи с ID: {task_id} ===")
            print(f"1. Получаем данные задачи из Bitrix")
            bitrix_task = get_bitrix_task(task_id)
            print("DEBUG: Task data:", bitrix_task)
            bitrix_tags = get_bitrix_tags(task_id)
            if not bitrix_task:
                print(f"❌ Задача с ID {task_id} не найдена")
                continue
            print(f"2. Данные задачи успешно получены")

            print(f"3. Подготовка данных для создания задачи в ClickUp")
            task_name = bitrix_task['title']
            task_description = trancfer_descriprion(bitrix_task)
            bitrix_priority = get_bitrix_priority(bitrix_task.get('priority', 4))
            bitrix_comments = get_bitrix_comments(task_id)
            # Применение к данным
            date_created = convert_to_timestamp(bitrix_task.get('createdDate'))
            deadline = convert_to_timestamp(bitrix_task.get('deadline'))
            print(f"4. Данные подготовлены: {task_name}")

            print(f"5. Проверка на наличие родительской задачи")
            parent_task_id = None
            if bitrix_task.get('parentId'):
                parent_task_id = task_id_map.get(bitrix_task['parentId'])
                print(f"   Найдена родительская задача: {parent_task_id}")
            else:
                print(f"   Родительская задача не найдена")

            print(f"6. Маппинг пользователей и статуса")
            clickup_assinged_id = map_assignees(bitrix_task)
            status = map_status(bitrix_task,bitrix_tags)
            print(f"7. Создание задачи в ClickUp")
            # Создание задачи или подзадачи в ClickUp
            try:
                # Получаем список наблюдателей до создания задачи
                watchers = map_watchers(bitrix_task)
                
                # Создаем задачу
                clickup_task_id = create_clickup_task(task_name, task_description, clickup_assinged_id, bitrix_priority, status, date_created, deadline,bitrix_tags) if not parent_task_id else create_clickup_subtask(parent_task_id, task_name, task_description, clickup_assinged_id, bitrix_priority,status, date_created, deadline,bitrix_tags)
                print(f"   Задача успешно создана: {clickup_task_id}")
                
                # Если задача создана успешно, добавляем комментарии и наблюдателей
                print(f"✅ Задача перенесена в ClickUp: {clickup_task_id}")
                add_task_to_map(task_id, clickup_task_id)
                add_clickup_comment(clickup_task_id, bitrix_comments)
                update_task_add_watchers(clickup_task_id, watchers)
                
                # Добавляем чеклисты, если они есть
                print("DEBUG: Проверяем наличие чеклистов")
                print(f"DEBUG: 'checkListTree' в bitrix_task: {'checkListTree' in bitrix_task}")
                print("DEBUG: Все ключи в bitrix_task:", bitrix_task.keys())
                print("DEBUG: Данные задачи:", json.dumps(bitrix_task, indent=2, ensure_ascii=False))
                
                if 'checkListTree' in bitrix_task:
                    print("\n=== Данные из Bitrix ===\n")
                    with open('debug_checklist.json', 'w', encoding='utf-8') as f:
                        json.dump(bitrix_task['checkListTree'], f, indent=2, ensure_ascii=False)
                    print(json.dumps(bitrix_task['checkListTree'], indent=2, ensure_ascii=False))
                    print("\n=== Конец данных ===\n")
                    
                    if isinstance(bitrix_task['checkListTree'], dict):
                        # Если это словарь, преобразуем в список
                        checklists = [bitrix_task['checkListTree']]
                        print("Создаем чеклисты...")
                        add_checklist_to_task(clickup_task_id, checklists)
                    elif isinstance(bitrix_task['checkListTree'], list):
                        print("Создаем чеклисты...")
                        add_checklist_to_task(clickup_task_id, bitrix_task['checkListTree'])
                print(f"✅ Задача успешно перенесена в ClickUp с ID {task_id}")
            except Exception as e:
                print(f"❌ Ошибка при создании задачи: {str(e)}")
                raise

        except Exception as e:
            print(f"❌ Ошибка при обработке задачи с ID {task_id}: {e}")
            continue  # Переходим к следующей задаче, если произошла ошибка

if __name__ == "__main__":
    transfer_task()
