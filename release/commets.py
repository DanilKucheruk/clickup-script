import re
import uuid
import requests
from .get_link_to_image import get_link_to_image
# Словарь для маппинга имен пользователей на их user_id в ClickUp.
BITRIX_TO_CLICKUP_USERS = {
    "Мария Новикова": 48467541,
    "Maria Novikova" : 48467541,
    "Данил Кучерук": 87773460,
    "Иван Жуков" : 152444606,
    "Ivan Zhukov": 152444606,
    "Danil Kucheruk": 87773460
}

SLICKUPID_TO_CLICKUP_USERS = {
    87773460: "Danil Kucheruk",
    48467541: "Maria Novikova",
    152444606: "Ivan Zhukov"
}


def extract_mentions(comment):
    """Извлечение упоминаний пользователей из комментария."""
    mentioned_users = re.findall(r'@([А-Яа-яЁёA-Za-z]+ [А-Яа-яЁёA-Za-z]+)', comment)
    mentions = []
    start = 0  # Начало для извлечения части текста до упоминания
    comment_parts = []
    
    # Обрабатываем упоминания
    for mention in mentioned_users:
        mention_position = comment.find(f"@{mention}", start)  # Позиция упоминания в строке
        clean_comment = comment.replace(f"@{mention}", "")
        
        # Добавляем текст до упоминания в parts
        if mention_position > start:
            comment_parts.append({
                "text": comment[start:mention_position],
                "attributes": {}
            })
        
        # Добавляем упоминание как тег
        comment_parts.append({
            "type": "tag",
            "text": f"@{mention}",
            "attributes": {}
        })
        
        # Обновляем start, чтобы начать с позиции после текущего упоминания
        start = mention_position + len(f"@{mention}")
        
        # Получаем user_id для каждого упомянутого пользователя
        user_id = BITRIX_TO_CLICKUP_USERS.get(mention)
        if user_id:
            mentions.append({
                "user_id": user_id,  # Используем user_id из словаря
                "username": SLICKUPID_TO_CLICKUP_USERS.get(user_id)
            })
    
    # Добавляем оставшуюся часть текста после последнего упоминания
    if start < len(comment):
        comment_parts.append({
            "text": comment[start:],
            "attributes": {}
        })
    
    return mentions, comment_parts


def extract_dates_and_format(comment_parts):
    """Обработка и форматирование дат в комментарии."""
    # date_pattern = r'[А-ЯЁа-яёA-Za-z]+ [А-ЯЁа-яёA-Za-z]+-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2}:'
    date_pattern = r'[А-ЯЁа-яёA-Za-z]+ [А-ЯЁа-яёA-Za-z]+       \d{1,2} [A-Za-z]+ \d{4}, \d{2}:\d{2}:\d{2}'

    comment_parts_with_dates = []
    
    start = 0  # Начало для извлечения части текста до даты
    
    for part in comment_parts:
        if "text" in part:
            text = part["text"]
            date_matches = re.findall(date_pattern, text)
            
            # Если есть даты, разбиваем текст на части
            if date_matches:
                last_end = 0
                for date in date_matches:
                    date_position = text.find(date, last_end)
                    # Добавляем текст до даты
                    if date_position > last_end:
                        comment_parts_with_dates.append({
                            "text": text[last_end:date_position],
                            "attributes": {}
                        })

                    # Добавляем саму дату как тег
                    comment_parts_with_dates.append({
                        "text": date + "\n",
                        "attributes": {"badge-class": "blue"}
                    })

                    # Обновляем last_end для следующего фрагмента текста
                    last_end = date_position + len(date)

                # Добавляем оставшийся текст после последней даты
                if last_end < len(text):
                    comment_parts_with_dates.append({
                        "text": text[last_end:], 
                        "attributes": {}
                    })
            else:
                # Если дат не найдено, просто добавляем этот фрагмент
                comment_parts_with_dates.append(part)

        # for item in comment_parts_with_dates:
        #     if 'text' in item and item['text'].startswith('|'):
        #         item.setdefault('attributes', {})['blockquote'] = '{}'

    return comment_parts_with_dates


def process_code_and_tables(comment_parts):
    """Обрабатывает код и таблицы в комментарии."""
    processed_parts = []
    
    for part in comment_parts:
        if "text" in part:
            text = part["text"]
            
            # Обработка кода - удаляем теги [CODE] и делаем текст серым
            code_pattern = r'\[CODE\](.*?)\[/CODE\]'
            code_matches = re.finditer(code_pattern, text, re.DOTALL)
            last_end = 0
            
            has_code = False
            for match in code_matches:
                has_code = True
                start, end = match.span()
                # Добавляем текст до кода
                if start > last_end:
                    processed_parts.append({
                        "text": text[last_end:start],
                        "attributes": part.get("attributes", {})
                    })
                
                # Добавляем код с серым фоном
                code_text = match.group(1).strip()
                processed_parts.append({
                    "text": code_text,
                    "attributes": {"background-class": "grey"}
                })
                last_end = end
            
            # Добавляем оставшийся текст
            if not has_code:
                # Удаляем теги таблиц
                text = re.sub(r'\[/?(?:TABLE|TR|TD)\]', '', text)
                processed_parts.append({
                    "text": text,
                    "attributes": part.get("attributes", {})
                })
            elif last_end < len(text):
                remaining_text = text[last_end:]
                remaining_text = re.sub(r'\[/?(?:TABLE|TR|TD)\]', '', remaining_text)
                processed_parts.append({
                    "text": remaining_text,
                    "attributes": part.get("attributes", {})
                })
        else:
            processed_parts.append(part)
            
    return processed_parts

