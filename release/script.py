import requests
import json
import re
import time
from datetime import datetime
from .checklist_transfer import add_checklist_to_task
from .commets import add_comment_with_mentions
from .description import transfer_description
from config_map_category_and_priority import BITRIX_ID_IMPORTANCE_TO_CLICKUP_PRIORITY
from get_task_category import get_task_importance, get_task_category
from .set_custom_field import set_custom_fields
# 🔹 Ваши API ключи
BITRIX24_WEBHOOK_URL = 'https://bit.paypoint.pro/rest/334/ns8ufic41u9h1nla/'
CLICKUP_API_KEY = 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU'
CLICKUP_LIST_ID = '901508672918'
FILTER_PATTERNS = [
    r'Необходимо указать крайний срок, иначе задача не будет выполнена вовремя\.',
    r'вы добавлены наблюдателем\.',
    r'задача почти просрочена\.',
    r'задача\s+просрочена',
    r'Крайний срок изменен на',
    r'Проект задачи изменен на'


]
BITRIX_TO_CLICKUP_USERS = {
    # "Мария Новикова": 48467541,
    "Данил Кучерук": 87773460,
    # "Иван Жуков" : 152444604,
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
        # print(f"Ошибка при получении комментариев Bitrix для задачи {task_id}: {e}")
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
        # print(f"Ошибка при получении задачи {task_id} из Bitrix: {e}")
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
            tags_data = task["tags"]
            tags_list = []
            
            if isinstance(tags_data, dict):
                # Если tags - это словарь
                for tag_data in tags_data.values():
                    if isinstance(tag_data, dict) and 'title' in tag_data:
                        tags_list.append(tag_data['title'])
            elif isinstance(tags_data, list):
                # Если tags - это список
                for tag_data in tags_data:
                    if isinstance(tag_data, dict) and 'title' in tag_data:
                        tags_list.append(tag_data['title'])
                    elif isinstance(tag_data, str):
                        tags_list.append(tag_data)
            
            # print(f"Теги задачи {task_id}: {tags_list}")
            return tags_list
        else:
            # print(f"Задача {task_id} не содержит тегов.")
            return []
    
    except Exception as e:
        # print(f"Ошибка при получении тегов для задачи {task_id}: {e}")
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
    # print("Mapped Assignees (ClickUp IDs):")
    # print(clickupid)
    
    return clickupid


def map_watchers(bitrix_task):
    clickup_auditor_ids = set()  # Используем set для уникальных ID
    
    # print("DEBUG: auditorsData type:", type(bitrix_task.get('auditorsData')))
    # print("DEBUG: auditorsData value:", bitrix_task.get('auditorsData'))
    # print("DEBUG: auditors type:", type(bitrix_task.get('auditors')))
    # print("DEBUG: auditors value:", bitrix_task.get('auditors'))

    # Проверяем наличие auditorsData (словарь с данными аудиторов)
    auditorsData = bitrix_task.get('auditorsData')
    if auditorsData and isinstance(auditorsData, dict):
        # print("DEBUG: Processing auditorsData as dict")
        for auditor_id_str in auditorsData:
            auditor_id = int(auditor_id_str)  # Используем ID из ключа словаря
            # print(f"DEBUG: Processing auditor_id {auditor_id} from auditorsData")
            if auditor_id in MAP_USER_ID_BITRIX_TO_CLICKUP:
                clickup_auditor_ids.add(MAP_USER_ID_BITRIX_TO_CLICKUP[auditor_id])
    
    # Проверяем наличие auditors (список ID аудиторов)
    auditors = bitrix_task.get('auditors')
    if auditors and isinstance(auditors, list):
        # print("DEBUG: Processing auditors as list")
        for auditor_id_str in auditors:
            auditor_id = int(auditor_id_str)
            # print(f"DEBUG: Processing auditor_id {auditor_id} from auditors list")
            if auditor_id in MAP_USER_ID_BITRIX_TO_CLICKUP:
                clickup_auditor_ids.add(MAP_USER_ID_BITRIX_TO_CLICKUP[auditor_id])
    
    # Печатаем результат
    # print("Mapped Watchers (ClickUp IDs):")
    result = list(clickup_auditor_ids)  # Преобразуем обратно в список
    # print(result)
    
    return result


# 🔹 Приоритеты задач: Преобразуем из Bitrix в ClickUp
def get_bitrix_priority(bitrix_task):
    bitrix_id = bitrix_task['id']
    tags = get_bitrix_tags(bitrix_id)
    
    # Маппинг тегов на приоритеты ClickUp
    # 4 - Urgent (П1)
    # 3 - High (П2, П2+)
    # 2 - Normal (П3, П3+)
    # 1 - Low (П4, П4+)
    
    for tag in tags:
        if tag == 'П1':
            print(f"- Найден тег {tag}, установлен приоритет ClickUp: 4 (Urgent)")
            return 1
        elif tag in ['П2', 'П2+']:
            print(f"- Найден тег {tag}, установлен приоритет ClickUp: 3 (High)")
            return 2
        elif tag in ['П3', 'П3+']:
            print(f"- Найден тег {tag}, установлен приоритет ClickUp: 2 (Normal)")
            return 3
        elif tag in ['П4', 'П4+']:
            print(f"- Найден тег {tag}, установлен приоритет ClickUp: 1 (Low)")
            return 4
    
    # Если теги приоритета не найдены, приоритет не устанавливается
    print("- Теги приоритета не найдены, приоритет не будет установлен")
    return None



def map_status(bitrix_task,tags):
    # 1 — вывалить ошибку? проверить в бд запросом наличие таких?
    # 2 — Создана => "Не начата"
    # 3 — (этот статус появиться в json, если нажата кнопка "Начать выполнение") => "В работе"
    # 4 — Ждёт контроля => если есть тег "Ожидает тестирования", то "На тестировании", а если тега нет, то "Ждет контроля"
    # 5 — Завершена => "Завершена"

    

    MAP_STATUS_BITRIX_TO_CLICKUP = {
        3: "to do",  # In Progress -> to do
        2: "to do",  # Planning -> to do
        4: "to do",  # Ready for Review -> to do
        5: "complete"  # Done -> complete
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

    # print(data, task_id)

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
    headers = {
        'Authorization': CLICKUP_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        "name": name, 
        "markdown_content": description, 
        "assignees": assignees, 
        "status" : status,
        "start_date": date_created,
        "due_date": deadline,
        "tags": bitrix_tags
    }
    
    # Добавляем приоритет только если он указан
    if priority is not None:
        data["priority"] = priority
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"API Response: {response.status_code} - {response.text}")
        response.raise_for_status()
        clickup_task_id = response.json().get('id')
        print(f"Задача создана в ClickUp: {clickup_task_id}")
        return clickup_task_id
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании задачи в ClickUp: {e}")
        return None

# 🔹 Создание подзадачи в ClickUp
def create_clickup_subtask(parent_task_id, task_name, task_description, clickup_assign_ids, bitrix_priority,status, date_created, deadline,bitrix_tags):
    print(f"\nСоздание подзадачи:")
    print(f"- Родительская задача: {parent_task_id}")
    print(f"- Название: {task_name}")
    
    # Проверяем формат ID задачи
    if not parent_task_id or len(parent_task_id) < 5:
        print(f"- Ошибка: Неверный формат ID родительской задачи")
        return None

    headers = {'Authorization': CLICKUP_API_KEY, 'Content-Type': 'application/json'}
    
    def get_parent_task(task_id, max_retries=3):
        """Get parent task information from ClickUp with retries"""
        url = f'https://api.clickup.com/api/v2/task/{task_id}'
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"- Попытка {attempt + 1} из {max_retries}")
                    time.sleep(2)  # Пауза между попытками
                
                response = requests.get(url, headers=headers, timeout=30)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limit
                    print(f"- Превышен лимит запросов, ожидание...")
                    time.sleep(1)
                    continue
                else:
                    print(f"- Ошибка API: {response.status_code} - {response.text}")
            except requests.exceptions.Timeout:
                print(f"- Таймаут при получении родительской задачи")
            except Exception as e:
                print(f"- Ошибка при получении родительской задачи: {str(e)}")
        
        return None
    
    def find_last_valid_parent(task_id):
        """Находит последнего валидного родителя в пределах лимита вложенности"""
        current_id = task_id
        path = []
        
        while current_id:
            parent_info = get_parent_task(current_id)
            if not parent_info:
                break
            current_id = parent_info.get('parent')
            if current_id:
                path.append(current_id)
        
        # Если глубина больше 6, возвращаем ID задачи на 6-м уровне
        if len(path) >= 6:
            return path[-(6+1)]  # Берем задачу на 6-м уровне
        return task_id
    
    def try_create_subtask(parent_id, max_retries=3, level=0):
        """Try to create a subtask under the specified parent with retries"""
        url = f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task'
        data = {
            "name": task_name, 
            "markdown_content": task_description, 
            "assignees": clickup_assign_ids, 
            "status" : status,
            "start_date": date_created,
            "due_date": deadline,
            "tags": bitrix_tags
        }
        
        # Добавляем приоритет только если он указан
        if bitrix_priority is not None:
            data["priority"] = bitrix_priority
        
        # Добавляем parent только если он есть
        if parent_id:
            data["parent"] = parent_id
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"- Попытка {attempt + 1} из {max_retries}")
                    time.sleep(2)  # Пауза между попытками
                
                response = requests.post(url, headers=headers, json=data, timeout=30)
                if response.status_code == 200:
                    return response
                elif response.status_code == 400 and "Level of nested subtasks is limited to 7" in response.text:
                    # Если ошибка связана с лимитом вложенности, ищем последнего валидного родителя
                    if parent_id:
                        print("- Достигнут лимит вложенности, ищем последнего валидного родителя")
                        last_valid_parent = find_last_valid_parent(parent_id)
                        if last_valid_parent and last_valid_parent != parent_id:
                            print(f"- Создаем подзадачу для родителя на допустимом уровне")
                            return try_create_subtask(last_valid_parent, max_retries)
                    return None
                elif response.status_code == 429:  # Rate limit
                    print(f"- Превышен лимит запросов, ожидание...")
                    time.sleep(5)
                    continue
                else:
                    print(f"- Ошибка API: {response.status_code} - {response.text}")
            except requests.exceptions.Timeout:
                print(f"- Таймаут при создании подзадачи")
            except Exception as e:
                print(f"- Ошибка при создании подзадачи: {str(e)}")
        
        return None
    
    try:
        current_parent_id = parent_task_id
        while True:
            # Пробуем создать подзадачу
            response = try_create_subtask(current_parent_id)
            
            if response is None:
                return None
            
            if response.status_code == 200:
                # Успешно создали задачу
                task_id = response.json().get('id')
                print(f"- Создана задача с ID: {task_id}")
                return task_id
            
            error_data = response.json()
            if error_data.get('err') == 'Level of nested subtasks is limited to 7' and error_data.get('ECODE') == 'ITEM_224':
                print("- Превышен лимит вложенности (7 уровней)")
                
                # Получаем родительскую задачу
                parent_data = get_parent_task(current_parent_id)
                if not parent_data:
                    print("- Не удалось получить информацию о родительской задаче")
                    return None
                
                parent_of_parent = parent_data.get('parent')
                if parent_of_parent:
                    print(f"- Пробуем создать задачу на уровень выше (родитель: {parent_of_parent})")
                    current_parent_id = parent_of_parent
                    continue
                else:
                    print("- У родительской задачи нет родителя, создаем обычную задачу")
                    # Создаем задачу без родителя
                    url = f'https://api.clickup.com/api/v2/list/{CLICKUP_LIST_ID}/task'
                    data = {
                        "name": task_name, 
                        "markdown_content": task_description, 
                        "assignees": clickup_assign_ids, 
                        "priority": bitrix_priority,
                        "status" : status,
                        "start_date": date_created,
                        "due_date": deadline,
                        "tags": bitrix_tags
                    }
                    response = requests.post(url, headers=headers, json=data)
                    if response.status_code == 200:
                        task_id = response.json().get('id')
                        print(f"- Создана обычная задача с ID: {task_id}")
                        return task_id
                    break
            else:
                print(f"- Ошибка при создании задачи: {response.text}")
                return None
                
    except Exception as e:
        print(f"- Ошибка: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"- Текст ошибки: {e.response.text}")
        return None

# # 🔹 Хеш-карта для хранения ID задач
# task_id_map = {}

# # 🔹 Функция для добавления задачи в хеш-карту
# def add_task_to_map(bitrix_task_id, clickup_task_id):
#     task_id_map[bitrix_task_id] = clickup_task_id


def convert_to_timestamp(date_str):
    if date_str:
        # Преобразуем строку в объект datetime
        dt = datetime.fromisoformat(date_str)
        # Получаем timestamp в секундах и умножаем на 1000 для миллисекунд
        return int(dt.timestamp() * 1000)
    else:
        return None

def record_task_mapping(bitrix_id, clickup_task_id, mapping_file="mapping.txt"):
    """Записывает соответствие между ID задачи из Bitrix и ID задачи в ClickUp в файл mapping.txt."""
    try:
        with open(mapping_file, "a", encoding="utf-8") as f:
            f.write(f"{bitrix_id} - {clickup_task_id}\n")
        print(f"Сохранено соответствие: Bitrix ID {bitrix_id} -> ClickUp ID {clickup_task_id}")
    except Exception as e:
        print(f"Ошибка при записи соответствия: {e}")


def find_clickup_id(bitrix_id, mapping_file="mapping.txt"):
    """Ищет в mapping файле запись для заданного Bitrix ID и возвращает ClickUp ID, если найден."""
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            for line in f:
                # Каждая строка имеет формат: bitrix_id - clickup_id
                if line.startswith(f"{bitrix_id} - "):
                    parts = line.split(" - ")
                    if len(parts) >= 2:
                        return parts[1].strip()
        return None
    except Exception as e:
        print(f"Ошибка при чтении mapping файла: {e}")
        return None


def transfer_task(task_ids):


    for task_id in task_ids:
        try:
            bitrix_task = get_bitrix_task(task_id)
            bitrix_tags = get_bitrix_tags(task_id)
            task_name = bitrix_task['title']
            task_description = transfer_description(bitrix_task)
            bitrix_priority = get_bitrix_priority(bitrix_task)
            bitrix_comments = get_bitrix_comments(task_id)
            date_created = convert_to_timestamp(bitrix_task.get('createdDate'))
            deadline = convert_to_timestamp(bitrix_task.get('deadline'))
            watchers = map_watchers(bitrix_task)
            clickup_assinged_id = map_assignees(bitrix_task)
            status = map_status(bitrix_task,bitrix_tags)

            # Проверка на наличие родительской задачи
            if bitrix_task.get('parentId'):
                parent_id = bitrix_task.get('parentId')
                print(f"\nНайден ParentID: {parent_id}")
                parent_clickup_id = find_clickup_id(parent_id)
                
                if parent_clickup_id:
                    print(f"Найдена родительская задача в ClickUp: {parent_clickup_id}")
                    # Создаем подзадачу
                    clickup_task_id = create_clickup_subtask(parent_clickup_id, task_name, task_description, clickup_assinged_id, bitrix_priority, status, date_created, deadline, bitrix_tags)
                else:
                    print(f"Родительская задача {parent_id} не найдена в ClickUp, создаем обычную задачу")
                    # Создаем обычную задачу
                    clickup_task_id = create_clickup_task(task_name, task_description, clickup_assinged_id, bitrix_priority, status, date_created, deadline, bitrix_tags)
            else:
                print(f"Родительская задача не найдена")
                # Создаем обычную задачу
                clickup_task_id = create_clickup_task(task_name, task_description, clickup_assinged_id, bitrix_priority, status, date_created, deadline, bitrix_tags)

            # print(f"6. Маппинг пользователей и статуса")

            try:
                if clickup_task_id:
                    # Записываем соответствие ID задач
                    record_task_mapping(task_id, clickup_task_id)
                    
                    # Добавляем дополнительные данные
                    add_clickup_comment(clickup_task_id, bitrix_comments)
                    update_task_add_watchers(clickup_task_id, watchers)
                    create_checklist(bitrix_task, clickup_task_id)
                    set_custom_fields(clickup_task_id, task_id)
                    print(f"✅ Задача из Bitrix {task_id} успешно перенесена в ClickUp с ID {clickup_task_id}")
                else:
                    print(f"❌ Не удалось создать задачу в ClickUp для Bitrix задачи {task_id}")

            except Exception as e:
                print(f"❌ Ошибка при создании задачи в ClickUp: {e}")
                continue  # Переходим к следующей задаче, если произошла ошибка

        except Exception as e:
            print(f"❌ Ошибка при обработке задачи с ID {task_id}: {e}")
            continue  # Переходим к следующей задаче, если произошла ошибка

def create_checklist(bitrix_task, clickup_task_id):
    try:
        checklist_data = bitrix_task.get('checkListTree', [])
        if checklist_data and clickup_task_id:
            with open('debug_checklist.json', 'w', encoding='utf-8') as f:
                json.dump(checklist_data, f, indent=2, ensure_ascii=False)

            if isinstance(checklist_data, (list, dict)): 
                add_checklist_to_task(clickup_task_id, checklist_data)
            else:
                print(f"Неподдерживаемый тип данных чеклиста: {type(checklist_data)}")
        elif not clickup_task_id:  
            print("Ошибка: Не удалось создать задачу в ClickUp, пропускаем создание чеклистов")
        else:
            print("Чеклисты отсутствуют или пустые")

            
    except Exception as e:
        print(f"❌ Ошибка при обработке чеклиста: {str(e)}")
        raise

if __name__ == "__main__":
    transfer_task([])
