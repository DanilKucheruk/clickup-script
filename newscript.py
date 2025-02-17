import re

# Регулярное выражение для "Имя Фамилия-YYYY-MM-DDTHH:MM:SS+TZ"
date_pattern = r'([А-ЯЁа-яёA-Za-z]+ [А-ЯЁа-яёA-Za-z]+-\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[+-]\d{2}:\d{2})'

def process_dates_in_text(text):
    """Обработка текста с разделением на блоки, включая даты в формате 'Имя Фамилия-YYYY-MM-DDTHH:MM:SS+TZ'."""
    
    date_matches = re.findall(date_pattern, text)
    
    if not date_matches:
        return [{"text": text, "attributes": {}}]  # Если даты не найдены, возвращаем без изменений
    
    result = []
    start = 0
    for date in date_matches:
        date_position = text.find(date, start)
        
        # Добавляем часть текста до даты
        if date_position > start:
            result.append({
                "text": text[start:date_position],
                "attributes": {}
            })
        
        # Добавляем саму дату
        result.append({
            "text": date + "\n",
            "attributes": {"badge-class": "blue"}
        })
        
        # Обновляем start для следующей обработки
        start = date_position + len(date)
    
    # Добавляем оставшуюся часть текста после последней даты
    if start < len(text):
        result.append({
            "text": text[start:],
            "attributes": {}
        })
    
    return result

# Пример текста
example_text = """ждем вышеуказанный тикет
\n\nДанил Кучерук-2025-02-12T16:36:44+03:00При сохранении возникла ошибка, возможно из-за того, что не указан блокчейн
\n\n[DISK FILE ID=n336280]
\n"""
example_text2 = """,\xa0да, есть, у меня все записано, вот он\xa0(https://bit.paypoint.pro/company/personal/user/320/tasks/task/view/62935/)
\n\nМария Новикова-2025-02-07T10:53:16+03:00ждем вышеуказанный тикет
\n"""

# Применяем обработку
processed_text_1 = process_dates_in_text(example_text)
processed_text_2 = process_dates_in_text(example_text2)

# Выводим результат
print("Обработанный текст 1:", processed_text_1)
print("Обработанный текст 2:", processed_text_2)