def process_disk_file_ids(comment_parts):
    """Обрабатывает строку [DISK FILE ID=n328528] и возвращает ссылку в комментарии."""
    updated_parts = []
    
    # Регулярное выражение для поиска [DISK FILE ID=n328528]
    disk_file_pattern = r'\[DISK FILE ID=n(\d+)\]'

    for part in comment_parts:
        if 'text' in part:
            text = part['text']
            # Найдем все вхождения шаблона
            matches = re.finditer(disk_file_pattern, text)
            
            # Если находим [DISK FILE ID=n328528], извлекаем ID и получаем ссылку
            last_end = 0
            for match in matches:
                start, end = match.span()
                # Добавляем текст до [DISK FILE ID=n328528]
                if start > last_end:
                    updated_parts.append({
                        "text": text[last_end:start],
                        "attributes": part.get("attributes", {})
                    })
                
                # Извлекаем ID файла
                file_id = match.group(1)
                
                # Составляем ссылку
                link = get_link_to_image(file_id)

                # Заменяем пробелы на '%'
                if link:
                    link = link.replace(" ", "%20")
                    updated_parts.append({
                        "text": link,
                        "attributes": {}
                    })
                else:
                    updated_parts.append({
                        "text": "[Ошибка получения ссылки]",
                        "attributes": {}
                    })
                
                last_end = end
            
            # Добавляем оставшийся текст после последнего [DISK FILE ID=n328528]
            if last_end < len(text):
                updated_parts.append({
                    "text": text[last_end:],
                    "attributes": part.get("attributes", {})
                })
        else:
            updated_parts.append(part)
    
    return updated_parts



def remove_bbcode(text):
    """Удаление всех BB-кодов из текста."""
    # Удаляем все BB-коды (например, [B], [I], [U], [CODE], [TABLE] и т.д.)
    clean_text = re.sub(r'\[.*?\]', '', text)  # Удаляет все теги вида [B], [/B] и т.д.
    return clean_text
def process_comment_with_quotes(comment_parts_with_dates):
    """Обрабатывает комментарий с цитатами, начиная с 'написал(а):' и добавляет атрибуты к цитатам."""
    
    # Сначала обрабатываем код и таблицы
    comment_part = process_disk_file_ids(comment_parts_with_dates)
    comment_parts = process_code_and_tables(comment_part)
    
    # Шаблон для нахождения "написал(а):"
    write_pattern = r"^\|\s*(?!\/n\/n).+$|написал\(а\):|написала:|написал:|"
    
    comment_parts_with_q = []
    
    for part in comment_parts:
        if "text" in part:
            text = part["text"]
            date_matches = re.findall(write_pattern, text, re.MULTILINE)
            
            # Если есть совпадения, разбиваем текст на части
            if date_matches:
                last_end = 0
                for date in date_matches:
                    date_position = text.find(date, last_end)
                    # Добавляем текст до совпадения
                    if date_position > last_end:
                        comment_parts_with_q.append({
                            "text": text[last_end:date_position],
                            "attributes": part.get("attributes", {})
                        })

                    # Добавляем само совпадение
                    comment_parts_with_q.append({
                        "text": date,
                        "attributes": {"background-class": "grey", "italic": True}
                    })

                    last_end = date_position + len(date)

                # Добавляем оставшийся текст
                if last_end < len(text):
                    comment_parts_with_q.append({
                        "text": text[last_end:], 
                        "attributes": part.get("attributes", {})
                    })
            else:
                # Если совпадений нет, добавляем часть как есть
                comment_parts_with_q.append(part)
        else:
            comment_parts_with_q.append(part)

    for part in comment_parts_with_q:
        if "text" in part:
            part["text"] = remove_bbcode(part["text"])
    return comment_parts_with_q

def send_comment_to_clickup(task_id, comment_parts_with_dates, mentions):
    """Отправка комментария в ClickUp с упоминаниями."""
    url = f"https://api.clickup.com/api/v2/task/{task_id}/comment"
    
    headers = {
        'Authorization': 'pk_87773460_IA6NSWKD8W9PLWU480KIDV4ED6YATJNU',
        'Content-Type': 'application/json'
    }
    # Формируем данные для отправки
    data = {
        "comment_text": " ",  # Текст комментария без упоминаний
        "mentions": mentions,  # Список упомянутых пользователей
        "comment": comment_parts_with_dates  # Составляем окончательный список для комментария с тэгами и цитатами
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"API Response: {response.status_code} - {response.text}")
        response.raise_for_status()  # Проверка на успешность запроса (200 OK)
        print(f"Комментарий успешно отправлен для задачи {task_id}")
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при добавлении комментария: {e}")

def add_comment_with_mentions(task_id, comment):
    """Основная функция для добавления комментария с упоминаниями и датами."""
    
    # Логируем очищенный комментарий для отладки
    if not comment or not comment.strip():
        print("Пустой комментарий, пропускаем отправку.")
        return
    
    # Извлекаем упоминания и очищаем текст комментария
    mentions, comment_parts = extract_mentions(comment)
    
    # Разбираем текст на даты
    comment_parts_with_dates = extract_dates_and_format(comment_parts)
    # Отправляем комментарий в ClickUp

    resukt = process_comment_with_quotes(comment_parts_with_dates)
    send_comment_to_clickup(task_id, resukt, mentions)
